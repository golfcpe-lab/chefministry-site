#!/usr/bin/env python3
"""
ChefMinistry — Inject YouTube Reviews → data.js
รันก่อน weekly_summary.py ใน GitHub Actions

งาน:
  1. ร้านที่มีอยู่แล้ว → เพิ่ม overlapSignal, signalCount, trendVelocity
  2. ร้านใหม่ที่ไม่มีใน list → ใช้ OpenAI generate entry เพิ่มเข้า CM_RESTAURANTS
  3. อัปเดต trendCategories จาก YouTube cuisine data จริง

รัน:
  python inject_youtube.py
  python inject_youtube.py --dry-run    # preview โดยไม่บันทึก
"""

import os, re, json, pathlib, datetime, argparse
from collections import defaultdict
from openai import OpenAI

# ── Paths ──────────────────────────────────────────────────────────────────────
HERE         = pathlib.Path(__file__).parent
SCRIPTS_DIR  = pathlib.Path(os.environ.get("SCRIPTS_DIR", str(HERE.parent)))
DATA_FILE    = pathlib.Path(os.environ.get("DATA_FILE",   str(HERE.parent / "site" / "js" / "data.js")))
YOUTUBE_FILE = pathlib.Path(os.environ.get("YOUTUBE_FILE", str(SCRIPTS_DIR / "youtube_reviews.json")))

def _load_env():
    env_file = HERE.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
_load_env()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

# ── Cuisine → trendCategory mapping ───────────────────────────────────────────
CUISINE_TO_CAT = {
    "thai fine dining": "Thai Fine Dining",
    "modern thai":      "Thai Fine Dining",
    "thai":             "Thai Fine Dining",
    "japanese":         "Japanese Omakase",
    "omakase":          "Japanese Omakase",
    "sushi":            "Japanese Omakase",
    "ramen":            "Artisan Ramen",
    "street food":      "Thai Street Food",
    "thai street food": "Thai Street Food",
    "pizza":            "Neapolitan Pizza",
    "italian":          "Neapolitan Pizza",
    "steakhouse":       "Steakhouse",
    "steak":            "Steakhouse",
    "farm-to-table":    "Farm-to-Table",
    "organic":          "Farm-to-Table",
    "hot pot":          "Hot Pot / Suki",
    "suki":             "Hot Pot / Suki",
}

SIGNAL_LEVELS = ["weak", "moderate", "strong", "very-strong"]

def normalize(name):
    return re.sub(r'[^a-zA-Zก-๙0-9\s]', '', name.lower()).strip()

def fuzzy_match(name, restaurant_list):
    """หา restaurant ใน list ที่ชื่อใกล้เคียงที่สุด"""
    norm = normalize(name)
    # exact match
    for r in restaurant_list:
        if normalize(r.get("name", "")) == norm:
            return r
    # partial match
    for r in restaurant_list:
        rn = normalize(r.get("name", ""))
        if norm in rn or rn in norm:
            return r
    # word overlap (≥2 words match)
    words = set(norm.split())
    for r in restaurant_list:
        rwords = set(normalize(r.get("name", "")).split())
        if len(words & rwords) >= 2:
            return r
    return None

def js_to_python(raw):
    raw = re.sub(r'//[^\n]*', '', raw)
    raw = re.sub(r'/\*.*?\*/', '', raw, flags=re.DOTALL)
    raw = re.sub(r',\s*([}\]])', r'\1', raw)
    raw = re.sub(r'(?<=[{,\[])\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:',
                 lambda m: f' "{m.group(1).strip()}":', raw)
    raw = raw.replace('true', 'True').replace('false', 'False').replace('null', 'None')
    return raw

def extract_restaurants(js_text):
    # หา index ของ [ เปิด แล้วนับ bracket จนปิด — ป้องกัน ]; ใน string value
    m = re.search(r'const CM_RESTAURANTS\s*=\s*\[', js_text, re.DOTALL)
    if not m:
        return []
    start = m.end() - 1  # ชี้ที่ [
    depth, i, in_str, esc = 0, start, False, False
    while i < len(js_text):
        ch = js_text[i]
        if esc:
            esc = False
        elif ch == '\\' and in_str:
            esc = True
        elif ch == '"' and not esc:
            in_str = not in_str
        elif not in_str:
            if ch == '[':   depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    break
        i += 1
    arr_text = js_text[start:i+1]
    try:
        return eval(js_to_python(arr_text))
    except Exception as e:
        print(f"  ⚠️  extract_restaurants eval error: {e}")
        return []

