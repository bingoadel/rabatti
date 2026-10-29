"""Erzeugt data/grocery.sqlite mit 1100 Lebensmitteln.

Die ersten 200 Produkte bleiben die festen Beispieldaten. Weitere 900
fiktive Lebensmittel liegen in Filialen im Umkreis von 50 km um Augsburg.
Das Spaltenschema steht in info/DatabaseShema/grocery_database_columns.csv.
"""

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.store_locations import AUGSBURG_AREA_STORES

DATA = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA / "grocery.sqlite"

CHAINS = [
    ("lidl", "Lidl"),
    ("aldi", "Aldi"),
    ("rewe", "Rewe"),
    ("edeka", "Edeka"),
    ("kaufland", "Kaufland"),
    ("penny", "Penny"),
    ("netto", "Netto"),
    ("norma", "Norma"),
    ("marktkauf", "Marktkauf"),
    ("spar", "Spar"),
    ("real", "real"),
    ("globus", "Globus"),
]

CITIES = [
    (
        "Augsburg",
        [
            ("86154", "Ulmer Straße 12", "Oberhausen"),
            ("86157", "Stadtberger Straße 40", "Pfersee"),
            ("86150", "Annastraße 8", "Innenstadt"),
            ("86165", "Neuburger Straße 90", "Lechhausen"),
            ("86199", "Wellenburger Straße 15", "Göggingen"),
            ("86179", "Haunstetter Straße 22", "Haunstetten"),
        ],
    ),
    (
        "München",
        [
            ("80331", "Tal 18", "Altstadt"),
            ("80469", "Kaiserstraße 30", "Isarvorstadt"),
            ("80992", "Pelkovenstraße 90", "Moosach"),
            ("81541", "Tegernseer Landstraße 100", "Obergiesing"),
        ],
    ),
    (
        "Berlin",
        [
            ("10115", "Chausseestraße 25", "Mitte"),
            ("12043", "Karl-Marx-Straße 80", "Neukölln"),
            ("13347", "Seestraße 40", "Wedding"),
        ],
    ),
    (
        "Hamburg",
        [
            ("20095", "Mönckebergstraße 7", "Altstadt"),
            ("22041", "Wandsbeker Marktstraße 50", "Wandsbek"),
            ("22765", "Neue Große Bergstraße 12", "Altona"),
        ],
    ),
    (
        "Köln",
        [
            ("50667", "Schildergasse 60", "Innenstadt"),
            ("50823", "Venloer Straße 300", "Ehrenfeld"),
        ],
    ),
    (
        "Stuttgart",
        [
            ("70173", "Königstraße 20", "Mitte"),
            ("70469", "Heilbronner Straße 200", "Feuerbach"),
        ],
    ),
    (
        "Nürnberg",
        [
            ("90402", "Königstraße 40", "Altstadt"),
            ("90441", "Fürther Straße 120", "Gostenhof"),
        ],
    ),
    ("Plochingen", [("73207", "Am Fischbrunnen 5", "Zentrum")]),
]

OFFERS = ["", "", "Rabatt", "Preisaktion", "Mengenrabatt", "Gutschein", "Coupon", "Gratisartikel"]
OFFER_FACTOR = {
    "": 1,
    "Rabatt": 0.8,
    "Preisaktion": 0.7,
    "Mengenrabatt": 0.75,
    "Gutschein": 0.85,
    "Coupon": 0.9,
    "Gratisartikel": 0,
}

