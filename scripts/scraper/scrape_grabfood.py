"""
ChefMinistry — GrabFood Scraper v3
Strategy:
  1. ดัก ALL JSON responses จาก grab.com (ไม่ filter URL)
  2. ลอง parse ทุก response ว่ามีข้อมูลร้านมั้ย
  3. บันทึก API log ทุกครั้งเพื่อ debug ง่าย
  4. HTML fallback

ทำไม v3 ต่างจาก v2:
  v2 filter URL ด้วย GRAB_API_PATTERNS — ถ้า Grab เปลี่ยน endpoint จะพลาด
  v3 ดัก ทุก JSON response จาก grab.com domain แล้วค่อยกรองว่ามีข้อมูลร้านมั้ย

รัน: python scrape_grabfood.py
"""
import asyncio, re, json, pathlib
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from db import init_db, upsert_restaurant, record_snapshot
from config import HEADLESS, DELAY_BETWEEN_PAGES, CUISINE_MAP

GRAB_AREAS = [
    {"name": "thonglor",  "lat": 13.7280, "lng": 100.5849},
    {"name": "ekkamai",   "lat": 13.7221, "lng": 100.5872},
    {"name": "silom",     "lat": 13.7225, "lng": 100.5226},
    {"name": "sathorn",   "lat": 13.7205, "lng": 100.5311},
    {"name": "ari",       "lat": 13.7770, "lng": 100.5437},
    {"name": "ratchada",  "lat": 13.7667, "lng": 100.5701},
    {"name": "sukhumvit", "lat": 13.7390, "lng": 100.5597},
    {"name": "onnut",     "lat": 13.7049, "lng": 100.5993},
]

GRAB_DOMAINS = ["grab.com", "grabfood", "portal.grab"]
GRAB_BASE    = "https://food.grab.com/th/en"
DEBUG_DIR    = pathlib.Path(__file__).parent / "debug_output"


def detect_cuisine(text: str) -> str:
    t = (text or "").lower()
    for th, en in CUISINE_MAP.items():
        if th in text:
            return en
    mapping = {
        "ramen": "ramen", "omakase": "omakase", "sushi": "japanese",
        "steak": "steakhouse", "thai": "thai", "cafe": "cafe",
        "pizza": "italian", "seafood": "seafood", "bbq": "steakhouse",
        "ราเมน": "ramen", "ญี่ปุ่น": "japanese", "ไทย": "thai",
        "คาเฟ่": "cafe", "สเต็ก": "steakhouse", "เกาหลี": "korean",
    }
    for kw, cat in mapping.items():
        if kw in t:
            return cat
    return "other"


def parse_price(level) -> int:
    try:
        return max(1, min(4, int(level)))
    except:
        return 2


def looks_like_restaurant(obj: dict) -> bool:
    """ตรวจว่า dict นี้น่าจะเป็นข้อมูลร้านมั้ย"""
    name_keys = {"name", "merchantName", "restaurantName", "displayName"}
    id_keys   = {"id", "merchantID", "restaurantID", "merchant_id"}
    return bool(name_keys & obj.keys()) and bool(id_keys & obj.keys())


def find_restaurant_lists(obj, depth=0) -> list:
    """Recursive search หา list ที่มี restaurant dicts"""
    if depth > 8:
        return []
    found = []
    if isinstance(obj, list) and obj:
        if isinstance(obj[0], dict) and looks_like_restaurant(obj[0]):
            return [obj]
        for item in obj[:3]:
            found.extend(find_restaurant_lists(item, depth + 1))
    elif isinstance(obj, dict):
        for v in obj.values():
            found.extend(find_restaurant_lists(v, depth + 1))
    return found


def parse_any_grab_response(data, area_name: str) -> list:
    """
    ลอง parse JSON response ใดๆ จาก Grab
    คืน list of restaurant dicts (อาจว่างถ้าไม่ใช่ restaurant response)
    """
    if not data:
        return []

    # หา restaurant lists
    lists = find_restaurant_lists(data)
    if not lists:
        return []

    items = max(lists, key=len)  # เลือก list ใหญ่สุด
    restaurants = []

    for item in items[:120]:
        try:
            if not isinstance(item, dict):
                continue

            ext_id = str(
                item.get("id") or item.get("merchantID") or
                item.get("restaurantID") or item.get("merchant_id") or ""
            )
            if not ext_id or ext_id == "None":
                continue

            name = (
                item.get("name") or item.get("merchantName") or
                item.get("restaurantName") or item.get("displayName") or ""
            )
            if not name:
                continue

            # Rating
            rating_raw   = item.get("rating") or item.get("ratingInfo") or {}
            if isinstance(rating_raw, dict):
                rating       = float(rating_raw.get("score", 0) or rating_raw.get("average", 0) or 0)
                review_count = int(rating_raw.get("count", 0) or rating_raw.get("total", 0) or 0)
            else:
                rating       = float(rating_raw or 0)
                review_count = int(
                    item.get("reviewCount") or item.get("ratingCount") or
                    item.get("totalReview") or 0
                )

            # Cuisine
            cats = item.get("categories") or item.get("tags") or item.get("cuisines") or []
            cat_text = " ".join(
                c.get("name", c) if isinstance(c, dict) else str(c)
                for c in (cats if isinstance(cats, list) else [])
            )

            # Price
            price_range = parse_price(
                item.get("priceLevel") or item.get("price_range") or
                item.get("priceRange") or 2
            )

            # URL
            slug = item.get("slug") or item.get("urlKey") or item.get("permalink") or str(ext_id)
            url  = f"{GRAB_BASE}/restaurant/{slug}" if not slug.startswith("http") else slug

            # Image
            img = (
                item.get("photoHref") or item.get("imageUrl") or
                item.get("heroImgUrl") or
                (item.get("coverPhotoInfo") or {}).get("url") or ""
            )

            restaurants.append({
                "source":        "grabfood",
                "external_id":   ext_id,
                "name":          name,
                "name_en":       item.get("nameEn") or item.get("name_en") or "",
                "cuisine":       detect_cuisine(cat_text or name),
                "area":          area_name,
                "price_range":   price_range,
                "url":           url,
                "image_url":     str(img) if img else "",
                "_review_count": review_count,
                "_rating":       rating,
            })
        except Exception:
            continue

    return restaurants


