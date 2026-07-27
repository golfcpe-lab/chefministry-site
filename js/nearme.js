// ─────────────────────────────────────────────────────────────────────────────
// ChefMinistry — Near Me Module
// หาร้านใกล้ตำแหน่งผู้ใช้ (Geolocation + Haversine)
//
// ลำดับการหาพิกัดร้าน:
//   1. r.lat / r.lng          (จาก pipeline — data.js รุ่นใหม่)
//   2. CM_GEO[r.place_id]     (js/geo.js — พิกัดที่ geocode ไว้ล่วงหน้า)
//   3. AREA_CENTROIDS[area]   (จุดกลางย่าน — ค่าประมาณ)
//
// API:
//   CM_NEARME.locate(cb)          → ขอตำแหน่งผู้ใช้ (cache 10 นาที)
//   CM_NEARME.hasPosition()       → มีตำแหน่งแล้วหรือยัง
//   CM_NEARME.distanceKm(r)       → ระยะทาง กม. (null ถ้าไม่รู้พิกัด)
//   CM_NEARME.sortByDistance(list)→ เรียงใกล้→ไกล (ร้านไม่รู้พิกัดไปท้าย)
// ─────────────────────────────────────────────────────────────────────────────

const CM_NEARME = (() => {
  "use strict";

  let _pos = null;           // {lat, lng, ts}
  let _locating = false;
  const CACHE_MS = 10 * 60 * 1000;

  // ── จุดกลางย่าน (fallback หยาบ) ──────────────────────────────────────────
  const AREA_CENTROIDS = {
    // English (normalized)
    "thonglor": [13.7280, 100.5849], "ekkamai": [13.7221, 100.5872],
    "silom": [13.7225, 100.5226], "sathorn": [13.7205, 100.5311],
    "ari": [13.7770, 100.5437], "ratchada": [13.7667, 100.5701],
    "sukhumvit": [13.7390, 100.5597], "on nut": [13.7049, 100.5993],
    "onnut": [13.7049, 100.5993], "lat phrao": [13.8142, 100.5655],
    "ladprao": [13.8142, 100.5655], "rama 9": [13.7599, 100.5840],
    "rama9": [13.7599, 100.5840], "phrom phong": [13.7305, 100.5697],
    "asok": [13.7374, 100.5602], "asoke": [13.7374, 100.5602],
    "chinatown": [13.7398, 100.5090], "yaowarat": [13.7398, 100.5090],
    "charoenkrung": [13.7238, 100.5148], "charoen krung": [13.7238, 100.5148],
    "bang rak": [13.7262, 100.5183], "bangrak": [13.7262, 100.5183],
    "siam": [13.7455, 100.5343], "ratchathewi": [13.7592, 100.5316],
    "victory monument": [13.7649, 100.5383], "phaya thai": [13.7568, 100.5339],
    "banglamphu": [13.7629, 100.4976], "old town": [13.7529, 100.4941],
    "rattanakosin": [13.7529, 100.4941], "dusit": [13.7745, 100.5150],
    "sam yan": [13.7327, 100.5289], "samyan": [13.7327, 100.5289],
    "chidlom": [13.7440, 100.5432], "ploenchit": [13.7433, 100.5490],
    "langsuan": [13.7389, 100.5423], "bang na": [13.6680, 100.6042],
    "bangna": [13.6680, 100.6042], "udomsuk": [13.6797, 100.6089],
    "phra khanong": [13.7024, 100.5918], "prakanong": [13.7024, 100.5918],
    "thonburi": [13.7215, 100.4862], "talad noi": [13.7325, 100.5136],
    "ari-pradipat": [13.7802, 100.5416], "saphan khwai": [13.7937, 100.5497],
    "chatuchak": [13.8022, 100.5539], "huai khwang": [13.7692, 100.5745],
    "wongwian yai": [13.7269, 100.4934], "kaset": [13.8420, 100.5719],
    "nawamin": [13.8241, 100.6438], "ram inthra": [13.8630, 100.6250],
    "ramkhamhaeng": [13.7559, 100.6206], "bang kapi": [13.7659, 100.6435],
    "sena nikhom": [13.8271, 100.5735], "pinklao": [13.7629, 100.4769],
    // Thai (curated CM_RESTAURANTS)
    "วิทยุ": [13.7407, 100.5470], "ทองหล่อ": [13.7280, 100.5849],
    "เอกมัย": [13.7221, 100.5872], "สีลม": [13.7225, 100.5226],
    "สาทร": [13.7205, 100.5311], "อารีย์": [13.7770, 100.5437],
    "สุขุมวิท": [13.7390, 100.5597], "เจริญกรุง": [13.7238, 100.5148],
    "เยาวราช": [13.7398, 100.5090], "สยาม": [13.7455, 100.5343],
    "อ่อนนุช": [13.7049, 100.5993], "ลาดพร้าว": [13.8142, 100.5655],
    "รัชดา": [13.7667, 100.5701], "พร้อมพงษ์": [13.7305, 100.5697],
    "อโศก": [13.7374, 100.5602], "ราชเทวี": [13.7592, 100.5316],
    "บางรัก": [13.7262, 100.5183], "ธนบุรี": [13.7215, 100.4862],
    "จตุจักร": [13.8022, 100.5539], "บางนา": [13.6680, 100.6042],
    "ปิ่นเกล้า": [13.7629, 100.4769], "เกษตร": [13.8420, 100.5719],
  };

  // ── พิกัดร้าน ────────────────────────────────────────────────────────────
  function getCoords(r) {
    if (r == null) return null;
    if (typeof r.lat === "number" && typeof r.lng === "number" && r.lat) {
      return [r.lat, r.lng];
    }
    const geo = window.CM_GEO || {};
    const pid = r.place_id || r.gmaps_place_id;
    if (pid && geo[pid]) return geo[pid];
    const area = (r.area_normalized || r.area || "").toLowerCase().trim();
    if (area && AREA_CENTROIDS[area]) return AREA_CENTROIDS[area];
    return null;
  }

  // ── Haversine (กม.) ─────────────────────────────────────────────────────
  function _haversine(lat1, lng1, lat2, lng2) {
    const R = 6371, toRad = d => d * Math.PI / 180;
    const dLat = toRad(lat2 - lat1), dLng = toRad(lng2 - lng1);
    const a = Math.sin(dLat / 2) ** 2 +
              Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(a));
  }

  function distanceKm(r) {
    if (!_pos) return null;
    const c = getCoords(r);
    if (!c) return null;
    return _haversine(_pos.lat, _pos.lng, c[0], c[1]);
  }

  function fmtDistance(km) {
    if (km == null) return "";
    if (km < 1) return Math.round(km * 1000) + " ม.";
    if (km < 10) return km.toFixed(1) + " กม.";
    return Math.round(km) + " กม.";
  }

  // ── ตำแหน่งผู้ใช้ ─────────────────────────────────────────────────────────
  function hasPosition() { return !!_pos && (Date.now() - _pos.ts) < CACHE_MS; }

  // มือถือมัก timeout ถ้าไม่มีพิกัด cache — ลอง 2 ชั้น:
  //   รอบ 1 low-accuracy (เร็ว ใช้ cell/wifi, ยอมรับค่าเก่าได้ 10 นาที)
  //   รอบ 2 high-accuracy (เปิด GPS จริง, ให้เวลานานขึ้น) เมื่อรอบแรก timeout/หาไม่เจอ
  const _waiters = [];

  function _finish(err, pos) {
    _locating = false;
    const list = _waiters.splice(0, _waiters.length);
    list.forEach(w => { if (err) { w.err && w.err(err); } else { w.ok && w.ok(pos); } });
  }

  function _errMessage(e) {
    if (!e) return "หาตำแหน่งไม่สำเร็จ ลองใหม่อีกครั้ง";
    if (e.code === 1) return "กรุณาอนุญาตให้เข้าถึงตำแหน่ง แล้วกดอีกครั้ง (ไอคอน 🔒 ข้าง URL → Location → Allow)";
    if (e.code === 2) return "อุปกรณ์หาตำแหน่งไม่ได้ — เปิด Location/GPS ในเครื่องแล้วลองอีกครั้ง";
    return "หาตำแหน่งไม่สำเร็จ (สัญญาณ GPS อ่อน) — ลองใหม่ใกล้หน้าต่างหรือกลางแจ้ง";
  }

  function locate(cb, errCb) {
    if (hasPosition()) { cb && cb(_pos); return; }
    if (!navigator.geolocation) {
      errCb && errCb("เบราว์เซอร์นี้ไม่รองรับการหาตำแหน่ง");
      return;
    }
    if (!window.isSecureContext) {
      errCb && errCb("ต้องเปิดผ่าน https:// เท่านั้นถึงจะหาตำแหน่งได้");
      return;
    }

    _waiters.push({ ok: cb, err: errCb });
    if (_locating) return;       // มีคำขอค้างอยู่ — รอ callback รอบเดียวกัน
    _locating = true;

    const onOk = p => {
      _pos = { lat: p.coords.latitude, lng: p.coords.longitude, ts: Date.now() };
      _finish(null, _pos);
    };

    const tryHighAccuracy = e1 => {
      if (e1 && e1.code === 1) { _finish(_errMessage(e1)); return; }  // ถูกปฏิเสธ ไม่ต้องลองซ้ำ
      navigator.geolocation.getCurrentPosition(
        onOk,
        e2 => _finish(_errMessage(e2)),
        { enableHighAccuracy: true, timeout: 25000, maximumAge: 0 }
      );
    };

    navigator.geolocation.getCurrentPosition(
      onOk,
      tryHighAccuracy,
      { enableHighAccuracy: false, timeout: 8000, maximumAge: CACHE_MS }
    );
  }

  function sortByDistance(list) {
    if (!_pos) return list;
    return list.slice().sort((a, b) => {
      const da = distanceKm(a), db = distanceKm(b);
      if (da == null && db == null) return 0;
      if (da == null) return 1;
      if (db == null) return -1;
      return da - db;
    });
  }

  // ── Distance badge บนการ์ดร้าน ───────────────────────────────────────────
  // wrap buildRestaurantCard (อยู่ใน data.js — generated, แก้ตรงๆ ไม่ได้)
  function _wrapCardBuilder() {
    if (typeof window.buildRestaurantCard !== "function") return;
    if (window.buildRestaurantCard._cmNearmeWrapped) return;
    const orig = window.buildRestaurantCard;
    const wrapped = function (r, opts) {
      let html = orig(r, opts);
      const km = distanceKm(r);
      if (km != null) {
        html = html.replace(
          '<div class="r-location">📍 ',
          '<div class="r-location">📍 ' + fmtDistance(km) + " · "
        );
      }
      return html;
    };
    wrapped._cmNearmeWrapped = true;
    window.buildRestaurantCard = wrapped;
  }
  document.addEventListener("DOMContentLoaded", _wrapCardBuilder);
  _wrapCardBuilder();

  return { locate, hasPosition, distanceKm, fmtDistance, sortByDistance, getCoords };
})();
