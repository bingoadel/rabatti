"""Ergebnis der CO2-Optimierung.

Summary:
    Je Produktart bleibt eine Packung, dazu Summe und Ersparnis.
"""

class Co2Basket:
    """Gewählter Einkaufszettel nach dem CO2-Abdruck.

    Summary:
        products enthält je Produktart genau ein Angebot, in der Reihenfolge des Zettels.
        total ist die Summe der CO2-Äquivalente für die gewünschte Menge.
        expensive_total ist dieselbe Menge mit dem höchsten Wert der Produktart.
        savings und savings_percent sind die Differenz daraus.
    """

    def __init__(self, products, total, expensive_total, savings, savings_percent):
        self.products = products
        self.total = total
        self.expensive_total = expensive_total
        self.savings = savings
        self.savings_percent = savings_percent

