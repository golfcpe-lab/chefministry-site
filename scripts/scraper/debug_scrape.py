"""
ChefMinistry — Debug Tool
รันเพื่อดูว่า scraper เห็นอะไรบน Wongnai / GrabFood จริงๆ
บันทึก HTML dump + network log ไว้ใน debug_output/

รัน: python debug_scrape.py wongnai
     python debug_scrape.py grabfood
"""
import asyncio, json, sys, pathlib, re
from playwright.async_api import async_playwright

OUT_DIR = pathlib.Path(__file__).parent / "debug_output"
OUT_DIR.mkdir(exist_ok=True)

HEADLESS = False   # เปิด browser ให้เห็น

async def debug_wongnai():
    area = "thonglor"
    url  = f"https://www.wongnai.com/restaurants/bangkok/{area}"
    print(f"\n[Wongnai DEBUG] {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        ctx = await browser.new_context(
            locale="th-TH",
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await ctx.new_page()

        # ── ดัก ALL network requests ─────────────────────────────────────
        net_log = []
        def on_request(req):
            net_log.append({"type": "request", "url": req.url, "method": req.method})

        api_hits = []
        async def on_response(resp):
            ct = resp.headers.get("content-type", "")
            entry = {"url": resp.url, "status": resp.status, "ct": ct}
            if "json" in ct:
                try:
                    body = await resp.json()
                    entry["keys"] = list(body.keys()) if isinstance(body, dict) else f"list[{len(body)}]"
                    api_hits.append(entry)
                except:
                    pass
            net_log.append(entry)

        page.on("request",  on_request)
        page.on("response", on_response)

        print("  Navigating...")
        await page.goto(url, wait_until="networkidle", timeout=45_000)
        await asyncio.sleep(3)

        # Scroll ลงเพื่อ trigger lazy load
        await page.evaluate("window.scrollTo(0, 500)")
        await asyncio.sleep(2)
        await page.evaluate("window.scrollTo(0, 1200)")
        await asyncio.sleep(2)

        # ── ลองทุก selector ที่อาจใช้ได้ ────────────────────────────────
        selectors = [
            "a[href*='/restaurants/bangkok']",
            "a[href*='/restaurants/thonglor']",
            "[data-testid='restaurant-card']",
            "[data-testid*='restaurant']",
            "[class*='RestaurantCard']",
            "[class*='restaurant-card']",
            "[class*='restaurant-item']",
            "[class*='RestaurantItem']",
            "[class*='restaurantCard']",
            "li[class*='restaurant']",
            "article",
        ]
        print("\n  Selector results:")
        for sel in selectors:
            els = await page.query_selector_all(sel)
            if els:
                print(f"    ✅ '{sel}' → {len(els)} elements")
                # เอา text ของตัวแรก
                try:
                    txt = (await els[0].inner_text())[:80].replace("\n"," ")
                    href = await els[0].get_attribute("href")
                    print(f"       first: {txt!r} | href={href}")
                except:
                    pass
            else:
                print(f"    ❌ '{sel}' → 0")

        # ── บันทึก HTML ──────────────────────────────────────────────────
        html = await page.content()
        html_path = OUT_DIR / "wongnai_page.html"
        html_path.write_text(html, encoding="utf-8")
        print(f"\n  HTML saved → {html_path} ({len(html):,} chars)")

        # ── บันทึก API log ───────────────────────────────────────────────
        api_path = OUT_DIR / "wongnai_api.json"
        api_path.write_text(json.dumps(api_hits, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  API hits saved → {api_path} ({len(api_hits)} JSON endpoints)")

        if api_hits:
            print("\n  JSON API endpoints found:")
            for h in api_hits[:15]:
                print(f"    {h['status']} {h['url'][:100]} → keys={h.get('keys')}")

        # ── ดู <a> tags ทั้งหมดที่มี /restaurants/ ──────────────────────
        hrefs = await page.eval_on_selector_all(
            "a[href*='/restaurants/']",
            "els => els.map(e => e.href).slice(0, 20)"
        )
        if hrefs:
            print(f"\n  Found {len(hrefs)} /restaurants/ links (first 20):")
            for h in hrefs:
                print(f"    {h}")

        await browser.close()
    print("\n  Done. ดู debug_output/ สำหรับไฟล์ dump")


async def debug_grabfood():
    lat, lng = 13.7280, 100.5849  # thonglor
    url = f"https://food.grab.com/th/en/restaurants?lat={lat}&lng={lng}"
    print(f"\n[GrabFood DEBUG] {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        ctx = await browser.new_context(
            locale="th-TH",
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await ctx.new_page()

        api_hits = []
        async def on_response(resp):
            ct = resp.headers.get("content-type", "")
            u  = resp.url
            if "json" in ct and "grab.com" in u:
                try:
                    body = await resp.json()
                    keys = list(body.keys()) if isinstance(body, dict) else f"list[{len(body)}]"
                    api_hits.append({"url": u, "status": resp.status, "keys": keys})
                except:
                    pass

        page.on("response", on_response)

        print("  Navigating (นานหน่อย — รอ cookies/location)...")
        await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
        await asyncio.sleep(5)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        await asyncio.sleep(3)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(3)

        print(f"\n  Intercepted {len(api_hits)} JSON API responses:")
        for h in api_hits[:20]:
            print(f"    {h['status']} {h['url'][:100]}")
            print(f"       keys: {h['keys']}")

        # บันทึก API log
        api_path = OUT_DIR / "grabfood_api.json"
        api_path.write_text(json.dumps(api_hits, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n  API log saved → {api_path}")

        # บันทึก HTML
        html = await page.content()
        html_path = OUT_DIR / "grabfood_page.html"
        html_path.write_text(html, encoding="utf-8")
        print(f"  HTML saved → {html_path}")

        # ลอง selectors
        selectors = [
            "[data-testid='restaurant-card']",
            "[class*='RestaurantCard']",
            "[class*='restaurantCard']",
            "[class*='merchant']",
            "[data-testid*='merchant']",
            "a[href*='/restaurant/']",
        ]
        print("\n  Selector results:")
        for sel in selectors:
            els = await page.query_selector_all(sel)
            print(f"    {'✅' if els else '❌'} '{sel}' → {len(els)}")

        await browser.close()
    print("\n  Done. ดู debug_output/ สำหรับไฟล์ dump")


if __name__ == "__main__":
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "wongnai"
    if target == "grabfood":
        asyncio.run(debug_grabfood())
    else:
        asyncio.run(debug_wongnai())
