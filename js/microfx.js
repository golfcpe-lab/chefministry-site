/**
 * microfx.js — count-up stats + fresh-data badge
 */
(function () {
  'use strict';

  // ── Count-up: animate numbers in hero stats when visible ──
  function countUp(el) {
    var raw = el.textContent.trim();
    var m = raw.match(/^(\d+)(.*)$/);
    if (!m) return;
    var target = parseInt(m[1], 10), suffix = m[2] || '';
    if (!target || target < 5) return;
    var t0 = null, DUR = 900;
    function step(ts) {
      if (!t0) t0 = ts;
      var p = Math.min((ts - t0) / DUR, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function initCountUp() {
    var els = document.querySelectorAll('.hero-stat-num');
    if (!els.length || !('IntersectionObserver' in window)) return;
    var seen = false;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting && !seen) {
          seen = true;
          els.forEach(countUp);
          io.disconnect();
        }
      });
    }, { threshold: 0.4 });
    io.observe(els[0]);
  }

  // ── Fresh badge: show "อัปเดตวันนี้" when data date == today ──
  function initFreshBadge() {
    var host = document.getElementById('cmFreshBadge');
    if (!host) return;
    var d = (typeof CM_DB_STATS !== 'undefined' && CM_DB_STATS.lastUpdated) || '';
    if (!d) { host.style.display = 'none'; return; }
    var today = new Date().toISOString().slice(0, 10);
    var label = d === today ? 'ข้อมูลอัปเดตวันนี้' : 'อัปเดตล่าสุด ' + d;
    host.innerHTML = '<span class="cm-live-dot"></span> ' + label;
  }

  function init() { initCountUp(); initFreshBadge(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
}());
