"""
ChefMinistry — Wongnai Scraper v3
Strategy (ลำดับ):
  1. __NEXT_DATA__  — Next.js ฝัง JSON ไว้ใน <script id="__NEXT_DATA__"> ทุกหน้า
  2. API interception — ดัก XHR/fetch ที่หน้าทำ
  3. HTML selectors  — fallback สุดท้าย

ทำไม __NEXT_DATA__ ถึงดีที่สุด:
  - ไม่ต้องรู้ CSS class ที่อาจ hash ทุกครั้ง build
  - ข้อมูลครบ (ชื่อ, rating, review, ราคา) ในครั้งเดียว
  - ไม่ขึ้นกับ JS render / timing

รัน: python scrape_wongnai.py
     python scrape_wongnai.py thonglor ekkamai
"""
import asyncio, re, json, pathlib
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from db import init_db, upsert_restaurant, record_snapshot
from config import BANGKOK_AREAS, DELAY_BETWEEN_PAGES, MAX_PAGES_PER_RUN, HEADLESS, CUISINE_MAP

BASE_URL  = "https://www.wongnai.com"
DEBUG_DIR = pathlib.Path(__file__).parent / "debug_output"


def detect_cuisine(text: str) -> str:
    t = (text or "").lower()
    for th, en in CUISINE_MAP.items():
        if th in text:
            return en
    mapping = {
        "ราเมน": "ramen",    "ramen": "ramen",
        "โอมากาเสะ": "omakase", "omakase": "omakase",
        "สเต็ก": "steakhouse","steak": "steakhouse",
        "ญี่ปุ่น": "japanese", "japanese": "japanese", "sushi": "japanese",
        "อาหารไทย": "thai",   "thai": "thai",
        "คาเฟ่": "cafe",      "cafe": "cafe",
        "ซีฟู้ด": "seafood",  "seafood": "seafood",
        "อิตาเลียน": "italian","italian": "italian","pizza": "italian",
        "อีสาน": "isaan",     "isaan": "isaan",
        "เกาหลี": "korean",   "korean": "korean",
    }
    for kw, cat in mapping.items():
        if kw in t:
            return cat
    return "other"


def parse_price(raw) -> int:
    if not raw:
        return 2
    s = str(raw)
    if "฿" in s:
        return max(1, min(4, s.count("฿")))
    try:
        return max(1, min(4, int(float(s))))
    except:
        return 2


def clean_int(s) -> int:
    nums = re.sub(r"[^\d]", "", str(s or ""))
    return int(nums) if nums else 0


# ─── 1. __NEXT_DATA__ extractor ───────────────────────────────────────────────

def walk_for_restaurants(obj, found=None, depth=0):
    """
    เดิน JSON tree แบบ recursive หาทุก list ที่น่าจะเป็น restaurants
    (มี dict ที่มี key 'name' และ 'id' หรือ 'rating')
    """
    if found is None:
        found = []
    if depth > 10:
        return found
    if isinstance(obj, list):
        if obj and isinstance(obj[0], dict):
            sample = obj[0]
            has_name = any(k in sample for k in ["name", "displayName", "nameTh"])
            has_id   = any(k in sample for k in ["id", "restaurantId", "_id", "publicId"])
            if has_name and has_id:
                found.append(obj)
                return found   # ไม่ลึกต่อจาก list นี้
        for item in obj[:5]:
            walk_for_restaurants(item, found, depth + 1)
    elif isinstance(obj, dict):
        for v in obj.values():
            walk_for_restaurants(v, found, depth + 1)
    return found


