"""
ChefMinistry — Wongnai Scraper v5
แก้ปัญหา: Wongnai ใช้ Cloudflare WAF ตรวจ TLS fingerprint (JA3/JA4)
→ requests และ headless Playwright ถูก block ตั้งแต่ระดับ CDN

Strategy stack (ลำดับ):
  1. curl-cffi  — impersonate Chrome TLS fingerprint จริงๆ (ผ่าน Cloudflare ได้)
  2. Playwright (non-headless) — เปิดหน้าต่าง browser จริง ถ้า curl-cffi ไม่พอ
  3. Playwright + playwright-stealth (headless fallback)

ติดตั้งก่อนรัน:
  pip install curl-cffi playwright playwright-stealth
  playwright install chromium
"""
import asyncio, re, json, pathlib, sys
from db import init_db, upsert_restaurant, record_snapshot
from config import BANGKOK_AREAS, DELAY_BETWEEN_PAGES, MAX_PAGES_PER_RUN, CUISINE_MAP

BASE_URL  = "https://www.wongnai.com"
DEBUG_DIR = pathlib.Path(__file__).parent / "debug_output"
DEBUG_DIR.mkdir(exist_ok=True)

WONGNAI_API_PATTERNS = [
    "api.wongnai.com", "wongnai.com/api", "/graphql",
    "/restaurants/search", "/v1/restaurants", "/v2/restaurants",
    "_next/data",
]

# ── URL mapping ที่ถูกต้องสำหรับแต่ละ area ──────────────────────────────────────
# ค้นพบจาก web search — แต่ละ area มี URL ที่ต่างกัน
# ลำดับ: listings page (มี schema.org ครบ) → regions= URL → search URL

AREA_URLS: dict[str, list[str]] = {
    "thonglor": [
        f"{BASE_URL}/listings/restaurants-in-thonglor",   # ✅ ยืนยันแล้ว
        f"{BASE_URL}/restaurants?regions=224&rerank=true&domain=1",
    ],
    "ekkamai": [
        f"{BASE_URL}/listings/ekkamai-restaurant",
        f"{BASE_URL}/restaurants?regions=18675&rerank=true&domain=1",
    ],
    "silom": [
        f"{BASE_URL}/listings/foods-around-silom-district",
        f"{BASE_URL}/restaurants?regions=32&rerank=true&domain=1",
    ],
    "sathorn": [
        f"{BASE_URL}/listings/must-try-restaurants-sathorn",
        f"{BASE_URL}/restaurants?regions=135&rerank=true&domain=1",
    ],
    "ari": [
        f"{BASE_URL}/listings/ari-restaurants",
        f"{BASE_URL}/listings/restaurants-in-ari",
        f"{BASE_URL}/restaurants?regions=242&rerank=true&domain=1",
    ],
    "ratchada": [
        f"{BASE_URL}/listings/ratchada-restaurants",
        f"{BASE_URL}/listings/restaurants-in-ratchada",
        f"{BASE_URL}/restaurants?regions=180&rerank=true&domain=1",  # approx
    ],
    "sukhumvit": [
        f"{BASE_URL}/listings/sukhumvit-restaurants-with-good-atmosphere",
        f"{BASE_URL}/listings/nice-atmosphere-restaurants-in-sukhumvit",
        f"{BASE_URL}/listings/buffets-around-sukhumvit",
        f"{BASE_URL}/listings/must-try-restaurants-sukhumvit",
        f"{BASE_URL}/restaurants?regions=230&rerank=true&domain=1",  # soi 11-19 area
        f"{BASE_URL}/restaurants?regions=12809&rerank=true&domain=1",  # sukhumvit plaza
    ],
    "onnut": [
        f"{BASE_URL}/listings/onnut-restaurants",
        f"{BASE_URL}/listings/restaurants-in-on-nut",
        f"{BASE_URL}/restaurants?regions=183&rerank=true&domain=1",  # approx
    ],
    "ladprao": [
        f"{BASE_URL}/listings/ladprao-restaurants",
        f"{BASE_URL}/restaurants?regions=175&rerank=true&domain=1",
    ],
    "rama9": [
        f"{BASE_URL}/listings/must-try-restaurants-at-rama9",
        f"{BASE_URL}/listings/restaurants-in-rama-9",
        f"{BASE_URL}/restaurants?regions=156&rerank=true&domain=1",  # approx
    ],
}


def get_area_urls(area: str) -> list[str]:
    """Return ordered list of URLs to try for this area"""
    return AREA_URLS.get(area, [
        f"{BASE_URL}/listings/restaurants-in-{area}",
        f"{BASE_URL}/restaurants?for={area}&locale=en",
    ])

