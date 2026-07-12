#!/usr/bin/env python3
"""
ChefMinistry — Push site files to GitHub
รัน: python3 push_to_github.py
"""
import urllib.request, json, base64, datetime, pathlib

REPO = "golfcpe-lab/chefministry-site"

# ── ไฟล์ site/ ที่ต้อง push (relative to site/ folder) ───────────────────────
SITE_FILES = [
    ("index.html",              "index.html"),
    ("listing.html",            "listing.html"),
    ("about.html",              "about.html"),
    ("creator.html",            "creator.html"),
    ("restaurant.html",         "restaurant.html"),
    ("restaurant_partner.html", "restaurant_partner.html"),
    ("contact.html",              "contact.html"),
    ("faq.html",                  "faq.html"),
    ("legal.html",                "legal.html"),
    ("vercel.json",               "vercel.json"),
    ("sitemap.xml",               "sitemap.xml"),
    ("robots.txt",                "robots.txt"),
    ("assets/og-image.png",       "assets/og-image.png"),
    ("css/style.css",              "css/style.css"),
    ("js/safeDataAdapter.js",       "js/safeDataAdapter.js"),
    # ⛔ js/data.js ห้าม push! — เป็นไฟล์ generated โดย pipeline บน GitHub ทุกคืน
    #    push จากเครื่อง = ทับข้อมูลสดด้วยข้อมูลเก่า (เกิดเหตุแล้ว 2026-07-09)
    ("js/dataService.js",        "js/dataService.js"),
    ("js/quickpick.js",          "js/quickpick.js"),
    ("js/creatorbuzz.js",        "js/creatorbuzz.js"),
    ("js/suggest.js",            "js/suggest.js"),
    ("js/microfx.js",            "js/microfx.js"),
    ("js/auth.js",                 "js/auth.js"),
    ("js/firebase-config.js",      "js/firebase-config.js"),
    ("admin.html",                 "admin.html"),
    ("api/add-restaurant.js",      "api/add-restaurant.js"),
    ("api/manage-users.js",        "api/manage-users.js"),
]

# ── scripts ที่อยู่ใน root (ไม่ใช่ใน site/) ────────────────────────────────────
# หมายเหตุ: ไม่รวม .env และ .github_token.txt เพราะเป็นข้อมูลลับ
ROOT_FILES = [
    ("push_to_github.py",         "scripts/push_to_github.py"),
    ("weekly_summary.py",         "scripts/weekly_summary.py"),
    # GitHub Actions workflows
    (".github/workflows/weekly_update.yml", ".github/workflows/weekly_update.yml"),
    (".github/workflows/scraper.yml",       ".github/workflows/scraper.yml"),
    # Scraper suite (ใหม่ — แทนที่ grabfood/lineman/wongnai v1 เดิม)
    ("scraper/config.py",         "scripts/scraper/config.py"),
    ("scraper/db.py",             "scripts/scraper/db.py"),
    ("scraper/run_all.py",        "scripts/scraper/run_all.py"),
    ("scraper/export_signals.py", "scripts/scraper/export_signals.py"),
    ("scraper/requirements.txt",  "scripts/scraper/requirements.txt"),
    ("scraper/scrape_wongnai_v5.py", "scripts/scraper/scrape_wongnai_v5.py"),
    ("scraper/scrape_gmaps.py",      "scripts/scraper/scrape_gmaps.py"),
    ("scraper/seed_discover.py",     "scripts/scraper/seed_discover.py"),
    ("scraper/scrape_youtube.py",    "scripts/scraper/scrape_youtube.py"),
    ("scraper/inject_youtube.py",    "scripts/scraper/inject_youtube.py"),
    ("scraper/canonical.py",         "scripts/scraper/canonical.py"),
    ("scraper/area_fix.py",          "scripts/scraper/area_fix.py"),
    ("scraper/process_suggestions.py", "scripts/scraper/process_suggestions.py"),
    # ⛔ ไฟล์ generated — pipeline บน GitHub เป็นเจ้าของ ห้าม push จากเครื่องเด็ดขาด:
    #    - scraper/export_restaurants.json  (สร้างใหม่ทุกคืนจาก DB บน GitHub)
    #    - scraper/chefministry_data.db     (DB บน GitHub มี snapshot ล่าสุด เครื่องนี้ไม่มี)
    #    - scraper/fb_digest.json           (ส่งผ่าน Firestore แล้ว)
    ("scraper/classify.py",          "scripts/scraper/classify.py"),
    ("scraper/dedup_restaurants.py", "scripts/scraper/dedup_restaurants.py"),
    ("scraper/inject_fb_digest.py",  "scripts/scraper/inject_fb_digest.py"),
]

FILES_TO_DELETE = []  # ไม่มีไฟล์ที่ต้องลบแล้ว

