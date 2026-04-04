# ChefMinistry — Data Scraper Suite

ระบบดึงข้อมูลร้านและ review velocity จาก Wongnai, GrabFood, LINE MAN

## Setup (ครั้งแรก)

```bash
cd scripts/scraper
python run_all.py --setup
```

## การใช้งาน

```bash
# รัน scraper ทั้งหมด (Wongnai + GrabFood + LINE MAN) + export
python run_all.py

# รัน scraper แยกทีละตัว
python run_all.py --wongnai
python run_all.py --grabfood
python run_all.py --lineman

# ดูสรุปข้อมูลในฐานข้อมูล
python run_all.py --summary

# Export + inject เข้า data.js (อัปเดต site)
python run_all.py --inject
```

## โครงสร้างไฟล์

```
scraper/
├── run_all.py          ← จุดเริ่มต้น รันทุกอย่าง
├── config.py           ← ตั้งค่า: areas, delay, paths
├── db.py               ← SQLite: restaurants + review_snapshots
├── scrape_wongnai.py   ← Playwright HTML scraper
├── scrape_grabfood.py  ← Network interception (JSON API)
├── scrape_lineman.py   ← Network interception (JSON API)
├── export_signals.py   ← คำนวณ velocity + export JSON
└── requirements.txt    ← pip dependencies
```

## หลักการทำงาน

1. **Scrape** — ดึงชื่อร้าน + review count ทุกวัน
2. **Store** — บันทึก snapshot รายวันใน SQLite
3. **Velocity** — คำนวณ % เพิ่มของ review ใน 30 วัน
4. **Signal** — ร้านที่ review เพิ่มเร็ว = trending signal

ต้องรัน scraper อย่างน้อย **2 วันขึ้นไป** จึงจะมี velocity data

## Cron (Linux/Mac)

```bash
# รันทุกวัน 09:00
0 9 * * * cd /path/to/scripts/scraper && python run_all.py --inject >> logs/daily.log 2>&1
```

## Task Scheduler (Windows)

ตั้ง trigger: Daily 09:00
Action: `python C:\path\to\scripts\scraper\run_all.py --inject`
