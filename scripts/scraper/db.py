"""
ChefMinistry — SQLite Database Manager
เก็บข้อมูลร้านและ snapshot review count รายวัน
เพื่อคำนวณ velocity (ร้านไหน review กำลัง spike)
"""
import sqlite3, json
from datetime import datetime, date, timedelta
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """สร้าง tables ถ้ายังไม่มี"""
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
        """)
    print(f"✅ DB ready: {DB_PATH}")


def upsert_restaurant(data: dict) -> str:
    """
    Insert หรือ update ร้าน
    data ต้องมี: source, external_id, name, cuisine, area
    Returns: restaurant_id
    """
    rid = f"{data['source']}_{data['external_id']}"
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO restaurants
                (id, source, external_id, name, name_en, cuisine, area,
                 address, lat, lng, price_range, url, image_url, last_updated)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))
            ON CONFLICT(source, external_id) DO UPDATE SET
                name         = excluded.name,
                cuisine      = excluded.cuisine,
                area         = excluded.area,
                price_range  = excluded.price_range,
                last_updated = excluded.last_updated
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
    ดึงร้านที่ review เพิ่มขึ้นเร็วที่สุดใน N วัน
    """
    since = (date.today() - timedelta(days=days)).isoformat()

    with get_conn() as conn:
        # หา earliest และ latest review_count ของแต่ละร้านใน window
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
                fl.first_count, fl.last_count, fl.latest_rating, fl.snapshot_count,
                (fl.last_count - fl.first_count) AS new_reviews,
                CASE
                    WHEN fl.first_count > 0
                    THEN ROUND((fl.last_count - fl.first_count) * 100.0 / fl.first_count, 1)
                    ELSE 0
                END AS velocity_pct
            FROM restaurants r
            JOIN first_last fl ON fl.restaurant_id = r.id
            WHERE fl.last_count > fl.first_count
            ORDER BY new_reviews DESC, velocity_pct DESC
            LIMIT ?
        """, (since, limit)).fetchall()

    return [dict(r) for r in rows]


def get_stats() -> dict:
    """Summary stats ของ database"""
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM restaurants").fetchone()[0]
        by_source = conn.execute(
            "SELECT source, COUNT(*) n FROM restaurants GROUP BY source"
        ).fetchall()
        snapshots = conn.execute("SELECT COUNT(*) FROM review_snapshots").fetchone()[0]
        latest_snap = conn.execute(
            "SELECT MAX(snapshot_date) FROM review_snapshots"
        ).fetchone()[0]
    return {
        "total_restaurants": total,
        "by_source": {r["source"]: r["n"] for r in by_source},
        "total_snapshots": snapshots,
        "latest_snapshot": latest_snap,
    }


if __name__ == "__main__":
    init_db()
    print(get_stats())
