"""Mengenvorgabe und Zeilen des Einkaufszettels.

Summary:
    Jede Produktart hat Einheit, Schritt und Startwert.
    Die Zeilen des Zettels übernehmen die Eingabe oder diesen Startwert.
"""

from models.supermarket_catalog import SupermarketCatalog
from models.shopping_amount import ShoppingAmount

class ShoppingDemand:
    """Mengenvorgabe und Zeilen des Einkaufszettels.

    Summary:
        Jede Produktart hat Einheit, Schritt und Startwert.
        Die Zeilen des Zettels übernehmen die Eingabe oder diesen Startwert.
    """

    @staticmethod
    def _g(default, step=50, minimum=50):
        return ShoppingAmount("g", step, minimum, default)

    @staticmethod
    def _kg(default=1, step=0.5, minimum=0.5):
        return ShoppingAmount("kg", step, minimum, default)

    @staticmethod
    def _l(default=1, step=0.5, minimum=0.5):
        return ShoppingAmount("l", step, minimum, default)

    @staticmethod
    def _ml(default=500, step=250, minimum=250):
        return ShoppingAmount("ml", step, minimum, default)

    @staticmethod
    def _piece(default, grams, step=1, minimum=1):
        return ShoppingAmount("Stück", step, minimum, default, grams_each=grams)

    @staticmethod
    def _count(unit, default, step=1, minimum=1):
        return ShoppingAmount(unit, step, minimum, default)

    @staticmethod
    def demand_for(kind):
        """Einheit, Schritt und Startwert einer Produktart.

        Summary:
            Getränke in Liter, Aufschnitt und Käse in Gramm, Brötchen und Gebäck in Stück.
            Kräuter, Beeren und Gewürze starten klein, Kartoffeln und Brote bei der üblichen Haushaltmenge.
            Eine unbekannte Art fällt auf ein Stück zurück.
        """
        if kind in _MILK:
            return ShoppingDemand._l(1)
        if kind in _CREAM:
            return ShoppingDemand._g(200)
        if kind in _BUTTER:
            return ShoppingDemand._g(250)
        if kind in _LOAVES:
            return ShoppingDemand._g(500, step=250, minimum=250)
        if kind == "Toast":
            return ShoppingAmount("Scheiben", 1, 1, 8, grams_each=25)
        if kind == "Knäckebrot":
            return ShoppingDemand._g(200)
        if kind in _ROLLS:
            return ShoppingDemand._piece(6, 60)
        if kind == "Laugenstange":
            return ShoppingDemand._piece(2, 120)
        if kind == "Pita":
            return ShoppingDemand._piece(4, 60)
        if kind == "Baguette":
            return ShoppingDemand._piece(1, 250)
        if kind == "Ciabatta":
            return ShoppingDemand._piece(1, 250)
        if kind == "Fladenbrot":
            return ShoppingDemand._piece(1, 300)
        if kind in _PASTRY:
            return ShoppingDemand._piece(2, _PASTRY[kind])
        if kind in _BERRIES:
            return ShoppingDemand._g(250)
        if kind in _COUNTED_FRUIT:
            default, grams = _COUNTED_FRUIT[kind]
            return ShoppingDemand._piece(default, grams)
        if kind in _HERBS:
            return ShoppingDemand._g(20, step=10, minimum=10)
        if kind in _SALADS:
            return ShoppingDemand._g(300, step=100, minimum=100)
        if kind in _HEAVY_VEG:
            return ShoppingDemand._kg(2 if "Kartoffel" in kind or kind == "Drillinge" else 1)
        if kind in _COLD_CUTS:
            return ShoppingDemand._g(100)
        if kind in _SPREADS:
            return ShoppingDemand._g(150)
        if kind in {"Leberkäse", "Fleischkäse", "Chorizo", "Sucuk"}:
            return ShoppingDemand._g(200)
        if kind in _SAUSAGES:
            default, grams = _SAUSAGES[kind]
            return ShoppingDemand._piece(default, grams)
        if kind == "Fischstäbchen":
            return ShoppingDemand._count("Stück", 15, step=5, minimum=5)
        if kind == "Tiefkühlpizza":
            return ShoppingDemand._piece(1, 350)
        if kind in {"Vanilleeis", "Schokoladeneis", "Zitroneneis"}:
            return ShoppingDemand._ml(500)
        if kind in _WATER or kind in _SODA:
            return ShoppingDemand._l(1.5)
        if kind in _JUICE:
            return ShoppingDemand._l(1)
        if kind in {"Filterkaffee", "Espressobohnen"}:
            return ShoppingDemand._g(500, step=250, minimum=250)
        if kind in _TEA:
            return ShoppingDemand._count("Beutel", 20, step=5, minimum=5)
        if kind in _OILS:
            return ShoppingDemand._ml(500)
        if kind in _VINEGAR:
            return ShoppingDemand._ml(250, step=250, minimum=250)
        if kind in _SAUCES:
            return ShoppingDemand._ml(500)
        if kind == "Tomatenmark":
            return ShoppingDemand._g(200)
        if kind in _FLOUR:
            return ShoppingDemand._g(1000, step=250, minimum=250)
        if kind in {"Vanillinzucker", "Backpulver"}:
            return ShoppingDemand._count("Stück", 1)
        if kind == "Hefe":
            return ShoppingDemand._count("Stück", 1)
        if kind in {"Eier Größe M", "Eier Größe L"}:
            return ShoppingDemand._count("Stück", 10)
        if kind in {"Speisesalz", "Meersalz", "Jodsalz", "Kräutersalz", "Knoblauchsalz"}:
            return ShoppingDemand._g(500, step=100, minimum=100)
        if kind == "Zimtstangen":
            return ShoppingDemand._piece(3, 4)
        try:
            return _CATEGORY[SupermarketCatalog.category_of(kind)]
        except KeyError:
            return ShoppingDemand._count("Stück", 1)

    @staticmethod
    def parse_amount(raw):
        """Zahl aus dem Mengenfeld, Komma oder Punkt.

        Summary:
            Leere oder nicht positive Eingaben ergeben None.
            Der Aufrufer setzt dann den Startwert der Produktart ein.
        """
        text = str(raw or "").strip().replace(",", ".")
        if not text:
            return None
        try:
            value = float(text)
        except ValueError:
            return None
        if value <= 0:
            return None
        return value

    @staticmethod
    def format_amount(value):
        """Anzeige der Menge mit deutschem Komma.

        Summary:
            Ganze Zahlen bleiben ohne Nachkommastelle.
            Andere Werte behalten höchstens zwei Stellen.
        """
        if abs(value - round(value)) < 1e-9:
            return str(int(round(value)))
        return f"{value:.2f}".rstrip("0").rstrip(".").replace(".", ",")

    @staticmethod
    def compare_amount(demand, user_amount):
        """Menge in der Einheit, mit der die Preise verglichen werden.

        Summary:
            Gramm und Stück mit Stückgewicht werden zu Kilogramm.
            Milliliter werden zu Liter. Stück, Beutel und Tüten bleiben eine Anzahl.
        """
        if demand.grams_each:
            return {"measure": "mass", "amount": user_amount * demand.grams_each / 1000}
        if demand.unit == "g":
            return {"measure": "mass", "amount": user_amount / 1000}
        if demand.unit == "kg":
            return {"measure": "mass", "amount": user_amount}
        if demand.unit == "ml":
            return {"measure": "volume", "amount": user_amount / 1000}
        if demand.unit == "l":
            return {"measure": "volume", "amount": user_amount}
        return {"measure": "count", "amount": user_amount}

    @staticmethod
    def shopping_rows(names, raw_amounts):
        """Zeilen für den Einkaufszettel, inklusive vorbelegter Menge.

        Summary:
            Jeder Name behält seine Mengenangabe aus dem Formular.
            Fehlt sie oder ist sie ungültig, gilt der Startwert der Produktart.
            amounts ist die umgerechnete Menge für die Preisoptimierung.
        """
        from models.product_search import ProductSearch

        rows = []
        amounts = {}
        for index, name in enumerate(names or []):
            canonical = ProductSearch.product_kind(name) or name
            demand = ShoppingDemand.demand_for(canonical)
            raw = raw_amounts[index] if index < len(raw_amounts or []) else ""
            parsed = ShoppingDemand.parse_amount(raw)
            chosen = demand.default if parsed is None else parsed
            rows.append(
                {
                    "name": canonical,
                    "amount": ShoppingDemand.format_amount(chosen),
                    "unit": demand.unit,
                    "step": demand.step,
                    "minimum": demand.minimum,
                    "default": demand.default,
                }
            )
            amounts[canonical] = ShoppingDemand.compare_amount(demand, chosen)
        return rows, amounts


