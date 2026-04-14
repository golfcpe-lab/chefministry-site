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
from db import get_trending_restaurants, get_all_restaurants, get_emerging_restaurants, get_stats, get_conn
from config import EXPORT_JSON, EXPORT_DIR
from classify import classify_record  # v2: venue/scope classification

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


def compute_trend_label(growth_rate: float, total_reviews: int, is_emerging: bool = False) -> str:
    """แปลง growth_rate + size เป็น trend label สำหรับ frontend badge"""
    if is_emerging or (total_reviews < 200 and growth_rate > 0.05):
        return "Emerging"
    if growth_rate > 0.5:
        return "Rising Fast"
    if growth_rate > 0.2:
        return "Gaining Momentum"
    if growth_rate > 0.05:
        return "Steady Growth"
    if growth_rate <= -0.05:
        return "Cooling Down"
    return "Stable"


def trend_velocity_label(trend: str, velocity_pct: float) -> str:
    """แปลง trend + velocity เป็น badge text (legacy — ใช้ใน show_summary)"""
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


def to_cm_format(row: dict, days: int = 30, is_emerging: bool = False) -> dict | None:
    """
    แปลง DB row → ChefMinistry restaurant object

    New fields added (v3):
      _growth      : absolute review growth (int)
      _growthRate  : growth / max(base, 1)  (float)
      _score       : normalized trend score (float) — used by frontend ranking
      _trendLabel  : "Emerging" | "Rising Fast" | "Gaining Momentum" | "Stable"
      _isEmerging  : bool — ใช้แยก tab Trending vs Emerging
    """
    name = row.get("name") or row.get("name_en") or ""
    if not name:
        return None

    new_reviews  = max(0, row.get("new_reviews") or 0)
    velocity_pct = max(0.0, row.get("velocity_pct") or 0.0)   # clamp negative
    last_count   = row.get("last_count") or 0
    first_count  = row.get("first_count") or 0
    rating       = row.get("latest_rating") or row.get("rating") or 4.0
    trend_score  = row.get("trend_score") or row.get("emerging_score") or 0.0

    # ── Growth metrics ────────────────────────────────────────────────────────
    growth      = new_reviews
    base        = max(first_count, 1)
    growth_rate = round(growth / base, 4) if growth > 0 else 0.0

    # ── Trend label ───────────────────────────────────────────────────────────
    trend_label = compute_trend_label(growth_rate, last_count, is_emerging)

    # ── Legacy fields (backward compat) ───────────────────────────────────────
    trend       = "rising" if velocity_pct >= 5 else "stable"
    trend_badge = trend_velocity_label(trend, velocity_pct)
    sig_strength = compute_signal_strength(new_reviews, velocity_pct, last_count)

    cuisine = row.get("cuisine") or "other"
    area    = row.get("area") or "bangkok"
    price   = row.get("price_range") or 2
    source  = row.get("source") or "wongnai"

    NON_RESTAURANT_TYPES = {"street-food", "cafe", "bar", "casual"}
    is_restaurant = cuisine not in NON_RESTAURANT_TYPES

    signal_count  = max(1, int(new_reviews / 10)) if new_reviews else 1
    overlap_signal = 1

    # ── Auto cm_note ──────────────────────────────────────────────────────────
    if is_emerging:
        cm_note = f"🆕 ร้านใหม่น่าจับตา — {int(last_count)} รีวิว rating {rating:.1f} ⭐"
    elif growth_rate >= 0.25:
        cm_note = f"🔥 Review เพิ่ม +{int(velocity_pct)}% ใน {days} วัน — กำลัง spike"
    elif growth_rate >= 0.05:
        cm_note = f"↑ Review เพิ่มขึ้นต่อเนื่องจาก {source.title()}"
    else:
        cm_note = f"ข้อมูลจาก {source.title()} · {int(last_count)} รีวิว"

    # ── Growth metric string for card display ─────────────────────────────────
    growth_pct_display = int(round(growth_rate * 100))
    if growth_pct_display >= 10:
        growth_metric = f"+{growth_pct_display}% in {days} days"
    elif growth > 0:
        growth_metric = f"+{growth} reviews"
    else:
        growth_metric = ""

    base_record = {
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
        # ── New v3 fields for frontend scoring ──────────────────────────────
        "_growth":        growth,
        "_growthRate":    growth_rate,
        "_score":         round(trend_score, 4),
        "_trendLabel":    trend_label,
        "_trendEmoji":    {"Emerging":"🆕","Rising Fast":"🔥","Gaining Momentum":"📈",
                          "Steady Growth":"↗️","Cooling Down":"❄️"}.get(trend_label, "→"),
        "_isEmerging":    is_emerging,
        "_growthMetric":  growth_metric,
        # ── Meta ────────────────────────────────────────────────────────────
        "tags":           [cuisine, area, source],
        "cmNote":         cm_note,
        "isRestaurant":   is_restaurant,
        "source":         source,
        "sourceUrl":      row.get("url") or "",
        "reviewerTiers":  {"mega": 0, "macro": 0, "mid": 0},
        "lastUpdated":    date.today().isoformat(),
        # ── v2: classification pass-through from DB (classify_record fills gaps)
        "city":                row.get("city") or "",
        "province":            row.get("province") or "",
        "country":             row.get("country") or "Thailand",
        "gmaps_types":         _parse_gmaps_types(row.get("gmaps_types")),
        "venue_type":          row.get("venue_type") or "",
        "scope_market":        row.get("scope_market") or "",
        "is_bangkok_focus":    bool(row.get("is_bangkok_focus")),
        "is_restaurant_focus": bool(row.get("is_restaurant_focus")),
        "exclude_reason":      row.get("exclude_reason"),
    }
    # ── v2: run classify_record to fill/correct any missing classification ──
    return classify_record(base_record)