# ── Helpers (same as v4) ───────────────────────────────────────────────────────

def detect_cuisine(text: str) -> str:
    t = (text or "").lower()
    for th, en in CUISINE_MAP.items():
        if th in text:
            return en
    mapping = {
        "ราเมน": "ramen",     "ramen": "ramen",
        "โอมากาเสะ": "omakase","omakase": "omakase",
        "สเต็ก": "steakhouse", "steak": "steakhouse",
        "ญี่ปุ่น": "japanese",  "japanese": "japanese", "sushi": "japanese",
        "อาหารไทย": "thai",    "thai": "thai",
        "คาเฟ่": "cafe",       "cafe": "cafe",
        "ซีฟู้ด": "seafood",   "seafood": "seafood",
        "อิตาเลียน": "italian", "italian": "italian", "pizza": "italian",
        "อีสาน": "isaan",      "isaan": "isaan",
        "เกาหลี": "korean",    "korean": "korean",
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


def item_to_restaurant(item: dict, area: str) -> dict | None:
    try:
        ext_id = str(
            item.get("id") or item.get("restaurantId") or
            item.get("publicId") or item.get("_id") or ""
        )
        if not ext_id:
            return None

        name = (
            item.get("name") or item.get("displayName") or
            item.get("nameTh") or item.get("nameLocale") or ""
        )
        if not name:
            return None

        rating_obj = item.get("rating") or item.get("ratingInfo") or {}
        if isinstance(rating_obj, dict):
            rating       = float(rating_obj.get("score") or rating_obj.get("average") or 0)
            review_count = int(rating_obj.get("count") or rating_obj.get("total") or 0)
        else:
            rating       = float(rating_obj or item.get("score") or 0)
            review_count = int(item.get("reviewCount") or item.get("totalReview") or 0)

        cats = item.get("categories") or item.get("cuisines") or item.get("tags") or []
        cat_text = " ".join(
            c.get("name", c) if isinstance(c, dict) else str(c)
            for c in (cats if isinstance(cats, list) else [])
        )

        slug = item.get("slug") or item.get("urlName") or item.get("permalink") or str(ext_id)
        url  = f"{BASE_URL}/restaurants/{slug}" if not slug.startswith("http") else slug

        img = item.get("coverImage") or item.get("photoUrl") or item.get("thumbnailUrl") or ""
        if isinstance(img, dict):
            img = img.get("url", "")

        return {
            "source":        "wongnai",
            "external_id":   ext_id,
            "name":          name,
            "name_en":       item.get("nameEn") or item.get("nameEnglish") or "",
            "cuisine":       detect_cuisine(cat_text or name),
            "area":          area,
            "price_range":   parse_price(item.get("priceRange") or item.get("priceLevel") or 2),
            "url":           url,
            "image_url":     str(img) if img else "",
            "_review_count": review_count,
            "_rating":       rating,
        }
    except Exception:
        return None


def walk_for_restaurants(obj, depth=0) -> list:
    if depth > 10:
        return []
    found = []
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        sample = obj[0]
        has_name = any(k in sample for k in ["name", "displayName", "nameTh"])
        has_id   = any(k in sample for k in ["id", "restaurantId", "_id", "publicId"])
        if has_name and has_id:
            return [obj]
        for item in obj[:3]:
            found.extend(walk_for_restaurants(item, depth + 1))
    elif isinstance(obj, dict):
        for v in obj.values():
            found.extend(walk_for_restaurants(v, depth + 1))
    return found


def parse_json_for_restaurants(data, area: str) -> list:
    candidates = walk_for_restaurants(data)
    if not candidates:
        return []
    items = max(candidates, key=len)
    results = []
    for item in items[:150]:
        r = item_to_restaurant(item, area)
        if r:
            results.append(r)
    return results


# ── Schema.org JSON-LD parser (format ใหม่ของ Wongnai listings page) ──────────

def parse_price_dollar(raw: str) -> int:
    """แปลง "$", "$$", "$$$", "$$$$" → 1-4"""
    if not raw:
        return 2
    count = raw.count("$")
    return max(1, min(4, count)) if count else 2


def _restaurant_from_url(url: str, area: str) -> dict | None:
    """แกะ restaurant record จาก Wongnai URL เท่านั้น (ไม่มี rating)
    pattern: wongnai.com/restaurants/{alphanumericId}-{slug}
    """
    from urllib.parse import unquote
    m = re.search(r"/restaurants/([A-Za-z0-9]+)-(.+?)(?:\?|#|$)", url)
    if not m:
        return None
    ext_id = m.group(1)
    slug   = unquote(m.group(2)).replace("-", " ").replace("+", " ").strip()
    # slug มักเป็น English mixed Thai — ใช้เป็น fallback name
    name = slug[:80] if slug else f"Restaurant {ext_id}"
    return {
        "source":        "wongnai",
        "external_id":   ext_id,
        "name":          name,
        "name_en":       "",
        "cuisine":       detect_cuisine(name),
        "area":          area,
        "price_range":   2,
        "url":           url,
        "image_url":     "",
        "_review_count": 0,
        "_rating":       0.0,
    }


def parse_schema_org_restaurants(html: str, area: str) -> list:
    """
    แกะ Schema.org JSON-LD ItemList จาก HTML — รองรับ 2 formats:
    1. listings pages → ItemList > ListItem > item > Restaurant (มี name, rating, cuisine ครบ)
    2. regions= pages → ItemList > ListItem > url only (แค่ URL ไม่มี rating)
    """
    schemas = re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.DOTALL | re.IGNORECASE
    )
    full_results  = []   # มี name + rating
    url_results   = []   # มีแค่ URL

    for raw in schemas:
        try:
            data = json.loads(raw)
        except:
            continue

        if data.get("@type") != "ItemList":
            continue

        for list_item in data.get("itemListElement", []):
            # ── Format 1: มี item.@type == Restaurant ─────────────────────────
            restaurant = list_item.get("item") or {}
            if restaurant.get("@type") == "Restaurant":
                name = restaurant.get("name", "").strip()
                if not name:
                    continue

                ext_id = ""
                url    = restaurant.get("url", "")
                m      = re.search(r"#(\d+)$", url)
                if m:
                    ext_id = m.group(1)
                if not ext_id:
                    menu_url = restaurant.get("menu", "")
                    m2 = re.search(r"/restaurants/([^/]+)/menu", menu_url)
                    if m2:
                        ext_id = m2.group(1)
                if not ext_id:
                    ext_id = re.sub(r"[^\w]", "", name.lower())[:20]

                agg          = restaurant.get("aggregateRating") or {}
                rating       = float(agg.get("ratingValue") or 0)
                review_count = int(agg.get("ratingCount") or 0)
                cuisine_raw  = restaurant.get("servesCuisine", "")
                cuisine_text = cuisine_raw if isinstance(cuisine_raw, str) else " ".join(cuisine_raw)
                price_range  = parse_price_dollar(restaurant.get("priceRange", ""))
                image        = restaurant.get("image", "")
                if isinstance(image, list):
                    image = image[0] if image else ""
                menu_url = restaurant.get("menu", "")
                rest_url = menu_url.replace("/menu", "") if menu_url else url

                full_results.append({
                    "source":        "wongnai",
                    "external_id":   str(ext_id),
                    "name":          name,
                    "name_en":       "",
                    "cuisine":       detect_cuisine(cuisine_text or name),
                    "area":          area,
                    "price_range":   price_range,
                    "url":           rest_url or url,
                    "image_url":     str(image),
                    "_review_count": review_count,
                    "_rating":       rating,
                })

            # ── Format 2: มีแค่ URL (regions= pages) ─────────────────────────
            else:
                url = list_item.get("url", "")
                if "wongnai.com/restaurants/" in url:
                    r = _restaurant_from_url(url, area)
                    if r:
                        url_results.append(r)

    # คืน full results ก่อน (มี rating) ถ้าไม่มีค่อย fallback เป็น URL-only
    return full_results if full_results else url_results


