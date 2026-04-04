"""
ChefMinistry — Wongnai Scraper (Playwright)
ดึงข้อมูลร้านและ review count จาก wongnai.com

ข้อมูลที่ได้:
- ชื่อร้าน (ไทย/อังกฤษ)
- ประเภทอาหาร, ย่าน
- Rating + จำนวน review
- ราคาโดยประมาณ
- URL ร้าน

รัน: python scrape_wongnai.py
"""
import asyncio, re, time, json
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from db import init_db, upsert_restaurant, record_snapshot
from config import BANGKOK_AREAS, DELAY_BETWEEN_PAGES, MAX_PAGES_PER_RUN, HEADLESS, CUISINE_MAP

BASE_URL = "https://www.wongnai.com"

# ── Cuisine detection จาก Thai text ─────────────────────────────────────────
def detect_cuisine(text: str) -> str:
    t = text.lower()
    for th, en in CUISINE_MAP.items():
        if th in text:
            return en
    if "ราเมน" in text or "ramen" in t:   return "ramen"
    if "โอมากาเสะ" in text or "omakase" in t: return "omakase"
    if "สเต็ก" in text or "steak" in t:   return "steakhouse"
    if "ญี่ปุ่น" in text or "japanese" in t: return "japanese"
    if "อาหารไทย" in text or "thai" in t:  return "thai"
    if "คาเฟ่" in text or "cafe" in t:     return "cafe"
    return "other"


def parse_price_range(text: str) -> int:
    """แปลง ฿, ฿฿, ฿฿฿ → 1,2,3"""
    count = text.count("฿")
    return max(1, min(4, count)) if count else 2


def clean_int(s: str) -> int:
    """'1,234 รีวิว' → 1234"""
    nums = re.sub(r"[^\d]", "", s or "")
    return int(nums) if nums else 0


async def scrape_area(page, area: str, max_pages: int) -> list:
    """ดึงร้านจาก 1 area บน Wongnai"""
    results = []
    url = f"{BASE_URL}/restaurants/bangkok/{area}"
    print(f"\n  🗺️  Area: {area} — {url}")

    for page_num in range(1, max_pages + 1):
        current_url = f"{url}?page={page_num}" if page_num > 1 else url
        try:
            await page.goto(current_url, wait_until="networkidle", timeout=30_000)
            await asyncio.sleep(1.5)
        except PWTimeout:
            print(f"    ⚠️  Timeout page {page_num}, skip")
            break

        # ── ดึงการ์ดร้านทั้งหมดในหน้า ────────────────────────────────────────
        cards = await page.query_selector_all(
            "a[href*='/restaurants/'], div[data-testid='restaurant-card']"
        )
        if not cards:
            # ลองหา selector แบบ fallback
            cards = await page.query_selector_all(".restaurant-card, [class*='RestaurantCard']")

        if not cards:
            print(f"    ⚠️  No cards found on page {page_num} (site structure may have changed)")
            break

        page_count = 0
        for card in cards:
            try:
                data = await extract_card_data(card, area)
                if data:
                    results.append(data)
                    page_count += 1
            except Exception as e:
                pass  # skip broken cards

        print(f"    Page {page_num}: {page_count} restaurants")

        # Check ถ้าไม่มีหน้าถัดไป
        next_btn = await page.query_selector("a[aria-label='Next page'], [class*='pagination'] a:last-child")
        if not next_btn or page_num >= max_pages:
            break
        await asyncio.sleep(DELAY_BETWEEN_PAGES)

    return results


async def extract_card_data(card, area: str) -> dict | None:
    """ดึงข้อมูลจาก restaurant card element"""
    # ── ชื่อร้าน ──
    name_el = await card.query_selector("h3, h2, [class*='name'], [class*='title']")
    name = (await name_el.inner_text()).strip() if name_el else None
    if not name or len(name) < 2:
        return None

    # ── URL ──
    href = await card.get_attribute("href") or ""
    if not href.startswith("http"):
        href = BASE_URL + href
    # ดึง external_id จาก URL: /restaurants/bangkok/xxxx-12345
    id_match = re.search(r"-(\d+)/?$", href)
    external_id = id_match.group(1) if id_match else re.sub(r"[^a-z0-9]", "_", name.lower())[:30]

    # ── Rating ──
    rating_el = await card.query_selector("[class*='rating'], [class*='score']")
    rating_text = (await rating_el.inner_text()).strip() if rating_el else "0"
    rating = float(re.search(r"[\d.]+", rating_text).group()) if re.search(r"[\d.]+", rating_text) else 0.0

    # ── Review count ──
    review_el = await card.query_selector("[class*='review'], [class*='count']")
    review_text = (await review_el.inner_text()).strip() if review_el else "0"
    review_count = clean_int(review_text)

    # ── Cuisine ──
    cuisine_el = await card.query_selector("[class*='cuisine'], [class*='category'], [class*='tag']")
    cuisine_text = (await cuisine_el.inner_text()).strip() if cuisine_el else ""
    cuisine = detect_cuisine(cuisine_text or name)

    # ── Price range ──
    price_el = await card.query_selector("[class*='price'], [class*='baht']")
    price_text = (await price_el.inner_text()).strip() if price_el else "฿฿"
    price_range = parse_price_range(price_text)

    # ── Image ──
    img_el = await card.query_selector("img")
    image_url = await img_el.get_attribute("src") if img_el else None

    return {
        "source":       "wongnai",
        "external_id":  external_id,
        "name":         name,
        "name_en":      None,
        "cuisine":      cuisine,
        "area":         area,
        "price_range":  price_range,
        "url":          href,
        "image_url":    image_url,
        "_review_count": review_count,
        "_rating":       rating,
    }


async def run(areas: list = None, max_pages: int = None):
    areas     = areas     or BANGKOK_AREAS
    max_pages = max_pages or MAX_PAGES_PER_RUN

    init_db()
    total = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=["--lang=th-TH,th"]
        )
        context = await browser.new_context(
            locale="th-TH",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for area in areas:
            restaurants = await scrape_area(page, area, max_pages)
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


if __name__ == "__main__":
    import sys
    areas = sys.argv[1:] if len(sys.argv) > 1 else None
    asyncio.run(run(areas=areas))
