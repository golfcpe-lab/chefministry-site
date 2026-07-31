#!/usr/bin/env python3
"""
ChefMinistry — Sync KML ขึ้น Google Drive
อัปเดตเนื้อไฟล์ .kml ในโฟลเดอร์ Drive ที่ใช้เป็นต้นทางของ Google My Maps
ให้ตรงกับข้อมูลล่าสุด เพื่อให้ตอน reimport เข้า My Maps ได้ของใหม่เสมอ

ทำไมทำได้โดยไม่ต้อง OAuth ของผู้ใช้:
  โฟลเดอร์สร้างโดย service account (metadata ไม่กินโควตา) แล้วแชร์ให้เจ้าของบัญชี
  ไฟล์ที่ผู้ใช้อัปโหลดเข้ามาจึงเป็นของผู้ใช้ (กินโควตาผู้ใช้) แต่ SA มีสิทธิ์แก้ไข
  → SA "อัปเดตเนื้อไฟล์" ได้ (files.update) แม้จะ "สร้างไฟล์ใหม่" ไม่ได้

Usage:
  python sync_drive_maps.py                    # sync ทุกไฟล์ใน maps_masters
  python sync_drive_maps.py --dry-run
  DRIVE_FOLDER_ID=... python sync_drive_maps.py
"""
import argparse, json, os, pathlib, sys, time, urllib.parse, urllib.request, urllib.error

HERE = pathlib.Path(__file__).parent
SA_FILE = HERE / "firebase_admin_key.json"
DEFAULT_DIR = HERE.parent / "maps_masters"
# โฟลเดอร์ "ChefMinistry Map Data" (SA เป็นเจ้าของ, เจ้าของบัญชีเป็นเอดิเตอร์)
FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "1xSE966_NVxIJrkNHfD3LMcakU6SDkg8P")


def load_sa():
    """อ่าน service account จาก env (CI) หรือไฟล์ (เครื่อง local)"""
    raw = os.environ.get("GOOGLE_SA_JSON", "").strip()
    if raw:
        return json.loads(raw)
    if SA_FILE.exists():
        return json.loads(SA_FILE.read_text(encoding="utf-8"))
    sys.exit("❌ ไม่พบ credential — ตั้ง env GOOGLE_SA_JSON หรือวาง firebase_admin_key.json")


def access_token():
    try:
        import jwt
    except ImportError:
        sys.exit("❌ ต้องติดตั้งก่อน: pip install pyjwt cryptography")
    sa = load_sa()
    now = int(time.time())
    assertion = jwt.encode({
        "iss": sa["client_email"], "scope": "https://www.googleapis.com/auth/drive",
        "aud": "https://oauth2.googleapis.com/token", "iat": now, "exp": now + 3600,
    }, sa["private_key"], algorithm="RS256")
    data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion}).encode()
    return json.load(urllib.request.urlopen(
        urllib.request.Request("https://oauth2.googleapis.com/token", data=data)))["access_token"]


def api(url, tok, data=None, method="GET", content_type="application/json"):
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + tok)
    if data is not None:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            body = r.read()
            return json.loads(body) if body else {"ok": True}
    except urllib.error.HTTPError as e:
        return {"ERR": e.code, "msg": e.read().decode(errors="replace")[:300]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(DEFAULT_DIR))
    ap.add_argument("--folder", default=FOLDER_ID)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src = pathlib.Path(args.dir)
    if not src.exists():
        sys.exit(f"❌ ไม่พบโฟลเดอร์ {src} — รัน export_maps.py ก่อน")
    tok = access_token()
    q = urllib.parse.quote(f"'{args.folder}' in parents and trashed=false")
    listing = api(f"https://www.googleapis.com/drive/v3/files?q={q}"
                  "&fields=files(id,name,size)&pageSize=200", tok)
    if "ERR" in listing:
        sys.exit(f"❌ อ่านโฟลเดอร์ไม่ได้: {listing}")
    remote = {f["name"]: f["id"] for f in listing.get("files", [])}
    print(f"\n{'='*56}\n  Sync KML → Google Drive ({len(remote)} ไฟล์บน Drive)\n{'='*56}")

    updated = skipped = missing = 0
    for local in sorted(src.glob("*.kml")):
        fid = remote.get(local.name)
        if not fid:
            print(f"  ⚠️  {local.name}: ยังไม่มีบน Drive — อัปโหลดครั้งแรกต้องทำจากบัญชีผู้ใช้")
            missing += 1
            continue
        data = local.read_bytes()
        if args.dry_run:
            print(f"  [dry-run] {local.name} ({len(data)//1024} KB)")
            continue
        res = api(f"https://www.googleapis.com/upload/drive/v3/files/{fid}"
                  "?uploadType=media&fields=id,name,size,modifiedTime",
                  tok, data, "PATCH", "application/vnd.google-earth.kml+xml")
        if "ERR" in res:
            print(f"  ❌ {local.name}: {res['ERR']} {res['msg'][:90]}")
        else:
            print(f"  ✅ {local.name} → {int(res.get('size', 0))//1024} KB")
            updated += 1

    print(f"\n  อัปเดต {updated} · ข้าม {skipped} · ยังไม่มีบน Drive {missing}")
    print("  ℹ️  ข้อมูลใน Google My Maps จะเปลี่ยนก็ต่อเมื่อกด reimport เลเยอร์")
    print(f"{'='*56}\n")


if __name__ == "__main__":
    main()
