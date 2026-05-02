// ─────────────────────────────────────────────────────────────────────────────
// ChefMinistry Admin API — add-restaurant.js
// POST /api/add-restaurant
// Body: { idToken, placeUrl, action: 'preview' | 'add' }
//
// Env vars required (set in Vercel dashboard):
//   GOOGLE_PLACES_API_KEY   — Google Cloud → Places API key
//   GITHUB_TOKEN            — GitHub Personal Access Token (repo write)
//   FIREBASE_API_KEY        — same key as frontend (for token verify)
//   FIREBASE_PROJECT_ID     — e.g. chefministry-d50e9
// ─────────────────────────────────────────────────────────────────────────────

const GITHUB_REPO    = 'golfcpe-lab/chefministry-site';
const GITHUB_PATH    = 'scraper/export_restaurants.json';
const FIRESTORE_COLL = 'cm_allowlist';

// ── CORS helper ───────────────────────────────────────────────────────────────
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
    if (!data.users || !data.users[0]) return null;
    return data.users[0].email || null;
  } catch { return null; }
}

// ── Check Firestore allowlist → returns role or null ─────────────────────────
async function checkAllowlist(email, idToken) {
  try {
    const url = `https://firestore.googleapis.com/v1/projects/${process.env.FIREBASE_PROJECT_ID}/databases/(default)/documents/${FIRESTORE_COLL}/${encodeURIComponent(email)}`;
    const r = await fetch(url, { headers: { 'Authorization': `Bearer ${idToken}` } });
    if (!r.ok) return null;
    const doc = await r.json();
    return doc.fields?.role?.stringValue || null;
  } catch { return null; }
}

// ── Resolve Google Maps URL → place name + coordinates ───────────────────────
async function resolvePlaceUrl(rawUrl) {
  let url = rawUrl.trim();

  // Follow short URL redirects (goo.gl, maps.app.goo.gl)
  if (url.includes('goo.gl') || url.includes('maps.app')) {
    try {
      const r = await fetch(url, { method: 'HEAD', redirect: 'follow' });
      url = r.url;
    } catch { return null; }
  }

  // Extract place name from URL path: /place/NAME/@lat,lng
  const nameMatch = url.match(/\/place\/([^\/@?]+)/);
  const placeName = nameMatch ? decodeURIComponent(nameMatch[1].replace(/\+/g, ' ')) : null;

  // Extract coordinates if present
  const coordMatch = url.match(/@(-?\d+\.\d+),(-?\d+\.\d+)/);
  const lat = coordMatch ? parseFloat(coordMatch[1]) : 13.7563;
  const lng = coordMatch ? parseFloat(coordMatch[2]) : 100.5018;

  if (!placeName) return null;
  return { placeName, lat, lng, sourceUrl: rawUrl };
}

// ── Call Google Places API → restaurant details ───────────────────────────────
async function fetchPlaceDetails({ placeName, lat, lng, sourceUrl }) {
  const apiKey = process.env.FIREBASE_API_KEY;

  // Text Search (New Places API v1)
  const r = await fetch('https://places.googleapis.com/v1/places:searchText', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Goog-Api-Key': apiKey,
      'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.priceLevel,places.primaryType,places.types,places.location,places.googleMapsUri'
    },
    body: JSON.stringify({
      textQuery: `${placeName} Bangkok`,
      languageCode: 'th',
      maxResultCount: 1,
      locationBias: {
        circle: { center: { latitude: lat, longitude: lng }, radius: 5000 }
      }
    })
  });

  const data = await r.json();
  if (!data.places || !data.places.length) return null;
  const p = data.places[0];

  // Map Google place types → cuisine
  const cuisine = mapCuisine(p.primaryType, p.types || []);
  const area    = extractArea(p.formattedAddress || '');
  const budget  = mapBudget(p.priceLevel);

  return {
    id:                  `gmaps_${p.id}`,
    name:                p.displayName?.text || placeName,
    name_en:             p.displayName?.text || placeName,
    source:              'admin_added',
    address:             p.formattedAddress || '',
    place_id:            p.id,
    cuisine_normalized:  cuisine,
    cuisine:             cuisine,
    area_normalized:     area,
    area:                area,
    city:                'Bangkok',
    province:            'Bangkok',
    budget:              budget,
    budgetLabel:         '฿'.repeat(budget),
    rating_gmaps:        p.rating || 0,
    totalReviews:        p.userRatingCount || 0,
    newReviews30d:       0,
    velocityPct:         0,
    _growthRate:         0,
    _growth:             0,
    _score:              0,
    trend_label:         'Stable',
    _trendLabel:         'Stable',
    _trendEmoji:         '→',
    _isEmerging:         false,
    trendVelocity:       'stable',
    trendBadge:          '→ Stable',
    signalStrength:      'moderate',
    signalCount:         0,
    overlapSignal:       0,
    venue_type:          'restaurant',
    is_bangkok_focus:    true,
    is_restaurant_focus: true,
    candidate_status:    'admin_approved',
    scope_market:        'in_scope',
    tags:                [],
    occasions:           [],
    bookingLinks:        { googlemaps: p.googleMapsUri || sourceUrl },
    reviewerTiers:       { mega: 0, macro: 0, mid: 0 },
    recentReviewers:     [],
    cmNote:              '',
  };
}

