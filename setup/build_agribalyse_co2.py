"""Baut die kleine CO2-Tabelle aus den heruntergeladenen Agribalyse-Dateien.

Summary:
    Die Suche liest danach nur data/agribalyse_co2.json.
    Die großen Quelldateien bleiben außerhalb der Anfrage.
"""

import json
from pathlib import Path

import openpyxl

DATA = Path(__file__).resolve().parent.parent / "data"
SYNTHESIS = DATA / "agribalyse4-synthese.json"
BIO_XLSX = DATA / "agribalyse32-agri-bio.xlsx"
CONV_XLSX = DATA / "agribalyse32-agri-conv.xlsx"
OUT = DATA / "agribalyse_co2.json"

EXACT = {
    "milk_whole": "Lait entier, UHT",
    "milk_low": "Lait demi-écrémé, UHT",
    "yogurt": "Yaourt, lait fermenté ou spécialité laitière, nature",
    "quark": "Fromage blanc nature, 0% MG",
    "butter": "Beurre à 82% MG, doux",
    "butter_light": "Beurre à 39-41% MG, léger, doux",
    "margarine": "Matière grasse végétale (type margarine) à 80% MG, salé",
    "bread": "Pain, baguette, courante",
    "apple": "Pomme, pulpe et peau, crue",
    "banana": "Banane, pulpe, crue",
    "tomato": "Tomate, crue",
    "tomato_dried": "Tomate, séchée",
    "tomato_puree": "Tomate, purée, appertisée",
    "carrot": "Carotte, crue",
    "potato": "Pomme de terre, sans peau, crue",
    "lettuce": "Laitue, crue",
    "onion": "Oignon, cru",
    "berry": "Fruits rouges, crus (framboises, fraises, groseilles, cassis)",
    "chicken": "Poulet, filet, sans peau, cru",
    "turkey": "Dinde, escalope, crue",
    "beef": "Boeuf, steak ou bifteck, cru",
    "pork": "Porc, côte, crue",
    "lamb": "Agneau, côtelette, crue",
    "ham_cooked": "Jambon cuit, choix",
    "ham_raw": "Jambon cru",
    "merguez": "Merguez, boeuf et mouton, crue",
    "egg": "Oeuf, cru",
    "salmon": "Saumon, cru, élevage",
    "tuna": "Thon germon ou thon blanc, cru",
    "white_fish": "Cabillaud, cru",
    "pasta": "Pâtes sèches standard, crues",
    "pasta_egg": "Pâtes sèches, aux œufs, crues",
    "rice": "Riz blanc étuvé, cru",
    "oat": "Flocon d'avoine",
    "lentil": "Lentille blonde, sèche",
    "chickpea": "Pois chiche, appertisé, égoutté",
    "green_bean": "Haricot vert, cru",
    "coffee": "Café, moulu",
    "tea": "Thé infusé, non sucré",
    "water": "Eau embouteillée de source",
    "cola": "Cola, sucré",
    "apple_juice": "Jus de pomme, pur jus",
    "orange_juice": "Jus d'orange, à base de concentré",
    "sugar": "Sucre blanc",
    "chocolate": "Chocolat au lait, tablette",
    "honey": "Miel",
    "salt": "Sel blanc alimentaire, non iodé, non fluoré (marin, ignigène ou gemme)",
    "pepper": "Poivre noir, poudre",
    "mustard": "Moutarde",
    "ketchup": "Ketchup",
    "mayonnaise": "Mayonnaise (70% MG min.)",
    "flour": "Farine de blé tendre ou froment T55 (pour pains)",
    "rye_flour": "Farine de blé tendre ou froment T150",
    "coconut": "Lait de coco ou Crème de coco",
    "hummus": "Houmous",
    "pizza": "Pizza au fromage ou Pizza margherita",
    "olive_fruit": "Olives vertes, fourrées ou farcies (anchois, poivrons, etc.)",
    "wine": "Vin rouge",
    "beer": 'Bière "coeur de marché" (4-5° alcool)',
}

ALTERNATIVES = {
    "cheese": ["Emmental ou emmenthal", "Emmental"],
    "cream": ["Crème de lait, 30% MG, semi-épaisse, UHT"],
    "olive_oil": ["Huile d'olive vierge extra", "Huile d'olive vierge", "Huile d'olive"],
    "rape_oil": ["Huile de colza"],
    "sunflower_oil": ["Huile de tournesol"],
    "sesame_oil": ["Huile de sésame", "Huile de tournesol"],
    "orange": ["Orange, pulpe, crue", "Orange, pulpe et peau, crue"],
    "lemon": ["Citron, pulpe, cru", "Citron, pulpe, crue", "Citron, pulpe et zeste, cru"],
    "sausage": ["Saucisson sec, pur porc", "Saucisson sec pur porc"],
    "spinach": ["Épinard, cru", "Epinard, cru"],
    "pepper_veg": ["Poivron rouge, cru", "Poivron, rouge, cru", "Poivron vert, cru"],
}