def signal_strength(overlap, count):
    if overlap >= 5 or count >= 9:  return "very-strong"
    if overlap >= 3 or count >= 6:  return "strong"
    if overlap >= 2 or count >= 3:  return "moderate"
    return "weak"

def trend_badge(velocity):
    return {"rising": "↑ Rising", "declining": "↓ Declining"}.get(velocity, "→ Stable")

# ── Update existing restaurant signals ────────────────────────────────────────
def update_restaurant_in_js(js_text, restaurant_name, delta_overlap, delta_count, new_velocity):
    """อัปเดต signal fields ของร้านใน JS text ด้วย regex"""
    # หา block ของร้านนี้ด้วยชื่อ
    escaped = re.escape(restaurant_name)
    # pattern ครอบ id:"rXXX" ... ถึง closing }
    block_pattern = re.compile(
        r'(\{[^{}]*?name\s*:\s*["\']' + escaped + r'["\'][^{}]*?\})',
        re.DOTALL
    )
    match = block_pattern.search(js_text)
    if not match:
        return js_text, False

    block = match.group(1)
    orig_block = block

    # อ่านค่าเดิม
    def get_int(field, text, default=0):
        m = re.search(rf'{field}\s*:\s*(\d+)', text)
        return int(m.group(1)) if m else default

    def get_str(field, text, default=""):
        m = re.search(rf'{field}\s*:\s*["\']([^"\']*)["\']', text)
        return m.group(1) if m else default

    old_overlap = get_int("overlapSignal", block)
    old_count   = get_int("signalCount",   block)
    old_total   = get_int("totalReviews",  block)

    new_overlap = old_overlap + delta_overlap
    new_count   = old_count   + delta_count
    new_total   = old_total   + delta_count
    new_strength = signal_strength(new_overlap, new_count)
    new_badge    = trend_badge(new_velocity)

    # replace fields
    def sub_int(field, new_val, text):
        return re.sub(rf'({field}\s*:\s*)\d+', rf'\g<1>{new_val}', text)
    def sub_str(field, new_val, text):
        return re.sub(rf'({field}\s*:\s*)["\'][^"\']*["\']', rf'\1"{new_val}"', text)

    block = sub_int("overlapSignal", new_overlap,  block)
    block = sub_int("signalCount",   new_count,    block)
    block = sub_int("totalReviews",  new_total,    block)
    block = sub_str("signalStrength", new_strength, block)
    block = sub_str("trendVelocity",  new_velocity, block)
    block = sub_str("trendBadge",     new_badge,    block)

    js_text = js_text.replace(orig_block, block, 1)
    return js_text, True

# ── CM_EXTERNAL_RESTAURANTS helpers ───────────────────────────────────────────
def _find_bracket_end(text, start):
    """นับ bracket จาก start จนถึงปิด — คืน index ของ bracket ปิดสุดท้าย"""
    depth, i, in_str, esc = 0, start, False, False
    while i < len(text):
        c = text[i]
        if esc:     esc = False
        elif c == '\\' and in_str: esc = True
        elif c == '"': in_str = not in_str
        elif not in_str:
            if c in '[{':   depth += 1
            elif c in ']}':
                depth -= 1
                if depth == 0: return i
        i += 1
    return -1

def extract_external_restaurants(js_text):
    """ดึง CM_EXTERNAL_RESTAURANTS array (JSON) พร้อม start/end index"""
    m = re.search(r'const CM_EXTERNAL_RESTAURANTS\s*=\s*\[', js_text)
    if not m:
        return [], -1, -1
    start = m.end() - 1  # ชี้ที่ [
    end   = _find_bracket_end(js_text, start)
    if end == -1:
        return [], -1, -1
    try:
        return json.loads(js_text[start:end+1]), start, end
    except Exception as e:
        print(f"  ⚠️  parse CM_EXTERNAL error: {e}")
        return [], start, end

