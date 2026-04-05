"""
ChefMinistry — Wongnai Scraper v2 (API Interception + HTML fallback)
ดึงข้อมูลร้านและ review count จาก wongnai.com

Strategy:
1. ดัก JSON API calls ที่ Wongnai ทำ (เหมือน GrabFood approach)
2. ถ้าไม่ได้จาก API → ลอง HTML selectors หลายแบบ
3. รอ JS render ด้วย wait_for_selector ก่อน query

รัน: python scrape_wongnai.py
     python scrape_wongnai.py thonglor ekkamai  (ระบุ areas)
"""
import asyncio, re, json
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from db import init_db, upsert_restaurant, record_snapshot
from config import BANGKOK_AREAS, DELAY_BETWEEN_PAGES, MAX_PAGES_PER_RUN, HEADLESS, CUISINE_MAP

BASE_URL = "https://www.wongnai.com"

# Wongnai API endpoints ที่มักพบ
WONGNAI_API_PATTERNS = [
    "api.wongnai.com",
    "wongnai.com/api",
    "/graphql",
    "/restaurants/search",
    "/v1/restaurants",
    "/v2/restaurants",
    "wongnai.com/_next/data",   # Next.js data fetching
]

# Selectors หลายแบบ — ลองทีละอัน
RESTAURANT_CARD_SELECTORS = [
    # Next.js / React class-based (อาจ hash)
    "a[href*='/restaurants/bangkok/']",    # link ที่ชี้ไปหน้าร้าน
    "[data-testid='restaurant-card'] a",
    "[data-testid*='restaurant-list'] a",
    "[data-testid*='RestaurantCard'] a",
    # class-based fallbacks
    "[class*='RestaurantCard'] a",
    "[class*='restaurant-card'] a",
    "[class*='restaurantCard'] a",
    "[class*='restaurant-item'] a",
    "[class*='RestaurantListItem'] a",
    # Generic: article / li ที่มี link ไปหน้าร้าน
    "article a[href*='/restaurants/']",
    "li a[href*='/restaurants/bangkok/']",
    # Broadest: ทุก link ที่ URL ตรง pattern ร้าน
    "a[href*='/restaurants/'][href*='-']",  # URL ร้านมักมี dash เช่น somtum-der-12345
]

# Selectors สำหรับดึงข้อมูลในการ์ด
NAME_SELECTORS     = ["h3", "h2", "h4", "[class*='name']", "[class*='title']", "[class*='Name']"]
RATING_SELECTORS   = ["[class*='rating']", "[class*='score']", "[class*='Rating']", "[class*='Score']"]
REVIEW_SELECTORS   = ["[class*='review']", "[class*='count']", "[class*='Review']", "[class*='Count']"]
CUISINE_SELECTORS  = ["[class*='cuisine']", "[class*='category']", "[class*='tag']", "[class*='Cuisine']", "[class*='Category']"]
PRICE_SELECTORS    = ["[class*='price']", "[class*='Price']", "[class*='baht']"]


def detect_cuisine(text: str) -> str:
    t = text.lower()
    for th, en in CUISINE_MAP.items():
        if th in text:
            return en
    mapping = {
        "ราเมน": "ramen", "ramen": "ramen",
        "โอมากาเสะ": "omakase", "omakase": "omakase",
        "สเต็ก": "steakhouse", "steak": "steakhouse",
        "ญี่ปุ่น": "japanese", "japanese": "japanese", "sushi": "japanese",
        "อาหารไทย": "thai", "thai": "thai",
        "คาเฟ่": "cafe", "cafe": "cafe",
        "ซีฟู้ด": "seafood", "seafood": "seafood",
        "อิตาเลียน": "italian", "italian": "italian", "pizza": "italian",
        "อีสาน": "isaan", "isaan": "isaan",
    }
    for kw, cat in mapping.items():
        if kw in t:
            return cat
    return "other"


def parse_price_range(text: str) -> int:
    count = text.count("฿")
    return max(1, min(4, count)) if count else 2


def clean_int(s: str) -> int:
    nums = re.sub(r"[^\d]", "", s or "")
    return int(nums) if nums else 0


