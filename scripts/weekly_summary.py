#!/usr/bin/env python3
"""
ChefMinistry — Weekly Signal Summary Generator
ใช้ OpenAI API อ่าน signal data แล้วเขียน weekly summary ภาษาไทยอัตโนมัติ

วิธีรัน:
  python3 weekly_summary.py

ต้องการ:
  pip install openai
  OPENAI_API_KEY ใส่ใน .env หรือ environment variable
"""

import os, re, json, pathlib, datetime
from openai import OpenAI

# ── Config ────────────────────────────────────────────────────────────────────
HERE      = pathlib.Path(__file__).parent
# รองรับทั้ง local (site/js/data.js) และ GitHub Actions (ส่งผ่าน env DATA_FILE)
DATA_FILE    = pathlib.Path(os.environ.get("DATA_FILE", str(HERE / "site" / "js" / "data.js")))
# youtube_reviews.json: อยู่ใน scripts/ (sibling ของ weekly_summary.py ใน repo)
YOUTUBE_FILE = pathlib.Path(os.environ.get("YOUTUBE_FILE", str(HERE / "youtube_reviews.json")))

# หา API key จาก .env หรือ environment
env_file = HERE / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if line.startswith("OPENAI_API_KEY="):
            os.environ["OPENAI_API_KEY"] = line.split("=", 1)[1].strip()

client = OpenAI()  # ดึง OPENAI_API_KEY จาก environment อัตโนมัติ

# ── อ่านข้อมูลร้านจาก data.js ─────────────────────────────────────────────────
def js_to_python(raw):
    """แปลง JS object literal → Python dict/list ที่ eval ได้"""
    raw = re.sub(r'//[^\n]*', '', raw)                          # ลบ // comment
    raw = re.sub(r'/\*.*?\*/', '', raw, flags=re.DOTALL)        # ลบ /* */ comment
    raw = re.sub(r',\s*([}\]])', r'\1', raw)                    # ลบ trailing comma
    # quote unquoted JS keys เช่น  name: → "name":
    raw = re.sub(r'(?<=[{,\[])\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:',
                 lambda m: f' "{m.group(1).strip()}":', raw)
    raw = raw.replace('true', 'True').replace('false', 'False').replace('null', 'None')
    return raw

def extract_restaurants(js_text):
    """ดึง CM_RESTAURANTS array ออกจาก JS file"""
    match = re.search(r'const CM_RESTAURANTS\s*=\s*(\[.*?\]);', js_text, re.DOTALL)
    if not match:
        raise ValueError("ไม่พบ CM_RESTAURANTS ใน data.js")
    return eval(js_to_python(match.group(1)))

def extract_signals(js_text):
    """ดึง CM_SIGNALS object ออกจาก JS file"""
    match = re.search(r'const CM_SIGNALS\s*=\s*(\{.*?\});', js_text, re.DOTALL)
    if not match:
        raise ValueError("ไม่พบ CM_SIGNALS ใน data.js")
    raw = match.group(1)
    return eval(js_to_python(raw))

def extract_external_restaurants(js_text):
    """ดึง CM_EXTERNAL_RESTAURANTS array (จาก DB scraper) — ถ้าไม่มีคืน []"""
    match = re.search(r'const CM_EXTERNAL_RESTAURANTS\s*=\s*(\[.*?\]);', js_text, re.DOTALL)
    if not match:
        return []
    try:
        return json.loads(match.group(1))
    except Exception:
        return []

# ── อ่าน YouTube reviews (ถ้ามี) ──────────────────────────────────────────────
def load_youtube_reviews():
    if not YOUTUBE_FILE.exists():
        return []
    try:
        data = json.loads(YOUTUBE_FILE.read_text(encoding="utf-8"))
        return data.get("reviews", [])
    except Exception:
        return []

