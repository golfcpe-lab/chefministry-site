# -*- coding: utf-8 -*-
"""
area_fix.py — คำนวณ 'ย่าน' ที่ถูกต้องจาก gmaps_address (ที่อยู่สดจาก Google)
แก้ปัญหา area เก่าผิด เช่น ร้านอยู่ดอนเมืองแต่ data เก่าบอกมีนบุรี
"""
import re

# 50 เขต กทม. (ไทย → ชื่อแสดงผล) + เมืองปริมณฑลที่พบบ่อย
DISTRICTS = {
    "พระนคร": "Phra Nakhon", "ดุสิต": "Dusit", "หนองจอก": "Nong Chok",
    "บางรัก": "Bang Rak", "บางเขน": "Bang Khen", "บางกะปิ": "Bangkapi",
    "ปทุมวัน": "Pathumwan", "ป้อมปราบศัตรูพ่าย": "Pom Prap", "พระโขนง": "Phra Khanong",
    "มีนบุรี": "Minburi", "ลาดกระบัง": "Lat Krabang", "ยานนาวา": "Yan Nawa",
    "สัมพันธวงศ์": "Yaowarat", "พญาไท": "Phaya Thai", "ธนบุรี": "Thonburi",
    "บางกอกใหญ่": "Bangkok Yai", "ห้วยขวาง": "Huai Khwang", "คลองสาน": "Khlong San",
    "ตลิ่งชัน": "Taling Chan", "บางกอกน้อย": "Bangkok Noi", "บางขุนเทียน": "Bang Khun Thian",
    "ภาษีเจริญ": "Phasi Charoen", "หนองแขม": "Nong Khaem", "ราษฎร์บูรณะ": "Rat Burana",
    "บางพลัด": "Bang Phlat", "ดินแดง": "Din Daeng", "บึงกุ่ม": "Bueng Kum",
    "สาทร": "Sathorn", "บางซื่อ": "Bang Sue", "จตุจักร": "Chatuchak",
    "บางคอแหลม": "Bang Kho Laem", "ประเวศ": "Prawet", "คลองเตย": "Khlong Toei",
    "สวนหลวง": "Suan Luang", "จอมทอง": "Chom Thong", "ดอนเมือง": "Don Mueang",
    "ราชเทวี": "Ratchathewi", "ลาดพร้าว": "Lat Phrao", "วัฒนา": "Watthana",
    "บางแค": "Bang Khae", "หลักสี่": "Lak Si", "สายไหม": "Sai Mai",
    "คันนายาว": "Khan Na Yao", "สะพานสูง": "Saphan Sung", "วังทองหลาง": "Wang Thonglang",
    "คลองสามวา": "Khlong Sam Wa", "บางนา": "Bangna", "ทวีวัฒนา": "Thawi Watthana",
    "ทุ่งครุ": "Thung Khru", "บางบอน": "Bang Bon",
    # ปริมณฑล
    "ปากเกร็ด": "Pak Kret", "เมืองนนทบุรี": "Nonthaburi", "นนทบุรี": "Nonthaburi",
    "เมืองสมุทรปราการ": "Samut Prakan", "บางพลี": "Bang Phli",
    "ธัญบุรี": "Rangsit", "คลองหลวง": "Pathum Thani", "ปทุมธานี": "Pathum Thani",
}

# ย่านย่อยเดิมที่ "ละเอียดกว่าเขต" — ถ้าเขตจาก Google สอดคล้อง ให้เก็บย่านเดิมไว้
SUBAREA_PARENT = {
    "thonglor":  {"วัฒนา", "คลองเตย"},
    "ekkamai":   {"วัฒนา", "คลองเตย", "พระโขนง"},
    "sukhumvit": {"วัฒนา", "คลองเตย", "พระโขนง", "บางนา", "ปทุมวัน"},
    "asok":      {"วัฒนา", "คลองเตย"},
    "phrom phong": {"วัฒนา", "คลองเตย"},
    "onnut":     {"สวนหลวง", "พระโขนง", "วัฒนา"},
    "silom":     {"บางรัก", "สาทร"},
    "sathorn":   {"สาทร", "บางรัก", "ยานนาวา"},
    "riverside": {"บางรัก", "คลองสาน", "บางคอแหลม", "ธนบุรี", "สัมพันธวงศ์"},
    "chinatown": {"สัมพันธวงศ์", "ป้อมปราบศัตรูพ่าย"},
    "yaowarat":  {"สัมพันธวงศ์", "ป้อมปราบศัตรูพ่าย"},
    "ari":       {"พญาไท", "จตุจักร"},
    "rama9":     {"ห้วยขวาง", "ดินแดง", "สวนหลวง"},
    "ratchada":  {"ห้วยขวาง", "ดินแดง", "จตุจักร"},
    "ladprao":   {"ลาดพร้าว", "จตุจักร", "วังทองหลาง", "ห้วยขวาง"},
    "ramintra":  {"บางเขน", "คันนายาว", "บึงกุ่ม", "สายไหม", "มีนบุรี"},
    "victory monument": {"ราชเทวี", "พญาไท"},
    "siam":      {"ปทุมวัน"},
    "banglamphu": {"พระนคร"},
}
# ชื่อเขตเอง (lower display) → เขตไทย เพื่อเช็คว่า area เดิมระดับเขตตรงกับ Google ไหม
for _th, _en in list(DISTRICTS.items()):
    SUBAREA_PARENT.setdefault(_en.lower(), set()).add(_th)


def district_from_address(addr):
    """คืนชื่อเขต (ไทย) จากที่อยู่ Google Maps หรือ None"""
    if not addr:
        return None
    a = str(addr)
    # รูปแบบชัดเจน: "เขตดอนเมือง"
    m = re.search(r"เขต\s*([ก-๙]+)", a)
    if m:
        cand = m.group(1)
        for th in DISTRICTS:
            if cand.startswith(th) or th.startswith(cand):
                return th
    # รูปแบบย่อ: "แขวงสนามบิน ดอนเมือง กรุงเทพมหานคร" — ตัดคำหลัง "แขวง" ทิ้งก่อน
    a2 = re.sub(r"แขวง\s*[ก-๙]+", " ", a)
    best, best_pos = None, -1
    for th in DISTRICTS:
        p = a2.rfind(th)
        if p > best_pos:
            best, best_pos = th, p
    return best


def resolve_area(current_area, gmaps_address):
    """
    คืน area ที่ควรแสดง:
    - ไม่มีที่อยู่ Google → คงค่าเดิม
    - area เดิมเป็นย่านย่อยที่สอดคล้องกับเขตจริง → คงค่าเดิม (ละเอียดกว่า)
    - นอกนั้น → ใช้ชื่อเขตจากที่อยู่จริง
    """
    district = district_from_address(gmaps_address)
    if not district:
        return current_area
    cur = (current_area or "").strip().lower()
    if cur and cur not in ("bangkok", "other", "unknown"):
        allowed = SUBAREA_PARENT.get(cur)
        if allowed and district in allowed:
            return current_area  # ย่านเดิมถูกต้องและละเอียดกว่า
    return DISTRICTS[district]
