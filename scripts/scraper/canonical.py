"""
ChefMinistry — Canonical Dataset Builder
Single source of truth for the restaurant data pipeline.

Usage:
    python3 canonical.py [--db PATH] [--output PATH] [--days N]

Imports:
    from canonical import build_canonical
"""
import sqlite3, json, math, sys, argparse, pathlib
from datetime import date, timedelta

DB  = str(pathlib.Path(__file__).parent / "chefministry_data.db")
OUT = str(pathlib.Path(__file__).parent / "export_restaurants.json")

CUISINE_NORM = {
    "thai":"Thai","japanese":"Japanese","omakase":"Omakase","italian":"Italian",
    "ramen":"Ramen","steakhouse":"Steakhouse","steak":"Steakhouse","seafood":"Seafood",
    "cafe":"Cafe","coffee":"Cafe","street-food":"Street Food","street food":"Street Food",
    "street_food":"Street Food","chinese":"Chinese","korean":"Korean","french":"French",
    "indian":"Indian","dim-sum":"Dim Sum","dimsum":"Dim Sum","hotpot":"Hotpot",
    "shabu":"Hotpot","bbq":"BBQ","yakiniku":"Yakiniku","noodle":"Noodle",
    "isaan":"Isaan Thai","fine-dining":"Fine Dining","fine dining":"Fine Dining",
    "western":"Western","fusion":"Fusion","vegetarian":"Vegetarian","vegan":"Vegan",
    "other":"Other","casual-dining":"Casual Dining","casual":"Casual Dining",
    "local":"Local Thai","bar":"Bar & Grill","pizza":"Italian",
}
AREA_NORM = {
    "thonglor":"Thonglor","ekkamai":"Ekkamai","silom":"Silom","sathorn":"Sathorn",
    "ari":"Ari","ratchada":"Ratchada","sukhumvit":"Sukhumvit","onnut":"On Nut",
    "on nut":"On Nut","ladprao":"Lat Phrao","lat phrao":"Lat Phrao",
    "rama9":"Rama 9","rama 9":"Rama 9","asok":"Asok","asoke":"Asok",
    "phromphong":"Phrom Phong","phrom phong":"Phrom Phong",
    "ramintra":"Ram Intra","raminthra":"Ram Intra","ram intra":"Ram Intra",
    "ramkhamhaeng":"Ram Khamhaeng","bangkok":"Bangkok","siam":"Siam",
    "nana":"Nana","chit lom":"Chit Lom","chitlom":"Chit Lom",
    "phaya thai":"Phaya Thai",
}
PRICE_LABEL = {1:"\u0e3f", 2:"\u0e3f\u0e3f", 3:"\u0e3f\u0e3f\u0e3f", 4:"\u0e3f\u0e3f\u0e3f\u0e3f"}
SOURCE_NORM = {"wongnai":"Wongnai","gmaps":"Google Maps","youtube":"YouTube","manual":"Manual","community":"Community Pick"}
EMOJI_MAP = {
    "Rising Fast":"\U0001f525","Emerging":"\U0001f195","Gaining Momentum":"\U0001f4c8",
    "Steady Growth":"\u2197\ufe0f","Social Buzz":"\U0001f4f2","Also Trending":"\u2197\ufe0f",
    "Under Watch":"\U0001f440","Cooling Down":"\u2744\ufe0f","Stable":"\u2192",
}


def norm_cuisine(raw):
    if not raw: return "Other"
    return CUISINE_NORM.get(raw.strip().lower(), raw.strip().title())


def norm_area(raw):
    if not raw: return ""
    return AREA_NORM.get(raw.strip().lower(), raw.strip().title())


def norm_source(raw):
    return SOURCE_NORM.get((raw or "").strip().lower(), (raw or "").title())


def compute_trend(fc, lc, appeared3):
    if not fc or not lc:
        return 0.0, 0.0, 0
    growth = max(0, lc - fc)
    gr = growth / max(fc, 1)
    sc = gr * math.log(lc + 1) / math.log(lc + 10)
    if appeared3:
        sc *= 0.8
    return round(sc, 6), round(gr, 4), growth


def get_trend_label(gr, total, is_em, c_sc):
    if c_sc > 0.5 and total < 200: return "Social Buzz"
    if is_em or (total < 200 and gr > 0.03): return "Emerging"
    if gr > 0.5:  return "Rising Fast"
    if gr > 0.15: return "Gaining Momentum"
    if gr > 0.05: return "Steady Growth"
    if gr > 0.01: return "Also Trending"
    if gr < -0.05: return "Cooling Down"
    return "Stable"


def creator_score(m7, m30, total):
    if not m30: return 0.0
    base = ((m7 or 0) * 2 + (m30 or 0)) / 10.0
    if total and total < 100: base *= 1.5
    return round(min(base, 1.0), 3)


