"""
ChefMinistry — Wongnai Scraper v4
ปัญหาที่แก้: Wongnai detect headless browser → ส่ง empty HTML กลับมา

Solution stack (ลำดับ):
  1. requests + SSR  — ลอง GET ธรรมดาก่อน ถ้า Wongnai ใช้ SSR จะได้ HTML + __NEXT_DATA__
  2. Playwright stealth — ใช้ playwright-stealth ซ่อน automation fingerprint
  3. Network interception — ดัก XHR/fetch API calls ระหว่าง page load
  4. HTML link fallback — เก็บ URL ร้านจาก <a> tags

ติดตั้ง: pip install playwright-stealth
"""
import asyncio, re, json, pathlib
import requests as req_lib
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from db import init_db, upsert_restaurant, record_snapshot
from config import BANGKOK_AREAS, DELAY_BETWEEN_PAGES, MAX_PAGES_PER_RUN, HEADLESS, CUISINE_MAP

BASE_URL  = "https://www.wongnai.com"
DEBUG_DIR = pathlib.Path(__file__).parent / "debug_output"

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "th-TH,th;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

WONGNAI_API_PATTERNS = [
    "api.wongnai.com",
    "wongnai.com/api",
    "/graphql",
    "/restaurants/search",
    "/v1/restaurants", "/v2/restaurants",
    "wongnai.com/_next/data",
    "_next/data",
]


# ── Helpers ────────────────────────────────────────────────────────────────────

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


def item_to_restaurant(item: dict, area: str) -> dict | None:
    """แปลง Wongnai API/Next item → restaurant dict"""
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
    """Recursive: หา list ที่มี restaurant dicts"""
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
    """แกะ JSON ใดๆ หา restaurant list"""
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


# ── Strategy 1: plain requests (ไม่ใช้ browser) ──────────────────────────────

def try_requests_strategy(area: str, page_num: int = 1) -> list:
    """
    ลอง GET ธรรมดา — ถ้า Wongnai ทำ SSR จะได้ __NEXT_DATA__ ใน HTML
    ถ้า detect bot จะได้ empty HTML (39 bytes)
    """
    url = f"{BASE_URL}/restaurants/bangkok/{area}"
    if page_num > 1:
        url += f"?page={page_num}"
    try:
        resp = req_lib.get(url, headers=REQUEST_HEADERS, timeout=15)
        if len(resp.text) < 500:
            return []   # empty → bot detected

        # หา __NEXT_DATA__
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', resp.text, re.DOTALL)
        if not m:
            return []
        data = json.loads(m.group(1))
        restaurants = parse_json_for_restaurants(data, area)
        if restaurants:
            print(f"    ✅ [requests/__NEXT_DATA__] {len(restaurants)} restaurants")
        return restaurants
    except Exception as e:
        return []


# ── Strategy 2: Playwright + stealth ─────────────────────────────────────────

async def apply_stealth(page):
    """
    Manual stealth — ซ่อน automation fingerprints
    (ใช้แทน playwright-stealth ในกรณีที่ install ไม่ได้)
    """
    await page.add_init_script("""
        // ซ่อน webdriver flag
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        // แก้ plugins (bot มักมี 0 plugins)
        Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
        // แก้ languages
        Object.defineProperty(navigator, 'languages', {get: () => ['th-TH','th','en-US','en']});
        // ซ่อน automation properties
        window.chrome = {runtime: {}};
        // แก้ permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) =>
            parameters.name === 'notifications'
                ? Promise.resolve({ state: Notification.permission })
                : originalQuery(parameters);
    """)

    # ลอง import playwright-stealth ถ้ามี
    try:
        from playwright_stealth import stealth_async
        await stealth_async(page)
        print("    🥷 playwright-stealth applied")
    except ImportError:
        print("    🥷 manual stealth applied (pip install playwright-stealth สำหรับ full stealth)")


