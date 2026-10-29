"""Orte, Filialkoordinaten, Entfernung und Kartenausschnitt.

Summary:
    Deutsche Ortsnamen lösen die Suche auf.
    Jede Filiale bleibt an ihrem eigenen Punkt auf der Karte.
"""

import json
import math
from pathlib import Path

from models.product_labels import ProductLabels

FLAG_COLORS = {
    "Lidl": ("#0050aa", "#fff000"),
    "Aldi": ("#00005c", "#ffffff"),
    "Rewe": ("#cc0000", "#ffffff"),
    "Edeka": ("#ffd100", "#003399"),
    "Kaufland": ("#e10915", "#ffffff"),
    "Penny": ("#e30613", "#ffe100"),
    "Netto": ("#ffd000", "#d40000"),
    "Norma": ("#ffed00", "#111111"),
    "Marktkauf": ("#ffffff", "#15803d"),
    "Spar": ("#e30613", "#ffffff"),
    "real": ("#e30613", "#ffffff"),
    "Globus": ("#e30613", "#ffed00"),
}

CITY_CENTERS = {
    "augsburg": (48.3705, 10.8978),
    "muenchen": (48.1372, 11.5755),
    "berlin": (52.5200, 13.4050),
    "hamburg": (53.5511, 9.9937),
    "koeln": (50.9375, 6.9603),
    "stuttgart": (48.7758, 9.1829),
    "nuernberg": (49.4521, 11.0767),
    "plochingen": (48.7106, 9.4194),
}

# Nord/Ost-Versatz in Kilometern, damit der Umkreis Filialen unterscheidet.
# Fiktive Filialen im Umkreis von 50 km: postal, Straße, Ort, Nord-km, Ost-km.
AUGSBURG_AREA_STORES = (
    ("86368", "Augsburger Straße 4", "Gersthofen", 6.2, 1.5),
    ("86391", "Ulrichstraße 10", "Stadtbergen", -1.5, -4.2),
    ("86356", "Bürgermeister-Wohlfarth-Straße 8", "Neusäß", 1.2, -5.5),
    ("86343", "Königsallee 20", "Königsbrunn", -8.5, -2.0),
    ("86316", "Augsburger Straße 15", "Friedberg", 2.5, 6.5),
    ("86420", "Augsburger Straße 30", "Diedorf", 2.0, -12.0),
    ("86399", "Wertachstraße 12", "Bobingen", -12.5, -3.0),
    ("86415", "Kirchbergstraße 6", "Mering", -4.0, 14.0),
    ("86405", "Hauptstraße 18", "Meitingen", 17.0, 3.0),
    ("86830", "Fuggerstraße 9", "Schwabmünchen", -20.0, -4.0),
    ("86551", "Stadtplatz 3", "Aichach", 8.0, 22.0),
    ("86441", "Augsburger Straße 22", "Zusmarshausen", 6.0, -20.0),
    ("86637", "Augsburger Straße 5", "Wertingen", 28.0, 2.0),
    ("86424", "Augsburger Straße 11", "Dinkelscherben", -8.0, -22.0),
    ("86836", "Augsburger Straße 40", "Klosterlechfeld", -16.0, 6.0),
    ("86438", "Kissinger Straße 7", "Kissing", -2.0, 12.5),
    ("86381", "Augsburger Straße 2", "Krumbach", -38.0, -18.0),
    ("86609", "Hauptstraße 14", "Donauwörth", 32.0, 22.0),
    ("86899", "Augsburger Straße 8", "Landsberg", -28.0, -32.0),
    ("86529", "Schrobenhausener Straße 16", "Schrobenhausen", 18.0, 32.0),
    ("86641", "Augsburger Straße 19", "Rain", 30.0, 18.0),
    ("89312", "Augsburger Straße 6", "Günzburg", 12.0, -32.0),
    ("86470", "Augsburger Straße 25", "Thannhausen", -22.0, -24.0),
    ("87719", "Augsburger Straße 3", "Mindelheim", -36.0, -12.0),
)

DISTRICT_OFFSETS_KM = {
    "Augsburg-Oberhausen": (2.0, 0.5),
    "Augsburg-Pfersee": (0.4, -3.0),
    "Augsburg-Innenstadt": (0.3, 0.2),
    "Augsburg-Lechhausen": (1.0, 3.5),
    "Augsburg-Göggingen": (-6.0, -1.0),
    "Augsburg-Haunstetten": (-8.0, 0.5),
    **{f"Augsburg-{district}": (north, east) for _postal, _street, district, north, east in AUGSBURG_AREA_STORES},
}