def extract_from_wongnai_api(data, area: str) -> list:
    """แกะ JSON จาก Wongnai API / Next.js data"""
    restaurants = []
    if not isinstance(data, dict):
        return []

    # หา list of restaurants ใน JSON
    items = []
    for key in ["restaurants", "data", "results", "items", "list", "feeds"]:
        val = data.get(key, [])
        if isinstance(val, list) and val:
            items = val
            break
        if isinstance(val, dict):
            for sub in ["restaurants", "items", "results", "data"]:
                sub_val = val.get(sub, [])
                if isinstance(sub_val, list) and sub_val:
                    items = sub_val
                    break
        if items:
            break

    # Next.js pageProps structure
    if not items:
        page_props = data.get("pageProps", {})
        for key in ["restaurants", "data", "results"]:
            val = page_props.get(key, [])
            if isinstance(val, list) and val:
                items = val
                break

    for item in items[:150]:
        try:
            if not isinstance(item, dict):
                continue

            ext_id = str(
                item.get("id") or item.get("restaurantId") or
                item.get("_id") or ""
            )
            if not ext_id:
                continue

            name = (
                item.get("name") or item.get("displayName") or
                item.get("nameLocale") or item.get("nameTh") or ""
            )
            if not name:
                continue

            # Rating / reviews
            rating      = float(item.get("rating") or item.get("score") or 0)
            review_count = int(
                item.get("reviewCount") or item.get("totalReviews") or
                item.get("ratingCount") or 0
            )

            # Cuisine
            cats = item.get("categories") or item.get("cuisines") or item.get("tags") or []
            cat_text = " ".join(
                c.get("name", c) if isinstance(c, dict) else str(c)
                for c in (cats if isinstance(cats, list) else [])
            )
            cuisine = detect_cuisine(cat_text or name)

            # Price
            price_raw    = item.get("priceRange") or item.get("priceLevel") or "฿฿"
            price_range  = parse_price_range(str(price_raw)) if "฿" in str(price_raw) else int(price_raw or 2)

            # URL
            slug = item.get("slug") or item.get("urlName") or item.get("permalink") or str(ext_id)
            url  = f"{BASE_URL}/restaurants/{slug}" if not slug.startswith("http") else slug

            # Image
            image_url = (
                item.get("coverImage") or item.get("photoUrl") or
                item.get("thumbnailUrl") or ""
            )
            if isinstance(image_url, dict):
                image_url = image_url.get("url", "")

            restaurants.append({
                "source":        "wongnai",
                "external_id":   ext_id,
                "name":          name,
                "name_en":       item.get("nameEn") or item.get("nameEnglish") or "",
                "cuisine":       cuisine,
                "area":          area,
                "price_range":   int(price_range),
                "url":           url,
                "image_url":     str(image_url) if image_url else "",
                "_review_count": review_count,
                "_rating":       rating,
            })
        except Exception:
            continue

    return restaurants


async def try_query_selector_first(page, selectors: list):
    """ลอง selector ทีละอัน คืนค่าแรกที่ได้ผล"""
    for sel in selectors:
        try:
            els = await page.query_selector_all(sel)
            if els:
                return els, sel
        except:
            continue
    return [], None


async def scrape_area_html(page, area: str, max_pages: int) -> list:
    """HTML fallback: query selectors หลังจาก JS render แล้ว"""
    results = []
    url = f"{BASE_URL}/restaurants/bangkok/{area}"
    print(f"    [HTML mode] {url}")

    for page_num in range(1, max_pages + 1):
        current_url = f"{url}?page={page_num}" if page_num > 1 else url
        try:
            await page.goto(current_url, wait_until="domcontentloaded", timeout=35_000)
            # รอ JS render — ลอง wait_for_selector
            for wait_sel in [
                "a[href*='/restaurants/bangkok/']",
                "[data-testid*='restaurant']",
                "[class*='RestaurantCard']",
                "[class*='restaurant']",
                "main",
            ]:
                try:
                    await page.wait_for_selector(wait_sel, timeout=8_000)
                    break
                except:
                    continue
            await asyncio.sleep(2)
        except PWTimeout:
            print(f"    ⚠️  Timeout page {page_num}")
            break

        cards, matched_sel = await try_query_selector_first(page, RESTAURANT_CARD_SELECTORS)
        if not cards:
            print(f"    ⚠️  No restaurant cards found (page {page_num})")
            print(f"         Tips: รัน 'python debug_scrape.py wongnai' เพื่อดู selector จริง")
            break

        print(f"    Page {page_num}: {len(cards)} cards (selector: {matched_sel})")
        page_count = 0
        seen_hrefs = set()

        for card in cards:
            try:
                href = await card.get_attribute("href") or ""
                if not href or href in seen_hrefs:
                    continue
                # กรอง: URL ต้องเป็นร้านอาหาร (มี pattern รูปร้าน)
                if not re.search(r"/restaurants/[\w-]+/[\w-]+-\d+", href):
                    continue
                seen_hrefs.add(href)

                if not href.startswith("http"):
                    href = BASE_URL + href

                # ดึง id จาก URL
                id_match = re.search(r"-(\d+)/?$", href)
                ext_id = id_match.group(1) if id_match else re.sub(r"[^a-z0-9]", "_", href)[-30:]

                # ชื่อร้านจาก child elements
                name = None
                for sel in NAME_SELECTORS:
                    el = await card.query_selector(sel)
                    if el:
                        txt = (await el.inner_text()).strip()
                        if txt and len(txt) >= 2:
                            name = txt
                            break
                if not name:
                    # ใช้ alt text หรือ title
                    name_raw = await card.get_attribute("title") or await card.get_attribute("aria-label") or ""
                    name = name_raw.strip()
                if not name or len(name) < 2:
                    continue

                # Rating
                rating = 0.0
                for sel in RATING_SELECTORS:
                    el = await card.query_selector(sel)
                    if el:
                        txt = (await el.inner_text()).strip()
                        m = re.search(r"[\d.]+", txt)
                        if m:
                            rating = float(m.group())
                            break

                # Review count
                review_count = 0
                for sel in REVIEW_SELECTORS:
                    el = await card.query_selector(sel)
                    if el:
                        txt = (await el.inner_text()).strip()
                        review_count = clean_int(txt)
                        if review_count > 0:
                            break

                # Cuisine
                cuisine_text = ""
                for sel in CUISINE_SELECTORS:
                    el = await card.query_selector(sel)
                    if el:
                        cuisine_text = (await el.inner_text()).strip()
                        if cuisine_text:
                            break

                # Price
                price_text = "฿฿"
                for sel in PRICE_SELECTORS:
                    el = await card.query_selector(sel)
                    if el:
                        price_text = (await el.inner_text()).strip()
                        if price_text:
                            break

                # Image
                img_el = await card.query_selector("img")
                image_url = await img_el.get_attribute("src") if img_el else ""

                results.append({
                    "source":        "wongnai",
                    "external_id":   ext_id,
                    "name":          name,
                    "name_en":       "",
                    "cuisine":       detect_cuisine(cuisine_text or name),
                    "area":          area,
                    "price_range":   parse_price_range(price_text),
                    "url":           href,
                    "image_url":     image_url or "",
                    "_review_count": review_count,
                    "_rating":       rating,
                })
                page_count += 1
            except Exception:
                continue

        print(f"    → extracted {page_count} valid restaurants")
        if page_count == 0 or page_num >= max_pages:
            break

        next_btn = await page.query_selector(
            "a[aria-label='Next page'], a[rel='next'], "
            "[class*='pagination'] a:last-child, button[aria-label*='next']"
        )
        if not next_btn:
            break
        await asyncio.sleep(DELAY_BETWEEN_PAGES)

    return results


