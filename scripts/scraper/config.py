"""
ChefMinistry — Scraper Config
แก้ไข PATH และค่าต่างๆ ที่นี่ก่อนรัน
"""
import pathlib, os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = pathlib.Path(__file__).parent
DB_PATH     = BASE_DIR / "chefministry_data.db"
EXPORT_DIR  = pathlib.Path(os.environ.get("EXPORT_DIR", str(BASE_DIR.parent / "site" / "js")))
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

# ── Google Maps Places API ───────────────────────────────────────────────────
# ขอ key ได้ที่ https://console.cloud.google.com/
#   1. New Project → Enable "Places API (New)"
#   2. Credentials → Create API Key
#   3. ใส่ key ด้านล่างนี้
# ⚠️  อย่าใส่ key ตรงนี้โดยตรง — repo นี้เป็น public จะ exposed!
# วิธีตั้งค่า local: สร้างไฟล์ .env ใน Chef IP folder แล้วเพิ่ม:
#   GOOGLE_MAPS_API_KEY=AIzaSy...
# วิธีตั้งค่า GitHub Actions: Settings → Secrets → GOOGLE_MAPS_API_KEY
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")

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
