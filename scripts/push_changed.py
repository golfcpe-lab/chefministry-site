#!/usr/bin/env python3
"""
ChefMinistry — Push ONLY the files changed in this batch (2026-07-25)
รัน: python push_changed.py

ทำไมไม่ใช้ push_to_github.py:
  push_to_github.py push ไฟล์ทั้งชุด (site 30+ ไฟล์) รวมไฟล์ HTML ที่เราไม่ได้แก้
  ซึ่งบน repo ถูก pipeline ประทับ ?v= ใหม่ทุกคืน (ล่าสุด 202607251732) แต่สำเนา
  ในเครื่องยังเป็นของ 7/12–7/13 → push ทับแล้ว browser อาจดึง data.js เวอร์ชันเก่า
  จาก HTTP cache จนกว่า pipeline จะประทับใหม่คืนถัดไป
  สคริปต์นี้จึงแตะเฉพาะ 7 ไฟล์ที่แก้จริง (index/listing ได้ stamp ใหม่แล้ว)

ตรวจก่อน push ทุกไฟล์: .py ต้อง compile ผ่าน / .html ต้องจบ </html> / .js ต้อง
decode utf-8 ได้ — ไฟล์ไหนไม่ผ่านจะถูกข้าม (ไม่ทับของดีบน repo)
"""
import base64, datetime, json, pathlib, urllib.request, urllib.error

REPO = "golfcpe-lab/chefministry-site"
HERE = pathlib.Path(__file__).parent

# (local path, repo path)
FILES = [
    ("site/index.html",          "index.html"),
    ("site/listing.html",        "listing.html"),
    ("site/js/dataService.js",   "js/dataService.js"),
    ("site/sw.js",               "sw.js"),
    ("scraper/area_fix.py",      "scripts/scraper/area_fix.py"),
    ("scraper/canonical.py",     "scripts/scraper/canonical.py"),
    ("scraper/scrape_gmaps.py",  "scripts/scraper/scrape_gmaps.py"),
]

MESSAGE = ("feat: segment tabs (street food แยกกลุ่ม) + trend floor 150 reviews/15 new "
           "+ sync ชื่อ-ย่านจาก GMaps + Category Heat ไม่ค้างที่ 0%")

token_file = HERE / ".github_token.txt"
if not token_file.exists():
    token_file = HERE / ".github_token"
if not token_file.exists():
    raise SystemExit("❌  ไม่พบ .github_token.txt")
TOKEN = token_file.read_text().strip()

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "ChefMinistry-Bot",
    "Accept": "application/vnd.github+json",
}


def gh(url, method="GET", body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read() or b"{}")


def safe(p: pathlib.Path) -> bool:
    try:
        raw = p.read_bytes()
        txt = raw.decode("utf-8")
        if p.suffix.lower() in (".html", ".htm") and not txt.rstrip().endswith("</html>"):
            print(f"⛔  {p.name}: ไม่จบด้วย </html> — ไฟล์อาจขาด")
            return False
        if p.suffix.lower() == ".py":
            compile(txt, str(p), "exec")
    except Exception as e:
        print(f"⛔  {p.name}: {str(e)[:80]}")
        return False
    return True


print(f"\n{'='*58}\n  Push changed files → {REPO}\n{'='*58}\n")

ok, skipped = 0, 0
for local_rel, gh_path in FILES:
    p = HERE / local_rel
    if not p.exists():
        print(f"⚠️   ไม่พบ {local_rel} — ข้าม\n")
        skipped += 1
        continue
    if not safe(p):
        print(f"⛔  ข้าม {gh_path}\n")
        skipped += 1
        continue
    content = base64.b64encode(p.read_bytes()).decode()
    url = f"https://api.github.com/repos/{REPO}/contents/{gh_path}"
    sha = None
    try:
        sha = gh(url).get("sha")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"    ⚠️  ดึง SHA ไม่ได้ ({e.code})")
    body = {"message": MESSAGE, "content": content}
    if sha:
        body["sha"] = sha
    try:
        res = gh(url, "PUT", body)
        print(f"✅  {gh_path}  →  commit {res['commit']['sha'][:7]}")
        ok += 1
    except urllib.error.HTTPError as e:
        print(f"❌  {gh_path}: HTTP {e.code} {e.read().decode(errors='replace')[:160]}")

# ── สั่ง scraper workflow ให้ regen data.js (จะได้มี field segment) ──
if ok:
    try:
        gh(f"https://api.github.com/repos/{REPO}/actions/workflows/scraper.yml/dispatches",
           "POST", {"ref": "main"})
        print("\n🚀  สั่งรัน scraper.yml แล้ว — data.js รอบใหม่จะมี field segment (~5-6 นาที)")
    except Exception as e:
        print(f"\n⚠️  dispatch workflow ไม่สำเร็จ: {str(e)[:120]}")
        print("    สั่งมือได้ที่ GitHub → Actions → ChefMinistry Scraper → Run workflow")

print(f"\n{'='*58}")
print(f"  push สำเร็จ {ok} ไฟล์ · ข้าม {skipped}")
print(f"  รอ GitHub Pages build ~2-4 นาที แล้วเปิด chefministry.com (Ctrl+Shift+R)")
print(f"{'='*58}\n")
