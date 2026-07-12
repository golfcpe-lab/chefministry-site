# -*- coding: utf-8 -*-
"""
process_suggestions.py — ตรวจร้านที่ community เสนอผ่านหน้าเว็บ
อ่าน cm_suggestions จาก Firestore (REST) → resolve Google Maps link → เช็คเกณฑ์:
  PASS  : ร้านอาหาร/คาเฟ่ ใน กทม.-ปริมณฑล + rating >= 4.2 + reviews >= 50
          → เพิ่มเข้า DB (source=community) ขึ้นเว็บพร้อมป้าย Community Pick
  NEAR  : rating >= 3.8 + reviews >= 15 → เก็บใน community_shortlist.json
  FAIL  : บันทึกเหตุผลไว้ ไม่ขึ้นเว็บ
สถานะทั้งหมดเก็บใน processed_suggestions.json (กันประมวลผลซ้ำ)
หมายเหตุ: ถ้า Firestore ยังไม่เปิด rules ให้อ่าน — สคริปต์จะเตือนแล้วจบแบบ exit 0
"""
import json, os, re, sys, hashlib, pathlib, sqlite3
import urllib.request, urllib.parse
from datetime import date

HERE = pathlib.Path(__file__).parent
DB = HERE / "chefministry_data.db"
PROCESSED_F = HERE / "processed_suggestions.json"
SHORTLIST_F = HERE / "community_shortlist.json"

FIREBASE_PROJECT = "chefministry-d50e9"
FIREBASE_KEY = "AIzaSyA6-SU_06S9zjCzXBKDtAl1lBuLl9JU9nY"  # web API key (public)
GMAPS_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")

# ── เกณฑ์ (ปรับได้ที่นี่) ────────────────────────────────────────────────
PASS_RATING, PASS_REVIEWS = 4.2, 50
NEAR_RATING, NEAR_REVIEWS = 3.8, 15
FOOD_TYPES = {"restaurant", "food", "cafe", "coffee_shop", "bakery", "bar",
              "meal_takeaway", "meal_delivery", "ice_cream_shop", "dessert_shop"}
BKK_HINTS = ("กรุงเทพ", "Bangkok", "นนทบุรี", "Nonthaburi", "ปทุมธานี", "Pathum",
             "สมุทรปราการ", "Samut Prakan")

CUISINE_FROM_TYPE = {
    "japanese_restaurant": "Japanese", "ramen_restaurant": "Ramen",
    "sushi_restaurant": "Japanese", "thai_restaurant": "Thai",
    "chinese_restaurant": "Chinese", "korean_restaurant": "Korean",
    "italian_restaurant": "Italian", "french_restaurant": "French",
    "pizza_restaurant": "Pizza", "seafood_restaurant": "Seafood",
    "cafe": "Cafe", "coffee_shop": "Cafe", "bakery": "Bakery",
    "dessert_shop": "Dessert", "ice_cream_shop": "Dessert",
    "steak_house": "Steakhouse", "barbecue_restaurant": "BBQ",
    "vietnamese_restaurant": "Vietnamese", "indian_restaurant": "Indian",
}


