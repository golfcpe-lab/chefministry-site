// ─────────────────────────────────────────────────────────────────────────────
// ChefMinistry — Drive helper (ให้/ถอนสิทธิ์แผนที่ Google My Maps รายอีเมล)
//
// แนวคิด: master map อยู่ในบัญชี Google ของเจ้าของ (golf.cpe@gmail.com)
// และแชร์ให้ service account เป็น "เอดิเตอร์" → SA จึงเพิ่ม/ถอน permission
// ของสมาชิกได้โดยไม่ต้องทำ OAuth flow ของผู้ใช้
//
// ต้องตั้ง env บน Vercel:
//   GOOGLE_SA_JSON  = เนื้อไฟล์ service account JSON ทั้งก้อน
//   CM_MAP_FILE_ID  = id ของแผนที่ (ค่าเริ่มต้นด้านล่างคือแผนที่ปัจจุบัน)
// ถ้าไม่ตั้ง ระบบจะข้ามส่วนแผนที่เงียบ ๆ (ดาวน์โหลดไฟล์ยังทำงานปกติ)
// ─────────────────────────────────────────────────────────────────────────────
const crypto = require('crypto');

const MAP_FILE_ID = process.env.CM_MAP_FILE_ID || '16MnZd7TA5ou0Ywafd_33yH5lkQ-HJPs';
const MAP_URL = `https://www.google.com/maps/d/viewer?mid=${MAP_FILE_ID}`;

let _cachedToken = null;   // { token, exp }

function loadSA() {
  const raw = (process.env.GOOGLE_SA_JSON || '').trim();
  if (!raw) return null;
  try { return JSON.parse(raw); } catch { return null; }
}

function b64url(input) {
  return Buffer.from(input).toString('base64')
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function accessToken() {
  if (_cachedToken && _cachedToken.exp > Date.now() + 60_000) return _cachedToken.token;
  const sa = loadSA();
  if (!sa) return null;

  const now = Math.floor(Date.now() / 1000);
  const header = b64url(JSON.stringify({ alg: 'RS256', typ: 'JWT' }));
  const claim = b64url(JSON.stringify({
    iss: sa.client_email,
    scope: 'https://www.googleapis.com/auth/drive',
    aud: 'https://oauth2.googleapis.com/token',
    iat: now, exp: now + 3600,
  }));
  const signer = crypto.createSign('RSA-SHA256');
  signer.update(`${header}.${claim}`);
  const sig = b64url(signer.sign(sa.private_key));

  const r = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
      assertion: `${header}.${claim}.${sig}`,
    }),
  });
  if (!r.ok) return null;
  const d = await r.json();
  _cachedToken = { token: d.access_token, exp: Date.now() + (d.expires_in || 3600) * 1000 };
  return _cachedToken.token;
}

async function listPermissions(tok) {
  const r = await fetch(
    `https://www.googleapis.com/drive/v3/files/${MAP_FILE_ID}/permissions` +
    '?fields=permissions(id,type,role,emailAddress)',
    { headers: { Authorization: `Bearer ${tok}` } });
  if (!r.ok) return [];
  return (await r.json()).permissions || [];
}

/** ให้สิทธิ์ดูแผนที่กับอีเมลสมาชิก — idempotent */
async function grantMapAccess(email) {
  const tok = await accessToken();
  if (!tok) return { ok: false, skipped: 'no-credentials' };
  const existing = (await listPermissions(tok))
    .find(p => (p.emailAddress || '').toLowerCase() === email.toLowerCase());
  if (existing) return { ok: true, already: true, mapUrl: MAP_URL };

  const r = await fetch(
    `https://www.googleapis.com/drive/v3/files/${MAP_FILE_ID}/permissions` +
    '?sendNotificationEmail=false&fields=id',
    { method: 'POST',
      headers: { Authorization: `Bearer ${tok}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: 'reader', type: 'user', emailAddress: email }) });
  if (!r.ok) {
    const msg = await r.text();
    // 400 = อีเมลนั้นไม่มีบัญชี Google (สมาชิกล็อกอินด้วย Google อยู่แล้วจึงไม่ควรเกิด)
    return { ok: false, error: msg.slice(0, 200) };
  }
  return { ok: true, mapUrl: MAP_URL };
}

/** ถอนสิทธิ์ทันที (หมดอายุ / ถูกตัด / ลบบัญชี) */
async function revokeMapAccess(email) {
  const tok = await accessToken();
  if (!tok) return { ok: false, skipped: 'no-credentials' };
  const perms = await listPermissions(tok);
  const target = perms.filter(p =>
    (p.emailAddress || '').toLowerCase() === email.toLowerCase() && p.role !== 'owner');
  let removed = 0;
  for (const p of target) {
    const r = await fetch(
      `https://www.googleapis.com/drive/v3/files/${MAP_FILE_ID}/permissions/${p.id}`,
      { method: 'DELETE', headers: { Authorization: `Bearer ${tok}` } });
    if (r.ok) removed++;
  }
  return { ok: true, removed };
}

/** ตรวจว่าอีเมลนี้ยังมีสิทธิ์อยู่ไหม (ใช้ตอนแสดงปุ่มบนเว็บ) */
async function hasMapAccess(email) {
  const tok = await accessToken();
  if (!tok) return null;         // null = ตรวจไม่ได้ (ยังไม่ตั้ง credential)
  const perms = await listPermissions(tok);
  return perms.some(p => (p.emailAddress || '').toLowerCase() === email.toLowerCase());
}

module.exports = { MAP_FILE_ID, MAP_URL, grantMapAccess, revokeMapAccess, hasMapAccess };