// ── Cuisine mapping ───────────────────────────────────────────────────────────
function mapCuisine(primaryType, types) {
  const all = [primaryType, ...types].filter(Boolean).join(' ').toLowerCase();
  if (all.includes('japanese') || all.includes('sushi') || all.includes('ramen')) return 'Japanese';
  if (all.includes('thai'))           return 'Thai';
  if (all.includes('italian'))        return 'Italian';
  if (all.includes('french'))         return 'French';
  if (all.includes('chinese') || all.includes('dim_sum')) return 'Chinese';
  if (all.includes('korean'))         return 'Korean';
  if (all.includes('indian'))         return 'Indian';
  if (all.includes('seafood'))        return 'Seafood';
  if (all.includes('steak') || all.includes('beef')) return 'Steakhouse';
  if (all.includes('cafe') || all.includes('coffee')) return 'Café';
  if (all.includes('pizza'))          return 'Pizza';
  if (all.includes('burger'))         return 'Burger';
  if (all.includes('noodle') || all.includes('ramen')) return 'Noodles';
  return 'Restaurant';
}

// ── Area extraction from address ──────────────────────────────────────────────
function extractArea(address) {
  const AREAS = [
    'ทองหล่อ','เอกมัย','อารีย์','สีลม','สาทร','สุขุมวิท','พระโขนง',
    'ออนนุช','บางนา','รัชดา','ลาดพร้าว','พระราม 9','สยาม','ชิดลม',
    'เพลินจิต','นานา','อโศก','พร้อมพงษ์','ทองหล่อ','วิทยุ','หลังสวน',
    'Thonglor','Ekkamai','Ari','Silom','Sathorn','Sukhumvit','Phrom Phong',
    'Asok','Nana','Siam','Chidlom','Ploenchit','Ratchada','Lat Phrao'
  ];
  for (const a of AREAS) {
    if (address.includes(a)) return a;
  }
  return 'Bangkok';
}

// ── Budget mapping from Google priceLevel ────────────────────────────────────
function mapBudget(priceLevel) {
  const map = { PRICE_LEVEL_INEXPENSIVE: 1, PRICE_LEVEL_MODERATE: 2,
                PRICE_LEVEL_EXPENSIVE: 3, PRICE_LEVEL_VERY_EXPENSIVE: 4 };
  return map[priceLevel] || 2;
}

// ── Read export_restaurants.json from GitHub ──────────────────────────────────
async function readFromGitHub() {
  const r = await fetch(
    `https://api.github.com/repos/${GITHUB_REPO}/contents/${GITHUB_PATH}`,
    { headers: { 'Authorization': `token ${process.env.GITHUB_TOKEN}`,
                 'Accept': 'application/vnd.github.v3+json' } }
  );
  if (!r.ok) throw new Error(`GitHub read failed: ${r.status}`);
  const meta = await r.json();
  const content = Buffer.from(meta.content, 'base64').toString('utf-8');
  return { data: JSON.parse(content), sha: meta.sha };
}

