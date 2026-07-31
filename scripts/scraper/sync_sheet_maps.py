#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChefMinistry — sync map CSVs into Google Sheets (10 ชีต) สำหรับ My Maps reimport

ทำไมต้องมีไฟล์นี้:
  Google My Maps "นำเข้าใหม่" (reimport) เลือกไฟล์ผ่าน picker ที่แสดง "เฉพาะไฟล์สเปรดชีต"
  ไฟล์ KML/CSV ธรรมดาเลือกไม่ได้ → เราจึงเก็บข้อมูลไว้เป็น Google ชีต 1 ไฟล์ต่อ 1 เลเยอร์
  แล้วแต่ละเลเยอร์บนแผนที่ reimport จากชีตของตัวเอง (ทำเดือนละครั้ง กด 3 คลิก)

กลไก:
  ชีตเป็นของ golf.cpe@gmail.com (service account สร้างไฟล์เองไม่ได้ — ไม่มี storage quota)
  แต่วางอยู่ในโฟลเดอร์ที่ service account เป็นเจ้าของ → SA จึงมีสิทธิ์แก้ไข
  อัปเดตเนื้อหาด้วย Drive files.update (uploadType=media, Content-Type: text/csv)
  Drive จะแปลง CSV ทับเนื้อหาชีตเดิมให้อัตโนมัติ — ไม่ต้องใช้ Sheets API

ใช้:
  python scraper/sync_sheet_maps.py
  python scraper/sync_sheet_maps.py --dry-run
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import jwt  # PyJWT

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MASTERS = os.path.join(ROOT, "maps_masters")

SCOPES = "https://www.googleapis.com/auth/drive"

# (ชื่อไฟล์ CSV, Google Sheet ID, ชื่อเลเยอร์บนแผนที่)
SHEETS = [
    ("chefministry-cafe-matcha.csv",  "1wqzyumMsud7xawJLz-sPnVt-gFGHGOJE7p2IAiYWJto", "คาเฟ่ & มัทฉะ"),
    ("chefministry-fine-dining.csv",  "12K44x5wBeX6cwdpGQXC3QDWk1WvHu3pOiQ8oqjvU9yE", "Fine Dining & Omakase"),
    ("chefministry-thai.csv",         "1pN__QM9puprrzrx8XDJwOD7QwNO0V8AnGluEZYCKDFo", "อาหารไทย"),
    ("chefministry-noodles.csv",      "18kRFoNJaDUd04vvRRg03CkFiDZ-WPkXZvbkEqlfw6Y4", "ก๋วยเตี๋ยว & เส้น"),
    ("chefministry-grill-hotpot.csv", "1jx2T01-04u4CRX0JBNdC_GT8ykmV6O7LqzhWhhDk56Y", "ปิ้งย่าง & ชาบู"),
    ("chefministry-japanese.csv",     "1qNa4H2BBIk_9VzhFcZyxhl2syZHkHkRNH6FpKrUX4hw", "ญี่ปุ่น"),
    ("chefministry-korean.csv",       "1cn4FAQcY3nZEAEu1mJlqq5C_55s2s8R7SbSAS6Avhy8", "เกาหลี"),
    ("chefministry-chinese.csv",      "1U7M9cYA3MMjEUVi7dyNyejEWdrMHYVGLx4BsM3UZeO4", "จีน & ติ่มซำ"),
    ("chefministry-western.csv",      "1FzjllL8sqsu-C5HahQ1gXKNMWYZZHAdbAqCkoKRiyWA", "ตะวันตก"),
    ("chefministry-other-picks.csv",  "1nLQGfvVVsxxF97FbUOOre8mkbLHVrhhW82RYk74T2IU", "คัดพิเศษอื่นๆ"),
]


def load_sa():
    raw = os.environ.get("GOOGLE_SA_JSON")
    if raw:
        return json.loads(raw)
    for p in (os.path.join(HERE, "firebase_admin_key.json"),
              os.path.join(ROOT, "firebase_admin_key.json")):
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                return json.load(f)
    raise SystemExit("ไม่พบ service account (GOOGLE_SA_JSON หรือ firebase_admin_key.json)")


def access_token(sa):
    now = int(time.time())
    assertion = jwt.encode(
        {"iss": sa["client_email"], "scope": SCOPES,
         "aud": "https://oauth2.googleapis.com/token", "iat": now, "exp": now + 3600},
        sa["private_key"], algorithm="RS256")
    body = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion}).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=body)
    return json.load(urllib.request.urlopen(req, timeout=30))["access_token"]


def push_csv(token, file_id, data):
    url = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media"
    req = urllib.request.Request(url, data=data, method="PATCH", headers={
        "Authorization": "Bearer " + token, "Content-Type": "text/csv"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--dir", default=MASTERS, help="โฟลเดอร์ที่เก็บไฟล์ CSV")
    args = ap.parse_args()

    src = args.dir
    token = access_token(load_sa())
    ok = fail = total = 0

    for fname, file_id, label in SHEETS:
        path = os.path.join(src, fname)
        if not os.path.exists(path):
            print(f"  ! ข้าม {label} — ไม่พบ {fname}")
            fail += 1
            continue
        raw = open(path, "rb").read()
        rows = max(0, raw.decode("utf-8-sig").strip().count("\n"))
        total += rows
        if args.dry_run:
            print(f"  [dry] {label:<22} {rows} ร้าน")
            continue
        try:
            push_csv(token, file_id, raw)
            print(f"  ✓ {label:<22} {rows} ร้าน")
            ok += 1
        except urllib.error.HTTPError as e:
            print(f"  ✗ {label:<22} {e.code} {e.read().decode()[:200]}")
            fail += 1

    print(f"\nอัปเดต {ok}/{len(SHEETS)} ชีต · รวม {total} ร้าน")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
