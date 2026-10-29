import os
from decimal import Decimal

import django
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from models.price_optimizer import PriceOptimizer
from models.product_kinds import PRODUCT_KINDS
from models.product_labels import ProductLabels
from models.product_search import ProductSearch
from models.shopping_demand import ShoppingDemand


def offer(name, kind, price, quantity, unit, base=None):
    row = {
        "product_name": name,
        "product_kind": kind,
        "current_price": price,
        "net_quantity": quantity,
        "unit": unit,
    }
    if base is not None:
        row["calculated_base_price"] = base
    return row


def test_larger_pack_wins_when_its_price_per_kilo_is_lower() -> None:
    small = offer("Klein, 500 g", "Brot", 1.69, 500, "g")
    large = offer("Groß, 1000 g", "Brot", 2.79, 1000, "g")

    chosen = PriceOptimizer.choose_cheapest([small, large])

    assert chosen is large
    assert PriceOptimizer.offer_base_price(small) == 3.38
    assert PriceOptimizer.offer_base_price(large) == 2.79


def test_equal_base_price_keeps_the_cheaper_pack_then_the_name() -> None:
    expensive = offer("Beta, 1 kg", "Reis", 2.00, 1, "kg", base=2.0)
    cheap = offer("Alpha, 1 kg", "Reis", 2.00, 1, "kg", base=2.0)
    smaller = offer("Gamma, 500 g", "Reis", 1.00, 500, "g", base=2.0)

    assert PriceOptimizer.choose_cheapest([expensive, smaller, cheap]) is smaller
    assert PriceOptimizer.choose_cheapest([expensive, cheap]) is cheap


def test_mixed_units_are_not_converted_into_each_other() -> None:
    by_weight = offer("Pizza, 400 g", "Tiefkühlpizza", 2.79, 400, "g", base=6.975)
    by_piece = offer("Pizza, 3 Stück", "Tiefkühlpizza", 5.99, 3, "Stück", base=1.996666)

    assert PriceOptimizer.measure_of("g") == PriceOptimizer.measure_of("kg") == "mass"
    assert PriceOptimizer.measure_of("ml") == PriceOptimizer.measure_of("l") == "volume"
    assert PriceOptimizer.measure_of("Stück") == "count"
    assert PriceOptimizer.choose_cheapest([by_piece, by_weight]) is by_weight


def test_basket_keeps_list_order_and_sums_pack_prices() -> None:
    milk_small = offer("Milch, 0,5 l", "H-Milch 1,5 %", 0.73, 0.5, "l", base=1.46)
    milk_large = offer("Milch, 1 l", "H-Milch 1,5 %", 1.11, 1, "l", base=1.11)
    hummus_small = offer("Hummus, 200 g", "Hummus", 1.85, 200, "g", base=9.25)
    hummus_large = offer("Hummus, 400 g", "Hummus", 2.59, 400, "g", base=6.475)

    basket = PriceOptimizer.optimize_prices([milk_small, milk_large, hummus_small, hummus_large])

    assert [row["product_name"] for row in basket.products] == ["Milch, 1 l", "Hummus, 400 g"]
    assert basket.products[0]["line_savings"] == Decimal("0.35")
    assert basket.products[1]["line_savings"] == Decimal("1.11")
    assert basket.total == Decimal("3.70")
    assert basket.expensive_total == Decimal("5.16")
    assert basket.savings == Decimal("1.46")
    assert basket.savings_percent == 28


def test_offers_without_a_kind_stay_separate() -> None:
    first = offer("Lose", "", 1.00, 1, "Stück", base=1)
    second = offer("Noch lose", "", 0.50, 1, "Stück", base=0.5)

    basket = PriceOptimizer.optimize_prices([first, second])

    assert [row["product_name"] for row in basket.products] == ["Lose", "Noch lose"]
    assert basket.total == Decimal("1.50")
    assert basket.savings == Decimal("0.00")
    assert basket.savings_percent == 0


def test_each_kind_has_a_sensible_amount() -> None:
    for kind in PRODUCT_KINDS:
        demand = ShoppingDemand.demand_for(kind)
        assert demand.unit
        assert demand.step > 0
        assert demand.minimum > 0
        assert demand.default >= demand.minimum


def test_amounts_follow_how_the_food_is_bought() -> None:
    milk = ShoppingDemand.demand_for("H-Milch 1,5 %")
    rolls = ShoppingDemand.demand_for("Brötchen")
    donut = ShoppingDemand.demand_for("Donut")
    eggs = ShoppingDemand.demand_for("Eier Größe M")
    spice = ShoppingDemand.demand_for("Paprikapulver edelsüß")
    oil = ShoppingDemand.demand_for("Olivenöl")
    tea = ShoppingDemand.demand_for("Schwarztee")

    assert (milk.unit, milk.default, milk.step) == ("l", 1, 0.5)
    assert (rolls.unit, rolls.default) == ("Stück", 6)
    assert donut.unit == "Stück"
    assert (eggs.unit, eggs.default) == ("Stück", 10)
    assert spice.unit == "g" and spice.default <= 50
    assert oil.unit == "ml"
    assert tea.unit == "Beutel"
    assert ShoppingDemand.parse_amount("1,5") == 1.5
    assert ShoppingDemand.parse_amount("") is None
    assert ShoppingDemand.compare_amount(rolls, 6)["measure"] == "mass"
    assert ShoppingDemand.compare_amount(milk, 1) == {"measure": "volume", "amount": 1}


