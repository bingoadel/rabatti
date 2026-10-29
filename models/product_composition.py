"""Typische Zusammensetzung der Produktarten, ohne Markennamen.

Summary:
    Jede Art aus PRODUCT_KINDS bekommt Fett, Zucker und Eiweiß in Gramm
    sowie ein festes Panel aus Vitaminen und Mineralstoffen. Die Werte sind
    gerundete Referenzwerte je 100 g oder 100 ml, keine Laborwerte einer Marke.
    Prozent im Namen von Quark meint Fett in der Trockenmasse; gespeichert
    ist das Fett in Gramm je 100 g.
"""

from decimal import Decimal

from models.product_kinds import PRODUCT_KINDS

NOTE = "Gerundeter typischer Referenzwert, keine Markenanalyse."

NUTRIENTS = (
    ("vitamin", "vitamin_a_ug", "Vitamin A", "µg"),
    ("vitamin", "vitamin_d_ug", "Vitamin D", "µg"),
    ("vitamin", "vitamin_e_mg", "Vitamin E", "mg"),
    ("vitamin", "vitamin_k_ug", "Vitamin K", "µg"),
    ("vitamin", "vitamin_c_mg", "Vitamin C", "mg"),
    ("vitamin", "vitamin_b1_mg", "Vitamin B1", "mg"),
    ("vitamin", "vitamin_b2_mg", "Vitamin B2", "mg"),
    ("vitamin", "vitamin_b3_mg", "Vitamin B3", "mg"),
    ("vitamin", "vitamin_b6_mg", "Vitamin B6", "mg"),
    ("vitamin", "vitamin_b12_ug", "Vitamin B12", "µg"),
    ("vitamin", "folat_ug", "Folat", "µg"),
    ("mineral", "natrium_mg", "Natrium", "mg"),
    ("mineral", "kalium_mg", "Kalium", "mg"),
    ("mineral", "calcium_mg", "Calcium", "mg"),
    ("mineral", "magnesium_mg", "Magnesium", "mg"),
    ("mineral", "phosphor_mg", "Phosphor", "mg"),
    ("mineral", "eisen_mg", "Eisen", "mg"),
    ("mineral", "zink_mg", "Zink", "mg"),
    ("mineral", "jod_ug", "Jod", "µg"),
)

NUTRIENT_CODES = tuple(item[1] for item in NUTRIENTS)


class ProductComposition:
    """Referenzwerte der Zusammensetzung je Produktart.

    Summary:
        Fett, Zucker, Eiweiß, Vitamine und Mineralstoffe sind gerundete Werte.
        Sie beschreiben die Produktart, nicht eine Marke.
    """

    @staticmethod
    def _decimal(value) -> Decimal:
        return Decimal(str(value))

    @staticmethod
    def panel(kcal, fat, sugar, protein, basis="100 g", **nutrients) -> dict:
        unknown = set(nutrients) - set(NUTRIENT_CODES)
        if unknown:
            raise KeyError(", ".join(sorted(unknown)))
        return {
            "energy_kcal": ProductComposition._decimal(kcal),
            "fat_g": ProductComposition._decimal(fat),
            "sugar_g": ProductComposition._decimal(sugar),
            "protein_g": ProductComposition._decimal(protein),
            "basis": basis,
            "nutrients": {code: ProductComposition._decimal(nutrients.get(code, 0)) for code in NUTRIENT_CODES},
        }

    @staticmethod
    def _milk(kcal, fat, vitamin_a, basis="100 ml"):
        return ProductComposition.panel(
            kcal, fat, 4.8, 3.4, basis,
            vitamin_a_ug=vitamin_a, vitamin_d_ug=0.1, vitamin_b2_mg=0.18, vitamin_b12_ug=0.4,
            calcium_mg=120, phosphor_mg=92, kalium_mg=150, magnesium_mg=12, natrium_mg=45,
            zink_mg=0.4, jod_ug=10,
        )

    @staticmethod
    def _cheese(kcal, fat, protein, natrium, calcium, vitamin_a=250, vitamin_b12=1.5, zink=3.5, sugar=0.1):
        return ProductComposition.panel(
            kcal, fat, sugar, protein,
            vitamin_a_ug=vitamin_a, vitamin_b2_mg=0.3, vitamin_b12_ug=vitamin_b12,
            calcium_mg=calcium, phosphor_mg=int(calcium * 0.65), natrium_mg=natrium,
            kalium_mg=90, magnesium_mg=28, zink_mg=zink, jod_ug=8,
        )

    @staticmethod
    def _fruit(kcal, sugar, protein=0.7, fat=0.2, vitamin_c=12, kalium=180, vitamin_a=6, magnesium=10, folat=15, calcium=12):
        return ProductComposition.panel(
            kcal, fat, sugar, protein,
            vitamin_c_mg=vitamin_c, vitamin_a_ug=vitamin_a, folat_ug=folat, vitamin_k_ug=8,
            kalium_mg=kalium, magnesium_mg=magnesium, calcium_mg=calcium, phosphor_mg=15, eisen_mg=0.3,
        )

    @staticmethod
    def _vegetable(kcal, sugar, protein=1.4, fat=0.2, vitamin_c=20, vitamin_a=40, vitamin_k=40, kalium=250, calcium=30, folat=40, eisen=0.6, magnesium=15):
        return ProductComposition.panel(
            kcal, fat, sugar, protein,
            vitamin_c_mg=vitamin_c, vitamin_a_ug=vitamin_a, vitamin_k_ug=vitamin_k, folat_ug=folat,
            kalium_mg=kalium, calcium_mg=calcium, magnesium_mg=magnesium, phosphor_mg=35, eisen_mg=eisen,
        )

    @staticmethod
    def _meat(kcal, fat, protein, natrium=70, eisen=1.8, zink=3.5, vitamin_b12=1.8, vitamin_b3=6):
        return ProductComposition.panel(
            kcal, fat, 0, protein,
            vitamin_b3_mg=vitamin_b3, vitamin_b6_mg=0.4, vitamin_b12_ug=vitamin_b12, vitamin_b2_mg=0.15,
            natrium_mg=natrium, kalium_mg=320, phosphor_mg=180, eisen_mg=eisen, zink_mg=zink, magnesium_mg=20,
        )

    @staticmethod
    def _fish(kcal, fat, protein, natrium=80, vitamin_d=6, vitamin_b12=3, jod=40, calcium=20, eisen=0.5):
        return ProductComposition.panel(
            kcal, fat, 0, protein,
            vitamin_d_ug=vitamin_d, vitamin_b12_ug=vitamin_b12, vitamin_b3_mg=6, vitamin_b6_mg=0.3,
            natrium_mg=natrium, kalium_mg=340, phosphor_mg=220, jod_ug=jod, calcium_mg=calcium,
            eisen_mg=eisen, zink_mg=0.5, magnesium_mg=25,
        )

    @staticmethod
    def _pasta(kcal=350, fat=1.5, sugar=2.5, protein=12, eisen=1.4, magnesium=40, natrium=6):
        return ProductComposition.panel(
            kcal, fat, sugar, protein,
            vitamin_b1_mg=0.15, vitamin_b3_mg=2, folat_ug=20,
            eisen_mg=eisen, magnesium_mg=magnesium, phosphor_mg=140, kalium_mg=180, zink_mg=1.2, natrium_mg=natrium,
        )

    @staticmethod
    def _rice(protein=7, fat=0.6, eisen=0.4, magnesium=25):
        return ProductComposition.panel(
            350, fat, 0.2, protein,
            vitamin_b1_mg=0.06, vitamin_b3_mg=1.5,
            eisen_mg=eisen, magnesium_mg=magnesium, phosphor_mg=100, kalium_mg=90, zink_mg=1,
        )

    @staticmethod
    def _herb_fresh(vitamin_c=50, vitamin_k=200, vitamin_a=200, calcium=80, eisen=2):
        return ProductComposition.panel(
            40, 0.6, 1, 3,
            vitamin_c_mg=vitamin_c, vitamin_k_ug=vitamin_k, vitamin_a_ug=vitamin_a, folat_ug=80,
            calcium_mg=calcium, kalium_mg=350, magnesium_mg=30, eisen_mg=eisen, phosphor_mg=50,
        )

    @staticmethod
    def _herb_dried(vitamin_k=800, calcium=400, eisen=20, kalium=1200):
        return ProductComposition.panel(
            280, 5, 2, 12,
            vitamin_k_ug=vitamin_k, vitamin_c_mg=20, vitamin_a_ug=300, vitamin_e_mg=3,
            calcium_mg=calcium, kalium_mg=kalium, magnesium_mg=200, eisen_mg=eisen, phosphor_mg=200,
        )

    @staticmethod
    def _spice(kcal=280, fat=6, sugar=2, protein=11, eisen=15, calcium=200, kalium=1200, magnesium=180, vitamin_a=80):
        return ProductComposition.panel(
            kcal, fat, sugar, protein,
            vitamin_a_ug=vitamin_a, vitamin_e_mg=2, vitamin_k_ug=100,
            eisen_mg=eisen, calcium_mg=calcium, kalium_mg=kalium, magnesium_mg=magnesium, phosphor_mg=200, zink_mg=2,
        )

    @staticmethod
    def _salt(natrium=39300, jod=0):
        return ProductComposition.panel(0, 0, 0, 0, natrium_mg=natrium, calcium_mg=20, magnesium_mg=10, jod_ug=jod)

    @staticmethod
    def _oil(vitamin_e, vitamin_k=60):
        return ProductComposition.panel(900, 99.9, 0, 0, vitamin_e_mg=vitamin_e, vitamin_k_ug=vitamin_k)

    @staticmethod
    def _tea():
        return ProductComposition.panel(1, 0, 0, 0, "100 ml Aufguss", kalium_mg=20, magnesium_mg=2)

    @staticmethod
    def put(profile: dict, *names: str, remark: str = "") -> None:
        for name in names:
            if name in COMPOSITION:
                raise ValueError(f"Produktart doppelt beschrieben: {name}")
            row = dict(profile)
            row["nutrients"] = dict(profile["nutrients"])
            row["remark"] = remark
            row["note"] = NOTE
            COMPOSITION[name] = row

    @staticmethod
    def _check() -> None:
        listed = list(PRODUCT_KINDS)
        missing = [name for name in listed if name not in COMPOSITION]
        extra = [name for name in COMPOSITION if name not in set(listed)]
        if missing or extra or len(COMPOSITION) != len(listed):
            raise RuntimeError(f"Zusammensetzung passt nicht zur Produktliste. Fehlend: {missing}. Zu viel: {extra}.")

    @staticmethod
    def composition_rows():
        """Liefert Name und Zusammensetzung in der Reihenfolge der Produktliste."""
        for name in PRODUCT_KINDS:
            yield name, COMPOSITION[name]


