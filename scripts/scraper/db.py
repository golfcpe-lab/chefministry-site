"""
ChefMinistry — SQLite Database Manager
เก็บข้อมูลร้านและ snapshot review count รายวัน
เพื่อคำนวณ velocity (ร้านไหน review กำลัง spike)
"""
import sqlite3, json
from datetime import datetime, date, timedelta
from config import DB_PATH
import pathlib


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """สร้าง tables ถ้ายังไม่มี — auto-recover ถ้า DB เสียหาย"""
    # ตรวจ DB corruption ก่อน
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1")
    except sqlite3.DatabaseError as e:
        if "malformed" in str(e) or "corrupt" in str(e):
            import shutil
            bak = str(DB_PATH) + ".bak"
            try:
                shutil.copy(str(DB_PATH), bak)
                print(f"⚠️  DB เสียหาย — backup ไว้ที่ {bak} แล้วสร้างใหม่")
            except Exception:
                pass
            DB_PATH.unlink(missing_ok=True)
        else:
            raise

    with get_conn() as conn:
        conn.executescript("""
        -- ข้อมูลหลักของร้าน
        CREATE TABLE IF NOT EXISTS restaurants (
            id          TEXT PRIMARY KEY,   -- "{source}_{external_id}"
            source      TEXT NOT NULL,      -- "wongnai" | "grabfood" | "lineman"
            external_id TEXT NOT NULL,
            name        TEXT NOT NULL,
            name_en     TEXT,
            cuisine     TEXT,
            area        TEXT,
            address     TEXT,
            lat         REAL,
            lng         REAL,
            price_range INTEGER,            -- 1-4
            url         TEXT,
            image_url   TEXT,
            first_seen  TEXT DEFAULT (date('now')),
            last_updated TEXT DEFAULT (datetime('now')),
            business_status TEXT DEFAULT 'OPERATIONAL',  -- OPERATIONAL | CLOSED_TEMPORARILY | CLOSED_PERMANENTLY

            -- ── Classification layer (schema v2) ──────────────────────────
            -- Populated by classify.py at export time and by scrape_gmaps.py
            -- at ingest time.  All columns are nullable so old records stay valid.
            city                TEXT,  -- "Bangkok" | ""
            province            TEXT,  -- "Bangkok" | "Chiang Mai" | ...
            country             TEXT DEFAULT 'Thailand',
            gmaps_types         TEXT,  -- JSON array from Places API (e.g. ["restaurant","thai_restaurant"])
            venue_type          TEXT,  -- restaurant | cafe | kiosk | street_food | food_stand | takeaway_only | unknown
            scope_market        TEXT,  -- bangkok_restaurant_focus | bangkok_cafe_focus | out_of_scope_location | out_of_scope_format | needs_review
            is_bangkok_focus    INTEGER DEFAULT 0,   -- 0/1 boolean
            is_restaurant_focus INTEGER DEFAULT 0,   -- 0/1 boolean
            exclude_reason      TEXT,  -- null | province_not_bangkok | kiosk_format | street_food_format | food_stand_format | takeaway_only | missing_location | unclear_format
            -- ──────────────────────────────────────────────────────────────

            UNIQUE(source, external_id)
        );

        -- Snapshot รายวัน — หัวใจของ velocity tracking
        CREATE TABLE IF NOT EXISTS review_snapshots (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id   TEXT NOT NULL REFERENCES restaurants(id),
            snapshot_date   TEXT NOT NULL DEFAULT (date('now')),
            review_count    INTEGER,
            rating          REAL,
            rating_count    INTEGER,
            UNIQUE(restaurant_id, snapshot_date)
        );

        -- Index เพื่อ query เร็ว
        CREATE INDEX IF NOT EXISTS idx_snap_restaurant ON review_snapshots(restaurant_id);
        CREATE INDEX IF NOT EXISTS idx_snap_date ON review_snapshots(snapshot_date);
        CREATE INDEX IF NOT EXISTS idx_rest_source ON restaurants(source);
        CREATE INDEX IF NOT EXISTS idx_rest_area ON restaurants(area);
        -- scope/bkk indexes created after migration (see _migrate_classification_columns)
        -- scope/bkk indexes created after migration (see _migrate_classification_columns)
        """)
    # ── Safe migration: add classification columns if they don't exist yet ──
    _migrate_classification_columns()
    print(f"✅ DB ready: {DB_PATH}")


