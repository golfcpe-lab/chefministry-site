// ─────────────────────────────────────────────────────────────────────────────
// ChefMinistry — Gated Map Download
// GET/POST /api/map-download?group=cafe&format=kml   (Authorization: Bearer <idToken>)
//
// ทำไมต้องผ่าน API: ไฟล์ใน GitHub Pages เป็น public URL ใครก็โหลดได้
// endpoint นี้จึง (1) ตรวจ Firebase ID token (2) เช็คสถานะสมาชิกที่ cm_subscriptions
// (client เขียนเองไม่ได้ — rules อนุญาตเฉพาะ admin) (3) ค่อยสร้างไฟล์ส่งกลับ
//
// ไม่ต้องมีที่เก็บไฟล์ลับ: สร้างสดจาก export_restaurants.json ทุกครั้ง
// ─────────────────────────────────────────────────────────────────────────────

const RAW_EXPORT = 'https://raw.githubusercontent.com/golfcpe-lab/chefministry-site/main/scripts/scraper/export_restaurants.json';

const MIN_RATING = 4.3;
const MIN_REVIEWS = 50;
const BBOX = { latMin: 13.45, latMax: 14.05, lngMin: 100.25, lngMax: 100.95 };

const GROUPS = {
  cafe:       { label: '☕ คาเฟ่ & มัทฉะ',          color: 'ff3b8cd6' },
  finedining: { label: '🍽️ Fine Dining & Omakase', color: 'ff2b52c9' },
  thai:       { label: '🇹🇭 อาหารไทย',              color: 'ff4fc3ff' },
  noodles:    { label: '🍜 ก๋วยเตี๋ยว & เส้น',       color: 'ff64d19a' },
  grill:      { label: '🥩 ปิ้งย่าง & ชาบู',         color: 'ff4b4bd6' },
  japanese:   { label: '🍣 ญี่ปุ่น',                 color: 'ffb37cff' },
  korean:     { label: '🇰🇷 เกาหลี',                color: 'ff7cc0ff' },
  chinese:    { label: '🇨🇳 จีน & ติ่มซำ',           color: 'ff3ba7e8' },
  western:    { label: '🍕 ตะวันตก',                color: 'ff8fd14f' },
  other:      { label: '✨ ร้านน่าสนใจอื่นๆ',        color: 'ff9e9e9e' },
};
const GROUP_ORDER = Object.keys(GROUPS);

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
}

// ── Auth: idToken → { uid, email } ───────────────────────────────────────────
async function verifyToken(idToken) {
  try {
    const r = await fetch(
      `https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=${process.env.FIREBASE_API_KEY}`,
      { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idToken }) });
    const d = await r.json();
    const u = d.users?.[0];
    return u ? { uid: u.localId, email: u.email } : null;
  } catch { return null; }
}

// ── Subscription: อ่านจาก collection ที่ client เขียนไม่ได้ ───────────────────
async function getSubscription(uid, idToken) {
  const url = `https://firestore.googleapis.com/v1/projects/${process.env.FIREBASE_PROJECT_ID}` +
              `/databases/(default)/documents/cm_subscriptions/${encodeURIComponent(uid)}`;
  const r = await fetch(url, { headers: { Authorization: `Bearer ${idToken}` } });
  if (!r.ok) return null;
  const doc = await r.json();
  const f = doc.fields || {};
  return {
    status:    f.status?.stringValue || 'none',
    plan:      f.plan?.stringValue || '',
    expiresAt: f.expiresAt?.stringValue || '',
    note:      f.note?.stringValue || '',
  };
}

function isActive(sub) {
  if (!sub || sub.status !== 'active') return false;
  if (!sub.expiresAt) return true;                       // ไม่กำหนดวันหมด = ใช้ได้
  return new Date(sub.expiresAt).getTime() > Date.now(); // หมดอายุ = ตัดทันที
}

