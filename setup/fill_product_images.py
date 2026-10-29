"""Sucht Produktfotos und schreibt data/product_images.json.

Zuerst wird das konkrete Markenprodukt in Open Food Facts gesucht.
Nur ein Treffer mit passender Marke, passendem Namen und Bildlink wird übernommen.
Sonst ein geprüftes allgemeines Lebensmittelbild zur Unterkategorie.
"""

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:
    from . import build_grocery_db
except ImportError:
    import build_grocery_db

DATA = Path(__file__).resolve().parent.parent / "data"
OUT = DATA / "product_images.json"
HEADERS = {"User-Agent": "Rabattparty/1.0 (info@cvboostai.de)"}
STOP = {
    "und", "mit", "art", "bio", "der", "die", "das", "von", "fuer", "für",
    "aus", "ohne", "extra", "classic", "klassisch", "dem", "den", "ein", "eine",
    "stuck", "stueck", "stück", "grose", "grosse", "grosse", "große",
}
BAD_CATEGORY = (
    "wiki loves earth", "landscape", "mountain", "lake", "sunset",
    "beach", "castle", "waterfall", "skyline", "aterro",
)
GOOD_CATEGORY = (
    "food", "drink", "beverage", "dairy", "fruit", "vegetable", "meat", "bread",
    "confection", "snack", "cereal", "pasta", "rice", "fish", "cheese", "milk",
    "sugar", "spice", "coffee", "tea", "juice", "chocolate", "candy", "dessert",
    "ice cream", "yogurt", "yoghurt", "butter", "egg", "flour", "oil", "vinegar",
    "sauce", "sausage", "ham", "poultry", "beef", "pork", "nut", "breakfast",
    "grocery", "dishes", "cuisine", "water", "soft drink", "cola", "jam",
    "spread", "margarine", "cream", "quark", "mustard", "ketchup", "mayonnaise",
    "pizza", "potato", "cake", "pudding", "baking", "noodle", "soup", "bean",
    "tomato", "apple", "banana", "grape", "berr", "citrus", "kiwi", "carrot",
    "lettuce", "cucumber", "mushroom", "chicken", "salmon", "tuna", "herring",
    "trout", "sweet", "gummi", "honey", "cookie", "cracker", "crisp", "chip",
    "waffle", "ice", "frozen", "stew", "lentil", "olive", "cocoa", "praline",
    "toffee", "nougat", "hazelnut", "peanut", "almond", "oat", "muesli", "corn",
    "flake", "sugar", "vanilla", "yeast", "breadcrumb", "panade", "roll",
    "toast", "bun", "loaf", "rye", "wheat", "clementine", "orange", "lemon",
    "strawberry", "berry", "salad", "pepper", "onion", "mince", "cutlet",
    "schnitzel", "wurst", "salami", "liver", "forelle", "seelachs", "pollock",
    "stick", "finger", "spaghetti", "penne", "fusilli", "basmati", "passata",
    "ketchup", "senf", "mayo", "essig", "öl", "oil", "mate", "limonade", "soda",
    "mineral", "schokolade", "haribo", "riegel", "bar", "eis", "sorbet",
)
SEARCH = {
    "Milch": "glass of cow milk",
    "Joghurt": "plain yogurt cup",
    "Käse": "piece of cheese",
    "Butter": "stick of butter",
    "Sahne": "whipped cream dairy",
    "Quark": "quark curd cheese spoon",
    "Mischbrot": "loaf of rye bread",
    "Toast": "slice of toast bread",
    "Vollkornbrot": "whole grain bread loaf",
    "Brötchen": "bread rolls",
    "Bananen": "bananas fruit",
    "Äpfel": "red apple fruit",
    "Zitrusfrüchte": "clementines fruit",
    "Beeren": "strawberries fruit",
    "Exoten": "kiwifruit sliced",
    "Trauben": "grapes fruit",
    "Wurzelgemüse": "carrots vegetable",
    "Salat": "iceberg lettuce",
    "Fruchtgemüse": "cucumber vegetable",
    "Pilze": "button mushrooms",
    "Hackfleisch": "raw minced meat",
    "Geflügel": "raw chicken breast",
    "Schwein": "raw pork chop",
    "Rind": "raw beef steak",
    "Brühwurst": "lyoner sausage",
    "Würstchen": "frankfurter sausages",
    "Schinken": "sliced cooked ham",
    "Geflügelwurst": "poultry sausage",
    "Rohwurst": "salami sausage",
    "Streichwurst": "liverwurst spread",
    "Fischstäbchen": "fish fingers",
    "Räucherfisch": "smoked trout",
    "Hering": "herring fish",
    "Seelachs": "pollock fish fillet",
    "Backfisch": "battered fried fish",
    "Lachs": "salmon fillet",
    "Thunfisch": "canned tuna",
    "Nudeln": "dry spaghetti",
    "Reis": "uncooked white rice",
    "Gemüse": "mixed vegetables",
    "Hülsenfrüchte": "kidney beans",
    "Tomaten": "tomato passata",
    "Eintopf": "vegetable stew bowl",
    "Fisch": "fish fillet",
    "Nusscreme": "chocolate hazelnut spread",
    "Konfitüre": "strawberry jam jar",
    "Margarine": "margarine tub",
    "Limonade": "cola soft drink",
    "Wasser": "bottled mineral water",
    "Mate": "mate iced tea bottle",
    "Orangensaft": "orange juice glass",
    "Apfelsaft": "apple juice glass",
    "Mehrfruchtsaft": "mixed fruit juice",
    "Kaffee": "roasted coffee beans",
    "Tee": "tea leaves",
    "Schokolade": "milk chocolate bar",
    "Fruchtgummi": "gummy bears",
    "Riegel": "chocolate bar snack",
    "Pralinen": "chocolate pralines box",
    "Chips": "potato chips",
    "Nüsse": "roasted peanuts",
    "Gebäck": "salt sticks crackers",
    "Pizza": "pizza margherita",
    "Kartoffelprodukte": "french fries",
    "Kuchen": "strawberry cream cake",
    "Suppen": "instant soup cup",
    "Nudelgerichte": "cooked pasta bowl",
    "Reisgerichte": "cooked rice dish",
    "Öl": "olive oil bottle",
    "Essig": "vinegar bottle",
    "Mayonnaise": "mayonnaise bowl",
    "Ketchup": "ketchup bottle",
    "Würze": "seasoning sauce bottle",
    "Saucen": "brown gravy sauce",
    "Senf": "mustard jar",
    "Cornflakes": "corn flakes bowl",
    "Müsli": "muesli cereal",
    "Haferflocken": "rolled oats",
    "Zucker": "white granulated sugar",
    "Mehl": "wheat flour",
    "Pudding": "chocolate pudding",
    "Backtriebmittel": "baking powder",
    "Eier": "chicken eggs carton",
    "Panade": "bread crumbs",
    "Vanilleeis": "vanilla ice cream",
    "Eisriegel": "ice cream bar on stick",
    "Mehrsorte": "neapolitan ice cream",
    "Eisbecher": "ice cream sundae cup",
}