# Je Gruppe genau acht Produkte: Marke|Hersteller|Name
GROUPS = """
Molkereiprodukte|Milch|WG-101|1|l|Getränkekarton|0|A|Milch|vegetarisch|1.15|Milch
Milbona|Lidl Stiftung|H-Milch 1,5 %
Milsani|Aldi Einkauf|H-Milch 3,5 %
Gut & Günstig|Edeka Zentrale|Frische Vollmilch 3,5 %
ja!|Rewe Markt|Fettarme Milch 1,5 %
Weihenstephan|Molkerei Weihenstephan|Alpenmilch 3,5 %
Bärenmarke|Milchwerke Schwaben|Alpenfrische Milch 3,8 %
Berchtesgadener Land|Milchwerke Berchtesgadener Land|Bio-Frischmilch 3,8 %
Landliebe|FrieslandCampina|Frische Landmilch 3,8 %
Molkereiprodukte|Joghurt|WG-102|500|g|Becher|0|B|Milch|vegetarisch|0.79|Milch, Milchsäurekulturen
Ehrmann|Ehrmann|Almighurt Erdbeere
Zott|Zott|Sahnejoghurt Vanille
Danone|Danone|Activia Natur
Milbona|Lidl Stiftung|Joghurt Mild
ja!|Rewe Markt|Fruchtjoghurt Kirsche
Gut & Günstig|Edeka Zentrale|Joghurt Natur
Weihenstephan|Molkerei Weihenstephan|Rahmjoghurt
Landliebe|FrieslandCampina|Joghurt Erdbeere
Molkereiprodukte|Käse|WG-103|200|g|Folie|0|C|Milch|vegetarisch|2.49|Milch, Salz, Lab
Milram|DMK|Gouda mittelalt
Gut & Günstig|Edeka Zentrale|Emmentaler Scheiben
Hochland|Hochland|Sandwich Scheiben
Milbona|Lidl Stiftung|Maasdamer
Grünländer|Hochwald|Kräuterrahmkäse
Galbani|Lactalis|Mozzarella
Rougette|Savencia|Ofenkäse
ja!|Rewe Markt|Reibekäse
Molkereiprodukte|Sahne und Quark|WG-104|250|g|Becher|0|C|Milch|vegetarisch|1.29|Milch
Meggle|Meggle|Deutsche Markenbutter|Butter
Gut & Günstig|Edeka Zentrale|Markenbutter|Butter
Milbona|Lidl Stiftung|Schlagsahne|Sahne
Weihenstephan|Molkerei Weihenstephan|Saure Sahne|Sahne
Milsani|Aldi Einkauf|Speisequark mager|Quark
Exquisa|Käserei Champignon|Quark fein|Quark
Landliebe|FrieslandCampina|Schlagsahne|Sahne
ja!|Rewe Markt|Schmand|Sahne
Brot und Backwaren|Brot|WG-201|500|g|Beutel|0|B|Gluten|vegetarisch|1.49|Mehl, Wasser, Hefe, Salz
Harry|Harry-Brot|Roggenmischbrot|Mischbrot
Golden Toast|Lieken|Buttertoast|Toast
Grafschafter|Lieken|Toastbrötchen|Toast
K-Classic|Kaufland|Bauernbrot|Mischbrot
Gut & Günstig|Edeka Zentrale|Vollkornbrot|Vollkornbrot
Lieken|Lieken|Urkorn|Vollkornbrot
Schulstad|Lantmännen|Krustenbrot|Mischbrot
ja!|Rewe Markt|Mehrkornbrötchen|Brötchen
Obst|Obst|WG-301|1|kg|Lose|0|A|||1.99|Obst
Chiquita|Chiquita|Bananen|Bananen
Dole|Dole|Bananen|Bananen
Pink Lady|Pink Lady|Äpfel|Äpfel
ja!|Rewe Markt|Äpfel Elstar|Äpfel
Gut & Günstig|Edeka Zentrale|Clementinen|Zitrusfrüchte
Driscoll's|Driscoll's|Erdbeeren|Beeren
Zespri|Zespri|Kiwi gold|Exoten
Sunner|Sunner|Tafeltrauben hell|Trauben
Gemüse|Gemüse|WG-302|1|kg|Lose|0|A|||1.49|Gemüse
ja!|Rewe Markt|Möhren|Wurzelgemüse
Gut & Günstig|Edeka Zentrale|Speisekartoffeln|Wurzelgemüse
Eisberg|Eisberg|Salat|Salat
ja!|Rewe Markt|Salatgurke|Fruchtgemüse
Gut & Günstig|Edeka Zentrale|Zwiebeln|Wurzelgemüse
Edeka|Edeka Zentrale|Champignons|Pilze
ja!|Rewe Markt|Paprika rot|Fruchtgemüse
Tasty Tom|Tasty Tom|Cherrytomaten|Fruchtgemüse
Fleisch|Fleisch|WG-401|500|g|Schale|0|C|||4.99|Fleisch
Gut & Günstig|Edeka Zentrale|Hackfleisch gemischt|Hackfleisch
ja!|Rewe Markt|Hähnchenbrustfilet|Geflügel
Tillman's|Tillman's|Rinderhack|Rind
Wilhelm Brandenburg|Sprehe|Hähnchenschenkel|Geflügel
K-Classic|Kaufland|Schweineschnitzel|Schwein
Bauerngut|Bauerngut|Putensteaks|Geflügel
Mühlenhof|Mühlenhof|Schweinebraten|Schwein
Rewe Bio|Rewe Markt|Bio-Rinderhack|Rind
Wurst|Wurst|WG-402|200|g|Folie|0|D|||2.29|Fleisch, Salz, Gewürze
Herta|Herta|Fleischwurst|Brühwurst
Böklunder|Böklunder|Würstchen|Würstchen
Rügenwalder Mühle|Rügenwalder Mühle|Schinken Spicker|Schinken
Meica|Meica|Schinkenwurst|Brühwurst
Gutfried|Gutfried|Geflügellyoner|Geflügelwurst
Zimbo|Zimbo|Salami|Rohwurst
ja!|Rewe Markt|Bierschinken|Schinken
Gut & Günstig|Edeka Zentrale|Leberwurst|Streichwurst
Fisch|Fisch|WG-403|250|g|Schale|0|B|Fisch||3.49|Fisch
Iglo|Iglo|Fischstäbchen|Fischstäbchen
Friedrichs|Gottfried Friedrichs|Geräucherte Forelle|Räucherfisch
Nadler|Nadler|Matjesfilet|Hering
Gut & Günstig|Edeka Zentrale|Seelachsfilet|Seelachs
ja!|Rewe Markt|Backfisch|Backfisch
Deutsche See|Deutsche See|Lachsfilet|Lachs
Followfish|Followfish|Thunfischfilet|Thunfisch
Appel|Appel|Heringsfilet|Hering
Nudeln und Reis|Nudeln|WG-501|500|g|Beutel|0|A|Gluten|vegan|1.19|Hartweizengrieß, Wasser
Barilla|Barilla|Spaghetti No. 5|Nudeln
Buitoni|Nestlé|Penne Rigate|Nudeln
De Cecco|De Cecco|Fusilli|Nudeln
Milbona|Lidl Stiftung|Spaghetti|Nudeln
ja!|Rewe Markt|Langkornreis|Reis
Uncle Ben's|Mars|Reis im Beutel|Reis
Gut & Günstig|Edeka Zentrale|Spiralen|Nudeln
Tilda|Tilda|Basmati Reis|Reis
Konserven|Gemüsekonserven|WG-502|400|g|Dose|0|A|||1.29|Gemüse, Wasser, Salz
Bonduelle|Bonduelle|Junge Erbsen|Gemüse
ja!|Rewe Markt|Zuckermais|Gemüse
Gut & Günstig|Edeka Zentrale|Kidneybohnen|Hülsenfrüchte
Mutti|Mutti|Passata|Tomaten
Cirio|Cirio|Stückige Tomaten|Tomaten
Hengstenberg|Hengstenberg|Rotkohl|Gemüse
Erasco|Erasco|Linseneintopf|Eintopf
Saupiquet|Saupiquet|Thunfisch in Sonnenblumenöl|Fisch
Brotaufstrich|Aufstrich|WG-503|400|g|Glas|0|D|Milch, Schalenfrüchte|vegetarisch|2.79|Zucker, Haselnüsse, Kakao
Nutella|Ferrero|Nuss-Nougat-Creme|Nusscreme
Nusspli|Zentis|Nuss-Nougat-Creme|Nusscreme
Schwartau|Schwartau|Extra Erdbeere|Konfitüre
Mövenpick|Schwartau|Fruchtaufstrich Himbeere|Konfitüre
Gut & Günstig|Edeka Zentrale|Nuss-Nougat-Creme|Nusscreme
ja!|Rewe Markt|Erdbeerkonfitüre|Konfitüre
Rapunzel|Rapunzel|Samba Aufstrich|Nusscreme
Du darfst|Unilever|Halbfettmargarine|Margarine
Getränke|Limonade und Wasser|WG-601|1.25|l|PET-Flasche|1|C|||0.89|Wasser, Zucker
Coca-Cola|Coca-Cola|Cola|Limonade
Pepsi|PepsiCo|Cola|Limonade
Fanta|Coca-Cola|Orange|Limonade
Sprite|Coca-Cola|Zitrone|Limonade
Gerolsteiner|Gerolsteiner|Sprudel|Wasser
Volvic|Danone|Naturelle|Wasser
Adelholzener|Adelholzener|Classic|Wasser
Mio Mio|Günter Coffee|Mate Banane|Mate
Säfte|Saft|WG-602|1|l|Getränkekarton|0|C|||1.49|Fruchtsaft
Hohes C|Eckes-Granini|Orange|Orangensaft
Granini|Eckes-Granini|Apfel|Apfelsaft
Amecke|Amecke|Sanfte Orange|Orangensaft
Innocent|Innocent|Orange ohne Fruchtfleisch|Orangensaft
ja!|Rewe Markt|Orangensaft|Orangensaft
Gut & Günstig|Edeka Zentrale|Apfelsaft|Apfelsaft
Valensina|Valensina|Orange|Orangensaft
Pfanner|Pfanner|Multivitamin|Mehrfruchtsaft
Kaffee und Tee|Kaffee|WG-603|500|g|Beutel|0|B|||4.99|Kaffee
Jacobs|Jacobs Douwe Egberts|Krönung|Kaffee
Dallmayr|Dallmayr|Prodomo|Kaffee
Melitta|Melitta|Auslese klassisch|Kaffee
Tchibo|Tchibo|Feine Milde|Kaffee
Milbona|Lidl Stiftung|Café Crema|Kaffee
ja!|Rewe Markt|Filterkaffee|Kaffee
Teekanne|Teekanne|Ostfriesen Tee|Tee
Meßmer|Meßmer|Pfefferminze|Tee
Süßwaren|Schokolade|WG-701|100|g|Folie|0|E|Milch|vegetarisch|1.29|Zucker, Kakao, Milch
Milka|Mondelez|Alpenmilch|Schokolade
Haribo|Haribo|Goldbären|Fruchtgummi
Kinder|Ferrero|Schokolade|Schokolade
Ritter Sport|Ritter Sport|Voll-Nuss|Schokolade
Snickers|Mars|Riegel|Riegel
Merci|Storck|Große Vielfalt|Pralinen
Katjes|Katjes|Wunderland|Fruchtgummi
Storck|Storck|Toffifee|Pralinen
Snacks|Snacks|WG-702|175|g|Beutel|0|D|Gluten|vegetarisch|1.59|Kartoffeln, Sonnenblumenöl, Salz
Pringles|Kellanova|Original|Chips
Funny-frisch|Intersnack|Ungarisch|Chips
Chio|Intersnack|Chips Paprika|Chips
Lorenz|Lorenz|Crunchips Salted|Chips
Lay's|PepsiCo|Gesalzen|Chips
Ültje|Intersnack|Erdnüsse geröstet|Nüsse
Seeberger|Seeberger|Studentenfutter|Nüsse
ja!|Rewe Markt|Salzstangen|Gebäck
Tiefkühl|Tiefkühlkost|WG-801|450|g|Karton|0|C|Gluten||2.49|siehe Verpackung
Dr. Oetker|Dr. Oetker|Ristorante Salame|Pizza
Wagner|Nestlé Wagner|Steinofen Pizza|Pizza
Iglo|Iglo|Schlemmerfilet Bordelaise|Fisch
Frosta|Frosta|Gemüsepfanne|Gemüse
Coppenrath & Wiese|Coppenrath & Wiese|Sahnetorte Erdbeere|Kuchen
McCain|McCain|Pommes Frites|Kartoffelprodukte
ja!|Rewe Markt|Rahmspinat|Gemüse
Gut & Günstig|Edeka Zentrale|Erbsen Fein|Gemüse
Fertiggerichte|Fertiggerichte|WG-802|400|g|Beutel|0|C|Gluten||1.99|siehe Verpackung
Maggi|Nestlé|5 Minuten Terrine Gulasch|Suppen
Knorr|Unilever|Spaghetteria|Nudelgerichte
Miracoli|Mars|Spaghetti-Gerichte|Nudelgerichte
Sonnen Bassermann|Sonnen Bassermann|Chili con Carne|Eintopf
Erasco|Erasco|Gulaschtopf|Eintopf
Gut & Günstig|Edeka Zentrale|Nudelgericht Tomate|Nudelgerichte
ja!|Rewe Markt|Linseneintopf|Eintopf
Uncle Ben's|Mars|Express Reis Indisch|Reisgerichte
Öl und Essig|Öl|WG-901|750|ml|Glasflasche|0|C|||3.49|pflanzliches Öl
Mazola|Mazola|Maiskeimöl|Öl
Thomy|Nestlé|Rapsöl|Öl
Bertolli|Deoleo|Olivenöl|Öl
ja!|Rewe Markt|Sonnenblumenöl|Öl
Gut & Günstig|Edeka Zentrale|Rapsöl|Öl
Kühne|Kühne|Branntweinessig|Essig
Mazzetti|Mazzetti|Aceto Balsamico|Essig
Filippo Berio|Filippo Berio|Natives Olivenöl|Öl
Soßen|Soßen|WG-902|250|ml|Flasche|0|D|||1.19|siehe Verpackung
Thomy|Nestlé|Delikatess Mayonnaise|Mayonnaise
Miracel Whip|Kraft|Salatcreme|Mayonnaise
Develey|Develey|Ketchup|Ketchup
Heinz|Kraft Heinz|Tomato Ketchup|Ketchup
Maggi|Nestlé|Würze|Würze
Knorr|Unilever|Bratensauce|Saucen
ja!|Rewe Markt|Mittelscharfer Senf|Senf
Kikkoman|Kikkoman|Sojasauce|Saucen
Frühstückscerealien|Müsli|WG-903|500|g|Beutel|0|A|Gluten|vegetarisch|2.29|Hafer, Zucker
Kellogg's|Kellanova|Corn Flakes|Cornflakes
Seitenbacher|Seitenbacher|Müsli|Müsli
ja!|Rewe Markt|Haferflocken|Haferflocken
Gut & Günstig|Edeka Zentrale|Knuspermüsli|Müsli
Nestlé|Nestlé|Lion Cerealien|Cornflakes
Kölln|Kölln|Haferflocken zart|Haferflocken
Corny|Schwartau|Schoko Riegel|Riegel
Dr. Oetker|Dr. Oetker|Vitalis Knusper|Müsli
Backzutaten|Backen|WG-904|500|g|Beutel|0|A|Gluten|vegetarisch|1.09|siehe Verpackung
Dr. Oetker|Dr. Oetker|Vanillinzucker|Zucker
Diamant|GoodMills|Weizenmehl Type 405|Mehl
Südzucker|Südzucker|Raffinade|Zucker
Ruf|Ruf|Schokoladenpudding|Pudding
Dr. Oetker|Dr. Oetker|Backin|Backtriebmittel
ja!|Rewe Markt|Eier 10 Stück|Eier
Gut & Günstig|Edeka Zentrale|Backhefe|Backtriebmittel
Leimer|Leimer|Paniermehl|Panade
Eis|Eis|WG-905|500|ml|Becher|0|D|Milch|vegetarisch|2.99|Milch, Zucker
Langnese|Unilever|Cremissimo Vanille|Vanilleeis
Schöller|Nestlé|Bum Bum|Eisriegel
Mövenpick|Froneri|Vanilleeis|Vanilleeis
ja!|Rewe Markt|Vanilleeis|Vanilleeis
Gut & Günstig|Edeka Zentrale|Fürst-Pückler-Art|Mehrsorte
Ben & Jerry's|Unilever|Cookie Dough|Eisbecher
Magnum|Unilever|Mandel|Eisriegel
Mars|Mars|Eisriegel|Eisriegel
"""


