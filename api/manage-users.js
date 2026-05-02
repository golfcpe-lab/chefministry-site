// ─────────────────────────────────────────────────────────────────────────────
// ChefMinistry Admin API — manage-users.js
// POST /api/manage-users
// Body: { idToken, action: 'list' | 'add' | 'remove', email?, role? }
//
// Only users with role='admin' in cm_allowlist can call this endpoint.
// ─────────────────────────────────────────────────────────────────────────────

const FIRESTORE_COLL = 'cm_allowlist';

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

// ── Verify Firebase ID token → returns email or null ─────────────────────────
async function verifyToken(idToken) {
  try {
    const r = await fetch(
      `https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=${process.env.FIREBASE_API_KEY}`,
      { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idToken }) }
    );
    const data = await r.json();
    return data.users?.[0]?.email || null;
  } catch { return null; }
}

// ── Firestore REST helpers ────────────────────────────────────────────────────
function fsUrl(docPath) {
  return `https://firestore.googleapis.com/v1/projects/${process.env.FIREBASE_PROJECT_ID}/databases/(default)/documents/${docPath}`;
}

async function fsGet(docPath, idToken) {
  const r = await fetch(fsUrl(docPath), {
    headers: { 'Authorization': `Bearer ${idToken}` }
  });
  if (r.status === 404) return null;
  if (!r.ok) return null;
  return r.json();
}

async function fsList(collPath, idToken) {
  const r = await fetch(fsUrl(collPath), {
    headers: { 'Authorization': `Bearer ${idToken}` }
  });
  if (!r.ok) return [];
  const data = await r.json();
  return data.documents || [];
}

async function fsSet(docPath, fields, idToken) {
  // Build Firestore field map
  const fsFields = {};
  for (const [k, v] of Object.entries(fields)) {
    if (typeof v === 'string')  fsFields[k] = { stringValue: v };
    if (typeof v === 'boolean') fsFields[k] = { booleanValue: v };
    if (typeof v === 'number')  fsFields[k] = { integerValue: String(v) };
  }
  const r = await fetch(fsUrl(docPath), {
    method: 'PATCH',
    headers: { 'Authorization': `Bearer ${idToken}`,
               'Content-Type': 'application/json' },
    body: JSON.stringify({ fields: fsFields })
  });
  return r.ok;
}

async function fsDelete(docPath, idToken) {
  const r = await fetch(fsUrl(docPath), {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${idToken}` }
  });
  return r.ok;
}

// ── Parse Firestore doc → plain object ───────────────────────────────────────
function parseDoc(doc) {
  if (!doc || !doc.fields) return null;
  const obj = {};
  for (const [k, v] of Object.entries(doc.fields)) {
    obj[k] = v.stringValue ?? v.booleanValue ?? v.integerValue ?? null;
  }
  // Extract email from document name path
  const parts = (doc.name || '').split('/');
  obj.email = decodeURIComponent(parts[parts.length - 1]);
  return obj;
}

// ── Main handler ──────────────────────────────────────────────────────────────
module.exports = async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST')    return res.status(405).json({ error: 'Method not allowed' });

  const { idToken, action, email: targetEmail, role } = req.body || {};
  if (!idToken) return res.status(400).json({ error: 'idToken required' });
  if (!action)  return res.status(400).json({ error: 'action required' });

  // 1. Verify token
  const callerEmail = await verifyToken(idToken);
  if (!callerEmail) return res.status(401).json({ error: 'Invalid token' });

  // 2. Check caller is admin
  const callerDoc = await fsGet(`${FIRESTORE_COLL}/${encodeURIComponent(callerEmail)}`, idToken);
  const callerRole = callerDoc?.fields?.role?.stringValue;
  if (callerRole !== 'admin') return res.status(403).json({ error: 'Admin only' });

  // ── LIST ──────────────────────────────────────────────────────────────────
  if (action === 'list') {
    const docs = await fsList(FIRESTORE_COLL, idToken);
    const users = docs.map(parseDoc).filter(Boolean);
    return res.status(200).json({ ok: true, users });
  }

  // ── ADD ───────────────────────────────────────────────────────────────────
  if (action === 'add') {
    if (!targetEmail) return res.status(400).json({ error: 'email required' });
    const targetRole = role === 'admin' ? 'admin' : 'editor';

    // Check if already exists
    const existing = await fsGet(`${FIRESTORE_COLL}/${encodeURIComponent(targetEmail)}`, idToken);
    if (existing) return res.status(409).json({ error: `${targetEmail} มีสิทธิ์อยู่แล้ว` });

    const ok = await fsSet(`${FIRESTORE_COLL}/${encodeURIComponent(targetEmail)}`, {
      role:       targetRole,
      grantedBy:  callerEmail,
      grantedAt:  new Date().toISOString(),
      active:     true
    }, idToken);

    if (!ok) return res.status(500).json({ error: 'Firestore write failed' });
    return res.status(200).json({ ok: true, message: `เพิ่ม ${targetEmail} (${targetRole}) เรียบร้อย` });
  }

  // ── REMOVE ────────────────────────────────────────────────────────────────
  if (action === 'remove') {
    if (!targetEmail) return res.status(400).json({ error: 'email required' });
    if (targetEmail === callerEmail) return res.status(400).json({ error: 'ไม่สามารถลบสิทธิ์ตัวเองได้' });

    const ok = await fsDelete(`${FIRESTORE_COLL}/${encodeURIComponent(targetEmail)}`, idToken);
    if (!ok) return res.status(500).json({ error: 'Firestore delete failed' });
    return res.status(200).json({ ok: true, message: `ลบสิทธิ์ ${targetEmail} เรียบร้อย` });
  }

  return res.status(400).json({ error: 'action ต้องเป็น list, add, หรือ remove' });
};