def inject_influencer_to_external(ext_entry, influencers, new_velocity):
    """เพิ่ม influencer signal fields เข้า CM_EXTERNAL_RESTAURANTS entry"""
    mega  = sum(1 for i in influencers if i.get("tier") == "Mega")
    macro = sum(1 for i in influencers if i.get("tier") == "Macro")
    mid   = sum(1 for i in influencers if i.get("tier") == "Mid")
    overlap = len(set(i["name"] for i in influencers))
    old_tiers = ext_entry.get("reviewerTiers", {"mega": 0, "macro": 0, "mid": 0})
    ext_entry["overlapSignal"]   = ext_entry.get("overlapSignal", 0) + overlap
    ext_entry["signalCount"]     = ext_entry.get("signalCount",   0) + overlap
    ext_entry["signalStrength"]  = signal_strength(ext_entry["overlapSignal"], ext_entry["signalCount"])
    ext_entry["trendVelocity"]   = new_velocity
    ext_entry["trendBadge"]      = trend_badge(new_velocity)
    ext_entry["reviewerTiers"]   = {
        "mega":  old_tiers.get("mega",  0) + mega,
        "macro": old_tiers.get("macro", 0) + macro,
        "mid":   old_tiers.get("mid",   0) + mid,
    }
    ext_entry["influencerNames"] = list(set(
        ext_entry.get("influencerNames", []) + [i["name"] for i in influencers]
    ))

def write_external_restaurants(js_text, ext_list, arr_start, arr_end):
    """เขียน CM_EXTERNAL_RESTAURANTS กลับเข้า data.js (แทนที่ JSON เดิม)"""
    new_json = json.dumps(ext_list, ensure_ascii=False, separators=(',', ':'))
    return js_text[:arr_start] + new_json + js_text[arr_end+1:]

# ── Generate new restaurant entry via OpenAI ──────────────────────────────────
NEW_REST_PROMPT = """คุณเป็น data generator สำหรับ ChefMinistry

สร้าง JavaScript object สำหรับร้านอาหารใหม่ในรูปแบบที่กำหนด
ตอบเป็น JSON เท่านั้น (ไม่มีข้อความอื่น):

{{
  "id": "{new_id}",
  "name": "{name}",
  "cuisine": "{cuisine}",
  "type": "fine-dining | casual-dining | ramen | street-food | steakhouse | omakase | cafe | casual | local",
  "budget": 1,
  "budgetLabel": "฿ | ฿฿ | ฿฿฿",
  "occasions": ["casual","date","special","business","family"],
  "area": "{area}",
  "priceRange": "เช่น 500–1,200",
  "emoji": "emoji ที่เหมาะสม 1 ตัว",
  "signalStrength": "{signal_strength}",
  "signalCount": {signal_count},
  "overlapSignal": {overlap},
  "trendVelocity": "rising",
  "trendBadge": "↑ Rising",
  "reviewerTiers": {{"mega": {mega}, "macro": {macro}, "mid": {mid}}},
  "recentReviewers": [],
  "bookingLinks": {{"googlemaps": "#", "wongnai": "#"}},
  "tags": ["tag1", "tag2"],
  "menuHighlights": ["เมนู 1", "เมนู 2", "เมนู 3"],
  "cmNote": "สรุปสั้นๆ ว่าทำไมร้านนี้ถึงน่าสนใจ (ภาษาไทย 1 ประโยค)",
  "totalReviews": {signal_count}
}}

ข้อมูลที่มี:
ชื่อร้าน: {name}
cuisine: {cuisine}
ย่าน: {area}
influencer ที่รีวิว: {influencers}
"""

def generate_new_restaurant_entry(name, cuisine, area, influencers, new_id):
    """ใช้ OpenAI สร้าง restaurant entry ใหม่"""
    mega  = sum(1 for i in influencers if i.get("tier") == "Mega")
    macro = sum(1 for i in influencers if i.get("tier") == "Macro")
    mid   = sum(1 for i in influencers if i.get("tier") == "Mid")
    overlap = len(influencers)
    count   = max(overlap, 1)
    strength = signal_strength(overlap, count)

    prompt = NEW_REST_PROMPT.format(
        new_id=new_id, name=name, cuisine=cuisine, area=area,
        signal_strength=strength, signal_count=count, overlap=overlap,
        mega=mega, macro=macro, mid=mid,
        influencers=", ".join(i["name"] for i in influencers),
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600,
        )
        text = resp.choices[0].message.content.strip()
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            return json.loads(m.group())
    except Exception as e:
        print(f"    ⚠️  OpenAI error: {e}")
    return None

