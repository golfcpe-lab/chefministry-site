"""
ChefMinistry — LINE MAN Wongnai Scraper (Network Interception)
ดัก API calls ที่ LINE MAN ทำเพื่อดึงข้อมูลร้านในรูป JSON โดยตรง

ข้อมูลที่ได้:
- ชื่อร้าน (ไทย + อังกฤษ)
- Cuisine / category
- Rating + จำนวน review
- ย่าน / พื้นที่จัดส่ง
- Price range
- Delivery info (proxy ของ popularity)

รัน: python scrape_lineman.py
"""
import asyncio, json, re, time
from playwright.async_api import async_playwright
from db import init_db, upsert_restaurant, record_snapshot
from config import HEADLESS, DELAY_BETWEEN_PAGES, CUISINE_MAP

# Bangkok delivery areas พร้อม lat/lng center
LINEMAN_AREAS = [
    {"name": "thonglor",  "lat": 13.7280, "lng": 100.5849},
    {"name": "ekkamai",   "lat": 13.7221, "lng": 100.5872},
    {"name": "silom",     "lat": 13.7225, "lng": 100.5226},
    {"name": "sathorn",   "lat": 13.7205, "lng": 100.5311},
    {"name": "ari",       "lat": 13.7770, "lng": 100.5437},
    {"name": "ratchada",  "lat": 13.7667, "lng": 100.5701},
    {"name": "sukhumvit", "lat": 13.7390, "lng": 100.5597},
    {"name": "onnut",     "lat": 13.7049, "lng": 100.5993},
]

LINEMAN_BASE   = "https://lmwn.com"
LINEMAN_SEARCH = "https://lmwn.com/th"