# ── หา token ──────────────────────────────────────────────────────────────────
HERE = pathlib.Path(__file__).parent
token_file = HERE / ".github_token.txt"
if not token_file.exists():
    token_file = HERE / ".github_token"
if not token_file.exists():
    raise SystemExit("❌  ไม่พบ .github_token.txt — ใส่ token ใน Chef IP/.github_token.txt ก่อน")

TOKEN = token_file.read_text().strip()

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Content-Type":  "application/json",
    "User-Agent":    "ChefMinistry-Bot"
}

def gh_request(url, method="GET", body=None):
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(url, data=data, method=method, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode(errors="replace")
        raise Exception(f"HTTP {e.code} {e.reason}: {err_body[:300]}")

today   = datetime.date.today().strftime("%Y-%m-%d")
message = f"chore: manual push ({today})"


# ── SQLite safety guard ───────────────────────────────────────────────────────
# ห้าม push ไฟล์ .db ที่ (1) มี journal ค้าง หรือ (2) integrity check ไม่ผ่าน
# — นี่คือต้นเหตุที่ DB ใน repo เคย corrupt แล้ว pipeline ตายเงียบ 3 เดือน
def sqlite_safe_to_push(local_file: pathlib.Path) -> bool:
    if local_file.suffix != ".db":
        return True
    journal = local_file.with_name(local_file.name + "-journal")
    if journal.exists() and journal.stat().st_size > 0:
        print(f"❌  {local_file.name}: มี journal ค้าง ({journal.name}) — DB อยู่กลาง transaction")
        print(f"    ปิดโปรแกรมที่เปิด DB อยู่ก่อน แล้วรันใหม่")
        return False
    import sqlite3
    try:
        conn = sqlite3.connect(str(local_file))
        result = conn.execute("PRAGMA integrity_check").fetchone()[0]
        conn.close()
    except Exception as e:
        result = str(e)
    if result != "ok":
        print(f"❌  {local_file.name}: integrity check ไม่ผ่าน — {result[:120]}")
        print(f"    ห้าม push DB เสียขึ้น repo (จะทำให้ scraper ตายเงียบ)")
        return False
    return True

print(f"\n{'='*55}")
print(f"  ChefMinistry → Push to GitHub")
print(f"  Repo: {REPO}")
print(f"{'='*55}\n")

def push_file(local_file, gh_path):
    if not local_file.exists():
        print(f"⚠️   ไม่พบไฟล์ {local_file.name} — ข้ามไป")
        return
    if not sqlite_safe_to_push(local_file):
        print(f"⛔  ข้าม {gh_path} เพื่อความปลอดภัย\n")
        return
    file_bytes = local_file.read_bytes()
    encoded    = base64.b64encode(file_bytes).decode()
    print(f"📄  {gh_path}  ({len(file_bytes):,} bytes)")
    url = f"https://api.github.com/repos/{REPO}/contents/{gh_path}"
    try:
        sha = gh_request(url)["sha"]
        print(f"    SHA ปัจจุบัน: {sha[:7]}…")
    except Exception as e:
        if "HTTP 404" in str(e):
            print(f"    ไม่พบไฟล์ใน repo (จะสร้างใหม่)")
        else:
            print(f"    ⚠️  ดึง SHA ไม่ได้: {e}")
        sha = None
    body = {"message": message, "content": encoded}
    if sha:
        body["sha"] = sha
    try:
        result  = gh_request(url, method="PUT", body=body)
        new_sha = result["commit"]["sha"]
        print(f"    ✅  Push สำเร็จ — commit {new_sha[:7]}\n")
    except Exception as e:
        print(f"    ❌  Push ไม่สำเร็จ: {e}\n")

def delete_file(gh_path):
    """ลบไฟล์ออกจาก GitHub repo (ถ้ามีอยู่)"""
    url = f"https://api.github.com/repos/{REPO}/contents/{gh_path}"
    try:
        info = gh_request(url)
        sha  = info["sha"]
        print(f"🗑️   ลบ {gh_path}  (SHA: {sha[:7]}…)")
        gh_request(url, method="DELETE", body={"message": f"remove: ลบ scraper เก่า ({today})", "sha": sha})
        print(f"    ✅  ลบสำเร็จ\n")
    except Exception as e:
        if "HTTP 404" in str(e):
            print(f"⏭️   ข้าม {gh_path} (ไม่มีใน repo)\n")
        else:
            print(f"    ❌  ลบไม่สำเร็จ: {e}\n")

print("── Site files ──────────────────────────────────────")
for local_rel, gh_path in SITE_FILES:
    push_file(HERE / "site" / local_rel, gh_path)

print("── Scripts ─────────────────────────────────────────")
for local_rel, gh_path in ROOT_FILES:
    push_file(HERE / local_rel, gh_path)


print(f"{'='*55}")
print(f"  เสร็จสิ้น — รอ 1-2 นาทีแล้วเปิด chefministry.com")
print(f"{'='*55}\n")
