"""
ChefMinistry -- Venue & Scope Classifier
=========================================
Rule-based classifier that assigns structured filtering fields to every
restaurant record.  Runs at export time (export_signals.py) and is also
called by scrape_gmaps.py to tag records at ingest.

Output fields (schema v2):
  city                : "Bangkok" | ""
  province            : "Bangkok" | "Chiang Mai" | ...
  area                : canonical neighbourhood (existing field, preserved)
  country             : "Thailand"
  venue_type          : restaurant | cafe | kiosk | street_food |
                        food_stand | takeaway_only | unknown
  scope_market        : bangkok_restaurant_focus | bangkok_cafe_focus |
                        out_of_scope_location | out_of_scope_format |
                        needs_review
  is_bangkok_focus    : True | False
  is_restaurant_focus : True | False
  exclude_reason      : null | province_not_bangkok | kiosk_format |
                        street_food_format | food_stand_format |
                        takeaway_only | missing_location | unclear_format

Usage:
    from classify import classify_record
    enriched = classify_record(record_dict)
"""

import re

# -- Bangkok neighbourhoods / areas -------------------------------------------
# Any record whose `area` matches one of these is assumed to be in Bangkok.
BANGKOK_AREAS = {
    "thonglor", "ekkamai", "silom", "sathorn", "ari", "ratchada",
    "sukhumvit", "onnut", "on nut", "ladprao", "lat phrao", "rama9", "rama 9",
    "asok", "asoke", "phrom phong", "phromphong", "nana", "chit lom",
    "chitlom", "siam", "ratchaprasong", "phaya thai", "phayathai",
    "bang na", "bangna", "bang kapi", "bangkapi", "minburi", "min buri",
    "lat krabang", "latkrabang", "don mueang", "sathon", "talat phlu",
    "talad phlu", "phra khanong", "phrakhanong", "udom suk",
    "udomsuk", "bearing", "bangmod", "bang mod", "pinklao", "pin klao",
    "charoennakorn", "charoen nakhon", "iconsiam", "waterfront",
    "phra ram", "rama", "dindeang", "din daeng", "ratchathewi", "ratchathevi",
    "bang rak", "bangrak", "samyan", "silom-sathorn", "pathumwan",
    "pratunam", "makkasan", "huai khwang", "huaikhwang", "lak si", "laksi",
    "nonthaburi",
    # Scraped areas confirmed from export_restaurants.json
    "ramintra", "ram intra", "raminthra",
    "ramkhamhaeng", "ram khamhaeng",
    "bangkok",
}

# Province names that are clearly NOT Bangkok
OUT_OF_SCOPE_PROVINCES = {
    "trat", "chiang mai", "chiang rai", "phuket", "krabi", "samui",
    "koh samui", "ko samui", "pattaya", "hua hin", "rayong", "khon kaen",
    "udon thani", "nakhon ratchasima", "korat", "ayutthaya", "lopburi",
    "chonburi", "suratthani", "surat thani", "songkhla", "hat yai",
    "nakhon si thammarat", "phetchaburi", "phetchabun", "lampang",
    "uttaradit", "nan", "phrae", "mae hong son", "tak", "kanchanaburi",
    "suphan buri", "nakhon pathom", "samut sakhon", "samut prakan",
    "samut songkhram", "prachuap khiri khan", "chumphon", "ranong",
    "phang nga", "satun", "trang", "phatthalung", "pattani", "yala",
    "narathiwat", "buriram", "surin", "si sa ket", "yasothon", "roi et",
    "mukdahan", "nakhon phanom", "sakon nakhon", "nong khai", "loei",
    "nong bua lam phu", "ubon ratchathani", "amnat charoen", "chiang khan",
    "phitsanulok", "nakhon sawan", "uthai thani", "kamphaeng phet",
    "phichit", "sukhothai", "phetchabun",
}

# -- Google Maps types mapping ------------------------------------------------
GMAPS_RESTAURANT_TYPES = {
    "restaurant", "thai_restaurant", "japanese_restaurant",
    "italian_restaurant", "french_restaurant", "chinese_restaurant",
    "korean_restaurant", "american_restaurant", "indian_restaurant",
    "steak_house", "seafood_restaurant", "ramen_restaurant",
    "sushi_restaurant", "noodle_restaurant", "buffet_restaurant",
    "fine_dining_restaurant",
}
GMAPS_CAFE_TYPES = {
    "cafe", "coffee_shop", "dessert_shop", "bakery", "tea_house",
    "juice_shop",
}
GMAPS_KIOSK_TYPES = {"kiosk"}
GMAPS_STREET_FOOD_TYPES = {"street_food_gathering", "food_stand", "meal_takeaway"}
GMAPS_TAKEAWAY_TYPES = {"meal_takeaway", "fast_food_restaurant"}