def dict_to_js(d, indent=4):
    """แปลง Python dict → JS object syntax"""
    def val(v):
        if isinstance(v, bool):      return "true" if v else "false"
        if isinstance(v, int):       return str(v)
        if isinstance(v, float):     return str(v)
        if isinstance(v, str):       return json.dumps(v, ensure_ascii=False)
        if isinstance(v, list):
            items = ", ".join(val(i) for i in v)
            return f'[{items}]'
        if isinstance(v, dict):
            pairs = ", ".join(f'{k}:{val(vv)}' for k, vv in v.items())
            return f'{{{pairs}}}'
        return json.dumps(str(v), ensure_ascii=False)
    sp = " " * indent
    lines = ["{"]
    for k, v in d.items():
        lines.append(f"{sp}{k}:{val(v)},")
    lines.append("  }")
    return "\n  ".join(lines)

# ── Update trendCategories ─────────────────────────────────────────────────────
def update_trend_categories(js_text, cuisine_counts):
    """อัปเดต trendCategories ใน CM_SIGNALS จาก YouTube cuisine data"""
    if not cuisine_counts:
        return js_text

    # map cuisine → category
    cat_influencers = defaultdict(set)
    for cuisine, influencers in cuisine_counts.items():
        norm = cuisine.lower()
        cat = next((v for k, v in CUISINE_TO_CAT.items() if k in norm), None)
        if cat:
            cat_influencers[cat].update(influencers)

    if not cat_influencers:
        return js_text

    def update_cat_block(match):
        block = match.group(0)
        cat_m = re.search(r'cat\s*:\s*["\']([^"\']+)["\']', block)
        if not cat_m:
            return block
        cat_name = cat_m.group(1)
        if cat_name not in cat_influencers:
            return block
        count = len(cat_influencers[cat_name])
        # signal level
        sig = "very-strong" if count >= 6 else "strong" if count >= 4 else "rising" if count >= 2 else "stable"
        change = f"+{count * 8}%"
        block = re.sub(r'(signal\s*:\s*)["\'][^"\']*["\']', rf'\1"{sig}"',     block)
        block = re.sub(r'(change\s*:\s*)["\'][^"\']*["\']', rf'\1"{change}"', block)
        block = re.sub(r'(influencers\s*:\s*)\d+',          rf'\g<1>{count}',  block)
        return block

    # update each { cat:"...", signal:"...", ... } block
    js_text = re.sub(
        r'\{\s*cat\s*:\s*["\'][^"\']+["\'][^{}]*\}',
        update_cat_block,
        js_text,
        flags=re.DOTALL
    )
    return js_text

