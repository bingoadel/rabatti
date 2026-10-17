import os
from datetime import date
from unittest.mock import MagicMock

import django
import pytest
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agent_project.settings")
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
                            "flyerJson": "https://endpoints.leaflets.schwarz/v4/flyer?flyer_identifier=aktionsprospekt-aktuell&client=lidl",
                            "regions": [{"type": "national", "code": "0"}],
                        },
                        {
                            "name": "Aktionsprospekt",
                            "title": "19.10.2026 – 24.10.2026",
                            "offerStartDate": "2026-10-19",
                            "offerEndDate": "2026-10-24",
                            "flyerJson": "https://endpoints.leaflets.schwarz/v4/flyer?flyer_identifier=aktionsprospekt-naechste&client=lidl",
                            "regions": [{"type": "national", "code": "0"}],
                        },
                    ],
                }
            ],
        }
    ]
}


def test_search_stores_uses_current_public_brochure() -> None:
    session = MagicMock()
    response = MagicMock()
    response.json.return_value = OVERVIEW
    session.get.return_value = response

    brochures = LidlDiscountTool(session=session).search_stores("10115", today=date(2026, 10, 17))

    assert brochures == [
        LidlStore(
            store_key="aktionsprospekt-aktuell",
            label="Aktionsprospekt 12.10.2026 – 17.10.2026 für 10115",
        )
    ]
    assert "leaflets.schwarz" in session.get.call_args.args[0]


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


def test_start_page_offers_both_tools() -> None:
    response = Client().get("/")

    assert response.status_code == 200
    content = response.content.decode()
    assert "Historiker-Tool" in content
    assert "Lidl-Tool" in content
    assert 'href="/historiker/"' in content
    assert 'href="/lidl/"' in content


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

    monkeypatch.setattr("views.lidl.LidlDiscountTool", FakeTool)
    response = Client().post("/lidl/", {"location": "10115"})
    content = response.content.decode()

    assert response.status_code == 200
    assert "MALTESERS" in content
    assert "3,99 €" in content
    assert "Aktionsprospekt für 10115" in content
    assert "maltesers.jpg" in content
