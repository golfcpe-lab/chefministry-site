"""
ChefMinistry — FB Digest Injector
อ่าน fb_digest.json (จาก Cowork scheduled task) แล้ว inject เข้า data.js เป็น:
  1. CM_FB_DIGEST  — const ใหม่สำหรับ "New This Week" tab
  2. weeklyHighlight — อัปเดตจาก top entry ของ digest

Usage:
  python inject_fb_digest.py               # inject จาก fb_digest.json ใน folder นี้
  python inject_fb_digest.py --dry-run     # แสดงผลโดยไม่แก้ไขไฟล์
"""
import json, re, pathlib, argparse, datetime, sys, os

HERE     = pathlib.Path(__file__).parent
REPO_ROOT = HERE.parent.parent  # scripts/scraper/ → root

# รองรับทั้ง local path และ GitHub Actions path
DIGEST_FILE = HERE / "fb_digest.json"
DATA_JS     = pathlib.Path(os.environ.get("DATA_FILE",
              str(REPO_ROOT / "js" / "data.js")))

CUISINE_EMOJI = {
    "italian": "🍕", "japanese": "🍣", "thai": "🌶️", "coffee": "☕",
    "cafe": "☕", "nordic": "🧊", "french": "🥐", "korean": "🥢",
    "indian": "🍛", "chinese": "🥟", "seafood": "🦞", "steak": "🥩",
    "steakhouse": "🥩", "omakase": "🍱", "ramen": "🍜", "pizza": "🍕",
    "bbq": "🔥", "vegan": "🌱", "vegetarian": "🌿", "brunch": "🍳",
    "dessert": "🍰", "bakery": "🥐", "bar": "🍸", "fusion": "✨",
}


def emoji_for(cuisine: str) -> str:
    return CUISINE_EMOJI.get((cuisine or "").lower(), "🍽️")


def area_norm(raw: str) -> str:
    """ทำ area ให้ clean ขึ้น"""
    if not raw:
        return "Bangkok"
    # ตัด "Bangkok /" prefix ถ้ามี
    raw = re.sub(r'^Bangkok\s*/\s*', '', raw.strip())
    return raw.strip()


