#!/usr/bin/env python3
"""
ChefMinistry — Seed Curated Classics
ร้านดัง/fine dining 32 ร้านที่เคยเป็น mockup (CM_RESTAURANTS demo) — ingest
เข้า DB ด้วยข้อมูลจริงจาก Google Places แทนคะแนนที่เขียนมือ

ต่างจาก seed_discover: ไม่มี filter ราคา/รีวิวขั้นต่ำ (fine dining แพงและ
รีวิวน้อยกว่า mass) แต่มี name-similarity guard กันจับร้านผิด

ออกแบบให้รันใน CI (scraper.yml) ตอน workflow_dispatch — รันซ้ำได้ปลอดภัย
(dedupe ด้วย place_id + ชื่อ normalize)

Usage:
  python seed_curated.py
  python seed_curated.py --dry-run
"""
import argparse, difflib, json, pathlib, re, sys, time

from db import init_db, upsert_restaurant, record_snapshot, get_conn
from scrape_gmaps import find_place, get_place_details, save_gmaps_meta, load_blocklist, DELAY
from seed_discover import norm_name, extract_area
from config import GOOGLE_MAPS_API_KEY

SEED_FILE = pathlib.Path(__file__).parent / "curated_seed.json"

# cuisine ที่บ่งบอกร้านราคาสูง → price_range 3
PREMIUM_HINTS = ("fine dining", "omakase", "steakhouse", "progressive", "samrub")


def name_matches(query_name: str, found_name: str) -> bool:
    """กันจับร้านผิด: ชื่อที่เจอต้องคล้ายชื่อที่ค้นพอสมควร"""
    a, b = norm_name(query_name), norm_name(found_name)
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    # เทียบเฉพาะส่วนอังกฤษ/ไทยแยกกันด้วย เพราะชื่อมักผสมสองภาษา
    for part in re.split(r"\s+", query_name):
        p = norm_name(part)
        if len(p) >= 4 and p in b:
            return True
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.55


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not GOOGLE_MAPS_API_KEY:
        sys.exit("❌ ไม่พบ GOOGLE_MAPS_API_KEY")
    if not SEED_FILE.exists():
        sys.exit(f"❌ ไม่พบ {SEED_FILE}")

    seeds = json.loads(SEED_FILE.read_text(encoding="utf-8"))

    init_db()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT external_id, gmaps_place_id, name FROM restaurants").fetchall()
    known_ids   = {r["external_id"] for r in rows} | {r["gmaps_place_id"] for r in rows if r["gmaps_place_id"]}
    known_names = {norm_name(r["name"]) for r in rows}
    bl_ids, bl_names = load_blocklist()

    added, skipped, missed = 0, 0, []
    print(f"\n{'='*55}\n  ChefMinistry — Seed Curated Classics ({len(seeds)} ร้าน)\n{'='*55}")

    for s in seeds:
        name, area, cuisine = s["name"], s.get("area", "Bangkok"), s.get("cuisine", "Other")

        if norm_name(name) in known_names:
            print(f"  ⏭  มีอยู่แล้ว: {name}")
            skipped += 1
            continue

        place = find_place(name, area, GOOGLE_MAPS_API_KEY)
        time.sleep(DELAY)
        if not place:
            missed.append(name + " (search ไม่เจอ)")
            continue

        pid        = place.get("id", "")
        found_name = (place.get("displayName") or {}).get("text", "")
        if not pid or pid in known_ids:
            print(f"  ⏭  place ซ้ำใน DB: {name} → {found_name}")
            skipped += 1
            continue
        if pid in bl_ids or found_name.strip() in bl_names:
            print(f"  🚫 blocklisted: {found_name}")
            skipped += 1
            continue
        if not name_matches(name, found_name):
            missed.append(f"{name} (เจอ '{found_name}' — ชื่อไม่ตรงพอ ข้าม)")
            continue

        details = get_place_details(pid, GOOGLE_MAPS_API_KEY) or {}
        time.sleep(DELAY)

        rating = float(details.get("rating") or place.get("rating") or 0)
        urc    = int(details.get("userRatingCount") or place.get("userRatingCount") or 0)
        addr   = details.get("formattedAddress") or place.get("formattedAddress", "")
        status = details.get("businessStatus", "OPERATIONAL")
        loc    = details.get("location") or place.get("location") or {}
        types  = details.get("types") or []
        pt     = details.get("primaryType") or place.get("primaryType") or ""
        gmaps_types = list(dict.fromkeys(([pt] if pt else []) + types))

        if status == "CLOSED_PERMANENTLY":
            missed.append(f"{name} (ปิดถาวรตาม GMaps)")
            continue
        if urc == 0:
            missed.append(f"{name} (ไม่มีรีวิว — ข้าม)")
            continue

        price = "3" if any(h in cuisine.lower() for h in PREMIUM_HINTS) else "2"
        print(f"  ✅ {found_name} — ⭐{rating} ({urc:,} รีวิว) · {extract_area(addr)}")
        if args.dry_run:
            added += 1
            continue

        rid = upsert_restaurant({
            "source": "gmaps", "external_id": pid,
            "name": found_name or name, "cuisine": cuisine,
            "area": extract_area(addr), "address": addr,
            "city": "Bangkok", "province": "Bangkok",
            "lat": loc.get("latitude"), "lng": loc.get("longitude"),
            "price_range": price,
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
        known_names.add(norm_name(found_name))
        added += 1

    print(f"\n{'='*55}")
    print(f"  เพิ่ม {added} · ข้าม(มีแล้ว) {skipped} · ไม่เจอ/ไม่ชัวร์ {len(missed)}"
          f"{' (dry-run)' if args.dry_run else ''}")
    for m in missed:
        print(f"    ❓ {m}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
