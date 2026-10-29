"""Beispielsortiment je Supermarkt, 1000 konkrete Produkte.

Summary:
    Jede Kette bekommt eigene Eigenmarken, Packungsgrößen und Beispielpreise.
    Die Produktart verweist auf PRODUCT_KINDS. Preise sind keine Filialpreise.
"""

from decimal import Decimal

from models.product_kinds import PRODUCT_KINDS

CATALOG_SIZE = 1000
NOTE = "Beispielsortiment mit Beispielpreis, kein tagesaktueller Filialpreis."
# Zweite Packung dieser Arten ist Bio, damit die CO2-Wahl ein Hofpaar sieht.
ORGANIC_EXAMPLE = ("Hähnchenbrust", "Hähnchenschenkel", "Schweineschnitzel", "Rindersteak", "Äpfel")

CATEGORIES = {
    "milch": frozenset(PRODUCT_KINDS[0:24]),
    "kaese": frozenset(PRODUCT_KINDS[24:64]),
    "brot": frozenset(PRODUCT_KINDS[64:103]),
    "obst": frozenset(PRODUCT_KINDS[103:140]),
    "gemuese": frozenset(PRODUCT_KINDS[140:209]),
    "fleisch": frozenset(PRODUCT_KINDS[209:263]),
    "fisch": frozenset(PRODUCT_KINDS[263:275]),
    "nudeln": frozenset(PRODUCT_KINDS[275:322]),
    "suess": frozenset(PRODUCT_KINDS[322:342]),
    "feinkost": frozenset(PRODUCT_KINDS[342:373]),
    "konserve": frozenset(PRODUCT_KINDS[373:383]),
    "getraenk": frozenset(PRODUCT_KINDS[383:399]),
    "tiefkuehl": frozenset(PRODUCT_KINDS[399:407]),
    "vorrat": frozenset(PRODUCT_KINDS[407:434]),
    "gewuerz": frozenset(PRODUCT_KINDS[434:499]),
}

CATEGORY_LABELS = {
    "milch": "Molkereiprodukte",
    "kaese": "Käse",
    "brot": "Brot und Backwaren",
    "obst": "Obst",
    "gemuese": "Gemüse",
    "fleisch": "Fleisch und Wurst",
    "fisch": "Fisch",
    "nudeln": "Nudeln und Getreide",
    "suess": "Süßwaren und Snacks",
    "feinkost": "Feinkost",
    "konserve": "Konserven",
    "getraenk": "Getränke",
    "tiefkuehl": "Tiefkühl",
    "vorrat": "Vorrat",
    "gewuerz": "Gewürze",
}