async def try_playwright_strategy(page, area: str, api_buffer: list) -> list:
    """Playwright + stealth + networkidle"""
    url = f"{BASE_URL}/restaurants/bangkok/{area}"
    try:
        await page.goto(url, wait_until="networkidle", timeout=45_000)
        await asyncio.sleep(4)
    except PWTimeout:
        print(f"    ⚠️  Playwright timeout — รอ networkidle นานเกิน")
        try:
            await page.wait_for_load_state("load", timeout=10_000)
        except:
            pass

    # ลอง __NEXT_DATA__ ก่อน
    results = []
    try:
        raw = await page.evaluate("""
            () => {
                const el = document.getElementById('__NEXT_DATA__');
                return el ? el.textContent : null;
            }
        """)
        if raw and len(raw) > 100:
            data = json.loads(raw)
            results = parse_json_for_restaurants(data, area)
            if results:
                print(f"    ✅ [Playwright/__NEXT_DATA__] {len(results)} restaurants")
    except Exception:
        pass

    # ถ้า __NEXT_DATA__ ว่าง ลอง API buffer (intercepted ระหว่าง navigate)
    if not results and api_buffer:
        results = api_buffer[:]
        print(f"    ✅ [API intercept] {len(results)} restaurants")

    # HTML link fallback
    if not results:
        hrefs = await page.eval_on_selector_all(
            "a",
            """els => els
                .map(e => ({href: e.href, text: e.innerText.trim().substring(0, 80)}))
                .filter(e => /wongnai\\.com\\/restaurants\\/[\\w-]+\\/[\\w-]+-\\d+/.test(e.href))
            """
        )
        seen = set()
        for item in hrefs:
            href = item.get("href", "")
            if not href or href in seen:
                continue
            seen.add(href)
            id_m = re.search(r"-(\d+)/?$", href)
            ext_id = id_m.group(1) if id_m else href[-20:]
            name = item.get("text", "").split("\n")[0].strip() or f"Restaurant {ext_id}"
            results.append({
                "source": "wongnai", "external_id": ext_id, "name": name,
                "name_en": "", "cuisine": detect_cuisine(name), "area": area,
                "price_range": 2, "url": href, "image_url": "",
                "_review_count": 0, "_rating": 0.0,
            })
        if results:
            print(f"    ✅ [HTML links] {len(results)} restaurant URLs")

    # Save debug HTML ถ้ายังได้ 0
    if not results:
        DEBUG_DIR.mkdir(exist_ok=True)
        html = await page.content()
        debug_path = DEBUG_DIR / f"wongnai_{area}_v4.html"
        debug_path.write_text(html, encoding="utf-8")
        print(f"    ❌ 0 restaurants — HTML dump: {debug_path} ({len(html)} bytes)")

    return results


# ── Main ───────────────────────────────────────────────────────────────────────

async def run(areas: list = None, max_pages: int = None):
    areas     = areas or BANGKOK_AREAS
    max_pages = max_pages or MAX_PAGES_PER_RUN
    init_db()
    total = 0

    # ── ลอง requests strategy ก่อน (เร็วกว่า, ไม่ต้องใช้ browser) ───────
    print("\n  🔍 Strategy 1: plain requests (ไม่ต้อง browser)")
    requests_results = {}
    for area in areas:
        print(f"  [{area}] ", end="", flush=True)
        r = try_requests_strategy(area)
        requests_results[area] = r
        print(f"{len(r)} restaurants")

    all_requests_ok = all(len(v) > 0 for v in requests_results.values())
    if all_requests_ok:
        print("\n  ✅ requests strategy ได้ผลทุก area — ไม่ต้องใช้ Playwright")
        for area, restaurants in requests_results.items():
            for r in restaurants:
                rid = upsert_restaurant(r)
                record_snapshot(rid, review_count=r["_review_count"],
                                rating=r["_rating"], rating_count=r["_review_count"])
            total += len(restaurants)
            print(f"  ✅ {area}: saved {len(restaurants)} restaurants")
        print(f"\n🎉 Wongnai scrape done — {total} restaurants saved")
        return

    # ── ถ้า requests ไม่ได้ → ใช้ Playwright + stealth ──────────────────
    print("\n  🔍 Strategy 2: Playwright + stealth")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=[
                "--lang=th-TH,th",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--window-size=1280,900",
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
        await apply_stealth(page)

        # ── ดัก API calls ──────────────────────────────────────────────
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

            # ใช้ requests result ถ้ามีแล้ว
            if requests_results.get(area):
                restaurants = requests_results[area]
                print(f"    ✅ [requests cache] {len(restaurants)} restaurants")
            else:
                restaurants = await try_playwright_strategy(page, area, api_buffer)
                # backfill area ถ้ามาจาก API buffer
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
        print(f"\n  ⚠️  ยังได้ 0 ทุก strategy")
        print(f"  1. รัน: pip install playwright-stealth แล้วลองใหม่")
        print(f"  2. ลอง: python scrape_wongnai.py แบบ HEADLESS=False ใน config.py")
        print(f"     เพื่อดู browser จริงว่า block ยังไง")
        print(f"  3. ดู HTML dump ใน scraper/debug_output/")


if __name__ == "__main__":
    import sys
    areas = sys.argv[1:] if len(sys.argv) > 1 else None
    asyncio.run(run(areas=areas))