def _migrate_classification_columns():
    """
    ADD COLUMN migration — safe to run on existing DB.
    SQLite does not support IF NOT EXISTS on ALTER TABLE, so we catch errors.
    """
    new_columns = [
        ("city",                "TEXT"),
        ("province",            "TEXT"),
        ("country",             "TEXT DEFAULT 'Thailand'"),
        ("gmaps_types",         "TEXT"),
        ("venue_type",          "TEXT"),
        ("scope_market",        "TEXT"),
        ("is_bangkok_focus",    "INTEGER DEFAULT 0"),
        ("is_restaurant_focus", "INTEGER DEFAULT 0"),
        ("exclude_reason",      "TEXT"),
    ]
    with get_conn() as conn:
        for col_name, col_def in new_columns:
            try:
                conn.execute(f"ALTER TABLE restaurants ADD COLUMN {col_name} {col_def}")
            except Exception:
                pass  # Column already exists — skip silently
        # Create classification indexes now that columns exist
        for idx_sql in [
            "CREATE INDEX IF NOT EXISTS idx_rest_scope ON restaurants(scope_market)",
            "CREATE INDEX IF NOT EXISTS idx_rest_bkk ON restaurants(is_bangkok_focus)",
        ]:
            try:
                conn.execute(idx_sql)
            except Exception:
                pass


def upsert_restaurant(data: dict) -> str:
    """
    Insert หรือ update ร้าน
    data ต้องมี: source, external_id, name, cuisine, area

    v2: also stores classification fields (city, province, gmaps_types,
        venue_type, scope_market, is_bangkok_focus, is_restaurant_focus,
        exclude_reason) when provided.

    Returns: restaurant_id
    """
    import json as _json
    rid = f"{data['source']}_{data['external_id']}"

    # gmaps_types may be a list — serialise to JSON string for SQLite TEXT column
    gmaps_types_raw = data.get("gmaps_types")
    if isinstance(gmaps_types_raw, list):
        gmaps_types_val = _json.dumps(gmaps_types_raw, ensure_ascii=False)
    else:
        gmaps_types_val = gmaps_types_raw  # already a string or None

    with get_conn() as conn:
        conn.execute("""
            INSERT INTO restaurants
                (id, source, external_id, name, name_en, cuisine, area,
                 address, lat, lng, price_range, url, image_url, last_updated,
                 city, province, country, gmaps_types,
                 venue_type, scope_market,
                 is_bangkok_focus, is_restaurant_focus, exclude_reason)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'),
                    ?,?,?,?,?,?,?,?,?)
            ON CONFLICT(source, external_id) DO UPDATE SET
                name                = excluded.name,
                cuisine             = excluded.cuisine,
                area                = excluded.area,
                price_range         = excluded.price_range,
                last_updated        = excluded.last_updated,
                -- Update classification fields only if the new value is non-NULL
                -- (avoids overwriting a good classification with NULL on re-scrape)
                city                = COALESCE(excluded.city,                city),
                province            = COALESCE(excluded.province,            province),
                country             = COALESCE(excluded.country,             country),
                gmaps_types         = COALESCE(excluded.gmaps_types,         gmaps_types),
                venue_type          = COALESCE(excluded.venue_type,          venue_type),
                scope_market        = COALESCE(excluded.scope_market,        scope_market),
                is_bangkok_focus    = COALESCE(excluded.is_bangkok_focus,    is_bangkok_focus),
                is_restaurant_focus = COALESCE(excluded.is_restaurant_focus, is_restaurant_focus),
                exclude_reason      = excluded.exclude_reason
        """, (
            rid,
            data.get("source"),
            data.get("external_id"),
            data.get("name"),
            data.get("name_en"),
            data.get("cuisine"),
            data.get("area"),
            data.get("address"),
            data.get("lat"),
            data.get("lng"),
            data.get("price_range"),
            data.get("url"),
            data.get("image_url"),
            # classification fields
            data.get("city"),
            data.get("province"),
            data.get("country", "Thailand"),
            gmaps_types_val,
            data.get("venue_type"),
            data.get("scope_market"),
            1 if data.get("is_bangkok_focus") else 0,
            1 if data.get("is_restaurant_focus") else 0,
            data.get("exclude_reason"),
        ))
    return rid