MILK_15 = ProductComposition._milk(47, 1.5, 15)
MILK_35 = ProductComposition._milk(64, 3.5, 35)
MILK_38 = ProductComposition._milk(68, 3.8, 40)
WHEAT_PASTA = ProductComposition._pasta()
WHITE_RICE = ProductComposition._rice()
FRESH_HERB = ProductComposition._herb_fresh()
DRIED_HERB = ProductComposition._herb_dried()
PLAIN_SPICE = ProductComposition._spice()
TABLE_SALT = ProductComposition._salt()
TEA = ProductComposition._tea()
WATER = ProductComposition.panel(0, 0, 0, 0, "100 ml", calcium_mg=40, magnesium_mg=15, natrium_mg=10, kalium_mg=2)
POTATO = ProductComposition._vegetable(75, 0.8, protein=2, vitamin_c=17, vitamin_a=2, vitamin_k=4, kalium=420, calcium=10, folat=20, eisen=0.5, magnesium=22)
TOMATO = ProductComposition._vegetable(18, 2.6, protein=0.9, vitamin_c=14, vitamin_a=42, vitamin_k=8, kalium=240, calcium=10)
PAPRIKA_RED = ProductComposition._vegetable(31, 5, protein=1, vitamin_c=140, vitamin_a=160, vitamin_k=5, kalium=210)
ZUCCHINI = ProductComposition._vegetable(17, 2.5, protein=1.2, vitamin_c=17, vitamin_a=10, vitamin_k=4, kalium=260)
ONION = ProductComposition._vegetable(40, 4.2, protein=1.1, vitamin_c=7, vitamin_a=1, vitamin_k=1, kalium=150, calcium=20)
CABBAGE = ProductComposition._vegetable(25, 3.5, protein=1.3, vitamin_c=45, vitamin_a=5, vitamin_k=80, kalium=170)
SALAD = ProductComposition._vegetable(14, 1.5, protein=1.2, vitamin_c=8, vitamin_a=25, vitamin_k=100, kalium=180, folat=40)
HARD_CHEESE = ProductComposition._cheese(370, 29, 25, 800, 800)
BLUE_CHEESE = ProductComposition._cheese(350, 29, 19, 1200, 500)
FRESH_CHEESE = ProductComposition._cheese(250, 23, 7, 350, 80, vitamin_a=180, sugar=3)
BROTH = ProductComposition.panel(
    200, 10, 6, 10,
    natrium_mg=18000, kalium_mg=400, calcium_mg=40, eisen_mg=1,
)
SEASONED_SPICE = ProductComposition.panel(
    280, 6, 4, 10,
    natrium_mg=6000, kalium_mg=800, calcium_mg=150, eisen_mg=8, magnesium_mg=80,
)

COMPOSITION: dict[str, dict] = {}


ProductComposition.put(MILK_15, "H-Milch 1,5 %", "Frischmilch 1,5 %", "Laktosefreie Milch")
ProductComposition.put(MILK_35, "H-Milch 3,5 %", "Frischmilch 3,5 %")
ProductComposition.put(MILK_38, "Vollmilch 3,8 %")
ProductComposition.put(ProductComposition.panel(36, 0.5, 4, 3.5, "100 ml", vitamin_b2_mg=0.16, vitamin_b12_ug=0.3, calcium_mg=110, kalium_mg=150, phosphor_mg=90, natrium_mg=50, jod_ug=8), "Buttermilch")
ProductComposition.put(ProductComposition.panel(55, 1.5, 4, 3.3, "100 ml", vitamin_b2_mg=0.16, vitamin_b12_ug=0.3, calcium_mg=120, kalium_mg=150, phosphor_mg=90, natrium_mg=40, jod_ug=8), "Kefir")
ProductComposition.put(ProductComposition.panel(67, 0.2, 3.2, 13, vitamin_b2_mg=0.3, vitamin_b12_ug=0.8, calcium_mg=90, phosphor_mg=160, kalium_mg=130, natrium_mg=40, jod_ug=8), "Magerquark")
ProductComposition.put(
    ProductComposition.panel(105, 5, 3, 12, vitamin_b2_mg=0.3, vitamin_b12_ug=0.7, calcium_mg=90, phosphor_mg=160, kalium_mg=120, natrium_mg=40),
    "Quark (20 %)",
    remark="20 % im Namen ist Fett in der Trockenmasse, Fett steht in g je 100 g.",
)
ProductComposition.put(
    ProductComposition.panel(145, 10.5, 3, 10, vitamin_a_ug=100, vitamin_b2_mg=0.25, vitamin_b12_ug=0.5, calcium_mg=85, phosphor_mg=140, natrium_mg=40),
    "Quark (40 %)",
    remark="40 % im Namen ist Fett in der Trockenmasse, Fett steht in g je 100 g.",
)
ProductComposition.put(ProductComposition.panel(160, 12, 3.2, 8.5, vitamin_a_ug=120, vitamin_b2_mg=0.2, calcium_mg=80, phosphor_mg=130, natrium_mg=40), "Sahnequark")
ProductComposition.put(ProductComposition.panel(115, 5, 2.5, 10, vitamin_b2_mg=0.25, calcium_mg=90, phosphor_mg=140, natrium_mg=400, kalium_mg=140), "Kräuterquark")
ProductComposition.put(ProductComposition.panel(62, 3.5, 4, 3.8, vitamin_b2_mg=0.18, vitamin_b12_ug=0.3, calcium_mg=120, phosphor_mg=95, kalium_mg=160, natrium_mg=45, jod_ug=8), "Naturjoghurt")
ProductComposition.put(ProductComposition.panel(95, 2.5, 14, 3.2, vitamin_b2_mg=0.14, calcium_mg=110, phosphor_mg=90, kalium_mg=160, natrium_mg=45), "Fruchtjoghurt")
ProductComposition.put(ProductComposition.panel(133, 10, 3.5, 5.5, vitamin_a_ug=100, vitamin_b2_mg=0.2, calcium_mg=110, phosphor_mg=130, natrium_mg=40), "Griechischer Joghurt")
ProductComposition.put(ProductComposition.panel(63, 0.2, 4, 11, vitamin_b2_mg=0.25, vitamin_b12_ug=0.5, calcium_mg=130, phosphor_mg=180, kalium_mg=140, natrium_mg=40), "Skyr")
ProductComposition.put(ProductComposition.panel(292, 30, 3.2, 2.4, vitamin_a_ug=350, vitamin_d_ug=0.3, vitamin_b2_mg=0.15, calcium_mg=70, phosphor_mg=60, natrium_mg=35), "Schlagsahne")
ProductComposition.put(ProductComposition.panel(110, 10, 3.5, 3, vitamin_a_ug=100, vitamin_b2_mg=0.15, calcium_mg=90, phosphor_mg=80, natrium_mg=40), "Saure Sahne")
ProductComposition.put(ProductComposition.panel(240, 24, 3, 2.8, vitamin_a_ug=250, calcium_mg=70, phosphor_mg=60, natrium_mg=40), "Schmand")
ProductComposition.put(ProductComposition.panel(290, 30, 2.5, 2.4, vitamin_a_ug=300, calcium_mg=65, phosphor_mg=60, natrium_mg=35), "Crème fraîche")
ProductComposition.put(ProductComposition.panel(741, 83, 0.6, 0.7, vitamin_a_ug=650, vitamin_d_ug=1.2, vitamin_e_mg=2, calcium_mg=15, natrium_mg=10, phosphor_mg=20), "Butter")
ProductComposition.put(ProductComposition.panel(390, 41, 1, 5, vitamin_a_ug=320, vitamin_d_ug=0.6, calcium_mg=20, natrium_mg=50), "Halbfettbutter")
ProductComposition.put(ProductComposition.panel(720, 80, 0.4, 0.2, vitamin_a_ug=800, vitamin_d_ug=7.5, vitamin_e_mg=12, natrium_mg=400, kalium_mg=20), "Margarine")

