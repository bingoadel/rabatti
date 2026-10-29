"""CO2-Richtwerte je Produktart aus Agribalyse.

Summary:
    Die Zahlen stehen in data/agribalyse_co2.json und werden lokal gelesen.
    Jede Produktart zeigt auf ein Fertigprodukt der Agribalyse-4-Synthese.
    Eine Bio-Packung bekommt nur dann eine andere Zahl, wenn Agribalyse 3.2
    für dieses Lebensmittel ein Hofpaar führt. Markenname, Beschreibung und
    Zusatzstoffe ändern den Wert nicht.
"""

import json
from pathlib import Path

from models.supermarket_catalog import SupermarketCatalog

_DATA = Path(__file__).resolve().parents[1] / "data" / "agribalyse_co2.json"

SOURCE = (
    "Quelle: ADEME, AGRIBALYSE 4 Synthese (AGRIBALYSE 3.2), Stand 30.06.2026, "
    "kg CO2-Äq. je kg Fertigprodukt, https://data.ademe.fr/datasets/agribalyse-synthese. "
    "Die Bio-Zahl nutzt das Hofpaar aus AGRIBALYSE 3.2, https://doi.org/10.57745/XTENSJ, "
    "nur bei Hähnchen, Schwein, Rind und Apfel. "
    "Lizenz Ouverte Etalab 2.0, https://www.etalab.gouv.fr/licence-ouverte-open-licence. "
    "Diese Nennung ist keine Empfehlung der ADEME."
)

_TABLE = json.loads(_DATA.read_text(encoding="utf-8"))
ANCHORS = _TABLE["anchors"]

_BERRIES = {"Erdbeeren", "Himbeeren", "Brombeeren", "Heidelbeeren", "Johannisbeeren"}
_CITRUS = {"Orangen", "Blutorangen", "Mandarinen", "Clementinen", "Grapefruit"}
_SALADS = {"Eisbergsalat", "Kopfsalat", "Romanasalat", "Feldsalat", "Rucola"}
_ONIONS = {"Zwiebeln", "Rote Zwiebeln", "Schalotten", "Frühlingszwiebeln", "Knoblauch"}
_POTATOES = {
    "Kartoffeln",
    "Süßkartoffeln",
    "Festkochende Kartoffeln",
    "Mehligkochende Kartoffeln",
    "Drillinge",
}
_PEPPERS = {"Paprika rot", "Paprika gelb", "Paprika grün", "Peperoni", "Chili"}
_CHICKEN = {"Hähnchenbrust", "Hähnchenschenkel"}
_TURKEY = {"Putenbrust", "Geflügelsalami", "Geflügelbratwurst"}
_BEEF = {
    "Hackfleisch",
    "Rinderhackfleisch",
    "Rindersteak",
    "Rinderrouladen",
    "Rindersalami",
    "Rinderbratwurst",
    "Kalbsleberwurst",
}
_HAM_COOKED = {"Kochschinken", "Schinkenwurst", "Bierschinken"}
_SAUSAGE = {"Salami", "Pfeffersalami", "Chorizo", "Sucuk", "Landjäger", "Cabanossi"}
_RICE = {
    "Langkornreis",
    "Rundkornreis",
    "Basmatireis",
    "Jasminreis",
    "Vollkornreis",
    "Milchreis",
    "Risottoreis",
    "Wildreis",
}
_GRAIN = {"Couscous", "Bulgur", "Quinoa", "Polenta", "Haferflocken", "Müsli", "Cornflakes", "Müsliriegel"}
_NUTS = {"Erdnüsse", "Cashewkerne", "Mandeln", "Walnüsse", "Erdnussbutter"}
_WHOLE_MILK = {"H-Milch 3,5 %", "Frischmilch 3,5 %", "Vollmilch 3,8 %"}
_CREAM = {"Schlagsahne", "Saure Sahne", "Schmand", "Crème fraîche"}
_YOGURT = {"Naturjoghurt", "Fruchtjoghurt", "Griechischer Joghurt", "Skyr", "Buttermilch", "Kefir"}


