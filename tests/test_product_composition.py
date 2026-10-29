from decimal import Decimal

from models.product_composition import COMPOSITION, NUTRIENT_CODES, NUTRIENTS, ProductComposition
from models.product_kinds import PRODUCT_KINDS


def test_every_kind_has_fat_sugar_protein_vitamins_and_minerals() -> None:
    rows = list(ProductComposition.composition_rows())
    assert [name for name, _row in rows] == list(PRODUCT_KINDS)
    assert len(COMPOSITION) == len(PRODUCT_KINDS)
    vitamin_codes = {code for group, code, _label, _unit in NUTRIENTS if group == "vitamin"}
    mineral_codes = {code for group, code, _label, _unit in NUTRIENTS if group == "mineral"}
    assert vitamin_codes
    assert mineral_codes
    assert set(NUTRIENT_CODES) == vitamin_codes | mineral_codes

    for name, row in rows:
        assert row["fat_g"] >= 0
        assert row["sugar_g"] >= 0
        assert row["protein_g"] >= 0
        assert set(row["nutrients"]) == set(NUTRIENT_CODES)
        assert any(row["nutrients"][code] >= 0 for code in vitamin_codes)
        assert any(row["nutrients"][code] >= 0 for code in mineral_codes)

    milk = COMPOSITION["H-Milch 1,5 %"]
    assert milk["basis"] == "100 ml"
    assert milk["fat_g"] == Decimal("1.5")
    assert milk["protein_g"] > 3
    assert COMPOSITION["Zucker"]["sugar_g"] == Decimal("100")
    assert COMPOSITION["Speisesalz"]["nutrients"]["natrium_mg"] > 30000
    assert COMPOSITION["Jodsalz"]["nutrients"]["jod_ug"] > 0
    assert COMPOSITION["Olivenöl"]["fat_g"] > 99
    assert COMPOSITION["Cola"]["basis"] == "100 ml"
    assert COMPOSITION["Cola"]["sugar_g"] > 9
    assert COMPOSITION["Kiwi grün"]["nutrients"]["vitamin_c_mg"] > 50
    assert "keine Markenanalyse" in COMPOSITION["Magerquark"]["note"]
    assert "Milbona" not in COMPOSITION
    assert "Quark (20 %)" in COMPOSITION
    assert "Fett in der Trockenmasse" in COMPOSITION["Quark (20 %)"]["remark"]
