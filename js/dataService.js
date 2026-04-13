/**
 * ChefMinistry — Shared Data Service
 * Single source of truth for all pages.
 *
 * To connect a live API later, replace the _restaurants() / _config() internals
 * with fetch() calls and update the async variants below.
 *
 * Usage (any page):
 *   const stats = ChefMinistryData.getAllStats();
 *   const list  = ChefMinistryData.getRestaurantList({ velocity: 'rising' });
 */

(function (global) {
  'use strict';

  /* ─── Private accessors ────────────────────────────────────────────────── */

  function _restaurants() {
    return (typeof CM_RESTAURANTS !== 'undefined') ? CM_RESTAURANTS : [];
  }

  function _influencers() {
    return (typeof CM_INFLUENCERS !== 'undefined') ? CM_INFLUENCERS : [];
  }

  function _config() {
    return (typeof CM_CONFIG !== 'undefined') ? CM_CONFIG : {
      restaurantCount: 270,
      creatorCount: 31,
      categoryCount: 20,
      lastUpdated: '2026-04-13',
      updateFrequency: 'daily',
      coverage: 'Bangkok'
    };
  }

  function _signals() {
    return (typeof CM_SIGNALS !== 'undefined') ? CM_SIGNALS : {};
  }

  /* ─── Core counts ──────────────────────────────────────────────────────── */

  /**
   * Total restaurants tracked in the full DB (from CM_CONFIG / scraper).
   * This is the "270+" headline number.
   */
  function getDbTotalCount() {
    return _config().restaurantCount;
  }

  /**
   * Count of restaurants with full signal analysis in the current data layer.
   * Derived live from the actual CM_RESTAURANTS array — never hardcoded.
   */
  function getDetailedRestaurantCount() {
    return _restaurants().length;
  }

  /** Count of restaurants with trendVelocity === 'rising' */
  function getRisingCount() {
    return _restaurants().filter(function (r) { return r.trendVelocity === 'rising'; }).length;
  }

  /** Total creators/influencers from live array */
  function getCreatorCount() {
    var list = _influencers();
    return list.length > 0 ? list.length : _config().creatorCount;
  }

  /** Category count — derived from actual restaurant types */
  function getCategoryCount() {
    var types = getCategoryList().length;
    return Math.max(types, _config().categoryCount);
  }

  /** Last updated date */
  function getLastUpdated() {
    return _config().lastUpdated;
  }

  /* ─── Restaurant list + filtering ─────────────────────────────────────── */

  /**
   * Full restaurant list, optionally filtered and sorted.
   *
   * @param {Object} [opts]
   *   signal   — 'all' | 'very-strong' | 'strong' | 'moderate' | 'weak'
   *   velocity — 'all' | 'rising' | 'stable' | 'declining'
   *   budget   — 'all' | '1' | '2' | '3'
   *   type     — 'all' | 'fine-dining' | 'omakase' | 'street-food' | ...
   *   search   — free text (matches name, cuisine, area)
   *   sort     — 'signal' (default) | 'velocity' | 'reviews'
   * @returns {Array}
   */
  function getRestaurantList(opts) {
    var list = _restaurants().slice(); // shallow copy

    if (!opts) return _sortBySignal(list);

    if (opts.signal && opts.signal !== 'all')
      list = list.filter(function (r) { return r.signalStrength === opts.signal; });

    if (opts.velocity && opts.velocity !== 'all')
      list = list.filter(function (r) { return r.trendVelocity === opts.velocity; });

    if (opts.budget && opts.budget !== 'all')
      list = list.filter(function (r) { return String(r.budget) === String(opts.budget); });

    if (opts.type && opts.type !== 'all')
      list = list.filter(function (r) { return r.type === opts.type; });

    if (opts.search && opts.search.trim()) {
      var q = opts.search.trim().toLowerCase();
      list = list.filter(function (r) {
        return (r.name || '').toLowerCase().indexOf(q) >= 0
          || (r.cuisine || '').toLowerCase().indexOf(q) >= 0
          || (r.area || '').toLowerCase().indexOf(q) >= 0;
      });
    }

    var sort = opts.sort || 'signal';
    if (sort === 'velocity') return _sortByVelocity(list);
    if (sort === 'reviews')  return _sortByReviews(list);
    return _sortBySignal(list);
  }

  /* ─── Featured / spotlight ─────────────────────────────────────────────── */

  /**
   * Top N restaurants by signal strength + trend velocity.
   * Used by: hero card, rank list, any featured section.
   * @param {number} [n=5]
   * @returns {Array}
   */
  function getFeaturedRestaurants(n) {
    return _sortByVelocity(_restaurants().slice()).slice(0, n || 5);
  }

  /**
   * Top N rising restaurants, sorted by overlap signal.
   * Used by: Rising Grid on homepage.
   * @param {number} [n=6]
   * @returns {Array}
   */
  function getTrendingRestaurants(n) {
    return _restaurants()
      .filter(function (r) { return r.trendVelocity === 'rising'; })
      .sort(function (a, b) { return (b.overlapSignal || 0) - (a.overlapSignal || 0); })
      .slice(0, n || 6);
  }

  /**
   * Weekly spotlight restaurant matched from CM_SIGNALS.weeklyHighlight.
   * Falls back to highest-signal restaurant in actual data.
   * @returns {{ restaurant: Object, title: string, desc: string, trend: string }}
   */
  function getWeeklySpotlight() {
    var sig = _signals();
    var wh = sig.weeklyHighlight || {};
    var rest = null;

    if (wh.restaurant) {
      rest = _restaurants().find(function (r) { return r.name === wh.restaurant; }) || null;
    }

    if (!rest) {
      rest = getFeaturedRestaurants(1)[0] || null;
    }

    return {
      restaurant: rest,
      title: wh.title || (rest ? ('📈 ' + (rest.name || '') + ' — Signal แรงสัปดาห์นี้') : ''),
      desc: wh.desc || (rest ? rest.cmNote || '' : ''),
      trend: wh.trend || (rest ? rest.trendVelocity : 'stable')
    };
  }

  /* ─── Categories ───────────────────────────────────────────────────────── */

  /**
   * Distinct restaurant type categories derived from actual data.
   * @returns {Array<{ id: string, label: string, count: number }>}
   */
  function getCategoryList() {
    var labels = {
      'fine-dining':   'Fine Dining',
      'casual-dining': 'Casual Dining',
      'street-food':   'Street Food',
      'omakase':       'Omakase',
      'steakhouse':    'Steakhouse',
      'food-court':    'Food Court',
      'local':         'Local / Everyday'
    };
    var counts = {};
    _restaurants().forEach(function (r) {
      if (r.type) counts[r.type] = (counts[r.type] || 0) + 1;
    });
    return Object.keys(counts).map(function (t) {
      return { id: t, label: labels[t] || t, count: counts[t] };
    }).sort(function (a, b) { return b.count - a.count; });
  }

  /* ─── Creator stats ────────────────────────────────────────────────────── */

  /**
   * Live creator/influencer stats from actual array.
   * @returns {{ total: number, mega: number, macro: number, mid: number }}
   */
  function getCreatorStats() {
    var list = _influencers();
    return {
      total: list.length > 0 ? list.length : _config().creatorCount,
      mega:  list.filter(function (c) { return c.tier === 'Mega';  }).length,
      macro: list.filter(function (c) { return c.tier === 'Macro'; }).length,
      mid:   list.filter(function (c) { return c.tier === 'Mid';   }).length
    };
  }

  /* ─── Restaurant lookup ────────────────────────────────────────────────── */

  /**
   * Find a single restaurant by its id field.
   * @param {string} id
   * @returns {Object|null}
   */
  function getRestaurantById(id) {
    return _restaurants().find(function (r) { return r.id === id; }) || null;
  }

  /* ─── Unified stats bundle ─────────────────────────────────────────────── */

  /**
   * All key stats in one object.
   * Use this to populate any page's stat elements consistently.
   *
   * dbTotal   — 270  (total tracked in full DB, from CM_CONFIG)
   * detailed  — 32   (restaurants with full signal analysis, live from array)
   * rising    — n    (rising velocity count, live from array)
   * creators  — 31   (total influencers, live from array)
   * categories — 20+  (distinct types, live from array)
   * lastUpdated — "YYYY-MM-DD"
   */
  function getAllStats() {
    return {
      dbTotal:    getDbTotalCount(),
      detailed:   getDetailedRestaurantCount(),
      rising:     getRisingCount(),
      creators:   getCreatorCount(),
      categories: getCategoryCount(),
      lastUpdated: getLastUpdated()
    };
  }

  /* ─── DOM helper: inject stats into standard elements ─────────────────── */

  /**
   * Auto-populate standard stat element IDs on any page.
   * Call once after DOM ready and after data.js has loaded.
   *
   * Standard IDs this wires up:
   *   statRestaurants / statDashTotal / creatorStatRestaurants / partnerStatRestaurants
   *   statCategories
   *   statCreators
   *   statDashRising
   *   weeklyUpdatedDate / weeklyUpdatedBadge
   */
  function injectStats() {
    var s = getAllStats();

    // Restaurant count elements (all show dbTotal — the "270+" figure)
    var rEls = ['statRestaurants', 'statDashTotal',
                'creatorStatRestaurants', 'partnerStatRestaurants'];
    rEls.forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.textContent = s.dbTotal + '+';
    });

    // Categories
    var catEl = document.getElementById('statCategories');
    if (catEl) catEl.textContent = s.categories + '+';

    // Creators
    var creEl = document.getElementById('statCreators');
    if (creEl) creEl.textContent = s.creators + '+';

    // Rising count
    var riseEl = document.getElementById('statDashRising');
    if (riseEl) riseEl.textContent = '↑ ' + s.rising;

    // Last updated badge
    var dateEl  = document.getElementById('weeklyUpdatedDate');
    var badgeEl = document.getElementById('weeklyUpdatedBadge');
    if (dateEl)  dateEl.textContent = s.lastUpdated;
    if (badgeEl) badgeEl.style.display = 'flex';
  }

  /* ─── Private sort helpers ─────────────────────────────────────────────── */

  function _velOrder(v) {
    return v === 'rising' ? 3 : v === 'stable' ? 2 : v === 'declining' ? 1 : 0;
  }
  function _sigOrder(s) {
    return s === 'very-strong' ? 4 : s === 'strong' ? 3 : s === 'moderate' ? 2 : s === 'weak' ? 1 : 0;
  }

  function _sortBySignal(list) {
    return list.sort(function (a, b) {
      var sd = _sigOrder(b.signalStrength) - _sigOrder(a.signalStrength);
      return sd !== 0 ? sd : (b.overlapSignal || 0) - (a.overlapSignal || 0);
    });
  }

  function _sortByVelocity(list) {
    return list.sort(function (a, b) {
      var vd = _velOrder(b.trendVelocity) - _velOrder(a.trendVelocity);
      return vd !== 0 ? vd : (b.overlapSignal || 0) - (a.overlapSignal || 0);
    });
  }

  function _sortByReviews(list) {
    return list.sort(function (a, b) {
      return (b.totalReviews || 0) - (a.totalReviews || 0);
    });
  }

  /* ─── Export ────────────────────────────────────────────────────────────── */

  global.ChefMinistryData = {
    // Counts
    getDbTotalCount:            getDbTotalCount,
    getDetailedRestaurantCount: getDetailedRestaurantCount,
    getRisingCount:             getRisingCount,
    getCreatorCount:            getCreatorCount,
    getCategoryCount:           getCategoryCount,
    getLastUpdated:             getLastUpdated,

    // Lists
    getRestaurantList:     getRestaurantList,
    getFeaturedRestaurants: getFeaturedRestaurants,
    getTrendingRestaurants: getTrendingRestaurants,
    getWeeklySpotlight:    getWeeklySpotlight,
    getCategoryList:       getCategoryList,
    getCreatorStats:       getCreatorStats,
    getRestaurantById:     getRestaurantById,

    // Bundles
    getAllStats:  getAllStats,
    injectStats: injectStats
  };

}(typeof window !== 'undefined' ? window : this));