# ── สร้าง prompt summary สำหรับส่งให้ GPT ─────────────────────────────────────
def build_prompt(restaurants, signals, youtube_reviews=None, external_restaurants=None,
                 current_highlight=None):
    today = datetime.date.today().strftime("%d %B %Y")

    # ── "สัปดาห์นี้" score: YouTube count + velocity + overlapSignal (baseline) ──
    # นับ YouTube reviews ต่อร้าน (สัปดาห์นี้)
    yt_count = {}
    if youtube_reviews:
        for r in youtube_reviews:
            name = r.get("restaurant", "")
            if name:
                yt_count[name] = yt_count.get(name, 0) + 1

    # velocity map จาก CM_EXTERNAL_RESTAURANTS
    vel_map = {}
    if external_restaurants:
        for r in external_restaurants:
            vel_map[r.get("name", "")] = r.get("velocityPct", 0)

    def this_week_score(r):
        name = r.get("name", "")
        yt   = yt_count.get(name, 0) * 10        # YouTube สัปดาห์นี้ (น้ำหนักสูงสุด)
        vel  = vel_map.get(name, 0) / 10          # velocity จาก DB
        base = r.get("overlapSignal", 0)           # baseline (ประวัติ)
        return yt + vel + base

    # top 5 "สัปดาห์นี้" — ไม่ใช่แค่ all-time overlapSignal
    top5 = sorted(restaurants, key=this_week_score, reverse=True)[:5]

    # กรอง current_highlight ออกจาก top5 (ห้ามซ้ำสัปดาห์ที่แล้ว)
    if current_highlight:
        top5_filtered = [r for r in top5 if r.get("name","").lower() != current_highlight.lower()]
        # ถ้ากรองแล้วเหลือน้อยเกินไป ให้เอาจาก next best
        if len(top5_filtered) < 3:
            extras = sorted(restaurants, key=this_week_score, reverse=True)
            extras = [r for r in extras if r.get("name","").lower() != current_highlight.lower()]
            top5_filtered = extras[:5]
        top5 = top5_filtered

    top5_text = "\n".join([
        f"- {r['name']} ({r.get('cuisine','')}) — "
        f"overlap: {r.get('overlapSignal',0)}, "
        f"yt_reviews_this_week: {yt_count.get(r['name'],0)}, "
        f"velocity: {r.get('trendVelocity','')}"
        for r in top5
    ])

    # ร้านใหม่จาก YouTube สัปดาห์นี้ (ไม่อยู่ใน top5 ด้านบน)
    top5_names = {r['name'] for r in top5}
    yt_new = [name for name, cnt in sorted(yt_count.items(), key=lambda x: x[1], reverse=True)
              if name not in top5_names][:5]
    yt_new_text = ", ".join(yt_new) if yt_new else "ไม่มีใหม่"

    # trend categories
    cats = signals.get('trendCategories', [])
    cats_text = "\n".join([
        f"- {c['cat']}: signal={c['signal']}, change={c['change']}, influencers={c['influencers']}"
        for c in cats
    ])

    # top velocity จาก DB scraper (ข้อมูลสดจาก Wongnai/GMaps)
    velocity_section = ""
    if external_restaurants:
        top_vel = sorted(
            [r for r in external_restaurants if r.get('velocityPct', 0) > 0 and r.get('isRestaurant', True)],
            key=lambda r: r.get('velocityPct', 0), reverse=True
        )[:5]
        if top_vel:
            vel_lines = "\n".join([
                f"- {r.get('name','')} ({r.get('cuisine','')}, {r.get('area','')}) — velocity: +{r.get('velocityPct',0):.0f}%, new reviews: {r.get('newReviews30d',0)}"
                for r in top_vel
            ])
            velocity_section = f"\nTop Velocity จาก DB (ร้านที่รีวิวเพิ่มเร็วที่สุดสัปดาห์นี้):\n{vel_lines}"

    # YouTube influencer section (ถ้ามี)
    yt_section = ""
    if youtube_reviews:
        yt_lines = []
        for r in youtube_reviews[:10]:
            yt_lines.append(
                f"- [{r['tier']}] {r['influencer']}: {r['restaurant']} "
                f"({r.get('cuisine','')}) — {r.get('rating','?')} [{r['published']}]"
            )
        yt_section = f"\nYouTube Influencer Reviews สัปดาห์นี้:\n" + "\n".join(yt_lines)

    # ห้ามซ้ำ instruction
    no_repeat = ""
    if current_highlight:
        no_repeat = f"\n⚠️  ห้ามเลือก \"{current_highlight}\" — ถูก highlight ไปแล้วสัปดาห์ก่อน เลือกร้านอื่นเท่านั้น"

    return f"""คุณเป็น editor ของ ChefMinistry แพลตฟอร์ม food signal intelligence สำหรับวงการอาหารไทย

วันนี้: {today}{no_repeat}

ข้อมูล Signal ล่าสุด (เรียงตาม activity สัปดาห์นี้ ไม่ใช่แค่ประวัติ):

TOP 5 ร้านที่น่าสนใจสัปดาห์นี้ (YouTube + velocity + influencer รวมกัน):
{top5_text}

ร้านใหม่จาก YouTube ที่ยังไม่อยู่ใน TOP 5: {yt_new_text}

Trend Categories:
{cats_text}{velocity_section}{yt_section}

งานของคุณ: เขียน weekly summary สั้นๆ โดยเน้น insight ที่เปลี่ยนแปลงสัปดาห์นี้จริงๆ
- ให้ priority กับร้านที่มี yt_reviews_this_week > 0 หรือ velocity สูงสุด
- ถ้าไม่มี YouTube/velocity data ให้เลือกร้านจาก TOP 5 ที่มี overlapSignal สูงรองลงมา (ไม่ใช่อันดับ 1 เสมอ)
- ห้ามเลือกร้านที่ถูกระบุใน "ห้ามเลือก" ด้านบนโดยเด็ดขาด

ต้องการ JSON output แบบนี้เท่านั้น (ห้ามเพิ่มข้อความนอก JSON):
{{
  "title": "หัวข้อสั้นๆ ดึงดูด ภาษาไทย ไม่เกิน 60 ตัวอักษร (มี emoji ได้)",
  "desc": "สรุป 1-2 ประโยค ภาษาไทย อ่านง่าย บอก insight ที่น่าสนใจที่สุดของสัปดาห์นี้",
  "restaurant": "ชื่อร้านหลักที่ highlight ในสัปดาห์นี้ (ชื่อจริงจากข้อมูลด้านบนเท่านั้น)"
}}"""

