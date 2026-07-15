// ─────────────────────────────────────────────────────────────────────────────
// ChefMinistry — PWA Module
// 1. ลงทะเบียน service worker (ทุกคน — ได้ speed + offline)
// 2. ปุ่ม "ติดตั้งแอป" — แสดงเฉพาะสมาชิกที่ login แล้ว (free/paid)
//    - Android/Chrome: ใช้ beforeinstallprompt → ติดตั้งได้ในคลิกเดียว
//    - iOS Safari:     แสดงวิธี Add to Home Screen (Apple ไม่มี prompt API)
// ─────────────────────────────────────────────────────────────────────────────

const CM_PWA = (() => {
  "use strict";

  let _deferredPrompt = null;
  let _tier = "guest";
  const DISMISS_KEY = "cm_pwa_dismissed";
  const IS_STANDALONE =
    window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;
  const IS_IOS = /iphone|ipad|ipod/i.test(navigator.userAgent) && !window.MSStream;
  const IS_SAMSUNG = /SamsungBrowser/i.test(navigator.userAgent);

  // ── 1. Service worker ─────────────────────────────────────────────────────
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/sw.js").catch((e) => {
        console.warn("[CM_PWA] SW register failed:", e.message);
      });
    });
  }

  // ── 2. Install prompt ─────────────────────────────────────────────────────
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    _deferredPrompt = e;
    _refresh();
  });

  window.addEventListener("appinstalled", () => {
    _deferredPrompt = null;
    _removeBtn();
    try { localStorage.setItem(DISMISS_KEY, "installed"); } catch (_) {}
  });

  function _canShow() {
    if (IS_STANDALONE) return false;                     // เปิดจากแอปอยู่แล้ว
    if (_tier === "guest") return false;                 // ยังไม่ login
    let dismissed = null;
    try { dismissed = localStorage.getItem(DISMISS_KEY); } catch (_) {}
    if (dismissed === "installed") return false;
    if (dismissed && Date.now() - Number(dismissed) < 7 * 864e5) return false; // ปิดไป < 7 วัน
    return !!_deferredPrompt || IS_IOS;
  }

  // ── UI ────────────────────────────────────────────────────────────────────
  function _removeBtn() {
    const el = document.getElementById("cmPwaInstall");
    if (el) el.remove();
  }

  function _refresh() {
    _removeBtn();
    if (!_canShow()) return;

    const wrap = document.createElement("div");
    wrap.id = "cmPwaInstall";
    wrap.style.cssText =
      "position:fixed;bottom:18px;right:18px;z-index:9999;display:flex;align-items:center;gap:8px;" +
      "background:#0f1f3c;color:#fff;border-radius:14px;padding:12px 16px;" +
      "box-shadow:0 6px 24px rgba(15,31,60,.35);font-size:14px;font-weight:700;cursor:pointer;" +
      "max-width:calc(100vw - 36px)";
    wrap.innerHTML =
      '<span style="font-size:20px">📲</span>' +
      "<span>ติดตั้งแอป ChefMinistry</span>" +
      '<span id="cmPwaClose" style="margin-left:6px;opacity:.6;font-size:16px;padding:2px 6px">✕</span>';

    wrap.addEventListener("click", async (ev) => {
      if (ev.target && ev.target.id === "cmPwaClose") {
        try { localStorage.setItem(DISMISS_KEY, String(Date.now())); } catch (_) {}
        _removeBtn();
        return;
      }
      if (_deferredPrompt) {
        // Samsung Internet ห่อ PWA เป็น APK ที่ target SDK เก่า → Play Protect
        // จะเตือน "Unsafe app blocked" กับทุก PWA — แจ้งผู้ใช้ล่วงหน้าว่าปกติ
        if (IS_SAMSUNG && !document.getElementById("cmPwaSamsungNote")) {
          _showSamsungNote();
          return;
        }
        _deferredPrompt.prompt();
        const choice = await _deferredPrompt.userChoice;
        if (choice && choice.outcome === "accepted") _removeBtn();
        _deferredPrompt = null;
      } else if (IS_IOS) {
        _showIosGuide();
      }
    });

    document.body.appendChild(wrap);
  }

  function _showSamsungNote() {
    const m = document.createElement("div");
    m.id = "cmPwaSamsungNote";
    m.style.cssText =
      "position:fixed;inset:0;z-index:10000;background:rgba(15,31,60,.55);" +
      "display:flex;align-items:flex-end;justify-content:center";
    m.innerHTML =
      '<div style="background:#fff;border-radius:18px 18px 0 0;padding:24px 22px 34px;max-width:420px;width:100%;font-size:14.5px;line-height:1.7;color:#0f1f3c">' +
      '<div style="font-weight:800;font-size:17px;margin-bottom:10px">📲 ก่อนติดตั้งบน Samsung Internet</div>' +
      '<div>เบราว์เซอร์ Samsung อาจขึ้นเตือน <b>"Unsafe app blocked"</b> จาก Play Protect — ' +
      'เป็นพฤติกรรมของ Samsung Internet กับเว็บแอปทุกตัว ไม่ใช่ปัญหาของ ChefMinistry</div>' +
      '<div style="margin-top:8px">เลือกได้ 2 ทาง: กด <b>Install anyway</b> (ปลอดภัย — เป็นแค่ shortcut ของเว็บนี้) ' +
      'หรือติดตั้งผ่าน <b>Chrome</b> จะไม่มีคำเตือน</div>' +
      '<button id="cmPwaSamsungGo" style="margin-top:16px;width:100%;padding:12px;border:0;border-radius:10px;background:#0f1f3c;color:#fff;font-weight:700;font-size:15px">ติดตั้งต่อ</button>' +
      '<button id="cmPwaSamsungCancel" style="margin-top:8px;width:100%;padding:11px;border:1px solid #d8d5cc;border-radius:10px;background:#fff;color:#0f1f3c;font-weight:700;font-size:14px">ไว้ก่อน</button>' +
      "</div>";
    m.addEventListener("click", async (ev) => {
      if (ev.target === m || ev.target.id === "cmPwaSamsungCancel") { m.remove(); return; }
      if (ev.target.id === "cmPwaSamsungGo") {
        m.remove();
        if (_deferredPrompt) {
          _deferredPrompt.prompt();
          const choice = await _deferredPrompt.userChoice;
          if (choice && choice.outcome === "accepted") _removeBtn();
          _deferredPrompt = null;
        }
      }
    });
    document.body.appendChild(m);
  }

  function _showIosGuide() {
    const old = document.getElementById("cmPwaIosGuide");
    if (old) { old.remove(); return; }
    const m = document.createElement("div");
    m.id = "cmPwaIosGuide";
    m.style.cssText =
      "position:fixed;inset:0;z-index:10000;background:rgba(15,31,60,.55);" +
      "display:flex;align-items:flex-end;justify-content:center";
    m.innerHTML =
      '<div style="background:#fff;border-radius:18px 18px 0 0;padding:24px 22px 34px;max-width:420px;width:100%;font-size:15px;line-height:1.7;color:#0f1f3c">' +
      '<div style="font-weight:800;font-size:17px;margin-bottom:10px">📲 ติดตั้ง ChefMinistry บน iPhone</div>' +
      '<div>1. กดปุ่ม <b>แชร์</b> <span style="border:1px solid #ccc;border-radius:6px;padding:1px 7px">⬆️</span> ที่แถบด้านล่างของ Safari</div>' +
      '<div>2. เลื่อนหา <b>"เพิ่มไปยังหน้าจอโฮม"</b> (Add to Home Screen)</div>' +
      '<div>3. กด <b>เพิ่ม</b> — เสร็จแล้ว! เปิดใช้ได้จากหน้าจอโฮมเหมือนแอปทั่วไป</div>' +
      '<button style="margin-top:16px;width:100%;padding:12px;border:0;border-radius:10px;background:#0f1f3c;color:#fff;font-weight:700;font-size:15px" onclick="document.getElementById(\'cmPwaIosGuide\').remove()">เข้าใจแล้ว</button>' +
      "</div>";
    m.addEventListener("click", (ev) => { if (ev.target === m) m.remove(); });
    document.body.appendChild(m);
  }

  // ── login gate ────────────────────────────────────────────────────────────
  function _bindAuth() {
    if (typeof CM_AUTH !== "undefined" && CM_AUTH.onTierChange) {
      CM_AUTH.onTierChange((tier) => { _tier = tier; _refresh(); });
    } else {
      setTimeout(_bindAuth, 500); // รอ auth.js โหลด
    }
  }
  document.addEventListener("DOMContentLoaded", _bindAuth);

  return { refresh: _refresh };
})();
