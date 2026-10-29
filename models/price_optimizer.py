"""Preisoptimierung eines Einkaufszettels.

Summary:
    Für jede Produktart bleibt das Angebot mit dem niedrigsten vergleichbaren Preis.
    Verglichen wird je Kilogramm, je Liter oder je Stück, nicht der nackte Packungspreis.
    Die Ersparnis stellt diese Auswahl der teuersten vergleichbaren Alternative gegenüber.
"""

from decimal import Decimal, ROUND_HALF_UP


from models.price_basket import PriceBasket

class PriceOptimizer:
    """Wählt je Produktart die günstigste vergleichbare Packung.

    Summary:
        Verglichen wird der Preis je Kilogramm, je Liter oder je Stück.
        PriceBasket trägt die gewählte Liste und die Ersparnis.
    """

    @staticmethod
    def measure_of(unit):
        """Maß, in dem Packungen derselben Produktart vergleichbar sind.

        Summary:
            Gramm und Kilogramm sind Masse, Milliliter und Liter sind Volumen.
            Andere Einheiten zählen stückweise, zum Beispiel Stück oder Beutel.
        """
        if unit in {"g", "kg"}:
            return "mass"
        if unit in {"ml", "l"}:
            return "volume"
        return "count"

    @staticmethod
    def offer_base_price(product):
        """Preis je Kilogramm, je Liter oder je Stück.

        Summary:
            Liegt calculated_base_price schon auf dem Angebot, wird der verwendet.
            Sonst ergibt er sich aus Packungspreis, Füllmenge und Einheit.
            Eine Menge von 0 lässt sich nicht umlegen, dann bleibt der Packungspreis.
        """
        stored = product.get("calculated_base_price")
        if stored is not None:
            return float(stored)
        price = PriceOptimizer._pack_price(product)
        quantity = float(product.get("net_quantity") or 0)
        if quantity <= 0:
            return price
        if product.get("unit") in {"g", "ml"}:
            return price / quantity * 1000
        return price / quantity

    @staticmethod
    def choose_most_expensive(offers):
        """Das teuerste Angebot einer Produktart.

        Summary:
            Bei gleichem Maß gewinnt der höchste Grundpreis.
            Bei gleichem Grundpreis die teurere Packung, danach der Produktname.
            Gramm und Stück werden nicht ineinander umgerechnet; dann entscheidet der Packungspreis.
        """
        if len(offers) == 1:
            return offers[0]
        measures = {PriceOptimizer.measure_of(offer.get("unit") or "") for offer in offers}
        if len(measures) == 1:
            return max(offers, key=lambda offer: (PriceOptimizer.offer_base_price(offer), PriceOptimizer._pack_price(offer), PriceOptimizer._name(offer)))
        return max(offers, key=lambda offer: (PriceOptimizer._pack_price(offer), PriceOptimizer._name(offer)))

    @staticmethod
    def format_quantity(amount, unit):
        """Lesbare Menge für die Auswahlliste.

        Summary:
            Masse erscheint als Gramm oder Kilogramm, Volumen als Milliliter oder Liter.
            Stückweise Einheiten behalten ihren Namen, zum Beispiel Stück oder Beutel.
        """
        if PriceOptimizer.measure_of(unit) == "mass":
            grams = amount * 1000
            if grams >= 1000:
                return PriceOptimizer._de_number(grams / 1000) + " kg"
            return f"{round(grams)} g"
        if PriceOptimizer.measure_of(unit) == "volume":
            if amount < 1:
                return f"{round(amount * 1000)} ml"
            return PriceOptimizer._de_number(amount) + " l"
        word = unit or "Stück"
        return f"{round(amount)} {word}"

    @staticmethod
    def quantity_options(product):
        """Sinnvolle Mengen für die optionale Auswahl.

        Summary:
            Angeboten werden eine bis sechs Packungen der gewählten Größe.
            Ohne Auswahl zählt die Zusammenfassung eine Packung.
            Unterschiedliche Maße werden als Packungszahl angeboten, nicht umgerechnet.
        """
        if product.get("compare_by_pack"):
            return [
                {"value": str(count), "label": f"{count} {'Packung' if count == 1 else 'Packungen'}"}
                for count in range(1, 7)
            ]
        pack = float(product["compare_pack_amount"])
        unit = product.get("unit") or ""
        return [
            {"value": PriceOptimizer._amount_value(pack * count), "label": PriceOptimizer.format_quantity(pack * count, unit)}
            for count in range(1, 7)
        ]

    @staticmethod
    def choose_cheapest(offers):
        """Das günstigste Angebot einer Produktart.

        Summary:
            Bei gleichem Maß gewinnt der niedrigste Grundpreis.
            Bei gleichem Grundpreis die günstigere Packung, danach der Produktname.
            Gramm und Stück werden nicht ineinander umgerechnet; dann entscheidet der Packungspreis.
        """
        if len(offers) == 1:
            return offers[0]
        measures = {PriceOptimizer.measure_of(offer.get("unit") or "") for offer in offers}
        if len(measures) == 1:
            return min(offers, key=lambda offer: (PriceOptimizer.offer_base_price(offer), PriceOptimizer._pack_price(offer), PriceOptimizer._name(offer)))
        return min(offers, key=lambda offer: (PriceOptimizer._pack_price(offer), PriceOptimizer._name(offer)))

    @staticmethod
    def optimize_prices(products, amounts=None):
        """Wählt je Produktart das günstigste Angebot und rechnet die Ersparnis.

        Summary:
            Die Reihenfolge folgt dem ersten Auftreten jeder Produktart auf dem Einkaufszettel.
            Ein Angebot ohne Produktart bleibt für sich und wird nicht mit anderen zusammengelegt.
            amounts nennt je Produktart Maß und Menge. Ohne Angabe zählt eine Packung der günstigsten Wahl.
            Die Ersparnis vergleicht diese Menge mit dem teuersten Grundpreis derselben Maßeinheit.
        """
        amounts = amounts or {}
        groups = {}
        order = []
        for index, product in enumerate(products or []):
            key = PriceOptimizer._kind_key(product, index)
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(product)
        chosen = []
        applied = {}
        for key in order:
            offers = groups[key]
            pool, amount = PriceOptimizer._offers_for_amount(offers, amounts.get(key))
            cheap = PriceOptimizer.choose_cheapest(pool)
            PriceOptimizer._attach_comparison(cheap, PriceOptimizer.choose_most_expensive(pool))
            cheap_cost, expensive_cost = PriceOptimizer._line_costs(cheap, amount)
            saved = expensive_cost - cheap_cost
            cheap["line_savings"] = saved if saved > 0 else Decimal("0.00")
            chosen.append(cheap)
            if amount is not None:
                applied[key] = amount
        total, expensive_total, savings, percent = PriceOptimizer._basket_figures(chosen, applied)
        return PriceBasket(chosen, total, expensive_total, savings, percent)

    @staticmethod
    def _offers_for_amount(offers, spec):
        if not spec:
            return offers, None
        matched = [offer for offer in offers if PriceOptimizer.measure_of(offer.get("unit") or "") == spec.get("measure")]
        if not matched:
            return offers, None
        return matched, spec.get("amount")

    @staticmethod
    def _kind_key(product, index):
        kind = str(product.get("product_kind") or "").strip()
        if kind:
            return kind
        return f"#{index}"

    @staticmethod
    def _pack_price(product):
        if product.get("current_price") is not None:
            return float(product["current_price"])
        return float(product.get("regular_price") or 0)

    @staticmethod
    def _money(amount):
        return Decimal(f"{amount:.2f}")

    @staticmethod
    def _name(product):
        return str(product.get("product_name") or "")

    @staticmethod
    def _base_amount(product):
        quantity = float(product.get("net_quantity") or 0)
        unit = product.get("unit") or ""
        if quantity <= 0:
            return 0.0
        if unit in {"g", "ml"}:
            return quantity / 1000
        return quantity

    @staticmethod
    def _attach_comparison(cheap, expensive):
        amount = PriceOptimizer._base_amount(cheap)
        same_measure = PriceOptimizer.measure_of(cheap.get("unit") or "") == PriceOptimizer.measure_of(expensive.get("unit") or "")
        cheap["compare_by_pack"] = (not same_measure) or amount <= 0
        cheap["compare_pack_amount"] = 1.0 if cheap["compare_by_pack"] else amount
        cheap["compare_pack_price"] = PriceOptimizer._pack_price(cheap)
        cheap["compare_expensive_pack_price"] = PriceOptimizer._pack_price(expensive)
        cheap["compare_base_price"] = PriceOptimizer.offer_base_price(cheap)
        cheap["compare_expensive_base_price"] = PriceOptimizer.offer_base_price(expensive)
        cheap["quantity_options"] = PriceOptimizer.quantity_options(cheap)

    @staticmethod
    def _line_costs(product, amount=None):
        if product.get("compare_by_pack"):
            count = Decimal("1") if amount in (None, "") else Decimal(str(amount))
            cheap = PriceOptimizer._money(float(product["compare_pack_price"]) * float(count))
            expensive = PriceOptimizer._money(float(product["compare_expensive_pack_price"]) * float(count))
            return cheap, expensive
        chosen = product["compare_pack_amount"] if amount in (None, "") else amount
        cheap = PriceOptimizer._cost(product["compare_base_price"], chosen)
        expensive = PriceOptimizer._cost(product["compare_expensive_base_price"], chosen)
        return cheap, expensive

    @staticmethod
    def _basket_figures(products, amounts=None):
        amounts = amounts or {}
        total = Decimal("0.00")
        expensive_total = Decimal("0.00")
        for product in products:
            kind = str(product.get("product_kind") or "")
            cheap, expensive = PriceOptimizer._line_costs(product, amounts.get(kind))
            total += cheap
            expensive_total += expensive
        savings = expensive_total - total
        if savings < 0:
            savings = Decimal("0.00")
        if expensive_total == 0:
            percent = 0
        else:
            percent = int((savings / expensive_total * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        return total, expensive_total, savings, percent

    @staticmethod
    def _cost(price, amount):
        return (Decimal(str(price)) * Decimal(str(amount))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _de_number(value):
        return f"{value:.2f}".rstrip("0").rstrip(".").replace(".", ",")

    @staticmethod
    def _amount_value(amount):
        return f"{amount:.4f}".rstrip("0").rstrip(".") or "0"