def parse_html_for_restaurants(html: str, area: str) -> list:
    """
    ลอง parse ทุก format ที่ Wongnai ใช้:
    1. __NEXT_DATA__ (format เก่า)
    2. Schema.org JSON-LD ItemList (format ใหม่, listings pages)
    """
    # 1. __NEXT_DATA__
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
    if m and len(m.group(1)) > 100:
        try:
            data = json.loads(m.group(1))
            results = parse_json_for_restaurants(data, area)
            if results:
                return results, "next_data"
        except:
            pass

    # 2. Schema.org JSON-LD
    results = parse_schema_org_restaurants(html, area)
    if results:
        return results, "schema_org"

    return [], "none"


# ── Strategy 1: curl-cffi (Chrome TLS impersonation) ─────────────────────────

def try_curl_cffi_strategy(area: str, page_num: int = 1) -> list:
    """
    ใช้ curl-cffi เพื่อ impersonate TLS fingerprint ของ Chrome จริงๆ
    ลอง URL ใหม่หลายรูปแบบ (Wongnai เปลี่ยน URL structure แล้ว)

    pip install curl-cffi
    """
    try:
        from curl_cffi import requests as cffi_requests
    except ImportError:
        print("    ⚠️  curl-cffi ไม่ได้ติดตั้ง — รัน: pip install curl-cffi")
        return []

    urls_to_try = get_area_urls(area)
    if page_num > 1:
        urls_to_try = [u + (f"&page={page_num}" if "?" in u else f"?page={page_num}") for u in urls_to_try]

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }

    for url in urls_to_try:
        try:
            resp = cffi_requests.get(
                url,
                headers=headers,
                impersonate="chrome124",   # ← key: Chrome 124 TLS fingerprint
                timeout=20,
                allow_redirects=True,
            )

            if resp.status_code == 404:
                print(f"    ↪ 404 {url[:70]}")
                continue

            if len(resp.text) < 500:
                print(f"    ↪ {resp.status_code} {len(resp.text)}B (too small) {url[:60]}")
                continue

            # ลอง parse ทุก format
            restaurants, fmt = parse_html_for_restaurants(resp.text, area)
            if restaurants:
                print(f"    ✅ [curl-cffi/{fmt}] {len(restaurants)} restaurants — {url[:60]}")
                return restaurants

            # ไม่เจอข้อมูล — บันทึก debug แล้วลอง URL ถัดไป
            debug_path = DEBUG_DIR / f"wongnai_{area}_cffi.html"
            debug_path.write_text(resp.text[:80000], encoding="utf-8")
            print(f"    ⚠️  {resp.status_code} {len(resp.text)}B ไม่มีข้อมูล — dump: {debug_path.name} — ลอง URL ถัดไป")

        except Exception as e:
            print(f"    ❌ {url[:60]}: {e}")

    return []