def stores():
    result = []
    chain_index = 0
    for city, places in CITIES:
        for postal_code, street, district in places:
            slug, name = CHAINS[chain_index % len(CHAINS)]
            chain_index += 1
            result.append(
                {
                    "slug": slug,
                    "supermarket_name": name,
                    "store_id": f"{slug}-{city}-{district}".lower().replace(" ", "-"),
                    "store_address": f"{street}, {postal_code} {city}-{district}",
                }
            )
    return result


def catalog():
    products = []
    current = None
    for raw_line in GROUPS.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) == 12:
            current = {
                "main_category": parts[0],
                "sub_category": parts[1],
                "internal_commodity_group": parts[2],
                "net_quantity": float(parts[3]),
                "unit": parts[4],
                "packaging_type": parts[5],
                "is_deposit_required": int(parts[6]),
                "nutriscore": parts[7],
                "allergens": parts[8],
                "dietary_tags": parts[9],
                "regular_price": float(parts[10]),
                "ingredients_list": parts[11],
            }
            continue
        if current is None or len(parts) not in (3, 4):
            raise ValueError(f"Zeile nicht lesbar: {line}")
        brand, manufacturer, name = parts[:3]
        item = dict(current)
        if len(parts) == 4:
            item["sub_category"] = parts[3]
        item["brand"] = brand
        item["manufacturer"] = manufacturer
        item["product_name"] = f"{brand} {name}"
        item["is_organic"] = int("bio" in item["product_name"].casefold())
        if item["sub_category"].casefold() == item["main_category"].casefold():
            raise ValueError(f"Unterkategorie gleich Kategorie: {item['product_name']}")
        products.append(item)
    names = [item["product_name"].casefold() for item in products]
    if len(products) != 200:
        raise ValueError(f"Erwartet 200 Produkte, gefunden {len(products)}")
    if len(names) != len(set(names)):
        raise ValueError("Produktnamen sind nicht eindeutig")
    by_main = {}
    for item in products:
        by_main.setdefault(item["main_category"], set()).add(item["sub_category"])
    lonely = [name for name, subs in by_main.items() if len(subs) < 2]
    if lonely:
        raise ValueError(f"Kategorie mit nur einer Unterkategorie: {lonely}")
    return products


