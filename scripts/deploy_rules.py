#!/usr/bin/env python3
"""
ChefMinistry — Deploy Firestore rules
รัน: python deploy_rules.py            (deploy site/firestore.rules)
     python deploy_rules.py --show     (ดู rules ที่ใช้อยู่จริงบน production)
     python deploy_rules.py --dry-run  (แค่ compile ตรวจ syntax ไม่ publish)

ใช้ service account เดิม (scraper/firebase_admin_key.json) — ไม่ต้องเข้า Console
หมายเหตุ: SA มีสิทธิ์ create ruleset + patch release แต่ "ไม่มี" สิทธิ์ Rules Test API
(ถ้าอยากใช้ :test ต้องให้ role roles/firebaserules.admin เพิ่มใน IAM)

⚠️ หลัง deploy ทุกครั้ง ให้เช็คว่าของเดิมไม่พัง อย่างน้อย:
   - scheduled task เขียน cm_fb_digest ด้วย write key ได้
   - สมาชิกเสนอร้าน (cm_suggestions) ได้
   - สมาชิกทั่วไป "เขียน cm_subscriptions ของตัวเองไม่ได้"  ← หัวใจ paywall
"""
import argparse, json, pathlib, sys, time, urllib.parse, urllib.request, urllib.error

HERE = pathlib.Path(__file__).parent
SA_FILE = HERE / "scraper" / "firebase_admin_key.json"
RULES_FILE = HERE / "site" / "firestore.rules"


def access_token(sa, scope="https://www.googleapis.com/auth/cloud-platform"):
    try:
        import jwt  # pyjwt
    except ImportError:
        sys.exit("❌ ต้องติดตั้งก่อน: pip install pyjwt cryptography")
    now = int(time.time())
    assertion = jwt.encode({
        "iss": sa["client_email"], "scope": scope,
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now, "exp": now + 3600,
    }, sa["private_key"], algorithm="RS256")
    data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion}).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    return json.load(urllib.request.urlopen(req))["access_token"]


def api(url, token, data=None, method="GET"):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, method=method)
    req.add_header("Authorization", "Bearer " + token)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        return json.load(urllib.request.urlopen(req, timeout=45))
    except urllib.error.HTTPError as e:
        sys.exit(f"❌ {method} {url.split('/v1/')[-1]} → {e.code}\n{e.read().decode()[:500]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not SA_FILE.exists():
        sys.exit(f"❌ ไม่พบ {SA_FILE}")
    sa = json.loads(SA_FILE.read_text(encoding="utf-8"))
    pid = sa["project_id"]
    tok = access_token(sa)

    if args.show:
        rel = api(f"https://firebaserules.googleapis.com/v1/projects/{pid}/releases/cloud.firestore", tok)
        rs = api(f"https://firebaserules.googleapis.com/v1/{rel['rulesetName']}", tok)
        print(f"# ruleset: {rel['rulesetName']}\n")
        print(rs["source"]["files"][0]["content"])
        return

    src = RULES_FILE.read_text(encoding="utf-8")
    print(f"📄 {RULES_FILE.name} ({len(src)} ตัวอักษร) → project {pid}")

    # สร้าง ruleset (ขั้นนี้ compile ให้ด้วย — syntax ผิดจะ error ที่นี่)
    rs = api(f"https://firebaserules.googleapis.com/v1/projects/{pid}/rulesets", tok,
             {"source": {"files": [{"name": "firestore.rules", "content": src}]}}, "POST")
    print(f"✅ compile ผ่าน — ruleset {rs['name'].split('/')[-1]}")

    if args.dry_run:
        print("🔎 dry-run — ไม่ publish")
        return

    rel = api(f"https://firebaserules.googleapis.com/v1/projects/{pid}/releases/cloud.firestore", tok,
              {"release": {"name": f"projects/{pid}/releases/cloud.firestore",
                           "rulesetName": rs["name"]}}, "PATCH")
    print(f"🚀 publish แล้ว — มีผลทันที ({rel.get('updateTime')})")


if __name__ == "__main__":
    main()
