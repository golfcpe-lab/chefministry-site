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
    ("css/style.css",           "css/style.css"),
    ("js/data.js",              "js/data.js"),
]

# ── scripts ที่อยู่ใน root (ไม่ใช่ใน site/) ────────────────────────────────────
# หมายเหตุ: ไม่รวม .env และ .github_token.txt เพราะเป็นข้อมูลลับ
ROOT_FILES = [
    ("push_to_github.py",  "scripts/push_to_github.py"),
    ("weekly_summary.py",  "scripts/weekly_summary.py"),
]

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
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

today   = datetime.date.today().strftime("%Y-%m-%d")
message = f"update: accuracy fixes, GA4 tracking, roadmap Phase 3 ({today})"

print(f"\n{'='*55}")
print(f"  ChefMinistry → Push to GitHub")
print(f"  Repo: {REPO}")
print(f"{'='*55}\n")

def push_file(local_file, gh_path):
    if not local_file.exists():
        print(f"⚠️   ไม่พบไฟล์ {local_file.name} — ข้ามไป")
        return
    file_bytes = local_file.read_bytes()
    encoded    = base64.b64encode(file_bytes).decode()
    print(f"📄  {gh_path}  ({len(file_bytes):,} bytes)")
    url = f"https://api.github.com/repos/{REPO}/contents/{gh_path}"
    try:
        sha = gh_request(url)["sha"]
        print(f"    SHA ปัจจุบัน: {sha[:7]}…")
    except:
        print(f"    ไม่พบไฟล์ใน repo (จะสร้างใหม่)")
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

print("── Site files ──────────────────────────────────────")
for local_rel, gh_path in SITE_FILES:
    push_file(HERE / "site" / local_rel, gh_path)

print("── Scripts ─────────────────────────────────────────")
for local_rel, gh_path in ROOT_FILES:
    push_file(HERE / local_rel, gh_path)

print(f"{'='*55}")
print(f"  เสร็จสิ้น — รอ 1-2 นาทีแล้วเปิด chefministry.com")
print(f"{'='*55}\n")