// ── Write export_restaurants.json to GitHub ───────────────────────────────────
async function writeToGitHub(data, sha, commitMsg) {
  const content = Buffer.from(JSON.stringify(data, null, 2), 'utf-8').toString('base64');
  const r = await fetch(
    `https://api.github.com/repos/${GITHUB_REPO}/contents/${GITHUB_PATH}`,
    { method: 'PUT',
      headers: { 'Authorization': `token ${process.env.GITHUB_TOKEN}`,
                 'Accept': 'application/vnd.github.v3+json',
                 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: commitMsg, content, sha }) }
  );
  if (!r.ok) {
    const err = await r.json();
    throw new Error(`GitHub write failed: ${JSON.stringify(err)}`);
  }
  return r.json();
}

// ── Duplicate check ───────────────────────────────────────────────────────────
function findDuplicate(existing, newRest) {
  const newName = (newRest.name || '').toLowerCase().trim();
  const newId   = newRest.place_id || '';
  return existing.find(r => {
    if (newId && (r.place_id === newId || r.id === `gmaps_${newId}`)) return true;
    const existName = (r.name || r.name_en || '').toLowerCase().trim();
    return existName === newName;
  });
}

// ── Main handler ──────────────────────────────────────────────────────────────
module.exports = async (req, res) => {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST')    return res.status(405).json({ error: 'Method not allowed' });

  const { idToken, placeUrl, action } = req.body || {};

  if (!idToken)  return res.status(400).json({ error: 'idToken required' });
  if (!placeUrl) return res.status(400).json({ error: 'placeUrl required' });
  if (!action)   return res.status(400).json({ error: 'action required (preview|add)' });

  // 1. Verify token
  const email = await verifyToken(idToken);
  if (!email) return res.status(401).json({ error: 'Invalid or expired token' });

  // 2. Check allowlist
  const role = await checkAllowlist(email, idToken);
  if (!role) return res.status(403).json({ error: 'ไม่มีสิทธิ์เข้าถึง — ติดต่อ admin' });

  // 3. Resolve URL
  const placeRef = await resolvePlaceUrl(placeUrl);
  if (!placeRef) return res.status(400).json({ error: 'ไม่สามารถอ่าน URL ได้ — ลองวาง link จาก Google Maps โดยตรง' });

  // 4. Fetch place details
  let restaurant;
  try {
    restaurant = await fetchPlaceDetails(placeRef);
  } catch (e) {
    return res.status(500).json({ error: `Places API error: ${e.message}` });
  }
  if (!restaurant) return res.status(404).json({ error: 'ไม่พบร้านใน Google Places — ลองค้นหาชื่อร้านโดยตรง' });

  if (action === 'preview') {
    return res.status(200).json({ ok: true, restaurant });
  }

  if (action === 'add') {
    // 5. Read current DB
    let existing, sha;
    try {
      ({ data: existing, sha } = await readFromGitHub());
    } catch (e) {
      return res.status(500).json({ error: `GitHub read error: ${e.message}` });
    }

    // 6. Duplicate check
    const dup = findDuplicate(existing, restaurant);
    if (dup) return res.status(409).json({ error: 'ร้านนี้มีในฐานข้อมูลแล้ว', duplicate: dup.name });

    // 7. Stamp metadata
    restaurant.addedBy  = email;
    restaurant.addedAt  = new Date().toISOString();

    // 8. Write back
    existing.push(restaurant);
    try {
      await writeToGitHub(existing, sha,
        `admin: add ${restaurant.name} (by ${email})`);
    } catch (e) {
      return res.status(500).json({ error: `GitHub write error: ${e.message}` });
    }

    return res.status(200).json({ ok: true, restaurant,
      message: `เพิ่ม "${restaurant.name}" เรียบร้อย — Vercel จะ rebuild ภายใน ~30 วินาที` });
  }

  return res.status(400).json({ error: 'action ต้องเป็น preview หรือ add' });
};
