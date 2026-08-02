#!/usr/bin/env python3
"""
ChefMinistry — Seed Discovery (premium mass)
ค้นร้านใหม่จาก Google Places Text Search ตามกลุ่ม "premium mass"
(ร้านเข้าถึงได้ กินได้บ่อย แต่คุณภาพ/กระแสดี) แล้ว upsert เข้า DB

ออกแบบให้รันใน CI (scraper.yml) ตอน workflow_dispatch เท่านั้น —
รันซ้ำได้ปลอดภัย (dedupe ด้วย place_id + ชื่อ)

Usage:
  python seed_discover.py --max-new 100
  python seed_discover.py --dry-run
"""
import argparse, json, re, sys, urllib.request

from db import init_db, upsert_restaurant, record_snapshot, get_conn
from scrape_gmaps import save_gmaps_meta, load_blocklist
from config import GOOGLE_MAPS_API_KEY
import api_budget

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = ",".join([
    "places.id", "places.displayName", "places.formattedAddress",
    "places.location", "places.rating", "places.userRatingCount",
    "places.priceLevel", "places.types", "places.businessStatus",
])

# ── กลุ่ม premium mass: (query, base cuisine) ─────────────────────────────────
QUERIES = [
    # สตรีทฟู้ดระดับตำนาน / อิ่มคุ้มเจ้าดัง
    ("ก๋วยเตี๋ยวเรือ อร่อย กรุงเทพ",        "Noodles"),
    ("ก๋วยเตี๋ยวต้มยำ เจ้าดัง กรุงเทพ",     "Noodles"),
    ("ข้าวมันไก่ เจ้าดัง กรุงเทพ",           "Thai"),
    ("ข้าวหมูแดง หมูกรอบ ดัง กรุงเทพ",      "Thai"),
    ("เป็ดย่าง ตำนาน กรุงเทพ",              "Chinese"),
    ("ติ่มซำ อร่อย เยาวราช กรุงเทพ",        "Chinese"),
    ("ข้าวแกง เจ้าดัง กรุงเทพ",             "Thai"),
    ("ส้มตำ ไก่ย่าง เจ้าดัง กรุงเทพ",       "Thai"),
    # คาเฟ่ / บรันช์ย่านฮิต
    ("คาเฟ่ ยอดนิยม อารีย์",                "Cafe"),
    ("คาเฟ่ ทองหล่อ เอกมัย",                "Cafe"),
    ("คาเฟ่ เจริญกรุง ตลาดน้อย",            "Cafe"),
    ("specialty coffee bangkok",             "Cafe"),
    # ชาบู / ปิ้งย่าง / หมูกระทะ
    ("ชาบู อร่อย กรุงเทพ",                  "Hot Pot / Suki"),
    ("หมูกระทะ เด็ด กรุงเทพ",               "BBQ"),
    ("ปิ้งย่างเกาหลี กรุงเทพ",              "Korean"),
    ("ยากินิคุ อร่อย กรุงเทพ",              "Yakiniku"),
]

MIN_RATING  = 4.3
MIN_REVIEWS = 200
OK_PRICE    = {None, "", "PRICE_LEVEL_UNSPECIFIED",
               "PRICE_LEVEL_INEXPENSIVE", "PRICE_LEVEL_MODERATE"}
PRICE_MAP   = {"PRICE_LEVEL_INEXPENSIVE": "1", "PRICE_LEVEL_MODERATE": "2"}


def search(query: str, api_key: str) -> list:
    # FIELD_MASK มี rating/userRatingCount/priceLevel (จำเป็นต่อการคัดกรอง)
    # → ตกชั้น Text Search Enterprise $35/1,000 ฟรีแค่ 1,000/เดือน
    # Text Search คิดเงินต่อ "request" ไม่ใช่ต่อผลลัพธ์ — 1 query = 1 call
    if not api_budget.allow("text_ent"):
        print("  ⏸  โควตา Text Search Enterprise เดือนนี้หมดแล้ว — หยุด seed")
        return []
    body = json.dumps({
        "textQuery": query, "languageCode": "th",
        "regionCode": "TH", "maxResultCount": 20,
    }).encode()
    req = urllib.request.Request(SEARCH_URL, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    })
    try:
        api_budget.record("text_ent")
        return json.loads(urllib.request.urlopen(req, timeout=30).read()).get("places", [])
    except Exception as e:
        print(f"  ⚠️ search fail: {e}")
        return []