class StoreLocations:
    """Orte, Filialkoordinaten, Entfernung und Kartenausschnitt.

    Summary:
        Deutsche Ortsnamen lösen die Suche auf.
        Jede Filiale bleibt an ihrem eigenen Punkt auf der Karte.
    """

    _german_places = None

    @staticmethod
    def district_name(address):
        """Orts- oder Stadtteilname am Ende einer Adresse."""
        tail = address.split(",")[-1].strip()
        pieces = tail.split(" ", 1)
        if len(pieces) == 2 and pieces[0].isdigit():
            return pieces[1]
        return tail

    @staticmethod
    def store_point(address, offsets=None):
        """Breite und Länge einer Filiale aus Stadtmitte und Versatz."""
        district = StoreLocations.district_name(address)
        city = ProductLabels.fold(district.split("-", 1)[0])
        center = CITY_CENTERS.get(city)
        if center is None:
            return None
        if offsets is None:
            north_km, east_km = DISTRICT_OFFSETS_KM.get(district, (1.0, 1.0))
        else:
            north_km, east_km = offsets
        lat = center[0] + north_km / 111
        lng = center[1] + east_km / (111 * math.cos(math.radians(center[0])))
        return lat, lng

    @staticmethod
    def distance_km(origin, point):
        """Entfernung zweier Koordinaten in Kilometern."""
        lat1, lng1 = origin
        lat2, lng2 = point
        earth = 6371
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        chord = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlng / 2) ** 2
        return 2 * earth * math.asin(math.sqrt(chord))

    @staticmethod
    def origin_for(place):
        """Stadtmitte, wenn der Ort einer bekannten Stadt entspricht."""
        folded = ProductLabels.fold(place.strip())
        for name, center in CITY_CENTERS.items():
            if folded == name or folded.startswith(name + " ") or folded.startswith(name + "-"):
                return center
        return None

    @staticmethod
    def known_places(rows):
        """Orte und Postleitzahlen aus den Adressen der Beispielprodukte."""
        places = set()
        for row in rows:
            district = StoreLocations.district_name(row["store_address"])
            places.add(district.split("-", 1)[0])
            tail = row["store_address"].split(",")[-1].strip()
            postal_code = tail.split(" ", 1)[0]
            if postal_code.isdigit():
                places.add(postal_code)
        return sorted(places, key=ProductLabels.fold)

    @classmethod
    def german_places(cls):
        """Orte als „PLZ Name“, auffindbar über den Namen oder die Postleitzahl.

        Quelle GeoNames (CC BY 4.0). Die Produktdatenbank ergänzt diese Liste nicht.
        """
        if cls._german_places is None:
            path = Path(__file__).resolve().parent.parent / "data" / "german_places.json"
            cls._german_places = json.loads(path.read_text(encoding="utf-8"))
        return cls._german_places

    @staticmethod
    def place_locality(label):
        """Ortsname ohne vorangestellte Postleitzahl."""
        text = str(label).strip()
        if len(text) > 6 and text[:5].isdigit() and text[5] == " ":
            return text[6:]
        if ", " in text:
            return text.split(", ", 1)[0]
        return text

    @classmethod
    def resolve_place(cls, value, labels=None):
        """Ort, Postleitzahl oder „PLZ Ort“ auf den Ortsnamen abbilden."""
        text = str(value).strip()
        if not text:
            return None
        choices = cls.german_places() if labels is None else labels
        folded = ProductLabels.fold(text)
        for label in choices:
            if ProductLabels.fold(label) == folded:
                return cls.place_locality(label)
        if len(text) == 5 and text.isdigit():
            for label in choices:
                if label.startswith(text + " "):
                    return cls.place_locality(label)
            return None
        for label in choices:
            if ProductLabels.fold(cls.place_locality(label)) == folded:
                return cls.place_locality(label)
        return None

    @staticmethod
    def _point_for(row):
        """Koordinaten einer Produktzeile, inklusive gespeichertem Versatz."""
        offsets = None
        if row.get("north_km") is not None and row.get("east_km") is not None:
            offsets = (row["north_km"], row["east_km"])
        return StoreLocations.store_point(row.get("store_address", ""), offsets)

    @staticmethod
    def annotate_distance(products, place):
        """Hängt die Entfernung zum gesuchten Ort an jede Zeile."""
        origin = StoreLocations.origin_for(place or "")
        annotated = []
        for product in products:
            shown = dict(product)
            point = StoreLocations._point_for(shown) if origin is not None else None
            if origin is not None and point is not None:
                shown["distance_km"] = round(StoreLocations.distance_km(origin, point), 1)
            else:
                shown["distance_km"] = None
            annotated.append(shown)
        return annotated

    @staticmethod
    def stores_for_map(products):
        """Fahnen der Supermärkte auf der Karte.

        Summary:
            Jede Fahne hängt an den Koordinaten der Filiale.
            Verschiebt oder zoomt man die Karte, wandert die Fahne mit dem Ort mit.
        """
        grouped = {}
        for product in products:
            store = grouped.setdefault(
                product["store_id"],
                {
                    "store_id": product["store_id"],
                    "supermarket_name": product["supermarket_name"],
                    "store_address": product["store_address"],
                    "north_km": product.get("north_km"),
                    "east_km": product.get("east_km"),
                    "offers": [],
                },
            )
            if len(store["offers"]) < 4:
                store["offers"].append(
                    {"name": product["product_name"], "price_label": product["price_label"]}
                )
        stores = []
        for store in grouped.values():
            background, foreground = FLAG_COLORS.get(store["supermarket_name"], ("#2563eb", "#ffffff"))
            store["flag_bg"] = background
            store["flag_fg"] = foreground
            offsets = None
            if store["north_km"] is not None and store["east_km"] is not None:
                offsets = (store["north_km"], store["east_km"])
            point = StoreLocations.store_point(store["store_address"], offsets)
            if point is None:
                continue
            store["lat"], store["lng"] = point
            stores.append(store)
        return stores

    @staticmethod
    def map_focus(stores, place):
        """Startpunkt der Karte.

        Summary:
            Eine Filiale startet in der Mitte.
            Mehrere Filialen starten um den gesuchten Ort, jede an ihrem eigenen Punkt.
        """
        points = [(store["lat"], store["lng"]) for store in stores if store.get("lat") is not None]
        if len(points) == 1:
            return points[0]
        origin = StoreLocations.origin_for(place or "")
        if origin is not None:
            return origin
        if not points:
            return None
        return (
            sum(point[0] for point in points) / len(points),
            sum(point[1] for point in points) / len(points),
        )