ProductComposition.put(ProductComposition._cheese(356, 28, 24, 750, 800), "Gouda jung")
ProductComposition.put(ProductComposition._cheese(380, 31, 26, 900, 850), "Gouda mittelalt")
ProductComposition.put(ProductComposition._cheese(400, 33, 28, 1000, 900), "Gouda alt")
ProductComposition.put(ProductComposition._cheese(350, 27, 25, 800, 800), "Edamer")
ProductComposition.put(ProductComposition._cheese(350, 27, 26, 800, 800), "Tilsiter")
ProductComposition.put(ProductComposition._cheese(360, 29, 25, 800, 780), "Maasdamer")
ProductComposition.put(ProductComposition._cheese(340, 28, 21, 700, 600), "Butterkäse")
ProductComposition.put(ProductComposition._cheese(400, 32, 28, 800, 900), "Bergkäse")
ProductComposition.put(ProductComposition._cheese(400, 31, 29, 450, 1000), "Emmentaler")
ProductComposition.put(ProductComposition._cheese(400, 32, 26, 700, 800), "Appenzeller")
ProductComposition.put(ProductComposition._cheese(410, 33, 27, 700, 1000), "Gruyère")
ProductComposition.put(ProductComposition._cheese(392, 28, 33, 1600, 1100, zink=4), "Parmesan")
ProductComposition.put(ProductComposition._cheese(390, 30, 28, 1800, 900), "Pecorino")
ProductComposition.put(ProductComposition._cheese(384, 28, 33, 1500, 1100), "Grana Padano")
ProductComposition.put(ProductComposition._cheese(400, 32, 26, 700, 800), "Manchego")
ProductComposition.put(ProductComposition._cheese(280, 22, 18, 900, 400), "Hirtenkäse")
ProductComposition.put(ProductComposition._cheese(264, 21, 16, 1100, 490), "Feta", "Schafskäse")
ProductComposition.put(ProductComposition._cheese(270, 21, 18, 400, 300), "Ziegenkäse")
ProductComposition.put(ProductComposition._cheese(320, 25, 22, 1200, 700), "Halloumi")
ProductComposition.put(ProductComposition._cheese(253, 17, 18, 400, 400, vitamin_a=150, sugar=1), "Mozzarella")
ProductComposition.put(ProductComposition._cheese(280, 22, 16, 350, 350, vitamin_a=180, sugar=0.5), "Büffelmozzarella")
ProductComposition.put(ProductComposition._cheese(300, 24, 14, 300, 250, vitamin_a=200, sugar=1), "Burrata")
ProductComposition.put(ProductComposition._cheese(160, 11, 9, 80, 200, vitamin_a=150, sugar=3), "Ricotta")
ProductComposition.put(ProductComposition._cheese(430, 45, 4, 50, 120, vitamin_a=350, sugar=3), "Mascarpone")
ProductComposition.put(ProductComposition._cheese(98, 4, 12, 350, 80, sugar=3, vitamin_a=40), "Hüttenkäse")
ProductComposition.put(FRESH_CHEESE, "Frischkäse")
ProductComposition.put(ProductComposition._cheese(240, 22, 6, 600, 80, sugar=3, vitamin_a=180), "Kräuterfrischkäse")
ProductComposition.put(ProductComposition._cheese(290, 23, 20, 800, 400), "Camembert", "Schimmelkäse")
ProductComposition.put(ProductComposition._cheese(334, 28, 18, 600, 180), "Brie")
ProductComposition.put(BLUE_CHEESE, "Gorgonzola", "Blauschimmelkäse")
ProductComposition.put(ProductComposition._cheese(369, 31, 19, 1600, 600), "Roquefort")
ProductComposition.put(ProductComposition._cheese(270, 20, 20, 800, 500), "Limburger")
ProductComposition.put(ProductComposition._cheese(130, 0.5, 30, 1000, 120, vitamin_a=20, vitamin_b12=1), "Harzer Käse")
ProductComposition.put(HARD_CHEESE, "Raclettekäse", "Scheibenkäse")
ProductComposition.put(ProductComposition._cheese(380, 30, 26, 800, 900), "Reibekäse")
ProductComposition.put(ProductComposition._cheese(280, 22, 12, 1200, 400, sugar=5), "Schmelzkäse")

ProductComposition.put(ProductComposition._vegetable(220, 2.5, protein=7, fat=1.2, vitamin_c=0, vitamin_a=0, vitamin_k=2, kalium=180, calcium=30, eisen=1.5, magnesium=30), "Mischbrot")
ProductComposition.put(ProductComposition.panel(200, 1.5, 2, 8, vitamin_b1_mg=0.2, vitamin_b3_mg=2, magnesium_mg=70, eisen_mg=2.5, phosphor_mg=200, kalium_mg=220, zink_mg=1.5, natrium_mg=450), "Vollkornbrot")
ProductComposition.put(ProductComposition.panel(210, 1, 2, 6, vitamin_b1_mg=0.15, magnesium_mg=40, eisen_mg=1.8, kalium_mg=180, natrium_mg=500, phosphor_mg=120), "Roggenbrot")
ProductComposition.put(ProductComposition.panel(260, 1.5, 3, 8, vitamin_b1_mg=0.1, eisen_mg=1, kalium_mg=120, natrium_mg=480, phosphor_mg=90, calcium_mg=20), "Weißbrot", "Baguette", "Brötchen")
ProductComposition.put(ProductComposition.panel(270, 4, 5, 8, vitamin_b1_mg=0.15, eisen_mg=1.2, natrium_mg=500, kalium_mg=130, calcium_mg=40), "Toast")
ProductComposition.put(ProductComposition.panel(280, 2, 2, 8, natrium_mg=900, kalium_mg=120, eisen_mg=1, phosphor_mg=90), "Laugenbrötchen")
ProductComposition.put(ProductComposition.panel(410, 21, 8, 8, vitamin_a_ug=150, natrium_mg=400, calcium_mg=30, eisen_mg=1), "Croissant")
ProductComposition.put(ProductComposition.panel(350, 2, 3, 10, magnesium_mg=70, eisen_mg=2, natrium_mg=500, phosphor_mg=220, kalium_mg=300), "Knäckebrot")
ProductComposition.put(ProductComposition.panel(240, 2, 2, 9, vitamin_b1_mg=0.15, magnesium_mg=50, eisen_mg=2, phosphor_mg=160, kalium_mg=180, natrium_mg=450), "Dinkelbrot", "Mehrkornbrot")
ProductComposition.put(ProductComposition.panel(180, 1.5, 4, 5, magnesium_mg=40, eisen_mg=1.6, kalium_mg=200, natrium_mg=450, phosphor_mg=120), "Pumpernickel")
ProductComposition.put(ProductComposition.panel(280, 8, 2, 9, vitamin_e_mg=3, magnesium_mg=60, eisen_mg=2, phosphor_mg=180, kalium_mg=200, natrium_mg=450, zink_mg=1.5), "Sonnenblumenkernbrot")
ProductComposition.put(ProductComposition.panel(270, 7, 2, 9, magnesium_mg=70, eisen_mg=2.2, phosphor_mg=200, kalium_mg=220, natrium_mg=450, zink_mg=1.6), "Kürbiskernbrot")
ProductComposition.put(ProductComposition.panel(270, 2, 2, 8, vitamin_b1_mg=0.1, eisen_mg=1, natrium_mg=500, kalium_mg=110, phosphor_mg=90), "Ciabatta", "Fladenbrot", "Pita")
ProductComposition.put(ProductComposition.panel(270, 1.5, 4, 10, vitamin_b1_mg=0.15, eisen_mg=1.2, natrium_mg=450, kalium_mg=120, phosphor_mg=100), "Bagel")
ProductComposition.put(ProductComposition.panel(260, 3, 2, 9, vitamin_b1_mg=0.15, eisen_mg=1.6, magnesium_mg=40, natrium_mg=480, kalium_mg=150, phosphor_mg=140), "Mehrkornbrötchen", "Roggenbrötchen", "Körnerbrötchen")
ProductComposition.put(ProductComposition.panel(290, 8, 2, 9, magnesium_mg=50, eisen_mg=1.5, natrium_mg=480, kalium_mg=140, phosphor_mg=160, calcium_mg=80), "Sesambrötchen", "Mohnbrötchen")
ProductComposition.put(ProductComposition.panel(280, 3, 2, 8, vitamin_b1_mg=0.1, eisen_mg=1, natrium_mg=500, kalium_mg=120, phosphor_mg=90), "Kaisersemmel")
ProductComposition.put(ProductComposition.panel(280, 2, 2, 8, natrium_mg=900, kalium_mg=120, eisen_mg=1, phosphor_mg=90), "Laugenstange", "Laugenbrezel")
ProductComposition.put(ProductComposition.panel(300, 6, 14, 7, eisen_mg=1.4, kalium_mg=180, natrium_mg=350, phosphor_mg=100, magnesium_mg=25), "Rosinenbrötchen")
ProductComposition.put(ProductComposition.panel(400, 22, 20, 5, vitamin_a_ug=40, natrium_mg=350, calcium_mg=30, eisen_mg=1), "Donut")
ProductComposition.put(ProductComposition.panel(320, 14, 18, 6, vitamin_a_ug=50, natrium_mg=280, calcium_mg=30, eisen_mg=0.8), "Krapfen", "Berliner")
ProductComposition.put(ProductComposition.panel(450, 28, 30, 6, vitamin_e_mg=2, magnesium_mg=40, calcium_mg=40, eisen_mg=1.2, natrium_mg=180), "Nussecke")
ProductComposition.put(ProductComposition.panel(440, 24, 16, 7, vitamin_a_ug=120, natrium_mg=350, calcium_mg=40, eisen_mg=1.2, magnesium_mg=25), "Schokocroissant")
ProductComposition.put(ProductComposition.panel(380, 14, 22, 6, vitamin_a_ug=60, natrium_mg=320, calcium_mg=40, eisen_mg=1), "Zimtschnecke", "Streuselschnecke", "Franzbrötchen")
ProductComposition.put(ProductComposition.panel(380, 16, 24, 5, vitamin_a_ug=50, natrium_mg=300, calcium_mg=40, eisen_mg=0.8), "Muffin", "Amerikaner")
ProductComposition.put(ProductComposition.panel(280, 12, 14, 4, vitamin_c_mg=2, natrium_mg=280, kalium_mg=90, calcium_mg=20, eisen_mg=0.6), "Apfeltasche")