def norm_name(s: str) -> str:
    return re.sub(r"[\s\-–—·.()]+", "", (s or "").lower())


def extract_area(addr: str) -> str:
    m = re.search(r"เขต([ก-๙]+)", addr or "")
    if m: return m.group(1)
    m = re.search(r"แขวง([ก-๙]+)", addr or "")
    if m: return m.group(1)
    return "Bangkok"


def brand_key(name: str) -> str:
    """กันสาขาแบรนด์เดียวกันเข้ามาซ้ำหลายสาขา — ใช้ 12 ตัวอักษรแรกของชื่อ normalize"""
    return norm_name(name)[:12]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-new", type=int, default=100)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not GOOGLE_MAPS_API_KEY:
        sys.exit("❌ ไม่พบ GOOGLE_MAPS_API_KEY")

    init_db()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT external_id, gmaps_place_id, name FROM restaurants").fetchall()
    known_ids   = {r["external_id"] for r in rows} | {r["gmaps_place_id"] for r in rows if r["gmaps_place_id"]}
    known_names = {norm_name(r["name"]) for r in rows}
    seen_brands = set()

    # blocklist: listing ปลอม/โรงแรม — ห้าม seed กลับเข้ามาอีก
    bl_ids, bl_names = load_blocklist()

    added = 0
    print(f"\n{'='*55}\n  ChefMinistry — Seed Discovery (premium mass)\n{'='*55}")
    for query, cuisine in QUERIES:
        if added >= args.max_new: break
        print(f"\n🔎 {query}")
        places = search(query, GOOGLE_MAPS_API_KEY)
        # เรียงตามจำนวนรีวิว (ความนิยมจริง) มากก่อน
        places.sort(key=lambda p: p.get("userRatingCount", 0), reverse=True)
        picked = 0
        for p in places:
            if added >= args.max_new or picked >= 8: break
            pid    = p.get("id", "")
            name   = (p.get("displayName") or {}).get("text", "")
            rating = p.get("rating", 0)
            urc    = p.get("userRatingCount", 0)
            price  = p.get("priceLevel")
            addr   = p.get("formattedAddress", "")
            status = p.get("businessStatus", "OPERATIONAL")
            loc    = p.get("location") or {}

            if not pid or not name: continue
            if pid in bl_ids or name.strip() in bl_names: continue  # blocklisted
            if pid in known_ids or norm_name(name) in known_names: continue
            if brand_key(name) in seen_brands: continue
            if rating < MIN_RATING or urc < MIN_REVIEWS: continue
            if price not in OK_PRICE: continue
            if status not in ("OPERATIONAL", None, ""): continue
            if not re.search(r"กรุงเทพ|Bangkok", addr): continue

            print(f"  ✅ {name} — ⭐{rating} ({urc:,} รีวิว) · {extract_area(addr)}")
            if args.dry_run:
                added += 1; picked += 1; continue

            rid = upsert_restaurant({
                "source": "gmaps", "external_id": pid,
                "name": name, "cuisine": cuisine,
                "area": extract_area(addr), "address": addr,
                "city": "Bangkok", "province": "Bangkok",
                "lat": loc.get("latitude"), "lng": loc.get("longitude"),
                "price_range": PRICE_MAP.get(price, "2"),
                "url": f"https://www.google.com/maps/place/?q=place_id:{pid}",
            })
            record_snapshot(rid, review_count=urc, rating=rating, rating_count=urc)
            save_gmaps_meta(rid, {
                "gmaps_place_id": pid, "gmaps_address": addr,
                "gmaps_types": p.get("types") or [],
                "gmaps_business_status": status or "OPERATIONAL",
            })
            known_ids.add(pid); known_names.add(norm_name(name))
            seen_brands.add(brand_key(name))
            added += 1; picked += 1

    print(f"\n{'='*55}\n  เพิ่มร้านใหม่ {added} ร้าน{' (dry-run)' if args.dry_run else ''}\n{'='*55}\n")


if __name__ == "__main__":
    main()
