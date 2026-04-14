"""
ChefMinistry - Signal Exporter v4 (canonical + fallback edition)

Usage:
    python export_signals.py             # export to export_restaurants.json
    python export_signals.py --inject    # also inject into data.js
    python export_signals.py --summary   # show DB stats only
    python export_signals.py --days 14   # 14-day velocity window
"""
import json, argparse, pathlib
from datetime import date
from config import EXPORT_JSON, EXPORT_DIR


def _get_db_stats():
    try:
        from db import get_stats
        return get_stats()
    except Exception as e:
        return {"total_restaurants": 0, "total_snapshots": 0, "latest_snapshot": None, "by_source": {}}


def export_json(days=30, limit=1000, **_kwargs):
    """
    Build canonical dataset from DB -> export_restaurants.json.
    Falls back to existing export file if DB is empty or broken.
    """
    here = pathlib.Path(__file__).parent
    out_path = str(EXPORT_JSON)
    records = []

    # Try building from DB via canonical.py
    try:
        import sys
        sys.path.insert(0, str(here))
        from canonical import build_canonical
        db_path = str(here / "chefministry_data.db")
        records = build_canonical(db_path=db_path, out_path=out_path, days=days)
    except Exception as e:
        print("DB build error: %s" % e)
        records = []

    # Guard: if DB produced 0 in-scope records, use existing export file as fallback
    in_scope = [r for r in records if r.get("is_restaurant_focus") and r.get("is_bangkok_focus")]
    if len(in_scope) == 0:
        existing = pathlib.Path(out_path)
        if existing.exists():
            try:
                fallback = json.loads(existing.read_text(encoding="utf-8"))
                in_scope_fb = [r for r in fallback if r.get("is_restaurant_focus") and r.get("is_bangkok_focus")]
                if len(in_scope_fb) > 0:
                    print("DB empty/broken - using existing export_restaurants.json (%d records)" % len(fallback))
                    return fallback
            except Exception:
                pass
        print("WARNING: no records available from DB or fallback")

    return records


def inject_into_datajs(cm_restaurants):
    """Inject in-scope records into js/data.js (or js/ dir based on EXPORT_DIR)."""
    data_js_path = EXPORT_DIR / "data.js"
    if not data_js_path.exists():
        # Try root js/data.js (GitHub repo structure)
        alt = pathlib.Path("js/data.js")
        if alt.exists():
            data_js_path = alt
        else:
            print("data.js not found at %s" % data_js_path)
            return

    stats = _get_db_stats()
    total_in_db = stats.get("total_restaurants", len(cm_restaurants))
    today = date.today().isoformat()

    with open(data_js_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    MARKERS = [
        "// -- DB Stats (injected by scraper)",
        "// -- DB Stats (injected by scraper)",
        "const CM_DB_STATS",
    ]
    marker_idx = -1
    for mk in MARKERS:
        idx = content.find(mk)
        if idx != -1:
            marker_idx = idx
            break

    if marker_idx == -1:
        print("Marker not found in data.js - appending")
        marker_idx = len(content)

    base = content[:marker_idx]

    # Only inject in-scope records
    in_scope = [r for r in cm_restaurants if r.get("is_restaurant_focus") and r.get("is_bangkok_focus")]

    # Guard: never inject 0 records (would wipe good data)
    if len(in_scope) == 0:
        print("SKIPPING inject: 0 in-scope records - keeping existing data.js")
        return

    json_str = json.dumps(in_scope, ensure_ascii=False)
    tail = (
        "// -- DB Stats (injected by scraper) ---\n"
        "const CM_DB_STATS = { total: %d, lastUpdated: \"%s\" };\n"
        "const CM_EXTERNAL_RESTAURANTS = %s;\n"
    ) % (max(total_in_db, len(in_scope)), today, json_str)

    with open(data_js_path, "w", encoding="utf-8") as f:
        f.write(base + tail)

    print("Injected %d in-scope records into data.js" % len(in_scope))


def show_summary(days=30):
    stats = _get_db_stats()
    print("\n" + "=" * 55)
    print("  ChefMinistry Database Summary")
    print("=" * 55)
    print("  Total restaurants : %d" % stats.get("total_restaurants", 0))
    for source, count in (stats.get("by_source") or {}).items():
        print("  -- %-12s: %d" % (source, count))
    print("  Snapshots stored  : %d" % stats.get("total_snapshots", 0))
    print("  Latest snapshot   : %s" % (stats.get("latest_snapshot") or "none"))
    print("=" * 55)

    try:
        from db import get_trending_restaurants, get_emerging_restaurants
        trending = get_trending_restaurants(limit=10, days=days)
        if trending:
            print("\n  Top 10 Trending:")
            for i, r in enumerate(trending, 1):
                print("  %2d. %-35s %6d  %.4f" % (i, r["name"][:33], r.get("last_count", 0), r.get("trend_score", 0)))
        else:
            print("\n  No velocity data yet (need 2+ snapshots)")
        emerging = get_emerging_restaurants(limit=10, max_reviews=200)
        if emerging:
            print("\n  Top 10 Emerging:")
            for i, r in enumerate(emerging, 1):
                print("  %2d. %-35s %8d %7.1f" % (i, r["name"][:33], r.get("last_count", 0), r.get("latest_rating") or 0))
    except Exception as e:
        print("  (DB query error: %s)" % e)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ChefMinistry Signal Exporter v4")
    parser.add_argument("--days",    type=int, default=30)
    parser.add_argument("--limit",   type=int, default=1000)
    parser.add_argument("--inject",  action="store_true")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    show_summary(days=args.days)

    if not args.summary:
        restaurants = export_json(days=args.days, limit=args.limit)
        if args.inject and restaurants:
            inject_into_datajs(restaurants)
