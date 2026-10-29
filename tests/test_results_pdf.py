"""PDF-Download der Produktsuche."""

import os
from datetime import date
from io import BytesIO

import django
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from pypdf import PdfReader

from models.results_pdf import ResultsPdf


def test_results_heading_follows_the_search() -> None:
    assert ResultsPdf.results_heading(False, "", False, "10", "") == "Zufällige Produkte"
    assert ResultsPdf.results_heading(True, "Augsburg", True, "10", "") == "Augsburg, Umkreis 10 km"
    assert ResultsPdf.results_heading(True, "Augsburg", False, "10", "") == "Augsburg"
    assert ResultsPdf.results_heading(True, "", False, "10", "Leider nichts Genaues") == "Ähnliche Produkte"
    assert ResultsPdf.results_heading(True, "", False, "10", "") == "Alle Beispielprodukte"


def test_pdf_lists_offers_sum_and_additives() -> None:
    payload = ResultsPdf.build_results_pdf(
        {
            "searched": True,
            "result_place": "Augsburg",
            "keep_radius": True,
            "radius": "10",
            "notice": "",
            "form_error": "",
            "price_optimized": True,
            "basket_total_label": "3,70 €",
            "savings_label": "0,90 €",
            "savings_percent": 20,
            "products": [
                {
                    "product_name": "Hähnchenbrühe, 1 l",
                    "brand": "Kania",
                    "main_category": "Gewürze",
                    "quantity_label": "1 l",
                    "supermarket_name": "Lidl",
                    "store_address": "Augsburg",
                    "distance_km": 1.7,
                    "price_label": "1,11 €",
                    "base_price_label": "1,11 €/l",
                    "savings_label": "0,35 €",
                    "flags": ["Glutenfrei"],
                    "additives": [],
                    "description": "Beispielsortiment mit Beispielpreis.",
                },
                {
                    "product_name": "Hummus, 200 g",
                    "brand": "Kania",
                    "main_category": "Feinkost",
                    "quantity_label": "200 g",
                    "supermarket_name": "Lidl",
                    "store_address": "Augsburg",
                    "distance_km": 1.7,
                    "price_label": "2,59 €",
                    "base_price_label": "12,95 €/kg",
                    "savings_label": "0,55 €",
                    "flags": [],
                    "additives": ["Kaliumsorbat (E 202 Konservierungsstoff)"],
                    "description": "Beispielsortiment mit Beispielpreis.",
                },
            ],
        },
        generated_on=date(2026, 10, 28),
    )

    text = _pdf_text(payload)

    assert payload.startswith(b"%PDF")
    assert "Augsburg, Umkreis 10 km" in text
    assert "28.10.2026" in text
    assert "Hähnchenbrühe, 1 l" in text
    assert "1,11 €" in text
    assert "Glutenfrei" in text
    assert "Zusatzstoffe: keine" in text
    assert "Kaliumsorbat (E 202 Konservierungsstoff)" in text
    assert "Summe der gewählten Packungen: 3,70 €" in text
    assert "Je Produktart ist das Angebot" not in text
    assert "Gesamtersparnis gegenüber den teuersten Angeboten: 0,90 € (20 %)" in text
    assert "1,7 km" in text
    assert text.count("Beispielsortiment mit Beispielpreis.") == 1


def test_pdf_keeps_german_text_when_a_symbol_is_missing() -> None:
    text = _pdf_text(
        ResultsPdf.build_results_pdf(
            {
                "searched": True,
                "result_place": "Köln",
                "keep_radius": False,
                "radius": "10",
                "notice": "",
                "form_error": "",
                "products": [
                    {
                        "product_name": "Käse 🧀",
                        "brand": "Milbona",
                        "main_category": "Käse",
                        "quantity_label": "200 g",
                        "supermarket_name": "Lidl",
                        "store_address": "Köln",
                        "distance_km": None,
                        "price_label": "2,49 €",
                        "flags": [],
                        "additives": [],
                        "description": "",
                    }
                ],
            },
            generated_on=date(2026, 10, 28),
        )
    )

    assert "Käse" in text
    assert "Köln" in text
    assert "2,49 €" in text


def test_pdf_without_offers_says_there_are_none() -> None:
    text = _pdf_text(
        ResultsPdf.build_results_pdf(
            {
                "searched": True,
                "result_place": "Augsburg",
                "keep_radius": False,
                "radius": "10",
                "notice": "",
                "form_error": "",
                "products": [],
            },
            generated_on=date(2026, 10, 28),
        )
    )

    assert "Keine Treffer" in text


def test_search_page_offers_the_same_results_as_pdf() -> None:
    query = {
        "wo": "Augsburg",
        "umkreis": "10",
        "maerkte": "lidl",
        "produkte": ["H-Milch 1,5 %", "Hummus"],
        "mengen": ["1", "200"],
        "ziel": "preis",
    }
    client = Client(HTTP_HOST="localhost")
    page = client.get("/", query)
    download = client.get("/ergebnisse.pdf", query)
    html = page.content.decode()
    text = _pdf_text(download.content)

    assert page.status_code == 200
    assert 'class="pdf-download"' in html
    assert 'class="download-icon"' in html
    assert "Produktliste herunterladen" in html
    assert html.index("Gesamtersparnis") < html.index('class="pdf-download"')
    assert html.index('class="pdf-download"') < html.index('class="product-results"')
    assert "ergebnisse.pdf?" in html
    assert "wo=Augsburg" in html
    assert download.status_code == 200
    assert download["Content-Type"] == "application/pdf"
    assert download["Content-Disposition"] == 'attachment; filename="einkaufszettel.pdf"'
    assert "Milbona H-Milch 1,5 %, 1 l" in text
    assert "Hummus" in text
    assert "Summe der gewählten Packungen" in text
    assert "Augsburg, Umkreis 10 km" in text


def test_homepage_has_no_pdf_download() -> None:
    content = Client(HTTP_HOST="localhost").get("/").content.decode()

    assert "Produktliste herunterladen" not in content


def _pdf_text(payload):
    """Text aller PDF-Seiten, Leerzeichen zusammengezogen.

    Summary:
        Die Prüfung liest den sichtbaren Text, nicht die Rohbytes der Schrift.
    """
    reader = PdfReader(BytesIO(payload))
    raw = " ".join(page.extract_text() or "" for page in reader.pages)
    return " ".join(raw.split())