def http_json(url, method="GET", body=None, headers=None):
    req = urllib.request.Request(url, method=method,
                                 data=json.dumps(body).encode() if body else None,
                                 headers={"Content-Type": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def fetch_suggestions():
    url = (f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT}"
           f"/databases/(default)/documents/cm_suggestions?pageSize=100&key={FIREBASE_KEY}")
    try:
        data = http_json(url)
    except Exception as e:
        print(f"⚠️  อ่าน Firestore ไม่ได้ ({e}) — ต้องตั้ง rules ให้ cm_suggestions อ่านได้ก่อน")
        return None
    out = []
    for doc in data.get("documents", []):
        doc_id = doc["name"].rsplit("/", 1)[-1]
        f = doc.get("fields", {})
        out.append({
            "id": doc_id,
            "url": f.get("url", {}).get("stringValue", ""),
            "note": f.get("note", {}).get("stringValue", ""),
            "by": f.get("submittedBy", {}).get("stringValue", ""),
        })
    return out


def expand_short_link(url):
    """maps.app.goo.gl → ตาม redirect ไป URL เต็ม"""
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.geturl()
    except Exception:
        return url


def resolve_place(url):
    """แปลง Google Maps URL → place object จาก Places API (New)"""
    if "goo.gl" in url or "g.co" in url:
        url = expand_short_link(url)
    name, lat, lng = None, None, None
    m = re.search(r"/maps/place/([^/@]+)", url)
    if m:
        name = urllib.parse.unquote_plus(m.group(1))
    m = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
    if m:
        lat, lng = float(m.group(1)), float(m.group(2))
    if not name:
        q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get("q", [None])[0]
        name = q
    if not name:
        return None, "อ่านชื่อร้านจากลิงก์ไม่ได้"

    body = {"textQuery": name, "languageCode": "th", "maxResultCount": 1}
    if lat and lng:
        body["locationBias"] = {"circle": {"center": {"latitude": lat, "longitude": lng}, "radius": 2000.0}}
    try:
        data = http_json("https://places.googleapis.com/v1/places:searchText", "POST", body, {
            "X-Goog-Api-Key": GMAPS_KEY,
            "X-Goog-FieldMask": ("places.id,places.displayName,places.rating,places.userRatingCount,"
                                 "places.formattedAddress,places.types,places.priceLevel"),
        })
    except Exception as e:
        return None, f"Places API error: {e}"
    places = data.get("places", [])
    if not places:
        return None, "หาร้านใน Google Places ไม่เจอ"
    return places[0], None


def evaluate(p):
    types = set(p.get("types", []))
    addr = p.get("formattedAddress", "")
    rating = p.get("rating", 0) or 0
    reviews = p.get("userRatingCount", 0) or 0
    if not (types & FOOD_TYPES):
        return "fail", "ไม่ใช่ร้านอาหาร/คาเฟ่"
    if not any(h in addr for h in BKK_HINTS):
        return "fail", f"อยู่นอกพื้นที่ กทม.-ปริมณฑล ({addr[:60]})"
    if rating >= PASS_RATING and reviews >= PASS_REVIEWS:
        return "pass", f"rating {rating} · {reviews} reviews"
    if rating >= NEAR_RATING and reviews >= NEAR_REVIEWS:
        return "shortlist", f"rating {rating} · {reviews} reviews (เกือบผ่าน)"
    return "fail", f"rating {rating} · {reviews} reviews ต่ำกว่าเกณฑ์"


def cuisine_of(p):
    for t in p.get("types", []):
        if t in CUISINE_FROM_TYPE:
            return CUISINE_FROM_TYPE[t]
    return "Other"


def add_to_db(p, suggested_by):
    try:
        from area_fix import resolve_area
        area = resolve_area("", p.get("formattedAddress", ""))
    except Exception:
        area = ""
    name = p.get("displayName", {}).get("text", "")
    h = hashlib.sha1((p.get("id") or name).encode()).hexdigest()[:10]
    rid = f"community_{h}"
    conn = sqlite3.connect(str(DB))
    try:
        exists = conn.execute(
            "SELECT 1 FROM restaurants WHERE id=? OR gmaps_place_id=?",
            (rid, p.get("id", ""))).fetchone()
        if exists:
            return rid, False
        conn.execute("""INSERT INTO restaurants
            (id, source, external_id, name, cuisine, area, address,
             gmaps_place_id, gmaps_address, price_range)
            VALUES (?,?,?,?,?,?,?,?,?,?)""", (
            rid, "community", h, name, cuisine_of(p), area or "",
            p.get("formattedAddress", ""), p.get("id", ""),
            p.get("formattedAddress", ""),
            {"PRICE_LEVEL_INEXPENSIVE": 1, "PRICE_LEVEL_MODERATE": 2,
             "PRICE_LEVEL_EXPENSIVE": 3, "PRICE_LEVEL_VERY_EXPENSIVE": 4}.get(p.get("priceLevel"), 2),
        ))
        conn.execute("""INSERT OR IGNORE INTO review_snapshots
            (restaurant_id, snapshot_date, review_count, rating, rating_count)
            VALUES (?,?,?,?,?)""", (
            rid, date.today().isoformat(),
            p.get("userRatingCount", 0), p.get("rating", 0), p.get("userRatingCount", 0)))
        conn.commit()
        return rid, True
    finally:
        conn.close()


def main():
    if not GMAPS_KEY:
        print("⚠️  ไม่มี GOOGLE_MAPS_API_KEY — ข้าม"); return
    processed = json.loads(PROCESSED_F.read_text(encoding="utf-8")) if PROCESSED_F.exists() else {}
    shortlist = json.loads(SHORTLIST_F.read_text(encoding="utf-8")) if SHORTLIST_F.exists() else []

    suggestions = fetch_suggestions()
    if suggestions is None:
        return  # Firestore ยังอ่านไม่ได้ — ไม่ถือว่า error
    pending = [s for s in suggestions if s["id"] not in processed]
    print(f"📨 suggestions ทั้งหมด {len(suggestions)} | ใหม่ {len(pending)}")

    for s in pending:
        place, err = resolve_place(s["url"])
        if err:
            processed[s["id"]] = {"status": "error", "reason": err, "date": date.today().isoformat()}
            print(f"  ❓ {s['url'][:60]} — {err}")
            continue
        verdict, reason = evaluate(place)
        name = place.get("displayName", {}).get("text", "?")
        entry = {"status": verdict, "name": name, "reason": reason,
                 "by": s["by"], "date": date.today().isoformat()}
        if verdict == "pass":
            rid, added = add_to_db(place, s["by"])
            entry["restaurant_id"] = rid
            print(f"  ✅ PASS: {name} — {reason}" + ("" if added else " (มีอยู่แล้ว)"))
        elif verdict == "shortlist":
            shortlist.append({"name": name, "place_id": place.get("id"),
                              "address": place.get("formattedAddress"),
                              "rating": place.get("rating"), "reviews": place.get("userRatingCount"),
                              "note": s["note"], "by": s["by"], "date": date.today().isoformat()})
            print(f"  📋 SHORTLIST: {name} — {reason}")
        else:
            print(f"  ❌ FAIL: {name} — {reason}")
        processed[s["id"]] = entry

    PROCESSED_F.write_text(json.dumps(processed, ensure_ascii=False, indent=1), encoding="utf-8")
    SHORTLIST_F.write_text(json.dumps(shortlist, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"เสร็จ — processed {len(processed)} | shortlist {len(shortlist)}")


if __name__ == "__main__":
    main()