# ── เรียก GPT ──────────────────────────────────────────────────────────────────
def generate_summary(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",     # เร็ว + ถูก เหมาะกับงานนี้
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200,
    )
    text = response.choices[0].message.content.strip()
    # parse JSON จาก response
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError(f"GPT ไม่ส่ง JSON กลับมา: {text}")
    return json.loads(match.group())

# ── อ่าน weeklyHighlight ปัจจุบัน ──────────────────────────────────────────────
def extract_current_highlight(js_text):
    """ดึงชื่อร้านที่ถูก highlight ล่าสุด (จาก field 'restaurant' ใน weeklyHighlight)"""
    # อ่าน field 'restaurant' (เพิ่มเวอร์ชันใหม่)
    m = re.search(r'weeklyHighlight\s*:\s*\{[^}]*restaurant\s*:\s*"([^"]*)"', js_text, re.DOTALL)
    return m.group(1) if m else None

# ── อัปเดต weeklyHighlight ใน data.js ─────────────────────────────────────────
def update_weekly_highlight(js_text, new_title, new_desc, new_restaurant=None):
    # replace title + desc
    pattern = r'(weeklyHighlight\s*:\s*\{[^}]*title\s*:\s*")[^"]*("[^}]*desc\s*:\s*")[^"]*(")'

    def replacer(m):
        return f'{m.group(1)}{new_title}{m.group(2)}{new_desc}{m.group(3)}'

    new_text, count = re.subn(pattern, replacer, js_text, flags=re.DOTALL)
    if count == 0:
        raise ValueError("ไม่สามารถ replace weeklyHighlight ได้ — ตรวจสอบ pattern")

    # เพิ่ม/อัปเดต field 'restaurant' ใน weeklyHighlight block
    if new_restaurant:
        rest_escaped = new_restaurant.replace('"', '\\"')
        # ถ้ามี field restaurant อยู่แล้ว → replace
        if re.search(r'weeklyHighlight\s*:\s*\{[^}]*restaurant\s*:', new_text, re.DOTALL):
            new_text = re.sub(
                r'(weeklyHighlight\s*:\s*\{[^}]*restaurant\s*:\s*")[^"]*(")',
                rf'\g<1>{rest_escaped}\2',
                new_text, flags=re.DOTALL
            )
        else:
            # ยังไม่มี → เพิ่มหลัง desc field
            new_text = re.sub(
                r'(weeklyHighlight\s*:\s*\{[^}]*desc\s*:\s*"[^"]*")',
                rf'\1, restaurant: "{rest_escaped}"',
                new_text, flags=re.DOTALL
            )
    return new_text

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  ChefMinistry — Weekly Summary Generator")
    print("=" * 55)

    if not DATA_FILE.exists():
        raise SystemExit(f"❌ ไม่พบ {DATA_FILE}")

    print(f"\n[1] อ่าน data.js...")
    js_text = DATA_FILE.read_text(encoding="utf-8")

    restaurants       = extract_restaurants(js_text)
    signals           = extract_signals(js_text)
    ext_rests         = extract_external_restaurants(js_text)
    current_highlight = extract_current_highlight(js_text)
    print(f"    พบ {len(restaurants)} ร้าน (influencer), {len(ext_rests)} ร้าน (DB velocity), {len(signals.get('trendCategories',[]))} categories")
    if current_highlight:
        print(f"    🔒  current highlight (จะไม่ซ้ำ): {current_highlight}")

    yt_reviews = load_youtube_reviews()
    if yt_reviews:
        print(f"    + YouTube reviews: {len(yt_reviews)} รีวิว (จาก {YOUTUBE_FILE.name})")
    else:
        print(f"    ℹ️  ไม่พบ youtube_reviews.json — ใช้เฉพาะข้อมูล data.js")

    print(f"\n[2] ส่งข้อมูลให้ GPT-4o-mini...")
    prompt  = build_prompt(restaurants, signals, yt_reviews, ext_rests, current_highlight)
    result  = generate_summary(prompt)

    print(f"\n[3] ผลลัพธ์จาก GPT:")
    print(f"    title : {result['title']}")
    print(f"    desc  : {result['desc']}")

    print(f"\n[4] อัปเดต data.js...")
    highlighted_rest = result.get('restaurant', '')
    if highlighted_rest:
        print(f"    🏆  ร้านที่ highlight: {highlighted_rest}")
    new_js = update_weekly_highlight(js_text, result['title'], result['desc'], highlighted_rest)
    DATA_FILE.write_text(new_js, encoding="utf-8")
    print(f"    ✅ บันทึกแล้ว")

    print(f"\n{'=' * 55}")
    print(f"  เสร็จแล้ว! รัน push_to_github.py เพื่อ deploy")
    print(f"{'=' * 55}\n")

if __name__ == "__main__":
    main()
