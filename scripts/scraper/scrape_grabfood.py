"""
ChefMinistry — GrabFood Scraper (Network Interception)
ดัก API calls ที่ GrabFood ทำเพื่อดึงข้อมูลร้านในรูป JSON โดยตรง
วิธีนี้เร็วกว่า HTML scraping มาก และข้อมูลสะอาดกว่า

ข้อมูลที่ได้:
- ชื่อร้าน (ไทย + อังกฤษ)
- Cuisine / category
- Rating + จำนวน review
- ย่าน / พื้นที่จัดส่ง
- Price range
- Estimated delivery time (proxy ของ popularity)

รัน: python scrape_grabfood.py
"""
import asyncio, json, re, time
from playwright.async_api import async_playwright
from db import init_db, upsert_restaurant, record_snapshot
from config import HEADLESS, DELAY_BETWEEN_PAGES, CUISINE_MAP

# Bangkok delivery areas พร้อม lat/lng center
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

# GrabFood URL templates
GRAB_BASE = "https://food.grab.com/th/en"
GRAB_SEARCH_URL = "https://food.grab.com/th/en/restaurants"


def detect_cuisine(text: str) -> str:
    t = (text or "").lower()
    for th, en in CUISINE_MAP.items():
        if th in text:
            return en
    mapping = {
        "ramen": "ramen", "omakase": "omakase", "sushi": "japanese",
        "steak": "steakhouse", "thai": "thai", "cafe": "cafe",
        "pizza": "italian", "seafood": "seafood", "bbq": "steakhouse",
    }
    for kw, cat in mapping.items():
        if kw in t:
            return cat
    return "other"


def parse_price_level(level) -> int:
    """GrabFood price level: 1-4 → 1-4"""
    try:
        return max(1, min(4, int(level)))
    except:
        return 2


def extract_from_grab_api(data: dict, area_name: str) -> list:
    """
    แกะ JSON response จาก GrabFood API
    ลอง paths หลายแบบเพราะ GrabFood อาจเปลี่ยน structure
    """
    restaurants = []

    # Path 1: /v6/merchant/search หรือ /v7/...
    for top_key in ["data", "restaurants", "items", "merchants", "result"]:
        items = data.get(top_key, [])
        if not isinstance(items, list):
            # อาจซ้อนอยู่อีก level
            items = data.get(top_key, {}).get("items", [])
        if items:
            break

    # Path 2: nested cardContent
    if not items and "cardContent" in str(data):
        try:
            items = data["cardContent"]["restaurants"]
        except:
            pass

    for item in items[:100]:  # limit 100 per area
        try:
            # ดึง external_id
            ext_id = (item.get("id") or item.get("merchantID") or
                      item.get("restaurant_id") or "")
            if not ext_id:
                continue

            # ชื่อร้าน
            name = (item.get("name") or item.get("restaurantName") or
                    item.get("merchantName") or "")
            name_en = item.get("nameEn") or item.get("name_en") or ""

            # Cuisine/category
            cats = (item.get("categories") or item.get("tags") or
                    item.get("cuisines") or [])
            if isinstance(cats, list):
                cat_text = " ".join(
                    c.get("name", c) if isinstance(c, dict) else str(c)
                    for c in cats
                )
            else:
                cat_text = str(cats)
            cuisine = detect_cuisine(cat_text or name)

            # Rating
            rating_data = item.get("rating") or item.get("ratingInfo") or {}
            if isinstance(rating_data, dict):
                rating = float(rating_data.get("score", 0) or rating_data.get("rating", 0) or 0)
                review_count = int(rating_data.get("count", 0) or rating_data.get("total", 0) or 0)
            else:
                rating = float(rating_data or 0)
                review_count = int(item.get("reviewCount", 0) or item.get("ratingCount", 0) or 0)

            # Price
            price_range = parse_price_level(
                item.get("priceLevel") or item.get("price_range") or 2
            )

            # URL
            slug = item.get("slug") or item.get("urlKey") or str(ext_id)
            url = f"{GRAB_BASE}/restaurant/{slug}"

            # Image
            photos = item.get("photoHref") or item.get("coverPhotoInfo", {}).get("url") or ""
            image_url = photos if isinstance(photos, str) else ""

            restaurants.append({
                "source":        "grabfood",
                "external_id":   str(ext_id),
                "name":          name or name_en,
                "name_en":       name_en,
                "cuisine":       cuisine,
                "area":          area_name,
                "price_range":   price_range,
                "url":           url,
                "image_url":     image_url,
                "_review_count": review_count,
                "_rating":       rating,
            })
        except Exception as e:
            continue

    return restaurants


