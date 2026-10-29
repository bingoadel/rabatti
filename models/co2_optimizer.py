"""CO2-Optimierung eines Einkaufszettels.

Summary:
    Für jede Produktart bleibt die Packung mit dem niedrigsten Agribalyse-Wert.
    Die Packungsmenge und das Bio-Kennzeichen der Markenartikel gehen in die Rechnung ein.
    Markenname, Beschreibung und Zusatzstoffe ändern die Zahl nicht.
    Bei gleichem Wert bleibt die günstigere Packung.
"""

from decimal import Decimal, ROUND_HALF_UP

from models.co2_factors import Co2Factors
from models.co2_basket import Co2Basket
from models.price_optimizer import PriceOptimizer

# Stück ohne Stückgewicht in der Mengenvorgabe. Die Gramm sind nur die Umrechnung
# in Kilogramm, keine eigenen Klimazahlen. Tee zählt als Aufguss, weil die
# Agribalyse-Zeile das fertige Getränk ist.
_PIECE_KG = {
    "Eier Größe M": 0.058,
    "Eier Größe L": 0.068,
    "Fischstäbchen": 0.030,
    "Hefe": 0.042,
    "Backpulver": 0.015,
    "Vanillinzucker": 0.008,
    "Schwarztee": 0.2,
    "Grüntee": 0.2,
    "Pfefferminztee": 0.2,
    "Früchtetee": 0.2,
    "Kamillentee": 0.2,
}


