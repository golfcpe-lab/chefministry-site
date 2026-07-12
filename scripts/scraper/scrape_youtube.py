#!/usr/bin/env python3
"""
ChefMinistry — YouTube Influencer Scraper
ดึง video ใหม่จาก influencer YouTube channels → ใช้ OpenAI สกัดชื่อร้าน + rating

วิธีรัน (local):
  python scrape_youtube.py
  python scrape_youtube.py --days 14     # ย้อนหลัง 14 วัน
  python scrape_youtube.py --dry-run     # แสดงผลโดยไม่บันทึก

Output:
  scripts/youtube_reviews.json  (ใน repo root เพื่อให้ weekly_summary.py อ่านได้)
"""

import os, json, pathlib, datetime, urllib.request, urllib.parse, argparse, time
from openai import OpenAI

# ── Paths ──────────────────────────────────────────────────────────────────────
HERE        = pathlib.Path(__file__).parent                          # scraper/
SCRIPTS_DIR = pathlib.Path(os.environ.get("SCRIPTS_DIR", str(HERE.parent)))  # scripts/
OUTPUT_FILE = SCRIPTS_DIR / "youtube_reviews.json"

# ── Load API Keys ──────────────────────────────────────────────────────────────
def _load_env():
    env_file = HERE.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

_load_env()

YT_KEY     = os.environ.get("YOUTUBE_API_KEY", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

if not YT_KEY:
    raise SystemExit("❌ ไม่พบ YOUTUBE_API_KEY — ใส่ใน .env หรือ GitHub Secrets")
if not OPENAI_KEY:
    raise SystemExit("❌ ไม่พบ OPENAI_API_KEY — ใส่ใน .env หรือ GitHub Secrets")

client = OpenAI(api_key=OPENAI_KEY)

# ── YouTube Channels ───────────────────────────────────────────────────────────
# format: (display_name, youtube_handle, tier)
# tier roles:
#   Mega   = traffic generator  — ยิงทีเดียว impact ใหญ่
#   Macro  = paid media layer   — balance reach + credibility
#   Mid    = data + review core — conversion ดี, คนเชื่อจริง
CHANNELS = [
    # ── MEGA (5M+ subscribers) ────────────────────────────────────────────────
    ("Peach Eat Laek",    "@PeachEatLaek",       "Mega"),   # ~9M  — Viral machine
    ("Mark Wiens",        "@MarkWiens",           "Mega"),   # ~10M — Global food authority

    # ── MACRO (1M–5M subscribers) ─────────────────────────────────────────────
    ("Starving Time",     "@Starvingtime",        "Macro"),  # ~3–4M — Food media platform
    ("ชีวิตติดรีวิว",     "@Tid_Review",          "Macro"),  # ~2–3M — Mass lifestyle review
    ("EaterOat",          "@EaterOat",            "Macro"),  # ~1.5M — Heavy review, conversion สูง
    ("GoWentGo",          "@GoWentGo",            "Macro"),  # ~1.2M — Food + travel

    # ── MID (300K–1M subscribers) ─────────────────────────────────────────────
    ("KiaZaab",           "@KiaZaab",             "Mid"),    # ~600K — Local expert, trust สูง
    ("กินกับกี้",         "@kin-kub-ky",          "Mid"),    # ~1M   — Honest review
    ("EatGuide",          "@EatGuide",            "Mid"),    # ~500K — Curated restaurant
]

YT_BASE = "https://www.googleapis.com/youtube/v3"

# ── YouTube API helpers ────────────────────────────────────────────────────────
def yt_get(endpoint, params):
    params["key"] = YT_KEY
    url = f"{YT_BASE}/{endpoint}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"  ⚠️  YouTube API error {e.code}: {body[:200]}")
        return None

def get_channel_id(handle):
    """แปลง YouTube handle → channel ID"""
    data = yt_get("channels", {"part": "id", "forHandle": handle})
    if data and data.get("items"):
        return data["items"][0]["id"]
    return None

def get_uploads_playlist(channel_id):
    """ดึง uploads playlist ID ของ channel"""
    data = yt_get("channels", {"part": "contentDetails", "id": channel_id})
    if data and data.get("items"):
        return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    return None

def get_recent_videos(playlist_id, max_results=10):
    """ดึง video ล่าสุดจาก uploads playlist"""
    data = yt_get("playlistItems", {
        "part":       "snippet",
        "playlistId": playlist_id,
        "maxResults": max_results,
    })
    if not data:
        return []
    return [
        {
            "id":          item["snippet"]["resourceId"]["videoId"],
            "title":       item["snippet"]["title"],
            "description": item["snippet"]["description"][:800],  # trim ยาวเกิน
            "published":   item["snippet"]["publishedAt"][:10],
        }
        for item in data.get("items", [])
    ]

# ── OpenAI extraction ──────────────────────────────────────────────────────────
EXTRACT_PROMPT = """\
คุณเป็น data extractor สำหรับ ChefMinistry แพลตฟอร์ม food intelligence ไทย

จาก title และ description ของ YouTube video ด้านล่าง ให้สกัดร้านอาหารที่ถูกรีวิว
(เฉพาะร้านที่ชัดเจน ไม่ต้องเดา — ถ้าไม่มีร้านให้ return array ว่าง)

ตอบเป็น JSON array เท่านั้น ห้ามมีข้อความอื่น:
[
  {{
    "restaurant": "ชื่อร้าน",
    "cuisine": "ประเภทอาหาร เช่น Thai, Japanese, Street Food, Fine Dining",
    "area": "ย่านหรือจังหวัด เช่น Thonglor, Silom, Bangkok (ถ้าไม่รู้ใส่ Bangkok)",
    "country": "ประเทศที่ร้านตั้งอยู่ เช่น Thailand, UK, Japan (ดูจาก context ถ้าไม่แน่ใจใส่ Thailand)",
    "rating": "exceed | above_average | average | need_improve (ประเมินจาก tone ของ video)",
    "confidence": "high | medium | low"
  }}
]

Video title: {title}
Description: {description}
"""

def extract_restaurants_from_video(title, description):
    """ใช้ OpenAI สกัดร้านจาก title + description"""
    prompt = EXTRACT_PROMPT.format(title=title, description=description)
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=400,
        )
        text = resp.choices[0].message.content.strip()
        # parse JSON
        import re
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"    ⚠️  OpenAI error: {e}")
    return []

