"""
ChefMinistry — ตัววัด/คุมงบ Google Maps Places API

Places API (New) คิดเงินตาม **SKU ที่สูงที่สุดใน field mask** ไม่ใช่จำนวน field
โควตาฟรีต่อเดือน (รีเซ็ตวันที่ 1 ของเดือน ไม่ทบไปเดือนถัดไป):

  SKU                          ราคา/1,000   ฟรี/เดือน   field ที่ทำให้ตกชั้นนี้
  ---------------------------  -----------  ---------   -----------------------------------
  Place Details Essentials     $5           10,000      formattedAddress, location, types
  Place Details Pro            $17           5,000      displayName, businessStatus, primaryType
  Place Details Enterprise     $20           1,000      rating, userRatingCount, priceLevel,
                                                        regularOpeningHours, websiteUri
  Text Search Pro              $32           5,000      (ไม่มี field Enterprise)
  Text Search Enterprise       $35           1,000      rating, userRatingCount, priceLevel

บทเรียนที่ทำให้บิลบานปลาย: field mask เดิมใส่ rating+userRatingCount ทุกที่
→ ทุก call ตกชั้น Enterprise ที่ฟรีแค่ 1,000/เดือน → call ที่ 1,001 เป็นต้นไป
เสียเงินจริง ~฿0.70/ครั้ง

โมดูลนี้:
  1. นับ call ต่อ SKU ต่อเดือน เก็บลงตาราง api_usage ใน chefministry_data.db
     (DB ถูก commit ขึ้น repo ทุกคืน → ตัวนับอยู่รอดข้าม CI run)
  2. บล็อก call เมื่อถึงเพดาน (allow() คืน False)
  3. กระจายโควตาที่เหลือให้เท่า ๆ กันตามวันที่เหลือในเดือน (daily_allowance)
     เพื่อไม่ให้ใช้หมดตั้งแต่ต้นเดือนแล้วไม่มี snapshot ใช้ปลายเดือน

ปรับเพดานด้วย env CM_API_BUDGET_PCT (ค่าเริ่มต้น 100 = อยู่ในโควตาฟรีพอดี)
  CM_API_BUDGET_PCT=100  → ไม่เสียเงินเลย
  CM_API_BUDGET_PCT=150  → ยอมจ่ายส่วนเกิน 50% ของโควตาฟรี
  CM_API_BUDGET_PCT=0    → dry mode: บล็อกทุก call
"""
import os
import calendar
import math
from datetime import date

from db import get_conn

# โควตาฟรีต่อเดือน (Google Maps Platform, price list อัปเดต 2026-07-20)
FREE_CAPS = {
    "details_ess":  10_000,
    "details_pro":   5_000,
    "details_ent":   1_000,
    "text_pro":      5_000,
    "text_ent":      1_000,
}

# ราคาต่อ 1,000 call หลังเกินโควตาฟรี (USD) — ใช้แค่รายงาน
UNIT_USD = {
    "details_ess":  5.0,
    "details_pro": 17.0,
    "details_ent": 20.0,
    "text_pro":    32.0,
    "text_ent":    35.0,
}

USD_TO_THB = 35.0  # ประมาณการสำหรับรายงานเท่านั้น


def _budget_pct() -> float:
    try:
        return max(0.0, float(os.environ.get("CM_API_BUDGET_PCT", "100")))
    except ValueError:
        return 100.0


def budget(sku: str) -> int:
    """เพดาน call ต่อเดือนของ SKU นี้ (โควตาฟรี × CM_API_BUDGET_PCT)"""
    return int(FREE_CAPS.get(sku, 0) * _budget_pct() / 100.0)


def month_key(d: date = None) -> str:
    d = d or date.today()
    return d.strftime("%Y-%m")


def days_left_in_month(d: date = None) -> int:
    """จำนวนวันที่เหลือในเดือน นับวันนี้ด้วย (อย่างน้อย 1)"""
    d = d or date.today()
    last = calendar.monthrange(d.year, d.month)[1]
    return max(1, last - d.day + 1)


def _ensure_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_usage (
            month TEXT NOT NULL,
            sku   TEXT NOT NULL,
            calls INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (month, sku)
        )
    """)


def used(sku: str, month: str = None) -> int:
    month = month or month_key()
    with get_conn() as conn:
        _ensure_table(conn)
        row = conn.execute(
            "SELECT calls FROM api_usage WHERE month = ? AND sku = ?", (month, sku)
        ).fetchone()
    return int(row["calls"]) if row else 0


def remaining(sku: str) -> int:
    return max(0, budget(sku) - used(sku))


def allow(sku: str, n: int = 1) -> bool:
    """ยังยิง call ของ SKU นี้ได้อีก n ครั้งไหม (ไม่บันทึก — เรียก record() หลังยิงสำเร็จ)"""
    if sku not in FREE_CAPS:
        return True
    return remaining(sku) >= n


def record(sku: str, n: int = 1):
    """บันทึกว่ายิงไปแล้ว n call — เรียกทุกครั้งที่ยิงจริง ไม่ว่า response จะสำเร็จหรือไม่
    (Google คิดเงินตาม request ที่ยิง ไม่ใช่ตามผลลัพธ์)"""
    if sku not in FREE_CAPS:
        return
    month = month_key()
    with get_conn() as conn:
        _ensure_table(conn)
        conn.execute("""
            INSERT INTO api_usage (month, sku, calls) VALUES (?, ?, ?)
            ON CONFLICT(month, sku) DO UPDATE SET calls = calls + excluded.calls
        """, (month, sku, n))


def daily_allowance(sku: str) -> int:
    """โควตาที่ควรใช้ "วันนี้" = ที่เหลือทั้งเดือน ÷ วันที่เหลือ
    ทำให้ pipeline ไม่ใช้โควตาหมดตั้งแต่ต้นเดือน"""
    rem = remaining(sku)
    if rem <= 0:
        return 0
    return max(1, math.ceil(rem / days_left_in_month()))


def report(month: str = None) -> str:
    month = month or month_key()
    lines = [f"  📊 การใช้ Google Maps API เดือน {month}"]
    total_thb = 0.0
    for sku in FREE_CAPS:
        u = used(sku, month)
        if u == 0:
            continue
        cap = FREE_CAPS[sku]
        billable = max(0, u - cap)
        thb = billable / 1000.0 * UNIT_USD[sku] * USD_TO_THB
        total_thb += thb
        flag = "⚠️ " if billable else "✅"
        lines.append(f"     {flag} {sku:<12} {u:>6,} / ฟรี {cap:,}"
                     + (f"  → คิดเงิน {billable:,} ครั้ง ≈ ฿{thb:,.0f}" if billable else ""))
    if len(lines) == 1:
        lines.append("     (ยังไม่มีการใช้งานเดือนนี้)")
    else:
        lines.append(f"     รวมประมาณ ฿{total_thb:,.0f}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        with get_conn() as conn:
            _ensure_table(conn)
            conn.execute("DELETE FROM api_usage WHERE month = ?", (month_key(),))
        print(f"reset ตัวนับเดือน {month_key()} แล้ว")
    print(report())
    print()
    for _sku in FREE_CAPS:
        print(f"  {_sku:<12} เหลือเดือนนี้ {remaining(_sku):>6,}  ใช้ได้วันนี้ {daily_allowance(_sku):>4,}")