# Eigenmarken, die in der jeweiligen Kette geführt werden. Bio ist die Biomarke der Kette.
CHAINS = {
    "aldi": {
        "label": "Aldi",
        "factor": Decimal("0.90"),
        "bio": "Aldi Bio",
        "default": {
            "milch": "Milsani",
            "kaese": "Milsani",
            "brot": "Meine Bäckerei",
            "obst": "Aldi",
            "gemuese": "Aldi",
            "fleisch": "Meine Metzgerei",
            "fisch": "Golden Seafood",
            "nudeln": "Cucina",
            "suess": "King's Crown",
            "feinkost": "Cucina",
            "konserve": "Cucina",
            "getraenk": "River",
            "tiefkuehl": "Aldi",
            "vorrat": "Cucina",
            "gewuerz": "Le Gusto",
        },
    },
    "lidl": {
        "label": "Lidl",
        "factor": Decimal("0.93"),
        "bio": "Bio Organic",
        "default": {
            "milch": "Milbona",
            "kaese": "Milbona",
            "brot": "Goldähren",
            "obst": "Freshona",
            "gemuese": "Freshona",
            "fleisch": "Dulano",
            "fisch": "Nixe",
            "nudeln": "Combino",
            "suess": "Sondey",
            "feinkost": "Kania",
            "konserve": "Kania",
            "getraenk": "Freeway",
            "tiefkuehl": "Chef Select",
            "vorrat": "Kania",
            "gewuerz": "Kania",
        },
    },
    "rewe": {
        "label": "Rewe",
        "factor": Decimal("1.00"),
        "bio": "REWE Bio",
        "default": {
            "milch": "ja!",
            "kaese": "ja!",
            "brot": "ja!",
            "obst": "ja!",
            "gemuese": "ja!",
            "fleisch": "Wilhelm Brandenburg",
            "fisch": "ja!",
            "nudeln": "ja!",
            "suess": "ja!",
            "feinkost": "ja!",
            "konserve": "ja!",
            "getraenk": "ja!",
            "tiefkuehl": "ja!",
            "vorrat": "ja!",
            "gewuerz": "ja!",
        },
    },
    "netto": {
        "label": "Netto",
        "factor": Decimal("0.95"),
        "bio": "BioBio",
        "default": {
            "milch": "Mibell",
            "kaese": "Mibell",
            "brot": "A&P",
            "obst": "A&P",
            "gemuese": "A&P",
            "fleisch": "Landjunker",
            "fisch": "A&P",
            "nudeln": "Oro di Parma",
            "suess": "A&P",
            "feinkost": "Oro di Parma",
            "konserve": "Oro di Parma",
            "getraenk": "A&P",
            "tiefkuehl": "A&P",
            "vorrat": "A&P",
            "gewuerz": "A&P",
        },
    },
    "penny": {
        "label": "Penny",
        "factor": Decimal("0.97"),
        "bio": "ich bin bio",
        "default": {
            "milch": "Penny",
            "kaese": "Penny",
            "brot": "Penny",
            "obst": "Penny",
            "gemuese": "Penny",
            "fleisch": "Grillmeister",
            "fisch": "Penny",
            "nudeln": "San Fabio",
            "suess": "Penny",
            "feinkost": "San Fabio",
            "konserve": "San Fabio",
            "getraenk": "Penny",
            "tiefkuehl": "Penny",
            "vorrat": "Penny",
            "gewuerz": "Penny",
        },
    },
}

PACKS = {
    "milch": ((Decimal("1"), "l", "Getränkekarton", Decimal("1.19")), (Decimal("0.5"), "l", "Getränkekarton", Decimal("0.79"))),
    "kaese": ((Decimal("200"), "g", "Folie", Decimal("2.49")), (Decimal("400"), "g", "Folie", Decimal("4.29"))),
    "brot": ((Decimal("500"), "g", "Beutel", Decimal("1.69")), (Decimal("1000"), "g", "Beutel", Decimal("2.79"))),
    "obst": ((Decimal("1"), "kg", "lose", Decimal("1.99")), (Decimal("500"), "g", "Schale", Decimal("1.49"))),
    "gemuese": ((Decimal("1"), "kg", "lose", Decimal("1.49")), (Decimal("500"), "g", "Beutel", Decimal("1.19"))),
    "fleisch": ((Decimal("400"), "g", "Schale", Decimal("3.99")), (Decimal("250"), "g", "Schale", Decimal("2.69"))),
    "fisch": ((Decimal("300"), "g", "Schale", Decimal("4.49")), (Decimal("150"), "g", "Schale", Decimal("2.79"))),
    "nudeln": ((Decimal("500"), "g", "Beutel", Decimal("1.29")), (Decimal("1000"), "g", "Beutel", Decimal("1.99"))),
    "suess": ((Decimal("100"), "g", "Tüte", Decimal("1.49")), (Decimal("250"), "g", "Tüte", Decimal("2.29"))),
    "feinkost": ((Decimal("200"), "g", "Glas", Decimal("1.99")), (Decimal("400"), "g", "Becher", Decimal("2.79"))),
    "konserve": ((Decimal("400"), "g", "Dose", Decimal("0.99")), (Decimal("800"), "g", "Glas", Decimal("1.59"))),
    "getraenk": ((Decimal("1.5"), "l", "Flasche", Decimal("0.99")), (Decimal("0.5"), "l", "Flasche", Decimal("0.69"))),
    "tiefkuehl": ((Decimal("500"), "g", "Beutel", Decimal("1.99")), (Decimal("1000"), "g", "Beutel", Decimal("2.99"))),
    "vorrat": ((Decimal("500"), "g", "Tüte", Decimal("0.99")), (Decimal("1000"), "g", "Tüte", Decimal("1.49"))),
    "gewuerz": ((Decimal("40"), "g", "Tüte", Decimal("1.19")), (Decimal("15"), "g", "Glas", Decimal("1.79"))),
}