async def scrape_area(context, area: dict) -> list:
    area_name = area["name"]
    lat, lng  = area["lat"], area["lng"]
    print(f"\n  🗺️  GrabFood area: {area_name}")

    page = await context.new_page()
    all_responses = []    # [(url, data)]
    restaurants   = []

    # ── ผูก listener ก่อน navigate ───────────────────────────────────────
    async def on_response(resp):
        u  = resp.url
        ct = resp.headers.get("content-type", "")
        # ดัก JSON จาก grab domains ทั้งหมด
        if "json" not in ct:
            return
        if not any(d in u for d in GRAB_DOMAINS):
            return
        if resp.status not in (200, 201):
            return
        try:
            body = await resp.json()
            all_responses.append((u, body))
        except Exception:
            pass

    page.on("response", on_response)

    try:
        target_url = f"{GRAB_BASE}/restaurants?lat={lat}&lng={lng}"
        await page.goto(target_url, wait_until="domcontentloaded", timeout=40_000)
        await asyncio.sleep(5)

        # Scroll ลงเพื่อ trigger lazy load
        for frac in [0.33, 0.66, 1.0]:
            await page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {frac})")
            await asyncio.sleep(2)

        # รอ response สุดท้ายมาถึง
        await asyncio.sleep(3)

    except PWTimeout:
        print(f"    ⚠️  Timeout")
    except Exception as e:
        print(f"    ⚠️  Error: {e}")

    print(f"    Intercepted {len(all_responses)} JSON responses from grab.com")

    # ── บันทึก API log ──────────────────────────────────────────────────
    DEBUG_DIR.mkdir(exist_ok=True)
    api_log = [{"url": u, "keys": list(d.keys()) if isinstance(d, dict) else type(d).__name__}
               for u, d in all_responses]
    log_path = DEBUG_DIR / f"grabfood_{area_name}_api.json"
    log_path.write_text(json.dumps(api_log, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── ลอง parse ทุก response ──────────────────────────────────────────
    seen_ids = set()
    for url, data in all_responses:
        items = parse_any_grab_response(data, area_name)
        if items:
            print(f"    📡 {url[:80]}")
            print(f"       → {len(items)} restaurants")
            for item in items:
                if item["external_id"] not in seen_ids:
                    seen_ids.add(item["external_id"])
                    restaurants.append(item)

    # ── HTML fallback ───────────────────────────────────────────────────
    if not restaurants:
        print(f"    ⚠️  No API data — trying HTML fallback")
        hrefs = await page.eval_on_selector_all(
            "a",
            """els => els
                .map(e => ({href: e.href, text: e.innerText.trim().substring(0,80)}))
                .filter(e => /food\\.grab\\.com.*\\/restaurant\\//.test(e.href))
            """
        )
        seen_h = set()
        for item in hrefs:
            href = item.get("href", "")
            if not href or href in seen_h:
                continue
            seen_h.add(href)
            name = item.get("text", "").split("\n")[0].strip() or href.split("/")[-1]
            ext_id = href.split("/restaurant/")[-1].split("?")[0] or name[:20]
            restaurants.append({
                "source":        "grabfood",
                "external_id":   re.sub(r"[^a-z0-9_-]", "_", ext_id)[:40],
                "name":          name or ext_id,
                "name_en":       "",
                "cuisine":       detect_cuisine(name),
                "area":          area_name,
                "price_range":   2,
                "url":           href,
                "image_url":     "",
                "_review_count": 0,
                "_rating":       0.0,
            })
        if restaurants:
            print(f"    HTML links: {len(restaurants)} restaurants")
        else:
            print(f"    ❌ HTML fallback ก็ไม่ได้ — ดู debug_output/{area_name}_api.json")

    print(f"    Found {len(restaurants)} restaurants")
    await page.close()
    return restaurants


async def run(areas: list = None):
    areas = areas or GRAB_AREAS
    init_db()
    total = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=[
                "--lang=th-TH,th",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        context = await browser.new_context(
            locale="th-TH",
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )

        for area in areas:
            restaurants = await scrape_area(context, area)
            for r in restaurants:
                rid = upsert_restaurant(r)
                record_snapshot(
                    rid,
                    review_count=r.get("_review_count", 0),
                    rating=r.get("_rating", 0),
                    rating_count=r.get("_review_count", 0),
                )
            total += len(restaurants)
            print(f"  ✅ {area['name']}: saved {len(restaurants)} restaurants")
            await asyncio.sleep(DELAY_BETWEEN_PAGES)

        await browser.close()

    print(f"\n🎉 GrabFood scrape done — {total} restaurants saved")
    if total == 0:
        print(f"\n  ⚠️  ยังได้ 0 — ดูไฟล์ scraper/debug_output/grabfood_*_api.json")
        print(f"      ส่งให้ Claude ดูเพื่อหา endpoint จริง")


if __name__ == "__main__":
    asyncio.run(run())