def fold(value):
    return (
        str(value)
        .casefold()
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )


def norm(value):
    text = fold(value).replace("&", " und ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def words(value):
    return [word for word in norm(value).split() if word not in {"dr", "und", "co", "gmbh", "kg", "the"}]


def get_json(url):
    for attempt in range(4):
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=40) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    return {}


def off_search(query):
    url = "https://search.openfoodfacts.org/search?" + urllib.parse.urlencode({"q": query, "page_size": "20"})
    data = get_json(url)
    time.sleep(0.2)
    return data.get("hits") or []


def brand_match(wanted, brands):
    if isinstance(brands, list):
        have = []
        for brand in brands:
            have.extend(words(brand))
    else:
        have = words(brands or "")
    wanted_words = words(wanted)
    distinctive = [word for word in wanted_words if len(word) > 2] or wanted_words
    return bool(distinctive) and all(word in have for word in distinctive)


def name_tokens(brand, product_name):
    short = product_name
    if product_name.startswith(brand + " "):
        short = product_name[len(brand) + 1:]
    return [word for word in words(short) if len(word) >= 4 and word not in STOP]


def hit_text(hit):
    parts = []
    for key, value in hit.items():
        if key.startswith("product_name") and isinstance(value, str):
            parts.append(value)
    return " ".join(parts)


def choose_product_image(item):
    brand = item["brand"]
    label = item["product_name"]
    short = label[len(brand) + 1:] if label.startswith(brand + " ") else label
    brand_word = max(words(brand), key=len)
    queries = [f"{short} brands:{brand_word}", f"{brand} {short}", short]
    tokens = name_tokens(brand, label)
    best = None
    best_score = 0
    seen = set()
    for query in queries:
        if query in seen:
            continue
        seen.add(query)
        for hit in off_search(query):
            image = hit.get("image_front_small_url") or hit.get("image_front_url")
            if not image or "openfoodfacts.org" not in image or not brand_match(brand, hit.get("brands")):
                continue
            haystack = set(words(hit_text(hit)))
            overlap = [token for token in tokens if token in haystack]
            if tokens and not overlap:
                continue
            score = len(overlap) * 10 + (5 if short.casefold() in hit_text(hit).casefold() else 0)
            if score > best_score:
                best_score = score
                best = image.split("?")[0]
        if best:
            return best, "openfoodfacts"
    return None, ""


