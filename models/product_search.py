"""Katalog, Produktsuche und Einkaufszettel.

Summary:
    Die Beispielprodukte kommen aus SQLite.
    Die aktuelle Suche liest die Ketten aus PostgreSQL.
"""

import json
import random
import re
import sqlite3
from itertools import combinations
from pathlib import Path

import psycopg

from models.product_kinds import KIND_RULES, PRODUCT_KINDS
from models.product_labels import ProductLabels
from models.store_locations import StoreLocations

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "grocery.sqlite"

CHAIN_NAMES = {
    "lidl": "Lidl",
    "aldi": "Aldi",
    "rewe": "Rewe",
    "edeka": "Edeka",
    "kaufland": "Kaufland",
    "penny": "Penny",
    "netto": "Netto",
    "norma": "Norma",
    "marktkauf": "Marktkauf",
    "spar": "Spar",
    "real": "real",
    "globus": "Globus",
}

class ProductSearch:
    """Katalog, Produktsuche und Einkaufszettel über die Supermarkt-Daten.

    Summary:
        Die Beispielprodukte kommen aus SQLite.
        Die aktuelle Suche liest die Ketten aus PostgreSQL.
    """

    _rows = None

    @classmethod
    def load_products(cls):
        """Alle Zeilen der lokalen Beispieldatenbank, einmal gelesen."""
        if cls._rows is None:
            connection = sqlite3.connect(DB_PATH)
            connection.row_factory = sqlite3.Row
            try:
                fetched = connection.execute(
                    "SELECT * FROM grocery_product ORDER BY id"
                ).fetchall()
            finally:
                connection.close()
            cls._rows = [dict(row) for row in fetched]
        return cls._rows

    @staticmethod
    def sample_products(count=10):
        """Kleine Vorschau mit Bio- und Pfandartikeln aus den Kettensortimenten."""
        from models.chain_catalog import ChainCatalog

        try:
            rows = ChainCatalog.chain_rows()
        except psycopg.Error:
            return []
        organic = [row for row in rows if row.get("is_organic")]
        deposit = [row for row in rows if row.get("is_deposit_required")]
        preview = []
        for group in (organic, deposit):
            chosen = {row["id"] for row in preview}
            pool = [row for row in group if row["id"] not in chosen]
            take = min(2, len(pool), count - len(preview))
            if take:
                preview.extend(random.sample(pool, take))
        chosen = {row["id"] for row in preview}
        rest = [row for row in rows if row["id"] not in chosen]
        need = min(count, len(rows)) - len(preview)
        if need > 0:
            preview.extend(random.sample(rest, need))
        random.shuffle(preview)
        return [ProductLabels.present(row) for row in preview]

    @staticmethod
    def _demand_catalog():
        """Mengenvorgabe je Produktart für die Eingabe auf dem Einkaufszettel."""
        from models.shopping_demand import ShoppingDemand

        catalog = {}
        for name in PRODUCT_KINDS:
            demand = ShoppingDemand.demand_for(name)
            catalog[name] = {
                "einheit": demand.unit,
                "schritt": demand.step,
                "minimum": demand.minimum,
                "vorgabe": demand.default,
            }
        return catalog

    @staticmethod
    def search_catalog():
        """Orte, Kategorien, Produktarten und Preisarten für die Vorschläge."""
        from models.chain_catalog import ChainCatalog

        try:
            rows = ChainCatalog.chain_rows()
        except psycopg.Error:
            rows = []
        tree = {}
        specials = set()
        for row in rows:
            subs = tree.setdefault(row["main_category"], {})
            subs.setdefault(row["sub_category"], set()).add(row["product_name"])
            if row["special_pricing"]:
                specials.add(row["special_pricing"])
        categories = []
        for name in sorted(tree, key=ProductLabels.fold):
            subs = [
                {"name": sub, "anzahl": len(tree[name][sub]), "produkte": sorted(tree[name][sub], key=ProductLabels.fold)}
                for sub in sorted(tree[name], key=ProductLabels.fold)
            ]
            categories.append(
                {
                    "name": name,
                    "anzahl": sum(sub["anzahl"] for sub in subs),
                    "unterkategorien": subs,
                }
            )
        order = ["Rabatt", "Mengenrabatt", "Preisaktion", "Gutschein", "Gratisartikel", "Coupon"]
        priced = list(order)
        priced += sorted(specials.difference(order), key=ProductLabels.fold)
        return {
            "orte": list(StoreLocations.german_places()),
            "kategorien": categories,
            "produktarten": list(PRODUCT_KINDS),
            "bedarf": ProductSearch._demand_catalog(),
            "preisarten": ["regulärer Preis", *priced, "Alle"],
        }

    @staticmethod
    def product_kind(value):
        """Produktart aus der Vorschlagsliste, ohne Markennamen."""
        return ProductSearch.canonical(str(value), PRODUCT_KINDS)

    @staticmethod
    def _kind_haystack(row):
        """Suchtext aus Name und Kategorien einer Zeile."""
        return ProductLabels.fold(" ".join((row["product_name"], row["sub_category"], row["main_category"])))

    @staticmethod
    def kind_matches(row, kind):
        """Prüft, ob eine Zeile zur Produktart gehört."""
        hay = ProductSearch._kind_haystack(row)
        rule = KIND_RULES.get(kind)
        if rule:
            if rule.get("all") and not all(ProductLabels.fold(term) in hay for term in rule["all"]):
                return False
            if rule.get("any") and not any(ProductLabels.fold(term) in hay for term in rule["any"]):
                return False
            if rule.get("none") and any(ProductLabels.fold(term) in hay for term in rule["none"]):
                return False
            return True
        base = ProductLabels.fold(re.sub(r"\s*\([^)]*\)", "", kind)).strip()
        return bool(base) and base in hay

    @staticmethod
    def canonical(value, options):
        """Schreibt einen Wert in der Schreibweise der Vorschlagsliste."""
        folded = ProductLabels.fold(value.strip())
        if not folded:
            return ""
        for option in options:
            if ProductLabels.fold(option) == folded:
                return option
        return None

    @staticmethod
    def _category_names(catalog):
        """Namen der Hauptkategorien im Suchkatalog."""
        return [category["name"] for category in catalog["kategorien"]]

    @staticmethod
    def _subcategories(catalog, category=""):
        """Namen der Unterkategorien, optional nur innerhalb einer Hauptkategorie."""
        names = []
        for entry in catalog["kategorien"]:
            if category and entry["name"] != category:
                continue
            names.extend(sub["name"] for sub in entry["unterkategorien"])
        return names

    @staticmethod
    def _find_product(catalog, product):
        """Produktname mit seiner Kategorie, wenn er in den Vorschlägen steht."""
        for category in catalog["kategorien"]:
            for sub in category["unterkategorien"]:
                for name in sub["produkte"]:
                    if ProductLabels.fold(name) == ProductLabels.fold(product):
                        return {"name": name, "category": category["name"], "sub": sub["name"]}
        return None

    @staticmethod
    def _join_phrases(parts):
        """Aufzählung mit Kommas und einem „und“ vor dem letzten Teil."""
        if len(parts) == 1:
            return parts[0]
        return ", ".join(parts[:-1]) + " und " + parts[-1]

    @staticmethod
    def _candidate_steps(place, category, subcategory, product, markets, offer_type, radius_km):
        """Lockerungen, die aus einer leeren Suche noch Treffer machen können."""
        steps = []
        if offer_type not in ("", "Alle"):
            steps.append(("price", f"ohne die Preisart „{offer_type}“", {"offer_type": "Alle"}))
        if place and radius_km not in (None, ""):
            steps.append(("radius", "außerhalb des gewählten Umkreises", {"radius_km": None}))
        chain_labels = [CHAIN_NAMES[name] for name in (markets or []) if name in CHAIN_NAMES]
        if chain_labels:
            steps.append(("market", "in anderen Supermärkten als " + ProductSearch._join_phrases(chain_labels), {"markets": []}))
        record = ProductSearch._find_product(ProductSearch.search_catalog(), product) if product else None
        sub_name = subcategory or (record["sub"] if record else "")
        cat_name = category or (record["category"] if record else "")
        if product and (sub_name or cat_name):
            label = f"der Unterkategorie {sub_name}" if sub_name else f"der Kategorie {cat_name}"
            steps.append(
                (
                    "product",
                    f"mit ähnlichen Produkten aus {label}",
                    {"product": "", "subcategory": sub_name, "category": cat_name},
                )
            )
        if sub_name:
            category_label = f"der Kategorie {cat_name}" if cat_name else "derselben Kategorie"
            steps.append(
                (
                    "sub",
                    f"mit weiteren Produkten aus {category_label}",
                    {"product": "", "subcategory": "", "category": cat_name},
                )
            )
        if place and (product or sub_name or cat_name or markets):
            steps.append(("place", "an anderen Orten", {"place": "", "radius_km": None}))
        return steps

    @staticmethod
    def _visible_reasons(steps):
        """Gründe, die im Hinweis stehen, ohne doppelte Lockerungen."""
        used = {step_id for step_id, _reason, _changes in steps}
        reasons = []
        for step_id, reason, _changes in steps:
            if step_id == "radius" and "place" in used:
                continue
            if step_id == "product" and "sub" in used:
                continue
            reasons.append(reason)
        return reasons

    @staticmethod
    def suggest_alternatives(place="", category="", subcategory="", product="", markets=None, offer_type="", radius_km=None):
        """Nächstliegende Treffer, wenn die exakte Kombination leer ist."""
        base = {
            "place": place,
            "category": category,
            "subcategory": subcategory,
            "product": product,
            "markets": list(markets or []),
            "offer_type": offer_type,
            "radius_km": radius_km,
        }
        steps = ProductSearch._candidate_steps(place, category, subcategory, product, markets, offer_type, radius_km)
        for size in range(1, min(3, len(steps)) + 1):
            for combo in combinations(steps, size):
                trial = dict(base)
                for _step_id, _reason, changes in combo:
                    trial.update(changes)
                found = ProductSearch.search_products(**trial)
                if found:
                    return found, ProductSearch._visible_reasons(combo), trial
        return [], [], base

    @staticmethod
    def _empty_notice(reasons):
        """Hinweistext, wenn die exakte Suche leer ist."""
        lead = "Leider konnten wir keine Produkte mit genau den gewählten Kriterien finden"
        if not reasons:
            return lead + "."
        return lead + ", aber " + ProductSearch._join_phrases(reasons) + " gibt es diese Produkte."

    @staticmethod
    def prepare_search(place="", category="", subcategory="", product="", markets=None, offer_type="", radius_km=None):
        """Prüft die Suchfelder und liefert Treffer oder einen Hinweis auf ähnliche Produkte."""
        catalog = ProductSearch.search_catalog()
        markets = [name for name in (markets or []) if name in CHAIN_NAMES]
        chosen_place = StoreLocations.resolve_place(place, catalog["orte"]) if place.strip() else ""
        chosen_category = ProductSearch.canonical(category, ProductSearch._category_names(catalog)) if category.strip() else ""
        chosen_sub = ProductSearch.canonical(subcategory, ProductSearch._subcategories(catalog)) if subcategory.strip() else ""
        chosen_product = ProductSearch._find_product(catalog, product) if product.strip() else None
        allowed_prices = set(catalog["preisarten"])
        chosen_price = ProductSearch.canonical(offer_type, allowed_prices) if str(offer_type).strip() else "regulärer Preis"
        if place.strip() and not chosen_place:
            return ProductSearch._invalid("Bitte einen Ort aus den Vorschlägen wählen.", place, category, subcategory, product, offer_type)
        if category.strip() and chosen_category is None:
            return ProductSearch._invalid("Bitte eine Kategorie aus den Vorschlägen wählen.", place, category, subcategory, product, offer_type)
        if subcategory.strip() and chosen_sub is None:
            return ProductSearch._invalid("Bitte eine Unterkategorie aus den Vorschlägen wählen.", place, category, subcategory, product, offer_type)
        if product.strip() and chosen_product is None:
            return ProductSearch._invalid("Bitte ein Produkt aus den Vorschlägen wählen.", place, category, subcategory, product, offer_type)
        if chosen_price is None:
            return ProductSearch._invalid("Bitte eine Preisart aus der Liste wählen.", place, category, subcategory, product, offer_type)
        if chosen_category and chosen_sub and chosen_sub not in ProductSearch._subcategories(catalog, chosen_category):
            return ProductSearch._invalid("Diese Unterkategorie gibt es in der gewählten Kategorie nicht.", chosen_place, chosen_category, subcategory, product, chosen_price)
        if chosen_product:
            if chosen_category and chosen_product["category"] != chosen_category:
                return ProductSearch._invalid("Dieses Produkt liegt nicht in der gewählten Kategorie.", chosen_place, chosen_category, chosen_sub, product, chosen_price)
            if chosen_sub and chosen_product["sub"] != chosen_sub:
                return ProductSearch._invalid("Dieses Produkt liegt nicht in der gewählten Unterkategorie.", chosen_place, chosen_category, chosen_sub, product, chosen_price)
        if not chosen_place or not markets or not (chosen_category or chosen_sub or chosen_product):
            return ProductSearch._invalid(
                "Bitte einen Ort und einen Supermarkt angeben. Bei Kategorie, Unterkategorie und Produkt genügt eine Angabe.",
                chosen_place,
                chosen_category,
                chosen_sub,
                product,
                chosen_price or "regulärer Preis",
            )
        found = ProductSearch.search_products(
            chosen_place,
            chosen_category,
            chosen_sub,
            chosen_product["name"] if chosen_product else "",
            markets,
            chosen_price,
            radius_km if chosen_place else None,
        )
        notice = ""
        result_place = chosen_place
        keep_radius = bool(chosen_place)
        if not found:
            found, reasons, trial = ProductSearch.suggest_alternatives(
                chosen_place,
                chosen_category,
                chosen_sub,
                chosen_product["name"] if chosen_product else "",
                markets,
                chosen_price,
                radius_km if chosen_place else None,
            )
            notice = ProductSearch._empty_notice(reasons)
            result_place = trial["place"] if found else ""
            keep_radius = bool(found and trial["place"] and trial["radius_km"] not in (None, ""))
            if len(found) > 24:
                notice += f" Es sind die ersten 24 von {len(found)} Produkten."
                found = found[:24]
        return {
            "error": "",
            "place": chosen_place,
            "category": chosen_category,
            "subcategory": chosen_sub,
            "product": chosen_product["name"] if chosen_product else "",
            "offer_type": chosen_price,
            "products": found,
            "notice": notice,
            "result_place": result_place,
            "keep_radius": keep_radius,
        }

    @staticmethod
    def _invalid(message, place, category, subcategory, product, offer_type):
        """Antwort einer Suche, die an den Eingaben scheitert."""
        return {
            "error": message,
            "place": place,
            "category": category,
            "subcategory": subcategory,
            "product": product,
            "offer_type": offer_type or "regulärer Preis",
            "products": [],
            "notice": "",
            "result_place": "",
            "keep_radius": False,
        }

    @staticmethod
    def prepare_shopping_list(place="", products=None, markets=None, radius_km=None):
        """Produkte eines Einkaufszettels in genau einem Supermarkt suchen."""
        catalog = ProductSearch.search_catalog()
        names = []
        seen_names = set()
        for raw in products or []:
            text = str(raw).strip()
            key = ProductLabels.fold(text)
            if not key or key in seen_names:
                continue
            seen_names.add(key)
            names.append(text)
        markets = [name for name in (markets or []) if name in CHAIN_NAMES][:1]
        chosen_place = StoreLocations.resolve_place(place, catalog["orte"]) if place.strip() else ""
        from models.chain_catalog import CHAIN_DATABASES

        if markets and markets[0] not in CHAIN_DATABASES:
            return ProductSearch._invalid(
                f"Für {CHAIN_NAMES[markets[0]]} gibt es noch kein Sortiment.",
                chosen_place or place,
                "",
                "",
                "",
                "Alle",
            )
        if place.strip() and not chosen_place:
            return ProductSearch._invalid("Bitte einen Ort aus den Vorschlägen wählen.", place, "", "", "", "Alle")
        resolved = []
        for name in names:
            found = ProductSearch.product_kind(name)
            if not found:
                return ProductSearch._invalid("Bitte nur Produktarten aus den Vorschlägen wählen.", chosen_place or place, "", "", name, "Alle")
            resolved.append(found)
        if not chosen_place or not markets or not resolved:
            return ProductSearch._invalid(
                "Bitte einen Ort, einen Supermarkt und mindestens ein Produkt angeben.",
                chosen_place or place,
                "",
                "",
                "",
                "Alle",
            )
        found_rows = []
        seen_ids = set()
        missing = []
        for name in resolved:
            hits = ProductSearch.search_products(chosen_place, "", "", "", markets, "Alle", radius_km, kind=name)
            if not hits:
                missing.append(name)
                continue
            for row in hits:
                if row["id"] in seen_ids:
                    continue
                seen_ids.add(row["id"])
                found_rows.append(row)
        notice = ""
        if missing:
            notice = "Diese Produkte gibt es dort nicht: " + ", ".join(missing) + "."
        return {
            "error": "",
            "place": chosen_place,
            "category": "",
            "subcategory": "",
            "product": "",
            "offer_type": "Alle",
            "products": found_rows,
            "notice": notice,
            "result_place": chosen_place,
            "keep_radius": True,
        }

    @staticmethod
    def search_products(place="", category="", subcategory="", product="", markets=None, offer_type="", radius_km=None, kind=""):
        """Filtert die Kettensortimente nach Ort, Kategorie, Produkt, Markt und Preisart."""
        from models.chain_catalog import ChainCatalog

        wanted_chains = {CHAIN_NAMES[name] for name in (markets or []) if name in CHAIN_NAMES}
        folded_place = ProductLabels.fold(place.strip())
        origin = StoreLocations.origin_for(place)
        try:
            radius = float(radius_km) if radius_km not in (None, "") else None
        except (TypeError, ValueError):
            radius = None
        try:
            source = ChainCatalog.chain_rows(markets)
        except psycopg.Error:
            return []
        matches = []
        for row in source:
            shown = dict(row)
            if place.strip():
                shown["store_address"] = place.strip()
            if folded_place and folded_place not in ProductLabels.fold(shown["store_address"]):
                continue
            if origin is not None and radius is not None:
                point = StoreLocations._point_for(shown)
                if point is None or StoreLocations.distance_km(origin, point) > radius:
                    continue
            if category and ProductLabels.fold(shown["main_category"]) != ProductLabels.fold(category):
                continue
            if subcategory and ProductLabels.fold(shown["sub_category"]) != ProductLabels.fold(subcategory):
                continue
            if product and ProductLabels.fold(shown["product_name"]) != ProductLabels.fold(product):
                continue
            if kind and ProductLabels.fold(shown.get("product_kind", "")) != ProductLabels.fold(kind):
                continue
            if wanted_chains and shown["supermarket_name"] not in wanted_chains:
                continue
            if offer_type == "regulärer Preis":
                if shown["special_pricing"]:
                    continue
            elif offer_type and offer_type != "Alle":
                if shown["special_pricing"] != offer_type:
                    continue
            matches.append(ProductLabels.present(shown))
        return matches

    @staticmethod
    def sort_products(products, mode, descending=False):
        """Sortiert Treffer nach Name, Entfernung oder Preis."""
        def name_key(product):
            return ProductLabels.fold(product["product_name"])

        if mode == "name":
            ordered = sorted(products, key=name_key, reverse=descending)
        elif mode == "distance":
            ordered = sorted(
                products,
                key=lambda product: (
                    product.get("distance_km") is None,
                    -(product.get("distance_km") or 0) if descending else (product.get("distance_km") or 0),
                    name_key(product),
                ),
            )
        elif mode == "price":
            ordered = sorted(
                products,
                key=lambda product: (product["current_price"], name_key(product)),
                reverse=descending,
            )
        else:
            return list(products)
        return ordered
