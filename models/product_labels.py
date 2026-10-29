"""Beschriftung von Preis, Menge und Kennzeichnungen.

Summary:
    Dieselbe Schreibweise gilt für die Ergebnisliste, die Karte und den PDF-Download.
"""

import json

class ProductLabels:
    """Beschriftung von Preis, Menge und Kennzeichnungen eines Produkts.

    Summary:
        Dieselbe Schreibweise gilt für die Ergebnisliste, die Karte und den PDF-Download.
    """

    BOOLEAN_FLAGS = (
        ("is_organic", "Bio"),
        ("is_gluten_free", "Glutenfrei"),
        ("is_lactose_free", "Laktosefrei"),
        ("is_deposit_required", "Pfand"),
    )

    @staticmethod
    def fold(value):
        """Vergleichstext ohne Großschreibung und mit aufgelösten Umlauten."""
        return (
            str(value)
            .casefold()
            .replace("ä", "ae")
            .replace("ö", "oe")
            .replace("ü", "ue")
            .replace("ß", "ss")
        )

    @staticmethod
    def euro(amount):
        """Preis mit deutschem Komma und Euro-Zeichen."""
        return f"{amount:.2f}".replace(".", ",") + " €"

    @staticmethod
    def quantity_label(quantity, unit):
        """Füllmenge mit deutschem Komma und Einheit."""
        number = f"{quantity:g}".replace(".", ",")
        return f"{number} {unit}"

    @staticmethod
    def per_unit(unit):
        """Einheit des Grundpreises, zum Beispiel Kilogramm oder Stück."""
        return {"g": "kg", "kg": "kg", "ml": "l", "l": "l"}.get(unit, "Stück")

    @classmethod
    def present(cls, row):
        """Anzeigefelder für Preis, Menge, Kennzeichnungen und Zusatzstoffe."""
        shown = dict(row)
        shown["price_label"] = cls.euro(row["current_price"])
        shown["regular_label"] = cls.euro(row["regular_price"])
        shown["show_regular"] = row["regular_price"] != row["current_price"]
        shown["quantity_label"] = cls.quantity_label(row["net_quantity"], row["unit"])
        shown["base_price_label"] = cls.euro(row["calculated_base_price"]) + "/" + cls.per_unit(row["unit"])
        shown["price_kind"] = row["special_pricing"] or "reg. Preis"
        shown["flags"] = [label for key, label in cls.BOOLEAN_FLAGS if row.get(key)]
        shown["additives"] = json.loads(row["additives"]) if row.get("additives") else []
        return shown