WATER = {"Mineralwasser", "Sprudel", "Stilles Wasser"}
SODA = {"Cola", "Orangenlimonade", "Zitronenlimonade"}
JUICE = {"Apfelsaft", "Orangensaft", "Multivitaminsaft"}
COFFEE = {"Filterkaffee", "Espressobohnen"}
TEA = {"Schwarztee", "Grüntee", "Pfefferminztee", "Früchtetee", "Kamillentee"}
CANNED_FISH = {"Thunfisch in Öl", "Thunfisch im eigenen Saft", "Sardinen", "Sardellen"}
CEREAL = {"Haferflocken", "Müsli", "Cornflakes", "Müsliriegel"}
CHOCOLATE = {"Vollmilchschokolade", "Zartbitterschokolade", "Weiße Schokolade", "Nuss-Nougat-Creme"}
OILS = {"Olivenöl", "Rapsöl", "Sonnenblumenöl", "Sesamöl"}
VINEGAR = {"Balsamico", "Branntweinessig", "Apfelessig"}
EGGS = {"Eier Größe M", "Eier Größe L"}
ICE = {"Vanilleeis", "Schokoladeneis", "Zitroneneis"}

DRINK_BRANDS = {
    "aldi": {"water": "Quellbrunn", "soda": "River", "juice": "Rio d'Oro", "coffee": "Amaroy", "tea": "Westcliff"},
    "lidl": {"water": "Saskia", "soda": "Freeway", "juice": "Solevita", "coffee": "Bellarom", "tea": "Lord Nelson"},
    "rewe": {"water": "ja!", "soda": "ja!", "juice": "ja!", "coffee": "ja!", "tea": "ja!"},
    "netto": {"water": "A&P", "soda": "A&P", "juice": "A&P", "coffee": "A&P", "tea": "A&P"},
    "penny": {"water": "Penny", "soda": "Penny", "juice": "Penny", "coffee": "Penny", "tea": "Penny"},
}