class Co2Optimizer:
    """Wählt je Produktart die Packung mit dem niedrigsten CO2-Abdruck.

    Summary:
        Die Rechnung nutzt die Agribalyse-Zahl und die gewünschte Menge.
        Co2Basket trägt die gewählte Liste und die Ersparnis.
    """

    @staticmethod
    def format_co2(kilograms):
        """Deutsche Anzeige eines CO2-Äquivalents.

        Summary:
            Werte unter 0,1 kg behalten drei Nachkommastellen, größere zwei.
            Die Einheit ist Kilogramm CO2-Äquivalent.
        """
        value = float(kilograms)
        if abs(value) < 0.0005:
            value = 0.0
        digits = 2 if value == 0 else 3 if abs(value) < 0.1 else 2
        text = f"{value:.{digits}f}".replace(".", ",")
        return f"{text} kg CO2e"

    @staticmethod
    def piece_kg(kind):
        """Kilogramm je Stück, Beutel oder Würfel, wenn die Menge nicht schon Masse ist.

        Summary:
            Eier, Fischstäbchen, Backzutaten und Teebeutel haben eine feste Umrechnung.
            Andere Produktarten kommen hier nicht an, weil ihre Menge schon Kilogramm oder Liter ist.
        """
        try:
            return _PIECE_KG[kind]
        except KeyError as exc:
            raise KeyError(f"keine Stückmasse für {kind}") from exc

    @staticmethod
    def optimize_co2(products, amounts=None):
        """Wählt je Produktart die Packung mit dem niedrigsten CO2-Abdruck.

        Summary:
            Verglichen wird das Kilogramm CO2-Äquivalent je Kilogramm Lebensmittel.
            Die Ersparnis gilt für die gewünschte Menge, nicht für die größere Packung.
            Eine Produktart ohne Zuordnung bleibt als eigener Posten mit 0 kg stehen.
        """
        amounts = amounts or {}
        groups = {}
        order = []
        for index, product in enumerate(products or []):
            key = Co2Optimizer._kind_key(product, index)
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(product)
        chosen = []
        for key in order:
            offers = groups[key]
            pool, spec = Co2Optimizer._offers_for_amount(offers, amounts.get(key))
            best = min(pool, key=Co2Optimizer._sort_key)
            worst = max(pool, key=Co2Optimizer._sort_key)
            kilograms = Co2Optimizer._line_kilograms(best, spec)
            best_factor = Co2Optimizer._factor(best)
            worst_factor = Co2Optimizer._factor(worst)
            line = Co2Optimizer._round_kg(best_factor * kilograms)
            high = Co2Optimizer._round_kg(worst_factor * kilograms)
            saved = high - line
            if saved < 0:
                saved = Decimal("0.000")
            best["co2_kg"] = line
            best["co2_label"] = Co2Optimizer.format_co2(line)
            best["co2_basis"] = Co2Optimizer._basis(best)
            best["line_savings"] = saved
            chosen.append(best)
        total, expensive_total, savings, percent = Co2Optimizer._basket_figures(chosen)
        return Co2Basket(chosen, total, expensive_total, savings, percent)

    @staticmethod
    def _sort_key(product):
        """Sortierschlüssel, niedrigster CO2-Wert zuerst.

        Summary:
            Bei gleichem Wert entscheidet der günstigere Grundpreis, danach der Name.
        """
        return (Co2Optimizer._factor(product), PriceOptimizer.offer_base_price(product), Co2Optimizer._name(product))

    @staticmethod
    def _factor(product):
        """Kilogramm CO2-Äquivalent je Kilogramm dieser Packung.

        Summary:
            Bio wird nur weitergegeben, wenn die Produktart ein Agribalyse-Hofpaar hat.
            Ohne Produktart ist der Wert 0, der Posten bleibt aber in der Liste.
        """
        kind = str(product.get("product_kind") or "").strip()
        if not kind:
            return 0.0
        return Co2Factors.co2_kg_per_kg(kind, bool(product.get("is_organic")))

    @staticmethod
    def _basis(product):
        """Herkunftssatz der Packung.

        Summary:
            Der Satz sagt, ob die Bio-Zeile oder der gemeinsame Fertigproduktwert gilt.
        """
        kind = str(product.get("product_kind") or "").strip()
        if not kind:
            return "keine Zuordnung"
        return Co2Factors.co2_basis(kind, bool(product.get("is_organic")))

    @staticmethod
    def _line_kilograms(product, spec):
        """Kilogramm Lebensmittel, für die der CO2-Wert gilt.

        Summary:
            Masse bleibt Masse. Ein Liter zählt als ein Kilogramm, weil die Packung keine Dichte trägt.
            Stück und Beutel nutzen die feste Umrechnung der Produktart.
        """
        if spec:
            amount = float(spec["amount"])
            measure = spec.get("measure")
            if measure == "mass":
                return amount
            if measure == "volume":
                return amount
            if measure == "count":
                return amount * Co2Optimizer.piece_kg(str(product.get("product_kind") or ""))
        return Co2Optimizer._pack_kilograms(product)

    @staticmethod
    def _pack_kilograms(product):
        """Kilogramm einer Packung, wenn keine Wunschmenge vorliegt.

        Summary:
            Gramm und Milliliter werden zu Kilogramm und Liter.
            Stück wird mit der festen Umrechnung malgenommen.
        """
        quantity = float(product.get("net_quantity") or 0)
        unit = product.get("unit") or ""
        if unit in {"g", "ml"}:
            return quantity / 1000
        if unit in {"kg", "l"}:
            return quantity
        return quantity * Co2Optimizer.piece_kg(str(product.get("product_kind") or ""))

    @staticmethod
    def _offers_for_amount(offers, spec):
        """Angebote, deren Einheit zur Wunschmenge passt.

        Summary:
            Passt keines, bleibt die ganze Produktart im Vergleich und die Menge fällt auf die Packung zurück.
        """
        if not spec:
            return offers, None
        matched = [offer for offer in offers if PriceOptimizer.measure_of(offer.get("unit") or "") == spec.get("measure")]
        if not matched:
            return offers, None
        return matched, spec

    @staticmethod
    def _kind_key(product, index):
        """Gruppenschlüssel der Produktart.

        Summary:
            Dieselbe Produktart landet in einer Gruppe.
            Ohne Art bleibt jedes Angebot für sich.
        """
        kind = str(product.get("product_kind") or "").strip()
        if kind:
            return kind
        return f"#{index}"

    @staticmethod
    def _name(product):
        """Produktname für die Sortierung.

        Summary:
            Ein fehlender Name sortiert als leerer Text.
        """
        return str(product.get("product_name") or "")

    @staticmethod
    def _round_kg(value):
        """CO2-Menge auf drei Nachkommastellen.

        Summary:
            Die Summe und die Ersparnis rechnen mit derselben Rundung.
        """
        return Decimal(str(value)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _basket_figures(products):
        """Summe, Vergleichswert und Prozent der Ersparnis.

        Summary:
            Jede Zeile bringt ihren eigenen CO2-Wert und ihre Ersparnis mit.
            Bei einer Summe von 0 ist der Prozentwert 0.
        """
        total = Decimal("0.000")
        expensive_total = Decimal("0.000")
        for product in products:
            line = product.get("co2_kg") or Decimal("0.000")
            saved = product.get("line_savings") or Decimal("0.000")
            total += line
            expensive_total += line + saved
        savings = expensive_total - total
        if savings < 0:
            savings = Decimal("0.000")
        if expensive_total == 0:
            percent = 0
        else:
            percent = int((savings / expensive_total * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        return total, expensive_total, savings, percent


