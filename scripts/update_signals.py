"""
ChefMinistry — Weekly Signal Update Script
รันทุกวันพุธผ่าน GitHub Actions
- ค้นหา YouTube video ล่าสุดจาก influencer ที่ติดตาม
- อัปเดต overlapSignal, trendVelocity, signalStrength ใน js/data.js
"""

import os, re, json, requests, datetime
from collections import defaultdict

# ─── CONFIG ──────────────────────────────────────────────────────────────────

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
DATA_JS_PATH    = "js/data.js"
DAYS_LOOKBACK   = 10   # นับ review ย้อนหลัง N วัน

# Influencer ที่มี YouTube channel — ค้นหาได้ตรงจาก API
YOUTUBE_CHANNELS = {
    "i01": {"name": "Peach Eat Laek",  "channel_id": "UC8jdjGFODrFuR3e-HTmcsAw"},
    "i06": {"name": "Mark Wiens",       "channel_id": "UCnTsM_Q4nKJOGCyBAbKOA6Q"},
}

# Influencer ทั้งหมด (ใช้ search fallback สำหรับ TikTok/Facebook)
ALL_INFLUENCERS = {
    "i01": "Peach Eat Laek",
    "i02": "icesy168",
    "i03": "พี่จ่า peeja_pachim",
    "i04": "bewvaraporn",
    "i05": "มหาชนี จุ๊บจิ๊บ",
    "i06": "Mark Wiens Bangkok",
    "i07": "Qunfoh food",
    "i08": "GUN ASMR Thailand",
    "i09": "Kodtap Moo ร้านอาหาร",
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

def extract_restaurant_names(text: str) -> list[str]:
    """ดึงชื่อร้านที่อาจถูก mention จาก title/description"""
    known = [
        "Gaggan", "Le Du", "Jay Fai", "ไก่ทอดโปโล", "Polo",
        "Sühring", "Supanniga", "Somtum Der", "Shuggi",
        "Err", "Nusara", "Potong", "80/20", "Saawaan",
        "Nahm", "Paste", "Canvas"
    ]
    found = []
    for r in known:
        if r.lower() in text.lower():
            found.append(r)
    return found

# ─── YOUTUBE SEARCH ──────────────────────────────────────────────────────────

def search_youtube(channel_id: str, influencer_id: str) -> list[dict]:
    """ค้นหา video ล่าสุดจาก YouTube channel"""
    if not YOUTUBE_API_KEY:
        print(f"  ⚠️  No YOUTUBE_API_KEY — skipping YouTube search")
        return []

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key":        YOUTUBE_API_KEY,
        "channelId":  channel_id,
        "part":       "snippet",
        "order":      "date",
        "maxResults": 5,
        "publishedAfter": since_iso(DAYS_LOOKBACK),
        "type":       "video",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        items = r.json().get("items", [])
        results = []
        for item in items:
            title = item["snippet"]["title"]
            desc  = item["snippet"]["description"]
            restaurants = extract_restaurant_names(title + " " + desc)
            if restaurants:
                results.append({
                    "influencer_id": influencer_id,
                    "title":         title,
                    "restaurants":   restaurants,
                    "published":     item["snippet"]["publishedAt"],
                })
                print(f"  ✓ Found: {title[:60]} → {restaurants}")
        return results
    except Exception as e:
        print(f"  ✗ YouTube API error: {e}")
        return []

# ─── SIGNAL UPDATE LOGIC ─────────────────────────────────────────────────────

def compute_new_signals(mentions: list[dict]) -> dict:
    """
    จาก mentions ที่พบ → คำนวณ overlapSignal ใหม่ต่อร้าน
    Returns: { restaurant_keyword: set_of_influencer_ids }
    """
    restaurant_reviewers = defaultdict(set)
    for m in mentions:
        for r in m["restaurants"]:
            restaurant_reviewers[r.lower()].add(m["influencer_id"])
    return restaurant_reviewers

def signal_strength(overlap: int) -> tuple[str, str]:
    if overlap >= 6: return "very-strong", "↑ Rising"
    if overlap >= 4: return "strong",       "↑ Rising"
    if overlap >= 2: return "moderate",     "→ Stable"
    return "weak", "↓ Declining"

def update_restaurant_in_js(js: str, r_id: str, new_overlap: int,
                             new_reviewers: list[str]) -> str:
    """อัปเดต overlapSignal + signalStrength + trendVelocity + trendBadge"""
    strength, badge = signal_strength(new_overlap)
    velocity = "rising" if new_overlap >= 4 else "stable" if new_overlap >= 2 else "declining"

    # overlapSignal
    js = re.sub(
        rf'(id:"{r_id}".*?overlapSignal:\s*)\d+',
        lambda m: m.group(1) + str(new_overlap),
        js, flags=re.DOTALL
    )
    # signalStrength
    js = re.sub(
        rf'(id:"{r_id}".*?signalStrength:\s*")[^"]+(")',
        lambda m: m.group(1) + strength + m.group(2),
        js, flags=re.DOTALL
    )
    # trendVelocity
    js = re.sub(
        rf'(id:"{r_id}".*?trendVelocity:\s*")[^"]+(")',
        lambda m: m.group(1) + velocity + m.group(2),
        js, flags=re.DOTALL
    )
    # trendBadge
    js = re.sub(
        rf'(id:"{r_id}".*?trendBadge:\s*")[^"]+(")',
        lambda m: m.group(1) + badge + m.group(2),
        js, flags=re.DOTALL
    )
    return js

# ─── RESTAURANT ID MAP ───────────────────────────────────────────────────────

RESTAURANT_ID_MAP = {
    "gaggan":       "r001",
    "le du":        "r002",
    "jay fai":      "r003",
    "ไก่ทอดโปโล":  "r004",
    "polo":         "r004",
    "sühring":      "r005",
    "supanniga":    "r006",
    "somtum der":   "r007",
}

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    today = datetime.date.today().isoformat()
    print(f"\n{'='*55}")
    print(f"ChefMinistry Signal Update — {today}")
    print(f"{'='*55}\n")

    all_mentions = []

    # 1. YouTube search (Peach + Mark Wiens)
    print("📡 Searching YouTube channels...")
    for inf_id, info in YOUTUBE_CHANNELS.items():
        print(f"  → {info['name']}")
        results = search_youtube(info["channel_id"], inf_id)
        all_mentions.extend(results)

    # 2. Summary
    print(f"\n📊 Mentions found: {len(all_mentions)}")
    if not all_mentions:
        print("  No new restaurant mentions detected this week.")
        print("  data.js unchanged.\n")
        return

    # 3. Map mentions to restaurants
    restaurant_reviewers = compute_new_signals(all_mentions)

    # 4. Update data.js
    js = read_data_js()
    changes = []

    for keyword, reviewer_ids in restaurant_reviewers.items():
        r_id = RESTAURANT_ID_MAP.get(keyword)
        if not r_id:
            print(f"  ⚠️  Restaurant '{keyword}' not in ID map — skipping")
            continue

        new_overlap = len(reviewer_ids)
        new_reviewers = list(reviewer_ids)
        js = update_restaurant_in_js(js, r_id, new_overlap, new_reviewers)
        strength, badge = signal_strength(new_overlap)
        changes.append(f"  {r_id} — overlap={new_overlap}, strength={strength}, badge={badge}")
        print(f"  ✓ Updated {r_id}: overlap={new_overlap}")

    write_data_js(js)

    print(f"\n✅ data.js updated — {len(changes)} restaurant(s) changed:")
    for c in changes:
        print(c)
    print()

if __name__ == "__main__":
    main()