ProductComposition.put(ProductComposition._fruit(89, 17, protein=1.1, vitamin_c=9, kalium=360, vitamin_a=3, magnesium=27, folat=20), "Bananen")
ProductComposition.put(ProductComposition._fruit(52, 10, protein=0.3, vitamin_c=12, kalium=120), "Äpfel")
ProductComposition.put(ProductComposition._fruit(57, 10, protein=0.4, vitamin_c=4, kalium=120), "Birnen")
ProductComposition.put(ProductComposition._fruit(47, 9, protein=0.9, vitamin_c=50, kalium=180, folat=30, calcium=40), "Orangen", "Blutorangen")
ProductComposition.put(ProductComposition._fruit(29, 2.5, protein=1.1, vitamin_c=53, kalium=140, calcium=26), "Zitronen")
ProductComposition.put(ProductComposition._fruit(30, 1.7, protein=0.7, vitamin_c=29, kalium=100), "Limetten")
ProductComposition.put(ProductComposition._fruit(42, 7, protein=0.8, vitamin_c=34, kalium=150), "Grapefruit")
ProductComposition.put(ProductComposition._fruit(53, 10, protein=0.8, vitamin_c=27, kalium=170), "Mandarinen")
ProductComposition.put(ProductComposition._fruit(47, 9, protein=0.9, vitamin_c=49, kalium=180), "Clementinen")
ProductComposition.put(ProductComposition._fruit(32, 5, protein=0.7, vitamin_c=59, kalium=150, folat=24), "Erdbeeren")
ProductComposition.put(ProductComposition._fruit(52, 4.4, protein=1.2, vitamin_c=26, kalium=150, magnesium=22, folat=21), "Himbeeren")
ProductComposition.put(ProductComposition._fruit(43, 4.9, protein=1.4, vitamin_c=21, kalium=160, magnesium=20), "Brombeeren")
ProductComposition.put(ProductComposition._fruit(57, 10, protein=0.7, vitamin_c=10, kalium=77), "Heidelbeeren")
ProductComposition.put(ProductComposition._fruit(56, 7, protein=1.4, vitamin_c=41, kalium=280), "Johannisbeeren")
ProductComposition.put(ProductComposition._fruit(69, 16, protein=0.7, vitamin_c=3, kalium=190), "Trauben hell", "Trauben dunkel")
ProductComposition.put(ProductComposition._fruit(61, 9, protein=1.1, fat=0.5, vitamin_c=93, kalium=312, magnesium=17, folat=25), "Kiwi grün")
ProductComposition.put(ProductComposition._fruit(63, 12, protein=1.2, fat=0.3, vitamin_c=150, kalium=300, magnesium=15), "Kiwi gelb")
ProductComposition.put(ProductComposition._fruit(60, 14, protein=0.8, vitamin_c=36, vitamin_a=54, kalium=170, folat=43), "Mango")
ProductComposition.put(ProductComposition._fruit(50, 10, protein=0.5, vitamin_c=48, kalium=110), "Ananas")
ProductComposition.put(ProductComposition._fruit(43, 8, protein=0.5, vitamin_c=61, vitamin_a=47, kalium=180, folat=37), "Papaya")
ProductComposition.put(ProductComposition._fruit(30, 6, protein=0.6, vitamin_c=8, vitamin_a=28, kalium=110), "Wassermelone")
ProductComposition.put(ProductComposition._fruit(34, 8, protein=0.8, vitamin_c=18, vitamin_a=170, kalium=270), "Honigmelone")
ProductComposition.put(ProductComposition._fruit(39, 8, protein=0.9, vitamin_c=7, vitamin_a=16, kalium=190), "Pfirsiche")
ProductComposition.put(ProductComposition._fruit(44, 8, protein=1.1, vitamin_c=5, vitamin_a=17, kalium=200), "Nektarinen")
ProductComposition.put(ProductComposition._fruit(48, 9, protein=0.9, vitamin_c=10, vitamin_a=96, kalium=260), "Aprikosen")
ProductComposition.put(ProductComposition._fruit(46, 10, protein=0.7, vitamin_c=9, kalium=160), "Pflaumen", "Zwetschgen")
ProductComposition.put(ProductComposition._fruit(63, 13, protein=1.1, vitamin_c=7, kalium=220), "Kirschen")
ProductComposition.put(ProductComposition._fruit(74, 16, protein=0.8, vitamin_c=2, kalium=230, calcium=35), "Feigen")
ProductComposition.put(ProductComposition.panel(
    282, 0.4, 63, 2.5, kalium_mg=650, magnesium_mg=43, calcium_mg=64, eisen_mg=1, phosphor_mg=60,
), "Datteln")
ProductComposition.put(ProductComposition.panel(
    160, 15, 0.7, 2,
    vitamin_e_mg=2.1, vitamin_k_ug=21, vitamin_b6_mg=0.26, folat_ug=81, vitamin_c_mg=10,
    kalium_mg=485, magnesium_mg=29, phosphor_mg=52, natrium_mg=7,
), "Avocado")
ProductComposition.put(ProductComposition._fruit(83, 14, protein=1.7, fat=1.2, vitamin_c=10, kalium=230), "Granatapfel")
ProductComposition.put(ProductComposition._fruit(70, 16, protein=0.6, vitamin_c=8, vitamin_a=81, kalium=160), "Kaki")
ProductComposition.put(ProductComposition._fruit(97, 11, protein=2.2, vitamin_c=30, kalium=350, magnesium=29), "Passionsfrucht")
ProductComposition.put(ProductComposition._fruit(66, 15, protein=0.8, vitamin_c=72, kalium=170), "Litschi")

ProductComposition.put(POTATO, "Kartoffeln", "Festkochende Kartoffeln", "Mehligkochende Kartoffeln", "Drillinge")
ProductComposition.put(ProductComposition._vegetable(86, 4.2, protein=1.6, vitamin_c=24, vitamin_a=709, vitamin_k=2, kalium=337, calcium=30, magnesium=25, folat=11), "Süßkartoffeln")
ProductComposition.put(ProductComposition._herb_fresh(vitamin_c=150, vitamin_k=1640, vitamin_a=420, calcium=140, eisen=6), "Blattpetersilie", "Petersilie", "Krause Petersilie")
ProductComposition.put(ProductComposition._herb_fresh(vitamin_c=58, vitamin_k=210, vitamin_a=220, calcium=90, eisen=1.6), "Schnittlauch")
ProductComposition.put(ProductComposition._herb_fresh(vitamin_c=18, vitamin_k=415, vitamin_a=260, calcium=180, eisen=3), "Basilikum")
ProductComposition.put(ProductComposition._herb_fresh(vitamin_c=85, vitamin_k=60, vitamin_a=380, calcium=200, eisen=6), "Dill")
ProductComposition.put(ProductComposition._herb_fresh(vitamin_c=27, vitamin_k=310, vitamin_a=340, calcium=70, eisen=1.8), "Koriander")
ProductComposition.put(ProductComposition._herb_fresh(vitamin_c=32, vitamin_k=80, vitamin_a=210, calcium=200, eisen=5), "Minze")
ProductComposition.put(ProductComposition._herb_fresh(vitamin_c=22, vitamin_k=100, vitamin_a=150, calcium=320, eisen=7), "Rosmarin")
ProductComposition.put(ProductComposition._herb_fresh(vitamin_c=160, vitamin_k=160, vitamin_a=240, calcium=400, eisen=17), "Thymian")
ProductComposition.put(SALAD, "Eisbergsalat", "Kopfsalat", "Feldsalat", "Romanasalat")
ProductComposition.put(ProductComposition._vegetable(25, 2, protein=2.6, vitamin_c=15, vitamin_a=120, vitamin_k=110, kalium=370, calcium=160, folat=97, eisen=1.5), "Rucola")
ProductComposition.put(ProductComposition._vegetable(15, 1.7, protein=0.7, vitamin_c=8, vitamin_a=5, vitamin_k=16, kalium=140, calcium=16), "Gurke", "Schmorgurke")
ProductComposition.put(TOMATO, "Tomaten", "Cherrytomaten", "Rispentomaten", "Fleischtomaten")
ProductComposition.put(PAPRIKA_RED, "Paprika rot")
ProductComposition.put(ProductComposition._vegetable(27, 5, protein=1, vitamin_c=184, vitamin_a=10, vitamin_k=5, kalium=210), "Paprika gelb")
ProductComposition.put(ProductComposition._vegetable(20, 2.4, protein=0.9, vitamin_c=80, vitamin_a=18, vitamin_k=8, kalium=175), "Paprika grün")
ProductComposition.put(ProductComposition._vegetable(31, 4, protein=1.5, vitamin_c=140, vitamin_a=50, vitamin_k=8, kalium=320), "Peperoni")
ProductComposition.put(ProductComposition._vegetable(40, 5, protein=1.9, vitamin_c=144, vitamin_a=48, vitamin_k=14, kalium=320), "Chili")
ProductComposition.put(ZUCCHINI, "Zucchini", "Zucchini gelb")
ProductComposition.put(ProductComposition._vegetable(25, 3.5, protein=1, vitamin_c=2, vitamin_a=1, vitamin_k=3, kalium=230, magnesium=14), "Aubergine")
ProductComposition.put(ProductComposition._vegetable(41, 4.7, protein=0.9, vitamin_c=6, vitamin_a=835, vitamin_k=13, kalium=320, calcium=33, folat=19), "Möhren")
ProductComposition.put(ProductComposition._vegetable(75, 4.8, protein=1.2, vitamin_c=17, vitamin_a=0, vitamin_k=22, kalium=375, calcium=36, folat=67, magnesium=29), "Pastinaken")
ProductComposition.put(ProductComposition._vegetable(43, 7, protein=1.6, vitamin_c=5, vitamin_a=2, vitamin_k=0, kalium=325, calcium=16, folat=109, eisen=0.8, magnesium=23), "Rote Bete")
ProductComposition.put(ProductComposition._vegetable(16, 1.5, protein=0.7, vitamin_c=8, vitamin_k=30, kalium=300, calcium=40), "Sellerie")
ProductComposition.put(ProductComposition._vegetable(31, 3.9, protein=1.5, vitamin_c=12, vitamin_a=83, vitamin_k=47, kalium=180, folat=64), "Lauch")
ProductComposition.put(ProductComposition._vegetable(32, 2.3, protein=1.8, vitamin_c=19, vitamin_a=50, vitamin_k=200, kalium=280), "Frühlingszwiebeln")
ProductComposition.put(ONION, "Zwiebeln", "Rote Zwiebeln")
ProductComposition.put(ProductComposition._vegetable(72, 7.9, protein=2.5, vitamin_c=8, vitamin_k=1, kalium=330, calcium=36), "Schalotten")
ProductComposition.put(ProductComposition.panel(149, 0.5, 1, 6.4, vitamin_c_mg=31, vitamin_b6_mg=1.2, calcium_mg=181, kalium_mg=400, phosphor_mg=150, eisen_mg=1.7, magnesium_mg=25), "Knoblauch")
ProductComposition.put(ProductComposition.panel(80, 0.8, 1.7, 1.8, vitamin_b6_mg=0.16, vitamin_c_mg=5, kalium_mg=415, magnesium_mg=43, phosphor_mg=34, eisen_mg=0.6), "Ingwer")
ProductComposition.put(ProductComposition.panel(22, 0.3, 0.5, 3.1, vitamin_b2_mg=0.4, vitamin_b3_mg=3.6, vitamin_d_ug=0.2, kalium_mg=320, phosphor_mg=86, eisen_mg=0.5, natrium_mg=5), "Champignons")
ProductComposition.put(ProductComposition.panel(33, 0.4, 1.1, 3.3, vitamin_b2_mg=0.3, vitamin_b3_mg=5, kalium_mg=420, phosphor_mg=120, eisen_mg=1.3), "Austernpilze")
ProductComposition.put(ProductComposition.panel(38, 0.5, 0.4, 1.5, vitamin_d_ug=2, vitamin_b2_mg=0.2, kalium_mg=500, eisen_mg=3.5, phosphor_mg=50), "Pfifferlinge")
ProductComposition.put(ProductComposition._vegetable(34, 1.7, protein=2.8, vitamin_c=89, vitamin_a=31, vitamin_k=102, kalium=316, calcium=47, folat=63, eisen=0.7, magnesium=21), "Brokkoli")
ProductComposition.put(ProductComposition._vegetable(25, 1.9, protein=1.9, vitamin_c=48, vitamin_a=1, vitamin_k=16, kalium=300, calcium=22, folat=57), "Blumenkohl")
ProductComposition.put(ProductComposition._vegetable(31, 2, protein=2.5, vitamin_c=70, vitamin_k=20, kalium=320, calcium=30, folat=50), "Romanesco")
ProductComposition.put(CABBAGE, "Weißkohl")
ProductComposition.put(ProductComposition._vegetable(31, 3.8, protein=1.4, vitamin_c=57, vitamin_a=6, vitamin_k=38, kalium=240), "Rotkohl")
ProductComposition.put(ProductComposition._vegetable(27, 2.3, protein=2, vitamin_c=31, vitamin_a=50, vitamin_k=80, kalium=230, calcium=35), "Wirsing")
ProductComposition.put(ProductComposition._vegetable(16, 1.2, protein=1.2, vitamin_c=27, vitamin_a=16, vitamin_k=43, kalium=240), "Chinakohl")
ProductComposition.put(ProductComposition._vegetable(49, 2.3, protein=4.3, fat=0.9, vitamin_c=120, vitamin_a=500, vitamin_k=390, kalium=490, calcium=150, folat=140, eisen=1.5, magnesium=47), "Grünkohl")
ProductComposition.put(ProductComposition._vegetable(43, 2.2, protein=3.4, vitamin_c=85, vitamin_a=38, vitamin_k=177, kalium=390, calcium=42, folat=61), "Rosenkohl")
ProductComposition.put(ProductComposition._vegetable(27, 2.6, protein=1.7, vitamin_c=62, vitamin_a=2, vitamin_k=0, kalium=350, calcium=24), "Kohlrabi")
ProductComposition.put(ProductComposition._vegetable(20, 1.9, protein=2.2, vitamin_c=20, vitamin_a=50, vitamin_k=42, kalium=200, folat=52), "Spargel weiß", "Spargel grün")
ProductComposition.put(ProductComposition._vegetable(31, 3.9, protein=1.2, vitamin_c=12, vitamin_a=48, vitamin_k=63, kalium=410, calcium=49), "Fenchel")
ProductComposition.put(ProductComposition._vegetable(63, 2.8, protein=1.5, vitamin_c=12, vitamin_a=420, vitamin_k=1, kalium=350, calcium=25, magnesium=18), "Hokkaido", "Butternut")
ProductComposition.put(ProductComposition._vegetable(19, 1.1, protein=1.8, vitamin_c=30, vitamin_a=300, vitamin_k=830, kalium=380, calcium=51, magnesium=81, eisen=1.8, folat=14), "Mangold")
ProductComposition.put(ProductComposition._vegetable(23, 0.4, protein=2.9, vitamin_c=28, vitamin_a=469, vitamin_k=483, kalium=558, calcium=99, magnesium=79, eisen=2.7, folat=194), "Spinat")
ProductComposition.put(ProductComposition._vegetable(42, 4, protein=2.8, vitamin_c=60, vitamin_a=54, vitamin_k=25, kalium=200), "Zuckerschoten")
ProductComposition.put(ProductComposition._vegetable(31, 3.3, protein=1.8, vitamin_c=12, vitamin_a=35, vitamin_k=43, kalium=210, folat=33), "Grüne Bohnen")
ProductComposition.put(ProductComposition._vegetable(16, 1.9, protein=0.7, vitamin_c=15, vitamin_k=1, kalium=230, calcium=25), "Radieschen", "Rettich")

