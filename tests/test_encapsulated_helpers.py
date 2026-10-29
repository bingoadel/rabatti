"""Prüft die Klassen, die früher freie Funktionen waren."""

import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from models.product_labels import ProductLabels
from models.product_search import ProductSearch
from models.store_locations import StoreLocations
from views.next_url import NextUrl


def test_product_labels_use_german_price_and_quantity() -> None:
    assert ProductLabels.fold("Äpfel") == "aepfel"
    assert ProductLabels.euro(1.5) == "1,50 €"
    assert ProductLabels.quantity_label(1.5, "kg") == "1,5 kg"
    assert ProductLabels.per_unit("ml") == "l"
    assert ProductLabels.per_unit("Stück") == "Stück"


def test_store_locations_resolve_a_place_and_a_zero_distance() -> None:
    augsburg = StoreLocations.origin_for("Augsburg")
    assert augsburg == (48.3705, 10.8978)
    assert StoreLocations.distance_km(augsburg, augsburg) == 0
    assert StoreLocations.place_locality("86150 Augsburg") == "Augsburg"
    assert StoreLocations.resolve_place("86150", ["86150 Augsburg"]) == "Augsburg"
    assert StoreLocations.resolve_place("irgendwo", ["86150 Augsburg"]) is None


def test_product_search_sorts_by_price_and_keeps_the_catalog_spelling() -> None:
    assert ProductSearch.canonical("milch", ["Milch"]) == "Milch"
    products = [
        {"product_name": "B", "current_price": 2},
        {"product_name": "A", "current_price": 1},
    ]
    ordered = ProductSearch.sort_products(products, "price")
    assert [row["product_name"] for row in ordered] == ["A", "B"]


def test_next_url_keeps_only_a_local_path() -> None:
    assert NextUrl.from_request(SimpleNamespace(POST={"next": "/start"})) == "/start"
    assert NextUrl.from_request(SimpleNamespace(POST={"next": "https://example.test"})) == "/"
    assert NextUrl.from_request(SimpleNamespace(POST={"next": "//example.test"})) == "/"
