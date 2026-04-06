"""
ChefMinistry — Signal Exporter
ดึงร้านที่ trending จาก database แล้วแปลงเป็น format ที่ใส่ใน data.js ได้

ใช้งาน:
    python export_signals.py             # export JSON ไปที่ export_restaurants.json
    python export_signals.py --inject    # inject เข้า data.js โดยตรง (ระวัง!)
    python export_signals.py --days 14   # ดู velocity 14 วัน แทน 30

Output:
    - export_restaurants.json  : ไฟล์ JSON พร้อมใช้
    - (optional) data.js update
"""
import json, argparse, re
from datetime import date
from db import get_trending_restaurants, get_all_restaurants, get_stats, get_conn
from config import EXPORT_JSON, EXPORT_DIR

# ── Signal strength mapping ───────────────────────────────────────────────────
def compute_signal_strength(new_reviews: int, velocity_pct: float, total_reviews: int) -> str:
    """
    คำนวณ signal strength จาก velocity data
    """
    if new_reviews >= 100 or velocity_pct >= 50:
        return "very-strong"
    if new_reviews >= 40 or velocity_pct >= 25:
        return "strong"
    if new_reviews >= 15 or velocity_pct >= 10:
        return "moderate"
    return "weak"


def trend_velocity_label(trend: str, velocity_pct: float) -> str:
    """แปลง trend + velocity เป็น badge text"""
    if trend == "rising":
        if velocity_pct >= 50:   return "↑↑ Viral"
        if velocity_pct >= 25:   return "↑ Rising Fast"
        return "↑ Rising"
    if trend == "declining":     return "↓ Declining"
    return "→ Stable"


def price_budget_label(price_range: int) -> str:
    return {1: "฿", 2: "฿฿", 3: "฿฿฿", 4: "฿฿฿฿"}.get(price_range, "฿฿")


def area_display(area: str) -> str:
    """canonical area name → display"""
    mapping = {
        "thonglor": "Thonglor", "ekkamai": "Ekkamai",
        "silom": "Silom", "sathorn": "Sathorn",
        "ari": "Ari", "ratchada": "Ratchada",
        "sukhumvit": "Sukhumvit", "onnut": "On Nut",
        "ladprao": "Lat Phrao", "rama9": "Rama 9",
    }
    return mapping.get(area, area.title())


def to_cm_format(row: dict, days: int = 30) -> dict | None:
    """แปลง DB row → ChefMinistry restaurant object"""
    name = row.get("name") or row.get("name_en") or ""
    if not name:
        return None

    new_reviews  = row.get("new_reviews") or 0
    velocity_pct = row.get("velocity_pct") or 0
    last_count   = row.get("last_count") or 0

    sig_strength = compute_signal_strength(new_reviews, velocity_pct, last_count)
    trend = "rising" if velocity_pct >= 5 else ("declining" if velocity_pct < -5 else "stable")
    trend_badge = trend_velocity_label(trend, velocity_pct)

    cuisine = row.get("cuisine") or "other"
    area    = row.get("area") or "bangkok"
    price   = row.get("price_range") or 2
    source  = row.get("source") or "wongnai"

    # ประเภทสถานที่: street food / bar / cafe ไม่นับเป็น "ร้านอาหาร" หลัก
    NON_RESTAURANT_TYPES = {"street-food", "cafe", "bar", "casual"}
    is_restaurant = cuisine not in NON_RESTAURANT_TYPES

    # Signal count: proxy จาก velocity_pct
    signal_count = max(1, int(new_reviews / 10)) if new_reviews else 1

    # overlap signal: ยังใช้ placeholder ตอนนี้
    # เมื่อมี creator data เข้ามาจะ cross-reference ได้
    overlap_signal = 1

    # cm_note: auto-generate
    if trend == "rising" and velocity_pct >= 25:
        cm_note = f"🔥 Review เพิ่ม +{int(velocity_pct)}% ใน {days} วัน — น่าจับตา"
    elif trend == "rising":
        cm_note = f"↑ Traffic กำลังเพิ่มบน {source.title()}"
    else:
        cm_note = f"ข้อมูลจาก {source.title()}"

    return {
        "id":             f"{source}_{row.get('id','').split('_',1)[-1]}",
        "name":           name,
        "cuisine":        cuisine.title() if cuisine != "other" else "Other",
        "area":           area_display(area),
        "type":           cuisine,
        "budget":         price,
        "budgetLabel":    price_budget_label(price),
        "signalStrength": sig_strength,
        "signalCount":    signal_count,
        "overlapSignal":  overlap_signal,
        "trendVelocity":  trend,
        "trendBadge":     trend_badge,
        "totalReviews":   last_count,
        "newReviews30d":  new_reviews,
        "velocityPct":    velocity_pct,
        "tags":           [cuisine, area, source],
        "cmNote":         cm_note,
        "isRestaurant":   is_restaurant,
        "source":         source,
        "sourceUrl":      row.get("url") or "",
        "reviewerTiers":  {"mega": 0, "macro": 0, "mid": 0},  # placeholder
        "lastUpdated":    date.today().isoformat(),
    }


