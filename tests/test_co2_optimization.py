"""CO2-Optimierung mit Agribalyse-Richtwerten."""

import os
from io import BytesIO

import django
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from pypdf import PdfReader

from models.co2_factors import SOURCE, Co2Factors
from models.co2_optimizer import Co2Optimizer
from models.product_kinds import PRODUCT_KINDS
from models.results_pdf import ResultsPdf


def offer(name, kind, price, quantity, unit, organic=False):
    return {
        "product_name": name,
        "product_kind": kind,
        "current_price": price,
        "net_quantity": quantity,
        "unit": unit,
        "is_organic": organic,
        "calculated_base_price": price / quantity * (1000 if unit in {"g", "ml"} else 1),
    }


def test_every_kind_has_an_agribalyse_factor() -> None:
    assert "ADEME, AGRIBALYSE" in SOURCE
    assert "30.06.2026" in SOURCE
    assert "https://data.ademe.fr/datasets/agribalyse-synthese" in SOURCE
    assert "https://www.etalab.gouv.fr/licence-ouverte-open-licence" in SOURCE
    for kind in PRODUCT_KINDS:
        assert Co2Factors.co2_kg_per_kg(kind) > 0
        assert Co2Factors.reference_code(kind)


def test_organic_row_is_used_only_when_agribalyse_has_a_farm_pair() -> None:
    assert Co2Factors.co2_kg_per_kg("Hähnchenbrust", organic=True) > Co2Factors.co2_kg_per_kg("Hähnchenbrust")
    assert Co2Factors.co2_kg_per_kg("Äpfel", organic=True) > Co2Factors.co2_kg_per_kg("Äpfel")
    assert Co2Factors.co2_kg_per_kg("Rindersteak", organic=True) > Co2Factors.co2_kg_per_kg("Rindersteak")
    assert Co2Factors.co2_kg_per_kg("Schweineschnitzel", organic=True) > Co2Factors.co2_kg_per_kg("Schweineschnitzel")
    assert Co2Factors.co2_kg_per_kg("H-Milch 1,5 %", organic=True) == Co2Factors.co2_kg_per_kg("H-Milch 1,5 %")
    assert Co2Factors.co2_kg_per_kg("Tomaten", organic=True) == Co2Factors.co2_kg_per_kg("Tomaten")
    assert Co2Factors.co2_kg_per_kg("Birnen", organic=True) == Co2Factors.co2_kg_per_kg("Birnen")
    assert Co2Factors.co2_kg_per_kg("Hähnchengewürz", organic=True) == Co2Factors.co2_kg_per_kg("Hähnchengewürz")
    assert Co2Factors.co2_basis("Hähnchenbrust", True) == "Bio-Zeile aus Agribalyse"
    assert Co2Factors.co2_basis("H-Milch 1,5 %", True) == "Bio-Packung, Agribalyse führt dafür keine eigene Zeile"


def test_lower_co2_pack_wins_even_when_it_is_not_organic() -> None:
    organic = offer("Bio-Brust", "Hähnchenbrust", 8.00, 500, "g", organic=True)
    conventional = offer("Brust", "Hähnchenbrust", 6.00, 500, "g")

    basket = Co2Optimizer.optimize_co2(
        [organic, conventional],
        {"Hähnchenbrust": {"measure": "mass", "amount": 0.4}},
    )

    assert basket.products[0]["product_name"] == "Brust"
    assert basket.products[0]["co2_basis"] == "konventionelle Zeile"
    assert basket.savings > 0
    assert "kg CO2e" in basket.products[0]["co2_label"]


def test_same_factor_keeps_the_cheaper_pack_and_saves_nothing() -> None:
    organic = offer("Bio-Milch", "H-Milch 1,5 %", 1.20, 1, "l", organic=True)
    conventional = offer("Milch", "H-Milch 1,5 %", 0.90, 1, "l")

    basket = Co2Optimizer.optimize_co2([organic, conventional], {"H-Milch 1,5 %": {"measure": "volume", "amount": 1}})

    assert basket.products[0]["product_name"] == "Milch"
    assert basket.savings == 0
    assert Co2Optimizer.format_co2(0) == "0,00 kg CO2e"
    assert basket.products[0]["co2_basis"] == "konventionelle Zeile"


def test_additives_do_not_change_the_factor() -> None:
    plain = offer("Brust", "Hähnchenbrust", 6.00, 500, "g")
    seasoned = offer("Gewürz-Brust", "Hähnchenbrust", 6.50, 500, "g")
    seasoned["additives"] = "Aroma"
    plain["description"] = "Beispiel"

    basket = Co2Optimizer.optimize_co2([seasoned, plain])

    assert basket.products[0]["product_name"] == "Brust"
    assert basket.savings == 0


def test_co2_goal_shows_the_sum_under_the_map_and_in_the_pdf() -> None:
    query = {
        "wo": "Augsburg",
        "umkreis": "10",
        "maerkte": "lidl",
        "produkte": "Hähnchenbrust",
        "ziel": "co2",
    }
    response = Client(HTTP_HOST="localhost").get("/", query)
    html = response.content.decode()

    assert response.status_code == 200
    assert html.count("<li data-name=") == 1
    assert "Summe des CO2-Abdrucks" in html
    assert "Ersparnis gegenüber den höchsten Abdrücken" in html
    assert "ADEME, AGRIBALYSE" in html
    assert 'href="https://www.etalab.gouv.fr/licence-ouverte-open-licence"' in html
    assert 'href="https://data.ademe.fr/datasets/agribalyse-synthese"' in html
    assert "konventionelle Zeile" in html
    assert "Bio-Zeile aus Agribalyse" not in html
    assert "(0 %)" not in html
    assert html.index('class="city-map"') < html.index("Summe des CO2-Abdrucks")
    assert html.index("Summe des CO2-Abdrucks") < html.index('class="pdf-download"')
    assert html.index('class="pdf-download"') < html.index("product-results")

    pdf = Client(HTTP_HOST="localhost").get("/ergebnisse.pdf", query)
    assert pdf["Content-Type"] == "application/pdf"
    text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(pdf.content)).pages)
    assert "Summe des CO2-Abdrucks" in text
    assert "ADEME, AGRIBALYSE" in text
    assert "konventionelle Zeile" in text


def test_pdf_builder_writes_the_co2_summary() -> None:
    payload = ResultsPdf.build_results_pdf(
        {
            "searched": True,
            "result_place": "Augsburg",
            "keep_radius": True,
            "radius": "10",
            "notice": "",
            "form_error": "",
            "co2_optimized": True,
            "co2_source": SOURCE,
            "basket_total_label": "2,16 kg CO2e",
            "savings_label": "1,19 kg CO2e",
            "savings_percent": 35,
            "products": [
                {
                    "product_name": "Milbona Hähnchenbrust",
                    "price_label": "6,00 €",
                    "co2_label": "2,16 kg CO2e",
                    "co2_basis": "konventionelle Zeile",
                    "savings_label": "1,19 kg CO2e",
                    "additives": [],
                    "description": "Beispiel",
                }
            ],
        }
    )
    text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(payload)).pages)
    assert "2,16 kg CO2e" in text
    assert "1,19 kg CO2e" in text
    assert "Je Produktart ist das Angebot" not in text