# ── Main ───────────────────────────────────────────────────────────────────────
def ingest_new_restaurant_to_db(name, cuisine, area):
    """เพิ่มร้านใหม่จาก YouTube เข้า DB ด้วยข้อมูลจริงจาก Google Places
    (แทนการ generate demo entry ด้วย OpenAI — เลิกใช้ 2026-07-13 เพราะได้
    คะแนน/รายละเอียดสังเคราะห์). ร้านจะโผล่บนเว็บผ่าน export รอบถัดไป
    และ Step 2 ของสคริปต์นี้จะติด influencer signal ให้ในสัปดาห์ถัดไป"""
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        try:
            from config import GOOGLE_MAPS_API_KEY as _k
            api_key = _k or ""
        except Exception:
            pass
    if not api_key:
        print("      ⚠️ ไม่มี GOOGLE_MAPS_API_KEY — ข้าม (รอเข้า DB ทาง seed/suggestion)")
        return False

    from db import init_db, upsert_restaurant, record_snapshot, get_conn
    from scrape_gmaps import find_place, get_place_details, save_gmaps_meta, load_blocklist
    from seed_discover import norm_name, extract_area

    init_db()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT external_id, gmaps_place_id, name FROM restaurants").fetchall()
    known_ids   = {r["external_id"] for r in rows} | {r["gmaps_place_id"] for r in rows if r["gmaps_place_id"]}
    known_names = {norm_name(r["name"]) for r in rows}
    if norm_name(name) in known_names:
        print("      ⏭ มีใน DB แล้ว — export รอบหน้าจะพาขึ้นเว็บเอง")
        return False

    place = find_place(name, area, api_key)
    if not place:
        print("      ❓ GMaps ไม่เจอ — ข้าม")
        return False
    pid   = place.get("id", "")
    found = (place.get("displayName") or {}).get("text", "")
    bl_ids, bl_names = load_blocklist()
    if not pid or pid in known_ids or pid in bl_ids or found.strip() in bl_names:
        print(f"      ⏭ ซ้ำ/blocklisted: {found}")
        return False

    details = get_place_details(pid, api_key) or {}
    urc    = int(details.get("userRatingCount") or place.get("userRatingCount") or 0)
    rating = float(details.get("rating") or place.get("rating") or 0)
    addr   = details.get("formattedAddress") or place.get("formattedAddress", "")
    status = details.get("businessStatus", "OPERATIONAL")
    loc    = details.get("location") or place.get("location") or {}
    pt     = details.get("primaryType") or place.get("primaryType") or ""
    gmaps_types = list(dict.fromkeys(([pt] if pt else []) + (details.get("types") or [])))
    if urc == 0 or status == "CLOSED_PERMANENTLY":
        print(f"      ❓ ไม่มีรีวิว/ปิดถาวร — ข้าม ({found})")
        return False

    rid = upsert_restaurant({
        "source": "gmaps", "external_id": pid,
        "name": found or name, "cuisine": cuisine or "Other",
        "area": extract_area(addr), "address": addr,
        "city": "Bangkok", "province": "Bangkok",
        "lat": loc.get("latitude"), "lng": loc.get("longitude"),
        "price_range": "2",
        "url": f"https://www.google.com/maps/place/?q=place_id:{pid}",
    })
    record_snapshot(rid, review_count=urc, rating=rating, rating_count=urc)
    save_gmaps_meta(rid, {
        "gmaps_place_id": pid, "gmaps_address": addr,
        "gmaps_types": gmaps_types,
        "gmaps_business_status": status or "OPERATIONAL",
        "gmaps_lat": loc.get("latitude"), "gmaps_lng": loc.get("longitude"),
    })
    print(f"      ✅ เข้า DB แล้ว: {found} ⭐{rating} ({urc:,} รีวิว)")
    return True