class SupermarketCatalog:
    """Erzeugt das konkrete Sortiment einer Supermarktkette.

    Summary:
        Produktart, Packung und Marke folgen festen Regeln.
        Zusatzstoffe und Diät-Kennzeichen hängen an der Produktart.
    """

    @staticmethod
    def _check_categories() -> None:
        covered = set()
        for names in CATEGORIES.values():
            overlap = covered & names
            if overlap:
                raise RuntimeError(f"Kategorie doppelt: {sorted(overlap)[:5]}")
            covered |= names
        missing = [name for name in PRODUCT_KINDS if name not in covered]
        if missing or len(covered) != len(PRODUCT_KINDS):
            raise RuntimeError(f"Kategorien unvollständig: {missing[:8]}")

    @staticmethod
    def category_of(kind: str) -> str:
        for key, names in CATEGORIES.items():
            if kind in names:
                return key
        raise KeyError(kind)

    @staticmethod
    def packs_for(kind: str, category: str):
        if category == "getraenk":
            if kind in WATER:
                return ((Decimal("1.5"), "l", "Flasche", Decimal("0.37")), (Decimal("0.5"), "l", "Flasche", Decimal("0.29")))
            if kind in SODA:
                return PACKS["getraenk"]
            if kind in JUICE:
                return ((Decimal("1"), "l", "Flasche", Decimal("1.29")), (Decimal("0.5"), "l", "Flasche", Decimal("0.89")))
            if kind in COFFEE:
                return ((Decimal("500"), "g", "Beutel", Decimal("5.99")), (Decimal("250"), "g", "Beutel", Decimal("3.49")))
            if kind in TEA:
                return ((Decimal("25"), "Beutel", "Schachtel", Decimal("1.69")), (Decimal("20"), "Beutel", "Schachtel", Decimal("1.29")))
        if category == "fisch" and kind in CANNED_FISH:
            return ((Decimal("185"), "g", "Dose", Decimal("1.79")), (Decimal("120"), "g", "Dose", Decimal("1.29")))
        if kind == "Fischstäbchen":
            return ((Decimal("15"), "Stück", "Schachtel", Decimal("2.49")), (Decimal("30"), "Stück", "Schachtel", Decimal("4.29")))
        if category == "vorrat":
            if kind in OILS:
                return ((Decimal("750"), "ml", "Flasche", Decimal("4.99")), (Decimal("500"), "ml", "Flasche", Decimal("3.49")))
            if kind in VINEGAR:
                return ((Decimal("500"), "ml", "Flasche", Decimal("1.29")), (Decimal("250"), "ml", "Flasche", Decimal("0.89")))
            if kind in EGGS:
                return ((Decimal("10"), "Stück", "Schachtel", Decimal("2.29")), (Decimal("6"), "Stück", "Schachtel", Decimal("1.49")))
            if kind in {"Ketchup", "Mayonnaise", "Senf mittelscharf", "Senf scharf", "Sojasauce", "Worcestersauce"}:
                return ((Decimal("500"), "ml", "Flasche", Decimal("1.49")), (Decimal("250"), "ml", "Flasche", Decimal("0.99")))
            if kind == "Tomatenmark":
                return ((Decimal("200"), "g", "Tube", Decimal("0.89")), (Decimal("70"), "g", "Tube", Decimal("0.49")))
            if kind in {"Backpulver", "Hefe"}:
                return ((Decimal("6"), "Stück", "Tüte", Decimal("0.69")), (Decimal("3"), "Stück", "Tüte", Decimal("0.39")))
        if category == "tiefkuehl" and kind in ICE:
            return ((Decimal("500"), "ml", "Becher", Decimal("2.49")), (Decimal("250"), "ml", "Becher", Decimal("1.49")))
        if kind == "Tiefkühlpizza":
            return ((Decimal("400"), "g", "Schachtel", Decimal("2.79")), (Decimal("3"), "Stück", "Schachtel", Decimal("5.99")))
        return PACKS[category]

    @staticmethod
    def brand_for(chain: str, kind: str, category: str, organic: bool) -> str:
        info = CHAINS[chain]
        if organic:
            return info["bio"]
        if category == "getraenk":
            drinks = DRINK_BRANDS[chain]
            if kind in WATER:
                return drinks["water"]
            if kind in SODA:
                return drinks["soda"]
            if kind in JUICE:
                return drinks["juice"]
            if kind in COFFEE:
                return drinks["coffee"]
            if kind in TEA:
                return drinks["tea"]
        if chain == "aldi" and kind in CEREAL:
            return "Sweet Valley"
        if chain == "aldi" and kind in CHOCOLATE:
            return "Moser Roth"
        if chain == "lidl" and kind in CEREAL:
            return "Crownfield"
        if chain == "lidl" and kind in CHOCOLATE:
            return "Fin Carré"
        if chain == "lidl" and category == "feinkost" and kind.endswith("salat"):
            return "Chef Select"
        return info["default"][category]

    @staticmethod
    def _format_quantity(quantity: Decimal) -> str:
        if quantity == quantity.to_integral():
            return str(int(quantity))
        return format(quantity.normalize(), "f").replace(".", ",")

    @staticmethod
    def _price(base: Decimal, factor: Decimal, organic: bool) -> Decimal:
        value = base * factor
        if organic:
            value *= Decimal("1.25")
        return value.quantize(Decimal("0.01"))

    @staticmethod
    def product_traits(kind: str) -> dict:
        """Zusatzstoffe und die Kennzeichnungen glutenfrei und laktosefrei.

        Summary:
            additives ist ein kommaseparierter Text und bleibt leer, wenn nichts zugesetzt ist.
            is_gluten_free und is_lactose_free gehören zur Produktart.
            Bio bleibt getrennt in is_organic, weil das je Packung anders sein kann.
        """
        category = SupermarketCatalog.category_of(kind)
        additives = ""
        gluten_free = True
        lactose_free = True

        if category == "milch":
            lactose_free = kind == "Laktosefreie Milch"
            if kind == "Margarine":
                additives = "Lecithine (E 322 Emulgator), Carotin (E 160a Farbstoff), Aroma"
                lactose_free = True
            elif kind == "Fruchtjoghurt":
                additives = "Aroma"
            elif kind == "Kräuterquark":
                additives = "Kaliumsorbat (E 202 Konservierungsstoff), Aroma"
        elif category == "kaese":
            lactose_free = False
            if kind == "Schmelzkäse":
                additives = "Natriumcitrate (E 331 Säureregulator)"
        elif category == "brot":
            gluten_free = False
            lactose_free = kind not in _MILK_PASTRY
            if kind in _MILK_PASTRY:
                additives = _EMULSIFIER
        elif category == "fleisch":
            if kind not in _FRESH_MEAT:
                additives = _NITRITE
            if kind == "Käsekrainer":
                lactose_free = False
        elif category == "fisch":
            if kind == "Fischstäbchen":
                additives = "Aroma"
                gluten_free = False
            elif kind in {"Matjes", "Sardellen"}:
                additives = _SORBATE
        elif category == "nudeln":
            gluten_free = kind in _GLUTEN_FREE_GRAINS
            if kind in {"Müsli", "Cornflakes", "Müsliriegel"}:
                additives = "Aroma"
            elif kind in {"Tortellini", "Ravioli"}:
                lactose_free = False
        elif category == "suess":
            if kind in {"Schokoriegel", "Schokokeksriegel", "Vollmilchschokolade", "Zartbitterschokolade", "Weiße Schokolade", "Nuss-Nougat-Creme", "Erdnussbutter"}:
                additives = _LECITHIN
            elif kind in {"Erdbeerkonfitüre", "Aprikosenkonfitüre"}:
                additives = _JAM
            elif kind == "Fruchtgummi":
                additives = "Citronensäure (E 330 Säuerungsmittel), Carotin (E 160a Farbstoff), Aroma"
            elif kind == "Lakritz":
                additives = "Ammoniumchlorid, Aroma"
            elif kind in {"Kartoffelchips", "Paprikachips"}:
                additives = "Aroma, Rosmarinextrakt (E 392 Antioxidationsmittel)"
            elif kind in _WHEAT_SNACKS:
                gluten_free = False
            if kind in {"Vollmilchschokolade", "Weiße Schokolade", "Nuss-Nougat-Creme"}:
                lactose_free = False
        elif category == "feinkost":
            if kind in _DELICATESSEN_SALADS or kind in _PRESERVED_DELICATESSEN or kind.startswith("Oliven") or kind in {"Essiggurken", "Cornichons", "Silberzwiebeln", "Tzatziki"}:
                additives = _SORBATE
            elif kind == "Rotkohl im Glas":
                additives = _CITRIC
            if kind in {"Pesto verde", "Pesto rosso", "Feta in Öl", "Tzatziki"}:
                lactose_free = False
                additives = additives or _CITRIC
            elif kind == "Falafel":
                gluten_free = False
        elif category == "getraenk":
            if kind in {"Cola", "Orangenlimonade", "Zitronenlimonade"}:
                additives = _SODA
        elif category == "konserve":
            if kind in {"Passierte Tomaten", "Stückige Tomaten"}:
                additives = _CITRIC
            elif kind == "Kokosmilch":
                additives = "Guarkernmehl (E 412 Stabilisator)"
        elif category == "tiefkuehl":
            if kind == "Tiefkühlpizza":
                additives = "Mononatriumglutamat (E 621 Geschmacksverstärker), Aroma"
                gluten_free = False
                lactose_free = False
            elif kind in {"Vanilleeis", "Schokoladeneis", "Zitroneneis"}:
                additives = _ICE
                lactose_free = False
            elif kind == "Pommes frites":
                additives = "Dinatriumdiphosphat (E 450 Stabilisator)"
            elif kind == "Rahmspinat":
                lactose_free = False
        elif category == "vorrat":
            if kind in {"Weizenmehl Type 405", "Weizenmehl Type 550", "Roggenmehl", "Paniermehl"}:
                gluten_free = False
            if kind == "Mayonnaise":
                lactose_free = False
            if kind in {"Ketchup", "Mayonnaise", "Senf mittelscharf", "Senf scharf"}:
                additives = _SORBATE
            elif kind == "Sojasauce":
                additives = "Aroma"
                gluten_free = False
            elif kind == "Worcestersauce":
                additives = _SORBATE
                gluten_free = False
            elif kind == "Backpulver":
                additives = "Dinatriumdiphosphat (E 450 Säureregulator)"
            elif kind == "Vanillinzucker":
                additives = "Vanillin (Aroma)"
            elif kind == "Tomatenmark":
                additives = _CITRIC
        elif category == "gewuerz":
            if kind in _BROTHS:
                additives = _BROTH
                gluten_free = False
            elif kind in _SEASONING_MIXES:
                additives = "Mononatriumglutamat (E 621 Geschmacksverstärker), Aroma"
            elif kind == "Jodsalz":
                additives = "Kaliumiodat, Natriumferrocyanid (E 535 Rieselhilfe)"
            elif kind == "Speisesalz":
                additives = "Natriumferrocyanid (E 535 Rieselhilfe)"
            elif kind in _SEASONED_SALT:
                additives = "Natriumferrocyanid (E 535 Rieselhilfe), Aroma"
        return {
            "additives": additives,
            "is_gluten_free": gluten_free,
            "is_lactose_free": lactose_free,
        }

    @staticmethod
    def _row(chain: str, kind: str, pack, organic: bool) -> dict:
        category = SupermarketCatalog.category_of(kind)
        quantity, unit, packaging, base = pack
        brand = SupermarketCatalog.brand_for(chain, kind, category, organic)
        amount = SupermarketCatalog._format_quantity(quantity)
        traits = SupermarketCatalog.product_traits(kind)
        return {
            "product_name": f"{brand} {kind}, {amount} {unit}",
            "brand": brand,
            "product_kind": kind,
            "main_category": CATEGORY_LABELS[category],
            "net_quantity": quantity,
            "unit": unit,
            "packaging_type": packaging,
            "regular_price": SupermarketCatalog._price(base, CHAINS[chain]["factor"], organic),
            "is_organic": organic,
            "is_gluten_free": traits["is_gluten_free"],
            "is_lactose_free": traits["is_lactose_free"],
            "additives": traits["additives"],
            "note": NOTE,
        }

    @staticmethod
    def catalog_for(chain: str) -> list[dict]:
        if chain not in CHAINS:
            raise KeyError(chain)
        rows = []
        for kind in PRODUCT_KINDS:
            standard, second = SupermarketCatalog.packs_for(kind, SupermarketCatalog.category_of(kind))
            rows.append(SupermarketCatalog._row(chain, kind, standard, False))
            rows.append(SupermarketCatalog._row(chain, kind, second, kind in ORGANIC_EXAMPLE))
        for kind in PRODUCT_KINDS:
            if len(rows) >= CATALOG_SIZE:
                break
            standard, _second = SupermarketCatalog.packs_for(kind, SupermarketCatalog.category_of(kind))
            rows.append(SupermarketCatalog._row(chain, kind, standard, True))
        names = [row["product_name"] for row in rows]
        if len(rows) != CATALOG_SIZE or len(set(names)) != CATALOG_SIZE:
            raise RuntimeError(f"{chain}: {len(rows)} Zeilen, {len(set(names))} eindeutige Namen")
        return rows

    @staticmethod
    def all_catalogs() -> dict[str, list[dict]]:
        return {chain: SupermarketCatalog.catalog_for(chain) for chain in CHAINS}


