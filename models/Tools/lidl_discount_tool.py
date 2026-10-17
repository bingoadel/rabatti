import re
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime
from urllib.parse import parse_qs, urlparse

import requests


class LidlDiscountError(Exception):
    """Das öffentliche Web-Prospekt konnte nicht geladen werden."""


@dataclass
class LidlStore:
    """Ein öffentliches Lidl-Web-Prospekt."""

    store_key: str
    label: str


@dataclass
class LidlOffer:
    """Ein Artikel aus dem öffentlichen Aktionsprospekt."""

    name: str
    price: str
    old_price: str
    discount: str
    period: str
    image_url: str = ""


class LidlDiscountTool:
    """Lädt Angebote aus dem öffentlichen Lidl-Web-Prospekt.

    Summary:
        Die Daten kommen von der Prospektübersicht, die lidl.de selbst anzeigt.
        Genutzt wird die bundesweite Ausgabe des aktuellen Aktionsprospekts.
        Die Lidl-Plus-Angebotsschnittstelle wird nicht aufgerufen.
    """

    overview_url = "https://endpoints.leaflets.schwarz/v4/overview"
    flyer_url = "https://endpoints.leaflets.schwarz/v4/flyer"

    def __init__(self, session: requests.Session | None = None, timeout: float = 30) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout
        self.session.headers.setdefault("Accept", "application/json")
        self.session.headers.setdefault("User-Agent", "Mozilla/5.0")

    def search_stores(self, location: str, today: date | None = None) -> list[LidlStore]:
        """Liefert das aktuelle bundesweite Web-Prospekt."""
        brochure = self._current_brochure(today or date.today())
        place = location.strip()
        if place:
            brochure = LidlStore(store_key=brochure.store_key, label=f"{brochure.label} für {place}")
        return [brochure]

    def get_discounts(self, store_key: str) -> list[LidlOffer]:
        """Liest die Artikel aus einem öffentlichen Prospekt."""
        if not _is_brochure_key(store_key):
            raise LidlDiscountError("Das ausgewählte Prospekt ist ungültig.")

        data = self._get(
            self.flyer_url,
            params={"version": "4", "flyer_identifier": store_key, "client": "lidl"},
        )
        flyer = data.get("flyer") if isinstance(data, dict) else None
        products = flyer.get("products") if isinstance(flyer, dict) else None
        if not isinstance(products, dict):
            raise LidlDiscountError("Das Web-Prospekt hat nicht das erwartete Format.")

        period = _period(flyer.get("offerStartDate"), flyer.get("offerEndDate"))
        offers: list[LidlOffer] = []
        for product in products.values():
            if isinstance(product, dict):
                offer = _to_offer(product, period)
                if offer is not None:
                    offers.append(offer)
        return offers

    def _current_brochure(self, today: date) -> LidlStore:
        data = self._get(self.overview_url, params={"client_locale": "lidl/de-DE"})
        flyers = [
            flyer
            for flyer in _store_flyers(data)
            if _covers(flyer, today)
        ]
        national = [flyer for flyer in flyers if _is_national(flyer)]
        chosen = (national or flyers or [None])[0]
        if not isinstance(chosen, dict):
            raise LidlDiscountError("Gerade ist kein aktuelles Web-Prospekt veröffentlicht.")

        identifier = _brochure_key(chosen.get("flyerJson"))
        if not identifier:
            raise LidlDiscountError("Das Web-Prospekt konnte nicht zugeordnet werden.")
        title = chosen.get("title") or chosen.get("name") or "Aktionsprospekt"
        return LidlStore(store_key=identifier, label=f"Aktionsprospekt {title}")

    def _get(self, url: str, params: dict | None = None) -> dict | list:
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise LidlDiscountError("Das Web-Prospekt konnte gerade nicht geladen werden.") from exc
        except ValueError as exc:
            raise LidlDiscountError("Die Prospekt-Antwort konnte nicht gelesen werden.") from exc


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


def _covers(flyer: dict, today: date) -> bool:
    try:
        start = date.fromisoformat(str(flyer.get("offerStartDate")))
        end = date.fromisoformat(str(flyer.get("offerEndDate")))
    except ValueError:
        return False
    return start <= today <= end


def _is_national(flyer: dict) -> bool:
    return any(
        isinstance(region, dict) and region.get("type") == "national" and str(region.get("code")) == "0"
        for region in flyer.get("regions") or []
    )


def _brochure_key(url: object) -> str:
    if not isinstance(url, str):
        return ""
    identifier = parse_qs(urlparse(url).query).get("flyer_identifier", [""])[0]
    return identifier if _is_brochure_key(identifier) else ""


def _is_brochure_key(value: str) -> bool:
    return re.fullmatch(r"[A-Za-z0-9-]{8,120}", value) is not None


def _to_offer(product: dict, period: str) -> LidlOffer | None:
    title = str(product.get("title") or "").strip()
    if not title or product.get("price") in (None, ""):
        return None
    brand = str(product.get("brand") or "").strip()
    name = f"{brand} {title}".strip() if brand and brand.casefold() not in title.casefold() else title
    return LidlOffer(
        name=_clean_text(name),
        price=_price(product.get("price"), product.get("currencySymbol")),
        old_price="",
        discount="",
        period=period,
        image_url=_image_url(product.get("image")),
    )


def _price(value: object, symbol: object) -> str:
    text = str(value).strip().replace(".", ",")
    mark = str(symbol).strip() if isinstance(symbol, str) else ""
    if mark and not text.endswith(mark):
        return f"{text} {mark}"
    return text


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


def _period(start: object, end: object) -> str:
    start_text = _format_date(start)
    end_text = _format_date(end)
    if start_text and end_text:
        return f"{start_text} – {end_text}"
    return start_text or end_text


def _format_date(value: object) -> str:
    if not isinstance(value, str) or not value:
        return ""
    try:
        return datetime.fromisoformat(value).strftime("%d.%m.%Y")
    except ValueError:
        return value[:10]


def _clean_text(value: str) -> str:
    cleaned = "".join(char for char in value if unicodedata.category(char) != "Cf")
    return " ".join(cleaned.split())