# ── Strategy 2: Playwright non-headless (เปิดหน้าต่างจริง) ──────────────────

async def try_playwright_visible(page, area: str, api_buffer: list) -> list:
    """
    Playwright แบบ non-headless — เปิดหน้าต่าง Chrome จริงๆ
    ลอง URL ใหม่หลายรูปแบบ (Wongnai เปลี่ยน URL structure แล้ว)
    """
    urls_to_try = get_area_urls(area)
    navigated = False
    for url in urls_to_try:
        try:
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            if resp and resp.status == 404:
                print(f"    ↪ 404 {url[:60]}")
                continue
            navigated = True
            print(f"    ↪ {resp.status if resp else '?'} {url[:60]}")
            break
        except Exception as e:
            print(f"    ↪ error {url[:60]}: {str(e)[:60]}")

    if not navigated:
        return []

    # รอให้ JS render เสร็จ
    await asyncio.sleep(5)
    # Scroll เพื่อ trigger lazy load
    try:
        await page.evaluate("window.scrollTo(0, 600)")
        await asyncio.sleep(2)
    except Exception as e:
        print(f"    ⚠️  scroll error: {e}")

    results = []

    # ดึง HTML จาก page (หลัง JS render)
    html = ""
    try:
        html = await page.content()
    except Exception as e:
        print(f"    ⚠️  get content error: {e}")
        return []

    # ลอง parse ทุก format (schema.org + __NEXT_DATA__)
    results, fmt = parse_html_for_restaurants(html, area)
    if results:
        print(f"    ✅ [Playwright/{fmt}] {len(results)} restaurants")
        return results

    # API buffer ที่ดักได้ระหว่าง navigate
    if api_buffer:
        results = api_buffer[:]
        print(f"    ✅ [API intercept] {len(results)} restaurants")
        return results

    # Debug dump ถ้ายังว่าง
    debug_path = DEBUG_DIR / f"wongnai_{area}_v5.html"
    debug_path.write_text(html, encoding="utf-8")
    print(f"    ❌ 0 restaurants — dump: {debug_path.name} ({len(html)} bytes)")
    return []


# ── Main ───────────────────────────────────────────────────────────────────────

