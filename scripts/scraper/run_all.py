"""
ChefMinistry — Master Runner
รันทุกอย่างในคลิกเดียว

วิธีใช้:
    python run_all.py              # รัน scraper ทั้งหมด + export
    python run_all.py --setup      # ติดตั้ง dependencies
    python run_all.py --wongnai    # รัน Wongnai เท่านั้น
    python run_all.py --grabfood   # รัน GrabFood เท่านั้น
    python run_all.py --lineman    # รัน LINE MAN เท่านั้น
    python run_all.py --export     # export signal เท่านั้น (ไม่ scrape)
    python run_all.py --inject     # export + inject เข้า data.js
    python run_all.py --summary    # แสดง DB summary

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Setup ครั้งแรก (รันแค่ทีเดียว):
    python run_all.py --setup

แล้วตั้ง cron / Task Scheduler รันทุกวัน:
    0 9 * * * cd /path/to/scraper && python run_all.py >> logs/daily.log 2>&1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import asyncio, argparse, subprocess, sys
from datetime import datetime
from db import init_db
from export_signals import show_summary, export_json, inject_into_datajs

BANNER = """
╔═══════════════════════════════════════════════╗
║     ChefMinistry — Data Intelligence Runner   ║
║     Restaurant Signal Scraper v1.0            ║
╚═══════════════════════════════════════════════╝
"""


def setup():
    """ติดตั้ง dependencies + Playwright browser"""
    print("📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    # ติดตั้ง playwright-stealth แยก (bypass bot detection)
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright-stealth"], check=False)
    print("🌐 Installing Playwright Chromium...")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    init_db()
    print("\n✅ Setup complete! รัน: python run_all.py")


async def run_scrapers(wongnai: bool = True, grabfood: bool = True, lineman: bool = True):
    """รัน scrapers ตามที่เลือก"""
    if wongnai:
        print("\n" + "─"*50)
        print("  🍜 Wongnai Scraper")
        print("─"*50)
        from scrape_wongnai import run as run_wongnai
        await run_wongnai()

    if grabfood:
        print("\n" + "─"*50)
        print("  🚗 GrabFood Scraper")
        print("─"*50)
        from scrape_grabfood import run as run_grabfood
        await run_grabfood()

    if lineman:
        print("\n" + "─"*50)
        print("  🟢 LINE MAN Scraper")
        print("─"*50)
        from scrape_lineman import run as run_lineman
        await run_lineman()


async def main():
    parser = argparse.ArgumentParser(description="ChefMinistry Data Runner")
    parser.add_argument("--setup",    action="store_true", help="Install dependencies")
    parser.add_argument("--wongnai",  action="store_true", help="Run Wongnai only")
    parser.add_argument("--grabfood", action="store_true", help="Run GrabFood only")
    parser.add_argument("--lineman",  action="store_true", help="Run LINE MAN only")
    parser.add_argument("--export",   action="store_true", help="Export without scraping")
    parser.add_argument("--inject",   action="store_true", help="Export + inject to data.js")
    parser.add_argument("--summary",  action="store_true", help="Show DB summary")
    parser.add_argument("--days",     type=int, default=30, help="Velocity window days")
    args = parser.parse_args()

    print(BANNER)
    print(f"  🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.setup:
        setup()
        return

    if args.summary:
        show_summary(days=args.days)
        return

    init_db()

    # Decide what to run
    any_specific = args.wongnai or args.grabfood or args.lineman
    run_w = args.wongnai or (not any_specific and not args.export and not args.inject)
    run_g = args.grabfood or (not any_specific and not args.export and not args.inject)
    run_l = args.lineman or (not any_specific and not args.export and not args.inject)

    if not args.export and not args.inject:
        await run_scrapers(wongnai=run_w, grabfood=run_g, lineman=run_l)

    # Export
    print("\n" + "─"*50)
    print("  📊 Exporting Signal Data")
    print("─"*50)
    show_summary(days=args.days)
    restaurants = export_json(days=args.days)

    if args.inject and restaurants:
        inject_into_datajs(restaurants)
        print("\n  ➡️  ต่อไปรัน push_to_github.py เพื่อ update live site")

    print("\n" + "═"*50)
    print(f"  ✅ Done — {datetime.now().strftime('%H:%M:%S')}")
    print("═"*50)


if __name__ == "__main__":
    asyncio.run(main())