def base_price(price, quantity, unit):
    if unit == "g":
        return round(price / quantity * 1000, 2)
    if unit == "ml":
        return round(price / quantity * 1000, 2)
    return round(price / quantity, 2)


# Frei verwendbare Produktfotos, als Web-Link in image_url gespeichert.
IMAGE_URLS = {
    "Milch": "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/38/Glass_of_milk.jpg/330px-Glass_of_milk.jpg",
    "Joghurt": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/05/Yogurt.jpg/330px-Yogurt.jpg",
    "Käse": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/45/Cheese.jpg/330px-Cheese.jpg",
    "Butter": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f9/Stick-of-butter-salted.jpg/330px-Stick-of-butter-salted.jpg",
    "Sahne": "https://upload.wikimedia.org/wikipedia/commons/0/01/Cream.jpg",
    "Quark": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/7b/Skimmed_milk_quark_on_spoon.jpg/330px-Skimmed_milk_quark_on_spoon.jpg",
    "Mischbrot": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a0/Rye_bread.jpg/330px-Rye_bread.jpg",
    "Toast": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/71/Toast.jpg/330px-Toast.jpg",
    "Vollkornbrot": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a6/Whole_grain_bread.jpg/330px-Whole_grain_bread.jpg",
    "Brötchen": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/61/Bread_rolls.jpg/330px-Bread_rolls.jpg",
    "Bananen": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4c/Bananas.jpg/330px-Bananas.jpg",
    "Äpfel": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/2b/Apple.jpg/330px-Apple.jpg",
    "Zitrusfrüchte": "https://upload.wikimedia.org/wikipedia/commons/4/41/Clementines.jpg",
    "Beeren": "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e1/Strawberries.jpg/330px-Strawberries.jpg",
    "Exoten": "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/38/Kiwifruit.jpg/330px-Kiwifruit.jpg",
    "Trauben": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/6b/Grapes.jpg/330px-Grapes.jpg",
    "Wurzelgemüse": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c8/Carrots.jpg/330px-Carrots.jpg",
    "Salat": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f5/Iceberg_lettuce.jpg/330px-Iceberg_lettuce.jpg",
    "Fruchtgemüse": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/0a/Cucumber.jpg/330px-Cucumber.jpg",
    "Pilze": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/6b/Agaricus_bisporus.jpg/330px-Agaricus_bisporus.jpg",
    "Hackfleisch": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/2b/Minced_meat.jpg/330px-Minced_meat.jpg",
    "Geflügel": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/7e/Chicken_meat.jpg/330px-Chicken_meat.jpg",
    "Schwein": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/00/Pork_chop.jpg/330px-Pork_chop.jpg",
    "Rind": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/5e/Beef_meat.jpg/330px-Beef_meat.jpg",
    "Brühwurst": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c7/Sausage.jpg/330px-Sausage.jpg",
    "Würstchen": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c7/Sausage.jpg/330px-Sausage.jpg",
    "Schinken": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/6b/Schinken.jpg/330px-Schinken.jpg",
    "Geflügelwurst": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/28/Chicken_sausage.jpg/330px-Chicken_sausage.jpg",
    "Rohwurst": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4d/Salami.jpg/330px-Salami.jpg",
    "Streichwurst": "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e0/Leberwurst.jpg/330px-Leberwurst.jpg",
    "Fischstäbchen": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/00/Fish_fingers.jpg/330px-Fish_fingers.jpg",
    "Räucherfisch": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/ca/Smoked_trout.jpg/330px-Smoked_trout.jpg",
    "Hering": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/68/Herring.jpg/330px-Herring.jpg",
    "Seelachs": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/08/Fish_fillet.jpg/330px-Fish_fillet.jpg",
    "Backfisch": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/76/Fish_and_chips.jpg/330px-Fish_and_chips.jpg",
    "Lachs": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/72/Salmon.jpg/330px-Salmon.jpg",
    "Thunfisch": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/5d/Thunfisch.jpg/330px-Thunfisch.jpg",
    "Nudeln": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/93/Spaghetti.jpg/330px-Spaghetti.jpg",
    "Reis": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a3/White_rice.jpg/330px-White_rice.jpg",
    "Gemüse": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/9f/Mixed_vegetables.jpg/330px-Mixed_vegetables.jpg",
    "Hülsenfrüchte": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/8b/Kidney_beans.jpg/330px-Kidney_beans.jpg",
    "Tomaten": "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/38/Tomato_sauce.jpg/330px-Tomato_sauce.jpg",
    "Eintopf": "https://upload.wikimedia.org/wikipedia/commons/7/71/Stew.jpg",
    "Fisch": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c3/Yellowfin_tuna.jpg/330px-Yellowfin_tuna.jpg",
    "Nusscreme": "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ea/Chocolate_spread.jpg/330px-Chocolate_spread.jpg",
    "Konfitüre": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/49/Strawberry_jam.jpg/330px-Strawberry_jam.jpg",
    "Margarine": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/5c/Margarine.jpg/330px-Margarine.jpg",
    "Limonade": "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ea/Cola.jpg/330px-Cola.jpg",
    "Wasser": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b1/Bottled_water.jpg/330px-Bottled_water.jpg",
    "Mate": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/05/Club-Mate.jpg/330px-Club-Mate.jpg",
    "Orangensaft": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f9/Orange_juice.jpg/330px-Orange_juice.jpg",
    "Apfelsaft": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c2/Apple_juice.jpg/330px-Apple_juice.jpg",
    "Mehrfruchtsaft": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f9/Orange_juice.jpg/330px-Orange_juice.jpg",
    "Kaffee": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a2/Coffee_beans.jpg/330px-Coffee_beans.jpg",
    "Tee": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c8/Tea_leaves.jpg/330px-Tea_leaves.jpg",
    "Schokolade": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/ac/Milk_chocolate.jpg/330px-Milk_chocolate.jpg",
    "Fruchtgummi": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/66/Gummy_bears.jpg/330px-Gummy_bears.jpg",
    "Riegel": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/cc/Chocolate_bar.jpg/330px-Chocolate_bar.jpg",
    "Pralinen": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/af/Chocolates.jpg/330px-Chocolates.jpg",
    "Chips": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/65/Potato_chips.jpg/330px-Potato_chips.jpg",
    "Nüsse": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/88/Peanuts.jpg/330px-Peanuts.jpg",
    "Gebäck": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/ac/Pretzel.jpg/330px-Pretzel.jpg",
    "Pizza": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/bd/Pizza_Margherita.jpg/330px-Pizza_Margherita.jpg",
    "Kartoffelprodukte": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/42/French_fries.jpg/330px-French_fries.jpg",
    "Kuchen": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/95/Strawberry_cake.jpg/330px-Strawberry_cake.jpg",
    "Suppen": "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ed/Soup.jpg/330px-Soup.jpg",
    "Nudelgerichte": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d4/Pasta.jpg/330px-Pasta.jpg",
    "Reisgerichte": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/50/Fried_rice.jpg/330px-Fried_rice.jpg",
    "Öl": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/Olive_oil.jpg/330px-Olive_oil.jpg",
    "Essig": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/03/Vinegar.jpg/330px-Vinegar.jpg",
    "Mayonnaise": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/79/Homemade_mayonnaise.jpg/330px-Homemade_mayonnaise.jpg",
    "Ketchup": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/bd/Ketchup.jpg/330px-Ketchup.jpg",
    "Würze": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b3/Seasoning.jpg/330px-Seasoning.jpg",
    "Saucen": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/26/Gravy.jpg/330px-Gravy.jpg",
    "Senf": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/66/Dijon_mustard.jpg/330px-Dijon_mustard.jpg",
    "Cornflakes": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c0/Cornflakes.jpg/330px-Cornflakes.jpg",
    "Müsli": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c0/Muesli.jpg/330px-Muesli.jpg",
    "Haferflocken": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/Rolled_oats.jpg/330px-Rolled_oats.jpg",
    "Zucker": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/47/Sugar.jpg/330px-Sugar.jpg",
    "Mehl": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a9/Flour.jpg/330px-Flour.jpg",
    "Pudding": "https://upload.wikimedia.org/wikipedia/commons/7/79/Chocolate_pudding.jpg",
    "Backtriebmittel": "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/3a/Baking_soda.jpg/330px-Baking_soda.jpg",
    "Eier": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/78/Chicken_egg.jpg/330px-Chicken_egg.jpg",
    "Panade": "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e2/Bread_crumbs.jpg/330px-Bread_crumbs.jpg",
    "Vanilleeis": "https://thumb.wikimedia.org/wikipedia/commons/thumb/1/1a/Vanilla_ice_cream.jpg/330px-Vanilla_ice_cream.jpg",
    "Eisriegel": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/59/Popsicle.jpg/330px-Popsicle.jpg",
    "Mehrsorte": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/86/Ice_cream_cone.jpg/330px-Ice_cream_cone.jpg",
    "Eisbecher": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/86/Ice_cream_cone.jpg/330px-Ice_cream_cone.jpg",
}