// ── Data + grouping (ตรงกับ scraper/export_maps.py) ──────────────────────────
let _cache = { at: 0, data: null };
async function loadData() {
  if (_cache.data && Date.now() - _cache.at < 10 * 60 * 1000) return _cache.data;
  const r = await fetch(RAW_EXPORT);
  if (!r.ok) throw new Error('load export failed: ' + r.status);
  const data = await r.json();
  _cache = { at: Date.now(), data };
  return data;
}

function groupOf(r) {
  const c = String(r.cuisine_normalized || r.cuisine || '').toLowerCase();
  const has = (...k) => k.some(x => c.includes(x));
  if (r.segment === 'fine' || has('fine dining', 'omakase')) return 'finedining';
  if (has('cafe', 'café', 'matcha', 'bakery', 'dessert', 'tea', 'coffee')) return 'cafe';
  if (has('noodle', 'ramen', 'ก๋วยเตี๋ยว')) return 'noodles';
  if (has('yakiniku', 'bbq', 'hot pot', 'hotpot', 'suki', 'shabu', 'grill')) return 'grill';
  if (has('korean')) return 'korean';
  if (has('chinese', 'dim sum', 'dimsum')) return 'chinese';
  if (has('japanese', 'sushi', 'katsu', 'izakaya', 'teppan')) return 'japanese';
  if (has('italian', 'french', 'steakhouse', 'western', 'pizza', 'american',
          'mexican', 'burger', 'german', 'mediterranean', 'indian')) return 'western';
  if (has('thai', 'isaan', 'local')) return 'thai';
  return 'other';
}

function isQuality(r) {
  if (!(r.is_restaurant_focus && r.is_bangkok_focus)) return false;
  const lat = Number(r.lat), lng = Number(r.lng);
  if (!lat || !lng) return false;
  if (lat < BBOX.latMin || lat > BBOX.latMax || lng < BBOX.lngMin || lng > BBOX.lngMax) return false;
  return (r.rating_gmaps || 0) >= MIN_RATING && (r.totalReviews || 0) >= MIN_REVIEWS;
}

const esc = s => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const mapsUrl = r => r.place_id
  ? `https://www.google.com/maps/place/?q=place_id:${r.place_id}`
  : (r.url || 'https://www.google.com/maps/search/' + encodeURIComponent(r.name || ''));

function describe(r) {
  const bits = [];
  if (r.rating_gmaps) bits.push(`⭐ ${Number(r.rating_gmaps).toFixed(1)}` +
    (r.totalReviews ? ` (${Number(r.totalReviews).toLocaleString()} รีวิว)` : ''));
  const cu = r.cuisine_normalized || r.cuisine, ar = r.area_normalized || r.area;
  if (cu) bits.push(cu);
  if (ar) bits.push(ar);
  if (r.budgetLabel) bits.push(r.budgetLabel);
  return `${bits.join(' · ')}\n${r.address || ''}\n${mapsUrl(r)}\nข้อมูลจาก ChefMinistry — chefministry.com`;
}

function buildKml(title, folders) {
  const out = ['<?xml version="1.0" encoding="UTF-8"?>',
    '<kml xmlns="http://www.opengis.net/kml/2.2">', '<Document>',
    `  <name>${esc(title)}</name>`,
    `  <description>${esc('อัปเดต ' + new Date().toISOString().slice(0, 10) + ' — chefministry.com')}</description>`];
  folders.forEach(([label, color, rows], i) => {
    if (!rows.length) return;
    const sid = 'cm' + i;
    out.push(`  <Style id="${sid}"><IconStyle><color>${color}</color>` +
      '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/dining.png</href></Icon></IconStyle></Style>');
    out.push('  <Folder>', `    <name>${esc(label)}</name>`);
    rows.forEach(r => {
      out.push('    <Placemark>',
        `      <styleUrl>#${sid}</styleUrl>`,
        `      <name>${esc(r.name)}</name>`,
        `      <description>${esc(describe(r))}</description>`,
        `      <Point><coordinates>${r.lng},${r.lat},0</coordinates></Point>`,
        '    </Placemark>');
    });
    out.push('  </Folder>');
  });
  out.push('</Document></kml>');
  return out.join('\n');
}