ProductComposition.put(ProductComposition._meat(250, 20, 18, eisen=1.5, zink=3.5), "Hackfleisch")
ProductComposition.put(ProductComposition._meat(217, 15, 20, eisen=2.3, zink=4.5, vitamin_b12=2.1), "Rinderhackfleisch")
ProductComposition.put(ProductComposition._meat(110, 1.3, 23, eisen=0.4, zink=0.7, vitamin_b12=0.2, vitamin_b3=11), "Hähnchenbrust")
ProductComposition.put(ProductComposition._meat(177, 11, 18, eisen=0.7, zink=1.5, vitamin_b12=0.3, vitamin_b3=5), "Hähnchenschenkel")
ProductComposition.put(ProductComposition._meat(105, 1, 24, eisen=0.4, zink=1.2, vitamin_b12=0.4, vitamin_b3=10), "Putenbrust")
ProductComposition.put(ProductComposition._meat(143, 4, 22, eisen=0.8, zink=2, vitamin_b12=0.6, vitamin_b3=7), "Schweineschnitzel")
ProductComposition.put(ProductComposition._meat(250, 19, 17, eisen=0.8, zink=2.2, vitamin_b12=0.6), "Schweinenacken")
ProductComposition.put(ProductComposition._meat(150, 6, 22, eisen=2.5, zink=4.2, vitamin_b12=2), "Rindersteak", "Rinderrouladen")
ProductComposition.put(ProductComposition._meat(250, 18, 18, eisen=1.8, zink=3, vitamin_b12=2.2), "Lammkotelett")
ProductComposition.put(ProductComposition._meat(300, 26, 14, natrium=800, eisen=1, zink=2, vitamin_b12=1), "Bratwurst")
ProductComposition.put(ProductComposition._meat(310, 28, 12, natrium=900, eisen=1, zink=1.8, vitamin_b12=1), "Fleischwurst", "Mortadella")
ProductComposition.put(ProductComposition._meat(280, 25, 12, natrium=900, eisen=1, zink=1.5, vitamin_b12=0.8), "Wiener Würstchen")
ProductComposition.put(ProductComposition._meat(400, 34, 22, natrium=1800, eisen=1.5, zink=3, vitamin_b12=1.5), "Salami")
ProductComposition.put(ProductComposition._meat(107, 3, 18, natrium=900, eisen=0.6, zink=1.5, vitamin_b12=0.4), "Kochschinken")
ProductComposition.put(ProductComposition._meat(230, 14, 26, natrium=2000, eisen=1, zink=2.5, vitamin_b12=0.6), "Rohschinken")
ProductComposition.put(ProductComposition.panel(326, 28, 1, 14, vitamin_a_ug=4200, vitamin_b12_ug=12, vitamin_b2_mg=1.2, eisen_mg=6, zink_mg=2.5, natrium_mg=800, phosphor_mg=200), "Leberwurst")
ProductComposition.put(ProductComposition._meat(380, 36, 12, natrium=900, eisen=1.2, zink=2, vitamin_b12=1), "Teewurst")
ProductComposition.put(ProductComposition.panel(300, 26, 1, 14, vitamin_a_ug=5000, vitamin_b12_ug=14, vitamin_b2_mg=1.3, eisen_mg=7, zink_mg=3, natrium_mg=750, phosphor_mg=220), "Kalbsleberwurst")
ProductComposition.put(ProductComposition._meat(380, 34, 16, natrium=1400, eisen=1.5, zink=2.2, vitamin_b12=1.2), "Mettwurst", "Zwiebelmettwurst")
ProductComposition.put(ProductComposition._meat(160, 8, 16, natrium=900, eisen=1, zink=1.5, vitamin_b12=0.8), "Presswurst", "Presskopf", "Sülze")
ProductComposition.put(ProductComposition.panel(360, 32, 1, 14, eisen_mg=6.5, vitamin_b12_ug=4, natrium_mg=900, phosphor_mg=140, zink_mg=1.5), "Blutwurst", "Rotwurst")
ProductComposition.put(ProductComposition._meat(290, 24, 13, natrium=850, eisen=1.2, zink=2, vitamin_b12=1), "Leberkäse", "Fleischkäse")
ProductComposition.put(ProductComposition._meat(380, 32, 24, natrium=1700, eisen=2, zink=3.5, vitamin_b12=1.6), "Rindersalami")
ProductComposition.put(ProductComposition._meat(280, 20, 20, natrium=1400, eisen=0.8, zink=1.5, vitamin_b12=0.4), "Geflügelsalami")
ProductComposition.put(ProductComposition._meat(410, 35, 22, natrium=1900, eisen=1.5, zink=3, vitamin_b12=1.5), "Pfeffersalami")
ProductComposition.put(ProductComposition._meat(270, 23, 11, natrium=700, eisen=0.8, zink=1.4, vitamin_b12=0.8), "Weißwurst")
ProductComposition.put(ProductComposition._meat(280, 25, 12, natrium=900, eisen=1, zink=1.5, vitamin_b12=0.8), "Bockwurst", "Frankfurter Würstchen", "Knackwurst")
ProductComposition.put(ProductComposition._meat(300, 26, 14, natrium=1000, eisen=1.2, zink=2, vitamin_b12=1), "Krakauer", "Debreziner", "Käsekrainer")
ProductComposition.put(ProductComposition._meat(450, 40, 24, natrium=1600, eisen=1.5, zink=2.5, vitamin_b12=1), "Cabanossi", "Landjäger")
ProductComposition.put(ProductComposition._meat(300, 26, 13, natrium=900, eisen=1, zink=1.8, vitamin_b12=1), "Lyoner", "Jagdwurst", "Gelbwurst", "Schinkenwurst", "Bierwurst")
ProductComposition.put(ProductComposition._meat(220, 14, 16, natrium=900, eisen=0.8, zink=1.5, vitamin_b12=0.6), "Bierschinken")
ProductComposition.put(ProductComposition._meat(420, 36, 22, natrium=1600, eisen=1.6, zink=2.5, vitamin_b12=1.2), "Chorizo", "Sucuk", "Merguez")
ProductComposition.put(ProductComposition._meat(300, 26, 14, natrium=800, eisen=1, zink=2, vitamin_b12=1), "Nürnberger Rostbratwurst", "Thüringer Rostbratwurst")
ProductComposition.put(ProductComposition._meat(250, 18, 16, natrium=750, eisen=2, zink=3, vitamin_b12=1.8), "Rinderbratwurst")
ProductComposition.put(ProductComposition._meat(190, 11, 17, natrium=700, eisen=0.6, zink=1, vitamin_b12=0.3), "Geflügelbratwurst")
ProductComposition.put(ProductComposition._fish(208, 13, 20, vitamin_d=11, vitamin_b12=3.2, jod=30), "Lachsfilet")
ProductComposition.put(ProductComposition._fish(182, 10, 23, natrium=1200, vitamin_d=8, vitamin_b12=3), "Räucherlachs")
ProductComposition.put(ProductComposition._fish(82, 0.8, 18, vitamin_d=1, vitamin_b12=3.5, jod=120), "Seelachsfilet")
ProductComposition.put(ProductComposition._fish(141, 6, 20, vitamin_d=8, vitamin_b12=4, jod=10), "Forelle")
ProductComposition.put(ProductComposition.panel(200, 9, 1, 12, vitamin_d_ug=1, natrium_mg=400, kalium_mg=200, phosphor_mg=150, jod_ug=30, eisen_mg=0.5), "Fischstäbchen")
ProductComposition.put(ProductComposition._fish(85, 0.5, 18, vitamin_d=0.1, vitamin_b12=1.2, jod=35, calcium=60), "Garnelen")
ProductComposition.put(ProductComposition._fish(86, 2.2, 12, vitamin_d=0.1, vitamin_b12=12, jod=140, calcium=30, eisen=4), "Miesmuscheln")
ProductComposition.put(ProductComposition._fish(190, 8, 26, natrium=300, vitamin_d=3, vitamin_b12=2.5, jod=20), "Thunfisch in Öl")
ProductComposition.put(ProductComposition._fish(105, 1, 24, natrium=300, vitamin_d=2, vitamin_b12=3, jod=20), "Thunfisch im eigenen Saft")
ProductComposition.put(ProductComposition._fish(208, 11, 25, natrium=400, vitamin_d=5, vitamin_b12=9, jod=30, calcium=380, eisen=2.9), "Sardinen")
ProductComposition.put(ProductComposition._fish(131, 2.7, 20, natrium=3600, vitamin_d=2, vitamin_b12=0.9, jod=20, calcium=230), "Sardellen")
ProductComposition.put(ProductComposition._fish(220, 15, 16, natrium=1500, vitamin_d=5, vitamin_b12=8, jod=40), "Matjes")

