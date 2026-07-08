/**
 * suggest.js — "เสนอร้านเด็ด" community suggestion box
 * แปะ Google Maps link → เก็บเข้า Firestore (cm_suggestions)
 * pipeline ตรวจเกณฑ์อัตโนมัติ: ผ่าน = ขึ้นเว็บเป็น Community Pick, เกือบผ่าน = shortlist
 * ต้อง sign in ก่อนส่ง (กันสแปม + ได้สมาชิกเพิ่ม)
 */
(function () {
  'use strict';

  var VALID_HOST = /(^|\.)((google\.[a-z.]+)|(maps\.app\.goo\.gl)|(goo\.gl)|(g\.co))$/i;

  function isMapsLink(url) {
    try {
      var u = new URL(url.trim());
      if (!VALID_HOST.test(u.hostname)) return false;
      return u.hostname.indexOf('goo.gl') >= 0 || u.hostname === 'g.co' ||
             u.pathname.indexOf('/maps') === 0 || u.hostname.indexOf('maps.') === 0;
    } catch (e) { return false; }
  }

  function setMsg(html, color) {
    var m = document.getElementById('cmSuggestMsg');
    if (m) { m.innerHTML = html; m.style.color = color || 'var(--text-2)'; }
  }

  function submit() {
    var input = document.getElementById('cmSuggestUrl');
    var note  = document.getElementById('cmSuggestNote');
    var btn   = document.getElementById('cmSuggestBtn');
    var url   = (input && input.value || '').trim();

    if (!url) { setMsg('แปะลิงก์ Google Maps ของร้านก่อนนะ', 'var(--amber)'); return; }
    if (!isMapsLink(url)) {
      setMsg('ลิงก์นี้ไม่ใช่ Google Maps — กดปุ่ม Share ในแอป Google Maps แล้วคัดลอกลิงก์มาแปะ', 'var(--red)');
      return;
    }
    var user = (typeof CM_AUTH !== 'undefined') ? CM_AUTH.getUser() : null;
    if (!user) {
      setMsg('อีกนิดเดียว — sign in ด้วย Google ก่อน แล้วกดส่งอีกครั้ง (ฟรี ไม่กี่วินาที)', 'var(--amber)');
      if (typeof CM_AUTH !== 'undefined') CM_AUTH.signIn();
      return;
    }

    btn.disabled = true; btn.style.opacity = '.6';
    setMsg('กำลังส่ง…');
    firebase.firestore().collection('cm_suggestions').add({
      url: url.slice(0, 450),
      note: ((note && note.value) || '').slice(0, 200),
      submittedBy: user.email || user.uid,
      createdAt: firebase.firestore.FieldValue.serverTimestamp(),
      status: 'pending'
    }).then(function () {
      input.value = ''; if (note) note.value = '';
      setMsg('✅ รับเรื่องแล้ว! ระบบจะตรวจข้อมูลร้านอัตโนมัติ ถ้าผ่านเกณฑ์ ร้านจะขึ้นบนเว็บพร้อมป้าย Community Pick', 'var(--green)');
      btn.disabled = false; btn.style.opacity = '1';
    }).catch(function (e) {
      console.warn('[suggest]', e);
      setMsg('ส่งไม่สำเร็จ (' + (e.code || 'error') + ') — ลองใหม่อีกครั้ง หรือแจ้งเราทาง LINE @chefministry', 'var(--red)');
      btn.disabled = false; btn.style.opacity = '1';
    });
  }

  function init() {
    var btn = document.getElementById('cmSuggestBtn');
    if (btn) btn.addEventListener('click', submit);
    var input = document.getElementById('cmSuggestUrl');
    if (input) input.addEventListener('keydown', function (e) { if (e.key === 'Enter') submit(); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
}());