def _parse_gmaps_types(val) -> list:
    """Deserialise gmaps_types from DB TEXT (JSON array) → Python list."""
    import json as _json
    if isinstance(val, list):
        return val
    if isinstance(val, str) and val.startswith("["):
        try:
            return _json.loads(val)
        except Exception:
            pass
    return []



def export_json(days: int = 30, limit: int = 500, min_snapshots: int = 0) -> list:
    """
    Export ร้านทั้งหมดจาก DB พร้อม velocity data → export_restaurants.json

    v3 changes:
    - Sort by _score (normalized) instead of raw velocity
    - Tag emerging restaurants with _isEmerging=True
    - Include emerging restaurants that have no growth data but high rating
    - Prevent large-restaurant dominance
    """
    all_rows = get_all_restaurants(days=days)

    # ── Get emerging rows upfront: build id→score map ────────────────────────
    emerging_rows    = get_emerging_restaurants(limit=50, max_reviews=200)
    emerging_id_map  = {row.get("id", ""): row for row in emerging_rows}

    # ── Build main export, tagging emerging restaurants inline ────────────────
    cm_restaurants = []
    for row in all_rows:
        rid  = row.get("id", "")
        is_em = rid in emerging_id_map
        # For emerging restaurants, inject their emerging_score so _score is non-zero
        if is_em:
            row = dict(row)   # don't mutate original
            em_row = emerging_id_map[rid]
            row["trend_score"] = em_row.get("emerging_score", 0)
        cm = to_cm_format(row, days=days, is_emerging=is_em)
        if cm:
            cm_restaurants.append(cm)

    # ── Sort: trending (by score) first, then emerging (by score) ─────────────
    trending_list = sorted([r for r in cm_restaurants if not r.get("_isEmerging")],
                           key=lambda r: -(r.get("_score") or 0))
    emerging_list = sorted([r for r in cm_restaurants if r.get("_isEmerging")],
                           key=lambda r: -(r.get("_score") or 0))
    cm_restaurants = trending_list + emerging_list

    with open(EXPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(cm_restaurants, f, ensure_ascii=False, indent=2)

    rising_count   = sum(1 for r in cm_restaurants if r.get("trendVelocity") == "rising")
    emerging_count = len(emerging_list)
    print("Exported %d restaurants to %s" % (len(cm_restaurants), EXPORT_JSON))
    print("  Rising: %d | Emerging: %d | Stable: %d" % (rising_count, emerging_count, len(cm_restaurants)-rising_count-emerging_count))
    return cm_restaurants


def show_summary(days=30):
    stats = get_stats()
    print("\n" + "="*55)
    print("  ChefMinistry Database Summary")
    print("="*55)
    print("  Total restaurants : %d" % stats["total_restaurants"])
    for source, count in (stats.get("by_source") or {}).items():
        print("  -- %-12s: %d" % (source, count))
    print("  Snapshots stored  : %d" % stats["total_snapshots"])
    print("  Latest snapshot   : %s" % (stats["latest_snapshot"] or "none"))
    print("="*55)

    trending = get_trending_restaurants(limit=10, days=days)
    if trending:
        print("\n  Top 10 Trending (normalized score, %dd window):" % days)
        print("  %3s %-35s %6s %7s %8s" % ("#", "Name", "total", "growth", "score"))
        print("  " + "-" * 62)
        for i, r in enumerate(trending, 1):
            v  = r.get("velocity_pct", 0)
            n  = r.get("new_reviews", 0)
            sc = r.get("trend_score", 0)
            print("  %2d. %-35s %6d %+7d (%+.0f%%)  %.4f" % (i, r["name"][:33], r.get("last_count",0), n, v, sc))
    else:
        print("\n  No velocity data yet")

    emerging = get_emerging_restaurants(limit=10, max_reviews=200)
    if emerging:
        print("\n  Top 10 Emerging (review_count < 200, rating >= 4.0):")
        print("  %3s %-35s %8s %7s %8s" % ("#", "Name", "reviews", "rating", "score"))
        print("  " + "-" * 62)
        for i, r in enumerate(emerging, 1):
            rating = r.get("latest_rating") or 0
            sc     = r.get("emerging_score") or 0
            print("  %2d. %-35s %8d %7.1f %8.4f" % (i, r["name"][:33], r.get("last_count",0), rating, sc))
    else:
        print("\n  No Emerging data")
    print()


DATAJS_MARKERS = [
    "// ── DB Stats (injected by scraper)",
    "// -- DB Stats (injected by scraper)",
    "// DB Stats (injected by scraper)",
    "const CM_DB_STATS",
]


def inject_into_datajs(cm_restaurants):
    data_js_path = EXPORT_DIR / "data.js"
    if not data_js_path.exists():
        print("data.js not found at %s" % data_js_path)
        return

    stats       = get_stats()
    total_in_db = stats.get("total_restaurants", len(cm_restaurants))
    today       = date.today().isoformat()

    with open(data_js_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    marker_idx = -1
    for mk in DATAJS_MARKERS:
        idx = content.find(mk)
        if idx != -1:
            marker_idx = idx
            print("Found marker: %r" % mk[:40])
            break

    if marker_idx == -1:
        print("Marker not found in data.js")
        return

    base     = content[:marker_idx]
    json_str = json.dumps(cm_restaurants, ensure_ascii=False)
    tail2 = (
        "// -- DB Stats (injected by scraper) ---\n"
        "const CM_DB_STATS = { total: %d, lastUpdated: \"%s\" };\n"
        "const CM_EXTERNAL_RESTAURANTS = %s;\n"
    ) % (total_in_db, today, json_str)

    with open(data_js_path, "w", encoding="utf-8") as f:
        f.write(base + tail2)

    print("Injected %d restaurants into data.js" % len(cm_restaurants))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ChefMinistry Signal Exporter")
    parser.add_argument("--days",    type=int, default=30)
    parser.add_argument("--limit",   type=int, default=100)
    parser.add_argument("--inject",  action="store_true")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    show_summary(days=args.days)

    if not args.summary:
        restaurants = export_json(days=args.days, limit=args.limit)
        if args.inject and restaurants:
            inject_into_datajs(restaurants)
