"""
ChefMinistry — Scraper Config
แก้ไข PATH และค่าต่างๆ ที่นี่ก่อนรัน
"""
import pathlib, os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = pathlib.Path(__file__).parent
DB_PATH     = BASE_DIR / "chefministry_data.db"
EXPORT_DIR  = BASE_DIR.parent / "site" / "js"   # จะ update data.js ที่นี่
EXPORT_JSON = BASE_DIR / "export_restaurants.json"

# ── Scraper settings ──────────────────────────────────────────────────────────
DELAY_BETWEEN_PAGES = 2.5   # วินาที — อย่าลดต่ำกว่า 2 เพื่อไม่ให้ถูก block
MAX_PAGES_PER_RUN   = 5     # จำนวนหน้าสูงสุดต่อการรันครั้งนึง
HEADLESS            = True  # False = เปิด browser ให้เห็น (ใช้ debug)

# ── Bangkok areas to scrape ───────────────────────────────────────────────────
BANGKOK_AREAS = [
    "thonglor",
    "ekkamai",
    "silom",
    "sathorn",
    "ari",
    "ratchada",
    "sukhumvit",
    "onnut",
    "ladprao",
    "rama9",
]

# ── Cuisine types to track ────────────────────────────────────────────────────
CUISINE_MAP = {
    "อาหารไทย": "thai",
    "ญี่ปุ่น": "japanese",
    "โอมากาเสะ": "omakase",
    "อิตาเลียน": "italian",
    "ราเมน": "ramen",
    "สเต็ก": "steakhouse",
    "ซีฟู้ด": "seafood",
    "คาเฟ่": "cafe",
    "ฟาสต์ฟู้ด": "casual",
    "สตรีทฟู้ด": "street-food",
}