SupermarketCatalog._check_categories()


_NITRITE = "Natriumnitrit (E 250 Konservierungsstoff), Ascorbinsäure (E 300 Antioxidationsmittel)"
_SORBATE = "Kaliumsorbat (E 202 Konservierungsstoff), Citronensäure (E 330 Säuerungsmittel)"
_SODA = "Citronensäure (E 330 Säuerungsmittel), Natriumbenzoat (E 211 Konservierungsstoff), Aroma"
_LECITHIN = "Lecithine (E 322 Emulgator), Aroma"
_ICE = "Carrageen (E 407 Stabilisator), Johannisbrotkernmehl (E 410 Stabilisator), Aroma"
_JAM = "Pektine (E 440 Geliermittel), Citronensäure (E 330 Säuerungsmittel), Kaliumsorbat (E 202 Konservierungsstoff)"
_EMULSIFIER = "Mono- und Diglyceride von Speisefettsäuren (E 471 Emulgator), Aroma"
_BROTH = "Mononatriumglutamat (E 621 Geschmacksverstärker), Dinatriuminosinat (E 631 Geschmacksverstärker), Dinatriumguanylat (E 627 Geschmacksverstärker), Zuckerkulör (E 150d Farbstoff), Aroma"
_CITRIC = "Citronensäure (E 330 Säuerungsmittel)"

