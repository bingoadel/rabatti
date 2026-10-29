"""Vitamin- oder Mineralstoffzeile einer Produktart.

Summary:
    Jede Zeile gehört zu genau einer Produktart.
"""

from django.db import models

from models.product_kind import ProductKind


class ProductKindNutrient(models.Model):
    """Ein Vitamin oder Mineralstoff einer Produktart."""

    kind = models.ForeignKey(
        ProductKind,
        verbose_name="Produktart",
        related_name="nutrients",
        on_delete=models.CASCADE,
    )
    group = models.CharField("Gruppe", max_length=16)
    code = models.CharField("Kürzel", max_length=32)
    label = models.CharField("Bezeichnung", max_length=40)
    amount = models.DecimalField("Menge", max_digits=9, decimal_places=3)
    unit = models.CharField("Einheit", max_length=8)

    class Meta:
        verbose_name = "Nährstoff"
        verbose_name_plural = "Nährstoffe"
        constraints = [
            models.UniqueConstraint(fields=["kind", "code"], name="unique_kind_nutrient"),
        ]
        ordering = ["kind", "group", "code"]

    def __str__(self) -> str:
        return f"{self.kind.name}: {self.label}"
