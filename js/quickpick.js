/**
 * quickpick.js — "กินอะไรดี?" decision helper widget
 * Renders into #quickPickRoot. Requires dataService.js (ChefMinistryData).
 * ไม่ต้องดูแลข้อมูล — ดึงจาก CM data ที่ pipeline อัปเดตอัตโนมัติ
 */
(function () {
  'use strict';

  var MOODS = [
    { key: 'all',        label: '🎲 อะไรก็ได้',   match: null },
    { key: 'thai',       label: '🍛 ไทยจัดจ้าน',  match: ['Thai', 'Street Food', 'Isaan', 'Southern'] },
    { key: 'japanese',   label: '🍣 ญี่ปุ่น',      match: ['Japanese', 'Ramen', 'Omakase', 'Sushi', 'Izakaya'] },
    { key: 'noodle',     label: '🍜 เส้น/ซด',      match: ['Ramen', 'Noodles', 'Noodle', 'Hot Pot'], nameRe: /ก๋วยเตี๋ยว|บะหมี่|เกี๊ยว|เย็นตาโฟ|ราเมน|สุกี้|ชาบู|หม้อไฟ|หม่าล่า|ramen|noodle|udon|soba/i },
    { key: 'chinese',    label: '🥟 จีน/ติ่มซำ',    match: ['Chinese', 'Dim Sum'], nameRe: /ติ่มซำ|เสี่ยวหลงเปา|dim ?sum|กวางตุ้ง|ฮ่องกง/i },
    { key: 'western',    label: '🍝 ฝรั่ง/อิตาเลียน', match: ['Italian', 'French', 'Western', 'Pizza', 'Steak'] },
    { key: 'finedining', label: '🏆 Fine Dining',  match: ['Fine Dining', 'Chef’s Table', 'Tasting'] },
    { key: 'cafe',       label: '☕ คาเฟ่/หวาน',   match: ['Cafe', 'Dessert', 'Bakery', 'Brunch'] },
    { key: 'korean',     label: '🥘 เกาหลี/ปิ้งย่าง', match: ['Korean', 'BBQ', 'Grill', 'Yakiniku'] }
  ];
  var BUDGETS = [
    { key: 'all', label: 'งบเท่าไหร่ก็ได้' },
    { key: '1',   label: '฿ ประหยัด' },
    { key: '2',   label: '฿฿ กลางๆ' },
    { key: '3',   label: '฿฿฿ พรีเมียม' },
    { key: '4',   label: '฿฿฿฿ จัดเต็ม' }
  ];

  var state = { mood: 'all', budget: 'all', lastPickName: null };

  function pool() {
    if (typeof ChefMinistryData === 'undefined') return [];
    var list = ChefMinistryData.mergeAll().filter(ChefMinistryData.scopeFilter);
    var mood = MOODS.filter(function (m) { return m.key === state.mood; })[0];
    if (mood && mood.match) {
      list = list.filter(function (r) {
        var c = ((r.cuisine || '') + ' ' + ((r.tags || []).join(' '))).toLowerCase();
        var hit = mood.match.some(function (m) { return c.indexOf(m.toLowerCase()) >= 0; });
        if (!hit && mood.nameRe) hit = mood.nameRe.test(r.name || '');
        return hit;
      });
    }
    if (state.budget !== 'all') {
      list = list.filter(function (r) { return String(r.budget || r.price_range || '') === state.budget; });
    }
    return list;
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function chipRow(items, sel, onKey) {
    return items.map(function (it) {
      var on = it.key === sel;
      return '<button data-' + onKey + '="' + it.key + '" style="cursor:pointer;font-family:inherit;font-size:12.5px;font-weight:' + (on ? '800' : '600') + ';padding:7px 14px;border-radius:99px;border:1.5px solid ' + (on ? 'var(--gold)' : 'var(--border)') + ';background:' + (on ? 'var(--gold-bg)' : '#fff') + ';color:' + (on ? 'var(--amber)' : 'var(--text-2)') + ';transition:all .15s">' + esc(it.label) + '</button>';
    }).join('');
  }

  function budgetStr(b) { var n = parseInt(b, 10); return n > 0 ? '฿'.repeat(Math.min(n, 4)) : ''; }

  function pickCard() {
    var list = pool();
    if (!list.length) {
      return '<div style="text-align:center;padding:22px;color:var(--text-2);font-size:13.5px">ยังไม่มีร้านในเงื่อนไขนี้ — ลองปรับหมวดหรืองบดู 🙏</div>';
    }
    var candidates = list.filter(function (r) { return r.name !== state.lastPickName; });
    if (!candidates.length) candidates = list;
    var r = candidates[Math.floor(Math.random() * candidates.length)];
    state.lastPickName = r.name;
    var s = ChefMinistryData.computeScore(r);
    var label = ChefMinistryData.trendLabel(s, r);
    var emoji = ChefMinistryData.trendEmoji(label);
    var rating = r.rating_gmaps || r.rating_score || 0;
    var meta = [esc(r.cuisine || ''), esc(r.area || ''), budgetStr(r.budget || r.price_range)].filter(Boolean).join(' · ');
    return (
      '<div style="background:#fff;border:1.5px solid var(--gold);border-radius:16px;padding:20px 22px;box-shadow:var(--shadow);text-align:left;animation:qpPop .25s ease">' +
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px;flex-wrap:wrap">' +
          '<div>' +
            '<div style="font-size:19px;font-weight:900;color:var(--navy)">' + esc(r.name) + '</div>' +
            '<div style="font-size:12.5px;color:var(--text-2);margin-top:4px">' + meta + '</div>' +
          '</div>' +
          '<span style="font-size:11px;font-weight:800;background:var(--green-bg);color:var(--green);border-radius:99px;padding:4px 11px;white-space:nowrap">' + emoji + ' ' + esc(label) + '</span>' +
        '</div>' +
        '<div style="display:flex;gap:14px;margin-top:12px;font-size:12px;color:var(--text-2);flex-wrap:wrap">' +
          (rating ? '<span>⭐ ' + rating.toFixed(1) + ' Google</span>' : '') +
          (s.totalReviews ? '<span>💬 ' + s.totalReviews.toLocaleString() + ' รีวิว</span>' : '') +
          (r.overlapSignal ? '<span>🎥 ' + r.overlapSignal + ' creators พูดถึง</span>' : '') +
        '</div>' +
      '</div>');
  }

  function render(withPick) {
    var root = document.getElementById('quickPickRoot');
    if (!root) return;
    root.innerHTML =
      '<div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-bottom:10px" id="qpMoods">' + chipRow(MOODS, state.mood, 'mood') + '</div>' +
      '<div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-bottom:18px" id="qpBudgets">' + chipRow(BUDGETS, state.budget, 'budget') + '</div>' +
      '<div id="qpResult" style="max-width:520px;margin:0 auto">' + (withPick ? pickCard() : '') + '</div>' +
      '<div style="margin-top:16px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap">' +
        '<button id="qpRoll" style="cursor:pointer;font-family:inherit;font-size:14.5px;font-weight:900;padding:12px 30px;border-radius:99px;border:none;background:var(--gold);color:var(--navy);box-shadow:var(--shadow)">🎲 ' + (withPick ? 'สุ่มใหม่อีกที' : 'สุ่มเลย!') + '</button>' +
        '<a href="./listing.html" style="font-size:13px;font-weight:700;color:var(--text-2);align-self:center;text-decoration:none">ดูร้านทั้งหมด →</a>' +
      '</div>';

    root.querySelectorAll('[data-mood]').forEach(function (b) {
      b.addEventListener('click', function () { state.mood = b.getAttribute('data-mood'); render(false); });
    });
    root.querySelectorAll('[data-budget]').forEach(function (b) {
      b.addEventListener('click', function () { state.budget = b.getAttribute('data-budget'); render(false); });
    });
    var roll = document.getElementById('qpRoll');
    if (roll) roll.addEventListener('click', function () { render(true); });
  }

  var style = document.createElement('style');
  style.textContent = '@keyframes qpPop{from{transform:scale(.96);opacity:.4}to{transform:scale(1);opacity:1}}';
  document.head.appendChild(style);

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { render(false); });
  else render(false);
}());