async def run(areas: list = None, max_pages: int = None, headless: bool = False):
    """
    headless=False (default) — เปิดหน้าต่าง browser จริง ผ่าน bot detection ได้ดีกว่า
    headless=True            — ไม่เปิดหน้าต่าง (เร็วกว่า แต่อาจถูก block)
    """
    areas     = areas or BANGKOK_AREAS
    max_pages = max_pages or MAX_PAGES_PER_RUN
    init_db()
    total = 0

    # ── Strategy 1: curl-cffi ─────────────────────────────────────────────
    print("\n  🔍 Strategy 1: curl-cffi (Chrome TLS impersonation)")
    cffi_results = {}
    for area in areas:
        print(f"  [{area}] ", end="", flush=True)
        r = try_curl_cffi_strategy(area)
        cffi_results[area] = r
        print(f"{len(r)} restaurants")

    all_cffi_ok = all(len(v) > 0 for v in cffi_results.values())
    if all_cffi_ok:
        print("\n  ✅ curl-cffi strategy ได้ผลทุก area!")
        for area, restaurants in cffi_results.items():
            for r in restaurants:
                rid = upsert_restaurant(r)
                record_snapshot(rid, review_count=r["_review_count"],
                                rating=r["_rating"], rating_count=r["_review_count"])
            total += len(restaurants)
            print(f"  ✅ {area}: saved {len(restaurants)} restaurants")
        print(f"\n🎉 Wongnai scrape done — {total} restaurants saved")
        return

    # ── Strategy 2: Playwright (non-headless by default) ─────────────────
    print(f"\n  🔍 Strategy 2: Playwright ({'headless' if headless else 'visible — เปิดหน้าต่าง Chrome'})")
    if not headless:
        print("  ℹ️  จะเปิดหน้าต่าง Chrome ขึ้นมา — ปกติ เป็นการ bypass bot detection")

    from playwright.async_api import async_playwright, TimeoutError as PWTimeout

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                "--lang=th-TH,th",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--window-size=1280,900",
                "--start-maximized",
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
            java_script_enabled=True,
        )
        page = await context.new_page()

        # Apply stealth (playwright-stealth ถ้ามี)
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['th-TH','th','en-US','en']});
            window.chrome = {runtime: {}};
        """)
        try:
            from playwright_stealth import stealth_async
            await stealth_async(page)
            print("  🥷 playwright-stealth applied")
        except ImportError:
            print("  🥷 basic stealth applied (pip install playwright-stealth สำหรับ full stealth)")

        # ดัก API calls
        api_buffer = []

        async def on_response(resp):
            ct = resp.headers.get("content-type", "")
            u  = resp.url
            if "json" not in ct:
                return
            if not any(kw in u for kw in WONGNAI_API_PATTERNS):
                return
            try:
                body = await resp.json()
                items = parse_json_for_restaurants(body, "api")
                if items:
                    api_buffer.extend(items)
                    print(f"    📡 {u[:70]} → {len(items)} restaurants")
            except Exception:
                pass

        page.on("response", on_response)

        for area in areas:
            print(f"\n  🗺️  Wongnai area: {area}")
            api_buffer.clear()

            if cffi_results.get(area):
                restaurants = cffi_results[area]
                print(f"    ✅ [curl-cffi cache] {len(restaurants)} restaurants")
            else:
                restaurants = await try_playwright_visible(page, area, api_buffer)
                for r in restaurants:
                    r["area"] = area

            for r in restaurants:
                rid = upsert_restaurant(r)
                record_snapshot(rid, review_count=r["_review_count"],
                                rating=r["_rating"], rating_count=r["_review_count"])
            total += len(restaurants)
            print(f"  ✅ {area}: saved {len(restaurants)} restaurants")
            await asyncio.sleep(DELAY_BETWEEN_PAGES)

        await browser.close()

    print(f"\n🎉 Wongnai scrape done — {total} restaurants saved")
    if total == 0:
        print("""
  ⚠️  ยังได้ 0 ทุก strategy — ให้ลอง:

  1. ติดตั้ง curl-cffi:
       pip install curl-cffi
     แล้วรันใหม่ → นี่น่าจะแก้ปัญหา Cloudflare TLS blocking ได้

  2. ถ้ายังไม่ได้ → ติดตั้ง playwright-stealth:
       pip install playwright-stealth
     แล้วรันใหม่ (script จะเปิด Chrome window ให้เห็น)

  3. ถ้ายังไม่ได้ → ดู HTML dump ใน scraper/debug_output/
     เพื่อดูว่า Wongnai แสดง error อะไร
        """)


if __name__ == "__main__":
    # Parse args: python scrape_wongnai_v5.py [area1 area2 ...] [--headless]
    args = sys.argv[1:]
    headless = "--headless" in args
    areas = [a for a in args if not a.startswith("--")] or None
    asyncio.run(run(areas=areas, headless=headless))
