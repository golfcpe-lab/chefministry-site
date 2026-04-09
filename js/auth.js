// ─────────────────────────────────────────────────────────────────────────────
// ChefMinistry — Auth Module
// Firebase Auth (Google Sign-in) + Firestore (user tiers)
//
// Tiers:
//   guest  → ไม่ได้ login (เห็นแค่ teaser)
//   free   → login ด้วย Gmail แล้ว (เห็น Signal/INF data เต็ม)
//   paid   → admin set isPaid:true ใน Firestore (unlock export + advanced)
// ─────────────────────────────────────────────────────────────────────────────

const CM_AUTH = (() => {
  "use strict";

  // ── State ──────────────────────────────────────────────────────────────────
  let _user     = null;   // Firebase user object
  let _tier     = "guest"; // 'guest' | 'free' | 'paid'
  let _db       = null;
  let _auth     = null;
  let _ready    = false;
  const _listeners = [];

  // ── Firebase init ──────────────────────────────────────────────────────────
  function init() {
    if (!window.firebase || !window.CM_FIREBASE_CONFIG) {
      console.warn("[CM_AUTH] Firebase หรือ config ยังไม่โหลด");
      return;
    }
    if (!firebase.apps.length) {
      firebase.initializeApp(CM_FIREBASE_CONFIG);
    }
    _auth = firebase.auth();
    _db   = firebase.firestore();

    // Listen to auth state
    _auth.onAuthStateChanged(async (user) => {
      _user = user;
      if (!user) {
        _setTier("guest");
        return;
      }
      // ตรวจสอบว่าเป็น Gmail (google.com provider) เท่านั้น
      const isGoogle = user.providerData.some(p => p.providerId === "google.com");
      if (!isGoogle) {
        await _auth.signOut();
        _setTier("guest");
        return;
      }
      // โหลด tier จาก Firestore
      try {
        const doc = await _db.collection("users").doc(user.uid).get();
        if (!doc.exists) {
          // สร้าง user doc ใหม่ (free tier)
          await _db.collection("users").doc(user.uid).set({
            email:     user.email,
            name:      user.displayName || "",
            photoURL:  user.photoURL || "",
            tier:      "free",
            isPaid:    false,
            createdAt: firebase.firestore.FieldValue.serverTimestamp(),
          });
          _setTier("free");
        } else {
          const data = doc.data();
          _setTier(data.isPaid ? "paid" : "free");
        }
      } catch (e) {
        console.warn("[CM_AUTH] Firestore error:", e.message);
        _setTier("free"); // ถ้าอ่าน Firestore ไม่ได้ ให้เป็น free ก่อน
      }
    });
  }

  function _setTier(tier) {
    _tier  = tier;
    _ready = true;
    _listeners.forEach(fn => fn(tier, _user));
    _applyGating();
  }

  // ── Sign in / out ──────────────────────────────────────────────────────────
  async function signIn() {
    if (!_auth) return;
    const provider = new firebase.auth.GoogleAuthProvider();
    provider.setCustomParameters({ prompt: "select_account" });
    try {
      await _auth.signInWithPopup(provider);
    } catch (e) {
      if (e.code !== "auth/popup-closed-by-user") {
        alert("เข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่อีกครั้ง");
      }
    }
  }

  async function signOut() {
    if (!_auth) return;
    await _auth.signOut();
  }

  function getTier()  { return _tier; }
  function getUser()  { return _user; }
  function isReady()  { return _ready; }

  function onTierChange(fn) {
    _listeners.push(fn);
    if (_ready) fn(_tier, _user); // fire immediately ถ้า ready แล้ว
  }

  // ── UI Gating ─────────────────────────────────────────────────────────────
  // element ที่มี data-require="free" → ต้อง login
  // element ที่มี data-require="paid" → ต้อง paid
  function _applyGating() {
    const els = document.querySelectorAll("[data-require]");
    els.forEach(el => {
      const need = el.getAttribute("data-require");
      const ok = (need === "free" && (_tier === "free" || _tier === "paid"))
              || (need === "paid" && _tier === "paid");
      if (ok) {
        _unlock(el);
      } else {
        _lock(el, need);
      }
    });

    // อัปเดต nav
    _updateNav();
  }

  function _lock(el, tier) {
    // เอา overlay เก่าออกก่อน
    const old = el.querySelector(".cm-auth-overlay");
    if (old) old.remove();
    el.style.position = "relative";

    const overlay = document.createElement("div");
    overlay.className = "cm-auth-overlay";
    overlay.style.cssText = `
      position:absolute;inset:0;z-index:10;
      display:flex;flex-direction:column;align-items:center;justify-content:center;
      background:rgba(255,255,255,0.82);backdrop-filter:blur(6px);
      border-radius:inherit;gap:10px;padding:20px;text-align:center;
    `;
    const isPaid = tier === "paid";
    overlay.innerHTML = `
      <div style="font-size:28px">${isPaid ? "⭐" : "🔒"}</div>
      <div style="font-weight:900;font-size:14px;color:#0d1f3c">
        ${isPaid ? "Paid Members Only" : "ต้อง Login เพื่อดูข้อมูล"}
      </div>
      <div style="font-size:12px;color:#64748b;max-width:220px;line-height:1.5">
        ${isPaid
          ? "อัปเกรดแพ็กเกจเพื่อปลดล็อก feature นี้"
          : "Sign in ด้วย Gmail เพื่อดู Signal & INF data แบบเต็ม ฟรี"}
      </div>
      ${!isPaid
        ? `<button class="cm-signin-cta btn btn-primary btn-sm" style="margin-top:4px;font-size:13px">
             <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
                  style="width:16px;height:16px;vertical-align:middle;margin-right:6px">Sign in with Google
           </button>`
        : `<a href="mailto:hello@chefministry.com" class="btn btn-sm" style="background:var(--gold);color:#0d1f3c;font-size:13px;margin-top:4px">ติดต่อ Upgrade →</a>`
      }
    `;
    el.appendChild(overlay);

    // bind CTA
    const cta = overlay.querySelector(".cm-signin-cta");
    if (cta) cta.addEventListener("click", signIn);

    // blur เนื้อหาข้างใน
    el.querySelectorAll(":scope > *:not(.cm-auth-overlay)").forEach(child => {
      child.style.filter    = "blur(5px)";
      child.style.userSelect = "none";
      child.style.pointerEvents = "none";
    });
  }

  function _unlock(el) {
    const overlay = el.querySelector(".cm-auth-overlay");
    if (overlay) overlay.remove();
    el.querySelectorAll(":scope > *:not(.cm-auth-overlay)").forEach(child => {
      child.style.filter    = "";
      child.style.userSelect = "";
      child.style.pointerEvents = "";
    });
  }

  // ── Nav UI ─────────────────────────────────────────────────────────────────
  function _updateNav() {
    const navBtns = document.querySelectorAll(".cm-auth-nav");
    navBtns.forEach(btn => {
      if (_tier === "guest") {
        btn.innerHTML = `
          <button class="cm-nav-signin btn btn-primary btn-sm"
                  style="font-size:13px;padding:6px 14px;display:flex;align-items:center;gap:6px">
            <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
                 style="width:15px;height:15px">Sign in
          </button>`;
        btn.querySelector(".cm-nav-signin").addEventListener("click", signIn);
      } else {
        const u = _user;
        const avatar = u.photoURL
          ? `<img src="${u.photoURL}" style="width:28px;height:28px;border-radius:50%;object-fit:cover;border:2px solid var(--gold)">`
          : `<div style="width:28px;height:28px;border-radius:50%;background:var(--gold);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:12px;color:#0d1f3c">${(u.displayName||u.email||"?")[0].toUpperCase()}</div>`;
        const tierBadge = _tier === "paid"
          ? `<span style="font-size:9px;background:var(--gold);color:#0d1f3c;font-weight:900;padding:2px 7px;border-radius:99px;letter-spacing:.06em">PAID</span>`
          : `<span style="font-size:9px;background:#e2f5ea;color:#0a6b43;font-weight:900;padding:2px 7px;border-radius:99px;letter-spacing:.06em">FREE</span>`;
        btn.innerHTML = `
          <div class="cm-user-menu" style="position:relative;cursor:pointer">
            <div class="cm-user-trigger" style="display:flex;align-items:center;gap:7px">
              ${avatar}${tierBadge}
            </div>
            <div class="cm-user-dropdown" style="
              display:none;position:absolute;right:0;top:calc(100% + 8px);
              background:#fff;border:1px solid var(--border);border-radius:12px;
              box-shadow:0 8px 24px rgba(0,0,0,.12);min-width:200px;padding:8px;z-index:999">
              <div style="padding:8px 12px 10px;border-bottom:1px solid var(--border);margin-bottom:6px">
                <div style="font-weight:800;font-size:13px;color:#0d1f3c">${u.displayName||""}</div>
                <div style="font-size:11px;color:#64748b;margin-top:2px">${u.email||""}</div>
              </div>
              ${_tier === "free" ? `<a href="mailto:hello@chefministry.com" style="display:block;padding:7px 12px;font-size:12px;font-weight:700;color:var(--gold);text-decoration:none;border-radius:8px" onmouseover="this.style.background='#faf7f0'" onmouseout="this.style.background=''">⭐ Upgrade to Paid</a>` : ""}
              <button class="cm-nav-signout" style="width:100%;text-align:left;padding:7px 12px;font-size:12px;font-weight:700;color:#ef4444;background:none;border:none;cursor:pointer;border-radius:8px" onmouseover="this.style.background='#fef2f2'" onmouseout="this.style.background=''">↩ Sign out</button>
            </div>
          </div>`;
        const trigger  = btn.querySelector(".cm-user-trigger");
        const dropdown = btn.querySelector(".cm-user-dropdown");
        const signoutBtn = btn.querySelector(".cm-nav-signout");
        trigger.addEventListener("click", (e) => {
          e.stopPropagation();
          dropdown.style.display = dropdown.style.display === "none" ? "block" : "none";
        });
        document.addEventListener("click", () => { dropdown.style.display = "none"; }, { once: false });
        if (signoutBtn) signoutBtn.addEventListener("click", signOut);
      }
    });
  }

  // ── Public API ─────────────────────────────────────────────────────────────
  return { init, signIn, signOut, getTier, getUser, isReady, onTierChange };
})();

// Auto-init เมื่อ DOM ready
document.addEventListener("DOMContentLoaded", () => CM_AUTH.init());
