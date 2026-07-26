// ─────────────────────────────────────────────────────────────────────────────
// ChefMinistry — Service Worker
// กลยุทธ์:
//   - HTML / data.js / geo.js  → network-first (ข้อมูลสดเสมอ, cache ไว้ใช้ตอนออฟไลน์)
//   - CSS / JS / icons / fonts → stale-while-revalidate
//   - อย่า cache: Firebase, Google APIs, analytics
// อัปเดตเวอร์ชันทุกครั้งที่ deploy เพื่อล้าง cache เก่า
// ─────────────────────────────────────────────────────────────────────────────

const CACHE_VERSION = "cm-v20260726a";
const PRECACHE = [
  "/",
  "/index.html",
  "/listing.html",
  "/css/style.css",
  "/icons/icon-192.png",
  "/manifest.json",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE_VERSION)
      .then((c) => c.addAll(PRECACHE.map((u) => new Request(u, { cache: "reload" }))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function isNetworkFirst(url) {
  return (
    url.pathname.endsWith(".html") ||
    url.pathname === "/" ||
    url.pathname.endsWith("/data.js") ||
    url.pathname.endsWith("/dataService.js") ||
    url.pathname.endsWith("/geo.js")
  );
}

function isBypass(url) {
  return (
    url.origin !== self.location.origin ||       // Firebase / Google / CDN
    url.pathname.startsWith("/api/")
  );
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (isBypass(url)) return; // ปล่อยผ่านตรงๆ

  if (isNetworkFirst(url)) {
    // network-first: ได้ของสดเสมอ, ตกมาใช้ cache ตอนออฟไลน์
    e.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE_VERSION).then((c) => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req).then((r) => r || caches.match("/index.html")))
    );
    return;
  }

  // stale-while-revalidate สำหรับ static assets
  e.respondWith(
    caches.match(req).then((cached) => {
      const fresh = fetch(req)
        .then((res) => {
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(CACHE_VERSION).then((c) => c.put(req, copy));
          }
          return res;
        })
        .catch(() => cached);
      return cached || fresh;
    })
  );
});
