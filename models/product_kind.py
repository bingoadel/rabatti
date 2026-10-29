"""Lebensmittelart in PostgreSQL.

Summary:
    Fett, Zucker, Eiweiß und der CO2-Richtwert hängen an der Art, nicht an der Marke.
"""

from django.db import models

class ProductKind(models.Model):
    """Lebensmittelart mit Energie, Fett, Zucker, Eiweiß und CO2-Richtwert."""

    name = models.CharField("Name", max_length=80, unique=True)
    basis = models.CharField("Bezugsgröße", max_length=40)
    energy_kcal = models.DecimalField("Energie kcal", max_digits=6, decimal_places=1)
    fat_g = models.DecimalField("Fett g", max_digits=5, decimal_places=1)
    sugar_g = models.DecimalField("Zucker g", max_digits=5, decimal_places=1)
    protein_g = models.DecimalField("Eiweiß g", max_digits=5, decimal_places=1)
    note = models.CharField("Hinweis", max_length=200)
    remark = models.CharField("Anmerkung", max_length=200, blank=True)
    co2_kg_per_kg = models.DecimalField(
        "CO2 kg je kg",
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
    )
    co2_organic_kg_per_kg = models.DecimalField(
        "CO2 Bio kg je kg",
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
    )
    agribalyse_code = models.CharField("CIQUAL", max_length=16, blank=True)
    co2_reference = models.CharField("Agribalyse-Referenz", max_length=160, blank=True)

    class Meta:
        verbose_name = "Produktart"
        verbose_name_plural = "Produktarten"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