# -- Cuisine / type keyword heuristics ----------------------------------------
CAFE_CUISINE_KEYWORDS = {
    "cafe", "coffee", "dessert", "bakery", "tea", "patisserie",
    "boulangerie", "brunch", "waffle", "crepe", "croissant", "smoothie",
    "bubble tea",
}
STREET_FOOD_CUISINE_KEYWORDS = {
    "street-food", "street food", "street_food", "streetfood",
    "food court", "hawker",
}
KIOSK_CUISINE_KEYWORDS = {"kiosk", "stall", "booth", "cart", "vendor"}
TAKEAWAY_CUISINE_KEYWORDS = {
    "takeaway", "take-away", "take away", "delivery only", "cloud kitchen",
}

# -- Name-pattern heuristics --------------------------------------------------
_KIOSK_NAME_PATTERNS = re.compile(
    r"(kiosk|\u0e23\u0e49\u0e32\u0e19\u0e40\u0e25\u0e47\u0e01|\u0e41\u0e1c\u0e07\u0e25\u0e2d\u0e22|\u0e23\u0e16\u0e40\u0e02\u0e47\u0e19|\u0e23\u0e34\u0e21\u0e17\u0e32\u0e07|food.?cart|booth|stall)",
    re.IGNORECASE,
)
_STREET_NAME_PATTERNS = re.compile(
    r"(street.?food|\u0e2a\u0e15\u0e23\u0e35\u0e17\u0e1f\u0e39\u0e49\u0e14|\u0e2b\u0e32\u0e1a\u0e40\u0e23\u0e48|\u0e41\u0e1c\u0e07\u0e02\u0e32\u0e22|night.?market|\u0e02\u0e2d\u0e07\u0e01\u0e34\u0e19|\u0e40\u0e14\u0e34\u0e19\u0e01\u0e34\u0e19)",
    re.IGNORECASE,
)
_TAKEAWAY_NAME_PATTERNS = re.compile(
    r"(takeaway|take.?away|\u0e2a\u0e48\u0e07\u0e2d\u0e32\u0e2b\u0e32\u0e23|cloud.?kitchen|dark.?kitchen|grab.?food.?only)",
    re.IGNORECASE,
)
_FOOD_STAND_NAME_PATTERNS = re.compile(
    r"(food.?stand|stand.?food|\u0e41\u0e1c\u0e07\u0e2d\u0e32\u0e2b\u0e32\u0e23|\u0e1a\u0e39\u0e18|\u0e0b\u0e38\u0e49\u0e21\u0e2d\u0e32\u0e2b\u0e32\u0e23|\u0e40\u0e15\u0e47\u0e19\u0e17\u0e4c)",
    re.IGNORECASE,
)


def _normalise(s):
    return (s or "").strip().lower()


def _gmaps_venue_type(gmaps_types):
    """Map Google Maps types list to venue_type string. Returns None if no match."""
    if not gmaps_types:
        return None
    types_set = {t.lower() for t in gmaps_types}
    if types_set & GMAPS_KIOSK_TYPES:
        return "kiosk"
    if types_set & GMAPS_STREET_FOOD_TYPES:
        return "street_food"
    if types_set & GMAPS_CAFE_TYPES and not (types_set & GMAPS_RESTAURANT_TYPES):
        return "cafe"
    if types_set & GMAPS_RESTAURANT_TYPES:
        return "restaurant"
    if types_set & GMAPS_TAKEAWAY_TYPES:
        return "takeaway_only"
    return None


def _cuisine_venue_type(cuisine, type_field):
    """Derive venue_type from cuisine / type strings."""
    c = _normalise(cuisine)
    t = _normalise(type_field)
    combined = c + " " + t
    for kw in KIOSK_CUISINE_KEYWORDS:
        if kw in combined:
            return "kiosk"
    for kw in STREET_FOOD_CUISINE_KEYWORDS:
        if kw in combined:
            return "street_food"
    for kw in TAKEAWAY_CUISINE_KEYWORDS:
        if kw in combined:
            return "takeaway_only"
    for kw in CAFE_CUISINE_KEYWORDS:
        if kw in combined:
            return "cafe"
    return None