ProductComposition.put(WHEAT_PASTA, "Spaghetti", "Spaghettini", "Bandnudeln", "Tagliatelle", "Fettuccine", "Linguine", "Bucatini", "Rigatoni", "Penne", "Penne rigate", "Fusilli", "Spiralen", "Farfalle", "Makkaroni", "Hörnchennudeln", "Cannelloni", "Lasagneplatten", "Suppennudeln")
ProductComposition.put(ProductComposition._pasta(kcal=370, fat=3.5, sugar=2, protein=13), "Eiernudeln")
ProductComposition.put(ProductComposition._pasta(kcal=330, fat=2.5, sugar=2, protein=14, eisen=3, magnesium=90), "Vollkornspaghetti")
ProductComposition.put(ProductComposition._pasta(kcal=280, fat=6, sugar=2, protein=11, natrium=400), "Tortellini", "Ravioli")
ProductComposition.put(ProductComposition.panel(150, 0.5, 1, 3.5, kalium_mg=250, vitamin_c_mg=6, phosphor_mg=50, magnesium_mg=15), "Gnocchi", "Schupfnudeln")
ProductComposition.put(ProductComposition.panel(180, 2, 1, 6, natrium_mg=300, kalium_mg=80, eisen_mg=0.8), "Spätzle")
ProductComposition.put(ProductComposition.panel(200, 8, 1.5, 8, natrium_mg=500, eisen_mg=1.2, kalium_mg=150), "Maultaschen")
ProductComposition.put(ProductComposition._pasta(kcal=360, fat=0.6, sugar=0.5, protein=6, eisen=0.5, magnesium=15), "Reisnudeln", "Udon")
ProductComposition.put(ProductComposition.panel(350, 0.1, 0, 0.2), "Glasnudeln")
ProductComposition.put(ProductComposition._pasta(kcal=360, fat=1.5, sugar=2, protein=8, natrium=400), "Mie-Nudeln")
ProductComposition.put(ProductComposition._pasta(kcal=340, fat=1, sugar=1, protein=14, eisen=2.5, magnesium=80), "Soba")
ProductComposition.put(WHITE_RICE, "Langkornreis", "Rundkornreis", "Basmatireis", "Jasminreis", "Milchreis", "Risottoreis")
ProductComposition.put(ProductComposition._rice(protein=7.5, fat=2.5, eisen=1.5, magnesium=140), "Vollkornreis")
ProductComposition.put(ProductComposition._rice(protein=15, fat=1, eisen=1.5, magnesium=170), "Wildreis")
ProductComposition.put(ProductComposition._pasta(), "Couscous")
ProductComposition.put(ProductComposition._pasta(kcal=340, fat=1.5, sugar=0.5, protein=12, eisen=2.5, magnesium=160), "Bulgur")
ProductComposition.put(ProductComposition.panel(368, 6, 2, 14, magnesium_mg=197, eisen_mg=4.6, phosphor_mg=457, kalium_mg=563, zink_mg=3.1, folat_ug=184, vitamin_b1_mg=0.36), "Quinoa")
ProductComposition.put(ProductComposition._pasta(kcal=360, fat=1.2, sugar=1, protein=8, eisen=1, magnesium=40), "Polenta")
ProductComposition.put(ProductComposition.panel(370, 7, 1, 13.5, vitamin_b1_mg=0.5, magnesium_mg=130, eisen_mg=4.3, phosphor_mg=430, kalium_mg=360, zink_mg=3, folat_ug=50), "Haferflocken")
ProductComposition.put(ProductComposition.panel(360, 6, 18, 9, magnesium_mg=60, eisen_mg=3, natrium_mg=80, kalium_mg=300, zink_mg=1.5), "Müsli")
ProductComposition.put(ProductComposition.panel(370, 0.8, 8, 7, natrium_mg=700, eisen_mg=8, vitamin_b1_mg=0.9, vitamin_b2_mg=1, vitamin_b3_mg=12, folat_ug=120, calcium_mg=15), "Cornflakes")
ProductComposition.put(ProductComposition.panel(420, 12, 30, 6, natrium_mg=150, eisen_mg=2, magnesium_mg=40, kalium_mg=180), "Müsliriegel")

ProductComposition.put(ProductComposition.panel(480, 24, 50, 6, natrium_mg=150, calcium_mg=80, kalium_mg=200, eisen_mg=1), "Schokoriegel")
ProductComposition.put(ProductComposition.panel(500, 26, 42, 6, natrium_mg=200, calcium_mg=70, eisen_mg=1.5), "Schokokeksriegel")
ProductComposition.put(ProductComposition.panel(620, 50, 8, 25, vitamin_e_mg=8, magnesium_mg=160, phosphor_mg=350, kalium_mg=600, zink_mg=2.5, eisen_mg=2, natrium_mg=20), "Erdnussbutter")
ProductComposition.put(ProductComposition.panel(540, 31, 56, 6, calcium_mg=100, natrium_mg=40, eisen_mg=2, magnesium_mg=60), "Nuss-Nougat-Creme")
ProductComposition.put(ProductComposition.panel(250, 0.1, 60, 0.4, vitamin_c_mg=5, kalium_mg=70), "Erdbeerkonfitüre")
ProductComposition.put(ProductComposition.panel(250, 0.1, 60, 0.4, vitamin_a_ug=30, kalium_mg=80), "Aprikosenkonfitüre")
ProductComposition.put(ProductComposition.panel(304, 0, 82, 0.3, kalium_mg=50), "Honig")
ProductComposition.put(ProductComposition.panel(535, 30, 52, 7, calcium_mg=190, phosphor_mg=200, kalium_mg=400, magnesium_mg=60, natrium_mg=80), "Vollmilchschokolade")
ProductComposition.put(ProductComposition.panel(530, 35, 40, 6, magnesium_mg=140, eisen_mg=3, kalium_mg=500, phosphor_mg=200, zink_mg=2), "Zartbitterschokolade")
ProductComposition.put(ProductComposition.panel(539, 32, 59, 6, calcium_mg=200, phosphor_mg=180, natrium_mg=90), "Weiße Schokolade")
ProductComposition.put(ProductComposition.panel(340, 0.1, 70, 5, natrium_mg=40), "Fruchtgummi")
ProductComposition.put(ProductComposition.panel(350, 1, 50, 4, natrium_mg=200, kalium_mg=150, eisen_mg=2), "Lakritz")
ProductComposition.put(ProductComposition.panel(530, 33, 0.5, 6, natrium_mg=600, kalium_mg=1200, magnesium_mg=40), "Kartoffelchips")
ProductComposition.put(ProductComposition.panel(520, 32, 3, 6, natrium_mg=700, kalium_mg=1000, vitamin_a_ug=40), "Paprikachips")
ProductComposition.put(ProductComposition.panel(567, 49, 4, 26, vitamin_e_mg=8, magnesium_mg=168, phosphor_mg=376, kalium_mg=705, zink_mg=3.3, eisen_mg=4.6, folat_ug=240), "Erdnüsse")
ProductComposition.put(ProductComposition.panel(553, 44, 6, 18, magnesium_mg=292, eisen_mg=6.7, phosphor_mg=593, kalium_mg=660, zink_mg=5.8, vitamin_k_ug=34), "Cashewkerne")
ProductComposition.put(ProductComposition.panel(579, 50, 4, 21, vitamin_e_mg=25, calcium_mg=269, magnesium_mg=270, phosphor_mg=481, kalium_mg=730, eisen_mg=3.7, zink_mg=3.1), "Mandeln")
ProductComposition.put(ProductComposition.panel(654, 65, 2.6, 15, vitamin_e_mg=0.7, magnesium_mg=158, phosphor_mg=346, kalium_mg=441, eisen_mg=2.9, zink_mg=3.1, folat_ug=98), "Walnüsse")
ProductComposition.put(ProductComposition.panel(390, 4, 2, 10, natrium_mg=1500, eisen_mg=1.5, kalium_mg=120), "Salzstangen", "Brezeln")