def record_snapshot(restaurant_id: str, review_count: int,
                    rating: float, rating_count: int):
    """บันทึก snapshot วันนี้ (ถ้ามีแล้วจะ update)"""
    today = date.today().isoformat()
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO review_snapshots
                (restaurant_id, snapshot_date, review_count, rating, rating_count)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(restaurant_id, snapshot_date) DO UPDATE SET
                review_count = excluded.review_count,
                rating       = excluded.rating,
                rating_count = excluded.rating_count
        """, (restaurant_id, today, review_count, rating, rating_count))


def get_velocity(restaurant_id: str, days: int = 30) -> dict:
    """
    คำนวณ velocity: จำนวน review ใหม่ใน N วันที่ผ่านมา
    Returns: { new_reviews, old_reviews, velocity_pct, trend }
    """
    since = (date.today() - timedelta(days=days)).isoformat()
    today = date.today().isoformat()

    with get_conn() as conn:
        rows = conn.execute("""
            SELECT snapshot_date, review_count
            FROM review_snapshots
            WHERE restaurant_id = ?
            ORDER BY snapshot_date
        """, (restaurant_id,)).fetchall()

    if len(rows) < 2:
        return {"new_reviews": 0, "old_reviews": 0,
                "velocity_pct": 0, "trend": "stable", "snapshots": len(rows)}

    # หา oldest และ latest snapshot
    oldest = rows[0]["review_count"] or 0
    latest = rows[-1]["review_count"] or 0
    new_reviews = max(0, latest - oldest)

    # velocity % เทียบกับ baseline
    pct = round((new_reviews / oldest * 100) if oldest > 0 else 0, 1)

    if pct >= 20 or new_reviews >= 50:
        trend = "rising"
    elif pct <= -5:
        trend = "declining"
    else:
        trend = "stable"

    return {
        "new_reviews":   new_reviews,
        "old_reviews":   oldest,
        "latest_count":  latest,
        "velocity_pct":  pct,
        "trend":         trend,
        "snapshots":     len(rows),
    }


def get_trending_restaurants(limit: int = 50, days: int = 30) -> list:
    """
    ดึงร้านที่ trending โดยใช้ normalized score เพื่อป้องกัน large-restaurant dominance.

    OLD: ORDER BY new_reviews DESC  → ร้านใหญ่ชนะเสมอ (absolute bias)
    NEW: score = growth_rate * log(total+1) / log(total+10)  → balanced by size
         growth_rate = (last - first) / max(first, 1)

    หมายเหตุ data quality: snapshot Apr-05 (Wongnai cumulative) vs Apr-06 (recent only)
    เป็น incompatible metrics → growth จะถูก clamp ที่ 0 ถ้า last < first
    """
    since = (date.today() - timedelta(days=days)).isoformat()

    with get_conn() as conn:
        rows = conn.execute("""
            WITH ranked AS (
                SELECT
                    s.restaurant_id,
                    s.review_count,
                    s.rating,
                    s.snapshot_date,
                    ROW_NUMBER() OVER (PARTITION BY s.restaurant_id ORDER BY s.snapshot_date ASC)  AS rn_asc,
                    ROW_NUMBER() OVER (PARTITION BY s.restaurant_id ORDER BY s.snapshot_date DESC) AS rn_desc
                FROM review_snapshots s
                WHERE s.snapshot_date >= ?
            ),
            first_last AS (
                SELECT
                    restaurant_id,
                    MAX(CASE WHEN rn_asc  = 1 THEN review_count END) AS first_count,
                    MAX(CASE WHEN rn_desc = 1 THEN review_count END) AS last_count,
                    MAX(CASE WHEN rn_desc = 1 THEN rating END)       AS latest_rating,
                    COUNT(*) / 2 AS snapshot_count
                FROM ranked GROUP BY restaurant_id
            )
            SELECT
                r.id, r.name, r.name_en, r.cuisine, r.area,
                r.price_range, r.url, r.source,
                r.city, r.province, r.country, r.gmaps_types,
                r.venue_type, r.scope_market,
                r.is_bangkok_focus, r.is_restaurant_focus, r.exclude_reason,
                fl.first_count, fl.last_count, fl.latest_rating, fl.snapshot_count,
                -- growth: clamp negative to 0 (data inconsistency guard)
                MAX(0, fl.last_count - fl.first_count) AS new_reviews,
                -- growth_rate: normalized by base (avoid divide-by-zero)
                CASE
                    WHEN fl.first_count > 0 AND fl.last_count > fl.first_count
                    THEN ROUND((fl.last_count - fl.first_count) * 100.0 / fl.first_count, 1)
                    ELSE 0
                END AS velocity_pct,
                -- normalized score: reduces large-restaurant dominance
                CASE
                    WHEN fl.first_count > 0 AND fl.last_count > fl.first_count
                    THEN ROUND(
                        ((fl.last_count - fl.first_count) * 1.0 / fl.first_count)
                        * (LOG(fl.last_count + 1) / LOG(fl.last_count + 10))
                        * COALESCE(fl.latest_rating, 4.0) / 4.0
                    , 4)
                    ELSE 0
                END AS trend_score
            FROM restaurants r
            JOIN first_last fl ON fl.restaurant_id = r.id
            WHERE COALESCE(r.business_status, 'OPERATIONAL') != 'CLOSED_PERMANENTLY'
            ORDER BY trend_score DESC, velocity_pct DESC
            LIMIT ?
        """, (since, limit)).fetchall()

    return [dict(r) for r in rows]


def get_emerging_restaurants(limit: int = 20, max_reviews: int = 200) -> list:
    """
    ดึงร้านใหม่ที่กำลังเติบโตเร็ว (review count ต่ำ แต่ trend ดี).

    เกณฑ์ Emerging:
      - last_count < max_reviews (ยังไม่ใหญ่มาก)
      - rating >= 4.0 (คุณภาพพอใช้)
      - ไม่ CLOSED_PERMANENTLY

    สำหรับร้านที่มี 1 snapshot: ใช้ rating เป็น signal หลัก
    สำหรับร้านที่มี 2 snapshot: ใช้ growth_rate เพิ่มเติม
    """
    with get_conn() as conn:

        rows = conn.execute("""
            WITH latest AS (
                SELECT restaurant_id, MAX(snapshot_date) AS snap_date, COUNT(*) AS snap_count
                FROM review_snapshots GROUP BY restaurant_id
            ),
            snap_data AS (
                SELECT l.restaurant_id, l.snap_count,
                       s.review_count AS last_count, s.rating AS latest_rating,
                       first_s.review_count AS first_count
                FROM latest l
                JOIN review_snapshots s ON s.restaurant_id=l.restaurant_id AND s.snapshot_date=l.snap_date
                LEFT JOIN review_snapshots first_s ON first_s.restaurant_id=l.restaurant_id
                   AND first_s.snapshot_date=(SELECT MIN(snapshot_date) FROM review_snapshots WHERE restaurant_id=l.restaurant_id)
            )
            SELECT r.id, r.name, r.name_en, r.cuisine, r.area, r.price_range, r.url, r.source, r.first_seen,
                   sd.last_count, sd.latest_rating, sd.snap_count,
                   CASE WHEN sd.snap_count>1 AND sd.last_count>sd.first_count
                        THEN ROUND((sd.last_count-sd.first_count)*100.0/sd.first_count,1) ELSE 0 END AS growth_rate,
                   ROUND((sd.latest_rating/5.0)*0.6
                       + CASE WHEN sd.last_count>0 THEN MIN(sd.last_count/100.0,1.0)*0.2 ELSE 0 END
                       + CASE WHEN sd.snap_count>1 AND sd.last_count>sd.first_count
                              THEN MIN((sd.last_count-sd.first_count)*1.0/sd.first_count,1.0)*0.2 ELSE 0 END
                   ,4) AS emerging_score
            FROM restaurants r JOIN snap_data sd ON sd.restaurant_id=r.id
            WHERE COALESCE(r.business_status,'OPERATIONAL') != 'CLOSED_PERMANENTLY'
              AND sd.latest_rating >= 4.0 AND sd.last_count < ? AND sd.last_count > 0
            ORDER BY emerging_score DESC LIMIT ?
        """, (max_reviews, limit)).fetchall()
    return [dict(r) for r in rows]


def get_all_restaurants(days: int = 30) -> list:
    """ดึงร้านทั้งหมดพร้อม velocity data สำหรับ export"""
    since = (date.today() - timedelta(days=days)).isoformat()
    with get_conn() as conn:
        rows = conn.execute("""
            WITH ranked AS (
                SELECT s.restaurant_id, s.review_count, s.rating, s.snapshot_date,
                       ROW_NUMBER() OVER (PARTITION BY s.restaurant_id ORDER BY s.snapshot_date ASC)  AS rn_asc,
                       ROW_NUMBER() OVER (PARTITION BY s.restaurant_id ORDER BY s.snapshot_date DESC) AS rn_desc
                FROM review_snapshots s WHERE s.snapshot_date >= ?
            ),
            first_last AS (
                SELECT restaurant_id,
                       MAX(CASE WHEN rn_asc=1  THEN review_count END) AS first_count,
                       MAX(CASE WHEN rn_desc=1 THEN review_count END) AS last_count,
                       MAX(CASE WHEN rn_desc=1 THEN rating END)       AS latest_rating,
                       COUNT(*)/2 AS snapshot_count
                FROM ranked GROUP BY restaurant_id
            )
            SELECT r.id, r.name, r.name_en, r.cuisine, r.area, r.price_range, r.url, r.source,
                   r.city, r.province, r.country, r.gmaps_types,
                   r.venue_type, r.scope_market, r.is_bangkok_focus, r.is_restaurant_focus, r.exclude_reason,
                   fl.first_count, fl.last_count, fl.latest_rating, fl.snapshot_count,
                   MAX(0, COALESCE(fl.last_count,0)-COALESCE(fl.first_count,0)) AS new_reviews,
                   CASE WHEN fl.first_count>0 AND fl.last_count>fl.first_count
                        THEN ROUND((fl.last_count-fl.first_count)*100.0/fl.first_count,1) ELSE 0 END AS velocity_pct,
                   CASE WHEN fl.first_count>0 AND fl.last_count>fl.first_count
                        THEN ROUND(((fl.last_count-fl.first_count)*1.0/fl.first_count)
                             *(LOG(fl.last_count+1)/LOG(fl.last_count+10))
                             *COALESCE(fl.latest_rating,4.0)/4.0, 4) ELSE 0 END AS trend_score
            FROM restaurants r
            LEFT JOIN first_last fl ON fl.restaurant_id=r.id
            WHERE COALESCE(r.business_status,'OPERATIONAL') != 'CLOSED_PERMANENTLY'
            ORDER BY trend_score DESC, velocity_pct DESC
        """, (since,)).fetchall()
    return [dict(r) for r in rows]


def get_stats() -> dict:
    """สถิติรวมของ DB"""
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM restaurants").fetchone()[0]
        snaps = conn.execute("SELECT COUNT(*) FROM review_snapshots").fetchone()[0]
        latest = conn.execute("SELECT MAX(snapshot_date) FROM review_snapshots").fetchone()[0]
        by_source_rows = conn.execute(
            "SELECT source, COUNT(*) as c FROM restaurants GROUP BY source"
        ).fetchall()
    return {
        "total_restaurants": total,
        "total_snapshots":   snaps,
        "latest_snapshot":   latest,
        "by_source":         {r["source"]: r["c"] for r in by_source_rows},
    }
