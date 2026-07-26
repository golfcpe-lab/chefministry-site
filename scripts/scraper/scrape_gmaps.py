"""
ChefMinistry — Google Maps Places API Scraper

ดึงข้อมูลจาก Google Maps สำหรับร้านที่มีอยู่ใน DB แล้ว (จาก Wongnai + influencer list)
เพื่อเก็บ review_count snapshot รายวัน → ใช้ track velocity

ค่าใช้จ่าย (ประมาณ) สำหรับ 500 ร้าน:
  - Text Search:        500 × $0.032 = $16
  ใช้ Find Place แทน:   500 × $0.017 = $8.50  (ถูกกว่า)
  + Place Details:      500 × $0.017 = $8.50
  รวม ≈ $17 พอดี

Setup:
  1. ไปที่ https://console.cloud.google.com/
  2. New Project → APIs & Services → Enable "Places API (New)"
  3. Credentials → + Create Credentials → API Key
  4. ใส่ key ใน config.py:  GOOGLE_MAPS_API_KEY = "AIzaSy..."
     หรือ set environment variable: set GOOGLE_MAPS_API_KEY=AIzaSy...

รัน: python scrape_gmaps.py
     python scrape_gmaps.py --limit 50    (ทดสอบ 50 ร้านก่อน)
     python scrape_gmaps.py --area thonglor
     python scrape_gmaps.py --source wongnai
"""
import json, time, sys, pathlib, re, argparse
import urllib.request, urllib.parse
from db import init_db, get_conn, record_snapshot, upsert_restaurant
from config import GOOGLE_MAPS_API_KEY
from classify import classify_record  # v2: venue/scope classification

BASE_URL   = "https://places.googleapis.com/v1"
OLD_BASE   = "https://maps.googleapis.com/maps/api/place"
DEBUG_DIR  = pathlib.Path(__file__).parent / "debug_output"
DEBUG_DIR.mkdir(exist_ok=True)

DELAY = 0.3   # วินาทีระหว่าง API calls (avoid rate limit)


# ── HTTP helper ───────────────────────────────────────────────────────────────