def parse_next_data(next_data: dict, area: str) -> list:
    """แกะ __NEXT_DATA__ → list of restaurant dicts"""
    restaurants = []

    # หา restaurant lists ใน JSON tree
    candidates = walk_for_restaurants(next_data)
    if not candidates:
        return []

    # เลือก list ที่ใหญ่ที่สุด
    items = max(candidates, key=len)
    print(f"    __NEXT_DATA__: พบ {len(items)} items")

    for item in items:
        try:
            if not isinstance(item, dict):
                continue

            ext_id = str(
                item.get("id") or item.get("restaurantId") or
                item.get("publicId") or item.get("_id") or ""
            )
            if not ext_id:
                continue

            name = (
                item.get("name") or item.get("displayName") or
                item.get("nameTh") or item.get("nameLocale") or ""
            )
            if not name:
                continue

            # Rating / reviews — อาจอยู่ใน nested object
            rating_obj   = item.get("rating") or item.get("ratingInfo") or {}
            if isinstance(rating_obj, dict):
                rating       = float(rating_obj.get("score") or rating_obj.get("average") or 0)
                review_count = int(rating_obj.get("count") or rating_obj.get("total") or 0)
            else:
                rating       = float(rating_obj or item.get("score") or 0)
                review_count = int(
                    item.get("reviewCount") or item.get("totalReview") or
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
            price_range = parse_price(
                item.get("priceRange") or item.get("priceLevel") or
                item.get("price_range") or 2
            )

            # URL
            slug = item.get("slug") or item.get("urlName") or item.get("permalink") or str(ext_id)
            url  = f"{BASE_URL}/restaurants/{slug}" if not slug.startswith("http") else slug

            # Image
            img = (item.get("coverImage") or item.get("photoUrl") or
                   item.get("thumbnailUrl") or "")
            if isinstance(img, dict):
                img = img.get("url", "")

            restaurants.append({
                "source":        "wongnai",
                "external_id":   ext_id,
                "name":          name,
                "name_en":       item.get("nameEn") or item.get("nameEnglish") or "",
                "cuisine":       cuisine,
                "area":          area,
                "price_range":   price_range,
                "url":           url,
                "image_url":     str(img) if img else "",
                "_review_count": review_count,
                "_rating":       rating,
            })
        except Exception:
            continue

    return restaurants


# ─── 2. API interception ───────────────────────────────────────────────────────

WONGNAI_API_PATTERNS = [
    "api.wongnai.com",
    "wongnai.com/api",
    "/graphql",
    "/restaurants/search",
    "/v1/restaurants", "/v2/restaurants",
    "wongnai.com/_next/data",
]


def parse_api_response(body: dict, area: str) -> list:
    """แกะ JSON จาก API call — ลอง paths หลายแบบ"""
    restaurants = []
    items = []
    for key in ["restaurants", "data", "results", "items", "list", "feeds", "content"]:
        val = body.get(key, [])
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
    if not items:
        page_props = body.get("pageProps", {})
        for key in ["restaurants", "data", "results"]:
            val = page_props.get(key, [])
            if isinstance(val, list) and val:
                items = val
                break
    if not items and isinstance(body, list):
        items = body

    for item in items[:150]:
        try:
            if not isinstance(item, dict):
                continue
            ext_id = str(item.get("id") or item.get("restaurantId") or "")
            name   = item.get("name") or item.get("displayName") or ""
            if not ext_id or not name:
                continue

            rating_obj   = item.get("rating") or item.get("ratingInfo") or {}
            rating       = float(rating_obj.get("score", 0) if isinstance(rating_obj, dict) else rating_obj or 0)
            review_count = int(rating_obj.get("count", 0) if isinstance(rating_obj, dict) else item.get("reviewCount", 0))

            cats     = item.get("categories") or item.get("cuisines") or []
            cat_text = " ".join(c.get("name", c) if isinstance(c, dict) else str(c) for c in cats)
            slug     = item.get("slug") or item.get("urlName") or str(ext_id)
            url      = f"{BASE_URL}/restaurants/{slug}" if not slug.startswith("http") else slug

            restaurants.append({
                "source":        "wongnai",
                "external_id":   ext_id,
                "name":          name,
                "name_en":       item.get("nameEn") or "",
                "cuisine":       detect_cuisine(cat_text or name),
                "area":          area,
                "price_range":   parse_price(item.get("priceRange") or item.get("priceLevel") or 2),
                "url":           url,
                "image_url":     str(item.get("coverImage") or item.get("photoUrl") or ""),
                "_review_count": review_count,
                "_rating":       rating,
            })
        except Exception:
            continue
    return restaurants


# ─── 3. HTML fallback ─────────────────────────────────────────────────────────

async def html_fallback(page, area: str) -> list:
    """
    ดึง href ของร้านจาก link elements แล้วกรองด้วย URL pattern
    ไม่ต้องรู้ class name เลย
    """
    results = []
    # ดึง hrefs ทั้งหมดที่ตรง pattern URL ร้าน
    hrefs = await page.eval_on_selector_all(
        "a",
        """els => els
            .map(e => ({href: e.href, text: e.innerText.trim().substring(0, 80)}))
            .filter(e => /wongnai\\.com\\/restaurants\\/[\\w-]+\\/[\\w-]+-\\d+/.test(e.href))
        """
    )
    print(f"    HTML fallback: พบ {len(hrefs)} restaurant links")

    seen = set()
    for item in hrefs:
        href = item.get("href", "")
        text = item.get("text", "").strip()
        if not href or href in seen:
            continue
        seen.add(href)

        id_match = re.search(r"-(\d+)/?$", href)
        ext_id   = id_match.group(1) if id_match else href[-20:]
        name     = text.split("\n")[0].strip() if text else f"Restaurant {ext_id}"
        if len(name) < 2:
            name = f"Restaurant {ext_id}"

        results.append({
            "source":        "wongnai",
            "external_id":   ext_id,
            "name":          name,
            "name_en":       "",
            "cuisine":       detect_cuisine(name),
            "area":          area,
            "price_range":   2,
            "url":           href,
            "image_url":     "",
            "_review_count": 0,
            "_rating":       0.0,
        })

    return results


# ─── Main scraper ─────────────────────────────────────────────────────────────

async def scrape_area(page, area: str, max_pages: int) -> list:
    results = []
    base_url = f"{BASE_URL}/restaurants/bangkok/{area}"
    print(f"\n  🗺️  Wongnai area: {area}")

    for page_num in range(1, max_pages + 1):
        url = f"{base_url}?page={page_num}" if page_num > 1 else base_url
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=40_000)
            await asyncio.sleep(3)
        except PWTimeout:
            print(f"    ⚠️  Timeout page {page_num}")
            break

        # ── Strategy 1: __NEXT_DATA__ ─────────────────────────────────
        page_results = []
        try:
            next_data_raw = await page.eval_on_selector(
                "#__NEXT_DATA__",
                "el => el.textContent"
            )
            if next_data_raw:
                next_data = json.loads(next_data_raw)
                page_results = parse_next_data(next_data, area)
                if page_results:
                    print(f"    ✅ __NEXT_DATA__: {len(page_results)} restaurants (page {page_num})")
        except Exception as e:
            pass

        # ── Strategy 2: HTML fallback ─────────────────────────────────
        if not page_results:
            page_results = await html_fallback(page, area)
            if page_results:
                print(f"    ✅ HTML links: {len(page_results)} restaurants (page {page_num})")

        if not page_results:
            print(f"    ⚠️  Page {page_num}: 0 restaurants — saving debug HTML")
            DEBUG_DIR.mkdir(exist_ok=True)
            html = await page.content()
            debug_file = DEBUG_DIR / f"wongnai_{area}_p{page_num}.html"
            debug_file.write_text(html, encoding="utf-8")
            print(f"    📄 Saved: {debug_file}")
            break

        # dedup by external_id
        existing = {r["external_id"] for r in results}
        new_items = [r for r in page_results if r["external_id"] not in existing]
        results.extend(new_items)

        if len(page_results) < 5 or page_num >= max_pages:
            break

        await asyncio.sleep(DELAY_BETWEEN_PAGES)

    return results


