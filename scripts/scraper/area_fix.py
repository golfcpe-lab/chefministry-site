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


# ที่อยู่ภาษาอังกฤษจาก Google (เช่น "P9P7+FCW, Bang Phai, Bang Khae, Bangkok 10160")
# เดิม regex จับแต่ภาษาไทย → district = None → area เก่าที่ผิดไม่เคยถูกแก้
# (เคส "อาเล็กโภชนา" อยู่บางแค แต่ data เก่าจาก Wongnai บอก On Nut)
_EN_DISTRICTS = {}
for _th, _en in DISTRICTS.items():
    _EN_DISTRICTS[_en.lower()] = _th
    _EN_DISTRICTS[_en.lower().replace(" ", "")] = _th
# ชื่ออังกฤษที่ Google สะกดต่างจาก display ของเรา
_EN_ALIASES = {
    "bang rak": "บางรัก", "bangrak": "บางรัก", "bang kho laem": "บางคอแหลม",
    "khlong toei": "คลองเตย", "klongtoey": "คลองเตย", "watthana": "วัฒนา",
    "vadhana": "วัฒนา", "huai khwang": "ห้วยขวาง", "huaykwang": "ห้วยขวาง",
    "chatuchak": "จตุจักร", "phaya thai": "พญาไท", "ratchathewi": "ราชเทวี",
    "pathum wan": "ปทุมวัน", "pathumwan": "ปทุมวัน", "sathon": "สาทร",
    "bang khae": "บางแค", "bangkhae": "บางแค", "lat phrao": "ลาดพร้าว",
    "lat krabang": "ลาดกระบัง", "din daeng": "ดินแดง", "bang sue": "บางซื่อ",
    "bang su": "บางซื่อ", "suan luang": "สวนหลวง", "phra khanong": "พระโขนง",
    "samphanthawong": "สัมพันธวงศ์", "pom prap sattru phai": "ป้อมปราบศัตรูพ่าย",
    "thon buri": "ธนบุรี", "bangkok noi": "บางกอกน้อย", "bangkok yai": "บางกอกใหญ่",
    "taling chan": "ตลิ่งชัน", "chom thong": "จอมทอง", "rat burana": "ราษฎร์บูรณะ",
    "prawet": "ประเวศ", "bang na": "บางนา", "min buri": "มีนบุรี",
    "nong chok": "หนองจอก", "nong khaem": "หนองแขม", "bang bon": "บางบอน",
    "thung khru": "ทุ่งครุ", "khan na yao": "คันนายาว", "saphan sung": "สะพานสูง",
    "wang thonglang": "วังทองหลาง", "khlong sam wa": "คลองสามวา",
    "thawi watthana": "ทวีวัฒนา", "sai mai": "สายไหม", "lak si": "หลักสี่",
    "don mueang": "ดอนเมือง", "bang khen": "บางเขน", "bueng kum": "บึงกุ่ม",
    "bang phlat": "บางพลัด", "phasi charoen": "ภาษีเจริญ", "yan nawa": "ยานนาวา",
    "khlong san": "คลองสาน", "phra nakhon": "พระนคร", "dusit": "ดุสิต",
    "bang kapi": "บางกะปิ", "bangkapi": "บางกะปิ", "bang khun thian": "บางขุนเทียน",
}
_EN_DISTRICTS.update(_EN_ALIASES)


def _district_from_english(addr):
    """หาเขตจากที่อยู่ภาษาอังกฤษ — เทียบทีละ segment ที่คั่นด้วย comma"""
    a = str(addr or "")
    if not a:
        return None
    segs = [s.strip().lower() for s in re.split(r"[,\n]", a) if s.strip()]
    for s in segs:
        s_clean = re.sub(r"\s+\d{5}$", "", s).strip()
        if s_clean in _EN_DISTRICTS:
            return _EN_DISTRICTS[s_clean]
    # fallback: substring (ยาวสุดก่อน กัน "bang" ไปชนคำสั้น)
    low = a.lower()
    for en in sorted(_EN_DISTRICTS, key=len, reverse=True):
        if len(en) >= 6 and en in low:
            return _EN_DISTRICTS[en]
    return None


def district_from_address(addr):
    """คืนชื่อเขต (ไทย) จากที่อยู่ Google Maps หรือ None"""
    if not addr:
        return None
    a = str(addr)
    if not re.search(r"[ก-๙]", a):
        return _district_from_english(a)
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