def main(dry_run=False):
    print(f"\n{'='*55}")
    print(f"  ChefMinistry — Inject YouTube → data.js")
    print(f"{'='*55}\n")

    if not YOUTUBE_FILE.exists():
        print("ℹ️  ไม่พบ youtube_reviews.json — ข้ามไป")
        return
    if not DATA_FILE.exists():
        raise SystemExit(f"❌ ไม่พบ {DATA_FILE}")

    yt_data  = json.loads(YOUTUBE_FILE.read_text(encoding="utf-8"))
    reviews  = yt_data.get("reviews", [])
    print(f"📺  YouTube reviews: {len(reviews)} รายการ\n")

    js_text  = DATA_FILE.read_text(encoding="utf-8")
    existing = extract_restaurants(js_text)
    existing_ids = [r.get("id","") for r in existing]
    next_num = max((int(re.sub(r'\D','', i)) for i in existing_ids if re.sub(r'\D','',i).isdigit()), default=0) + 1

    # โหลด CM_EXTERNAL_RESTAURANTS พร้อม position
    ext_list, ext_start, ext_end = extract_external_restaurants(js_text)
    ext_updated = False
    print(f"📦  CM_RESTAURANTS: {len(existing)} ร้าน | CM_EXTERNAL_RESTAURANTS: {len(ext_list)} ร้าน\n")

    # ── รวม reviews ต่อร้าน ──────────────────────────────────────────────────
    rest_map = defaultdict(lambda: {"influencers": [], "cuisines": [], "areas": []})
    cuisine_counts = defaultdict(set)

    for rv in reviews:
        name = rv.get("restaurant", "").strip()
        if not name:
            continue
        entry = rest_map[name]
        inf = {"name": rv.get("influencer",""), "tier": rv.get("tier","Mid")}
        if inf not in entry["influencers"]:
            entry["influencers"].append(inf)
        if rv.get("cuisine"):
            entry["cuisines"].append(rv["cuisine"])
            cuisine_counts[rv["cuisine"]].add(rv.get("influencer",""))
        if rv.get("area"):
            entry["areas"].append(rv["area"])

    updated_count  = 0
    ext_upd_count  = 0
    added_count    = 0

    for rest_name, data in rest_map.items():
        influencers = data["influencers"]
        delta_overlap = len(set(i["name"] for i in influencers))
        delta_count   = delta_overlap
        mega_count    = sum(1 for i in influencers if i["tier"] == "Mega")
        new_velocity  = "rising" if delta_overlap >= 2 or mega_count >= 1 else "stable"

        # ── Step 1: ค้นหาใน CM_RESTAURANTS ──────────────────────────────
        match = fuzzy_match(rest_name, existing)

        if match:
            print(f"  ✏️  [CM_REST] อัปเดต: {match['name']}  (+{delta_overlap} influencers → {new_velocity})")
            if not dry_run:
                js_text, ok = update_restaurant_in_js(
                    js_text, match["name"], delta_overlap, delta_count, new_velocity
                )
                if ok:
                    updated_count += 1
                else:
                    print(f"      ⚠️  regex ไม่ match — ข้ามไป")
            continue

        # ── Step 2: ค้นหาใน CM_EXTERNAL_RESTAURANTS ─────────────────────
        ext_match = fuzzy_match(rest_name, ext_list) if ext_list else None

        if ext_match:
            print(f"  🔗  [CM_EXT]  อัปเดต: {ext_match['name']}  (+{delta_overlap} influencers → {new_velocity})")
            if not dry_run:
                inject_influencer_to_external(ext_match, influencers, new_velocity)
                ext_updated = True
                ext_upd_count += 1
            continue

        # ── Step 3: ร้านใหม่ — เพิ่มเข้า CM_RESTAURANTS ─────────────────
        cuisine = data["cuisines"][0] if data["cuisines"] else "Thai"
        area    = data["areas"][0]    if data["areas"]    else "Bangkok"
        print(f"  ➕  [NEW]     ร้านใหม่: {rest_name} ({cuisine}, {area}) — ingest เข้า DB จาก GMaps")
        # เดิม: OpenAI generate demo entry เข้า CM_RESTAURANTS (คะแนนสังเคราะห์)
        # ตอนนี้: เพิ่มเข้า DB ด้วยข้อมูลจริง → export คืนถัดไปพาขึ้นเว็บเอง
        if not dry_run:
            try:
                if ingest_new_restaurant_to_db(rest_name, cuisine, area):
                    added_count += 1
            except Exception as e:
                print(f"      ⚠️ ingest ล้มเหลว: {e}")
        else:
            print(f"      [dry-run] จะ ingest เข้า DB ผ่าน GMaps")

    # ── เขียน CM_EXTERNAL_RESTAURANTS กลับ ──────────────────────────────────
    if not dry_run and ext_updated and ext_start != -1:
        js_text = write_external_restaurants(js_text, ext_list, ext_start, ext_end)
        print(f"\n  📦  เขียน CM_EXTERNAL_RESTAURANTS กลับ ({ext_upd_count} ร้านอัปเดต influencer)")

    # ── อัปเดต trendCategories ───────────────────────────────────────────────
    if not dry_run and cuisine_counts:
        js_text = update_trend_categories(js_text, cuisine_counts)
        print(f"  📊  อัปเดต trendCategories จาก {len(cuisine_counts)} cuisine types")

    # ── บันทึก ───────────────────────────────────────────────────────────────
    if not dry_run:
        DATA_FILE.write_text(js_text, encoding="utf-8")

    print(f"\n{'─'*55}")
    print(f"  [CM_REST]  อัปเดตแล้ว : {updated_count} ร้าน")
    print(f"  [CM_EXT]   อัปเดตแล้ว : {ext_upd_count} ร้าน")
    print(f"  [NEW]      เพิ่มใหม่  : {added_count}  ร้าน")
    if dry_run:
        print(f"  [dry-run] — ไม่มีการเปลี่ยนแปลงจริง")
    print(f"{'─'*55}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