def nutrition(item, index):
    return json.dumps(
        {
            "energie_kcal": 80 + (index % 17) * 12,
            "fett_g": round(1 + (index % 9) * 0.8, 1),
            "zucker_g": round(0.5 + (index % 11) * 0.7, 1),
            "salz_g": round(0.02 + (index % 5) * 0.08, 2),
            "hinweis": item["main_category"],
        },
        ensure_ascii=False,
    )


# Marke, Hersteller. Jede Marke kombiniert mit jedem Eintrag aus AREA_KINDS.
AREA_BRANDS = (
    ("Lechtaler", "Lechtaler Nahrung"),
    ("Wertachhof", "Wertachhof GmbH"),
    ("Bergmühle", "Bergmühle Augsburg"),
    ("Auenland", "Auenland Lebensmittel"),
    ("Schwabenkorn", "Schwabenkorn KG"),
    ("Lechgold", "Lechgold GmbH"),
    ("Almhof", "Almhof Schwaben"),
    ("Kornkammer", "Kornkammer eG"),
    ("Riedmarkt", "Riedmarkt GmbH"),
    ("Schmuttertal", "Schmuttertal Nahrung"),
    ("Lechquelle", "Lechquelle GmbH"),
    ("Holzbach", "Holzbach Lebensmittel"),
    ("Singold", "Singold KG"),
    ("Gennach", "Gennach Naturkost"),
    ("Paartal", "Paartal GmbH"),
    ("Zusamtal", "Zusamtal Nahrung"),
    ("Mindeltal", "Mindeltal eG"),
    ("Kammeltal", "Kammeltal GmbH"),
    ("Günztal", "Günztal Lebensmittel"),
    ("Rothsee", "Rothsee KG"),
    ("Lechauen", "Lechauen GmbH"),
    ("Wittelsbacher", "Wittelsbacher Nahrung"),
    ("Schmutterhof", "Schmutterhof GmbH"),
    ("Wertachgold", "Wertachgold eG"),
    ("Filstal", "Filstal Lebensmittel"),
)