ProductComposition.put(ProductComposition.panel(177, 9.6, 0.3, 8, eisen_mg=2.4, magnesium_mg=40, kalium_mg=230, folat_ug=80, natrium_mg=380), "Hummus")
ProductComposition.put(ProductComposition.panel(145, 15, 0, 1, natrium_mg=1550, vitamin_e_mg=3, eisen_mg=0.5, calcium_mg=50), "Oliven grün", "Oliven gefüllt")
ProductComposition.put(ProductComposition.panel(165, 16, 0, 0.8, natrium_mg=1200, vitamin_e_mg=2, eisen_mg=3), "Oliven schwarz")
ProductComposition.put(ProductComposition.panel(230, 22, 0, 1.5, natrium_mg=800, vitamin_e_mg=4, eisen_mg=1), "Kalamata-Oliven")
ProductComposition.put(ProductComposition.panel(90, 6, 3, 1.5, natrium_mg=600, vitamin_c_mg=10, kalium_mg=200), "Antipasti")
ProductComposition.put(ProductComposition.panel(213, 14, 38, 5, natrium_mg=800, kalium_mg=1500, vitamin_c_mg=40, eisen_mg=2.5), "Getrocknete Tomaten")
ProductComposition.put(ProductComposition.panel(50, 0.3, 1, 2.5, natrium_mg=400, folat_ug=70, kalium_mg=300, magnesium_mg=40), "Artischockenherzen")
ProductComposition.put(ProductComposition.panel(40, 0.5, 4, 1, natrium_mg=800, vitamin_c_mg=20), "Peperoni eingelegt")
ProductComposition.put(ProductComposition.panel(23, 0.9, 0.4, 2.4, natrium_mg=2300, eisen_mg=1.5, kalium_mg=40), "Kapern")
ProductComposition.put(ProductComposition.panel(450, 45, 3, 5, natrium_mg=600, vitamin_k_ug=100, vitamin_e_mg=3, calcium_mg=150, eisen_mg=1), "Pesto verde")
ProductComposition.put(ProductComposition.panel(380, 35, 6, 4, natrium_mg=700, vitamin_a_ug=40, vitamin_e_mg=3, kalium_mg=200), "Pesto rosso")
ProductComposition.put(ProductComposition.panel(90, 5, 6, 1.5, natrium_mg=500, vitamin_c_mg=15, vitamin_a_ug=40), "Ajvar")
ProductComposition.put(ProductComposition.panel(140, 12, 3, 2, natrium_mg=400, kalium_mg=250), "Baba Ganoush", "Auberginenmus")
ProductComposition.put(ProductComposition.panel(110, 8, 3, 4, natrium_mg=400, calcium_mg=80, vitamin_b2_mg=0.1), "Tzatziki")
ProductComposition.put(ProductComposition.panel(230, 20, 0.5, 2, natrium_mg=1200, eisen_mg=2), "Tapenade")
ProductComposition.put(ProductComposition.panel(250, 13, 2, 8, eisen_mg=2, magnesium_mg=40, natrium_mg=400, kalium_mg=250, folat_ug=70), "Falafel")
ProductComposition.put(ProductComposition.panel(300, 26, 0.5, 12, natrium_mg=1000, calcium_mg=300, vitamin_e_mg=2), "Feta in Öl")
ProductComposition.put(ProductComposition.panel(12, 0.2, 2, 0.5, natrium_mg=800, vitamin_k_ug=10), "Essiggurken")
ProductComposition.put(ProductComposition.panel(20, 0.2, 3, 0.6, natrium_mg=900), "Cornichons")
ProductComposition.put(ProductComposition.panel(30, 0.1, 5, 0.8, natrium_mg=500), "Silberzwiebeln")
ProductComposition.put(ProductComposition.panel(19, 0.1, 0.4, 1.1, natrium_mg=660, vitamin_c_mg=15, vitamin_k_ug=20, kalium_mg=170), "Sauerkraut")
ProductComposition.put(ProductComposition.panel(50, 0.2, 8, 1, natrium_mg=400, vitamin_c_mg=20), "Rotkohl im Glas")
ProductComposition.put(ProductComposition.panel(140, 8, 2, 2, natrium_mg=500, kalium_mg=250, vitamin_c_mg=6), "Kartoffelsalat")
ProductComposition.put(ProductComposition.panel(180, 9, 3, 4, natrium_mg=500, eisen_mg=0.8), "Nudelsalat")
ProductComposition.put(ProductComposition.panel(250, 22, 3, 7, natrium_mg=700, vitamin_b12_ug=0.5), "Fleischsalat")
ProductComposition.put(ProductComposition.panel(200, 16, 2, 8, natrium_mg=600), "Geflügelsalat")
ProductComposition.put(ProductComposition.panel(180, 14, 2, 8, natrium_mg=800), "Wurstsalat")
ProductComposition.put(ProductComposition.panel(180, 12, 4, 8, natrium_mg=700, vitamin_d_ug=2, vitamin_b12_ug=3, jod_ug=20), "Heringssalat")
ProductComposition.put(ProductComposition.panel(220, 18, 2, 8, natrium_mg=500, vitamin_a_ug=80, vitamin_b12_ug=0.8, vitamin_d_ug=0.8), "Eiersalat")

ProductComposition.put(ProductComposition.panel(70, 0.4, 4, 5, natrium_mg=250, vitamin_c_mg=10, kalium_mg=170, eisen_mg=1.2, folat_ug=40), "Erbsen", "Tiefkühlerbsen")
ProductComposition.put(ProductComposition.panel(127, 0.5, 0.3, 8.7, natrium_mg=230, eisen_mg=2.1, kalium_mg=270, magnesium_mg=35, folat_ug=40, phosphor_mg=130), "Kidneybohnen")
ProductComposition.put(ProductComposition.panel(110, 0.5, 0.5, 7, natrium_mg=250, eisen_mg=2, kalium_mg=300, magnesium_mg=40, folat_ug=50), "Weiße Bohnen")
ProductComposition.put(ProductComposition.panel(139, 2.4, 1, 7, natrium_mg=240, eisen_mg=1.9, kalium_mg=170, magnesium_mg=35, folat_ug=60, phosphor_mg=100), "Kichererbsen")
ProductComposition.put(ProductComposition.panel(353, 1.1, 2, 26, eisen_mg=6.5, magnesium_mg=80, kalium_mg=670, phosphor_mg=280, zink_mg=3.3, folat_ug=180, vitamin_b1_mg=0.4), "Linsen", "Rote Linsen")
ProductComposition.put(ProductComposition.panel(32, 0.2, 4, 1.6, natrium_mg=150, vitamin_c_mg=10, vitamin_a_ug=40, kalium_mg=250), "Passierte Tomaten", "Stückige Tomaten")
ProductComposition.put(ProductComposition.panel(80, 1.2, 5, 2.5, natrium_mg=200, magnesium_mg=25, kalium_mg=180, phosphor_mg=70), "Mais")
ProductComposition.put(ProductComposition.panel(185, 18, 2, 1.8, "100 ml", magnesium_mg=25, kalium_mg=220, eisen_mg=1.6, phosphor_mg=80), "Kokosmilch")

ProductComposition.put(WATER, "Mineralwasser", "Sprudel")
ProductComposition.put(ProductComposition.panel(0, 0, 0, 0, "100 ml", calcium_mg=8, magnesium_mg=2, natrium_mg=3), "Stilles Wasser")
ProductComposition.put(ProductComposition.panel(42, 0, 10.6, 0, "100 ml", natrium_mg=4), "Cola")
ProductComposition.put(ProductComposition.panel(40, 0, 9.5, 0, "100 ml", natrium_mg=5), "Orangenlimonade")
ProductComposition.put(ProductComposition.panel(38, 0, 9, 0, "100 ml", natrium_mg=5), "Zitronenlimonade")
ProductComposition.put(ProductComposition.panel(46, 0.1, 10, 0.1, "100 ml", vitamin_c_mg=2, kalium_mg=120), "Apfelsaft")
ProductComposition.put(ProductComposition.panel(45, 0.2, 9, 0.7, "100 ml", vitamin_c_mg=40, kalium_mg=180, folat_ug=25), "Orangensaft")
ProductComposition.put(ProductComposition.panel(48, 0.1, 10, 0.3, "100 ml", vitamin_c_mg=30, vitamin_a_ug=40, vitamin_e_mg=0.5, vitamin_b6_mg=0.1, kalium_mg=80), "Multivitaminsaft")
ProductComposition.put(ProductComposition.panel(2, 0, 0, 0.1, "100 ml Aufguss", kalium_mg=50, magnesium_mg=4, natrium_mg=2), "Filterkaffee")
ProductComposition.put(ProductComposition.panel(290, 12, 0, 12, kalium_mg=2000, magnesium_mg=200, phosphor_mg=200, eisen_mg=4, natrium_mg=5), "Espressobohnen")
ProductComposition.put(TEA, "Schwarztee", "Grüntee", "Pfefferminztee", "Früchtetee", "Kamillentee")

ProductComposition.put(ProductComposition.panel(250, 10, 3.5, 10, natrium_mg=600, calcium_mg=80, eisen_mg=1, kalium_mg=180), "Tiefkühlpizza")
ProductComposition.put(ProductComposition.panel(150, 5, 0.3, 2.5, natrium_mg=200, kalium_mg=400, vitamin_c_mg=8), "Pommes frites")
ProductComposition.put(ProductComposition.panel(80, 4.5, 1.5, 3, natrium_mg=300, vitamin_a_ug=200, vitamin_k_ug=200, kalium_mg=300, eisen_mg=1.5), "Rahmspinat")
ProductComposition.put(ProductComposition._fruit(40, 6, protein=0.7, vitamin_c=20, kalium=120), "Tiefkühlbeeren")
ProductComposition.put(ProductComposition.panel(207, 11, 21, 3.5, calcium_mg=120, vitamin_a_ug=80, vitamin_b2_mg=0.2, phosphor_mg=100, natrium_mg=60), "Vanilleeis")
ProductComposition.put(ProductComposition.panel(216, 11, 23, 3.8, calcium_mg=110, eisen_mg=0.8, magnesium_mg=25, natrium_mg=60), "Schokoladeneis")
ProductComposition.put(ProductComposition.panel(180, 8, 22, 2, vitamin_c_mg=4, calcium_mg=80, natrium_mg=40), "Zitroneneis")

