#!/usr/bin/env python3
"""
ChefMinistry — Map Export (Google My Maps)
สร้างไฟล์ .kml / .csv แยกตามหมวดอาหาร ให้สมาชิกโหลดไปเปิดใน Google My Maps
แล้วดูต่อในแอป Google Maps (Saved → Maps)

ทำไมต้อง My Maps: แอป Google Maps import ไฟล์เองไม่ได้ ต้อง import ที่
mymaps.google.com ก่อน (เว็บ/มือถือก็ได้) แล้วแผนที่จะไปโผล่ในแอปอัตโนมัติ

ข้อจำกัดที่ออกแบบตาม:
  - 1 แผนที่ = 10 layer → จัดหมวดไม่เกิน 10 กลุ่ม (KML 1 ไฟล์ = 1 folder ต่อหมวด)
  - 2,000 จุด/layer, 10,000 จุด/แผนที่ → ปัจจุบัน ~600 จุด สบายมาก

Usage:
  python export_maps.py                      # เขียนลง <repo>/downloads
  python export_maps.py --out ../site/downloads
  MAPS_DIR=/path/to/downloads python export_maps.py
"""
import argparse, csv, json, os, pathlib, re, datetime

HERE = pathlib.Path(__file__).parent
DEFAULT_OUT = pathlib.Path(os.environ.get("MAPS_DIR", str(HERE.parent / "site" / "downloads")))
EXPORT_JSON = HERE / "export_restaurants.json"

# ── เกณฑ์คุณภาพ: ไฟล์ต้อง "เปิดแล้วใช้ได้จริง" ไม่ใช่ทุกร้านในฐาน ──────────────
MIN_RATING  = 4.3
MIN_REVIEWS = 50

# ── หมวด (สูงสุด 10 กลุ่ม = 10 layer ของ My Maps) ─────────────────────────────
# (key, ชื่อไฟล์, ชื่อแสดงผล, สี KML (aabbggrr), เงื่อนไข)
GROUPS = [
    ("cafe",      "cafe-matcha",   "☕ คาเฟ่ & มัทฉะ",        "ff3b8cd6"),
    ("finedining","fine-dining",   "🍽️ Fine Dining & Omakase", "ff2b52c9"),
    ("thai",      "thai",          "🇹🇭 อาหารไทย",            "ff4fc3ff"),
    ("noodles",   "noodles",       "🍜 ก๋วยเตี๋ยว & เส้น",     "ff64d19a"),
    ("grill",     "grill-hotpot",  "🥩 ปิ้งย่าง & ชาบู",       "ff4b4bd6"),
    ("japanese",  "japanese",      "🍣 ญี่ปุ่น",               "ffb37cff"),
    ("korean",    "korean",        "🇰🇷 เกาหลี",              "ff7cc0ff"),
    ("chinese",   "chinese",       "🇨🇳 จีน & ติ่มซำ",         "ff3ba7e8"),
    ("western",   "western",       "🍕 ตะวันตก",              "ff8fd14f"),
    ("other",     "other-picks",   "✨ ร้านน่าสนใจอื่นๆ",      "ff9e9e9e"),
]
GROUP_NAMES = {g[0]: g[2] for g in GROUPS}


def group_of(r):
    """จัดร้านเข้ากลุ่ม — เรียงลำดับเงื่อนไขจากเฉพาะเจาะจงไปกว้าง"""
    c = (r.get("cuisine_normalized") or r.get("cuisine") or "").lower()
    seg = r.get("segment") or ""
    if seg == "fine" or "fine dining" in c or "omakase" in c:
        return "finedining"
    if any(k in c for k in ("cafe", "café", "matcha", "bakery", "dessert", "tea", "coffee")):
        return "cafe"
    if any(k in c for k in ("noodle", "ramen", "ก๋วยเตี๋ยว")):
        return "noodles"
    if any(k in c for k in ("yakiniku", "bbq", "hot pot", "hotpot", "suki", "shabu", "grill")):
        return "grill"
    if "korean" in c:
        return "korean"
    if any(k in c for k in ("chinese", "dim sum", "dimsum")):
        return "chinese"
    if any(k in c for k in ("japanese", "sushi", "katsu", "izakaya", "teppan")):
        return "japanese"
    if any(k in c for k in ("italian", "french", "steakhouse", "western", "pizza",
                            "american", "mexican", "burger", "german", "mediterranean", "indian")):
        return "western"
    if any(k in c for k in ("thai", "isaan", "local")):
        return "thai"
    return "other"


