#!/usr/bin/env python3
"""
ChefMinistry — Seed from place list with coordinates
ใช้กับลิสต์ที่ดึงมาจาก Google Maps saved list (เช่น matcha_bkk.json):
แต่ละ entry มีพิกัดจริง → search ด้วย locationBias วงแคบ แล้ว verify ด้วย
(1) ระยะห่างผลลัพธ์ ≤ 700m จากพิกัดที่คาด (2) ที่อยู่ต้องอยู่กรุงเทพ
→ กันจับร้านผิดได้แน่นกว่า name matching

รันใน CI (scraper.yml) ตอน workflow_dispatch — รันซ้ำได้ปลอดภัย (dedupe)

Usage:
  python seed_list.py --file matcha_bkk.json
  python seed_list.py --file matcha_bkk.json --dry-run
"""
import argparse, json, math, pathlib, sys, time

from db import init_db, upsert_restaurant, record_snapshot, get_conn
from scrape_gmaps import save_gmaps_meta, load_blocklist, DELAY, _post, BASE_URL
from seed_discover import norm_name, extract_area
from config import GOOGLE_MAPS_API_KEY

MAX_DIST_M = 700.0


def search_biased(name, lat, lng, api_key):
    """Text Search ด้วย bias วงแคบรอบพิกัดที่รู้ — คืน list ผลลัพธ์ (มี types ครบ ไม่ต้องเรียก details ซ้ำ)"""
    url = f"{BASE_URL}/places:searchText"
    hdrs = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": ",".join([
            "places.id", "places.displayName", "places.rating",
            "places.userRatingCount", "places.formattedAddress",
            "places.location", "places.primaryType", "places.types",
            "places.businessStatus", "places.priceLevel",
        ]),
        "Content-Type": "application/json",
    }
    body = {
        "textQuery": name, "languageCode": "th", "regionCode": "TH",
        "maxResultCount": 3,
        "locationBias": {"circle": {"center": {"latitude": lat, "longitude": lng}, "radius": 500.0}},
    }
    try:
        return (_post(url, body, hdrs) or {}).get("places", [])
    except Exception as e:
        print(f"      ❌ search({name[:30]}): {e}")
        return []


def dist_m(lat1, lng1, lat2, lng2):
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


PRICE_MAP = {"PRICE_LEVEL_INEXPENSIVE": "1", "PRICE_LEVEL_MODERATE": "2",
             "PRICE_LEVEL_EXPENSIVE": "3", "PRICE_LEVEL_VERY_EXPENSIVE": "3"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not GOOGLE_MAPS_API_KEY:
        sys.exit("❌ ไม่พบ GOOGLE_MAPS_API_KEY")
    path = pathlib.Path(__file__).parent / args.file
    if not path.exists():
        sys.exit(f"❌ ไม่พบ {path}")
    seeds = json.loads(path.read_text(encoding="utf-8"))

    init_db()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT external_id, gmaps_place_id, name FROM restaurants").fetchall()
    known_ids   = {r["external_id"] for r in rows} | {r["gmaps_place_id"] for r in rows if r["gmaps_place_id"]}
    known_names = {norm_name(r["name"]) for r in rows}
    bl_ids, bl_names = load_blocklist()

    added, skipped, missed = 0, 0, []
    print(f"\n{'='*55}\n  ChefMinistry — Seed from list: {args.file} ({len(seeds)} ร้าน)\n{'='*55}")

    for s in seeds:
        name, lat, lng = s["name"], s["lat"], s["lng"]
        cuisine = s.get("cuisine", "Cafe")

        if norm_name(name) in known_names:
            skipped += 1
            continue

        places = search_biased(name, lat, lng, GOOGLE_MAPS_API_KEY)
        time.sleep(DELAY)

        pick = None
        for p in places:
            loc = p.get("location") or {}
            if not loc:
                continue
            d = dist_m(lat, lng, loc.get("latitude", 0), loc.get("longitude", 0))
            if d <= MAX_DIST_M:
                pick = (p, d)
                break
        if not pick:
            missed.append(f"{name} (ไม่มีผลลัพธ์ในรัศมี {int(MAX_DIST_M)}m)")
            continue

        p, d = pick
        pid    = p.get("id", "")
        found  = (p.get("displayName") or {}).get("text", "")
        addr   = p.get("formattedAddress", "")
        rating = float(p.get("rating") or 0)
        urc    = int(p.get("userRatingCount") or 0)
        status = p.get("businessStatus", "OPERATIONAL")
        loc    = p.get("location") or {}
        pt     = p.get("primaryType") or ""
        gmaps_types = list(dict.fromkeys(([pt] if pt else []) + (p.get("types") or [])))

        if not pid or pid in known_ids:
            skipped += 1
            continue
        if pid in bl_ids or found.strip() in bl_names:
            print(f"  🚫 blocklisted: {found}")
            skipped += 1
            continue
        if not __import__("re").search(r"กรุงเทพ|Bangkok", addr):
            missed.append(f"{name} (ที่อยู่ไม่ใช่กรุงเทพ: {addr[:40]})")
            continue
        if status == "CLOSED_PERMANENTLY":
            missed.append(f"{name} (ปิดถาวร)")
            continue
        if urc == 0:
            missed.append(f"{name} (ยังไม่มีรีวิว)")
            continue

        print(f"  ✅ {found} — ⭐{rating} ({urc:,} รีวิว) · {extract_area(addr)} · {int(d)}m")
        if args.dry_run:
            added += 1
            continue

        rid = upsert_restaurant({
            "source": "gmaps", "external_id": pid,
            "name": found or name, "cuisine": cuisine,
            "area": s.get("area") or extract_area(addr), "address": addr,
            "city": "Bangkok", "province": "Bangkok",
            "lat": loc.get("latitude"), "lng": loc.get("longitude"),
            "price_range": PRICE_MAP.get(p.get("priceLevel"), "1"),
            "url": f"https://www.google.com/maps/place/?q=place_id:{pid}",
        })
        record_snapshot(rid, review_count=urc, rating=rating, rating_count=urc)
        save_gmaps_meta(rid, {
            "gmaps_place_id": pid, "gmaps_address": addr,
            "gmaps_types": gmaps_types,
            "gmaps_business_status": status or "OPERATIONAL",
            "gmaps_lat": loc.get("latitude"), "gmaps_lng": loc.get("longitude"),
        })
        known_ids.add(pid)
        known_names.add(norm_name(found))
        added += 1

    print(f"\n{'='*55}")
    print(f"  เพิ่ม {added} · ข้าม(มีแล้ว/ซ้ำ) {skipped} · ไม่ผ่าน guard {len(missed)}"
          f"{' (dry-run)' if args.dry_run else ''}")
    for m in missed:
        print(f"    ❓ {m}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
