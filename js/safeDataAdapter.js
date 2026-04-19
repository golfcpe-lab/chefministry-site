/**
 * safeDataAdapter.js — ChefMinistry safe data transformation layer
 * Loaded BEFORE data.js. Provides window.CM_SAFE global utilities.
 *
 * Purpose:
 *  - Normalise raw cuisine/tag fields coming from legacy data records
 *  - Enforce fixed 4-dimension score order (Quality→Value→Trend→Buzz)
 *  - Clamp/validate percentage values before SVG ring rendering
 *
 * Usage (plain <script> tag, no ES6 module imports needed):
 *   window.CM_SAFE.normalizePercent(val)
 *   window.CM_SAFE.migrateCategoryAndTags(record)
 *   window.CM_SAFE.getOrderedScores(scoreObj)
 */

(function (global) {
  'use strict';

  // ── Constants ────────────────────────────────────────────────────────────────

  /** Fixed canonical score dimension order. Never reorder within a card. */
  var SCORE_ORDER = ['quality', 'value', 'trend', 'buzz'];

  /**
   * Legacy cuisine strings that encode BOTH a category AND a tag.
   * Keys are the raw string; value is { category, tag }.
   */
  var CUISINE_MIGRATION_MAP = {
    'Japanese Omakase': { category: 'Japanese', tag: 'Omakase' },
    'Thai / Omakase':   { category: 'Thai',     tag: 'Omakase' },
  };

  // ── Utilities ────────────────────────────────────────────────────────────────

  /**
   * Clamp a value to [0, 100] and round to one decimal.
   * Accepts number or numeric string; returns 0 for null/undefined/NaN.
   *
   * @param  {*} val
   * @returns {number}
   */
  function normalizePercent(val) {
    var n = parseFloat(val);
    if (isNaN(n)) return 0;
    return Math.round(Math.min(100, Math.max(0, n)) * 10) / 10;
  }

  /**
   * Inspect a restaurant record's `cuisine` field.
   * If it matches a known legacy compound string, return a patched copy of
   * the record with the cuisine split into `cuisine` (clean category) and
   * the extra tag injected into `tags` (deduped).
   *
   * Non-matching records are returned as-is (no mutation of original).
   *
   * @param  {Object} record  — raw restaurant data record
   * @returns {Object}        — safe (possibly patched) record
   */
  function migrateCategoryAndTags(record) {
    if (!record || typeof record !== 'object') return record;

    var mapping = CUISINE_MIGRATION_MAP[record.cuisine];
    if (!mapping) return record;

    // Shallow-clone to avoid mutating the original data array
    var patched = Object.assign({}, record);
    patched.cuisine = mapping.category;

    // Inject tag if not already present
    var existingTags = Array.isArray(record.tags) ? record.tags.slice() : [];
    if (existingTags.indexOf(mapping.tag) === -1) {
      existingTags.unshift(mapping.tag);
    }
    patched.tags = existingTags;

    return patched;
  }

  /**
   * Given a plain object of { dimension: score } pairs, return an array of
   * { key, score } objects in the canonical SCORE_ORDER.
   * Dimensions not present in SCORE_ORDER are appended at the end (stable).
   * Missing dimensions get score 0.
   *
   * @param  {Object} scoreObj  e.g. { quality:82, buzz:64, trend:71, value:75 }
   * @returns {Array<{key:string, score:number}>}
   */
  function getOrderedScores(scoreObj) {
    if (!scoreObj || typeof scoreObj !== 'object') return [];

    var seen = {};
    var ordered = SCORE_ORDER.map(function (key) {
      seen[key] = true;
      return { key: key, score: normalizePercent(scoreObj[key] !== undefined ? scoreObj[key] : 0) };
    });

    // Append any extra dimensions not in the canonical order
    Object.keys(scoreObj).forEach(function (key) {
      if (!seen[key]) {
        ordered.push({ key: key, score: normalizePercent(scoreObj[key]) });
      }
    });

    return ordered;
  }

  // ── Export global ────────────────────────────────────────────────────────────

  global.CM_SAFE = {
    SCORE_ORDER: SCORE_ORDER,
    normalizePercent: normalizePercent,
    migrateCategoryAndTags: migrateCategoryAndTags,
    getOrderedScores: getOrderedScores,
  };

}(window));
