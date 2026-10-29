"""Datenbankmodelle der App.

Summary:
    Django lädt dieses Modul. Die Klassen liegen in den Dateien ihres Namens.
"""

from models.product_kind import ProductKind
from models.product_kind_nutrient import ProductKindNutrient

__all__ = ["ProductKind", "ProductKindNutrient"]
