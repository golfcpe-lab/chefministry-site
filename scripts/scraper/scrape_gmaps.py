"""
ChefMinistry — Google Maps Places API Scraper

ดึงข้อมูลจาก Google Maps สำหรับร้านที่มีอยู่ใน DB แล้ว (จาก Wongnai + influencer list)
เพื่อเก็บ review_count snapshot รายวัน → ใช้ track velocity

ค่าใช้จ่าย — อ่าน api_budget.py ประกอบ (สำคัญ):
  Places API (New) คิดเงินตาม "SKU สูงสุดใน field mask" และมีโควตาฟรีต่อเดือน
  แยกตาม SKU (ไม่ใช่เครดิต $200 แบบเดิมแล้ว ตั้งแต่ มี.ค. 2025):

    Place Details Enterprise  $20/1,000  ฟรีแค่ 1,000/เดือน  ← rating, userRatingCount,
                                                               priceLevel, openingHours
    Place Details Pro         $17/1,000  ฟรี  5,000/เดือน   ← displayName, businessStatus
    Text Search Enterprise    $35/1,000  ฟรี  1,000/เดือน
    Text Search Pro           $32/1,000  ฟรี  5,000/เดือน

  ดังนั้น refresh ทุกร้านทุก 2-3 วันด้วย field mask เต็ม = ~6,000 call/เดือน
  = เกินโควตา Enterprise 5,000 call ≈ $100 ≈ ฿3,500/เดือน

  วิธีคุมค่าใช้จ่ายที่ใช้อยู่ตอนนี้ (ดู run() และ api_budget.py):
    Tier A "hot"  — ร้านที่มีรีวิว ≥ CM_HOT_MIN_REVIEWS ใช้ field mask เต็ม
                    (Enterprise) refresh ทุก CM_HOT_INTERVAL_DAYS วัน
                    → velocity ยังคำนวณได้จริง
    Tier B "tail" — ร้านส่วนหางใช้ mask แบบ lite (Pro, ฟรี 5,000/เดือน)
                    refresh ทุก CM_TAIL_INTERVAL_DAYS วัน แค่เช็คว่าร้านยังเปิด
    ทุก call ผ่าน api_budget → หยุดเองเมื่อถึงเพดานโควตาฟรี

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
import json, time, sys, os, pathlib, re, argparse
import urllib.request, urllib.parse
from db import init_db, get_conn, record_snapshot, upsert_restaurant
from config import GOOGLE_MAPS_API_KEY
from classify import classify_record  # v2: venue/scope classification
import api_budget                      # นับ/คุมโควตา API ต่อเดือน

BASE_URL   = "https://places.googleapis.com/v1"
OLD_BASE   = "https://maps.googleapis.com/maps/api/place"
DEBUG_DIR  = pathlib.Path(__file__).parent / "debug_output"
DEBUG_DIR.mkdir(exist_ok=True)

DELAY = 0.3   # วินาทีระหว่าง API calls (avoid rate limit)


# ── Field masks ───────────────────────────────────────────────────────────────
# ⚠️ ห้ามเติม rating / userRatingCount / priceLevel / regularOpeningHours /
#    websiteUri ลงใน *_LITE เด็ดขาด — field พวกนี้ดัน call ขึ้นชั้น Enterprise
#    ที่ฟรีแค่ 1,000/เดือน (LITE ต้องอยู่ชั้น Pro ที่ฟรี 5,000/เดือน)

# ชั้น Enterprise — ใช้เฉพาะร้าน Tier A ที่ต้องใช้ตัวเลขรีวิวคำนวณ velocity
FIELDS_FULL = ",".join([
    "id", "displayName", "rating", "userRatingCount",
    "formattedAddress", "regularOpeningHours", "location", "websiteUri",
    "primaryType", "types", "businessStatus", "priceLevel",
])

# ชั้น Pro — พอสำหรับ "ร้านยังเปิดอยู่ไหม / ชื่อ-พิกัด-ประเภทเปลี่ยนไหม"
FIELDS_LITE = ",".join([
    "id", "displayName", "formattedAddress", "location",
    "primaryType", "types", "businessStatus",
])

# ชั้น Pro สำหรับ Text Search — เดิมใส่ rating+userRatingCount ทำให้ทุกครั้ง
# ที่ค้นร้านใหม่กินโควตา Text Search Enterprise (ฟรีแค่ 1,000/เดือน)
SEARCH_FIELDS_PRO = ",".join([
    "places.id", "places.displayName", "places.formattedAddress",
    "places.location", "places.primaryType", "places.businessStatus",
])


# ── Tier config (ปรับผ่าน env ได้โดยไม่ต้องแก้โค้ด) ──────────────────────────
def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default

# ร้านที่รีวิวถึงเกณฑ์นี้ถึงจะได้ refresh แบบเต็ม (ตรงกับ TREND_MIN_REVIEWS
# ใน dataService.js — ร้านที่ต่ำกว่านี้ยังไงก็ไม่ผ่าน trend floor บนเว็บ)
HOT_MIN_REVIEWS    = _env_int("CM_HOT_MIN_REVIEWS", 150)
HOT_INTERVAL_DAYS  = _env_int("CM_HOT_INTERVAL_DAYS", 7)
TAIL_INTERVAL_DAYS = _env_int("CM_TAIL_INTERVAL_DAYS", 30)


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
    ใช้ Places API (New) Text Search หาร้านด้วยชื่อ + ย่าน — คืน place_id + ข้อมูลพื้นฐาน

    ไม่ขอ rating/userRatingCount ตรงนี้ (จะดันเป็น Text Search Enterprise ที่ฟรี
    แค่ 1,000/เดือน) — ปล่อยให้ get_place_details ดึงตัวเลขรีวิวแทน
    """
    if not api_budget.allow("text_pro"):
        print("      ⏸  โควตา Text Search Pro เดือนนี้หมดแล้ว — ข้าม")
        return None

    # สร้าง query ที่เฉพาะเจาะจง
    query = f"{name} {area} Bangkok Thailand"

    url  = f"{BASE_URL}/places:searchText"
    hdrs = {
        "X-Goog-Api-Key":    api_key,
        "X-Goog-FieldMask":  SEARCH_FIELDS_PRO,
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
        api_budget.record("text_pro")   # นับตอนยิง — Google คิดเงินตาม request
        data   = _post(url, body, hdrs)
        places = data.get("places", [])
        if not places:
            return None
        return places[0]
    except Exception as e:
        print(f"      ❌ find_place({name[:30]}): {e}")
        return None


def get_place_details(place_id: str, api_key: str, lite: bool = False) -> dict | None:
    """
    Place Details (New API)

    lite=False → FIELDS_FULL (ชั้น Enterprise $20/1,000, ฟรี 1,000/เดือน)
                 ได้ rating + userRatingCount → บันทึก snapshot คำนวณ velocity ได้
    lite=True  → FIELDS_LITE (ชั้น Pro $17/1,000, ฟรี 5,000/เดือน)
                 ได้แค่ชื่อ/พิกัด/ประเภท/สถานะเปิด-ปิด แต่ถูกกว่ามากในแง่โควตา
    """
    sku = "details_pro" if lite else "details_ent"
    if not api_budget.allow(sku):
        print(f"      ⏸  โควตา {sku} เดือนนี้หมดแล้ว — ข้าม {place_id}")
        return None

    url  = f"{BASE_URL}/places/{place_id}"
    hdrs = {
        "X-Goog-Api-Key":   api_key,
        "X-Goog-FieldMask": FIELDS_LITE if lite else FIELDS_FULL,
    }
    try:
        api_budget.record(sku)
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

def estimate_cost(n_new: int, n_hot: int, n_tail: int) -> str:
    """ประมาณค่าใช้จ่าย "ส่วนที่เกินโควตาฟรี" ของรอบนี้ (ไม่ใช่ราคาเต็ม)"""
    def _billable(sku, n):
        # โควตาฟรีที่เหลืออยู่ก่อนรอบนี้
        free_left = max(0, api_budget.FREE_CAPS[sku] - api_budget.used(sku))
        return max(0, n - free_left)

    # ร้านใหม่กิน 2 call: Text Search Pro + Place Details Enterprise
    rows = [
        ("text_pro",    n_new),
        ("details_ent", n_new + n_hot),
        ("details_pro", n_tail),
    ]
    lines = [f"  📊 รอบนี้: ร้านใหม่ {n_new} · hot {n_hot} · tail {n_tail}"]
    total_usd = 0.0
    for sku, n in rows:
        if not n:
            continue
        b   = _billable(sku, n)
        usd = b / 1000.0 * api_budget.UNIT_USD[sku]
        total_usd += usd
        lines.append(f"     {sku:<12} {n:>4} call  (เกินโควตาฟรี {b:,})"
                     + (f" ≈ ${usd:.2f}" if usd else " — ฟรี"))
    lines.append(f"     รวมประมาณ ${total_usd:.2f} ≈ ฿{total_usd * api_budget.USD_TO_THB:,.0f}")
    return "\n".join(lines)


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
    address      = place.get("formattedAddress", "")
    gmaps_name   = (place.get("displayName") or {}).get("text", "")
    _loc         = place.get("location") or {}
    lat          = _loc.get("latitude")
    lng          = _loc.get("longitude")
    rating       = 0.0
    review_count = 0
    price_level  = None
    business_status = place.get("businessStatus", "OPERATIONAL")

    if not place_id:
        return {"status": "not_found"}

    time.sleep(DELAY)

    # Step 2: Place Details แบบเต็ม — Text Search (Pro) ไม่คืนตัวเลขรีวิวแล้ว
    # ร้านใหม่ต้องมี rating/reviews ตั้งแต่แรกไม่งั้นไม่มี snapshot ตั้งต้น
    details = get_place_details(place_id, api_key)
    if details:
        rating          = float(details.get("rating") or 0)
        review_count    = int(details.get("userRatingCount") or 0)
        address         = details.get("formattedAddress", address)
        business_status = details.get("businessStatus", business_status)
        price_level     = details.get("priceLevel")
        gmaps_name      = (details.get("displayName") or {}).get("text", "") or gmaps_name
        _dloc           = details.get("location") or {}
        lat             = _dloc.get("latitude")  or lat
        lng             = _dloc.get("longitude") or lng

    # ── Collect gmaps types for classification ───────────────────────────────
    gmaps_types = []
    primary_type = (details or {}).get("primaryType") or place.get("primaryType") or ""
    if primary_type:
        gmaps_types.append(primary_type)
    if details:
        gmaps_types.extend(details.get("types") or [])
    gmaps_types = list(dict.fromkeys(t for t in gmaps_types if t))  # deduplicate

    return {
        "status":               "ok",
        "tier":                 "new",
        "gmaps_place_id":       place_id,
        "gmaps_name":           gmaps_name,
        "gmaps_rating":         rating,
        "gmaps_review_count":   review_count,
        "gmaps_address":        address,
        "gmaps_business_status": business_status,
        "gmaps_types":          gmaps_types,  # v2: for venue classification
        "gmaps_price_level":    price_level,
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
        # ระดับราคาจาก Google — ของเดิมจาก Wongnai มักค้าง (฿1-200 จริงแต่ DB บอก ฿฿)
        _PRICE_MAP = {
            "PRICE_LEVEL_FREE": 1, "PRICE_LEVEL_INEXPENSIVE": 1,
            "PRICE_LEVEL_MODERATE": 2, "PRICE_LEVEL_EXPENSIVE": 3,
            "PRICE_LEVEL_VERY_EXPENSIVE": 3,
        }
        new_price = _PRICE_MAP.get(result.get("gmaps_price_level") or "")

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
                price_range         = COALESCE(?, price_range),
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
            new_price,
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

def refresh_restaurant(row: dict, api_key: str, lite: bool = False) -> dict:
    """ร้านที่มี gmaps_place_id แล้ว — เรียก Place Details ตรงๆ (ไม่ต้อง find_place)

    lite=False (Tier A) → ได้ rating + reviews → บันทึก snapshot → velocity ใช้ได้
    lite=True  (Tier B) → เช็คแค่ว่าร้านยังเปิด/ชื่อ-พิกัดเปลี่ยนไหม (ชั้น Pro,
                          โควตาฟรีมากกว่า 5 เท่า) — ไม่มี snapshot
    """
    place_id = (row.get("gmaps_place_id") or "").strip()
    if not place_id:
        return {"status": "not_found"}
    details = get_place_details(place_id, api_key, lite=lite)
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
        "tier":                  "tail" if lite else "hot",
        "gmaps_place_id":        place_id,
        "gmaps_name":            (details.get("displayName") or {}).get("text", ""),
        "gmaps_rating":          float(details.get("rating") or 0),
        "gmaps_review_count":    int(details.get("userRatingCount") or 0),
        "gmaps_address":         details.get("formattedAddress", ""),
        "gmaps_business_status": details.get("businessStatus", "OPERATIONAL"),
        "gmaps_types":           gmaps_types,
        "gmaps_price_level":     details.get("priceLevel"),
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
        # snapshot ใหม่เลย = velocity เป็น 0 ตลอดกาล
        #
        # ตอนนี้กรองเพิ่ม 2 ชั้นเพื่อประหยัด API:
        #  1. ข้ามร้านที่ยังไงก็ไม่ขึ้นเว็บ (นอก scope / ไม่ใช่ร้านอาหาร / ปิดถาวร)
        #     — เดิมโดน scrape ทุกคืนแล้วค่อยถูกกรองทิ้งตอน export = จ่ายฟรี
        #  2. ดึงจำนวนรีวิวล่าสุดมาด้วย เพื่อแยก Tier A (hot) / Tier B (tail)
        refresh_rows = []
        if "gmaps_place_id" in existing_cols:
            q2 = """
                SELECT r.id, r.name, r.area, r.source, r.gmaps_place_id,
                       r.last_updated,
                       COALESCE((SELECT s.review_count FROM review_snapshots s
                                  WHERE s.restaurant_id = r.id
                                  ORDER BY s.snapshot_date DESC LIMIT 1), 0) AS reviews,
                       CAST(julianday('now') - julianday(COALESCE(r.last_updated, '2000-01-01'))
                            AS INTEGER) AS stale_days
                FROM restaurants r
                WHERE r.gmaps_place_id IS NOT NULL AND r.gmaps_place_id != ''
                  AND (r.business_status IS NULL
                       OR r.business_status != 'CLOSED_PERMANENTLY')
                  AND COALESCE(r.is_restaurant_focus, 1) = 1
                  AND COALESCE(r.is_bangkok_focus, 1) = 1
                  AND COALESCE(r.venue_type, '') != 'non_food_venue'
                ORDER BY r.last_updated ASC
            """
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

    # ── แบ่ง Tier + คุมโควตา ────────────────────────────────────────────────
    # Tier A (hot):  รีวิวถึงเกณฑ์ trend floor → ต้องมีตัวเลขรีวิวสด ๆ เพื่อคำนวณ
    #                velocity → ใช้ field mask เต็ม (Enterprise, ฟรี 1,000/เดือน)
    # Tier B (tail): ที่เหลือ → แค่เช็คว่ายังเปิดอยู่ (Pro, ฟรี 5,000/เดือน)
    # refresh_rows เรียง last_updated ASC อยู่แล้ว → เก่าสุดได้คิวก่อนเสมอ
    hot_all   = [r for r in refresh_rows if (r.get("reviews") or 0) >= HOT_MIN_REVIEWS]
    hot_rows  = [r for r in hot_all if (r.get("stale_days") or 999) >= HOT_INTERVAL_DAYS]
    tail_rows = [r for r in refresh_rows
                 if (r.get("reviews") or 0) < HOT_MIN_REVIEWS
                 and (r.get("stale_days") or 999) >= TAIL_INTERVAL_DAYS]

    # โควตาที่ควรใช้วันนี้ = ที่เหลือทั้งเดือน ÷ วันที่เหลือ (กันใช้หมดต้นเดือน)
    ent_today = api_budget.daily_allowance("details_ent")
    pro_today = api_budget.daily_allowance("details_pro")
    txt_today = api_budget.daily_allowance("text_pro")

    # ร้านใหม่กิน text_pro 1 + details_ent 1 ต่อร้าน → กันโควตา ent ไว้ให้ก่อน
    new_rows  = rows[: max(0, min(txt_today, ent_today))]
    hot_quota = max(0, ent_today - len(new_rows))

    # ⚠️ กันคิว hot ว่างจนไม่มี snapshot ใหม่เลยทั้งวัน — freshness guard ใน
    # scraper.yml จะ fail ถ้าไม่มี snapshot เกิน 2 วัน. ถ้าร้านที่ "ถึงรอบ" มี
    # น้อยกว่าโควตาวันนี้ ให้เติมด้วยร้าน hot ที่เก่าสุดที่ยังไม่ได้ refresh วันนี้
    # (โควตาที่ไม่ใช้ก็หายไปเปล่า ๆ อยู่ดี — ใช้ให้คุ้มดีกว่า)
    if len(hot_rows) < hot_quota:
        seen = {r["id"] for r in hot_rows}
        hot_rows += [r for r in hot_all
                     if r["id"] not in seen and (r.get("stale_days") or 999) >= 1]

    hot_rows  = hot_rows[:hot_quota]
    tail_rows = tail_rows[: max(0, pro_today)]

    # --limit ยังใช้ได้ (เพดานแข็งอีกชั้น เผื่ออยากทดสอบ)
    if limit:
        new_rows  = new_rows[:limit]
        hot_rows  = hot_rows[: max(0, limit - len(new_rows))]
        tail_rows = tail_rows[: max(0, limit - len(new_rows) - len(hot_rows))]

    for r in new_rows:
        r["_tier"] = "new"
    for r in hot_rows:
        r["_tier"] = "hot"
    for r in tail_rows:
        r["_tier"] = "tail"
    rows = new_rows + hot_rows + tail_rows

    print(api_budget.report())
    print()
    print(estimate_cost(len(new_rows), len(hot_rows), len(tail_rows)))
    print(f"     โควตาที่ใช้ได้วันนี้: ent {ent_today} · pro {pro_today} · text {txt_today}")

    if not rows:
        print("\n  ℹ️  ไม่มีร้านที่ถึงรอบ refresh วันนี้ (หรือโควตาเดือนนี้หมดแล้ว) — จบ")
        return

    n = len(rows)
    print(f"\n  ▶  จะ scrape {n} ร้าน")
    if dry_run:
        print("  [dry-run] ไม่ได้เรียก API จริง — จบ")
        return

    print()
    ok_count   = 0
    miss_count = 0
    errors     = []

    tier_counts = {"new": 0, "hot": 0, "tail": 0}

    for i, row in enumerate(rows, 1):
        rid  = row["id"]
        name = row["name"]
        area_r = row["area"] or "bangkok"
        tier = row.get("_tier", "hot")

        # progress
        if i % 10 == 0 or i == 1 or i == n:
            print(f"  [{i}/{n}] {tier:<4} {name[:32]:<32} ({area_r})")

        if row.get("gmaps_place_id"):
            # มี place_id แล้ว — details อย่างเดียว; tail ใช้ mask แบบ lite
            result = refresh_restaurant(row, api_key, lite=(tier == "tail"))
        else:
            result = process_restaurant(row, api_key)

        if result["status"] == "ok":
            # snapshot เก็บได้เฉพาะรอบที่ขอ rating/reviews มาจริง (new/hot)
            # tail ใช้ mask ชั้น Pro ที่ไม่มีตัวเลขรีวิว — ข้าม snapshot ไม่ใช่ error
            if result.get("gmaps_review_count", 0) > 0:
                record_snapshot(
                    restaurant_id=rid,
                    review_count=result["gmaps_review_count"],
                    rating=result["gmaps_rating"],
                    rating_count=result["gmaps_review_count"],
                )
            # บันทึก metadata (อัปเดต last_updated → เข้าคิว refresh รอบถัดไป)
            save_gmaps_meta(rid, result)
            ok_count += 1
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

            if i <= 5:  # แสดงตัวอย่าง 5 ร้านแรก
                if result.get("gmaps_review_count"):
                    print(f"    ✅ {result['gmaps_name'][:30]} "
                          f"⭐{result['gmaps_rating']} "
                          f"({result['gmaps_review_count']:,} reviews)")
                else:
                    print(f"    ✅ {result['gmaps_name'][:30]} "
                          f"[{result.get('gmaps_business_status')}]")
        else:
            miss_count += 1
            if result["status"] == "not_found":
                errors.append(f"    ❓ not found: {name[:40]}")

        time.sleep(DELAY)

    print(f"\n  ✅ สำเร็จ : {ok_count} ร้าน "
          f"(ใหม่ {tier_counts['new']} · hot {tier_counts['hot']} · tail {tier_counts['tail']})")
    print(f"  ❓ ไม่พบ  : {miss_count} ร้าน")
    print()
    print(api_budget.report())

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
        # ต้องการแค่ businessStatus → ใช้ mask ชั้น Pro (ฟรี 5,000/เดือน)
        # เดิมใช้ mask เต็มซึ่งเป็นชั้น Enterprise (ฟรีแค่ 1,000/เดือน)
        details = get_place_details(place_id, api_key, lite=True)
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
