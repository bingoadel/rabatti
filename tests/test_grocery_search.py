import os
import sqlite3

import django
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from models.product_labels import ProductLabels
from models.product_search import DB_PATH, ProductSearch
from models.store_locations import StoreLocations


def test_grocery_database_has_1100_products() -> None:
    connection = sqlite3.connect(DB_PATH)
    try:
        columns = [row[1] for row in connection.execute("PRAGMA table_info(grocery_product)")]
        count = connection.execute("SELECT COUNT(*) FROM grocery_product").fetchone()[0]
        distinct = connection.execute("SELECT COUNT(DISTINCT product_name) FROM grocery_product").fetchone()[0]
        images = connection.execute(
            "SELECT COUNT(*) FROM grocery_product WHERE image_url LIKE 'https://%'"
        ).fetchone()[0]
        sugar = connection.execute(
            "SELECT image_url FROM grocery_product WHERE product_name = 'Dr. Oetker Vanillinzucker'"
        ).fetchone()[0]
        milk = connection.execute(
            "SELECT image_url FROM grocery_product WHERE product_name = 'Milbona H-Milch 1,5 %'"
        ).fetchone()[0]
    finally:
        connection.close()

    assert columns[:6] == ["id", "gtin_ean", "product_name", "brand", "manufacturer", "main_category"]
    assert "special_pricing" in columns
    assert "store_address" in columns
    assert count == 1100
    assert images == 1100
    assert sugar.startswith("https://")
    assert "Sugar.jpg" not in sugar
    assert "sugar" in sugar.casefold()
    assert "openfoodfacts.org" in milk
    assert distinct == 1100
    assert len(ProductSearch.load_products()) == 1100
    rows = ProductSearch.load_products()
    assert rows[0]["product_name"] == "Milbona H-Milch 1,5 %"
    assert "Augsburg-Oberhausen" in rows[0]["store_address"]
    extra = StoreLocations.annotate_distance(rows[200:], "Augsburg")
    assert len(extra) == 900
    assert all(row["distance_km"] is not None and row["distance_km"] <= 50 for row in extra)
    assert all("Augsburg" in row["store_address"] for row in extra)


def test_store_markers_are_fixed_to_the_branch() -> None:
    lidl = StoreLocations.stores_for_map([_map_product("lidl", "Lidl", 1.6, 0.7)])
    point = StoreLocations.store_point("Augsburg", (1.6, 0.7))
    assert (lidl[0]["lat"], lidl[0]["lng"]) == point
    assert StoreLocations.map_focus(lidl, "Augsburg") == point

    aldi = StoreLocations.stores_for_map([_map_product("aldi", "Aldi", 2.8, -1.4)])
    assert (aldi[0]["lat"], aldi[0]["lng"]) != point


def _map_product(store_id, name, north, east):
    """Eine Produktzeile, aus der die Karte eine Supermarkt-Fahne baut."""
    return {
        "store_id": store_id,
        "supermarket_name": name,
        "store_address": "Augsburg",
        "north_km": north,
        "east_km": east,
        "product_name": "H-Milch",
        "price_label": "1,11 €",
    }


