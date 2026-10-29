import json
import os
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import django
import pytest
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from models.Tools.lidl_discount_tool import LidlDiscountTool, LidlOffer, LidlStore


OVERVIEW = {
    "categories": [
        {
            "name": "Filial-Angebote",
            "subcategories": [
                {
                    "name": "Unsere Aktionsprospekte",
                    "flyers": [
                        {
                            "name": "Aktionsprospekt",
                            "title": "12.10.2026 – 17.10.2026",
                            "offerStartDate": "2026-10-12",
                            "offerEndDate": "2026-10-17",
                            "flyerJson": "https://endpoints.leaflets.schwarz/v4/flyer?flyer_identifier=aktionsprospekt-national&client=lidl",
                            "regions": [{"type": "national", "code": "0"}],
                        },
                        {
                            "name": "Aktionsprospekt",
                            "title": "12.10.2026 – 17.10.2026",
                            "offerStartDate": "2026-10-12",
                            "offerEndDate": "2026-10-17",
                            "flyerJson": "https://endpoints.leaflets.schwarz/v4/flyer?flyer_identifier=aktionsprospekt-berlin&client=lidl",
                            "regions": [{"type": "offer_region", "code": "24"}],
                        },
                        {
                            "name": "Aktionsprospekt",
                            "title": "12.10.2026 – 17.10.2026",
                            "offerStartDate": "2026-10-12",
                            "offerEndDate": "2026-10-17",
                            "flyerJson": "https://endpoints.leaflets.schwarz/v4/flyer?flyer_identifier=aktionsprospekt-hamburg&client=lidl",
                            "regions": [{"type": "offer_region", "code": "15"}],
                        },
                    ],
                }
            ],
        }
    ]
}

STORES = {
    "10115": {
        "storeKey": "DE6273",
        "name": "Berlin - Leipziger Straße",
        "locality": "Berlin-Mitte",
        "postalCode": "10117",
        "distance": 200,
        "region": "24",
    },
    "Hamburg": {
        "storeKey": "DE5996",
        "name": "Hamburg - Wilstorf",
        "locality": "Hamburg-Harburg",
        "postalCode": "21079",
        "distance": 400,
        "region": "15",
    },
}


def _response(payload):
    response = MagicMock()
    response.json.return_value = payload
    return response


def _session_for(place: str) -> MagicMock:
    store = STORES[place]
    session = MagicMock()

    def fake_get(url, params=None, headers=None, timeout=None):
        if "autocomplete" in url:
            return _response([store])
        if "stores-frontend" in url:
            assert params["object_number"] == f"DE{store['storeKey'][2:].zfill(5)}"
            return _response({"items": [{"marketingData": {"offerRegion": int(store["region"])}}]})
        return _response(OVERVIEW)

    session.get.side_effect = fake_get
    return session


def test_search_stores_uses_regional_brochure_for_place() -> None:
    berlin = LidlDiscountTool(session=_session_for("10115")).search_stores("10115", today=date(2026, 10, 17))
    hamburg = LidlDiscountTool(session=_session_for("Hamburg")).search_stores("Hamburg", today=date(2026, 10, 17))

    assert berlin == [
        LidlStore(store_key="aktionsprospekt-berlin", label="Berlin-Mitte (10117) · 12.10.2026 – 17.10.2026")
    ]
    assert hamburg == [
        LidlStore(store_key="aktionsprospekt-hamburg", label="Hamburg-Harburg (21079) · 12.10.2026 – 17.10.2026")
    ]
    assert berlin[0].store_key != hamburg[0].store_key


def test_search_stores_rejects_unknown_place() -> None:
    session = MagicMock()
    session.get.return_value = _response([])

    with pytest.raises(Exception, match="keine Lidl-Filiale"):
        LidlDiscountTool(session=session).search_stores("Nirgendwo", today=date(2026, 10, 17))


def test_get_discounts_reads_brochure_products() -> None:
    session = MagicMock()
    response = MagicMock()
    response.json.return_value = {
        "flyer": {
            "offerStartDate": "2026-10-12",
            "offerEndDate": "2026-10-17",
            "products": {
                "1": {
                    "title": "Herren Kaschmirpullover",
                    "brand": "STRENESSE",
                    "price": "49.99",
                    "currencySymbol": "€",
                    "image": "https://www.lidl.de/assets/pullover.jpg",
                }
            },
        }
    }
    session.get.return_value = response

    offers = LidlDiscountTool(session=session).get_discounts("aktionsprospekt-aktuell")

    assert offers == [
        LidlOffer(
            name="STRENESSE Herren Kaschmirpullover",
            price="49,99 €",
            old_price="",
            discount="",
            period="12.10.2026 – 17.10.2026",
            image_url="https://www.lidl.de/assets/pullover.jpg",
        )
    ]


def test_get_discounts_rejects_unexpected_store_key() -> None:
    with pytest.raises(Exception):
        LidlDiscountTool(session=MagicMock()).get_discounts("../secret")


def test_product_lists_for_autocomplete() -> None:
    catalog = json.loads((Path(__file__).parents[1] / "static" / "products.json").read_text(encoding="utf-8"))

    assert len(catalog["kategorien"]) >= 60
    assert len(catalog["produkte"]) >= 200
    assert "Milchprodukte" in catalog["kategorien"]
    assert "Spaghetti" in catalog["produkte"]
    assert len(catalog["marken"]) >= 150
    assert "Milka" in catalog["marken"]
    assert "Milbona" in catalog["marken"]
    assert len(catalog["kategorien"]) == len({name.casefold() for name in catalog["kategorien"]})
    assert len(catalog["produkte"]) == len({name.casefold() for name in catalog["produkte"]})
    assert len(catalog["marken"]) == len({name.casefold() for name in catalog["marken"]})


