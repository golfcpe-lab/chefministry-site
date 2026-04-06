"""
ChefMinistry — Master Runner

วิธีใช้:
    python run_all.py              # รัน Wongnai → Google Maps → export (ทุกอย่าง)
    python run_all.py --setup      # ติดตั้ง dependencies ครั้งแรก
    python run_all.py --wongnai    # รัน Wongnai เท่านั้น
    python run_all.py --gmaps      # รัน Google Maps เท่านั้น
    python run_all.py --export     # export signal เท่านั้น (ไม่ scrape)
    python run_all.py --summary    # แสดง DB summary

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Setup ครั้งแรก (รันแค่ทีเดียว):
    python run_all.py --setup

ตั้ง Task Scheduler รันทุกวัน:
    python run_all.py >> logs/daily.log 2>&1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import asyncio, argparse, subprocess, sys, pathlib
from datetime import datetime
from db import init_db

BANNER = """
╔═══════════════════════════════════════════════╗
║     ChefMinistry — Data Intelligence Runner   ║
║     Wongnai + Google Maps  v2.0               ║
╚═══════════════════════════════════════════════╝
"""


def setup():
    """ติดตั้ง dependencies"""
    print("📦 Installing dependencies...")
    req = pathlib.Path(__file__).parent / "requirements.txt"
    if req.exists():
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req)], check=True)
    print("🔒 Installing curl-cffi...")
    subprocess.run([sys.executable, "-m", "pip", "install", "curl-cffi"], check=False)
    print("🌐 Installing Playwright Chromium...")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)
    init_db()
    print("\n✅ Setup complete!")
    print("   ต่อไป: ใส่ GOOGLE_MAPS_API_KEY ใน config.py แล้วรัน python run_all.py")


def section(title: str):
    print("\n" + "─" * 52)
    print(f"  {title}")
    print("─" * 52)


async def run_scrapers(wongnai: bool = True, gmaps: bool = True, days: int = 30):
    # ── 1. Wongnai ─────────────────────────────────────────
    if wongnai:
        section("🍜  Wongnai Scraper")
        from scrape_wongnai_v5 import run as run_wongnai
        await run_wongnai()

    # ── 2. Google Maps — enrich ร้านที่ได้จาก Wongnai ──────
    if gmaps:
        section("🗺️  Google Maps Places API")
        from scrape_gmaps import run as run_gmaps
        run_gmaps()   # sync function


async def main():
    parser = argparse.ArgumentParser(description="ChefMinistry Data Runner")
    parser.add_argument("--setup",   action="store_true", help="Install dependencies")
    parser.add_argument("--wongnai", action="store_true", help="Run Wongnai only")
    parser.add_argument("--gmaps",   action="store_true", help="Run Google Maps only")
    parser.add_argument("--export",  action="store_true", help="Export without scraping")
    parser.add_argument("--summary", action="store_true", help="Show DB summary")
    parser.add_argument("--gsheets", action="store_true", help="Export to Google Sheets after run")
    parser.add_argument("--days",    type=int, default=30, help="Velocity window (days)")
    args = parser.parse_args()

    print(BANNER)
    print(f"  🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.setup:
        setup()
        return

    init_db()

    if args.summary:
        from export_signals import show_summary
        show_summary(days=args.days)
        return

    # ── Decide what to run ──────────────────────────────────
    any_specific = args.wongnai or args.gmaps
    run_w = args.wongnai or (not any_specific and not args.export)
    run_g = args.gmaps   or (not any_specific and not args.export)

    if not args.export:
        await run_scrapers(wongnai=run_w, gmaps=run_g, days=args.days)

    # ── Export + inject ─────────────────────────────────────
    section("📊  Exporting Signal Data")
    try:
        from export_signals import show_summary, export_json, inject_into_datajs
        show_summary(days=args.days)
        restaurants = export_json(days=args.days)
        inject_into_datajs(restaurants)
    except Exception as e:
        print(f"  ⚠️  export error: {e}")

    # ── Export to Google Sheets ─────────────────────────────
    if args.gsheets:
        section("📊  Google Sheets Export")
        try:
            from export_gsheets import run as run_gsheets
            run_gsheets(days=args.days)
        except Exception as e:
            print(f"  ⚠️  Google Sheets error: {e}")

    # ── Push to GitHub ──────────────────────────────────────
    push_script = pathlib.Path(__file__).parent.parent / "push_to_github.py"
    if push_script.exists():
        section("🚀  Pushing to GitHub")
        result = subprocess.run([sys.executable, str(push_script)])
        if result.returncode != 0:
            print("  ⚠️  Push มีปัญหา — ลองรัน push_to_github.py เอง")

    print("\n" + "═" * 52)
    print(f"  ✅ Done — {datetime.now().strftime('%H:%M:%S')}")
    print("═" * 52)


if __name__ == "__main__":
    asyncio.run(main())