function buildCsv(rows) {
  const cols = ['Name', 'Latitude', 'Longitude', 'Cuisine', 'Area', 'Rating', 'Reviews', 'Price', 'Address', 'GoogleMapsURL'];
  const cell = v => {
    const s = String(v == null ? '' : v);
    return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  };
  const lines = [cols.join(',')];
  rows.forEach(r => lines.push([
    r.name, r.lat, r.lng, r.cuisine_normalized || r.cuisine, r.area_normalized || r.area,
    r.rating_gmaps || '', r.totalReviews || '', r.budgetLabel || '', r.address || '', mapsUrl(r),
  ].map(cell).join(',')));
  return '﻿' + lines.join('\r\n');   // BOM ให้ Excel อ่านภาษาไทยถูก
}

module.exports = async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();

  const q = req.query || {};
  const body = req.body || {};
  const group = String(q.group || body.group || 'all').toLowerCase();
  const format = String(q.format || body.format || 'kml').toLowerCase();
  const idToken = (req.headers.authorization || '').replace(/^Bearer\s+/i, '') || body.idToken;

  if (!idToken) return res.status(401).json({ error: 'ต้องเข้าสู่ระบบก่อนดาวน์โหลด' });
  if (!['kml', 'csv'].includes(format)) return res.status(400).json({ error: 'format ต้องเป็น kml หรือ csv' });
  if (group !== 'all' && !GROUPS[group]) return res.status(400).json({ error: 'ไม่รู้จักหมวดนี้' });

  const user = await verifyToken(idToken);
  if (!user) return res.status(401).json({ error: 'token ไม่ถูกต้องหรือหมดอายุ — ลองล็อกอินใหม่' });

  const sub = await getSubscription(user.uid, idToken);
  if (!isActive(sub)) {
    return res.status(402).json({
      error: 'ต้องเป็นสมาชิกรายเดือนถึงจะดาวน์โหลดได้',
      status: sub?.status || 'none',
      expiresAt: sub?.expiresAt || null,
      subscribeUrl: 'https://chefministry.com/subscribe.html',
    });
  }

  let data;
  try { data = await loadData(); }
  catch (e) { return res.status(503).json({ error: 'โหลดข้อมูลร้านไม่สำเร็จ ลองใหม่อีกครั้ง' }); }

  const quality = data.filter(isQuality)
    .sort((a, b) => (b.rating_gmaps || 0) * Math.pow(b.totalReviews || 0, 0.3)
                  - (a.rating_gmaps || 0) * Math.pow(a.totalReviews || 0, 0.3));

  let payload, filename, mime;
  if (group === 'all') {
    const folders = GROUP_ORDER.map(k =>
      [GROUPS[k].label, GROUPS[k].color, quality.filter(r => groupOf(r) === k)]);
    payload = buildKml('ChefMinistry — ร้านคัดสรรกรุงเทพฯ', folders);
    filename = 'chefministry-bangkok-all.kml';
    mime = 'application/vnd.google-earth.kml+xml';
  } else {
    const rows = quality.filter(r => groupOf(r) === group);
    if (format === 'csv') {
      payload = buildCsv(rows);
      filename = `chefministry-${group}.csv`;
      mime = 'text/csv; charset=utf-8';
    } else {
      payload = buildKml(`ChefMinistry — ${GROUPS[group].label}`,
        [[GROUPS[group].label, GROUPS[group].color, rows]]);
      filename = `chefministry-${group}.kml`;
      mime = 'application/vnd.google-earth.kml+xml';
    }
  }

  res.setHeader('Content-Type', mime);
  res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
  res.setHeader('Cache-Control', 'private, no-store');
  return res.status(200).send(payload);
};
