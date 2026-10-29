"""Sinnvolle Menge je Produktart für den Einkaufszettel.

Summary:
    Jede Produktart bekommt eine Einheit, einen Schritt und einen Startwert.
    Stückware, die im Sortiment nach Gewicht liegt, wird über ein übliches Stückgewicht umgerechnet.
    Die Eingabe selbst bleibt frei, Plus und Minus springen nur in diesem Schritt.
"""

class ShoppingAmount:
    """Mengenvorgabe einer Produktart.

    Summary:
        unit steht neben dem Eingabefeld.
        step ist der Sprung von Plus und Minus.
        minimum ist die kleinste sinnvolle Menge.
        default ist der vorbelegte Wert.
        grams_each rechnet Stück in Gramm um, wenn das Regal nach Gewicht ausgezeichnet ist.
    """

    def __init__(self, unit, step, minimum, default, grams_each=None):
        self.unit = unit
        self.step = step
        self.minimum = minimum
        self.default = default
        self.grams_each = grams_each

