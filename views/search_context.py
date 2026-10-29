"""Daten der Produktseite für HTML und PDF."""

from models.co2_factors import SOURCE as CO2_SOURCE
from models.co2_optimizer import Co2Optimizer
from models.price_optimizer import PriceOptimizer
from models.product_labels import ProductLabels
from models.product_search import CHAIN_NAMES, ProductSearch
from models.results_pdf import ResultsPdf
from models.shopping_demand import ShoppingDemand
from models.store_locations import StoreLocations

MAP_ZOOM = {"5": 13, "10": 12, "15": 12, "20": 11, "30": 11, "40": 10, "50": 10}
OPTIMIZATION_GOALS = ("preis", "gesundheit", "co2")

class SearchContext:
    """Daten der Produktseite für HTML und PDF.

    Summary:
        Dieselbe Suche, dieselbe Optimierung und dieselbe Trefferliste
        gelten für die Seite und den PDF-Download.
    """

    @staticmethod
    def from_request(request):
        """Baut den Kontext aus den Query-Parametern der Suche."""
        searched = bool(request.GET)
        radius = request.GET.get("umkreis", "10") or "10"
        selected_markets = [name for name in request.GET.getlist("maerkte") if name]
        requested_products = [name.strip() for name in request.GET.getlist("produkte") if name.strip()]
        shopping_items, shopping_amounts = ShoppingDemand.shopping_rows(requested_products, request.GET.getlist("mengen"))
        optimization = request.GET.get("ziel", "preis")
        if optimization not in OPTIMIZATION_GOALS:
            optimization = "preis"
        criteria = request.GET.get("kriterien", "").strip()
        catalog = ProductSearch.search_catalog()
        if searched and "produkte" in request.GET:
            outcome = ProductSearch.prepare_shopping_list(
                request.GET.get("wo", ""),
                requested_products,
                selected_markets,
                radius,
            )
        elif searched:
            outcome = ProductSearch.prepare_search(
                request.GET.get("wo", ""),
                request.GET.get("kategorie", ""),
                request.GET.get("unterkategorie", ""),
                request.GET.get("produkt", ""),
                selected_markets,
                request.GET.get("preisart", "regulärer Preis"),
                radius,
            )
        else:
            outcome = {
                "error": "",
                "place": "",
                "category": "",
                "subcategory": "",
                "product": "",
                "offer_type": "regulärer Preis",
                "products": ProductSearch.sample_products(10),
                "notice": "",
                "result_place": "",
                "keep_radius": False,
            }
        products = StoreLocations.annotate_distance(outcome["products"], outcome.get("place", ""))
        price_optimized = False
        co2_optimized = False
        basket_total_label = ""
        savings_label = ""
        savings_percent = 0
        co2_source = ""
        shopping_ready = searched and not outcome["error"] and "produkte" in request.GET and products
        if optimization == "preis" and shopping_ready:
            basket = PriceOptimizer.optimize_prices(products, shopping_amounts)
            products = basket.products
            for product in products:
                product["savings_label"] = ProductLabels.euro(product.get("line_savings") or 0)
            basket_total_label = ProductLabels.euro(basket.total)
            savings_label = ProductLabels.euro(basket.savings)
            savings_percent = basket.savings_percent
            price_optimized = True
        elif optimization == "co2" and shopping_ready:
            basket = Co2Optimizer.optimize_co2(products, shopping_amounts)
            products = basket.products
            for product in products:
                product["savings_label"] = Co2Optimizer.format_co2(product.get("line_savings") or 0)
            basket_total_label = Co2Optimizer.format_co2(basket.total)
            savings_label = Co2Optimizer.format_co2(basket.savings)
            savings_percent = basket.savings_percent
            co2_source = CO2_SOURCE
            co2_optimized = True
        show_results = not outcome["error"] and (searched or bool(products))
        stores = StoreLocations.stores_for_map(products) if outcome["result_place"] and not outcome["error"] else []
        focus = StoreLocations.map_focus(stores, outcome.get("place") or outcome.get("result_place") or "")
        visible_search = searched and not outcome["error"]
        return {
            "searched": visible_search,
            "show_results": show_results,
            "form_error": outcome["error"],
            "products": products,
            "can_sort_distance": any(product["distance_km"] is not None for product in products),
            "stores": stores,
            "map_lat": focus[0] if focus else None,
            "map_lng": focus[1] if focus else None,
            "place": outcome["place"],
            "result_place": outcome["result_place"],
            "keep_radius": outcome["keep_radius"],
            "notice": outcome["notice"],
            "results_heading": ResultsPdf.results_heading(
                visible_search,
                outcome["result_place"],
                outcome["keep_radius"],
                radius,
                outcome["notice"],
            ),
            "category": outcome["category"],
            "subcategory": outcome["subcategory"],
            "product_query": outcome["product"],
            "product_list": shopping_items if searched else [],
            "supermarkets": list(CHAIN_NAMES.items()),
            "preisart": outcome["offer_type"],
            "preisarten": catalog["preisarten"],
            "radius": radius,
            "map_zoom": MAP_ZOOM.get(radius, 12),
            "selected_markets": selected_markets,
            "optimization": optimization,
            "price_optimized": price_optimized,
            "co2_optimized": co2_optimized,
            "co2_source": co2_source,
            "basket_total_label": basket_total_label,
            "savings_label": savings_label,
            "savings_percent": savings_percent,
            "criteria": criteria,
        }

