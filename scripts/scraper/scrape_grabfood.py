"""
ChefMinistry — GrabFood Scraper v2 (Network Interception + improved timing)
ดัก API calls ที่ GrabFood ทำเพื่อดึงข้อมูลร้านในรูป JSON โดยตรง

แก้ไขจาก v1:
- Listener ไม่ถูก remove ก่อนเวลา (v1 remove ระหว่าง navigate)
- รอ network settle ด้วย load_state แทน networkidle (เร็วกว่า)
- เพิ่ม URL patterns สำหรับ GrabFood API 2024-2025
- ลองทุก JSON response key ที่พบบ่อย
- HTML fallback ที่ robust ขึ้น

รัน: python scrape_grabfood.py
"""
import asyncio, json, re
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

GRAB_BASE   = "https://food.grab.com/th/en"

# URL patterns สำหรับ GrabFood API (ปรับปรุงสำหรับ 2024-2025)
GRAB_API_PATTERNS = [
    "food.grab.com/th/en/api",
    "food.grab.com/api",
    "portal.grab.com",
    "grab.com/grabfood-backend",
    "/merchant/search",
    "/recommendation",
    "/search/restaurant",
    "/v4/", "/v5/", "/v6/", "/v7/", "/v8/",
    "restaurants/search",
    "merchants/search",
    "fulfillment-portal",
]


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
        "คาเฟ่": "cafe", "สเต็ก": "steakhouse",
    }
    for kw, cat in mapping.items():
        if kw in t:
            return cat
    return "other"


def parse_price_level(level) -> int:
    try:
        return max(1, min(4, int(level)))
    except:
        return 2


