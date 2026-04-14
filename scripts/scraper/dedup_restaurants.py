"""
ChefMinistry — Duplicate Restaurant Cleaner

ตรวจและลบร้านซ้ำใน DB โดย:
  1. ชื่อเหมือนกัน (case-insensitive, trim whitespace)
  2. gmaps_place_id เหมือนกัน
  3. ชื่อคล้ายกัน (fuzzy match ≥ 85%) — optional ด้วย --fuzzy

หลักการเก็บ: ถ้าซ้ำ จะเก็บ row ที่ข้อมูลครบกว่า (มี source / มี gmaps_place_id / มี snapshot)
             แล้วลบอีก row ออก

วิธีรัน:
  python dedup_restaurants.py              # ตรวจ + ถามยืนยัน
  python dedup_restaurants.py --dry-run    # แค่รายงาน ไม่ลบ
  python dedup_restaurants.py --auto       # ลบทันทีโดยไม่ถาม
  python dedup_restaurants.py --fuzzy      # รวม fuzzy match ด้วย
"""
import argparse, sqlite3, shutil, pathlib, re
from datetime import datetime
from collections import defaultdict

DB_PATH = pathlib.Path(__file__).parent / "chefministry_data.db"


def backup_db():
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = DB_PATH.with_suffix(f".bak_{ts}")
    shutil.copy(str(DB_PATH), str(bak))
    print(f"  💾 Backup: {bak.name}")
    return bak


def get_all_restaurants(conn):
    return conn.execute("""
        SELECT
            r.id, r.name, r.source, r.area, r.cuisine,
            r.gmaps_place_id, r.url, r.address, r.first_seen,
            COUNT(s.id) AS snap_count
        FROM restaurants r
        LEFT JOIN review_snapshots s ON s.restaurant_id = r.id
        GROUP BY r.id
        ORDER BY r.name
    """).fetchall()


def score_row(row) -> int:
    """คะแนนความครบของข้อมูล — สูงกว่า = เก็บไว้"""
    s = 0
    if row["gmaps_place_id"]: s += 10
    if row["source"] != "gmaps_bookmark": s += 5   # prefer wongnai/scraped over manual
    if row["cuisine"]:    s += 2
    if row["area"]:       s += 2
    if row["address"]:    s += 1
    if row["url"]:        s += 1
    s += min(row["snap_count"] * 2, 20)             # snapshot history = valuable
    return s


def normalize_name(name: str) -> str:
    """ทำให้ชื่อเป็น canonical สำหรับเปรียบเทียบ"""
    if not name:
        return ""
    n = name.strip().lower()
    # ลบ suffix ที่มักเพิ่มมา เช่น " ทองหล่อ" ถ้าอยากเปรียบเทียบแบบ strict ไม่ต้องลบ
    # สำหรับ exact match แค่ lowercase + strip
    return n


def fuzzy_ratio(a: str, b: str) -> float:
    """Simple similarity ratio (SequenceMatcher)"""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()


def find_duplicates(rows, use_fuzzy: bool = False, fuzzy_threshold: float = 0.85):
    """คืน list ของ groups (แต่ละ group = list ของ rows ที่ซ้ำกัน)"""
    groups = []
    visited = set()  # row ids ที่จัดกลุ่มแล้ว

    # 1) ชื่อเหมือน (exact, normalized)
    by_name = defaultdict(list)
    for r in rows:
        key = normalize_name(r["name"])
        by_name[key].append(r)
    for key, grp in by_name.items():
        if len(grp) > 1:
            groups.append(("exact_name", key, grp))
            for r in grp:
                visited.add(r["id"])

    # 2) gmaps_place_id เหมือน (ไม่รวม None)
    by_pid = defaultdict(list)
    for r in rows:
        if r["gmaps_place_id"]:
            by_pid[r["gmaps_place_id"]].append(r)
    for pid, grp in by_pid.items():
        if len(grp) > 1:
            # อาจจะซ้ำกับกลุ่ม name แล้ว — เพิ่มเฉพาะ ids ใหม่
            ids_in_grp = {r["id"] for r in grp}
            if not ids_in_grp.issubset(visited):
                groups.append(("same_place_id", pid, grp))
                visited.update(ids_in_grp)

    # 3) Fuzzy (optional)
    if use_fuzzy:
        remaining = [r for r in rows if r["id"] not in visited]
        names_r = [(normalize_name(r["name"]), r) for r in remaining]
        used = set()
        for i, (na, ra) in enumerate(names_r):
            if ra["id"] in used:
                continue
            grp = [ra]
            for j, (nb, rb) in enumerate(names_r):
                if i == j or rb["id"] in used:
                    continue
                if fuzzy_ratio(na, nb) >= fuzzy_threshold:
                    grp.append(rb)
            if len(grp) > 1:
                groups.append(("fuzzy_name", na, grp))
                for r in grp:
                    used.add(r["id"])

    return groups


