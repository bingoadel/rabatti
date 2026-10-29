"""Schreibt data/german_places.json im Stil eines Routenplaners.

Download, falls die Dateien fehlen:
https://download.geonames.org/export/zip/DE.zip als geonames-postal.zip
https://download.geonames.org/export/dump/DE.zip als geonames-places.zip

Jeder Eintrag lautet „PLZ Ort“, zum Beispiel „86150 Augsburg“ oder
„78141 Schönwald im Schwarzwald“. Orte ohne eigene Postleitzahl bleiben
über den Namen auffindbar, bei doppeltem Namen mit Bundesland.
Quelle: GeoNames, CC BY 4.0.
"""

import json
import math
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

KEEP = {
    "PPL",
    "PPLA",
    "PPLA2",
    "PPLA3",
    "PPLA4",
    "PPLA5",
    "PPLC",
    "PPLL",
    "PPLF",
    "PPLR",
    "PPLS",
}

STATES = {
    "01": "Baden-Württemberg",
    "02": "Bayern",
    "03": "Bremen",
    "04": "Hamburg",
    "05": "Hessen",
    "06": "Niedersachsen",
    "07": "Nordrhein-Westfalen",
    "08": "Rheinland-Pfalz",
    "09": "Saarland",
    "10": "Schleswig-Holstein",
    "11": "Brandenburg",
    "12": "Mecklenburg-Vorpommern",
    "13": "Sachsen",
    "14": "Sachsen-Anhalt",
    "15": "Thüringen",
    "16": "Berlin",
}

DATA = Path(__file__).resolve().parent.parent / "data"
SAME_PLACE_KM = 8


def fold(value):
    return (
        value.casefold()
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )


def distance_km(lat1, lon1, lat2, lon2):
    earth = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlng = math.radians(lon2 - lon1)
    chord = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlng / 2) ** 2
    return 2 * earth * math.asin(math.sqrt(min(1, chord)))


def download(url, target):
    if target.exists():
        return
    urllib.request.urlretrieve(url, target)


def load_postal(zip_path):
    rows = []
    labels = []
    seen = set()
    with zipfile.ZipFile(zip_path) as archive:
        for line in archive.read("DE.txt").decode("utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) < 11 or parts[0] != "DE":
                continue
            plz = parts[1].strip()
            name = parts[2].strip()
            if len(plz) != 5 or not plz.isdigit() or not name:
                continue
            label = f"{plz} {name}"
            if label in seen:
                continue
            seen.add(label)
            labels.append(label)
            rows.append(
                {
                    "plz": plz,
                    "name": name,
                    "lat": float(parts[9]),
                    "lon": float(parts[10]),
                }
            )
    return labels, rows


def load_places(zip_path):
    places = []
    with zipfile.ZipFile(zip_path) as archive:
        for line in archive.read("DE.txt").decode("utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) < 11 or parts[6] != "P" or parts[7] not in KEEP or parts[8] != "DE":
                continue
            name = parts[1].strip()
            if not name:
                continue
            places.append(
                {
                    "name": name,
                    "lat": float(parts[4]),
                    "lon": float(parts[5]),
                    "state": STATES.get(parts[10], ""),
                }
            )
    return places


def covered(place, postal_by_token):
    token = fold(place["name"]).split(" ", 1)[0]
    place_name = fold(place["name"])
    for row in postal_by_token.get(token, []):
        postal_name = fold(row["name"])
        related = (
            postal_name == place_name
            or postal_name.startswith(place_name + " ")
            or place_name.startswith(postal_name + " ")
        )
        if not related:
            continue
        if distance_km(place["lat"], place["lon"], row["lat"], row["lon"]) <= SAME_PLACE_KM:
            return True
    return False


def extra_labels(places, postal_rows, labels):
    postal_by_token = defaultdict(list)
    for row in postal_rows:
        postal_by_token[fold(row["name"]).split(" ", 1)[0]].append(row)
    used = {fold(label.split(" ", 1)[1]) if label[:5].isdigit() else fold(label) for label in labels}
    extras = []
    seen_places = set()
    for place in places:
        if covered(place, postal_by_token):
            continue
        key = (fold(place["name"]), place["state"])
        if key in seen_places:
            continue
        seen_places.add(key)
        name_key = fold(place["name"])
        if name_key in used or place["state"] == "":
            text = f"{place['name']}, {place['state']}" if place["state"] else place["name"]
        else:
            text = place["name"]
            used.add(name_key)
        extras.append(text)
    return extras


def locality_key(label):
    if len(label) > 6 and label[:5].isdigit() and label[5] == " ":
        return fold(label[6:])
    if ", " in label:
        return fold(label.split(", ", 1)[0])
    return fold(label)


def main():
    download("https://download.geonames.org/export/zip/DE.zip", DATA / "geonames-postal.zip")
    download("https://download.geonames.org/export/dump/DE.zip", DATA / "geonames-places.zip")
    labels, rows = load_postal(DATA / "geonames-postal.zip")
    labels.extend(extra_labels(load_places(DATA / "geonames-places.zip"), rows, labels))
    labels = sorted(set(labels), key=lambda label: (locality_key(label), label))
    if len(labels) < 10000 or "86154 Augsburg" not in labels:
        raise SystemExit(f"Ortssliste unvollständig: {len(labels)}")
    target = DATA / "german_places.json"
    target.write_text(json.dumps(labels, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{target} mit {len(labels)} Orten geschrieben")


if __name__ == "__main__":
    main()
