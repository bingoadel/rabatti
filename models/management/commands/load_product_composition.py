"""Lädt die Produktarten mit ihrer Zusammensetzung nach PostgreSQL."""

from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from models.co2_factors import Co2Factors
from models.composition_router import COMPOSITION_DB
from models.models import ProductKind, ProductKindNutrient
from models.product_composition import NUTRIENTS, ProductComposition


class Command(BaseCommand):
    help = "Legt alle Produktarten mit Nährwerten und CO2-Richtwerten in PostgreSQL ab."

    def handle(self, *args, **options):
        if COMPOSITION_DB not in settings.DATABASES:
            raise CommandError(
                "PostgreSQL ist nicht konfiguriert. Setze POSTGRES_HOST, zum Beispiel 127.0.0.1, "
                "und starte die Datenbank mit docker compose up -d."
            )
        labels = {code: (group, label, unit) for group, code, label, unit in NUTRIENTS}
        names = []
        with transaction.atomic(using=COMPOSITION_DB):
            for name, row in ProductComposition.composition_rows():
                names.append(name)
                kind, _created = ProductKind.objects.using(COMPOSITION_DB).update_or_create(
                    name=name,
                    defaults={
                        "basis": row["basis"],
                        "energy_kcal": row["energy_kcal"],
                        "fat_g": row["fat_g"],
                        "sugar_g": row["sugar_g"],
                        "protein_g": row["protein_g"],
                        "note": row["note"],
                        "remark": row["remark"],
                        "co2_kg_per_kg": self._co2_decimal(name, organic=False),
                        "co2_organic_kg_per_kg": self._co2_decimal(name, organic=True),
                        "agribalyse_code": Co2Factors.reference_code(name),
                        "co2_reference": Co2Factors.reference_name(name),
                    },
                )
                for code, amount in row["nutrients"].items():
                    group, label, unit = labels[code]
                    ProductKindNutrient.objects.using(COMPOSITION_DB).update_or_create(
                        kind=kind,
                        code=code,
                        defaults={"group": group, "label": label, "amount": amount, "unit": unit},
                    )
            ProductKind.objects.using(COMPOSITION_DB).exclude(name__in=names).delete()
        count = ProductKind.objects.using(COMPOSITION_DB).count()
        nutrients = ProductKindNutrient.objects.using(COMPOSITION_DB).count()
        self.stdout.write(self.style.SUCCESS(f"{count} Produktarten, {nutrients} Nährstoffzeilen."))

    @staticmethod
    def _co2_decimal(name, organic):
        """CO2-Richtwert als Dezimalzahl für die Produktart.

        Summary:
            Bio und konventionell können sich unterscheiden, wenn ein Hofpaar vorliegt.
            Die Suche liest dieselben Zahlen aus der lokalen Tabelle, nicht aus dieser Spalte.
        """
        return Decimal(str(Co2Factors.co2_kg_per_kg(name, organic=organic))).quantize(Decimal("0.000001"))