def build_canonical(db_path=None, out_path=None, days=30):
    """Build canonical restaurant dataset from SQLite DB."""
    db_path  = db_path  or DB
    out_path = out_path or OUT

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    since = (date.today() - timedelta(days=days)).isoformat()
    today_str = date.today().isoformat()

    sql_snaps = (
        "WITH ranked AS ("
        "  SELECT s.restaurant_id, s.review_count, s.rating, s.snapshot_date,"
        "    ROW_NUMBER() OVER (PARTITION BY s.restaurant_id ORDER BY s.snapshot_date ASC) AS rn_asc,"
        "    ROW_NUMBER() OVER (PARTITION BY s.restaurant_id ORDER BY s.snapshot_date DESC) AS rn_desc"
        "  FROM review_snapshots s WHERE s.snapshot_date >= ?"
        "),"
        "fl AS ("
        "  SELECT restaurant_id,"
        "    MAX(CASE WHEN rn_asc=1 THEN review_count END) AS first_count,"
        "    MAX(CASE WHEN rn_desc=1 THEN review_count END) AS last_count,"
        "    MAX(CASE WHEN rn_desc=1 THEN rating END) AS latest_rating,"
        "    COUNT(*)/2 AS snap_count"
        "  FROM ranked GROUP BY restaurant_id"
        ")"
        " SELECT r.id, r.name, r.name_en, r.source, r.url,"
        "   r.address, r.cuisine, r.area, r.gmaps_address, r.gmaps_place_id,"
        "   r.city, r.province, r.country, r.gmaps_types,"
        "   r.venue_type, r.scope_market, r.is_bangkok_focus,"
        "   r.is_restaurant_focus, r.exclude_reason, r.price_range,"
        "   r.first_seen, r.last_updated, r.business_status, r.candidate_status,"
        "   r.creator_mentions_7d, r.creator_mentions_30d, r.creator_signal_score,"
        "   r.appeared_last_3_cycles,"
        "   fl.first_count, fl.last_count, fl.latest_rating, fl.snap_count,"
        "   MAX(0, COALESCE(fl.last_count,0)-COALESCE(fl.first_count,0)) AS new_reviews"
        " FROM restaurants r LEFT JOIN fl ON fl.restaurant_id=r.id"
        " WHERE (r.business_status IS NULL OR r.business_status != ?)"
        " ORDER BY new_reviews DESC"
    )
    rows = conn.execute(sql_snaps, (since, "CLOSED_PERMANENTLY")).fetchall()
    has_snaps = set(r["id"] for r in rows)

    if has_snaps:
        placeholders = ",".join("?" * len(has_snaps))
        sql_no_snaps = (
            "SELECT r.id, r.name, r.name_en, r.source, r.url,"
            "  r.address, r.cuisine, r.area, r.gmaps_address, r.gmaps_place_id,"
            "  r.city, r.province, r.country, r.gmaps_types,"
            "  r.venue_type, r.scope_market, r.is_bangkok_focus,"
            "  r.is_restaurant_focus, r.exclude_reason, r.price_range,"
            "  r.first_seen, r.last_updated, r.business_status, r.candidate_status,"
            "  r.creator_mentions_7d, r.creator_mentions_30d, r.creator_signal_score,"
            "  r.appeared_last_3_cycles,"
            "  NULL AS first_count, NULL AS last_count, NULL AS latest_rating,"
            "  0 AS snap_count, 0 AS new_reviews"
            " FROM restaurants r WHERE r.id NOT IN (" + placeholders + ")"
            " AND (r.business_status IS NULL OR r.business_status != ?)"
        )
        no_snaps = conn.execute(sql_no_snaps, list(has_snaps) + ["CLOSED_PERMANENTLY"]).fetchall()
    else:
        no_snaps = []

    all_rows = list(rows) + list(no_snaps)
    print("Rows: %d (%d with snaps, %d without)" % (len(all_rows), len(rows), len(no_snaps)))

    canonical = []
    for row in all_rows:
        d = dict(row)
        name = d.get("name") or d.get("name_en") or ""
        if not name:
            continue

        src = d.get("source") or "unknown"
        rid = d.get("id") or ("%s_%s" % (src, name[:20]))
        cuisine_raw  = d.get("cuisine") or "Other"
        cuisine_norm = norm_cuisine(cuisine_raw)
        area_raw     = d.get("area") or ""
        area_norm    = norm_area(area_raw)
        # แก้ area ผิดจากข้อมูลเก่า — เทียบกับที่อยู่จริงจาก Google Maps
        try:
            from area_fix import resolve_area
            area_norm = resolve_area(area_norm, d.get("gmaps_address") or "") or area_norm
        except Exception:
            pass
        price_raw    = d.get("price_range") or 2
        price_lbl    = PRICE_LABEL.get(price_raw, "\u0e3f\u0e3f")

        fc     = d.get("first_count") or 0
        lc     = d.get("last_count") or 0
        nr     = d.get("new_reviews") or 0
        rating = d.get("latest_rating") or 4.0
        app3   = bool(d.get("appeared_last_3_cycles"))

        sc, gr, growth = compute_trend(fc, lc, app3)

        m7  = d.get("creator_mentions_7d") or 0
        m30 = d.get("creator_mentions_30d") or 0
        c_sc = float(d.get("creator_signal_score") or 0) or creator_score(m7, m30, lc)
        c_gr = round((m7 / max(m30 - m7, 1)) if m30 > m7 else 0, 3)
        is_viral = bool(c_sc > 0.3 and lc < 200)

        is_em = bool(lc > 0 and lc < 200 and (gr > 0.03 or rating >= 4.5))
        tl = get_trend_label(gr, lc, is_em, c_sc)

        trend_rsn = ""
        if tl in ("Rising Fast", "Gaining Momentum"):
            trend_rsn = "+%d%% growth in 30d" % int(gr * 100)
        elif tl == "Emerging":
            trend_rsn = "%d reviews, rating %.1f" % (lc, rating)
        elif tl == "Social Buzz":
            trend_rsn = "%d creator mentions" % m30
        elif tl in ("Also Trending", "Steady Growth"):
            trend_rsn = "+%d new reviews" % nr

        gm_pct = int(gr * 100)
        if gm_pct >= 10:
            growth_metric = "+%d%% in 30 days" % gm_pct
        elif nr > 0:
            growth_metric = "+%d reviews" % nr
        else:
            growth_metric = ""

        venue_type = d.get("venue_type") or "unknown"
        scope_mkt  = d.get("scope_market") or "needs_review"
        is_bkk     = bool(d.get("is_bangkok_focus"))
        is_rest    = bool(d.get("is_restaurant_focus"))
        excl       = d.get("exclude_reason")

        gmaps_types = []
        if d.get("gmaps_types"):
            try:
                gmaps_types = json.loads(d["gmaps_types"])
            except Exception:
                pass

        record = {
            "id": rid, "name": name, "name_en": d.get("name_en") or name,
            "source": norm_source(src), "source_raw": src,
            "address": d.get("gmaps_address") or d.get("address") or "",
            "url": d.get("url") or "", "place_id": d.get("gmaps_place_id") or "",
            "cuisine_raw": cuisine_raw, "cuisine_normalized": cuisine_norm, "cuisine": cuisine_norm,
            "area_raw": area_raw, "area_normalized": area_norm, "area": area_norm,
            "city": d.get("city") or "Bangkok", "province": d.get("province") or "Bangkok",
            "price_range_raw": price_raw, "price_range_normalized": price_lbl,
            "budget": price_raw, "budgetLabel": price_lbl,
            "rating_gmaps": round(rating, 1), "rating_wongnai": None,
            "reviews_gmaps": lc if src == "gmaps" else None,
            "reviews_wongnai": lc if src == "wongnai" else None,
            "totalReviews": lc, "newReviews30d": nr,
            "velocityPct": round(gr * 100, 1),
            "first_seen": d.get("first_seen") or today_str, "last_updated": today_str,
            "venue_type": venue_type, "scope_market": scope_mkt,
            "is_bangkok_focus": is_bkk, "is_restaurant_focus": is_rest,
            "exclude_reason": excl, "gmaps_types": gmaps_types,
            "candidate_status": d.get("candidate_status") or "candidate",
            "_score": sc, "_growth": growth, "_growthRate": gr,
            "_growthMetric": growth_metric,
            "trend_score": sc, "trend_label": tl, "trend_reason": trend_rsn,
            "_trendLabel": tl, "_trendEmoji": EMOJI_MAP.get(tl, "\u2192"), "_isEmerging": is_em,
            "creator_mentions_7d": m7, "creator_mentions_30d": m30,
            "creator_growth_rate": c_gr, "creator_signal_score": c_sc,
            "first_social_seen": d.get("first_social_seen") or "",
            "is_viral_candidate": is_viral,
            "signalStrength": "strong" if sc > 0.1 else ("moderate" if sc > 0.02 else "weak"),
            "signalCount": max(1, int(nr / 10)) if nr else 1,
            "overlapSignal": 1,
            "trendVelocity": "rising" if gr > 0.05 else "stable",
            "trendBadge": ("\u2191 " + tl) if gr > 0.01 else "\u2192 Stable",
            "type": venue_type,
            "tags": [cuisine_norm, area_norm, norm_source(src)],
            "cmNote": trend_rsn or ("%d reviews \u00b7 %s" % (lc, norm_source(src))),
            "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0},
            "recentReviewers": [],
        }
        canonical.append(record)

    canonical.sort(key=lambda r: -(r["trend_score"] or 0))

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(canonical, f, ensure_ascii=False, indent=2)

    in_scope = [r for r in canonical if r["is_restaurant_focus"]]
    bkk_rest = [r for r in canonical if r["is_bangkok_focus"] and r["is_restaurant_focus"]]
    emerging = [r for r in canonical if r["_isEmerging"]]
    print("Total: %d | In-scope: %d | Bangkok+rest: %d | Emerging: %d" % (
        len(canonical), len(in_scope), len(bkk_rest), len(emerging)))
    return canonical


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ChefMinistry Canonical Dataset Builder")
    parser.add_argument("--db",     default=DB)
    parser.add_argument("--output", default=OUT)
    parser.add_argument("--days",   type=int, default=30)
    args = parser.parse_args()
    build_canonical(args.db, args.output, args.days)