FARM_PAIRS = {
    "chicken": (
        "Poulet, biologique, à la ferme, France",
        "Poulet, moyenne nationale, à la ferme, France",
    ),
    "beef": (
        "Boeuf, biologique, moyenne nationale, à la ferme, France",
        "Boeuf, moyenne nationale, à la ferme, France",
    ),
    "pork": (
        "Porc, biologique, moyenne nationale (50% intérieur, 50% extérieur), à la ferme, France",
        "Porc, conventionnel, moyenne nationale, à la ferme, France",
    ),
    "apple": (
        "Pomme, biologique, moyenne nationale, au verger, France",
        "Pomme conventionnelle, moyenne nationale, au verger, France",
    ),
}


def finished_rows():
    """Zeilen der Agribalyse-4-Synthese.

    Summary:
        Jede Zeile ist ein Fertigprodukt mit Code_CIQUAL und Klimawert je Kilogramm.
    """
    payload = json.loads(SYNTHESIS.read_text(encoding="utf-8"))
    return payload["results"]


def by_name(rows):
    """Nachschlagewerk der französischen Produktnamen.

    Summary:
        Doppelte Namen behalten die erste Zeile.
    """
    found = {}
    for row in rows:
        name = row.get("Nom_du_Produit_en_Français") or ""
        found.setdefault(name, row)
    return found


def choose(names, found):
    """Erste vorhandene Bezeichnung aus einer Kandidatenliste.

    Summary:
        Fehlt jede Bezeichnung, bricht der Bau ab, statt eine Zahl zu erfinden.
    """
    for name in names:
        if name in found:
            return found[name]
    raise SystemExit(f"keine Zeile für {names}")


def farm_sheet(path, sheet):
    """Hofwerte einer Agribalyse-3.2-Tabelle, Name und kg CO2-Äq.

    Summary:
        Die Klimaspalt liegt in der veröffentlichten Tabelle fest auf dem sechsten Feld.
    """
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    grid = book[sheet]
    values = {}
    for index, row in enumerate(grid.iter_rows(values_only=True)):
        if index < 3 or not row or not row[0] or row[5] is None:
            continue
        values[str(row[0])] = float(row[5])
    book.close()
    return values


def main():
    """Schreibt data/agribalyse_co2.json.

    Summary:
        Fertigproduktwerte kommen aus Agribalyse 4.
        Bio-Werte entstehen nur dort, wo ein Hofpaar aus Agribalyse 3.2 vorliegt.
    """
    found = by_name(finished_rows())
    anchors = {}
    for key, name in EXACT.items():
        row = choose([name], found)
        anchors[key] = _anchor(row)
    for key, names in ALTERNATIVES.items():
        row = choose(names, found)
        anchors[key] = _anchor(row)
    bio = farm_sheet(BIO_XLSX, "AGB 3.2 agricole biologique")
    conv = farm_sheet(CONV_XLSX, "AGB 3.2 agricole conventionnel")
    for key, (bio_name, conv_name) in FARM_PAIRS.items():
        organic_farm = bio[bio_name]
        conventional_farm = conv[conv_name]
        finished = anchors[key]["kg_co2e"]
        anchors[key]["organic"] = {
            "kg_co2e": round(finished * organic_farm / conventional_farm, 6),
            "farm_organic_name": bio_name,
            "farm_organic_kg": organic_farm,
            "farm_conventional_name": conv_name,
            "farm_conventional_kg": conventional_farm,
        }
    payload = {
        "attribution": "ADEME, AGRIBALYSE",
        "license": "Licence Ouverte Etalab 2.0",
        "consumer_title": "AGRIBALYSE 4 Synthese",
        "consumer_field": "Changement_climatique",
        "consumer_unit": "kg CO2-Äq. je kg Fertigprodukt",
        "consumer_updated": "2026-06-30",
        "farm_title": "AGRIBALYSE 3.2, 1 kg ab Hof",
        "farm_note": "Bio-Zahl = Fertigprodukt mal Bio-Hofwert geteilt durch den konventionellen Hofwert.",
        "anchors": anchors,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(anchors)} Anker -> {OUT.name}")


def _anchor(row):
    """Ein Fertigprodukt als Anker.

    Summary:
        Code, französischer Name und Kilogramm CO2-Äquivalent bleiben zusammen.
    """
    return {
        "ciqual": str(row["Code_CIQUAL"]),
        "name_fr": row["Nom_du_Produit_en_Français"],
        "kg_co2e": float(row["Changement_climatique"]),
    }


if __name__ == "__main__":
    main()
