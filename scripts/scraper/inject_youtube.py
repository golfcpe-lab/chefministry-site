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

    updated_count = 0
    added_count   = 0

    for rest_name, data in rest_map.items():
        influencers = data["influencers"]
        delta_overlap = len(set(i["name"] for i in influencers))
        delta_count   = delta_overlap
        mega_count    = sum(1 for i in influencers if i["tier"] == "Mega")
        new_velocity  = "rising" if delta_overlap >= 2 or mega_count >= 1 else "stable"

        match = fuzzy_match(rest_name, existing)

        if match:
            # ── อัปเดตร้านที่มีอยู่ ─────────────────────────────────────
            print(f"  ✏️  อัปเดต: {match['name']}  (+{delta_overlap} influencers → {new_velocity})")
            if not dry_run:
                js_text, ok = update_restaurant_in_js(
                    js_text, match["name"], delta_overlap, delta_count, new_velocity
                )
                if ok:
                    updated_count += 1
                else:
                    print(f"      ⚠️  regex ไม่ match — ข้ามไป")
        else:
            # ── เพิ่มร้านใหม่ ────────────────────────────────────────────
            cuisine = data["cuisines"][0] if data["cuisines"] else "Thai"
            area    = data["areas"][0]    if data["areas"]    else "Bangkok"
            new_id  = f"r{next_num:03d}"
            print(f"  ➕  ร้านใหม่: {rest_name} ({cuisine}, {area}) — id: {new_id}")

            if not dry_run:
                entry = generate_new_restaurant_entry(rest_name, cuisine, area, influencers, new_id)
                if entry:
                    js_entry = f"  {dict_to_js(entry)},"
                    # หาจุดปิด ] ของ CM_RESTAURANTS โดยนับ bracket
                    mo = re.search(r'const CM_RESTAURANTS\s*=\s*\[', js_text, re.DOTALL)
                    if mo:
                        start = mo.end() - 1
                        depth2, i2, in_s, esc2 = 0, start, False, False
                        while i2 < len(js_text):
                            c = js_text[i2]
                            if esc2:   esc2 = False
                            elif c == '\\' and in_s: esc2 = True
                            elif c == '"' and not esc2: in_s = not in_s
                            elif not in_s:
                                if c == '[':  depth2 += 1
                                elif c == ']':
                                    depth2 -= 1
                                    if depth2 == 0: break
                            i2 += 1
                        # แทรก entry ก่อน ]
                        js_text = js_text[:i2] + "\n" + js_entry + "\n" + js_text[i2:]
                    next_num += 1
                    added_count += 1
            else:
                print(f"      [dry-run] จะ generate entry ด้วย OpenAI")

    # ── อัปเดต trendCategories ───────────────────────────────────────────────
    if not dry_run and cuisine_counts:
        js_text = update_trend_categories(js_text, cuisine_counts)
        print(f"\n  📊  อัปเดต trendCategories จาก {len(cuisine_counts)} cuisine types")

    # ── บันทึก ───────────────────────────────────────────────────────────────
    if not dry_run:
        DATA_FILE.write_text(js_text, encoding="utf-8")

    print(f"\n{'─'*55}")
    print(f"  อัปเดตแล้ว : {updated_count} ร้าน")
    print(f"  เพิ่มใหม่  : {added_count}  ร้าน")
    if dry_run:
        print(f"  [dry-run] — ไม่มีการเปลี่ยนแปลงจริง")
    print(f"{'─'*55}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