def _name_venue_type(name):
    """Derive venue_type from restaurant name heuristics."""
    if _KIOSK_NAME_PATTERNS.search(name):
        return "kiosk"
    if _STREET_NAME_PATTERNS.search(name):
        return "street_food"
    if _TAKEAWAY_NAME_PATTERNS.search(name):
        return "takeaway_only"
    if _FOOD_STAND_NAME_PATTERNS.search(name):
        return "food_stand"
    return None


def _infer_province_from_area(area):
    """
    Given an area string, return (city, province).
    Bangkok neighbourhood  ->  ("Bangkok", "Bangkok")
    Known out-of-scope     ->  ("", province_name)
    Unknown                ->  ("", "")
    """
    a = _normalise(area)
    if a in BANGKOK_AREAS:
        return ("Bangkok", "Bangkok")
    for prov in OUT_OF_SCOPE_PROVINCES:
        if prov in a or a in prov:
            return ("", prov.title())
    if "bangkok" in a or "\u0e01\u0e23\u0e38\u0e07\u0e40\u0e17\u0e1e" in area:
        return ("Bangkok", "Bangkok")
    return ("", "")


def classify_record(record):
    """
    Enrich a restaurant record dict with classification fields.

    Accepts any record from export_signals.py, scrape_gmaps.py, or
    the curated CM_RESTAURANTS list.

    Returns a NEW dict (does not mutate the input).
    """
    r = dict(record)

    name        = r.get("name") or r.get("name_en") or ""
    cuisine     = r.get("cuisine") or ""
    type_field  = r.get("type") or ""
    area        = r.get("area") or ""
    gmaps_types = r.get("gmaps_types") or []

    # 1. Geo fields -----------------------------------------------------------
    # Re-derive from area (overrides stale empty strings from a prior run).
    # Only keep an existing value if it is non-empty AND non-None.
    city_derived, province_derived = _infer_province_from_area(area)
    city     = r["city"]     if r.get("city")     else city_derived
    province = r["province"] if r.get("province") else province_derived

    r["city"]     = city
    r["province"] = province
    r["country"]  = "Thailand"

    # 2. Venue type -----------------------------------------------------------
    RESTAURANT_TYPE_VALUES = {
        "fine-dining", "casual-dining", "casual", "local", "omakase",
        "steakhouse", "seafood", "thai", "japanese", "korean", "italian",
        "french", "chinese", "indian", "ramen", "noodle", "bbq", "hotpot",
        "bar-and-grill", "isaan", "fusion", "western", "mediterranean",
        "mexican", "vietnamese", "singaporean", "halal", "vegetarian",
        "vegan", "bar", "izakaya", "yakiniku", "teppanyaki", "dim-sum",
        "shabu", "sukiyaki",
    }
    vt = (
        _gmaps_venue_type(gmaps_types)
        or _cuisine_venue_type(cuisine, type_field)
        or _name_venue_type(name)
    )
    if vt is None:
        t_norm = _normalise(type_field)
        c_norm = _normalise(cuisine)
        if t_norm in RESTAURANT_TYPE_VALUES:
            vt = "restaurant"
        elif any(kw in c_norm for kw in [
            "thai", "japanese", "korean", "italian", "french", "chinese",
            "indian", "omakase", "steakhouse", "seafood", "ramen", "noodle",
            "isaan", "fusion", "western", "bar",
        ]):
            vt = "restaurant"
        else:
            # "Other" cuisine or truly ambiguous — unknown but may still be Bangkok
            vt = "unknown"

    r["venue_type"] = vt

    # 3. Scope market + focus flags -------------------------------------------
    is_bangkok          = (province == "Bangkok" or city == "Bangkok")
    is_restaurant_focus = vt in ("restaurant", "cafe")

    if not city and not province:
        # Cannot determine location at all
        scope_market        = "needs_review"
        exclude_reason      = "missing_location"
        is_bangkok          = False
        is_restaurant_focus = False

    elif not is_bangkok:
        # Outside Bangkok → out of scope for default discovery
        scope_market        = "out_of_scope_location"
        exclude_reason      = "province_not_bangkok"
        is_restaurant_focus = False

    elif vt == "kiosk":
        scope_market        = "out_of_scope_format"
        exclude_reason      = "kiosk_format"
        is_restaurant_focus = False

    elif vt == "street_food":
        scope_market        = "out_of_scope_format"
        exclude_reason      = "street_food_format"
        is_restaurant_focus = False

    elif vt == "food_stand":
        scope_market        = "out_of_scope_format"
        exclude_reason      = "food_stand_format"
        is_restaurant_focus = False

    elif vt == "takeaway_only":
        scope_market        = "out_of_scope_format"
        exclude_reason      = "takeaway_only"
        is_restaurant_focus = False

    elif vt == "unknown":
        # Bangkok location, no explicit exclusion signal.
        # Include in default output but flag for manual review.
        # These are typically scraped records where the DB has cuisine="Other"
        # with no GMaps types yet — not confirmed non-restaurants.
        scope_market        = "needs_review"
        exclude_reason      = "unclear_format"
        is_restaurant_focus = True   # shown by default; improve via gmaps_types later

    elif vt == "restaurant":
        scope_market        = "bangkok_restaurant_focus"
        exclude_reason      = None

    elif vt == "cafe":
        scope_market        = "bangkok_cafe_focus"
        exclude_reason      = None
        is_restaurant_focus = True

    else:
        scope_market        = "needs_review"
        exclude_reason      = "unclear_format"
        is_restaurant_focus = False

    r["scope_market"]        = scope_market
    r["is_bangkok_focus"]    = is_bangkok
    r["is_restaurant_focus"] = is_restaurant_focus
    r["exclude_reason"]      = exclude_reason

    return r


