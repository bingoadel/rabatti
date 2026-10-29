from models.product_kinds import PRODUCT_KINDS
from models.supermarket_catalog import CATALOG_SIZE, CHAINS, ORGANIC_EXAMPLE, SupermarketCatalog


def test_each_supermarket_has_1000_concrete_products() -> None:
    assert list(CHAINS) == ["aldi", "lidl", "rewe", "netto", "penny"]
    seen = set()
    for chain in CHAINS:
        rows = SupermarketCatalog.catalog_for(chain)
        names = [row["product_name"] for row in rows]
        assert len(rows) == 1000
        assert len(set(names)) == 1000
        assert all(row["product_kind"] in PRODUCT_KINDS for row in rows)
        assert all(row["regular_price"] > 0 for row in rows)
        assert all(isinstance(row["additives"], str) for row in rows)
        assert all(isinstance(row["is_gluten_free"], bool) and isinstance(row["is_lactose_free"], bool) for row in rows)
        organic_rows = CATALOG_SIZE - 2 * len(PRODUCT_KINDS) + len(ORGANIC_EXAMPLE)
        assert sum(1 for row in rows if row["is_organic"]) == organic_rows
        for kind in ORGANIC_EXAMPLE:
            of_kind = [row for row in rows if row["product_kind"] == kind]
            assert sum(1 for row in of_kind if row["is_organic"]) == 1
        milk = [row for row in rows if row["product_kind"] == "H-Milch 1,5 %"]
        assert len(milk) == 3
        assert {str(row["net_quantity"]) for row in milk} == {"1", "0.5"}
        seen.update(row["brand"] for row in rows)

    aldi = SupermarketCatalog.catalog_for("aldi")
    lidl = SupermarketCatalog.catalog_for("lidl")
    rewe = SupermarketCatalog.catalog_for("rewe")
    netto = SupermarketCatalog.catalog_for("netto")
    penny = SupermarketCatalog.catalog_for("penny")
    assert any(row["brand"] == "Milsani" and row["product_name"].startswith("Milsani H-Milch") for row in aldi)
    assert any(row["brand"] == "Milbona" and "H-Milch 1,5 %" in row["product_name"] for row in lidl)
    assert all(row["brand"] != "Milbona" for row in aldi)
    assert any(row["brand"] == "ja!" for row in rewe)
    assert any(row["brand"] == "Wilhelm Brandenburg" for row in rewe)
    assert any(row["brand"] == "Mibell" for row in netto)
    assert any(row["brand"] == "Landjunker" for row in netto)
    assert any(row["brand"] == "Grillmeister" for row in penny)
    assert any(row["brand"] == "San Fabio" for row in penny)
    assert "Milbona" not in {row["brand"] for row in aldi + rewe + netto + penny}
    assert seen


def test_additives_and_diet_flags_follow_the_product_kind() -> None:
    milk = SupermarketCatalog.product_traits("H-Milch 1,5 %")
    lactose_free_milk = SupermarketCatalog.product_traits("Laktosefreie Milch")
    cola = SupermarketCatalog.product_traits("Cola")
    roll = SupermarketCatalog.product_traits("Brötchen")
    apple = SupermarketCatalog.product_traits("Äpfel")
    rice = SupermarketCatalog.product_traits("Basmatireis")

    assert milk["additives"] == ""
    assert milk["is_gluten_free"] is True
    assert milk["is_lactose_free"] is False
    assert lactose_free_milk["is_lactose_free"] is True
    assert "Natriumbenzoat (E 211 Konservierungsstoff)" in cola["additives"]
    assert ", " in cola["additives"]
    assert roll["is_gluten_free"] is False
    assert apple["additives"] == ""
    assert apple["is_gluten_free"] is True
    assert apple["is_lactose_free"] is True
    assert rice["is_gluten_free"] is True
    broth = SupermarketCatalog.product_traits("Hühnerbrühe")
    assert "Mononatriumglutamat (E 621 Geschmacksverstärker)" in broth["additives"]
    assert "Dinatriumguanylat (E 627 Geschmacksverstärker)" in broth["additives"]
    assert broth["is_gluten_free"] is False
    assert "Kaliumsorbat (E 202 Konservierungsstoff)" in SupermarketCatalog.product_traits("Hummus")["additives"]
    assert "Kaliumsorbat (E 202 Konservierungsstoff)" in SupermarketCatalog.product_traits("Matjes")["additives"]
    assert SupermarketCatalog.product_traits("Oregano")["additives"] == ""
    assert SupermarketCatalog.catalog_for("lidl")[0]["additives"] == SupermarketCatalog.product_traits("H-Milch 1,5 %")["additives"]
