// ─────────────────────────────────────────────────────────────────────────────
// ChefMinistry — Subscription API
// POST /api/subscription
//   { idToken, action: 'me' }                                → สถานะของตัวเอง
//   { idToken, action: 'request', plan?, slipNote? }         → แจ้งโอนเงิน (pending)
//   { idToken, action: 'list' }                              → admin: ดูทั้งหมด
//   { idToken, action: 'approve', uid, months? }             → admin: อนุมัติ +30 วัน
//   { idToken, action: 'revoke',  uid }                      → admin: ตัด service ทันที
//   { idToken, action: 'purge',   uid }                      → admin: ลบข้อมูลสมาชิก
//
// สิทธิ์คุมด้วย Firestore rules:
//   cm_subscriptions/{uid}: read = เจ้าของ/แอดมิน, write = แอดมินเท่านั้น
//   cm_subscription_requests/{uid}: create/update = เจ้าของ, read/delete = แอดมิน
// (ดูไฟล์ firestore.rules ในโปรเจกต์ — ต้อง publish ผ่าน Firebase Console)
// ─────────────────────────────────────────────────────────────────────────────

const { grantMapAccess, revokeMapAccess, MAP_URL } = require('./_drive');

const PROJECT = () => process.env.FIREBASE_PROJECT_ID;
const SUBS = 'cm_subscriptions';
const REQS = 'cm_subscription_requests';
const ALLOWLIST = 'cm_allowlist';

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

async function verifyToken(idToken) {
  try {
    const r = await fetch(
      `https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=${process.env.FIREBASE_API_KEY}`,
      { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idToken }) });
    const d = await r.json();
    const u = d.users?.[0];
    return u ? { uid: u.localId, email: u.email, name: u.displayName || '' } : null;
  } catch { return null; }
}

const fsUrl = p => `https://firestore.googleapis.com/v1/projects/${PROJECT()}/databases/(default)/documents/${p}`;

