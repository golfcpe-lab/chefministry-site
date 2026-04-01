"""
ChefMinistry — Weekly Signal Update Script
รันทุกวันพุธผ่าน GitHub Actions
- ค้นหา YouTube video ล่าสุดจาก influencer channels
- ค้นหา YouTube keyword search สำหรับร้านในฐานข้อมูล
- อัปเดต overlapSignal, trendVelocity, signalStrength ใน js/data.js
"""

import os, re, json, requests, datetime
from collections import defaultdict

# ─── CONFIG ──────────────────────────────────────────────────────────────────

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
DATA_JS_PATH    = "js/data.js"
DAYS_LOOKBACK   = 30   # ขยายเป็น 30 วัน

# YouTube channels ที่ติดตาม
YOUTUBE_CHANNELS = {
    "i01": {"name": "Peach Eat Laek",  "channel_id": "UC8jdjGFODrFuR3e-HTmcsAw"},
    "i06": {"name": "Mark Wiens",       "channel_id": "UCnTsM_Q4nKJOGCyBAbKOA6Q"},
}

# Keyword searches เพิ่มเติม — ค้นหาทั่ว YouTube ไม่จำกัด channel
YOUTUBE_KEYWORD_SEARCHES = [
    "ร้านอาหาร กรุงเทพ รีวิว",
    "Bangkok restaurant review Thai food",
    "fine dining bangkok 2026",
    "ไก่ทอดโปโล",
    "Jay Fai bangkok",
    "Le Du restaurant",
    "Gaggan Bangkok",
    "Somtum Der review",
    "street food bangkok new",
    "อาหารไทย รีวิว 2026",
    # Omakase
    "omakase bangkok 2026",
    "sushi omakase กรุงเทพ รีวิว",
    "Sushi Masato Bangkok",
    "Sushi Ichizu Bangkok",
    "Ginza Sushi Ichi Bangkok",
    "โอมากาเสะ กรุงเทพ ใหม่",
    # Pizza
    "Maru Maru Pizza Bangkok",
    "มารุมารุ พิซซ่า รีวิว",
    "Pizza Massilia Bangkok",
    # Ramen
    "Sendo Ramen Bangkok รีวิว",
    "Shindo Ramen ศาลายา รีวิว",
    "ราเมน กรุงเทพ เปิดใหม่ 2026",
]

# restaurant name → restaurant id mapping
RESTAURANT_ID_MAP = {
    "gaggan":            "r001",
    "le du":             "r002",
    "jay fai":           "r003",
    "เจ๊ไฝ":             "r003",
    "ไก่ทอดโปโล":       "r004",
    "polo fried chicken":"r004",
    "polo":              "r004",
    "sühring":           "r005",
    "suhring":           "r005",
    "supanniga":         "r006",
    "somtum der":        "r007",
    "ส้มตำดอ":           "r007",
    "shuggi":            "r008",
    "err":               "r009",
    "nusara":            "r010",
    "potong":            "r011",
    "80/20":             "r012",
    "saawaan":           "r013",
    "สวรรค์":            "r013",
    "nahm":              "r014",
    "paste":             "r015",
    # Omakase
    "sushi masato":      "r016",
    "masato":            "r016",
    "sushi ichizu":      "r017",
    "ichizu":            "r017",
    "ginza sushi ichi":  "r018",
    "sushi ichi":        "r018",
    # Pizza (new)
    "maru maru":         "r025",
    "marumarupizza":     "r025",
    "มารุมารุ":         "r025",
    "pizza massilia":    "r021",
    "massilia":          "r021",
    "motorino":          "r022",
    # Ramen (new)
    "sendo ramen":       "r026",
    "sendo":             "r026",
    "shindo ramen":      "r027",
    "shindo":            "r027",
}

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def since_iso(days: int) -> str:
    dt = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def read_data_js() -> str:
    with open(DATA_JS_PATH, encoding="utf-8") as f:
        return f.read()

def write_data_js(content: str):
    with open(DATA_JS_PATH, "w", encoding="utf-8") as f:
        f.write(content)

def extract_restaurant_names(text: str) -> list:
    found = []
    text_lower = text.lower()
    for keyword, r_id in RESTAURANT_ID_MAP.items():
        if keyword.lower() in text_lower:
            if r_id not in found:
                found.append(r_id)
    return found

def youtube_get(endpoint: str, params: dict) -> dict:
    params["key"] = YOUTUBE_API_KEY
    r = requests.get(
        f"https://www.googleapis.com/youtube/v3/{endpoint}",
        params=params, timeout=15
    )
    r.raise_for_status()
    return r.json()

# ─── YOUTUBE CHANNEL SEARCH ──────────────────────────────────────────────────

def search_channel(channel_id: str, inf_id: str, name: str) -> list:
    print(f"  → {name} (channel search)")
    try:
        data = youtube_get("search", {
            "channelId":      channel_id,
            "part":           "snippet",
            "order":          "date",
            "maxResults":     10,
            "publishedAfter": since_iso(DAYS_LOOKBACK),
            "type":           "video",
        })
        return _parse_items(data.get("items", []), inf_id)
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return []

