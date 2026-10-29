import re
import unicodedata
from datetime import date, datetime
from urllib.parse import parse_qs, urlparse

import requests

from models.Tools.lidl_discount_error import LidlDiscountError
from models.Tools.lidl_offer import LidlOffer
from models.Tools.lidl_store import LidlStore

class LidlDiscountTool:
    """Lädt Angebote aus dem öffentlichen Lidl-Web-Prospekt.

    Summary:
        Die Daten kommen von der Prospektübersicht, die lidl.de selbst anzeigt.
        Der Ort wird einer Filiale zugeordnet. Deren Angebotsregion bestimmt
        die regionale Ausgabe des aktuellen Aktionsprospekts.
        Die Lidl-Plus-Angebotsschnittstelle wird nicht aufgerufen.
    """

    overview_url = "https://endpoints.leaflets.schwarz/v4/overview"
    flyer_url = "https://endpoints.leaflets.schwarz/v4/flyer"
    store_search_url = "https://stores.lidlplus.com/api/v1/autocomplete/DE"
    store_region_url = "https://live.api.schwarz/odj/stores-api/v2/myapi/stores-frontend/stores"
    # Öffentlicher Schlüssel aus dem Filialwähler von lidl.de.
    store_api_key = "KxboQtt40BG4VpBL16IhaRd2CXh0QbAc"

    def __init__(self, session: requests.Session | None = None, timeout: float = 30) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout
        self.session.headers.setdefault("Accept", "application/json")
        self.session.headers.setdefault("User-Agent", "Mozilla/5.0")

    def search_stores(self, location: str, today: date | None = None) -> list[LidlStore]:
        """Liefert das aktuelle Web-Prospekt der Filialregion zum Ort."""
        place = location.strip()
        candidates = self._find_stores(place)
        if not candidates:
            raise LidlDiscountError(f"Für „{place}“ wurde keine Lidl-Filiale gefunden.")

        flyers = self._current_flyers(today or date.today())
        brochures: list[LidlStore] = []
        seen: set[str] = set()
        for store in candidates[:6]:
            region = self._offer_region(str(store.get("storeKey") or ""))
            flyer = LidlDiscountTool._flyer_for_region(flyers, region)
            if not isinstance(flyer, dict):
                continue
            identifier = LidlDiscountTool._brochure_key(flyer.get("flyerJson"))
            if not identifier or identifier in seen:
                continue
            seen.add(identifier)
            locality = str(store.get("locality") or store.get("name") or place).strip()
            postal_code = str(store.get("postalCode") or "").strip()
            place_label = f"{locality} ({postal_code})" if postal_code else locality
            title = str(flyer.get("title") or flyer.get("name") or "Aktionsprospekt")
            brochures.append(LidlStore(store_key=identifier, label=f"{place_label} · {title}"))

        if not brochures:
            raise LidlDiscountError("Für diesen Ort gibt es gerade kein regionales Web-Prospekt.")
        return brochures

    def get_discounts(self, store_key: str) -> list[LidlOffer]:
        """Liest die Artikel aus einem öffentlichen Prospekt."""
        if not LidlDiscountTool._is_brochure_key(store_key):
            raise LidlDiscountError("Das ausgewählte Prospekt ist ungültig.")

        data = self._get(
            self.flyer_url,
            params={"version": "4", "flyer_identifier": store_key, "client": "lidl"},
        )
        flyer = data.get("flyer") if isinstance(data, dict) else None
        products = flyer.get("products") if isinstance(flyer, dict) else None
        if not isinstance(products, dict):
            raise LidlDiscountError("Das Web-Prospekt hat nicht das erwartete Format.")

        period = LidlDiscountTool._period(flyer.get("offerStartDate"), flyer.get("offerEndDate"))
        offers: list[LidlOffer] = []
        for product in products.values():
            if isinstance(product, dict):
                offer = LidlDiscountTool._to_offer(product, period)
                if offer is not None:
                    offers.append(offer)
        return offers

    def _current_flyers(self, today: date) -> list[dict]:
        data = self._get(self.overview_url, params={"client_locale": "lidl/de-DE"})
        flyers = [flyer for flyer in LidlDiscountTool._store_flyers(data) if LidlDiscountTool._covers(flyer, today)]
        if not flyers:
            raise LidlDiscountError("Gerade ist kein aktuelles Web-Prospekt veröffentlicht.")
        return flyers

    def _find_stores(self, location: str) -> list[dict]:
        found: list[dict] = []
        seen: set[str] = set()
        for query in LidlDiscountTool._location_queries(location):
            data = self._get(
                self.store_search_url,
                params={
                    "input": query,
                    "language": "de",
                    "latitude": "51.16",
                    "longitude": "10.45",
                },
            )
            if not isinstance(data, list):
                continue
            for item in data:
                if not isinstance(item, dict):
                    continue
                store_key = str(item.get("storeKey") or "")
                if not store_key or store_key in seen:
                    continue
                seen.add(store_key)
                found.append(item)

        ranked = [item for item in found if LidlDiscountTool._store_score(item, location) > 0]
        ranked.sort(key=lambda item: (-LidlDiscountTool._store_score(item, location), item.get("distance") or 10**12))
        return ranked

    def _offer_region(self, store_key: str) -> str:
        object_number = LidlDiscountTool._object_number(store_key)
        if not object_number:
            return ""
        try:
            data = self._get(
                self.store_region_url,
                params={"object_number": object_number},
                headers={"x-apikey": self.store_api_key},
            )
        except LidlDiscountError:
            return ""
        items = data.get("items") if isinstance(data, dict) else None
        store = items[0] if isinstance(items, list) and items else None
        marketing = store.get("marketingData") if isinstance(store, dict) else None
        region = marketing.get("offerRegion") if isinstance(marketing, dict) else None
        if region in (None, ""):
            return ""
        return str(region)

    def _get(self, url: str, params: dict | None = None, headers: dict | None = None) -> dict | list:
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise LidlDiscountError("Das Web-Prospekt konnte gerade nicht geladen werden.") from exc
        except ValueError as exc:
            raise LidlDiscountError("Die Prospekt-Antwort konnte nicht gelesen werden.") from exc


    @staticmethod
    def _store_flyers(data: dict) -> list[dict]:
        flyers: list[dict] = []
        for category in data.get("categories") or []:
            if not isinstance(category, dict) or category.get("name") != "Filial-Angebote":
                continue
            for subcategory in category.get("subcategories") or []:
                if not isinstance(subcategory, dict) or subcategory.get("name") != "Unsere Aktionsprospekte":
                    continue
                flyers.extend(flyer for flyer in subcategory.get("flyers") or [] if isinstance(flyer, dict))
        return flyers

    @staticmethod
    def _covers(flyer: dict, today: date) -> bool:
        try:
            start = date.fromisoformat(str(flyer.get("offerStartDate")))
            end = date.fromisoformat(str(flyer.get("offerEndDate")))
        except ValueError:
            return False
        return start <= today <= end

    @staticmethod
    def _is_national(flyer: dict) -> bool:
        return any(
            isinstance(region, dict) and region.get("type") == "national" and str(region.get("code")) == "0"
            for region in flyer.get("regions") or []
        )

    @staticmethod
    def _flyer_for_region(flyers: list[dict], region_code: str) -> dict | None:
        if not region_code:
            return None
        regional = [
            flyer
            for flyer in flyers
            if any(
                isinstance(region, dict)
                and region.get("type") == "offer_region"
                and str(region.get("code")) == region_code
                for region in flyer.get("regions") or []
            )
        ]
        if regional:
            regional.sort(key=lambda flyer: str(flyer.get("offerStartDate") or ""), reverse=True)
            return regional[0]
        national = [flyer for flyer in flyers if LidlDiscountTool._is_national(flyer)]
        return national[0] if national else None

    @staticmethod
    def _location_queries(location: str) -> list[str]:
        queries: list[str] = []
        for candidate in (location, LidlDiscountTool._with_umlauts(location)):
            text = candidate.strip()
            if text and text not in queries:
                queries.append(text)
        return queries

    @staticmethod
    def _with_umlauts(location: str) -> str:
        text = location
        for source, target in (
            ("AE", "Ä"),
            ("OE", "Ö"),
            ("UE", "Ü"),
            ("Ae", "Ä"),
            ("Oe", "Ö"),
            ("Ue", "Ü"),
            ("ae", "ä"),
            ("oe", "ö"),
            ("ue", "ü"),
        ):
            text = text.replace(source, target)
        return text

    @staticmethod
    def _object_number(store_key: str) -> str:
        if not re.fullmatch(r"DE\d{3,6}", store_key):
            return ""
        return f"DE{store_key[2:].zfill(5)}"

    @staticmethod
    def _store_score(store: dict, location: str) -> int:
        query = location.strip()
        folded_query = LidlDiscountTool._fold(query)
        locality = LidlDiscountTool._fold(str(store.get("locality") or ""))
        name = LidlDiscountTool._fold(str(store.get("name") or ""))
        postal_code = str(store.get("postalCode") or "").strip()
        if query.isdigit():
            if postal_code == query:
                return 100
            if len(query) >= 3 and postal_code.startswith(query[:3]):
                return 60
            return 0
        if not folded_query:
            return 0
        if locality == folded_query or locality.startswith(folded_query):
            return 80
        parts = locality.replace("-", " ").replace("/", " ").split()
        if any(part == folded_query or part.startswith(folded_query) for part in parts):
            return 70
        if folded_query in name:
            return 40
        return 0

    @staticmethod
    def _fold(value: str) -> str:
        text = value.casefold().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        decomposed = unicodedata.normalize("NFKD", text)
        return "".join(char for char in decomposed if not unicodedata.combining(char))

    @staticmethod
    def _brochure_key(url: object) -> str:
        if not isinstance(url, str):
            return ""
        identifier = parse_qs(urlparse(url).query).get("flyer_identifier", [""])[0]
        return identifier if LidlDiscountTool._is_brochure_key(identifier) else ""

    @staticmethod
    def _is_brochure_key(value: str) -> bool:
        return re.fullmatch(r"[A-Za-z0-9-]{8,120}", value) is not None

    @staticmethod
    def _to_offer(product: dict, period: str) -> LidlOffer | None:
        title = str(product.get("title") or "").strip()
        if not title or product.get("price") in (None, ""):
            return None
        brand = str(product.get("brand") or "").strip()
        name = f"{brand} {title}".strip() if brand and brand.casefold() not in title.casefold() else title
        return LidlOffer(
            name=LidlDiscountTool._clean_text(name),
            price=LidlDiscountTool._price(product.get("price"), product.get("currencySymbol")),
            old_price="",
            discount="",
            period=period,
            image_url=LidlDiscountTool._image_url(product.get("image")),
        )

    @staticmethod
    def _price(value: object, symbol: object) -> str:
        text = str(value).strip().replace(".", ",")
        mark = str(symbol).strip() if isinstance(symbol, str) else ""
        if mark and not text.endswith(mark):
            return f"{text} {mark}"
        return text

    @staticmethod
    def _image_url(value: object) -> str:
        if not isinstance(value, str):
            return ""
        url = value.strip()
        if url.startswith("//"):
            url = f"https:{url}"
        elif url.startswith("/"):
            url = f"https://www.lidl.de{url}"
        if url.startswith("https://") or url.startswith("http://"):
            return url
        return ""

    @staticmethod
    def _period(start: object, end: object) -> str:
        start_text = LidlDiscountTool._format_date(start)
        end_text = LidlDiscountTool._format_date(end)
        if start_text and end_text:
            return f"{start_text} – {end_text}"
        return start_text or end_text

    @staticmethod
    def _format_date(value: object) -> str:
        if not isinstance(value, str) or not value:
            return ""
        try:
            return datetime.fromisoformat(value).strftime("%d.%m.%Y")
        except ValueError:
            return value[:10]

    @staticmethod
    def _clean_text(value: str) -> str:
        cleaned = "".join(char for char in value if unicodedata.category(char) != "Cf")
        return " ".join(cleaned.split())