def classify_all(records):
    """Classify a list of records. Returns new list (does not mutate originals)."""
    return [classify_record(r) for r in records]


def needs_review_list(records):
    """Return records flagged for manual review (scope_market == 'needs_review')."""
    return [r for r in records if r.get("scope_market") == "needs_review"]


def excluded_list(records):
    """Return records excluded from the default discovery view."""
    return [r for r in records if not r.get("is_restaurant_focus")]


# -- CLI debug helper ---------------------------------------------------------
if __name__ == "__main__":
    import json, pathlib, sys
    from collections import Counter

    export_path = pathlib.Path(__file__).parent / "export_restaurants.json"
    if not export_path.exists():
        print("export_restaurants.json not found — run export_signals.py first")
        sys.exit(1)

    with open(export_path, encoding="utf-8") as f:
        records = json.load(f)

    classified = classify_all(records)

    restaurant_samples = [r for r in classified if r.get("venue_type") == "restaurant"][:3]
    excluded_samples   = [r for r in classified if r.get("venue_type") in
                          ("kiosk", "street_food", "food_stand")][:3]
    review_samples     = needs_review_list(classified)[:3]

    total      = len(classified)
    in_scope   = sum(1 for r in classified if r.get("is_restaurant_focus"))
    out_scope  = total - in_scope
    bkk_only   = sum(1 for r in classified if r.get("is_bangkok_focus"))
    review_cnt = sum(1 for r in classified if r.get("scope_market") == "needs_review")

    print("\n=== CLASSIFICATION REPORT ===")
    print(f"  Total records     : {total}")
    print(f"  In-scope (show)   : {in_scope}")
    print(f"  Out-of-scope      : {out_scope}")
    print(f"  Bangkok focus     : {bkk_only}")
    print(f"  Needs review      : {review_cnt}")

    vt_counts = Counter(r.get("venue_type") for r in classified)
    sm_counts = Counter(r.get("scope_market") for r in classified)
    ex_counts = Counter(r.get("exclude_reason") for r in classified if not r.get("is_restaurant_focus"))
    print("\n  venue_type breakdown:")
    for k, v in vt_counts.most_common():
        print(f"    {str(k):<25} : {v}")
    print("\n  scope_market breakdown:")
    for k, v in sm_counts.most_common():
        print(f"    {str(k):<35} : {v}")
    print("\n  exclude_reason breakdown (out-of-scope only):")
    for k, v in ex_counts.most_common():
        print(f"    {str(k):<30} : {v}")

    print("\n--- 3 restaurant samples ---")
    for r in restaurant_samples:
        print(f"  {r['name'][:40]:<40} | venue={r['venue_type']:<12} | scope={r['scope_market']}")

    print("\n--- 3 excluded (kiosk/street/food_stand) ---")
    for r in excluded_samples:
        print(f"  {r['name'][:40]:<40} | venue={r['venue_type']:<12} | reason={r.get('exclude_reason')}")

    print("\n--- 3 needs_review samples ---")
    for r in review_samples:
        print(f"  {r['name'][:40]:<40} | venue={r['venue_type']:<12} | bkk={r.get('is_bangkok_focus')} | shown={r.get('is_restaurant_focus')}")