# Oberkategorie, Unterkategorie, Warengruppe, Menge, Einheit, Packung, Pfand,
# Nutri-Score, Allergene, Tags, Preis, Zutaten. Keine Milch, damit die
# bestehenden Augsburger Milchtreffer im 10-km-Umkreis gleich bleiben.
AREA_KINDS = (
    ("Molkereiprodukte", "Joghurt", "WG-201", 500, "g", "Becher", 0, "B", "Milch", "vegetarisch", 0.89, "Milch, Milchsäurekulturen"),
    ("Molkereiprodukte", "Käse", "WG-202", 200, "g", "Folie", 0, "C", "Milch", "vegetarisch", 2.19, "Milch, Salz, Lab"),
    ("Molkereiprodukte", "Butter", "WG-203", 250, "g", "Folie", 0, "D", "Milch", "vegetarisch", 1.89, "Sahne, Salz"),
    ("Molkereiprodukte", "Quark", "WG-204", 500, "g", "Becher", 0, "A", "Milch", "vegetarisch", 0.99, "Milch"),
    ("Brot und Backwaren", "Mischbrot", "WG-211", 500, "g", "Beutel", 0, "A", "Gluten", "vegan", 1.49, "Roggen, Weizen, Wasser, Salz"),
    ("Brot und Backwaren", "Toast", "WG-212", 500, "g", "Beutel", 0, "B", "Gluten", "vegetarisch", 1.29, "Weizen, Wasser, Hefe"),
    ("Brot und Backwaren", "Vollkornbrot", "WG-213", 500, "g", "Beutel", 0, "A", "Gluten", "vegan", 1.79, "Vollkorn, Wasser, Salz"),
    ("Brot und Backwaren", "Brötchen", "WG-214", 6, "Stück", "Beutel", 0, "B", "Gluten", "vegan", 1.19, "Weizen, Wasser, Hefe"),
    ("Obst", "Bananen", "WG-221", 1, "kg", "lose", 0, "A", "", "vegan", 1.49, "Bananen"),
    ("Obst", "Äpfel", "WG-222", 1, "kg", "lose", 0, "A", "", "vegan", 1.99, "Äpfel"),
    ("Obst", "Beeren", "WG-223", 250, "g", "Schale", 0, "A", "", "vegan", 2.49, "Erdbeeren"),
    ("Obst", "Trauben", "WG-224", 500, "g", "Schale", 0, "A", "", "vegan", 2.29, "Trauben"),
    ("Gemüse", "Wurzelgemüse", "WG-231", 1, "kg", "Beutel", 0, "A", "", "vegan", 1.29, "Möhren"),
    ("Gemüse", "Salat", "WG-232", 1, "Stück", "lose", 0, "A", "", "vegan", 1.09, "Eisbergsalat"),
    ("Gemüse", "Fruchtgemüse", "WG-233", 1, "Stück", "lose", 0, "A", "", "vegan", 0.79, "Gurke"),
    ("Gemüse", "Pilze", "WG-234", 250, "g", "Schale", 0, "A", "", "vegan", 1.59, "Champignons"),
    ("Fleisch", "Hackfleisch", "WG-241", 400, "g", "Schale", 0, "D", "", "", 3.49, "Rinderhackfleisch"),
    ("Fleisch", "Geflügel", "WG-242", 400, "g", "Schale", 0, "B", "", "", 4.29, "Hähnchenbrust"),
    ("Fleisch", "Schwein", "WG-243", 400, "g", "Schale", 0, "D", "", "", 3.99, "Schweineschnitzel"),
    ("Fleisch", "Rind", "WG-244", 300, "g", "Schale", 0, "C", "", "", 5.49, "Rindersteak"),
    ("Wurst", "Brühwurst", "WG-251", 200, "g", "Folie", 0, "D", "", "", 1.99, "Fleisch, Salz, Gewürze"),
    ("Wurst", "Schinken", "WG-252", 150, "g", "Folie", 0, "C", "", "", 2.49, "Schweineschinken, Salz"),
    ("Nudeln und Reis", "Nudeln", "WG-261", 500, "g", "Beutel", 0, "A", "Gluten", "vegan", 0.99, "Hartweizengrieß"),
    ("Nudeln und Reis", "Reis", "WG-262", 500, "g", "Beutel", 0, "A", "", "vegan", 1.49, "Langkornreis"),
    ("Säfte", "Apfelsaft", "WG-271", 1, "l", "Glas", 1, "C", "", "vegan", 1.39, "Apfelsaft"),
    ("Säfte", "Orangensaft", "WG-272", 1, "l", "Glas", 1, "C", "", "vegan", 1.59, "Orangensaft"),
    ("Getränke", "Wasser", "WG-273", 1.5, "l", "PET", 1, "A", "", "vegan", 0.39, "Wasser"),
    ("Getränke", "Limonade", "WG-274", 1, "l", "PET", 1, "E", "", "vegan", 0.99, "Wasser, Zucker, Aroma"),
    ("Frühstückscerealien", "Haferflocken", "WG-281", 500, "g", "Beutel", 0, "A", "Gluten", "vegan", 0.99, "Hafer"),
    ("Frühstückscerealien", "Müsli", "WG-282", 500, "g", "Beutel", 0, "B", "Gluten, Nüsse", "vegetarisch", 2.29, "Hafer, Nüsse, Rosinen"),
    ("Snacks", "Chips", "WG-291", 175, "g", "Beutel", 0, "D", "", "vegan", 1.49, "Kartoffeln, Öl, Salz"),
    ("Snacks", "Nüsse", "WG-292", 200, "g", "Beutel", 0, "B", "Nüsse", "vegan", 2.19, "Erdnüsse, Salz"),
    ("Süßwaren", "Schokolade", "WG-301", 100, "g", "Folie", 0, "E", "Milch", "vegetarisch", 1.19, "Zucker, Kakaomasse, Milch"),
    ("Soßen", "Ketchup", "WG-311", 500, "ml", "Flasche", 0, "D", "", "vegan", 1.29, "Tomaten, Essig, Zucker"),
    ("Öl und Essig", "Öl", "WG-321", 500, "ml", "Glas", 0, "C", "", "vegan", 3.49, "Olivenöl"),
    ("Backzutaten", "Eier", "WG-331", 10, "Stück", "Karton", 0, "A", "Ei", "vegetarisch", 2.29, "Hühnereier"),
)


def area_stores():
    result = []
    for index, (postal_code, street, district, _north, _east) in enumerate(AUGSBURG_AREA_STORES):
        slug, name = CHAINS[index % len(CHAINS)]
        result.append(
            {
                "supermarket_name": name,
                "store_id": f"{slug}-augsburg-{district}".lower().replace(" ", "-").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss"),
                "store_address": f"{street}, {postal_code} Augsburg-{district}",
            }
        )
    return result


def area_catalog(existing_names):
    products = []
    for brand_index, (brand, manufacturer) in enumerate(AREA_BRANDS):
        organic = brand_index % 5 == 0
        for kind in AREA_KINDS:
            main, sub, group, qty, unit, pack, deposit, score, allergens, tags, price, ingredients = kind
            stem = f"Bio-{sub}" if organic else sub
            item = {
                "main_category": main,
                "sub_category": sub,
                "internal_commodity_group": group,
                "net_quantity": qty,
                "unit": unit,
                "packaging_type": pack,
                "is_deposit_required": deposit,
                "nutriscore": score,
                "allergens": allergens,
                "dietary_tags": tags,
                "regular_price": price,
                "ingredients_list": ingredients,
                "brand": brand,
                "manufacturer": manufacturer,
                "product_name": f"{brand} {stem}",
            }
            item["is_organic"] = int("bio" in item["product_name"].casefold())
            if item["sub_category"].casefold() == item["main_category"].casefold():
                raise ValueError(f"Unterkategorie gleich Kategorie: {item['product_name']}")
            if sub not in IMAGE_URLS:
                raise ValueError(f"Kein Bild für Unterkategorie {sub}")
            products.append(item)
    if len(products) != 900:
        raise ValueError(f"Erwartet 900 Umlandprodukte, gefunden {len(products)}")
    names = [item["product_name"].casefold() for item in products]
    if len(names) != len(set(names)):
        raise ValueError("Umland-Produktnamen sind nicht eindeutig")
    overlap = set(names) & {name.casefold() for name in existing_names}
    if overlap:
        raise ValueError(f"Umland-Namen schon vergeben: {sorted(overlap)[:5]}")
    return products