_FRESH_MEAT = {
    "Hackfleisch",
    "Rinderhackfleisch",
    "Hähnchenbrust",
    "Hähnchenschenkel",
    "Putenbrust",
    "Schweineschnitzel",
    "Schweinenacken",
    "Rindersteak",
    "Rinderrouladen",
    "Lammkotelett",
}
_GLUTEN_FREE_GRAINS = {
    "Langkornreis",
    "Rundkornreis",
    "Basmatireis",
    "Jasminreis",
    "Vollkornreis",
    "Milchreis",
    "Risottoreis",
    "Wildreis",
    "Reisnudeln",
    "Glasnudeln",
    "Quinoa",
    "Polenta",
}
_MILK_PASTRY = {
    "Toast",
    "Rosinenbrötchen",
    "Croissant",
    "Schokocroissant",
    "Krapfen",
    "Berliner",
    "Nussecke",
    "Zimtschnecke",
    "Streuselschnecke",
    "Muffin",
    "Amerikaner",
    "Apfeltasche",
    "Franzbrötchen",
}
_WHEAT_SNACKS = {"Salzstangen", "Brezeln", "Schokoriegel", "Schokokeksriegel", "Müsliriegel"}
_DELICATESSEN_SALADS = {
    "Kartoffelsalat",
    "Nudelsalat",
    "Fleischsalat",
    "Geflügelsalat",
    "Wurstsalat",
    "Heringssalat",
    "Eiersalat",
}
_PRESERVED_DELICATESSEN = {
    "Hummus",
    "Antipasti",
    "Getrocknete Tomaten",
    "Artischockenherzen",
    "Peperoni eingelegt",
    "Kapern",
    "Ajvar",
    "Baba Ganoush",
    "Auberginenmus",
    "Tapenade",
}
_BROTHS = {"Gemüsebrühe", "Hühnerbrühe", "Fleischbrühe"}
_SEASONING_MIXES = {"Pizzagewürz", "Grillgewürz", "Hähnchengewürz"}
_SEASONED_SALT = {"Kräutersalz", "Knoblauchsalz", "Zitronenpfeffer"}