async def scrape_area(page, area: str, max_pages: int, api_results_ref: list) -> list:
    """รวม API interception + HTML fallback"""
    area_api_results = [r for r in api_results_ref if r.get("area") == area]
    if area_api_results:
        print(f"    ✅ Using {len(area_api_results)} restaurants from API interception")
        return area_api_results
    # ถ้าไม่มีจาก API → HTML
    return await scrape_area_html(page, area, max_pages)


async def run(areas: list = None, max_pages: int = None):
    areas     = areas     or BANGKOK_AREAS
    max_pages = max_pages or MAX_PAGES_PER_RUN
    init_db()
    total = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=["--lang=th-TH,th", "--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            locale="th-TH",
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        # ── ดัก API calls ตลอด session ──────────────────────────────────
        all_api_restaurants = []

        async def on_response(resp):
            ct = resp.headers.get("content-type", "")
            u  = resp.url
            if "json" not in ct:
                return
            if not any(kw in u for kw in WONGNAI_API_PATTERNS):
                return
            try:
                body = await resp.json()
                items = extract_from_wongnai_api(body, "unknown")
                if items:
                    print(f"    📡 API hit: {u[:80]} → {len(items)} restaurants")
                    all_api_restaurants.extend(items)
            except:
                pass

        page.on("response", on_response)

        for area in areas:
            print(f"\n  🗺️  Wongnai area: {area}")
            # รีเซ็ต area ใน API results
            for r in all_api_restaurants:
                if r.get("area") == "unknown":
                    r["area"] = area

            restaurants = await scrape_area(page, area, max_pages, all_api_restaurants)

            for r in restaurants:
                rid = upsert_restaurant(r)
                record_snapshot(
                    rid,
                    review_count=r.get("_review_count", 0),
                    rating=r.get("_rating", 0),
                    rating_count=r.get("_review_count", 0),
                )
            total += len(restaurants)
            print(f"  ✅ {area}: saved {len(restaurants)} restaurants")
            await asyncio.sleep(DELAY_BETWEEN_PAGES)

        await browser.close()

    print(f"\n🎉 Wongnai scrape done — {total} restaurants saved")
    if total == 0:
        print("\n  💡 ได้ 0 ร้าน — ลองรัน: python debug_scrape.py wongnai")
        print("     เพื่อดู selector และ API ที่ใช้งานได้จริง")


if __name__ == "__main__":
    import sys
    areas = sys.argv[1:] if len(sys.argv) > 1 else None
    asyncio.run(run(areas=areas))