def _get(url: str, headers: dict = None) -> dict:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _post(url: str, body: dict, headers: dict = None) -> dict:
    data = json.dumps(body).encode()
    hdrs = {"Content-Type": "application/json", **(headers or {})}
    req  = urllib.request.Request(url, data=data, headers=hdrs, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


# ── Places API (New) ──────────────────────────────────────────────────────────

def find_place(name: str, area: str, api_key: str, lang: str = "th") -> dict | None:
    """
    ใช้ Places API (New) Text Search หาร้านด้วยชื่อ + ย่าน
    คืน dict ที่มี place_id, displayName, rating, userRatingCount, ...
    """
    # สร้าง query ที่เฉพาะเจาะจง
    query = f"{name} {area} Bangkok Thailand"

    url  = f"{BASE_URL}/places:searchText"
    hdrs = {
        "X-Goog-Api-Key":    api_key,
        "X-Goog-FieldMask":  "places.id,places.displayName,places.rating,"
                              "places.userRatingCount,places.formattedAddress,"
                              "places.location,places.primaryType",
        "Content-Type":      "application/json",
    }
    body = {
        "textQuery":         query,
        "languageCode":      lang,
        "regionCode":        "TH",
        "maxResultCount":    1,
        "locationBias": {
            "circle": {
                "center": _area_to_latlng(area),
                "radius": 3000.0,
            }
        },
    }

    try:
        data   = _post(url, body, hdrs)
        places = data.get("places", [])
        if not places:
            return None
        return places[0]
    except Exception as e:
        print(f"      ❌ find_place({name[:30]}): {e}")
        return None


def get_place_details(place_id: str, api_key: str) -> dict | None:
    """
    Place Details (New API) — ดึง review count, rating, hours, address
    """
    fields = ",".join([
        "id", "displayName", "rating", "userRatingCount",
        "formattedAddress", "internationalPhoneNumber",
        "regularOpeningHours", "location", "websiteUri",
        "primaryType", "types", "businessStatus",
    ])
    url  = f"{BASE_URL}/places/{place_id}"
    hdrs = {
        "X-Goog-Api-Key":   api_key,
        "X-Goog-FieldMask": fields,
    }
    try:
        return _get(url, hdrs)
    except Exception as e:
        print(f"      ❌ get_place_details({place_id}): {e}")
        return None


# ── Area → LatLng ─────────────────────────────────────────────────────────────

AREA_LATLNG = {
    "thonglor":  {"latitude": 13.7280, "longitude": 100.5849},
    "ekkamai":   {"latitude": 13.7221, "longitude": 100.5872},
    "silom":     {"latitude": 13.7225, "longitude": 100.5226},
    "sathorn":   {"latitude": 13.7205, "longitude": 100.5311},
    "ari":       {"latitude": 13.7770, "longitude": 100.5437},
    "ratchada":  {"latitude": 13.7667, "longitude": 100.5701},
    "sukhumvit": {"latitude": 13.7390, "longitude": 100.5597},
    "onnut":     {"latitude": 13.7049, "longitude": 100.5993},
    "ladprao":   {"latitude": 13.8142, "longitude": 100.5655},
    "rama9":     {"latitude": 13.7599, "longitude": 100.5840},
}
_DEFAULT_LATLNG = {"latitude": 13.7563, "longitude": 100.5018}  # Bangkok center

def _area_to_latlng(area: str) -> dict:
    return AREA_LATLNG.get(area, _DEFAULT_LATLNG)


# ── Estimate cost ─────────────────────────────────────────────────────────────

def estimate_cost(n_restaurants: int) -> str:
    # Text Search (New): $0.032/request, Place Details (New Basic): $0.017/request
    search_cost  = n_restaurants * 0.032
    details_cost = n_restaurants * 0.017
    total        = search_cost + details_cost
    return (f"  📊 ประมาณการค่าใช้จ่าย: {n_restaurants} ร้าน\n"
            f"     Text Search : {n_restaurants} × $0.032 = ${search_cost:.2f}\n"
            f"     Place Details: {n_restaurants} × $0.017 = ${details_cost:.2f}\n"
            f"     รวม ≈ ${total:.2f}")


# ── Process one restaurant ────────────────────────────────────────────────────

def process_restaurant(row: dict, api_key: str) -> dict:
    """
    หา place_id และดึง review count สำหรับร้านนึง
    คืน dict ที่มี gmaps_place_id, gmaps_rating, gmaps_review_count, gmaps_address
    """
    name  = row["name"]
    area  = row["area"] or "bangkok"

    # Step 1: หา place
    place = find_place(name, area, api_key)
    if not place:
        return {"status": "not_found"}

    place_id     = place.get("id", "")
    rating       = float(place.get("rating") or 0)
    review_count = int(place.get("userRatingCount") or 0)
    address      = place.get("formattedAddress", "")
    gmaps_name   = (place.get("displayName") or {}).get("text", "")
    _loc         = place.get("location") or {}
    lat          = _loc.get("latitude")
    lng          = _loc.get("longitude")

    time.sleep(DELAY)

    business_status = place.get("businessStatus", "OPERATIONAL")

    # Step 2: Place Details (ถ้า review_count ยังไม่มี หรือต้องการ businessStatus)
    if (review_count == 0 or not business_status) and place_id:
        details      = get_place_details(place_id, api_key)
        if details:
            rating          = float(details.get("rating") or rating)
            review_count    = int(details.get("userRatingCount") or review_count)
            address         = details.get("formattedAddress", address)
            business_status = details.get("businessStatus", business_status)
            _dloc           = details.get("location") or {}
            lat             = _dloc.get("latitude")  or lat
            lng             = _dloc.get("longitude") or lng

    # ── Collect gmaps types for classification ───────────────────────────────
    gmaps_types = []
    primary_type = place.get("primaryType") or ""
    if primary_type:
        gmaps_types.append(primary_type)
    # Also pull from Place Details if fetched
    if "details" in dir() and details:
        gmaps_types.extend(details.get("types") or [])
    gmaps_types = list(dict.fromkeys(t for t in gmaps_types if t))  # deduplicate

    return {
        "status":               "ok",
        "gmaps_place_id":       place_id,
        "gmaps_name":           gmaps_name,
        "gmaps_rating":         rating,
        "gmaps_review_count":   review_count,
        "gmaps_address":        address,
        "gmaps_business_status": business_status,
        "gmaps_types":          gmaps_types,  # v2: for venue classification
        "gmaps_lat":            lat,          # v3: พิกัดร้าน (near-me feature)
        "gmaps_lng":            lng,
    }


# ── Save gmaps metadata to DB ─────────────────────────────────────────────────

def save_gmaps_meta(restaurant_id: str, result: dict):
    """
    เก็บ gmaps_place_id, address ไว้ใน restaurants table
    (ถ้ายังไม่มี column เพิ่มให้อัตโนมัติ)
    """
    with get_conn() as conn:
        # เพิ่ม columns ถ้ายังไม่มี (SQLite ALTER TABLE ทำได้ครั้งละ 1 column)
        existing_cols = {
            row[1] for row in conn.execute("PRAGMA table_info(restaurants)").fetchall()
        }
        for col, typedef in [
            ("gmaps_place_id",       "TEXT"),
            ("gmaps_address",        "TEXT"),
            ("business_status",      "TEXT DEFAULT 'OPERATIONAL'"),
        ]:
            if col not in existing_cols:
                conn.execute(f"ALTER TABLE restaurants ADD COLUMN {col} {typedef}")

        # ── Save classification fields derived from gmaps_types ────────────────
        gmaps_types = result.get("gmaps_types") or []
        import json as _json
        gmaps_types_str = _json.dumps(gmaps_types) if gmaps_types else None

        # Build a minimal record for the classifier (we need name+area from DB)
        row_data = conn.execute(
            "SELECT name, area, cuisine FROM restaurants WHERE id = ?", (restaurant_id,)
        ).fetchone()
        if row_data:
            classification_input = {
                "name":       row_data["name"],
                "area":       row_data["area"] or "",
                "cuisine":    row_data["cuisine"] or "",
                "gmaps_types": gmaps_types,
            }
            classified = classify_record(classification_input)
        else:
            classified = {}

        # ── ชื่อ + ย่าน: เชื่อ Google เป็นหลัก ─────────────────────────────────
        # ชื่อเก่าจาก Wongnai มักมีสาขาห้อยท้าย ("อาเล็กโภชนา พุทธมณฑลสาย3")
        # ทำให้ค้นใน Google Maps ไม่เจอ + ย่านเก่าผิด (บางแค → On Nut)
        gmaps_name = (result.get("gmaps_name") or "").strip()
        new_name = None
        if row_data and gmaps_name:
            old_name = (row_data["name"] or "").strip()
            if gmaps_name != old_name:
                a, b = old_name.lower().replace(" ", ""), gmaps_name.lower().replace(" ", "")
                # อัปเดตเมื่อชื่อ Google เป็น "ตัวย่อ/ตัวเต็ม" ของชื่อเดิม (ร้านเดียวกันแน่)
                if a and (b in a or a in b):
                    new_name = gmaps_name
        new_area = None
        try:
            from area_fix import resolve_area
            _resolved = resolve_area(row_data["area"] if row_data else "",
                                     result.get("gmaps_address") or "")
            if _resolved and _resolved != (row_data["area"] if row_data else ""):
                new_area = _resolved
        except Exception:
            pass

        conn.execute("""
            UPDATE restaurants
            SET gmaps_place_id      = ?,
                gmaps_address       = ?,
                name                = COALESCE(?, name),
                area                = COALESCE(?, area),
                gmaps_types         = ?,
                business_status     = ?,
                city                = COALESCE(?, city),
                province            = COALESCE(?, province),
                venue_type          = COALESCE(?, venue_type),
                scope_market        = COALESCE(?, scope_market),
                is_bangkok_focus    = COALESCE(?, is_bangkok_focus),
                is_restaurant_focus = COALESCE(?, is_restaurant_focus),
                exclude_reason      = ?,
                lat                 = COALESCE(?, lat),
                lng                 = COALESCE(?, lng),
                last_updated        = datetime('now')
            WHERE id = ?
        """, (
            result.get("gmaps_place_id"),
            result.get("gmaps_address"),
            new_name,
            new_area,
            gmaps_types_str,
            result.get("gmaps_business_status", "OPERATIONAL"),
            classified.get("city") or None,
            classified.get("province") or None,
            classified.get("venue_type") or None,
            classified.get("scope_market") or None,
            1 if classified.get("is_bangkok_focus") else None,
            1 if classified.get("is_restaurant_focus") else None,
            classified.get("exclude_reason"),
            result.get("gmaps_lat"),
            result.get("gmaps_lng"),
            restaurant_id,
        ))


# ── Blocklist ─────────────────────────────────────────────────────────────────

def load_blocklist():
    """place_id + ชื่อร้านที่แบน (listing ปลอม/โรงแรม ฯลฯ) — ดู blocklist.json
    ร้านใน blocklist จะไม่ถูก scrape/refresh เลย (ประหยัด API + กันข้อมูลขยะ)"""
    ids, names = set(), set()
    try:
        p = pathlib.Path(__file__).parent / "blocklist.json"
        if p.exists():
            for e in json.loads(p.read_text(encoding="utf-8")):
                if e.get("place_id"): ids.add(e["place_id"].strip())
                if e.get("name"):     names.add(e["name"].strip())
    except Exception as e:
        print(f"  ⚠️ blocklist load error: {e}")
    return ids, names


# ── Refresh existing restaurant (มี place_id แล้ว) ────────────────────────────

def refresh_restaurant(row: dict, api_key: str) -> dict:
    """ร้านที่มี gmaps_place_id แล้ว — เรียก Place Details ตรงๆ (ไม่ต้อง find_place,
    ถูกกว่าครึ่งนึง) เพื่อเก็บ snapshot รายวัน → velocity คำนวณได้จริง"""
    place_id = (row.get("gmaps_place_id") or "").strip()
    if not place_id:
        return {"status": "not_found"}
    details = get_place_details(place_id, api_key)
    if not details:
        return {"status": "not_found"}
    _loc = details.get("location") or {}
    gmaps_types = []
    pt = details.get("primaryType") or ""
    if pt:
        gmaps_types.append(pt)
    gmaps_types.extend(details.get("types") or [])
    gmaps_types = list(dict.fromkeys(t for t in gmaps_types if t))
    return {
        "status":                "ok",
        "gmaps_place_id":        place_id,
        "gmaps_name":            (details.get("displayName") or {}).get("text", ""),
        "gmaps_rating":          float(details.get("rating") or 0),
        "gmaps_review_count":    int(details.get("userRatingCount") or 0),
        "gmaps_address":         details.get("formattedAddress", ""),
        "gmaps_business_status": details.get("businessStatus", "OPERATIONAL"),
        "gmaps_types":           gmaps_types,
        "gmaps_lat":             _loc.get("latitude"),
        "gmaps_lng":             _loc.get("longitude"),
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def run(
    source: str  = None,
    area: str    = None,
    limit: int   = None,
    dry_run: bool = False,
    api_key: str  = None,
):
    api_key = api_key or GOOGLE_MAPS_API_KEY
    if not api_key:
        print("""
  ❌ ไม่มี Google Maps API key!

  วิธีขอ key:
  1. ไปที่ https://console.cloud.google.com/
  2. สร้าง Project ใหม่ (หรือใช้อันเดิม)
  3. APIs & Services → Library → ค้น "Places API (New)" → Enable
  4. APIs & Services → Credentials → + Create Credentials → API Key
  5. ใส่ key ใน scraper/config.py:
       GOOGLE_MAPS_API_KEY = "AIzaSy..."
  6. หรือรัน: set GOOGLE_MAPS_API_KEY=AIzaSy...  (Windows)
        """)
        return

    init_db()

    # ── โหลดรายชื่อร้านจาก DB ──────────────────────────────────────
    with get_conn() as conn:
        query  = "SELECT id, name, area, source FROM restaurants WHERE 1=1"
        params = []
        if source:
            query  += " AND source = ?"
            params.append(source)
        if area:
            query  += " AND area = ?"
            params.append(area)
        # ร้านที่ยังไม่มี gmaps_place_id ก่อน (ประหยัด cost)
        # ตรวจก่อนว่า column มีอยู่จริง
        existing_cols = {
            row[1] for row in conn.execute("PRAGMA table_info(restaurants)").fetchall()
        }
        if "gmaps_place_id" in existing_cols:
            query += " AND (gmaps_place_id IS NULL OR gmaps_place_id = '')"
        query += " ORDER BY name"
        if limit:
            query += f" LIMIT {limit}"
        rows = [dict(r) for r in conn.execute(query, params).fetchall()]

        # ── ร้านเดิมที่มี place_id: refresh หมุนเวียน (เก่าสุดก่อน) ──────────
        # เดิม query ข้างบนกรอง place_id IS NULL อย่างเดียว → ร้านเดิมไม่เคยได้
        # snapshot ใหม่เลย = velocity เป็น 0 ตลอดกาล. เติม refresh ให้เต็ม limit
        refresh_rows = []
        if "gmaps_place_id" in existing_cols:
            q2 = ("SELECT id, name, area, source, gmaps_place_id FROM restaurants"
                  " WHERE gmaps_place_id IS NOT NULL AND gmaps_place_id != ''"
                  " AND (business_status IS NULL OR business_status != 'CLOSED_PERMANENTLY')"
                  " ORDER BY last_updated ASC")
            refresh_rows = [dict(r) for r in conn.execute(q2).fetchall()]

    # ── Blocklist: ข้ามร้านที่แบนตั้งแต่ต้นทาง (ไม่เรียก API เลย) ────────────
    bl_ids, bl_names = load_blocklist()
    def _blocked(r):
        return ((r.get("gmaps_place_id") or "").strip() in bl_ids
                or (r.get("name") or "").strip() in bl_names)
    n_before = len(rows) + len(refresh_rows)
    rows         = [r for r in rows if not _blocked(r)]
    refresh_rows = [r for r in refresh_rows if not _blocked(r)]
    n_blocked = n_before - len(rows) - len(refresh_rows)
    if n_blocked:
        print(f"  🚫 ข้าม {n_blocked} ร้านใน blocklist")

    # ร้านใหม่ก่อน แล้วเติม refresh จนเต็ม limit (คุมงบ API/วัน)
    if limit:
        rows = rows[:limit]
        rows = rows + refresh_rows[: max(0, limit - len(rows))]
    else:
        rows = rows + refresh_rows

    if not rows:
        print("  ℹ️  ไม่มีร้านใน DB — รัน scrape_wongnai_v5.py ก่อน")
        return

    n = len(rows)
    print(estimate_cost(n))
    print(f"\n  ▶  จะ scrape {n} ร้าน")
    if dry_run:
        print("  [dry-run] ไม่ได้เรียก API จริง — จบ")
        return

    print()
    ok_count   = 0
    miss_count = 0
    errors     = []

    for i, row in enumerate(rows, 1):
        rid  = row["id"]
        name = row["name"]
        area_r = row["area"] or "bangkok"

        # progress
        if i % 10 == 0 or i == 1 or i == n:
            print(f"  [{i}/{n}] {name[:35]:<35} ({area_r})")

        if row.get("gmaps_place_id"):
            result = refresh_restaurant(row, api_key)   # มี place_id แล้ว — details อย่างเดียว
        else:
            result = process_restaurant(row, api_key)

        if result["status"] == "ok" and result["gmaps_review_count"] > 0:
            # บันทึก snapshot
            record_snapshot(
                restaurant_id=rid,
                review_count=result["gmaps_review_count"],
                rating=result["gmaps_rating"],
                rating_count=result["gmaps_review_count"],
            )
            # บันทึก metadata
            save_gmaps_meta(rid, result)
            ok_count += 1

            if i <= 5:  # แสดงตัวอย่าง 5 ร้านแรก
                print(f"    ✅ {result['gmaps_name'][:30]} "
                      f"⭐{result['gmaps_rating']} "
                      f"({result['gmaps_review_count']:,} reviews)")
        else:
            miss_count += 1
            if result["status"] == "not_found":
                errors.append(f"    ❓ not found: {name[:40]}")

        time.sleep(DELAY)

    print(f"\n  ✅ สำเร็จ : {ok_count} ร้าน")
    print(f"  ❓ ไม่พบ  : {miss_count} ร้าน")

    if errors[:10]:
        print("\n  ตัวอย่างร้านที่ไม่พบ:")
        for e in errors[:10]:
            print(e)

    # บันทึก log
    log_path = DEBUG_DIR / "gmaps_scrape_log.json"
    log_data = {
        "total": n, "ok": ok_count, "not_found": miss_count,
        "missed_sample": [e.strip() for e in errors[:50]],
    }
    log_path.write_text(json.dumps(log_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  📋 log บันทึกที่: {log_path}")


# ── CLI ────────────────────────────────────────────────────────────────────────

def check_closed_restaurants(api_key: str = None, limit: int = None):
    """
    วนเช็กทุกร้านที่มี gmaps_place_id แล้วอัปเดต business_status
    ใช้รันเดือนละครั้ง หรือเมื่อสงสัยว่าร้านปิด

    python scrape_gmaps.py --check-closed
    python scrape_gmaps.py --check-closed --limit 20
    """
    api_key = api_key or GOOGLE_MAPS_API_KEY
    init_db()

    with get_conn() as conn:
        # เพิ่ม column ถ้ายังไม่มี
        existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(restaurants)").fetchall()}
        if "business_status" not in existing_cols:
            conn.execute("ALTER TABLE restaurants ADD COLUMN business_status TEXT DEFAULT 'OPERATIONAL'")
        if "gmaps_place_id" not in existing_cols:
            print("❌ ยังไม่มีข้อมูล gmaps_place_id — รัน scrape_gmaps.py ก่อน")
            return

        rows = conn.execute("""
            SELECT id, name, gmaps_place_id FROM restaurants
            WHERE gmaps_place_id IS NOT NULL AND gmaps_place_id != ''
            ORDER BY last_updated ASC
        """).fetchall()

    if limit:
        rows = rows[:limit]

    print(f"🔍 เช็ก business_status สำหรับ {len(rows)} ร้าน...")
    closed, temp_closed, ok = [], [], []

    for i, row in enumerate(rows, 1):
        rid, name, place_id = row["id"], row["name"], row["gmaps_place_id"]
        details = get_place_details(place_id, api_key)
        status = "OPERATIONAL"
        if details:
            status = details.get("businessStatus", "OPERATIONAL") or "OPERATIONAL"

        with get_conn() as conn:
            conn.execute(
                "UPDATE restaurants SET business_status = ?, last_updated = datetime('now') WHERE id = ?",
                (status, rid)
            )

        icon = "✅" if status == "OPERATIONAL" else ("⚠️ " if status == "CLOSED_TEMPORARILY" else "❌")
        print(f"  {icon} [{i}/{len(rows)}] {name}: {status}")

        if status == "CLOSED_PERMANENTLY":
            closed.append(name)
        elif status == "CLOSED_TEMPORARILY":
            temp_closed.append(name)
        else:
            ok.append(name)

        time.sleep(DELAY)

    print(f"\n── สรุป ─────────────────────────────────")
    print(f"  ✅ เปิดอยู่:           {len(ok)} ร้าน")
    if temp_closed:
        print(f"  ⚠️  ปิดชั่วคราว:      {len(temp_closed)} ร้าน: {', '.join(temp_closed)}")
    if closed:
        print(f"  ❌ ปิดถาวร (จะถูกกรองออก): {len(closed)} ร้าน: {', '.join(closed)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Google Maps Places scraper")
    ap.add_argument("--source",       help="wongnai / grabfood / lineman (default: ทั้งหมด)")
    ap.add_argument("--area",         help="thonglor / ekkamai / ... (default: ทั้งหมด)")
    ap.add_argument("--limit",        type=int, help="จำกัดจำนวนร้าน (ใช้ทดสอบ)")
    ap.add_argument("--dry-run",      action="store_true", help="แค่ประมาณ cost ไม่เรียก API")
    ap.add_argument("--key",          help="Google Maps API key (override config)")
    ap.add_argument("--check-closed", action="store_true", help="เช็กร้านที่ปิดแล้วจาก Google Maps")
    args = ap.parse_args()

    if args.check_closed:
        check_closed_restaurants(api_key=args.key, limit=args.limit)
    else:
        run(
            source  = args.source,
            area    = args.area,
            limit   = args.limit,
            dry_run = args.dry_run,
            api_key = args.key,
        )