class Co2Factors:
    """Liest den Agribalyse-Richtwert einer Produktart.

    Summary:
        Die Produktart bestimmt den Anker, nicht die Marke.
        Eine Bio-Zahl gibt es nur, wenn Agribalyse ein Hofpaar führt.
    """

    @staticmethod
    def anchor_for_kind(kind):
        """Anker-ID der Produktart.

        Summary:
            Die Produktart bestimmt den Agribalyse-Anker, nicht die Marke.
            Arten ohne eigene Zeile teilen den nächsten gespeicherten Anker derselben Warengruppe.
        """
        category = SupermarketCatalog.category_of(kind)
        if category == "gewuerz":
            if "Salz" in kind or kind in {"Gemüsebrühe", "Hühnerbrühe", "Fleischbrühe"}:
                return "salt"
            if kind == "Senfkörner":
                return "mustard"
            return "pepper"
        if category == "milch":
            if kind == "Butter":
                return "butter"
            if kind == "Halbfettbutter":
                return "butter_light"
            if kind == "Margarine":
                return "margarine"
            if kind in _CREAM:
                return "cream"
            if "Quark" in kind:
                return "quark"
            if kind in _YOGURT:
                return "yogurt"
            if kind in _WHOLE_MILK:
                return "milk_whole"
            return "milk_low"
        if category == "kaese":
            return "cheese"
        if category == "brot":
            return "bread"
        if category == "obst":
            if kind == "Bananen":
                return "banana"
            if kind in _CITRUS:
                return "orange"
            if kind in {"Zitronen", "Limetten"}:
                return "lemon"
            if kind in _BERRIES:
                return "berry"
            return "apple"
        if category == "gemuese":
            if "Tomate" in kind:
                return "tomato"
            if kind in _POTATOES or "Kartoffel" in kind:
                return "potato"
            if kind in {"Möhren", "Pastinaken"}:
                return "carrot"
            if kind in _ONIONS:
                return "onion"
            if kind == "Spinat":
                return "spinach"
            if kind in _SALADS or kind == "Mangold":
                return "lettuce"
            if kind in _PEPPERS:
                return "pepper_veg"
            if kind in {"Grüne Bohnen", "Zuckerschoten"}:
                return "green_bean"
            return "carrot"
        if category == "fleisch":
            if kind in _CHICKEN:
                return "chicken"
            if kind in _TURKEY:
                return "turkey"
            if kind in _BEEF:
                return "beef"
            if kind == "Lammkotelett":
                return "lamb"
            if kind == "Merguez":
                return "merguez"
            if kind in _HAM_COOKED:
                return "ham_cooked"
            if kind == "Rohschinken":
                return "ham_raw"
            if kind in _SAUSAGE:
                return "sausage"
            return "pork"
        if category == "fisch":
            if "Lachs" in kind:
                return "salmon"
            if "Thun" in kind:
                return "tuna"
            return "white_fish"
        if category == "nudeln":
            if kind in _RICE or kind.endswith("reis"):
                return "rice"
            if kind in _GRAIN:
                return "oat"
            if kind == "Eiernudeln":
                return "pasta_egg"
            return "pasta"
        if category == "suess":
            if kind == "Honig":
                return "honey"
            if kind in _NUTS:
                return "chickpea"
            if "Konfitüre" in kind:
                return "berry"
            if kind in {"Kartoffelchips", "Paprikachips"}:
                return "potato"
            if kind in {"Salzstangen", "Brezeln"}:
                return "bread"
            return "chocolate"
        if category == "feinkost":
            if kind == "Getrocknete Tomaten":
                return "tomato_dried"
            if "Tomate" in kind:
                return "tomato"
            if "Oliven" in kind or kind == "Tapenade":
                return "olive_fruit"
            if kind in {"Pesto verde", "Pesto rosso"}:
                return "olive_oil"
            if kind in {"Fleischsalat", "Wurstsalat"}:
                return "pork"
            if kind == "Geflügelsalat":
                return "turkey"
            if kind == "Heringssalat":
                return "white_fish"
            if kind == "Eiersalat":
                return "egg"
            if kind in {"Sauerkraut", "Rotkohl im Glas"}:
                return "carrot"
            return "hummus"
        if category == "konserve":
            if "Tomate" in kind:
                return "tomato_puree"
            if "Linsen" in kind:
                return "lentil"
            if kind == "Kichererbsen":
                return "chickpea"
            if kind == "Kokosmilch":
                return "coconut"
            return "green_bean"
        if category == "getraenk":
            if kind in {"Mineralwasser", "Sprudel", "Stilles Wasser"}:
                return "water"
            if kind in {"Cola", "Orangenlimonade", "Zitronenlimonade"}:
                return "cola"
            if kind == "Apfelsaft":
                return "apple_juice"
            if kind in {"Orangensaft", "Multivitaminsaft"}:
                return "orange_juice"
            if kind in {"Filterkaffee", "Espressobohnen"}:
                return "coffee"
            return "tea"
        if category == "tiefkuehl":
            if kind == "Tiefkühlpizza":
                return "pizza"
            if kind == "Pommes frites":
                return "potato"
            if kind == "Rahmspinat":
                return "spinach"
            if kind == "Tiefkühlerbsen":
                return "green_bean"
            if kind == "Tiefkühlbeeren":
                return "berry"
            if kind == "Schokoladeneis":
                return "chocolate"
            if kind == "Zitroneneis":
                return "lemon"
            return "cream"
        if kind in {"Olivenöl"}:
            return "olive_oil"
        if kind == "Rapsöl":
            return "rape_oil"
        if kind == "Sonnenblumenöl":
            return "sunflower_oil"
        if kind == "Sesamöl":
            return "sesame_oil"
        if kind == "Balsamico":
            return "wine"
        if kind == "Apfelessig":
            return "apple_juice"
        if kind == "Branntweinessig":
            return "beer"
        if kind == "Ketchup":
            return "ketchup"
        if kind == "Mayonnaise":
            return "mayonnaise"
        if kind in {"Senf mittelscharf", "Senf scharf"}:
            return "mustard"
        if kind == "Tomatenmark":
            return "tomato_puree"
        if kind in {"Sojasauce", "Worcestersauce"}:
            return "salt"
        if "Salz" in kind:
            return "salt"
        if kind in {"Eier Größe M", "Eier Größe L"}:
            return "egg"
        if kind in {"Zucker", "Puderzucker", "Rohrzucker", "Vanillinzucker"}:
            return "sugar"
        if kind == "Roggenmehl":
            return "rye_flour"
        return "flour"

    @staticmethod
    def farm_pair_for(kind):
        """Hofpaar, das eine Bio-Packung von der konventionellen Zahl unterscheidet.

        Summary:
            Hähnchen, Rind, Schwein und der Apfel haben ein Paar in Agribalyse 3.2.
            Schinken und Rohwurst nutzen das Schweinepaar, weil Agribalyse dafür kein eigenes Bio-Fertigprodukt führt.
            Ohne Paar bleibt die Bio-Packung auf dem Fertigproduktwert.
        """
        anchor_id = Co2Factors.anchor_for_kind(kind)
        if anchor_id == "apple" and kind == "Äpfel":
            return "apple"
        if anchor_id == "chicken":
            return "chicken"
        if anchor_id == "beef":
            return "beef"
        if anchor_id in {"pork", "ham_cooked", "ham_raw", "sausage"}:
            return "pork"
        return None

    @staticmethod
    def co2_kg_per_kg(kind, organic=False):
        """Kilogramm CO2-Äquivalent je Kilogramm dieser Packung.

        Summary:
            Die konventionelle Zahl ist der Fertigproduktwert des Ankers.
            Bei einer Bio-Packung mit Hofpaar wird dieser Wert mit dem Verhältnis der Hofzahlen malgenommen.
            Ohne Hofpaar bleibt es dieselbe Zahl, auch wenn die Packung Bio ist.
        """
        anchor = ANCHORS[Co2Factors.anchor_for_kind(kind)]
        pair_id = Co2Factors.farm_pair_for(kind) if organic else None
        if not pair_id:
            return float(anchor["kg_co2e"])
        pair = ANCHORS[pair_id]["organic"]
        ratio = float(pair["farm_organic_kg"]) / float(pair["farm_conventional_kg"])
        return float(anchor["kg_co2e"]) * ratio

    @staticmethod
    def co2_basis(kind, organic):
        """Kurzer Herkunftssatz für die gewählte Packung.

        Summary:
            Eine eigene Bio-Zeile wird nur genannt, wenn das Hofpaar existiert.
            Sonst bleibt sichtbar, dass die Bio-Packung denselben Fertigproduktwert trägt.
        """
        if organic and Co2Factors.farm_pair_for(kind):
            return "Bio-Zeile aus Agribalyse"
        if organic:
            return "Bio-Packung, Agribalyse führt dafür keine eigene Zeile"
        return "konventionelle Zeile"

    @staticmethod
    def reference_name(kind):
        """Französischer Name des Fertigprodukts, auf das die Produktart zeigt.

        Summary:
            Der Name stammt aus der Agribalyse-4-Synthese und dient der Zuordnung.
        """
        return ANCHORS[Co2Factors.anchor_for_kind(kind)]["name_fr"]

    @staticmethod
    def reference_code(kind):
        """CIQUAL-Code des Fertigprodukts.

        Summary:
            Der Code identifiziert die Zeile in der Agribalyse-Synthese.
        """
        return ANCHORS[Co2Factors.anchor_for_kind(kind)]["ciqual"]


