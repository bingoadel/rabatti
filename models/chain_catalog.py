"""Produktsuche aus den Supermarkt-Datenbanken in PostgreSQL.

Summary:
    Aldi, Lidl, Rewe, Netto und Penny haben je eine Datenbank.
    Die Zeilen werden in die Form gebracht, die die Ergebnisseite erwartet.
"""

import json
import os

import psycopg
from psycopg.rows import dict_row

CHAIN_DATABASES = ("aldi", "lidl", "rewe", "netto", "penny")
CHAIN_LABELS = {
    "aldi": "Aldi",
    "lidl": "Lidl",
    "rewe": "Rewe",
    "netto": "Netto",
    "penny": "Penny",
}

CATEGORY_IMAGES = {
    "Molkereiprodukte": "/static/products/product-milch.jpg",
    "Käse": "/static/products/product-kaese.jpg",
    "Brot und Backwaren": "/static/products/product-brot.jpg",
    "Obst": "/static/products/product-obst.jpg",
    "Gemüse": "/static/products/product-gemuese.jpg",
    "Fleisch und Wurst": "/static/products/product-fleisch.jpg",
    "Fisch": "/static/products/product-fisch.jpg",
    "Nudeln und Getreide": "/static/products/product-nudeln.jpg",
    "Süßwaren und Snacks": "/static/products/product-suess.jpg",
    "Feinkost": "/static/products/product-feinkost.jpg",
    "Konserven": "/static/products/product-konserve.jpg",
    "Getränke": "/static/products/product-getraenk.jpg",
    "Tiefkühl": "/static/products/product-tiefkuehl.jpg",
    "Vorrat": "/static/products/product-vorrat.jpg",
    "Gewürze": "/static/products/product-gewuerz.jpg",
}

# Kleiner Versatz je Kette, damit Filialen auf der Karte auseinanderliegen.
CHAIN_OFFSETS_KM = {
    "lidl": (1.6, 0.7),
    "aldi": (2.8, -1.4),
    "rewe": (0.5, 2.4),
    "netto": (3.4, 1.1),
    "penny": (-1.3, 1.8),
}

_CACHE = {}


class ChainCatalog:
    """Liest die Sortimente der Supermarktketten aus PostgreSQL.

    Summary:
        Jede Kette wird einmal geladen und danach aus dem Speicher gelesen.
    """

    @staticmethod
    def postgres_connection(database):
        return psycopg.connect(
            host=os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            port=os.environ.get("POSTGRES_PORT", "5433"),
            dbname=database,
            user=os.environ.get("POSTGRES_USER", "rabatti"),
            password=os.environ.get("POSTGRES_PASSWORD", "rabatti"),
            connect_timeout=3,
            row_factory=dict_row,
        )

    @staticmethod
    def _additive_parts(text):
        """Zerlegt den kommaseparierten Zusatzstoff-Text in einzelne Einträge."""
        return [part.strip() for part in text.split(",") if part.strip()]

    @staticmethod
    def _base_price(price, quantity, unit):
        if quantity <= 0:
            return price
        if unit in {"g", "ml"}:
            return price / quantity * 1000
        return price / quantity

    @staticmethod
    def _catalog_row(raw, chain):
        price = float(raw["regular_price"])
        quantity = float(raw["net_quantity"])
        north, east = CHAIN_OFFSETS_KM[chain]
        return {
            "id": f"{chain}-{raw['id']}",
            "product_name": raw["product_name"],
            "brand": raw["brand"],
            "manufacturer": raw["brand"],
            "main_category": raw["main_category"],
            "sub_category": raw["product_kind"],
            "product_kind": raw["product_kind"],
            "net_quantity": quantity,
            "unit": raw["unit"],
            "packaging_type": raw["packaging_type"],
            "regular_price": price,
            "current_price": price,
            "calculated_base_price": ChainCatalog._base_price(price, quantity, raw["unit"]),
            "special_pricing": "",
            "is_organic": bool(raw["is_organic"]),
            "is_gluten_free": bool(raw["is_gluten_free"]),
            "is_lactose_free": bool(raw["is_lactose_free"]),
            "is_deposit_required": False,
            "additives": json.dumps(ChainCatalog._additive_parts(raw.get("additives") or ""), ensure_ascii=False),
            "description": raw["note"],
            "image_url": CATEGORY_IMAGES.get(raw["main_category"], ""),
            "supermarket_name": CHAIN_LABELS[chain],
            "store_id": chain,
            "store_address": "",
            "north_km": north,
            "east_km": east,
        }

    @staticmethod
    def load_chain(chain):
        """Alle Produkte einer Supermarkt-Datenbank, einmal gelesen und dann im Speicher."""
        if chain not in CHAIN_DATABASES:
            return []
        cached = _CACHE.get(chain)
        if cached is None:
            with ChainCatalog.postgres_connection(chain) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, product_name, brand, product_kind, main_category,
                               net_quantity, unit, packaging_type, regular_price, is_organic,
                               is_gluten_free, is_lactose_free, additives, note
                        FROM product
                        ORDER BY id
                        """
                    )
                    cached = [ChainCatalog._catalog_row(raw, chain) for raw in cursor.fetchall()]
            _CACHE[chain] = cached
        return cached

    @staticmethod
    def chain_rows(markets=None):
        """Produkte der genannten Ketten. Ohne Angabe alle fünf Sortimente."""
        if markets:
            slugs = [name for name in markets if name in CHAIN_DATABASES]
        else:
            slugs = list(CHAIN_DATABASES)
        rows = []
        for slug in slugs:
            rows.extend(ChainCatalog.load_chain(slug))
        return rows


