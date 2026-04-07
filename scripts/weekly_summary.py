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
def build_prompt(restaurants, signals, youtube_reviews=None):
    today = datetime.date.today().strftime("%d %B %Y")

    # top 5 ร้านที่มี overlap สูงสุด
    top5 = sorted(restaurants, key=lambda r: r.get('overlapSignal', 0), reverse=True)[:5]
    top5_text = "\n".join([
        f"- {r['name']} ({r.get('cuisine','')}, {r.get('area','')}) — overlap: {r.get('overlapSignal',0)}, velocity: {r.get('trendVelocity','')}"
        for r in top5
    ])

    # rising ร้าน
    rising = [r['name'] for r in restaurants if r.get('trendVelocity') == 'rising']
    rising_text = ", ".join(rising[:5]) if rising else "ไม่มี"

    # trend categories
    cats = signals.get('trendCategories', [])
    cats_text = "\n".join([
        f"- {c['cat']}: signal={c['signal']}, change={c['change']}, influencers={c['influencers']}"
        for c in cats
    ])

    # YouTube influencer section (ถ้ามี)
    yt_section = ""
    if youtube_reviews:
        yt_lines = []
        for r in youtube_reviews[:10]:  # ใช้แค่ 10 รีวิวแรก
            yt_lines.append(
                f"- [{r['tier']}] {r['influencer']}: {r['restaurant']} "
                f"({r.get('cuisine','')}) — {r.get('rating','?')} [{r['published']}]"
            )
        yt_section = f"\nYouTube Influencer Reviews สัปดาห์นี้:\n" + "\n".join(yt_lines)

    return f"""คุณเป็น editor ของ ChefMinistry แพลตฟอร์ม food signal intelligence สำหรับวงการอาหารไทย

วันนี้: {today}

ข้อมูล Signal ล่าสุด:

TOP 5 ร้านที่มี Overlap Signal สูงสุด:
{top5_text}

ร้านที่กำลัง Rising ตอนนี้: {rising_text}

Trend Categories:
{cats_text}{yt_section}

งานของคุณ: เขียน weekly summary สั้นๆ สำหรับแสดงบนหน้าหลักเว็บ ChefMinistry
(ถ้ามีข้อมูล YouTube ให้นำมา highlight influencer ที่น่าสนใจด้วย)

ต้องการ JSON output แบบนี้เท่านั้น (ห้ามเพิ่มข้อความนอก JSON):
{{
  "title": "หัวข้อสั้นๆ ดึงดูด ภาษาไทย ไม่เกิน 60 ตัวอักษร (มี emoji ได้)",
  "desc": "สรุป 1-2 ประโยค ภาษาไทย อ่านง่าย บอก insight ที่น่าสนใจที่สุดของสัปดาห์นี้"
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

# ── อัปเดต weeklyHighlight ใน data.js ─────────────────────────────────────────
def update_weekly_highlight(js_text, new_title, new_desc):
    pattern = r'(weeklyHighlight\s*:\s*\{[^}]*title\s*:\s*")[^"]*("[^}]*desc\s*:\s*")[^"]*(")'

    def replacer(m):
        return f'{m.group(1)}{new_title}{m.group(2)}{new_desc}{m.group(3)}'

    new_text, count = re.subn(pattern, replacer, js_text, flags=re.DOTALL)
    if count == 0:
        raise ValueError("ไม่สามารถ replace weeklyHighlight ได้ — ตรวจสอบ pattern")
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

    restaurants = extract_restaurants(js_text)
    signals     = extract_signals(js_text)
    print(f"    พบ {len(restaurants)} ร้าน, {len(signals.get('trendCategories',[]))} categories")

    yt_reviews = load_youtube_reviews()
    if yt_reviews:
        print(f"    + YouTube reviews: {len(yt_reviews)} รีวิว (จาก {YOUTUBE_FILE.name})")
    else:
        print(f"    ℹ️  ไม่พบ youtube_reviews.json — ใช้เฉพาะข้อมูล data.js")

    print(f"\n[2] ส่งข้อมูลให้ GPT-4o-mini...")
    prompt  = build_prompt(restaurants, signals, yt_reviews)
    result  = generate_summary(prompt)

    print(f"\n[3] ผลลัพธ์จาก GPT:")
    print(f"    title : {result['title']}")
    print(f"    desc  : {result['desc']}")

    print(f"\n[4] อัปเดต data.js...")
    new_js = update_weekly_highlight(js_text, result['title'], result['desc'])
    DATA_FILE.write_text(new_js, encoding="utf-8")
    print(f"    ✅ บันทึกแล้ว")

    print(f"\n{'=' * 55}")
    print(f"  เสร็จแล้ว! รัน push_to_github.py เพื่อ deploy")
    print(f"{'=' * 55}\n")

if __name__ == "__main__":
    main()