_MILK = {
    "H-Milch 1,5 %",
    "H-Milch 3,5 %",
    "Frischmilch 1,5 %",
    "Frischmilch 3,5 %",
    "Vollmilch 3,8 %",
    "Buttermilch",
    "Kefir",
    "Laktosefreie Milch",
}
_CREAM = {"Schlagsahne", "Saure Sahne", "Schmand", "Crème fraîche"}
_BUTTER = {"Butter", "Halbfettbutter", "Margarine"}
_LOAVES = {
    "Mischbrot",
    "Vollkornbrot",
    "Roggenbrot",
    "Weißbrot",
    "Dinkelbrot",
    "Mehrkornbrot",
    "Pumpernickel",
    "Sonnenblumenkernbrot",
    "Kürbiskernbrot",
}
_ROLLS = {
    "Brötchen",
    "Laugenbrötchen",
    "Mehrkornbrötchen",
    "Roggenbrötchen",
    "Sesambrötchen",
    "Mohnbrötchen",
    "Körnerbrötchen",
    "Kaisersemmel",
    "Rosinenbrötchen",
}
_PASTRY = {
    "Croissant": 70,
    "Schokocroissant": 80,
    "Donut": 70,
    "Krapfen": 80,
    "Berliner": 80,
    "Nussecke": 90,
    "Zimtschnecke": 90,
    "Streuselschnecke": 90,
    "Muffin": 70,
    "Amerikaner": 60,
    "Apfeltasche": 100,
    "Franzbrötchen": 80,
    "Bagel": 100,
    "Laugenbrezel": 80,
}
_BERRIES = {"Erdbeeren", "Himbeeren", "Brombeeren", "Heidelbeeren", "Johannisbeeren"}
_COUNTED_FRUIT = {
    "Zitronen": (2, 80),
    "Limetten": (2, 60),
    "Kiwi grün": (4, 75),
    "Kiwi gelb": (4, 75),
    "Avocado": (2, 200),
    "Mango": (1, 300),
    "Papaya": (1, 500),
    "Granatapfel": (1, 300),
    "Kaki": (2, 150),
    "Ananas": (1, 900),
    "Honigmelone": (1, 1000),
}
_HERBS = {
    "Blattpetersilie",
    "Petersilie",
    "Krause Petersilie",
    "Schnittlauch",
    "Basilikum",
    "Dill",
    "Koriander",
    "Minze",
    "Rosmarin",
    "Thymian",
}
_SALADS = {"Eisbergsalat", "Kopfsalat", "Romanasalat", "Feldsalat", "Rucola"}
_HEAVY_VEG = {
    "Kartoffeln",
    "Süßkartoffeln",
    "Festkochende Kartoffeln",
    "Mehligkochende Kartoffeln",
    "Drillinge",
    "Weißkohl",
    "Rotkohl",
    "Wirsing",
    "Chinakohl",
    "Hokkaido",
    "Butternut",
}
_COLD_CUTS = {
    "Salami",
    "Rindersalami",
    "Geflügelsalami",
    "Pfeffersalami",
    "Kochschinken",
    "Rohschinken",
    "Mortadella",
    "Lyoner",
    "Bierschinken",
    "Jagdwurst",
    "Gelbwurst",
    "Schinkenwurst",
    "Bierwurst",
    "Presswurst",
    "Presskopf",
    "Sülze",
    "Blutwurst",
    "Rotwurst",
}
_SPREADS = {"Leberwurst", "Kalbsleberwurst", "Teewurst", "Mettwurst", "Zwiebelmettwurst"}
_SAUSAGES = {
    "Bratwurst": (4, 100),
    "Fleischwurst": (4, 80),
    "Wiener Würstchen": (6, 50),
    "Weißwurst": (2, 70),
    "Bockwurst": (4, 80),
    "Frankfurter Würstchen": (4, 80),
    "Knackwurst": (4, 80),
    "Krakauer": (2, 100),
    "Debreziner": (2, 100),
    "Cabanossi": (4, 40),
    "Landjäger": (2, 40),
    "Nürnberger Rostbratwurst": (8, 25),
    "Thüringer Rostbratwurst": (4, 100),
    "Rinderbratwurst": (4, 100),
    "Geflügelbratwurst": (4, 80),
    "Merguez": (4, 60),
    "Käsekrainer": (2, 100),
}
_WATER = {"Mineralwasser", "Sprudel", "Stilles Wasser"}
_SODA = {"Cola", "Orangenlimonade", "Zitronenlimonade"}
_JUICE = {"Apfelsaft", "Orangensaft", "Multivitaminsaft"}
_TEA = {"Schwarztee", "Grüntee", "Pfefferminztee", "Früchtetee", "Kamillentee"}
_OILS = {"Olivenöl", "Rapsöl", "Sonnenblumenöl", "Sesamöl"}
_VINEGAR = {"Balsamico", "Branntweinessig", "Apfelessig"}
_SAUCES = {"Ketchup", "Mayonnaise", "Senf mittelscharf", "Senf scharf", "Sojasauce", "Worcestersauce"}
_FLOUR = {"Weizenmehl Type 405", "Weizenmehl Type 550", "Roggenmehl", "Zucker", "Puderzucker", "Rohrzucker"}

_CATEGORY = {
    "milch": ShoppingDemand._g(500),
    "kaese": ShoppingDemand._g(200),
    "brot": ShoppingDemand._g(500, step=250, minimum=250),
    "obst": ShoppingDemand._kg(1),
    "gemuese": ShoppingDemand._g(500, step=100, minimum=100),
    "fleisch": ShoppingDemand._g(400, step=100, minimum=100),
    "fisch": ShoppingDemand._g(300, step=100, minimum=100),
    "nudeln": ShoppingDemand._g(500, step=100, minimum=100),
    "suess": ShoppingDemand._g(100),
    "feinkost": ShoppingDemand._g(200),
    "konserve": ShoppingDemand._g(400, step=100, minimum=100),
    "getraenk": ShoppingDemand._l(1),
    "tiefkuehl": ShoppingDemand._g(500, step=100, minimum=100),
    "vorrat": ShoppingDemand._g(500, step=100, minimum=100),
    "gewuerz": ShoppingDemand._g(20, step=5, minimum=5),
}