async def run(areas: list = None, max_pages: int = None):
    areas     = areas or BANGKOK_AREAS
    max_pages = max_pages or MAX_PAGES_PER_RUN
    init_db()
    total = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=[
                "--lang=th-TH,th",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
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
        page = await context.new_page()

        # ── ดัก API calls ตลอด session (bonus: จะได้ถ้า __NEXT_DATA__ ไม่มี) ──
        api_buffer = {}   # area → list

        async def on_response(resp):
            ct = resp.headers.get("content-type", "")
            u  = resp.url
            if "json" not in ct:
                return
            if not any(kw in u for kw in WONGNAI_API_PATTERNS):
                return
            try:
                body = await resp.json()
                items = parse_api_response(body, "api")
                if items:
                    api_buffer.setdefault("api", []).extend(items)
                    print(f"    📡 API: {u[:70]} → {len(items)} restaurants")
            except Exception:
                pass

        page.on("response", on_response)

        for area in areas:
            restaurants = await scrape_area(page, area, max_pages)

            # เพิ่มจาก API buffer ถ้ายังขาด
            if not restaurants and api_buffer.get("api"):
                for r in api_buffer["api"]:
                    r["area"] = area
                restaurants = api_buffer["api"]
                api_buffer.clear()

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
        print(f"\n  ⚠️  ยังได้ 0 — ดูไฟล์ debug HTML ที่ scraper/debug_output/")
        print(f"      แล้วส่งให้ Claude ดูเพื่อหา selector จริง")


if __name__ == "__main__":
    import sys
    areas = sys.argv[1:] if len(sys.argv) > 1 else None
    asyncio.run(run(areas=areas))
