"""Ergebnis der Preisoptimierung.

Summary:
    Je Produktart bleibt ein Angebot, dazu Summe und Ersparnis.
"""

class PriceBasket:
    """Gewählter Einkaufszettel nach dem Preisvergleich.

    Summary:
        products enthält je Produktart genau ein Angebot, in der Reihenfolge des Zettels.
        total ist die Summe für je eine Packung der gewählten Angebote.
        expensive_total ist dieselbe Menge zum teuersten Grundpreis.
        savings und savings_percent sind die Differenz daraus, in Euro und Prozent.
    """

    def __init__(self, products, total, expensive_total, savings, savings_percent):
        self.products = products
        self.total = total
        self.expensive_total = expensive_total
        self.savings = savings
        self.savings_percent = savings_percent