def commons_categories(titles):
    found = {}
    for start in range(0, len(titles), 4):
        batch = titles[start:start + 4]
        params = {
            "action": "query",
            "titles": "|".join("File:" + title for title in batch),
            "prop": "imageinfo|categories",
            "iiprop": "url",
            "iiurlwidth": "330",
            "cllimit": "500",
            "format": "json",
            "redirects": "0",
        }
        while True:
            url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
            data = get_json(url)
            time.sleep(0.25)
            for page in data.get("query", {}).get("pages", {}).values():
                title = page.get("title", "").removeprefix("File:")
                entry = found.setdefault(title, {"categories": [], "url": "", "missing": False})
                entry["categories"].extend(item.get("title", "") for item in page.get("categories", []))
                info = (page.get("imageinfo") or [{}])[0]
                link = (info.get("thumburl") or info.get("url") or "").split("?")[0]
                if link:
                    entry["url"] = link
                entry["missing"] = "missing" in page
            if "continue" not in data:
                break
            params.update(data["continue"])
    return found


def food_photo(categories):
    text = " ".join(categories).casefold()
    tokens = set(re.findall(r"[a-z]+", text))
    if "wiki loves earth" in text or "aterro" in text:
        return False
    if tokens & {"landscape", "mountain", "lake", "sunset", "beach", "castle", "waterfall", "skyline"}:
        return False
    return any(good in text for good in GOOD_CATEGORY)


MUST = {sub: tuple(word for word in query.split() if len(word) > 4) for sub, query in SEARCH.items()}
MUST["Zucker"] = ("sugar", "zucker")
MUST["Cornflakes"] = ("corn", "flake", "cereal")
MUST["Sahne"] = ("cream", "sahne")
MUST["Mehl"] = ("flour", "mehl")
MUST["Essig"] = ("vinegar", "essig")
MUST["Pizza"] = ("pizza",)
MUST["Riegel"] = ("bar", "riegel", "snack")
MUST["Thunfisch"] = ("tuna", "thunfisch")
MUST["Backtriebmittel"] = ("baking", "powder", "backpulver")
MUST["Kartoffelprodukte"] = ("fries", "potato", "pommes")


def filename_of(url):
    name = urllib.parse.unquote(url.rsplit("/", 1)[-1])
    if name.startswith("330px-"):
        name = name[len("330px-"):]
    return name.replace("_", " ")


def search_commons(query, required):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": "6",
        "srlimit": "12",
        "format": "json",
    })
    data = get_json(url)
    time.sleep(0.3)
    titles = [hit["title"].removeprefix("File:") for hit in data.get("query", {}).get("search", [])]
    checked = commons_categories(titles)
    for title in titles:
        info = checked.get(title)
        folded = fold(title)
        if not any(word in folded for word in required):
            continue
        if info and not info["missing"] and info["url"] and food_photo(info["categories"]):
            return info["url"]
    return ""


def generic_images():
    current = {}
    for sub, url in build_grocery_db.IMAGE_URLS.items():
        current[sub] = url
    checked = commons_categories([filename_of(url) for url in current.values()])
    resolved = {}
    for sub, url in current.items():
        info = checked.get(filename_of(url), {})
        if info.get("url") and not info.get("missing") and food_photo(info["categories"]):
            resolved[sub] = info["url"]
            print(f"generic ok  {sub}")
        else:
            found = search_commons(SEARCH[sub], MUST[sub])
            if not found:
                raise SystemExit(f"Kein allgemeines Bild für {sub}")
            print(f"generic neu {sub} -> {filename_of(found)}")
            resolved[sub] = found
    return resolved


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    products = build_grocery_db.catalog()
    if limit:
        products = products[:limit]
    generics = generic_images()
    chosen = {}
    sources = {}
    if OUT.exists() and not limit:
        previous = json.loads(OUT.read_text(encoding="utf-8"))
        chosen = previous.get("products", {})
        sources = previous.get("sources", {})
    branded = sum(1 for source in sources.values() if source == "openfoodfacts")
    for item in products:
        if item["product_name"] in chosen:
            continue
        image, source = choose_product_image(item)
        if not image:
            image = generics[item["sub_category"]]
            source = "generic"
        else:
            branded += 1
        chosen[item["product_name"]] = image
        sources[item["product_name"]] = source
        print(f"{source:14} {item['product_name']}")
        if not limit and len(chosen) % 20 == 0:
            OUT.write_text(
                json.dumps({"products": chosen, "sources": sources, "generic": generics}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
    payload = {"products": chosen, "sources": sources, "generic": generics}
    if not limit:
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{branded} Markenbilder, {len(chosen) - branded} allgemeine Bilder -> {OUT}")
    else:
        print(f"Probe: {branded} Markenbilder von {len(chosen)}")


if __name__ == "__main__":
    main()