# ── Main ───────────────────────────────────────────────────────────────────────
def run(days=7, dry_run=False):
    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    all_reviews = []

    print(f"\n{'='*55}")
    print(f"  ChefMinistry — YouTube Scraper")
    print(f"  ย้อนหลัง {days} วัน (ตั้งแต่ {cutoff})")
    print(f"{'='*55}\n")

    for name, handle, tier in CHANNELS:
        print(f"📺  {name} ({handle}) [{tier}]")

        # 1. หา channel ID
        ch_id = get_channel_id(handle)
        if not ch_id:
            print(f"    ❌ ไม่พบ channel — ข้ามไป\n")
            continue
        print(f"    Channel ID: {ch_id}")

        # 2. หา uploads playlist
        pl_id = get_uploads_playlist(ch_id)
        if not pl_id:
            print(f"    ❌ ไม่พบ playlist — ข้ามไป\n")
            continue

        # 3. ดึง video ล่าสุด
        videos = get_recent_videos(pl_id, max_results=8)
        # กรองเฉพาะ video ที่ publish ใน window
        recent = [v for v in videos if v["published"] >= cutoff]
        print(f"    พบ {len(videos)} video ล่าสุด, {len(recent)} อยู่ใน {days} วัน")

        for video in recent:
            print(f"    🎬 {video['title'][:60]}… ({video['published']})")

            # 4. สกัดร้านจาก OpenAI
            restaurants = extract_restaurants_from_video(video["title"], video["description"])
            high_conf   = [r for r in restaurants if r.get("confidence") != "low"]
            # กรองร้านนอกไทย (เช่น creator ไปเที่ยวต่างประเทศ — เคยมีร้านลอนดอนหลุดเข้า feed)
            _before = len(high_conf)
            high_conf = [r for r in high_conf
                         if r.get("country", "Thailand").strip().lower() in ("thailand", "th", "ไทย", "ประเทศไทย")]
            if _before > len(high_conf):
                print(f"       🌏 ตัดร้านนอกไทยออก {_before - len(high_conf)} ร้าน")

            if not high_conf:
                print(f"       → ไม่พบร้านที่ชัดเจน\n")
                continue

            for r in high_conf:
                review = {
                    "influencer":  name,
                    "handle":      handle,
                    "tier":        tier,
                    "restaurant":  r["restaurant"],
                    "cuisine":     r.get("cuisine", ""),
                    "area":        r.get("area", "Bangkok"),
                    "rating":      r.get("rating", "average"),
                    "confidence":  r.get("confidence", "medium"),
                    "video_title": video["title"],
                    "video_url":   f"https://youtube.com/watch?v={video['id']}",
                    "published":   video["published"],
                }
                all_reviews.append(review)
                print(f"       ✅ {r['restaurant']} — {r.get('rating','?')} ({r.get('confidence','?')})")

            time.sleep(0.5)  # อย่ายิง OpenAI เร็วเกินไป
        print()

    # ── Summary ────────────────────────────────────────────────────────────────
    print(f"{'─'*55}")
    print(f"  รวม: {len(all_reviews)} รีวิวจาก YouTube")
    print(f"{'─'*55}\n")

    if dry_run:
        print("🔍 Dry-run mode — ไม่บันทึกไฟล์")
        print(json.dumps(all_reviews, ensure_ascii=False, indent=2))
        return

    # ── บันทึก JSON ────────────────────────────────────────────────────────────
    output = {
        "generated_at": datetime.date.today().isoformat(),
        "days_window":  days,
        "total":        len(all_reviews),
        "reviews":      all_reviews,
    }
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ บันทึกแล้ว → {OUTPUT_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days",    type=int, default=7,      help="ย้อนหลังกี่วัน")
    parser.add_argument("--dry-run", action="store_true",      help="แสดงผลโดยไม่บันทึก")
    args = parser.parse_args()
    run(days=args.days, dry_run=args.dry_run)