# กรอบกรุงเทพ+ปริมณฑลชั้นใน — กันร้านที่ address เขียน "กรุงเทพ" แต่พิกัดจริง
# อยู่ภูเก็ต/ชลบุรี/เพชรบุรี (เจอ 9 ร้านตอนทำไฟล์รอบแรก) หลุดเข้าแผนที่
BKK_BBOX = (13.45, 14.05, 100.25, 100.95)   # lat_min, lat_max, lng_min, lng_max


def in_bangkok(r):
    try:
        lat, lng = float(r["lat"]), float(r["lng"])
    except (TypeError, ValueError, KeyError):
        return False
    la0, la1, ln0, ln1 = BKK_BBOX
    return la0 <= lat <= la1 and ln0 <= lng <= ln1


def is_quality(r):
    if not (r.get("is_restaurant_focus") and r.get("is_bangkok_focus")):
        return False
    if not r.get("lat") or not r.get("lng"):
        return False          # ไม่มีพิกัด = ปักหมุดไม่ได้
    if not in_bangkok(r):
        return False
    return (r.get("rating_gmaps") or 0) >= MIN_RATING and (r.get("totalReviews") or 0) >= MIN_REVIEWS


def esc(s):
    return (str(s or "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def maps_url(r):
    pid = r.get("place_id")
    if pid:
        return f"https://www.google.com/maps/place/?q=place_id:{pid}"
    return r.get("url") or ("https://www.google.com/maps/search/" +
                            (r.get("name") or "").replace(" ", "+"))


def describe(r):
    bits = []
    rating, reviews = r.get("rating_gmaps"), r.get("totalReviews")
    if rating:
        bits.append(f"⭐ {rating:.1f}" + (f" ({int(reviews):,} รีวิว)" if reviews else ""))
    if r.get("cuisine_normalized") or r.get("cuisine"):
        bits.append(r.get("cuisine_normalized") or r.get("cuisine"))
    if r.get("area_normalized") or r.get("area"):
        bits.append(r.get("area_normalized") or r.get("area"))
    if r.get("budgetLabel"):
        bits.append(r["budgetLabel"])
    line = " · ".join(str(b) for b in bits)
    addr = r.get("address") or ""
    return f"{line}\n{addr}\n{maps_url(r)}\nข้อมูลจาก ChefMinistry — chefministry.com"


def kml_placemark(r):
    return (
        "    <Placemark>\n"
        f"      <name>{esc(r.get('name'))}</name>\n"
        f"      <description>{esc(describe(r))}</description>\n"
        "      <ExtendedData>\n"
        f'        <Data name="rating"><value>{r.get("rating_gmaps") or ""}</value></Data>\n'
        f'        <Data name="reviews"><value>{r.get("totalReviews") or ""}</value></Data>\n'
        f'        <Data name="cuisine"><value>{esc(r.get("cuisine_normalized") or r.get("cuisine"))}</value></Data>\n'
        f'        <Data name="area"><value>{esc(r.get("area_normalized") or r.get("area"))}</value></Data>\n'
        f'        <Data name="google_maps"><value>{esc(maps_url(r))}</value></Data>\n'
        "      </ExtendedData>\n"
        f"      <Point><coordinates>{r['lng']},{r['lat']},0</coordinates></Point>\n"
        "    </Placemark>\n"
    )


def kml_document(title, folders):
    """folders = [(ชื่อ, สี, [records])]"""
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<kml xmlns="http://www.opengis.net/kml/2.2">',
           "<Document>",
           f"  <name>{esc(title)}</name>",
           f"  <description>{esc('อัปเดต ' + datetime.date.today().isoformat() + ' — chefministry.com')}</description>"]
    for i, (name, color, rows) in enumerate(folders):
        if not rows:
            continue
        sid = f"cm{i}"
        out.append(f'  <Style id="{sid}"><IconStyle><color>{color}</color>'
                   '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/dining.png</href></Icon>'
                   "</IconStyle></Style>")
        out.append("  <Folder>")
        out.append(f"    <name>{esc(name)}</name>")
        for r in rows:
            out.append(kml_placemark(r).replace(
                "    <Placemark>\n",
                f"    <Placemark>\n      <styleUrl>#{sid}</styleUrl>\n").rstrip("\n"))
        out.append("  </Folder>")
    out.append("</Document></kml>")
    return "\n".join(out)


CSV_COLS = ["Name", "Latitude", "Longitude", "Cuisine", "Area", "Rating",
            "Reviews", "Price", "Address", "GoogleMapsURL"]


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(CSV_COLS)
        for r in rows:
            w.writerow([
                r.get("name"), r.get("lat"), r.get("lng"),
                r.get("cuisine_normalized") or r.get("cuisine"),
                r.get("area_normalized") or r.get("area"),
                r.get("rating_gmaps") or "", r.get("totalReviews") or "",
                r.get("budgetLabel") or "", r.get("address") or "", maps_url(r),
            ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--source", default=str(EXPORT_JSON))
    args = ap.parse_args()

    src = pathlib.Path(args.source)
    if not src.exists():
        raise SystemExit(f"❌ ไม่พบ {src} — รัน export_signals.py ก่อน")
    data = json.loads(src.read_text(encoding="utf-8"))

    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # แจ้งร้านที่พิกัดหลุดกรอบ กทม. — เป็นสัญญาณข้อมูลผิด ควรตามไปแก้ใน DB
    strays = [r for r in data
              if r.get("is_bangkok_focus") and r.get("lat") and r.get("lng") and not in_bangkok(r)]
    if strays:
        print(f"  ⚠️  พิกัดหลุดกรอบกรุงเทพ {len(strays)} ร้าน (ไม่ใส่ในแผนที่): "
              + ", ".join((r.get("name") or "")[:22] for r in strays[:5])
              + (" …" if len(strays) > 5 else ""))

    quality = [r for r in data if is_quality(r)]
    quality.sort(key=lambda r: -((r.get("rating_gmaps") or 0) * (r.get("totalReviews") or 0) ** 0.3))

    buckets = {g[0]: [] for g in GROUPS}
    for r in quality:
        buckets[group_of(r)].append(r)

    print(f"\n{'='*58}\n  ChefMinistry — Map Export ({len(quality)} ร้านผ่านเกณฑ์)\n{'='*58}")

    manifest = {
        "generated": datetime.date.today().isoformat(),
        "criteria": {"minRating": MIN_RATING, "minReviews": MIN_REVIEWS},
        "total": len(quality),
        "groups": [],
    }

    folders = []
    for key, slug, label, color in GROUPS:
        rows = buckets[key]
        if not rows:
            print(f"  ⏭  {label}: 0 ร้าน — ข้าม")
            continue
        kml_path = out_dir / f"chefministry-{slug}.kml"
        csv_path = out_dir / f"chefministry-{slug}.csv"
        kml_path.write_text(kml_document(f"ChefMinistry — {label}", [(label, color, rows)]),
                            encoding="utf-8")
        write_csv(csv_path, rows)
        folders.append((label, color, rows))
        manifest["groups"].append({
            "key": key, "label": label, "count": len(rows),
            "kml": f"downloads/{kml_path.name}", "csv": f"downloads/{csv_path.name}",
            "top": [r.get("name") for r in rows[:3]],
        })
        print(f"  ✅ {label}: {len(rows)} ร้าน → {kml_path.name} + {csv_path.name}")

    # ไฟล์รวม: 1 แผนที่ ทุกหมวดเป็น layer แยก (สูงสุด 10 layer ตามข้อจำกัด My Maps)
    all_kml = out_dir / "chefministry-bangkok-all.kml"
    all_kml.write_text(kml_document("ChefMinistry — ร้านคัดสรรกรุงเทพฯ", folders[:10]),
                       encoding="utf-8")
    manifest["all"] = {"kml": f"downloads/{all_kml.name}", "layers": len(folders[:10]),
                       "count": sum(len(f[2]) for f in folders[:10])}
    print(f"  📦 รวมทุกหมวด → {all_kml.name} ({manifest['all']['count']} จุด / {manifest['all']['layers']} layer)")

    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  📝 manifest.json\n{'='*58}\n")


if __name__ == "__main__":
    main()