def export_json(days: int = 30, limit: int = 500, min_snapshots: int = 0) -> list:
    """
    Export ร้านทั้งหมดจาก DB พร้อม velocity data (ถ้ามี) → export_restaurants.json
    ร้านที่มี velocity (rising) จะขึ้นก่อน ที่เหลือตามหลัง
    """
    all_rows = get_all_restaurants(days=days)

    cm_restaurants = []
    for row in all_rows:
        cm = to_cm_format(row, days=days)
        if cm:
            cm_restaurants.append(cm)

    # Sort: rising first (by velocity), then stable by name
    cm_restaurants.sort(key=lambda r: (
        0 if r["trendVelocity"] == "rising" else 1,
        -(r.get("velocity_pct") or 0)
    ))

    with open(EXPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(cm_restaurants, f, ensure_ascii=False, indent=2)

    rising_count = sum(1 for r in cm_restaurants if r["trendVelocity"] == "rising")
    print(f"✅ Exported {len(cm_restaurants)} restaurants → {EXPORT_JSON}")
    print(f"   🔥 Rising: {rising_count}  |  Stable: {len(cm_restaurants) - rising_count}")
    return cm_restaurants


def show_summary(days: int = 30):
    """แสดงสรุปข้อมูลในฐานข้อมูล"""
    stats = get_stats()
    print("\n" + "="*55)
    print("  ChefMinistry — Database Summary")
    print("="*55)
    print(f"  Total restaurants : {stats['total_restaurants']}")
    for source, count in (stats.get("by_source") or {}).items():
        print(f"  └─ {source:<12}: {count}")
    print(f"  Snapshots stored  : {stats['total_snapshots']}")
    print(f"  Latest snapshot   : {stats['latest_snapshot'] or 'none'}")
    print("="*55)

    trending = get_trending_restaurants(limit=10, days=days)
    if trending:
        print(f"\n  🔥 Top 10 Rising Restaurants ({days}d velocity):")
        for i, r in enumerate(trending, 1):
            v = r.get("velocity_pct", 0)
            n = r.get("new_reviews", 0)
            print(f"  {i:2}. {r['name'][:35]:<35} +{n:3} reviews ({v:+.0f}%)")
    else:
        print("\n  ⚠️  ยังไม่มีข้อมูล velocity — ต้องรัน scraper ≥2 ครั้งต่างวันกัน")
    print()


# รองรับหลาย marker รูปแบบ (ทั้ง Unicode box และ ASCII)
DATAJS_MARKERS = [
    "// ── DB Stats (injected by scraper)",   # Unicode box chars
    "// -- DB Stats (injected by scraper)",   # ASCII dashes
    "// DB Stats (injected by scraper)",       # ไม่มี dashes
    "const CM_DB_STATS",                       # fallback: หา const โดยตรง
]

def inject_into_datajs(cm_restaurants: list):
    """
    อัปเดต CM_DB_STATS และ CM_EXTERNAL_RESTAURANTS ใน data.js
    วิธี: ตัดไฟล์ที่ marker แล้วต่อท้ายด้วยข้อมูลใหม่
    """
    data_js_path = EXPORT_DIR / "data.js"
    if not data_js_path.exists():
        print(f"❌ data.js not found at {data_js_path}")
        return

    stats       = get_stats()
    total_in_db = stats.get("total_restaurants", len(cm_restaurants))
    today       = date.today().isoformat()

    with open(data_js_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # ลอง marker ทีละตัวจนกว่าจะเจอ
    marker_idx = -1
    for mk in DATAJS_MARKERS:
        idx = content.find(mk)
        if idx != -1:
            marker_idx = idx
            print(f"   🔍 Found marker: {mk[:40]!r}")
            break

    if marker_idx == -1:
        print("❌ Marker not found in data.js — ไม่สามารถ inject ได้")
        print("   ลองเช็กว่า data.js มีบรรทัด 'const CM_DB_STATS' หรือไม่")
        return
    base = content[:marker_idx]

    # สร้างบรรทัดใหม่
    json_str = json.dumps(cm_restaurants, ensure_ascii=False)
    tail = (
        f"// -- DB Stats (injected by scraper) -------------------------------------------\n"
        f'const CM_DB_STATS = {{ total: {total_in_db}, lastUpdated: "{today}" }};\n'
        f'const CM_EXTERNAL_RESTAURANTS = {json_str};\n'
    )

    with open(data_js_path, "w", encoding="utf-8") as f:
        f.write(base + tail)

    print(f"✅ Injected {len(cm_restaurants)} restaurants into data.js")
    print(f"   📊 CM_DB_STATS.total = {total_in_db} (all monitored restaurants)")
    print(f"   → {data_js_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ChefMinistry Signal Exporter")
    parser.add_argument("--days",    type=int, default=30, help="Velocity window (days)")
    parser.add_argument("--limit",   type=int, default=100, help="Max restaurants to export")
    parser.add_argument("--inject",  action="store_true", help="Inject into data.js")
    parser.add_argument("--summary", action="store_true", help="Show DB summary only")
    args = parser.parse_args()

    show_summary(days=args.days)

    if not args.summary:
        restaurants = export_json(days=args.days, limit=args.limit)
        if args.inject and restaurants:
            inject_into_datajs(restaurants)