# Kurzer Satz je Unterkategorie und die dazugehörigen Zusatzstoffe.
# Leere Liste bedeutet: keine Konservierungs- oder Zusatzstoffe.
PRODUCT_NOTES = {
    "Milch": ("Trinkmilch zum direkten Verzehr.", []),
    "Joghurt": ("Joghurt aus Milch und Milchsäurekulturen.", []),
    "Käse": ("Schnitt- oder Weichkäse aus Milch, Salz und Lab.", []),
    "Butter": ("Butter aus Sahne.", []),
    "Sahne": ("Sahne zum Kochen oder Aufschlagen.", []),
    "Quark": ("Speisequark aus Milch.", []),
    "Mischbrot": ("Mischbrot aus Roggen und Weizen.", []),
    "Toast": ("Weizentoast zum Aufbacken oder Rösten.", []),
    "Vollkornbrot": ("Vollkornbrot aus dem vollen Korn.", []),
    "Brötchen": ("Weizenbrötchen.", []),
    "Bananen": ("Frische Bananen, ungeschält.", []),
    "Äpfel": ("Frische Tafeläpfel.", []),
    "Zitrusfrüchte": ("Frische Zitrusfrüchte.", []),
    "Beeren": ("Frische Beeren.", []),
    "Exoten": ("Frisches exotisches Obst.", []),
    "Trauben": ("Frische Tafeltrauben.", []),
    "Wurzelgemüse": ("Frisches Wurzelgemüse.", []),
    "Salat": ("Frischer Blattsalat.", []),
    "Fruchtgemüse": ("Frisches Fruchtgemüse.", []),
    "Pilze": ("Frische Speisepilze.", []),
    "Hackfleisch": ("Rohes Hackfleisch zum Braten.", []),
    "Geflügel": ("Rohes Geflügelfleisch.", []),
    "Schwein": ("Rohes Schweinefleisch.", []),
    "Rind": ("Rohes Rindfleisch.", []),
    "Brühwurst": ("Brühwurst aus Fleisch und Gewürzen.", ["Natriumnitrit (E 250, Konservierungsstoff)", "Ascorbinsäure (E 300, Antioxidationsmittel)"]),
    "Würstchen": ("Brühwürstchen.", ["Natriumnitrit (E 250, Konservierungsstoff)", "Ascorbinsäure (E 300, Antioxidationsmittel)"]),
    "Schinken": ("Gepökelter Schinken.", ["Natriumnitrit (E 250, Konservierungsstoff)", "Ascorbinsäure (E 300, Antioxidationsmittel)"]),
    "Geflügelwurst": ("Brühwurst aus Geflügelfleisch.", ["Natriumnitrit (E 250, Konservierungsstoff)", "Ascorbinsäure (E 300, Antioxidationsmittel)"]),
    "Rohwurst": ("Luftgetrocknete Rohwurst.", ["Natriumnitrit (E 250, Konservierungsstoff)", "Ascorbinsäure (E 300, Antioxidationsmittel)"]),
    "Streichwurst": ("Streichfähige Wurst.", ["Natriumnitrit (E 250, Konservierungsstoff)", "Ascorbinsäure (E 300, Antioxidationsmittel)"]),
    "Fischstäbchen": ("Panierte Fischstäbchen, tiefgekühlt.", ["Aroma"]),
    "Räucherfisch": ("Geräucherter Fisch.", []),
    "Hering": ("Heringsfilet.", []),
    "Seelachs": ("Seelachsfilet.", []),
    "Backfisch": ("Panierter Backfisch.", ["Aroma"]),
    "Lachs": ("Lachsfilet.", []),
    "Thunfisch": ("Thunfischfilet.", []),
    "Fisch": ("Fisch, gegart oder in Öl eingelegt.", []),
    "Nudeln": ("Getrocknete Hartweizennudeln.", []),
    "Reis": ("Getrockneter Reis.", []),
    "Gemüse": ("Gemüse als Konserve oder Tiefkühlware.", []),
    "Hülsenfrüchte": ("Hülsenfrüchte in der Dose.", []),
    "Tomaten": ("Tomaten, passiert oder stückig.", []),
    "Eintopf": ("Fertiger Eintopf zum Erwärmen.", ["Mononatriumglutamat (E 621, Geschmacksverstärker)", "Aroma"]),
    "Nusscreme": ("Süßer Brotaufstrich mit Nüssen und Kakao.", ["Lecithine (E 322, Emulgator)", "Aroma"]),
    "Konfitüre": ("Fruchtaufstrich mit Zucker gekocht.", ["Pektine (E 440, Geliermittel)", "Citronensäure (E 330, Säuerungsmittel)", "Kaliumsorbat (E 202, Konservierungsstoff)"]),
    "Margarine": ("Streichfett aus pflanzlichen Ölen.", ["Lecithine (E 322, Emulgator)", "Carotin (E 160a, Farbstoff)", "Aroma"]),
    "Limonade": ("Erfrischungsgetränk mit Zucker.", ["Citronensäure (E 330, Säuerungsmittel)", "Natriumbenzoat (E 211, Konservierungsstoff)", "Aroma"]),
    "Wasser": ("Mineralwasser.", []),
    "Mate": ("Mate-Erfrischungsgetränk.", ["Citronensäure (E 330, Säuerungsmittel)", "Zuckerkulör (E 150d, Farbstoff)", "Aroma"]),
    "Apfelsaft": ("Apfelsaft aus Frucht.", []),
    "Orangensaft": ("Orangensaft aus Frucht.", []),
    "Mehrfruchtsaft": ("Saft aus mehreren Früchten.", []),
    "Kaffee": ("Gerösteter Bohnenkaffee.", []),
    "Tee": ("Getrockneter Tee.", []),
    "Schokolade": ("Tafelschokolade.", ["Lecithine (E 322, Emulgator)", "Aroma"]),
    "Fruchtgummi": ("Weiches Fruchtgummi.", ["Citronensäure (E 330, Säuerungsmittel)", "Carotin (E 160a, Farbstoff)", "Aroma"]),
    "Riegel": ("Süßer Riegel.", ["Lecithine (E 322, Emulgator)", "Aroma"]),
    "Pralinen": ("Gefüllte Pralinen.", ["Lecithine (E 322, Emulgator)", "Aroma"]),
    "Chips": ("Gesalzene Kartoffelchips.", ["Aroma", "Rosmarinextrakt (E 392, Antioxidationsmittel)"]),
    "Nüsse": ("Geröstete Nüsse.", []),
    "Gebäck": ("Salziges Knabbergebäck.", ["Aroma"]),
    "Pizza": ("Tiefkühlpizza.", ["Mononatriumglutamat (E 621, Geschmacksverstärker)", "Aroma"]),
    "Kuchen": ("Tiefgekühlter Kuchen.", ["Mono- und Diglyceride von Speisefettsäuren (E 471, Emulgator)", "Aroma"]),
    "Kartoffelprodukte": ("Tiefgekühlte Kartoffelprodukte.", []),
    "Suppen": ("Instant-Suppe zum Anrühren.", ["Mononatriumglutamat (E 621, Geschmacksverstärker)", "Aroma"]),
    "Nudelgerichte": ("Fertiges Nudelgericht zum Erwärmen.", ["Mononatriumglutamat (E 621, Geschmacksverstärker)", "Aroma"]),
    "Reisgerichte": ("Fertiges Reisgericht zum Erwärmen.", ["Mononatriumglutamat (E 621, Geschmacksverstärker)", "Aroma"]),
    "Öl": ("Speiseöl zum Braten und für Salat.", []),
    "Essig": ("Speiseessig.", []),
    "Mayonnaise": ("Mayonnaise aus Öl und Eigelb.", ["Kaliumsorbat (E 202, Konservierungsstoff)", "Citronensäure (E 330, Säuerungsmittel)"]),
    "Ketchup": ("Tomatenketchup.", ["Kaliumsorbat (E 202, Konservierungsstoff)", "Citronensäure (E 330, Säuerungsmittel)"]),
    "Würze": ("Flüssige Speisewürze.", ["Mononatriumglutamat (E 621, Geschmacksverstärker)"]),
    "Saucen": ("Gebundene Sauce.", ["Kaliumsorbat (E 202, Konservierungsstoff)", "Aroma"]),
    "Senf": ("Mittelscharfer Senf.", ["Kaliumsorbat (E 202, Konservierungsstoff)", "Citronensäure (E 330, Säuerungsmittel)"]),
    "Cornflakes": ("Knusprige Maisflakes.", ["Aroma"]),
    "Müsli": ("Müsli aus Getreideflocken.", ["Aroma"]),
    "Haferflocken": ("Zarte Haferflocken.", []),
    "Zucker": ("Weißer Haushaltszucker.", []),
    "Mehl": ("Weizenmehl zum Backen.", []),
    "Pudding": ("Puddingpulver zum Kochen.", ["Aroma", "Carotin (E 160a, Farbstoff)"]),
    "Backtriebmittel": ("Backpulver oder Hefe als Triebmittel.", ["Dinatriumdiphosphat (E 450, Säureregulator)"]),
    "Eier": ("Frische Hühnereier.", []),
    "Panade": ("Paniermehl aus getrocknetem Brot.", []),
    "Vanilleeis": ("Vanilleeis zum Tiefkühlen.", ["Carrageen (E 407, Stabilisator)", "Johannisbrotkernmehl (E 410, Stabilisator)", "Aroma"]),
    "Eisriegel": ("Eisriegel am Stiel.", ["Carrageen (E 407, Stabilisator)", "Johannisbrotkernmehl (E 410, Stabilisator)", "Aroma"]),
    "Mehrsorte": ("Eis mit mehreren Sorten.", ["Carrageen (E 407, Stabilisator)", "Johannisbrotkernmehl (E 410, Stabilisator)", "Aroma"]),
    "Eisbecher": ("Eis im Becher.", ["Carrageen (E 407, Stabilisator)", "Johannisbrotkernmehl (E 410, Stabilisator)", "Aroma"]),
}