async function fsGet(path, idToken) {
  const r = await fetch(fsUrl(path), { headers: { Authorization: `Bearer ${idToken}` } });
  return r.ok ? r.json() : null;
}
async function fsList(coll, idToken) {
  const r = await fetch(fsUrl(coll) + '?pageSize=300', { headers: { Authorization: `Bearer ${idToken}` } });
  if (!r.ok) return [];
  return (await r.json()).documents || [];
}
async function fsSet(path, fields, idToken) {
  const f = {};
  for (const [k, v] of Object.entries(fields)) {
    if (v === null || v === undefined) continue;
    if (typeof v === 'string')  f[k] = { stringValue: v };
    else if (typeof v === 'boolean') f[k] = { booleanValue: v };
    else if (typeof v === 'number')  f[k] = { integerValue: String(v) };
  }
  const mask = Object.keys(f).map(k => `updateMask.fieldPaths=${encodeURIComponent(k)}`).join('&');
  const r = await fetch(fsUrl(path) + '?' + mask, {
    method: 'PATCH',
    headers: { Authorization: `Bearer ${idToken}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ fields: f }),
  });
  return r.ok;
}
async function fsDelete(path, idToken) {
  const r = await fetch(fsUrl(path), { method: 'DELETE', headers: { Authorization: `Bearer ${idToken}` } });
  return r.ok;
}

function parseDoc(doc) {
  if (!doc || !doc.fields) return null;
  const o = {};
  for (const [k, v] of Object.entries(doc.fields)) {
    o[k] = v.stringValue ?? v.booleanValue ?? (v.integerValue != null ? Number(v.integerValue) : null);
  }
  o.uid = (doc.name || '').split('/').pop();
  return o;
}

function computeState(sub) {
  if (!sub || !sub.status || sub.status === 'none') return { active: false, state: 'none' };
  if (sub.status !== 'active') return { active: false, state: sub.status };
  if (sub.expiresAt && new Date(sub.expiresAt).getTime() <= Date.now())
    return { active: false, state: 'expired' };
  return { active: true, state: 'active' };
}

async function isAdmin(email, idToken) {
  const doc = await fsGet(`${ALLOWLIST}/${encodeURIComponent(email)}`, idToken);
  return doc?.fields?.role?.stringValue === 'admin';
}

module.exports = async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { idToken, action, uid: targetUid, months, plan, slipNote } = req.body || {};
  if (!idToken) return res.status(400).json({ error: 'idToken required' });
  const me = await verifyToken(idToken);
  if (!me) return res.status(401).json({ error: 'token ไม่ถูกต้อง' });

  // ── สถานะของตัวเอง ─────────────────────────────────────────────────────────
  if (action === 'me') {
    const sub = parseDoc(await fsGet(`${SUBS}/${me.uid}`, idToken));
    const st = computeState(sub);
    // สมาชิกที่ยัง active → คืนลิงก์แผนที่ (สิทธิ์ผูกกับอีเมล เปิดได้เฉพาะบัญชีตัวเอง)
    return res.status(200).json({
      ok: true, ...st,
      plan: sub?.plan || null,
      expiresAt: sub?.expiresAt || null,
      email: me.email,
      mapUrl: st.active ? MAP_URL : null,
    });
  }

  // ── สมาชิกแจ้งโอนเงิน → สร้าง request ให้แอดมินตรวจ ────────────────────────
  if (action === 'request') {
    const ok = await fsSet(`${REQS}/${me.uid}`, {
      email: me.email,
      name: me.name,
      plan: plan || 'monthly',
      note: (slipNote || '').slice(0, 300),
      requestedAt: new Date().toISOString(),
      status: 'pending',
    }, idToken);
    if (!ok) return res.status(500).json({ error: 'บันทึกคำขอไม่สำเร็จ' });
    return res.status(200).json({ ok: true, message: 'ได้รับแจ้งแล้ว — แอดมินจะเปิดสิทธิ์ให้ภายใน 24 ชม.' });
  }

  // ── ต่อไปนี้เฉพาะแอดมิน ────────────────────────────────────────────────────
  if (!(await isAdmin(me.email, idToken)))
    return res.status(403).json({ error: 'เฉพาะแอดมิน' });

  if (action === 'list') {
    const [subs, reqs] = await Promise.all([fsList(SUBS, idToken), fsList(REQS, idToken)]);
    return res.status(200).json({
      ok: true,
      subscriptions: subs.map(parseDoc).filter(Boolean)
        .map(s => ({ ...s, ...computeState(s) })),
      requests: reqs.map(parseDoc).filter(Boolean),
    });
  }

  if (!targetUid) return res.status(400).json({ error: 'uid required' });

  if (action === 'approve') {
    const cur = parseDoc(await fsGet(`${SUBS}/${targetUid}`, idToken));
    const m = Math.max(1, Math.min(12, Number(months) || 1));
    // ต่ออายุจากวันหมดเดิมถ้ายังไม่หมด — ไม่งั้นเริ่มนับจากวันนี้
    const base = cur?.expiresAt && new Date(cur.expiresAt) > new Date()
      ? new Date(cur.expiresAt) : new Date();
    const exp = new Date(base.getTime() + m * 30 * 86400000);
    const reqDoc = parseDoc(await fsGet(`${REQS}/${targetUid}`, idToken));
    const ok = await fsSet(`${SUBS}/${targetUid}`, {
      status: 'active',
      plan: plan || cur?.plan || 'monthly',
      email: cur?.email || reqDoc?.email || '',
      startedAt: cur?.startedAt || new Date().toISOString(),
      expiresAt: exp.toISOString(),
      approvedBy: me.email,
      approvedAt: new Date().toISOString(),
    }, idToken);
    if (!ok) return res.status(500).json({ error: 'อัปเดตไม่สำเร็จ' });
    await fsDelete(`${REQS}/${targetUid}`, idToken);   // เคลียร์คำขอที่อนุมัติแล้ว

    // เปิดสิทธิ์ดู Google My Maps ให้อีเมลสมาชิกด้วย (ไม่ล้มทั้ง request ถ้าพลาด)
    const memberEmail = cur?.email || reqDoc?.email || '';
    let mapResult = null;
    if (memberEmail) {
      try { mapResult = await grantMapAccess(memberEmail); } catch (e) { mapResult = { ok: false }; }
    }
    return res.status(200).json({ ok: true, expiresAt: exp.toISOString(), map: mapResult,
      message: `เปิดสิทธิ์ถึง ${exp.toISOString().slice(0, 10)}` +
               (mapResult?.ok ? ' · เปิดแผนที่ให้แล้ว' : (mapResult ? ' · (แผนที่: ' + (mapResult.skipped || 'ล้มเหลว') + ')' : '')) });
  }

  if (action === 'revoke') {
    const cur = parseDoc(await fsGet(`${SUBS}/${targetUid}`, idToken));
    const ok = await fsSet(`${SUBS}/${targetUid}`, {
      status: 'revoked',
      revokedBy: me.email,
      revokedAt: new Date().toISOString(),
    }, idToken);
    let mapResult = null;
    if (cur?.email) {
      try { mapResult = await revokeMapAccess(cur.email); } catch (e) { mapResult = { ok: false }; }
    }
    return ok ? res.status(200).json({ ok: true, map: mapResult,
                  message: 'ตัดสิทธิ์แล้ว — ดาวน์โหลดและแผนที่ถูกปิดทันที' })
              : res.status(500).json({ error: 'อัปเดตไม่สำเร็จ' });
  }

  if (action === 'purge') {
    // ลบข้อมูลสมาชิก: subscription + request + user profile (+ ถอนสิทธิ์แผนที่)
    const curP = parseDoc(await fsGet(`${SUBS}/${targetUid}`, idToken));
    if (curP?.email) { try { await revokeMapAccess(curP.email); } catch (e) {} }
    const results = await Promise.all([
      fsDelete(`${SUBS}/${targetUid}`, idToken),
      fsDelete(`${REQS}/${targetUid}`, idToken),
      fsDelete(`users/${targetUid}`, idToken),
    ]);
    return res.status(200).json({ ok: true, deleted: results.filter(Boolean).length,
      message: 'ลบข้อมูลสมาชิกแล้ว (บัญชี Google ของผู้ใช้ไม่ถูกแตะต้อง)' });
  }

  return res.status(400).json({ error: 'ไม่รู้จัก action นี้' });
};