async def scrape_area(page, area: dict) -> list:
    """
    1. ไปที่ GrabFood URL ของย่านนั้น
    2. ดัก API responses
    3. แกะข้อมูลร้านออกมา
    """
    restaurants = []
    api_responses = []
    area_name = area["name"]
    lat, lng = area["lat"], area["lng"]

    print(f"\n  🗺️  GrabFood area: {area_name}")

    # ── ดัก network responses ──────────────────────────────────────────────
    async def handle_response(response):
        url = response.url
        # GrabFood ใช้ API endpoints เหล่านี้
        if any(kw in url for kw in [
            "/merchant/search", "/recommendation", "/search/",
            "/v4/", "/v5/", "/v6/", "/v7/",
            "restaurants", "merchants"
        ]) and "grab.com" in url:
            try:
                body = await response.json()
                api_responses.append({"url": url, "data": body})
            except:
                pass  # ไม่ใช่ JSON

    page.on("response", handle_response)

    # ── Navigate พร้อม location params ────────────────────────────────────
    try:
        target_url = f"{GRAB_SEARCH_URL}?lat={lat}&lng={lng}"
        await page.goto(target_url, wait_until="networkidle", timeout=30_000)
        await asyncio.sleep(3)  # รอ lazy-load requests

        # Scroll เพื่อ trigger more loads
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        await asyncio.sleep(2)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

    except Exception as e:
        print(f"    ⚠️  Navigation error: {e}")
        return []
    finally:
        page.remove_listener("response", handle_response)

    # ── แกะ JSON จาก intercepted API calls ────────────────────────────────
    print(f"    Intercepted {len(api_responses)} API responses")
    seen_ids = set()
    for resp in api_responses:
        items = extract_from_grab_api(resp["data"], area_name)
        for item in items:
            if item["external_id"] not in seen_ids:
                seen_ids.add(item["external_id"])
                restaurants.append(item)

    # ── Fallback: HTML scraping ถ้า API ไม่ได้ผล ──────────────────────────
    if not restaurants:
        print(f"    ⚠️  No API data, trying HTML fallback...")
        restaurants = await html_fallback(page, area_name)

    print(f"    Found {len(restaurants)} restaurants")
    return restaurants


async def html_fallback(page, area_name: str) -> list:
    """ดึงจาก HTML โดยตรงถ้า API ไม่สำเร็จ"""
    restaurants = []
    cards = await page.query_selector_all(
        "[class*='RestaurantItem'], [class*='merchantCard'], "
        "[data-testid*='restaurant'], [class*='restaurant-card']"
    )
    for card in cards:
        try:
            name_el = await card.query_selector("h3, h2, [class*='name'], [class*='title']")
            name = (await name_el.inner_text()).strip() if name_el else None
            if not name:
                continue

            rating_el = await card.query_selector("[class*='rating'], [class*='score'], span[class*='star']")
            rating_text = (await rating_el.inner_text()).strip() if rating_el else "0"
            rating_match = re.search(r"[\d.]+", rating_text)
            rating = float(rating_match.group()) if rating_match else 0.0

            cuisine_el = await card.query_selector("[class*='category'], [class*='cuisine'], [class*='tag']")
            cuisine_text = (await cuisine_el.inner_text()).strip() if cuisine_el else ""

            restaurants.append({
                "source":        "grabfood",
                "external_id":   re.sub(r"[^a-z0-9]", "_", name.lower())[:30] + "_html",
                "name":          name,
                "name_en":       None,
                "cuisine":       detect_cuisine(cuisine_text or name),
                "area":          area_name,
                "price_range":   2,
                "url":           await card.get_attribute("href") or "",
                "image_url":     None,
                "_review_count": 0,
                "_rating":       rating,
            })
        except:
            continue
    return restaurants


async def run(areas: list = None):
    areas = areas or GRAB_AREAS
    init_db()
    total = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=["--lang=th-TH,th", "--no-sandbox"]
        )
        context = await browser.new_context(
            locale="th-TH",
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for area in areas:
            restaurants = await scrape_area(page, area)
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


if __name__ == "__main__":
    asyncio.run(run())