def product_text(item):
    sentence, additives = PRODUCT_NOTES[item["sub_category"]]
    if item["sub_category"] == "Backtriebmittel" and "hefe" in item["product_name"].casefold():
        sentence, additives = "Frische Backhefe.", []
    description = (
        f"{item['product_name']} von {item['brand']}. {sentence} "
        f"Inhalt {item['net_quantity']:g} {item['unit']}, Verpackung {item['packaging_type']}."
    )
    return description, json.dumps(additives, ensure_ascii=False)


def product_record(index, item, location, image):
    offer = OFFERS[index % len(OFFERS)]
    regular = round(item["regular_price"] + (index % 4) * 0.1, 2)
    current = round(regular * OFFER_FACTOR[offer], 2)
    if not str(image).startswith("https://"):
        raise ValueError(f"Kein Bildlink für {item['product_name']}")
    description, additives = product_text(item)
    return {
        "id": index + 1,
        "gtin_ean": f"{4000000000000 + index + 1:013d}",
        "product_name": item["product_name"],
        "brand": item["brand"],
        "manufacturer": item["manufacturer"],
        "main_category": item["main_category"],
        "sub_category": item["sub_category"],
        "internal_commodity_group": item["internal_commodity_group"],
        "net_quantity": item["net_quantity"],
        "unit": item["unit"],
        "packaging_type": item["packaging_type"],
        "is_deposit_required": item["is_deposit_required"],
        "deposit_value": 0.25 if item["is_deposit_required"] else 0,
        "supermarket_name": location["supermarket_name"],
        "store_id": location["store_id"],
        "store_address": location["store_address"],
        "current_price": current,
        "calculated_base_price": base_price(current, item["net_quantity"], item["unit"]),
        "special_pricing": offer,
        "regular_price": regular,
        "last_updated": "2026-10-20T08:00:00+02:00",
        "nutriscore": item["nutriscore"],
        "ingredients_list": item["ingredients_list"],
        "allergens": item["allergens"],
        "dietary_tags": item["dietary_tags"],
        "is_organic": item["is_organic"],
        "nutrition_per_100g": nutrition(item, index),
        "image_url": image,
        "description": description,
        "additives": additives,
    }


def rows():
    locations = stores()
    images = json.loads((DATA / "product_images.json").read_text(encoding="utf-8"))["products"]
    base_items = catalog()
    result = []
    for index, item in enumerate(base_items):
        result.append(product_record(index, item, locations[index % len(locations)], images[item["product_name"]]))
    surroundings = area_stores()
    for offset, item in enumerate(area_catalog([item["product_name"] for item in base_items])):
        index = len(result)
        result.append(product_record(index, item, surroundings[offset % len(surroundings)], IMAGE_URLS[item["sub_category"]]))
    if len(result) != 1100:
        raise ValueError(f"Erwartet 1100 Produkte, gefunden {len(result)}")
    return result


def create_database():
    columns = [
        "id",
        "gtin_ean",
        "product_name",
        "brand",
        "manufacturer",
        "main_category",
        "sub_category",
        "internal_commodity_group",
        "net_quantity",
        "unit",
        "packaging_type",
        "is_deposit_required",
        "deposit_value",
        "supermarket_name",
        "store_id",
        "store_address",
        "current_price",
        "calculated_base_price",
        "special_pricing",
        "regular_price",
        "last_updated",
        "nutriscore",
        "ingredients_list",
        "allergens",
        "dietary_tags",
        "is_organic",
        "nutrition_per_100g",
        "image_url",
        "description",
        "additives",
    ]
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.execute("DROP TABLE IF EXISTS grocery_product")
        connection.execute(
            """
            CREATE TABLE grocery_product (
                id INTEGER PRIMARY KEY,
                gtin_ean TEXT NOT NULL,
                product_name TEXT NOT NULL,
                brand TEXT NOT NULL,
                manufacturer TEXT NOT NULL,
                main_category TEXT NOT NULL,
                sub_category TEXT NOT NULL,
                internal_commodity_group TEXT NOT NULL,
                net_quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                packaging_type TEXT NOT NULL,
                is_deposit_required INTEGER NOT NULL,
                deposit_value REAL NOT NULL,
                supermarket_name TEXT NOT NULL,
                store_id TEXT NOT NULL,
                store_address TEXT NOT NULL,
                current_price REAL NOT NULL,
                calculated_base_price REAL NOT NULL,
                special_pricing TEXT NOT NULL,
                regular_price REAL NOT NULL,
                last_updated TEXT NOT NULL,
                nutriscore TEXT NOT NULL,
                ingredients_list TEXT NOT NULL,
                allergens TEXT NOT NULL,
                dietary_tags TEXT NOT NULL,
                is_organic INTEGER NOT NULL,
                nutrition_per_100g TEXT NOT NULL,
                image_url TEXT NOT NULL,
                description TEXT NOT NULL,
                additives TEXT NOT NULL
            )
            """
        )
        placeholders = ", ".join("?" for _ in columns)
        connection.executemany(
            f"INSERT INTO grocery_product ({', '.join(columns)}) VALUES ({placeholders})",
            [tuple(row[column] for column in columns) for row in rows()],
        )
        connection.execute("CREATE INDEX idx_grocery_name ON grocery_product(product_name)")
        connection.execute("CREATE INDEX idx_grocery_store ON grocery_product(supermarket_name)")
        connection.execute("CREATE INDEX idx_grocery_address ON grocery_product(store_address)")
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    create_database()
    print(f"{DB_PATH} mit {len(rows())} Produkten geschrieben")