def load_digest(path: pathlib.Path) -> dict:
    if not path.exists():
        sys.exit(f"❌ ไม่พบ {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        sys.exit(f"❌ อ่าน {path.name} ไม่ได้: {e}")


def build_cm_records(digest: dict) -> list:
    """แปลง digest entries → CM_FB_DIGEST records สำหรับ web"""
    today = digest.get("digest_date", datetime.date.today().isoformat())
    week  = digest.get("week_label", "")
    records = []

    for i, e in enumerate(digest.get("entries", [])):
        if e.get("is_watchlist"):
            continue  # ไม่เอา watch-list เข้า web

        name     = e.get("name", "").strip()
        etype    = e.get("type", "Restaurant")
        city     = e.get("city", "Bangkok")
        area     = area_norm(e.get("area", ""))
        cuisine  = e.get("cuisine", "Other")
        desc     = e.get("description", "")
        src_url  = e.get("source_url", "")
        src_name = e.get("source_name", "")

        if not name:
            continue

        record = {
            "id":           f"fb_{today}_{i:02d}",
            "name":         name,
            "cuisine":      cuisine,
            "type":         etype.lower().replace(" ", "-"),
            "area":         area,
            "city":         city,
            "emoji":        emoji_for(cuisine),
            "description":  desc,
            "sourceUrl":    src_url,
            "sourceName":   src_name,
            "weekLabel":    week,
            "digestDate":   today,
            "isNew":        True,
            # ฟิลด์ที่ dataService.js ต้องการ
            "trendVelocity": "rising",
            "trendBadge":    "🆕 New",
            "trend_label":   "New Opening",
            "signalStrength": "new",
            "signalCount":   1,
            "overlapSignal": 0,
            "totalReviews":  0,
            "tags":          [cuisine, area, "New Opening"],
            "occasions":     ["casual", "special"],
            "bookingLinks":  {"googlemaps": "#"},
            "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0},
            "recentReviewers": [],
            "cmNote":        f"เปิดใหม่ {week} — {desc[:80]}",
        }
        records.append(record)

    return records


def inject_cm_fb_digest(js_text: str, records: list, digest: dict) -> str:
    """Inject CM_FB_DIGEST constant เข้า data.js"""
    today     = digest.get("digest_date", datetime.date.today().isoformat())
    week      = digest.get("week_label", "")
    trend_note = digest.get("trend_note", "")

    json_str = json.dumps(records, ensure_ascii=False)
    meta_str = json.dumps({
        "digestDate": today,
        "weekLabel":  week,
        "trendNote":  trend_note,
        "count":      len(records),
    }, ensure_ascii=False)

    new_block = (
        f"\n// -- FB Digest (injected by inject_fb_digest.py) ---\n"
        f"const CM_FB_DIGEST_META = {meta_str};\n"
        f"const CM_FB_DIGEST = {json_str};\n"
    )

    # ถ้ามีอยู่แล้ว → replace
    marker = "// -- FB Digest (injected by inject_fb_digest.py)"
    idx = js_text.find(marker)
    if idx != -1:
        # ตัดจาก marker ถึงท้ายไฟล์ แล้วใส่ใหม่
        return js_text[:idx] + new_block
    else:
        # append ท้ายไฟล์
        return js_text.rstrip() + "\n" + new_block


def update_weekly_highlight(js_text: str, top: dict, digest: dict) -> str:
    """อัปเดต weeklyHighlight ด้วย top entry จาก digest"""
    name       = top.get("name", "")
    desc_raw   = top.get("description", "")
    week       = digest.get("week_label", "")
    trend_note = digest.get("trend_note", "")

    # สร้าง title และ desc
    emoji = emoji_for(top.get("cuisine", ""))
    area  = area_norm(top.get("area", ""))
    new_title = f"{emoji} {name} — ร้านเปิดใหม่ที่น่าจับตา"[:60]
    # ตัด desc_raw ก่อนประกอบ เพื่อไม่ให้ suffix "(week)" ถูกตัดกลางคำ
    # (เคยเกิด: desc[:200] ตัดเหลือ "(Week of A" ค้างบนหน้าเว็บ)
    suffix = f" ({week})" if week else ""
    max_raw = 200 - len(suffix)
    if len(desc_raw) > max_raw:
        desc_raw = desc_raw[:max_raw - 1].rsplit(" ", 1)[0] + "…"
    new_desc = f"{desc_raw}{suffix}"
    if trend_note and len(new_desc) + len(trend_note) + 3 <= 200:
        new_desc += f" | {trend_note}"

    # Replace title
    new_text = re.sub(
        r'(weeklyHighlight\s*:\s*\{[^}]*title\s*:\s*")[^"]*(")',
        lambda m: f'{m.group(1)}{new_title}{m.group(2)}',
        js_text, flags=re.DOTALL
    )
    # Replace desc
    new_text = re.sub(
        r'(weeklyHighlight\s*:\s*\{[^}]*desc\s*:\s*")[^"]*(")',
        lambda m: f'{m.group(1)}{new_desc[:200]}{m.group(2)}',
        new_text, flags=re.DOTALL
    )
    # Replace / add restaurant field
    if re.search(r'weeklyHighlight\s*:\s*\{[^}]*restaurant\s*:', new_text, re.DOTALL):
        new_text = re.sub(
            r'(weeklyHighlight\s*:\s*\{[^}]*restaurant\s*:\s*")[^"]*(")',
            lambda m: f'{m.group(1)}{name}{m.group(2)}',
            new_text, flags=re.DOTALL
        )
    else:
        new_text = re.sub(
            r'(weeklyHighlight\s*:\s*\{[^}]*desc\s*:\s*"[^"]*")',
            lambda m: f'{m.group(0)}, restaurant: "{name}"',
            new_text, flags=re.DOTALL
        )

    return new_text


def main():
    parser = argparse.ArgumentParser(description="ChefMinistry FB Digest Injector")
    parser.add_argument("--dry-run", action="store_true", help="แสดงผลโดยไม่แก้ไขไฟล์")
    parser.add_argument("--digest", default=str(DIGEST_FILE), help="path to fb_digest.json")
    args = parser.parse_args()

    digest_path = pathlib.Path(args.digest)
    print(f"\n{'='*55}")
    print(f"  ChefMinistry FB Digest Injector")
    print(f"{'='*55}")

    # 1. Load digest
    print(f"\n[1] อ่าน {digest_path.name}...")
    digest = load_digest(digest_path)
    entries = [e for e in digest.get("entries", []) if not e.get("is_watchlist")]
    print(f"    พบ {len(entries)} entries (ไม่รวม watch-list)")
    print(f"    Week: {digest.get('week_label','?')}")
    if digest.get("trend_note"):
        print(f"    Trend: {digest['trend_note']}")

    if not entries:
        print("    ⚠️  ไม่มี entry — ยกเลิก")
        return

    # 2. Build records
    print(f"\n[2] แปลงเป็น CM_FB_DIGEST records...")
    records = build_cm_records(digest)
    print(f"    สร้างได้ {len(records)} records")

    # 3. Load data.js
    if not DATA_JS.exists():
        print(f"    ❌ ไม่พบ {DATA_JS}")
        return
    print(f"\n[3] อ่าน data.js ({DATA_JS})...")
    js_text = DATA_JS.read_text(encoding="utf-8")

    # 4. Inject CM_FB_DIGEST
    print(f"\n[4] Inject CM_FB_DIGEST...")
    js_text = inject_cm_fb_digest(js_text, records, digest)

    # 5. Update weeklyHighlight
    top = entries[0]
    print(f"\n[5] อัปเดต weeklyHighlight → {top['name']}")
    js_text = update_weekly_highlight(js_text, top, digest)

    # 6. Write
    if args.dry_run:
        print(f"\n[DRY RUN] ไม่บันทึกไฟล์ — แสดง 10 บรรทัดสุดท้าย:")
        for line in js_text.splitlines()[-10:]:
            print(f"  {line}")
    else:
        DATA_JS.write_text(js_text, encoding="utf-8")
        print(f"    ✅ บันทึก {DATA_JS.name} แล้ว")

    print(f"\n{'='*55}")
    print(f"  เสร็จ! {len(records)} ร้านใหม่ inject แล้ว")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