def test_entered_amount_scales_the_basket() -> None:
    hummus_small = offer("Hummus, 200 g", "Hummus", 1.85, 200, "g", base=9.25)
    hummus_large = offer("Hummus, 400 g", "Hummus", 2.59, 400, "g", base=6.475)

    one_pack = PriceOptimizer.optimize_prices([hummus_small, hummus_large])
    requested = PriceOptimizer.optimize_prices([hummus_small, hummus_large], {"Hummus": {"measure": "mass", "amount": 0.2}})

    assert one_pack.total == Decimal("2.59")
    assert requested.total == Decimal("1.30")
    assert requested.savings < one_pack.savings


def test_zero_quantity_falls_back_to_the_pack_price() -> None:
    unknown = offer("Unbekannt", "Brot", 1.20, 0, "g")

    assert PriceOptimizer.offer_base_price(unknown) == 1.20


def test_price_goal_shows_one_offer_per_kind_and_the_basket_sum() -> None:
    kinds = ["H-Milch 1,5 %", "Hummus"]
    hits = []
    for kind in kinds:
        hits.extend(ProductSearch.search_products("Augsburg", markets=["lidl"], radius_km="10", kind=kind))
    amounts = {kind: ShoppingDemand.compare_amount(ShoppingDemand.demand_for(kind), ShoppingDemand.demand_for(kind).default) for kind in kinds}
    basket = PriceOptimizer.optimize_prices(hits, amounts)
    response = Client(HTTP_HOST="localhost").get(
        "/",
        {
            "wo": "Augsburg",
            "umkreis": "10",
            "maerkte": "lidl",
            "produkte": kinds,
            "mengen": ["1", "200"],
            "ziel": "preis",
        },
    )
    content = response.content.decode()
    chosen = {row["product_name"] for row in basket.products}

    assert response.status_code == 200
    assert len(chosen) == 2
    assert content.index('class="city-map"') < content.index("Gesamtersparnis")
    assert content.index("Gesamtersparnis") < content.index('class="pdf-download"')
    assert content.index('class="pdf-download"') < content.index('class="product-results"')
    assert 'title="Je Produktart ist das Angebot mit dem niedrigsten Preis je Kilogramm, Liter oder Stück gewählt."' in content
    assert "<p>Je Produktart" not in content
    assert "Summe der gewählten Packungen" in content
    assert "Gesamtersparnis gegenüber den teuersten Angeboten" in content
    assert ProductLabels.euro(basket.total) in content
    assert f"{ProductLabels.euro(basket.savings)} ({basket.savings_percent} %)" in content
    assert 'class="quantity-select"' not in content
    assert content.count('class="amount-stepper"') == 2
    assert 'title="reg. Preis"' in content
    assert 'class="offer-kind"' not in content
    assert 'class="savings-badge"' in content
    assert 'title="Sie haben 0,35 € gespart"' in content
    assert 'title="Sie haben 0,55 € gespart"' in content
    assert ">-0,35 €<" in content
    assert ">-0,55 €<" in content
    assert 'class="amount-unit">l<' in content
    assert 'class="amount-unit">g<' in content
    assert 'name="mengen" value="1"' in content
    assert 'name="mengen" value="200"' in content
    for row in hits:
        marker = f'data-name="{row["product_name"]}"'
        assert (marker in content) is (row["product_name"] in chosen)
    assert "Milbona H-Milch 1,5 %, 1 l" in chosen
    assert "Kania Hummus, 400 g" in chosen


def test_health_goal_keeps_every_pack() -> None:
    query = {"wo": "Augsburg", "umkreis": "10", "maerkte": "lidl", "produkte": ["H-Milch 1,5 %", "Hummus"]}
    price = Client(HTTP_HOST="localhost").get("/", {**query, "ziel": "preis"})
    health = Client(HTTP_HOST="localhost").get("/", {**query, "ziel": "gesundheit"})

    assert price.content.decode().count("<li data-name=") == 2
    assert health.content.decode().count("<li data-name=") > 2
    assert "Summe der gewählten Packungen" not in health.content.decode()
    assert "Gesamtersparnis" not in health.content.decode()
    assert 'class="quantity-select"' not in health.content.decode()
    assert 'class="amount-stepper"' in health.content.decode()