def pick_keeper(grp: list) -> tuple:
    """เลือก row ที่จะเก็บ (score สูงสุด) และ rows ที่จะลบ"""
    scored = sorted(grp, key=score_row, reverse=True)
    keeper = scored[0]
    to_del = scored[1:]
    return keeper, to_del


def delete_restaurants(conn, ids_to_delete: list[str]):
    """ลบร้านและ snapshots ของมัน"""
    for rid in ids_to_delete:
        conn.execute("DELETE FROM review_snapshots WHERE restaurant_id = ?", (rid,))
        conn.execute("DELETE FROM restaurants WHERE id = ?", (rid,))


def run(dry_run: bool, auto: bool, use_fuzzy: bool):
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    rows  = get_all_restaurants(conn)
    total = len(rows)
    print(f"\n  🔍 ตรวจ duplicate ใน {total} ร้าน...\n")

    groups = find_duplicates(rows, use_fuzzy=use_fuzzy)

    if not groups:
        print("  ✅ ไม่พบ duplicate เลย — DB สะอาดดี!")
        conn.close()
        return

    # รายงาน
    all_to_delete = []
    print(f"  พบ {len(groups)} กลุ่มที่ซ้ำกัน:\n")
    for reason, key, grp in groups:
        keeper, to_del = pick_keeper(grp)
        label = {
            "exact_name":    "ชื่อเหมือน",
            "same_place_id": "place_id ซ้ำ",
            "fuzzy_name":    "ชื่อคล้าย",
        }.get(reason, reason)

        print(f"  [{label}] key={key!r}")
        for r in grp:
            tag = "✅ KEEP" if r["id"] == keeper["id"] else "❌ DELETE"
            print(f"    {tag}  id={r['id']:40s}  source={r['source']:15s}  area={r['area'] or '-':12s}  snaps={r['snap_count']}")
        print()

        all_to_delete.extend([r["id"] for r in to_del])

    print(f"  รวมจะลบ: {len(all_to_delete)} ร้าน")

    if dry_run:
        print("  🔍 DRY RUN — ไม่ได้ลบจริง\n")
        conn.close()
        return

    # ยืนยัน
    if not auto:
        confirm = input(f"\n  ลบ {len(all_to_delete)} ร้านเลยไหม? (y/N) ").strip().lower()
        if confirm != "y":
            print("  ยกเลิก\n")
            conn.close()
            return

    # Backup ก่อน
    backup_db()

    delete_restaurants(conn, all_to_delete)
    conn.commit()

    remaining = conn.execute("SELECT COUNT(*) FROM restaurants").fetchone()[0]
    conn.close()

    print(f"""
  ── สรุป ──────────────────────────────────────────
  ❌ ลบออก  : {len(all_to_delete)} ร้าน
  ✅ คงเหลือ : {remaining} ร้าน
  💾 Backup DB ไว้แล้ว (ก่อน delete)
""")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Dedup ChefMinistry DB")
    ap.add_argument("--dry-run", action="store_true", help="แสดงรายงาน ไม่ลบจริง")
    ap.add_argument("--auto",    action="store_true", help="ลบทันทีไม่ถาม")
    ap.add_argument("--fuzzy",   action="store_true", help="รวม fuzzy match ด้วย (≥85%)")
    args = ap.parse_args()

    run(dry_run=args.dry_run, auto=args.auto, use_fuzzy=args.fuzzy)