def test_start_page_shows_discount_search() -> None:
    response = Client(HTTP_HOST="localhost").get("/")

    assert response.status_code == 200
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    content = response.content.decode()
    assert "rabattparty-logo.png" in content
    assert "Website under construction" not in content
    assert 'id="construction-ok"' not in content
    assert "<h1 class=\"search-title\">Einkaufszettel optimieren</h1>" in content
    assert "Feier mit uns und spare bares Geld" in content
    assert "Komm auf unsere Rabattparty" not in content
    assert 'name="wo"' in content
    assert 'name="umkreis"' in content
    assert "50 km" in content
    assert 'name="maerkte"' in content
    assert 'type="checkbox"' not in content
    assert 'id="markt"' in content
    assert "Supermarkt wählen" in content
    assert 'value="lidl"' in content
    assert 'value="globus"' in content
    assert "Real" in content
    assert "Globus" in content
    assert "Marktkauf" in content
    assert "Müller" not in content
    assert "Spar" in content
    assert "katalog.json" in content
    assert "Lidl" in content
    assert "Edeka" in content
    assert "markets/lidl.svg" not in content
    assert 'name="kategorie"' not in content
    assert 'name="unterkategorie"' not in content
    assert "Einkaufszettel erstellen" in content
    assert 'id="chosen-products"' in content
    assert "Produkt hinzufügen" in content
    assert 'id="produkt"' not in content
    assert "Einkaufszettel optimieren" in content
    assert "Unsere Mission" in content
    assert "Rabattalarm" in content
    assert content.index("Einkaufszettel optimieren") < content.index("Unsere Mission")
    assert content.index("Unsere Mission") < content.index("Rabattalarm")
    assert "KI-Individualsuche" not in content
    assert "Produktnewsletter" not in content
    assert 'class="top-nav"' in content
    assert 'class="login-form"' in content
    assert 'name="password"' in content
    assert "Anmelden" in content
    assert "Detailssuche" not in content
    assert "Preisentwicklung verfolgen" not in content
    assert 'href="/impressum/"' in content
    assert "Jetzt Produkte finden" in content
    assert 'id="waiting"' in content
    assert 'class="spinner"' in content
    assert 'data-wait-ms="2000"' in content
    assert "Produkte werden gesucht" in content
    assert 'name="ziel" value="preis" checked' in content
    assert "Gesundheitsoptimierung" in content
    assert "CO2 Abdruck" in content
    assert 'name="kriterien"' in content
    assert "Individuelle KI-Suche" in content
    assert "Eigene Kriterien für die Optimierung beschreiben" in content
    assert "CO2-Abdruck-Optimierung" not in content
    assert content.count('class="optimize-choice"') == 3
    assert "Zufällige Produkte" in content
    assert content.count("<li data-name=") == 10
    assert content.count('class="product-photo"') == 10
    assert 'class="store-flag"' not in content
    assert "Historiker-Tool" not in content


def test_impressum_lists_provider_details() -> None:
    response = Client(HTTP_HOST="localhost").get("/impressum/")

    assert response.status_code == 200
    content = response.content.decode()
    assert "Angaben gemäß § 5 DDG" in content
    assert "Dr. Adel Nasser" in content
    assert "Richard-Wagner-Str. 27" in content
    assert "73207 Plochingen" in content
    assert "info@cvboostai.de" in content
    assert "0176 22699702" in content
    assert "DE278675449" in content
    assert "§ 18 Abs. 2 MStV" in content
    assert 'href="https://www.geonames.org/"' in content
    assert "Creative Commons Namensnennung 4.0" in content
    assert "ADEME, AGRIBALYSE" in content
    assert "30. Juni 2026" in content
    assert 'href="https://data.ademe.fr/datasets/agribalyse-synthese"' in content
    assert 'href="https://doi.org/10.57745/XTENSJ"' in content
    assert 'href="https://www.etalab.gouv.fr/licence-ouverte-open-licence"' in content
    assert "keine Empfehlung oder Anerkennung durch die ADEME" in content


def test_lidl_page_lists_discounts(monkeypatch) -> None:
    class FakeTool:
        def search_stores(self, location: str):
            assert location == "10115"
            return [LidlStore(store_key="aktionsprospekt-aktuell", label="Aktionsprospekt für 10115")]

        def get_discounts(self, store_key: str):
            assert store_key == "aktionsprospekt-aktuell"
            return [
                LidlOffer(
                    name="MALTESERS",
                    price="3,99 €",
                    old_price="",
                    discount="",
                    period="12.10.2026 – 17.10.2026",
                    image_url="https://www.lidl.de/assets/maltesers.jpg",
                )
            ]

    monkeypatch.setattr("views.lidl_view.LidlDiscountTool", FakeTool)
    response = Client(HTTP_HOST="localhost").post("/lidl/", {"location": "10115"})
    content = response.content.decode()

    assert response.status_code == 200
    assert "MALTESERS" in content
    assert "3,99 €" in content
    assert "Aktionsprospekt für 10115" in content
    assert "maltesers.jpg" in content