def extract_from_grab_response(data, area_name: str) -> list:
    """
    แกะ JSON response — ลอง paths ทั้งหมดที่ GrabFood เคยใช้
    """
    if not data:
        return []

    # หา list of restaurants
    items = []

    # Pattern 1: { "data": { "cards": [ { "restaurant": {...} } ] } }
    if not items:
        try:
            cards = data["data"]["cards"]
            if isinstance(cards, list):
                for card in cards:
                    r = card.get("restaurant") or card.get("merchant") or card
                    if isinstance(r, dict) and (r.get("name") or r.get("merchantName")):
                        items.append(r)
        except (KeyError, TypeError):
            pass

    # Pattern 2: { "restaurants": [...] } or { "merchants": [...] }
    if not items:
        for key in ["restaurants", "merchants", "items", "data", "result", "results"]:
            val = data.get(key, [])
            if isinstance(val, list) and val:
                items = val
                break
            if isinstance(val, dict):
                for sub in ["restaurants", "merchants", "items", "data"]:
                    sub_val = val.get(sub, [])
                    if isinstance(sub_val, list) and sub_val:
                        items = sub_val
                        break
            if items:
                break

    # Pattern 3: response IS the list
    if not items and isinstance(data, list):
        items = data

    restaurants = []
    for item in items[:120]:
        try:
            if not isinstance(item, dict):
                continue

            # ID
            ext_id = str(
                item.get("id") or item.get("merchantID") or
                item.get("restaurantID") or item.get("merchant_id") or ""
            )
            if not ext_id or ext_id == "None":
                continue

            # ชื่อ
            name = (
                item.get("name") or item.get("merchantName") or
                item.get("restaurantName") or item.get("displayName") or ""
            )
            name_en = item.get("nameEn") or item.get("name_en") or ""
            if not name and not name_en:
                continue

            # Cuisine
            cats = (
                item.get("categories") or item.get("tags") or
                item.get("cuisines") or item.get("foodTypes") or []
            )
            cat_text = " ".join(
                c.get("name", c) if isinstance(c, dict) else str(c)
                for c in (cats if isinstance(cats, list) else [])
            )
            cuisine = detect_cuisine(cat_text or name)

            # Rating
            rating_raw = item.get("rating") or item.get("ratingInfo") or {}
            if isinstance(rating_raw, dict):
                rating       = float(rating_raw.get("score", 0) or rating_raw.get("average", 0) or 0)
                review_count = int(rating_raw.get("count", 0) or rating_raw.get("total", 0) or 0)
            else:
                rating       = float(rating_raw or 0)
                review_count = int(
                    item.get("reviewCount", 0) or item.get("ratingCount", 0) or
                    item.get("totalReview", 0) or 0
                )

            # Price
            price_range = parse_price_level(
                item.get("priceLevel") or item.get("price_range") or
                item.get("priceRange") or 2
            )

            # URL
            slug = (
                item.get("slug") or item.get("urlKey") or
                item.get("permalink") or str(ext_id)
            )
            url = f"{GRAB_BASE}/restaurant/{slug}" if not slug.startswith("http") else slug

            # Image
            img = (
                item.get("photoHref") or item.get("imageUrl") or
                item.get("coverPhotoInfo", {}).get("url") or
                item.get("heroImgUrl") or ""
            )
            if isinstance(img, dict):
                img = img.get("url", "")

            restaurants.append({
                "source":        "grabfood",
                "external_id":   ext_id,
                "name":          name or name_en,
                "name_en":       name_en,
                "cuisine":       cuisine,
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


async def html_fallback(page, area_name: str) -> list:
    """HTML scraping fallback"""
    restaurants = []
    selectors = [
        "a[href*='/restaurant/']",
        "[data-testid='restaurant-card']",
        "[class*='RestaurantCard']",
        "[class*='restaurantCard']",
        "[class*='merchant-card']",
        "[class*='MerchantCard']",
    ]
    cards = []
    for sel in selectors:
        cards = await page.query_selector_all(sel)
        if cards:
            print(f"    HTML fallback: {len(cards)} cards via '{sel}'")
            break

    if not cards:
        print(f"    ❌ HTML fallback: ไม่พบการ์ดร้านอาหาร")
        return []

    for card in cards:
        try:
            name_el = await card.query_selector(
                "h3, h2, h4, [class*='name'], [class*='title'], [class*='Name']"
            )
            name = (await name_el.inner_text()).strip() if name_el else None
            if not name or len(name) < 2:
                continue

            href = await card.get_attribute("href") or ""
            if not href.startswith("http"):
                href = GRAB_BASE + href

            rating_el = await card.query_selector(
                "[class*='rating'], [class*='score'], [class*='Rating']"
            )
            rating_text = (await rating_el.inner_text()).strip() if rating_el else "0"
            m = re.search(r"[\d.]+", rating_text)
            rating = float(m.group()) if m else 0.0

            cuisine_el = await card.query_selector(
                "[class*='category'], [class*='cuisine'], [class*='tag']"
            )
            cuisine_text = (await cuisine_el.inner_text()).strip() if cuisine_el else ""

            restaurants.append({
                "source":        "grabfood",
                "external_id":   re.sub(r"[^a-z0-9]", "_", name.lower())[:30] + "_html",
                "name":          name,
                "name_en":       "",
                "cuisine":       detect_cuisine(cuisine_text or name),
                "area":          area_name,
                "price_range":   2,
                "url":           href,
                "image_url":     "",
                "_review_count": 0,
                "_rating":       rating,
            })
        except Exception:
            continue

    return restaurants


async def scrape_area(context, area: dict) -> list:
    """
    เปิด page ใหม่ต่อ area — listener คงอยู่จนกว่าจะ close page
    """
    restaurants = []
    api_hits    = []
    area_name   = area["name"]
    lat, lng    = area["lat"], area["lng"]

    print(f"\n  🗺️  GrabFood area: {area_name}")
    page = await context.new_page()

    # ── ผูก listener ก่อน navigate ───────────────────────────────────────
    async def on_response(resp):
        u  = resp.url
        ct = resp.headers.get("content-type", "")
        if "json" not in ct:
            return
        if not any(kw in u for kw in GRAB_API_PATTERNS):
            return
        if resp.status not in (200, 201):
            return
        try:
            body = await resp.json()
            items = extract_from_grab_response(body, area_name)
            if items:
                api_hits.extend(items)
                print(f"    📡 API: {u[:80]} → {len(items)} restaurants")
        except Exception:
            pass

    page.on("response", on_response)

    try:
        # ── Navigate ─────────────────────────────────────────────────────
        target_url = f"{GRAB_BASE}/restaurants?lat={lat}&lng={lng}"
        await page.goto(target_url, wait_until="domcontentloaded", timeout=40_000)

        # รอ content โหลด
        await asyncio.sleep(4)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
        await asyncio.sleep(2)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 2 / 3)")
        await asyncio.sleep(2)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(3)  # รอ lazy-load responses สุดท้าย

    except PWTimeout:
        print(f"    ⚠️  Navigation timeout")
    except Exception as e:
        print(f"    ⚠️  Error: {e}")

    # ── รวมผล ─────────────────────────────────────────────────────────────
    if api_hits:
        # dedup
        seen = set()
        for r in api_hits:
            if r["external_id"] not in seen:
                seen.add(r["external_id"])
                restaurants.append(r)
        print(f"    API total: {len(restaurants)} unique restaurants")
    else:
        print(f"    ⚠️  No API data (0 intercepts) — trying HTML fallback")
        restaurants = await html_fallback(page, area_name)

    await page.close()
    print(f"    Found {len(restaurants)} restaurants")
    return restaurants


async def run(areas: list = None):
    areas = areas or GRAB_AREAS
    init_db()
    total = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=["--lang=th-TH,th", "--no-sandbox",
                  "--disable-blink-features=AutomationControlled"]
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
        print("\n  💡 ได้ 0 ร้าน — ลองรัน: python debug_scrape.py grabfood")
        print("     เพื่อดู API URL ที่ใช้งานจริงและ selector")


if __name__ == "__main__":
    asyncio.run(run())