# ─── YOUTUBE KEYWORD SEARCH ───────────────────────────────────────────────────

def search_keyword(query: str) -> list:
    print(f"  → keyword: \"{query}\"")
    try:
        data = youtube_get("search", {
            "q":              query,
            "part":           "snippet",
            "order":          "date",
            "maxResults":     10,
            "publishedAfter": since_iso(DAYS_LOOKBACK),
            "type":           "video",
            "relevanceLanguage": "th",
            "regionCode":     "TH",
        })
        # keyword search = influencer unknown → use "kw" as placeholder
        return _parse_items(data.get("items", []), inf_id="kw")
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return []

def _parse_items(items: list, inf_id: str) -> list:
    results = []
    for item in items:
        snip = item.get("snippet", {})
        text = snip.get("title", "") + " " + snip.get("description", "")
        r_ids = extract_restaurant_names(text)
        if r_ids:
            results.append({
                "influencer_id": inf_id,
                "title":         snip.get("title", "")[:80],
                "restaurant_ids": r_ids,
                "published":     snip.get("publishedAt", ""),
            })
            print(f"    ✓ {snip.get('title','')[:60]} → r_ids={r_ids}")
    return results

# ─── SIGNAL UPDATE LOGIC ─────────────────────────────────────────────────────

def compute_overlap(mentions: list) -> dict:
    """{ restaurant_id: set_of_influencer_ids }"""
    overlap = defaultdict(set)
    for m in mentions:
        for r_id in m["restaurant_ids"]:
            overlap[r_id].add(m["influencer_id"])
    return overlap

def signal_strength(overlap: int) -> tuple:
    if overlap >= 6: return "very-strong", "rising",   "↑ Rising"
    if overlap >= 4: return "strong",       "rising",   "↑ Rising"
    if overlap >= 2: return "moderate",     "stable",   "→ Stable"
    return               "weak",        "declining","↓ Declining"

def update_js_field(js: str, r_id: str, field: str, value: str) -> str:
    pattern = rf'(id:"{r_id}".*?{re.escape(field)}:\s*")([^"]+)(")'
    replacement = lambda m: m.group(1) + value + m.group(3)
    return re.sub(pattern, replacement, js, flags=re.DOTALL)

def update_js_number(js: str, r_id: str, field: str, value: int) -> str:
    pattern = rf'(id:"{r_id}".*?{re.escape(field)}:\s*)(\d+)'
    replacement = lambda m: m.group(1) + str(value)
    return re.sub(pattern, replacement, js, flags=re.DOTALL)

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    today = datetime.date.today().isoformat()
    print(f"\n{'='*55}")
    print(f"ChefMinistry Signal Update — {today}")
    print(f"{'='*55}\n")

    if not YOUTUBE_API_KEY:
        print("⚠️  YOUTUBE_API_KEY not set — skipping all YouTube searches")
        print("   data.js unchanged.\n")
        return

    all_mentions = []

    # 1. Channel search
    print("📡 Channel search (known influencers)...")
    for inf_id, info in YOUTUBE_CHANNELS.items():
        results = search_channel(info["channel_id"], inf_id, info["name"])
        all_mentions.extend(results)

    # 2. Keyword search
    print("\n🔍 Keyword search (broad YouTube)...")
    for query in YOUTUBE_KEYWORD_SEARCHES:
        results = search_keyword(query)
        all_mentions.extend(results)

    # 3. Deduplicate
    seen = set()
    unique = []
    for m in all_mentions:
        key = (m["influencer_id"], tuple(sorted(m["restaurant_ids"])), m["title"])
        if key not in seen:
            seen.add(key)
            unique.append(m)
    all_mentions = unique

    print(f"\n📊 Total unique mentions found: {len(all_mentions)}")

    if not all_mentions:
        print("  No new restaurant mentions this week — data.js unchanged.\n")
        return

    # 4. Compute overlap per restaurant
    overlap_map = compute_overlap(all_mentions)

    # 5. Update data.js
    js = read_data_js()
    changes = []

    for r_id, reviewer_ids in overlap_map.items():
        n = len(reviewer_ids)
        strength, velocity, badge = signal_strength(n)

        js = update_js_number(js, r_id, "overlapSignal", n)
        js = update_js_field(js, r_id, "signalStrength", strength)
        js = update_js_field(js, r_id, "trendVelocity",  velocity)
        js = update_js_field(js, r_id, "trendBadge",     badge)

        changes.append(f"  {r_id}: overlap={n}, strength={strength}, velocity={velocity}")
        print(f"  ✓ Updated {r_id}")

    write_data_js(js)

    print(f"\n✅ data.js updated — {len(changes)} restaurant(s) changed:")
    for c in changes:
        print(c)
    print()

if __name__ == "__main__":
    main()