def test_search_form_reads_augsburg_products() -> None:
    markets = ["lidl", "aldi", "rewe", "edeka", "kaufland", "penny"]
    response = Client(HTTP_HOST="localhost").get(
        "/",
        {"wo": "Augsburg", "umkreis": "10", "unterkategorie": "H-Milch 1,5 %", "preisart": "Alle", "maerkte": markets},
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert "Augsburg, Umkreis 10 km" in content
    assert "Leider konnten wir keine Produkte" not in content
    assert "Milbona H-Milch 1,5 %" in content
    assert "/static/products/product-milch.jpg" in content
    assert 'class="product-photo"' in content
    assert 'id="store-map"' in content
    assert "leaflet.js" in content
    assert "10115" not in content
    assert content.count('class="store-flag"') == 4

    nearby = Client(HTTP_HOST="localhost").get(
        "/",
        {"wo": "Augsburg", "umkreis": "5", "unterkategorie": "H-Milch 1,5 %", "preisart": "Alle", "maerkte": markets},
    )
    assert nearby.content.decode().count('class="store-flag"') == 4


def test_search_form_filters_market_and_offer_type() -> None:
    lidl = Client(HTTP_HOST="localhost").get(
        "/",
        {"wo": "Augsburg", "unterkategorie": "H-Milch 1,5 %", "maerkte": "lidl", "preisart": "Alle"},
    )
    lidl_content = lidl.content.decode()
    assert "Milbona H-Milch 1,5 %" in lidl_content
    assert "Milsani H-Milch 3,5 %" not in lidl_content
    assert 'class="store-flag" data-lat="' in lidl_content

    discount = ProductSearch.search_products("Augsburg", offer_type="Rabatt", markets=["lidl"])
    assert discount == []


def test_search_requires_place_market_or_product_and_known_values() -> None:
    empty = Client(HTTP_HOST="localhost").get("/", {"umkreis": "10", "preisart": "regulärer Preis"})
    empty_content = empty.content.decode()
    assert "Bitte einen Ort und einen Supermarkt angeben. Bei Kategorie, Unterkategorie und Produkt genügt eine Angabe." in empty_content
    assert "Milbona H-Milch 1,5 %" not in empty_content

    place_only = Client(HTTP_HOST="localhost").get("/", {"wo": "Augsburg", "maerkte": "lidl"})
    assert "Bitte einen Ort und einen Supermarkt angeben. Bei Kategorie, Unterkategorie und Produkt genügt eine Angabe." in place_only.content.decode()

    without_market = Client(HTTP_HOST="localhost").get(
        "/",
        {"wo": "Augsburg", "unterkategorie": "H-Milch 1,5 %"},
    )
    assert "Bitte einen Ort und einen Supermarkt angeben. Bei Kategorie, Unterkategorie und Produkt genügt eine Angabe." in without_market.content.decode()

    without_place = Client(HTTP_HOST="localhost").get(
        "/",
        {"maerkte": "lidl", "unterkategorie": "H-Milch 1,5 %"},
    )
    assert "Bitte einen Ort und einen Supermarkt angeben. Bei Kategorie, Unterkategorie und Produkt genügt eine Angabe." in without_place.content.decode()

    category_only = Client(HTTP_HOST="localhost").get(
        "/",
        {"wo": "Augsburg", "maerkte": "lidl", "kategorie": "Molkereiprodukte", "preisart": "Alle"},
    )
    assert "Milbona H-Milch 1,5 %" in category_only.content.decode()

    unknown = Client(HTTP_HOST="localhost").get("/", {"wo": "Nirgendwo"})
    assert "Bitte einen Ort aus den Vorschlägen wählen." in unknown.content.decode()

    regular = Client(HTTP_HOST="localhost").get(
        "/",
        {"wo": "Augsburg", "produkt": "Milbona H-Milch 1,5 %, 1 l", "maerkte": "lidl"},
    )
    regular_content = regular.content.decode()
    assert "Milbona H-Milch 1,5 %" in regular_content
    assert 'title="reg. Preis"' in regular_content
    assert "Milsani H-Milch 3,5 %" not in regular_content

    catalog = Client(HTTP_HOST="localhost").get("/katalog.json")
    payload = catalog.json()
    assert "86154 Augsburg" in payload["orte"]
    assert "86150 Augsburg" in payload["orte"]
    assert "87719 Mindelheim" in payload["orte"]
    assert "78141 Schönwald im Schwarzwald" in payload["orte"]
    assert "95173 Schönwald" in payload["orte"]
    assert "86154" not in payload["orte"]
    assert len(payload["orte"]) > 50000

    by_postcode = Client(HTTP_HOST="localhost").get(
        "/",
        {"wo": "86154", "umkreis": "10", "unterkategorie": "H-Milch 1,5 %", "preisart": "Alle", "maerkte": "lidl"},
    )
    assert "Milbona H-Milch 1,5 %" in by_postcode.content.decode()
    assert "Augsburg" in by_postcode.content.decode()
    assert "regulärer Preis" == payload["preisarten"][0]
    dairy = next(category for category in payload["kategorien"] if category["name"] == "Molkereiprodukte")
    assert dairy["anzahl"] == sum(sub["anzahl"] for sub in dairy["unterkategorien"])
    assert dairy["anzahl"] == sum(len(sub["produkte"]) for sub in dairy["unterkategorien"])
    assert all(category["anzahl"] > 0 for category in payload["kategorien"])


def test_empty_exact_search_shows_nearest_alternatives() -> None:
    response = Client(HTTP_HOST="localhost").get(
        "/",
        {
            "wo": "Augsburg",
            "umkreis": "10",
            "unterkategorie": "H-Milch 1,5 %",
            "maerkte": "lidl",
            "preisart": "Rabatt",
        },
    )
    content = response.content.decode()
    assert "Leider konnten wir keine Produkte mit genau den gewählten Kriterien finden, aber ohne die Preisart „Rabatt“ gibt es diese Produkte." in content
    assert "Milbona H-Milch 1,5 %" in content
    assert "Milsani H-Milch 3,5 %" not in content
    assert "Augsburg, Umkreis 10 km" in content


def test_true_boolean_properties_show_as_checked_text() -> None:
    rows = {row["product_name"]: row for row in ProductSearch.load_products()}
    assert ProductLabels.present(rows["Coca-Cola Cola"])["flags"] == ["Pfand"]
    assert ProductLabels.present(rows["Berchtesgadener Land Bio-Frischmilch 3,8 %"])["flags"] == ["Bio"]
    assert ProductLabels.present(rows["Milbona H-Milch 1,5 %"])["flags"] == []

    plain = Client(HTTP_HOST="localhost").get(
        "/",
        {"wo": "Berlin", "produkt": "Milbona H-Milch 1,5 %, 1 l", "maerkte": "lidl", "preisart": "Alle"},
    )
    plain_content = plain.content.decode()
    assert ">Bio</span>" not in plain_content
    assert ">Pfand</span>" not in plain_content

    organic = Client(HTTP_HOST="localhost").get(
        "/",
        {"wo": "München", "produkt": "Bio Organic H-Milch 1,5 %, 1 l", "maerkte": "lidl", "preisart": "Alle"},
    )
    organic_content = organic.content.decode()
    assert 'class="product-flag"' in organic_content
    assert ">Bio</span>" in organic_content
    assert ">Pfand</span>" not in organic_content
    assert 'class="flag-check"' in organic_content


def test_start_sample_includes_bio_and_deposit_products() -> None:
    shown = ProductSearch.sample_products(10)
    flags = {flag for row in shown for flag in row["flags"]}
    assert len(shown) == 10
    assert "Bio" in flags

    page = Client(HTTP_HOST="localhost").get("/")
    content = page.content.decode()
    assert "Zufällige Produkte" in content
    assert ">Bio</span>" in content
    assert 'class="flag-icon"' in content
    assert 'class="flag-check"' in content


def test_results_sort_by_name_and_distance() -> None:
    markets = ["lidl", "aldi", "rewe", "edeka", "kaufland", "penny"]
    found = ProductSearch.search_products(
        "Augsburg",
            subcategory="H-Milch 1,5 %",
        markets=markets,
        offer_type="Alle",
        radius_km=10,
    )
    ranked = StoreLocations.annotate_distance(found, "Augsburg")
    by_distance = ProductSearch.sort_products(ranked, "distance")
    distances = [row["distance_km"] for row in by_distance]
    assert distances == sorted(distances)
    assert distances[0] < distances[-1]
    by_distance_desc = ProductSearch.sort_products(ranked, "distance", descending=True)
    far_first = [row["distance_km"] for row in by_distance_desc]
    assert far_first == sorted(distances, reverse=True)
    by_name = ProductSearch.sort_products(ranked, "name")
    names = [ProductLabels.fold(row["product_name"]) for row in ranked]
    assert [ProductLabels.fold(row["product_name"]) for row in by_name] == sorted(names)
    assert [ProductLabels.fold(row["product_name"]) for row in ProductSearch.sort_products(ranked, "name", descending=True)] == sorted(names, reverse=True)
    by_price = ProductSearch.sort_products(ranked, "price")
    prices = [row["current_price"] for row in by_price]
    assert prices == sorted(prices)
    assert prices[0] < prices[-1]
    assert [row["current_price"] for row in ProductSearch.sort_products(ranked, "price", descending=True)] == sorted(prices, reverse=True)

    page = Client(HTTP_HOST="localhost").get(
        "/",
        {"wo": "Augsburg", "umkreis": "10", "unterkategorie": "H-Milch 1,5 %", "preisart": "Alle", "maerkte": markets},
    )
    content = page.content.decode()
    assert content.index('class="city-map"') < content.index('class="sort-buttons"')
    assert content.index('class="sort-buttons"') < content.index('class="product-results"')
    assert content.count('data-sort="name"') == 1
    assert content.count('data-sort="distance"') == 1
    assert content.count('data-sort="price"') == 1
    assert ">Name</button>" in content
    assert ">Abstand</button>" in content
    assert ">Preis</button>" in content
    prices_on_page = [value for value in content.split('data-price="')[1:]]
    assert prices_on_page
    assert all("," not in value.split('"', 1)[0] for value in prices_on_page)
    distances_on_page = [value.split('"', 1)[0] for value in content.split('data-distance="')[1:]]
    assert len(set(distances_on_page)) > 1
    assert all("," not in value for value in distances_on_page)

    start = Client(HTTP_HOST="localhost").get("/")
    start_content = start.content.decode()
    assert 'data-sort="distance" disabled' in start_content
    assert 'data-sort="price"' in start_content


def test_shopping_list_searches_named_products_at_one_market() -> None:
    response = Client(HTTP_HOST="localhost").get(
        "/",
        {
            "wo": "Augsburg",
            "umkreis": "10",
            "maerkte": "lidl",
            "produkte": ["H-Milch 1,5 %", "Hummus"],
        },
    )
    content = response.content.decode()
    assert response.status_code == 200
    assert "Milbona H-Milch 1,5 %" in content
    assert "Hummus," in content
    assert "Diese Produkte gibt es dort nicht" not in content
    assert 'name="produkte" value="H-Milch 1,5 %"' in content
    assert 'name="produkte" value="Hummus"' in content
    assert 'value="lidl" selected' in content

    catalog = Client(HTTP_HOST="localhost").get("/katalog.json")
    kinds = catalog.json()["produktarten"]
    for name in (
        "Magerquark",
        "Quark (20 %)",
        "Bandnudeln",
        "Rigatoni",
        "Spaghetti",
        "Hirtenkäse",
        "Tilsiter",
        "Schimmelkäse",
        "Hummus",
        "Oliven grün",
        "Oliven schwarz",
        "Kiwi grün",
        "Kiwi gelb",
        "Aubergine",
        "Zucchini",
        "Süßkartoffeln",
        "Blattpetersilie",
        "Paprikapulver edelsüß",
        "Kreuzkümmel",
        "Kurkuma",
        "Lorbeerblätter",
        "Italienische Kräuter",
        "Mettwurst",
        "Presswurst",
        "Leberkäse",
        "Rindersalami",
        "Donut",
        "Bagel",
        "Laugenstange",
        "Nussecke",
        "Krapfen",
    ):
        assert name in kinds
    assert "Klopapier (2-lagig)" not in kinds
    assert "Geschirrspülmittel" not in kinds
    assert "Milbona H-Milch 1,5 %" not in kinds
    assert "Coca-Cola Cola" not in kinds


def test_product_cards_expand_description_and_additives() -> None:
    milk = ProductLabels.present(ProductSearch.load_products()[0])
    assert "Trinkmilch" in milk["description"]
    assert milk["additives"] == []

    cola = ProductLabels.present(next(row for row in ProductSearch.load_products() if row["product_name"] == "Coca-Cola Cola"))
    assert "Natriumbenzoat (E 211, Konservierungsstoff)" in cola["additives"]
    assert "Citronensäure (E 330, Säuerungsmittel)" in cola["additives"]

    yeast = ProductLabels.present(next(row for row in ProductSearch.load_products() if row["product_name"] == "Gut & Günstig Backhefe"))
    assert yeast["additives"] == []

    page = Client(HTTP_HOST="localhost").get(
        "/",
        {"wo": "Berlin", "produkt": "Milbona H-Milch 1,5 %, 1 l", "maerkte": "lidl", "preisart": "Alle"},
    )
    content = page.content.decode()
    assert 'class="product-details"' in content
    assert "<summary>Details</summary>" in content
    assert "Produktbeschreibung" in content
    assert "Beispielsortiment mit Beispielpreis" in content
    assert "Konservierungs- und Zusatzstoffe" in content
    assert ">keine</p>" in content

    milk_page = Client(HTTP_HOST="localhost").get(
        "/",
        {
            "wo": "Augsburg",
            "umkreis": "10",
            "unterkategorie": "H-Milch 1,5 %",
            "preisart": "Alle",
            "maerkte": ["lidl", "aldi", "rewe", "edeka", "kaufland", "penny"],
        },
    )
    milk_content = milk_page.content.decode()
    assert "Milbona H-Milch 1,5 %" in milk_content
    assert ">keine</p>" in milk_content