# LINE MAN API patterns
API_KEYWORDS = [
    "/api/", "/restaurant", "/merchant", "/search",
    "lmwn.com", "wongnai.com/api",
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


def extract_from_lineman_api(data: dict, area_name: str) -> list:
    """
    แกะ JSON response จาก LINE MAN API
    ลอง paths หลายแบบเพราะ structure อาจเปลี่ยน
    """
    restaurants = []

    # ลอง paths ที่ LINE MAN ใช้ทั่วไป
    items = []
    for top_key in ["data", "restaurants", "items", "result", "merchants", "results"]:
        candidate = data.get(top_key, [])
        if isinstance(candidate, list) and candidate:
            items = candidate
            break
        # อาจซ้อนอีก level
        if isinstance(candidate, dict):
            for sub_key in ["items", "restaurants", "data", "merchants"]:
                sub = candidate.get(sub_key, [])
                if isinstance(sub, list) and sub:
                    items = sub
                    break
        if items:
            break

    # Path ทางเลือก: array ตรงๆ
    if not items and isinstance(data, list):
        items = data

    for item in items[:100]:
        try:
            if not isinstance(item, dict):
                continue

            # External ID
            ext_id = (
                str(item.get("id") or "")
                or str(item.get("restaurantId") or "")
                or str(item.get("merchant_id") or "")
            )
            if not ext_id or ext_id == "None":
                continue

            # ชื่อร้าน
            name = (
                item.get("name")
                or item.get("restaurantName")
                or item.get("display_name")
                or item.get("title")
                or ""
            )
            name_en = item.get("nameEn") or item.get("name_en") or ""
            if not name and not name_en:
                continue

            # Cuisine
            cats = (
                item.get("categories")
                or item.get("tags")
                or item.get("cuisines")
                or item.get("foodTypes")
                or []
            )
            if isinstance(cats, list):
                cat_text = " ".join(
                    c.get("name", c) if isinstance(c, dict) else str(c)
                    for c in cats
                )
            else:
                cat_text = str(cats)
            cuisine = detect_cuisine(cat_text or name)

            # Rating + review count
            rating_data = (
                item.get("rating")
                or item.get("ratingInfo")
                or item.get("review")
                or {}
            )
            if isinstance(rating_data, dict):
                rating = float(
                    rating_data.get("score", 0)
                    or rating_data.get("average", 0)
                    or rating_data.get("rating", 0)
                    or 0
                )
                review_count = int(
                    rating_data.get("count", 0)
                    or rating_data.get("total", 0)
                    or rating_data.get("reviewCount", 0)
                    or 0
                )
            else:
                rating = float(rating_data or 0)
                review_count = int(
                    item.get("reviewCount", 0)
                    or item.get("ratingCount", 0)
                    or item.get("totalReview", 0)
                    or 0
                )

            # Price
            price_range = parse_price_level(
                item.get("priceLevel")
                or item.get("price_range")
                or item.get("price")
                or 2
            )

            # URL
            slug = (
                item.get("slug")
                or item.get("urlKey")
                or item.get("permalink")
                or str(ext_id)
            )
            url = f"{LINEMAN_BASE}/r/{slug}" if not slug.startswith("http") else slug

            # Image
            image_url = (
                item.get("coverImage")
                or item.get("imageUrl")
                or item.get("image")
                or item.get("photoUrl")
                or ""
            )
            if isinstance(image_url, dict):
                image_url = image_url.get("url", "")

            restaurants.append({
                "source":        "lineman",
                "external_id":   ext_id,
                "name":          name or name_en,
                "name_en":       name_en,
                "cuisine":       cuisine,
                "area":          area_name,
                "price_range":   price_range,
                "url":           url,
                "image_url":     str(image_url) if image_url else "",
                "_review_count": review_count,
                "_rating":       rating,
            })
        except Exception:
            continue

    return restaurants


async def scrape_area(page, area: dict) -> list:
    """
    1. ไปที่ LINE MAN URL พร้อม location
    2. ดัก API responses
    3. แกะข้อมูลร้านออกมา
    """
    restaurants = []
    api_responses = []
    area_name = area["name"]
    lat, lng = area["lat"], area["lng"]

    print(f"\n  🗺️  LINE MAN area: {area_name}")

    # ── ดัก network responses ──────────────────────────────────────────────
    async def handle_response(response):
        url = response.url
        if any(kw in url for kw in [
            "/api/", "/restaurant", "/merchant", "/search",
            "lmwn.com", "wongnai.com"
        ]):
            try:
                ct = response.headers.get("content-type", "")
                if "json" in ct:
                    body = await response.json()
                    api_responses.append({"url": url, "data": body})
            except:
                pass

    page.on("response", handle_response)

    try:
        # LINE MAN เปิดจาก URL พร้อม coords
        target_url = f"{LINEMAN_SEARCH}?lat={lat}&lng={lng}"
        await page.goto(target_url, wait_until="networkidle", timeout=35_000)
        await asyncio.sleep(4)

        # Scroll เพื่อ trigger more restaurant loads
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
        await asyncio.sleep(2)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 2/3)")
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
        items = extract_from_lineman_api(resp["data"], area_name)
        for item in items:
            if item["external_id"] not in seen_ids:
                seen_ids.add(item["external_id"])
                restaurants.append(item)

    # ── Fallback: HTML scraping ────────────────────────────────────────────
    if not restaurants:
        print(f"    ⚠️  No API data, trying HTML fallback...")
        restaurants = await html_fallback(page, area_name)

    print(f"    Found {len(restaurants)} restaurants")
    return restaurants


async def html_fallback(page, area_name: str) -> list:
    """ดึงจาก HTML โดยตรงถ้า API ไม่สำเร็จ"""
    restaurants = []
    cards = await page.query_selector_all(
        "[class*='restaurant'], [class*='RestaurantCard'], "
        "[class*='merchant'], [data-testid*='restaurant']"
    )
    for card in cards:
        try:
            name_el = await card.query_selector("h3, h2, h4, [class*='name'], [class*='title']")
            name = (await name_el.inner_text()).strip() if name_el else None
            if not name or len(name) < 2:
                continue

            rating_el = await card.query_selector("[class*='rating'], [class*='score'], [class*='star']")
            rating_text = (await rating_el.inner_text()).strip() if rating_el else "0"
            rating_match = re.search(r"[\d.]+", rating_text)
            rating = float(rating_match.group()) if rating_match else 0.0

            cuisine_el = await card.query_selector("[class*='category'], [class*='cuisine'], [class*='tag']")
            cuisine_text = (await cuisine_el.inner_text()).strip() if cuisine_el else ""

            restaurants.append({
                "source":        "lineman",
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
    areas = areas or LINEMAN_AREAS
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

    print(f"\n🎉 LINE MAN scrape done — {total} restaurants saved")


if __name__ == "__main__":
    asyncio.run(run())