ProductComposition.put(ProductComposition._oil(14), "Olivenöl")
ProductComposition.put(ProductComposition._oil(22, 70), "Rapsöl")
ProductComposition.put(ProductComposition._oil(41, 5), "Sonnenblumenöl")
ProductComposition.put(ProductComposition._oil(1.4, 14), "Sesamöl")
ProductComposition.put(ProductComposition.panel(88, 0, 15, 0.5, kalium_mg=90, calcium_mg=15, natrium_mg=20), "Balsamico")
ProductComposition.put(ProductComposition.panel(19, 0, 0.4, 0, natrium_mg=5, kalium_mg=20), "Branntweinessig", "Apfelessig")
ProductComposition.put(ProductComposition.panel(112, 0.3, 23, 1.5, natrium_mg=900, kalium_mg=300, vitamin_a_ug=40, vitamin_c_mg=4), "Ketchup")
ProductComposition.put(ProductComposition.panel(680, 75, 1.5, 1, natrium_mg=600, vitamin_e_mg=5, vitamin_k_ug=80), "Mayonnaise")
ProductComposition.put(ProductComposition.panel(66, 4, 3, 4.4, natrium_mg=1100, kalium_mg=140, calcium_mg=60, eisen_mg=1.5), "Senf mittelscharf")
ProductComposition.put(ProductComposition.panel(70, 4, 2, 5, natrium_mg=1200, kalium_mg=140, calcium_mg=60, eisen_mg=2), "Senf scharf")
ProductComposition.put(ProductComposition.panel(53, 0, 0.4, 8, natrium_mg=5500, kalium_mg=180, eisen_mg=2), "Sojasauce")
ProductComposition.put(ProductComposition.panel(78, 0, 15, 1, natrium_mg=980, kalium_mg=80), "Worcestersauce")
ProductComposition.put(ProductComposition.panel(82, 0.5, 12, 4.3, natrium_mg=50, kalium_mg=1000, vitamin_c_mg=20, vitamin_a_ug=80, eisen_mg=2), "Tomatenmark")
ProductComposition.put(ProductComposition.panel(348, 1, 0.3, 10, eisen_mg=1, magnesium_mg=20, phosphor_mg=100, kalium_mg=110, vitamin_b1_mg=0.1), "Weizenmehl Type 405", "Weizenmehl Type 550")
ProductComposition.put(ProductComposition.panel(325, 1.5, 1, 9, eisen_mg=2.5, magnesium_mg=70, phosphor_mg=200, kalium_mg=180, vitamin_b1_mg=0.2), "Roggenmehl")
ProductComposition.put(ProductComposition.panel(400, 0, 100, 0), "Zucker", "Puderzucker", "Rohrzucker", "Vanillinzucker")
ProductComposition.put(ProductComposition.panel(53, 0, 0, 0, natrium_mg=8200, phosphor_mg=500, calcium_mg=50), "Backpulver")
ProductComposition.put(ProductComposition.panel(105, 1.5, 0, 12, vitamin_b1_mg=0.7, vitamin_b2_mg=1.5, vitamin_b3_mg=11, vitamin_b6_mg=0.4, folat_ug=700, kalium_mg=600, phosphor_mg=400, eisen_mg=2, zink_mg=2, magnesium_mg=40), "Hefe")
ProductComposition.put(ProductComposition.panel(155, 11, 0.4, 13, vitamin_a_ug=160, vitamin_d_ug=1.8, vitamin_b2_mg=0.4, vitamin_b12_ug=1.3, folat_ug=47, phosphor_mg=200, eisen_mg=1.8, zink_mg=1.3, natrium_mg=140, kalium_mg=140, calcium_mg=50, jod_ug=10), "Eier Größe M", "Eier Größe L")
ProductComposition.put(ProductComposition.panel(395, 5, 4, 13, natrium_mg=700, eisen_mg=2, kalium_mg=150), "Paniermehl")
ProductComposition.put(ProductComposition.panel(348, 0.1, 0, 0.2), "Speisestärke")
ProductComposition.put(TABLE_SALT, "Speisesalz", "Meersalz")
ProductComposition.put(ProductComposition._salt(natrium=39300, jod=2000), "Jodsalz")
ProductComposition.put(ProductComposition._salt(natrium=28000, jod=0), "Kräutersalz")
ProductComposition.put(ProductComposition._salt(natrium=30000, jod=0), "Knoblauchsalz")
ProductComposition.put(ProductComposition._spice(kcal=255, fat=3.3, sugar=0.6, protein=10, eisen=10, calcium=440, kalium=1320, magnesium=170), "Schwarzer Pfeffer gemahlen", "Schwarzer Pfeffer ganz", "Weißer Pfeffer", "Grüner Pfeffer", "Bunter Pfeffer")
ProductComposition.put(ProductComposition._spice(kcal=318, fat=17, sugar=10, protein=12, eisen=8, calcium=150, kalium=2000, vitamin_a=2000), "Cayennepfeffer", "Chilipulver", "Chiliflocken")
ProductComposition.put(ProductComposition._spice(kcal=280, fat=6, sugar=6, protein=12, eisen=8, calcium=150, kalium=1800, vitamin_a=80), "Zitronenpfeffer")
ProductComposition.put(ProductComposition._spice(kcal=282, fat=13, sugar=10, protein=14, eisen=21, calcium=230, kalium=2280, magnesium=180, vitamin_a=2500), "Paprikapulver edelsüß", "Paprikapulver rosenscharf", "Paprikapulver scharf")
ProductComposition.put(ProductComposition._spice(kcal=325, fat=14, sugar=3, protein=14, eisen=30, calcium=520, kalium=1700, magnesium=250), "Currypulver")
ProductComposition.put(ProductComposition._spice(kcal=312, fat=3, sugar=3, protein=10, eisen=41, calcium=180, kalium=2500, magnesium=190, vitamin_a=0), "Kurkuma")
ProductComposition.put(ProductComposition._spice(kcal=375, fat=22, sugar=2, protein=18, eisen=66, calcium=930, kalium=1780, magnesium=366), "Kreuzkümmel")
ProductComposition.put(ProductComposition._spice(kcal=333, fat=15, sugar=2, protein=20, eisen=16, calcium=690, kalium=1350, magnesium=260), "Kümmel", "Koriander gemahlen", "Koriandersamen")
ProductComposition.put(ProductComposition._spice(kcal=247, fat=1.2, sugar=2, protein=4, eisen=8, calcium=1000, kalium=430, magnesium=60), "Zimt gemahlen", "Zimtstangen")
ProductComposition.put(DRIED_HERB, "Oregano", "Majoran", "Thymian getrocknet", "Rosmarin getrocknet", "Basilikum getrocknet", "Petersilie getrocknet", "Schnittlauch getrocknet", "Dillspitzen", "Lorbeerblätter", "Bohnenkraut", "Liebstöckel", "Salbei", "Estragon")
ProductComposition.put(ProductComposition._spice(kcal=525, fat=36, sugar=3, protein=6, eisen=3, calcium=180, kalium=350, magnesium=180), "Muskatnuss", "Muskat gemahlen")
ProductComposition.put(ProductComposition._spice(kcal=274, fat=13, sugar=2, protein=6, eisen=12, calcium=630, kalium=1000, magnesium=260), "Nelken")
ProductComposition.put(ProductComposition._spice(kcal=263, fat=9, sugar=2, protein=6, eisen=7, calcium=660, kalium=1000, magnesium=130), "Piment")
ProductComposition.put(ProductComposition._spice(kcal=347, fat=6, sugar=3, protein=9, eisen=20, calcium=110, kalium=1300, magnesium=210), "Ingwer gemahlen")
ProductComposition.put(ProductComposition._spice(kcal=330, fat=1, sugar=2, protein=16, eisen=5, calcium=80, kalium=1100, magnesium=60), "Knoblauchpulver", "Zwiebelpulver")
ProductComposition.put(ProductComposition._spice(kcal=337, fat=16, sugar=2, protein=18, eisen=37, calcium=650, kalium=1400, magnesium=170), "Anis", "Fenchelsamen")
ProductComposition.put(ProductComposition._spice(kcal=311, fat=7, sugar=2, protein=11, eisen=14, calcium=380, kalium=1100, magnesium=230), "Kardamom")
ProductComposition.put(ProductComposition._spice(kcal=337, fat=16, sugar=2, protein=18, eisen=37, calcium=650, kalium=1400, magnesium=170), "Sternanis")
ProductComposition.put(ProductComposition.panel(288, 0.1, 13, 0.1), "Vanilleschote")
ProductComposition.put(ProductComposition._spice(kcal=310, fat=6, sugar=6, protein=11, eisen=11, calcium=110, kalium=1700, magnesium=260), "Safran")
ProductComposition.put(ProductComposition._spice(kcal=300, fat=5, sugar=2, protein=4, eisen=3, calcium=300, kalium=600, magnesium=80), "Wacholderbeeren")
ProductComposition.put(ProductComposition._spice(kcal=508, fat=36, sugar=7, protein=26, eisen=9, calcium=270, kalium=740, magnesium=370), "Senfkörner")
ProductComposition.put(ProductComposition._spice(kcal=323, fat=6, sugar=2, protein=23, eisen=34, calcium=180, kalium=770, magnesium=190), "Bockshornklee")
ProductComposition.put(SEASONED_SPICE, "Garam Masala", "Ras el Hanout", "Za'atar", "Pizzagewürz", "Grillgewürz", "Hähnchengewürz")
ProductComposition.put(DRIED_HERB, "Italienische Kräuter", "Kräuter der Provence")
ProductComposition.put(BROTH, "Gemüsebrühe", "Hühnerbrühe", "Fleischbrühe")


ProductComposition._check()


