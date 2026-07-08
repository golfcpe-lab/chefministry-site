/**
 * creatorbuzz.js — "Creator พูดถึงร้านไหนสัปดาห์นี้" feed
 * ดึง scripts/youtube_reviews.json (pipeline commit ใหม่ทุกอาทิตย์) → render สด
 * ไม่ต้อง deploy ซ้ำ — ไฟล์ JSON ใหม่ = feed ใหม่อัตโนมัติ
 * Renders into #creatorBuzzRoot. แสดง 3 อันดับแรกฟรี ที่เหลือ blur ให้สมัครสมาชิก
 */
(function () {
  'use strict';

  var RATING_META = {
    exceed:          { label: 'Exceed',        color: 'var(--green)',  bg: 'var(--green-bg)',  w: 4 },
    above_average:   { label: 'Above Average', color: 'var(--blue)',   bg: 'var(--blue-bg)',   w: 3 },
    average:         { label: 'Average',       color: 'var(--amber)',  bg: 'var(--amber-bg)',  w: 2 },
    need_to_improve: { label: 'Need to Improve', color: 'var(--red)',  bg: 'var(--red-bg)',    w: 1 }
  };
  var TIER_W = { Mega: 3, Macro: 2, Mid: 1 };
  var FREE_COUNT = 3;

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function card(rv, rank, blurred) {
    var meta = RATING_META[rv.rating] || RATING_META.average;
    var tierBadge = rv.tier ? '<span style="font-size:10px;font-weight:800;background:var(--purple-bg);color:var(--purple);border-radius:99px;padding:2px 8px">' + esc(rv.tier) + '</span>' : '';
    var inner =
      '<div style="display:flex;gap:12px;align-items:flex-start">' +
        '<div style="font-size:17px;font-weight:900;color:var(--gold);min-width:28px;text-align:center">' + rank + '</div>' +
        '<div style="flex:1;min-width:0">' +
          '<div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;align-items:center">' +
            '<div style="font-size:14.5px;font-weight:800;color:var(--navy)">' + esc(rv.restaurant) + '</div>' +
            '<span style="font-size:10.5px;font-weight:800;background:' + meta.bg + ';color:' + meta.color + ';border-radius:99px;padding:3px 10px;white-space:nowrap">' + meta.label + '</span>' +
          '</div>' +
          '<div style="font-size:11.5px;color:var(--text-2);margin-top:2px">' + esc(rv.cuisine || '') + (rv.area ? ' · ' + esc(rv.area) : '') + '</div>' +
          '<div style="font-size:12.5px;color:var(--text);margin-top:7px;line-height:1.55;font-style:italic">“' + esc(rv.video_title || '') + '”</div>' +
          '<div style="display:flex;gap:8px;margin-top:8px;align-items:center;flex-wrap:wrap">' +
            '<span style="font-size:11.5px;font-weight:700;color:var(--text-2)">🎥 ' + esc(rv.influencer) + '</span>' + tierBadge +
            (rv.video_url && !blurred ? '<a href="' + esc(rv.video_url) + '" target="_blank" rel="noopener" style="font-size:11px;font-weight:700;color:var(--blue);text-decoration:none">ดูคลิป →</a>' : '') +
          '</div>' +
        '</div>' +
      '</div>';
    return '<div style="background:#fff;border:1px solid var(--border);border-radius:14px;padding:16px 18px;' + (blurred ? 'filter:blur(5px);user-select:none;pointer-events:none' : '') + '">' + inner + '</div>';
  }

  function render(data) {
    var root = document.getElementById('creatorBuzzRoot');
    if (!root) return;
    var reviews = (data && data.reviews) || [];
    if (!reviews.length) { root.closest('section') && (root.closest('section').style.display = 'none'); return; }

    // Rank: rating tier > influencer tier > recency
    reviews.sort(function (a, b) {
      var d = ((RATING_META[b.rating] || {}).w || 0) - ((RATING_META[a.rating] || {}).w || 0);
      if (d) return d;
      d = (TIER_W[b.tier] || 0) - (TIER_W[a.tier] || 0);
      if (d) return d;
      return String(b.published || '').localeCompare(String(a.published || ''));
    });

    var shown = reviews.slice(0, 8);
    var html = '<div style="display:grid;gap:12px">';
    shown.forEach(function (rv, i) { html += card(rv, i + 1, i >= FREE_COUNT); });
    html += '</div>';

    if (reviews.length > FREE_COUNT) {
      html +=
        '<div style="text-align:center;margin-top:-190px;position:relative;z-index:2;padding:60px 20px 20px;background:linear-gradient(to bottom, transparent, var(--cream) 55%)">' +
          '<div style="font-size:14px;font-weight:800;color:var(--navy);margin-bottom:6px">🔒 อีก ' + (reviews.length - FREE_COUNT) + ' ร้านที่ creator รีวิวสัปดาห์นี้</div>' +
          '<div style="font-size:12.5px;color:var(--text-2);margin-bottom:14px">สมัครฟรี — เห็น Creator Signal ครบทุกร้าน ทุกสัปดาห์</div>' +
          '<a href="./listing.html#signup" onclick="if(typeof CM_AUTH!==\'undefined\'&&CM_AUTH.signIn){CM_AUTH.signIn();return false}" style="display:inline-block;background:var(--navy);color:#fff;font-size:13.5px;font-weight:800;border-radius:99px;padding:11px 28px;text-decoration:none;box-shadow:var(--shadow)">สมัครสมาชิกฟรี →</a>' +
        '</div>';
    }

    var badge = document.getElementById('creatorBuzzDate');
    if (badge && data.generated_at) badge.textContent = 'อัปเดต ' + data.generated_at;
    root.innerHTML = html;
  }

  function init() {
    fetch('./scripts/youtube_reviews.json', { cache: 'no-cache' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) { if (d) render(d); })
      .catch(function () { /* เงียบ — section ซ่อนตัวเองถ้าไม่มีข้อมูล */ });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
}());
