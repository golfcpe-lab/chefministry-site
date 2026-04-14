/**
 * ChefMinistry — dataService.js (v6 — complete, tolerant, crash-safe)
 *
 * Fixes applied:
 *   1. _scopeFilter: tolerant — only excludes explicit out-of-scope records
 *   2. All functions that index.html / listing.html call are defined
 *   3. _computeScore uses totalReviews (canonical field)
 *   4. injectStats uses correct element IDs from HTML
 *   5. Every exported method guarded with try/catch
 */
(function (global) {
  'use strict';

  /* ─── Accessors ──────────────────────────────────────────────────────────── */
  function _restaurants()  { return (typeof CM_RESTAURANTS !== 'undefined'          ? CM_RESTAURANTS          : []); }
  function _external()     { return (typeof CM_EXTERNAL_RESTAURANTS !== 'undefined' ? CM_EXTERNAL_RESTAURANTS : []); }
  function _config()       { return (typeof CM_CONFIG !== 'undefined'               ? CM_CONFIG               : { restaurantCount: 270, creatorCount: 31, categoryCount: 20, lastUpdated: '2026-04-15', coverage: 'Bangkok' }); }
  function _signals()      { return (typeof CM_SIGNALS !== 'undefined'              ? CM_SIGNALS              : {}); }
  function _influencers()  { return (typeof CM_INFLUENCERS !== 'undefined'          ? CM_INFLUENCERS          : []); }

  /* ─── Merge ──────────────────────────────────────────────────────────────── */
  function _mergeAllRestaurants() {
    var ext = _external().map(function (r) {
      return Object.assign({}, r, {
        name:         r.name || r.name_en || '',
        cuisine:      r.cuisine_normalized || r.cuisine || '',
        area:         r.area_normalized    || r.area    || '',
        totalReviews: r.totalReviews || 0,
        tags:         r.tags     || [],
        occasions:    r.occasions || [],
        _fromDB:      true
      });
    });
    var dbNames = {};
    ext.forEach(function (r) { dbNames[(r.name || '').trim().toLowerCase()] = true; });
    var curated = _restaurants().filter(function (r) {
      return (r.name || '').trim().toLowerCase() && !dbNames[(r.name || '').trim().toLowerCase()];
    }).map(function (r) {
      return Object.assign({}, r, { _fromDB: false });
    });
    return ext.concat(curated);
  }

  /* ─── FIX 1: Scope filter (tolerant) ────────────────────────────────────── */
  function _scopeFilter(r) {
    if (!r) return false;
    // Explicit out-of-scope → exclude
    if (r.scope_market === 'out_of_scope_location') return false;
    if (r.scope_market === 'out_of_scope_format')   return false;
    // Non-restaurant venue types → exclude
    var vt = r.venue_type || '';
    if (vt === 'kiosk' || vt === 'street_food' || vt === 'food_stand' || vt === 'takeaway_only') return false;
    // Explicit false flags → exclude
    if (r.is_bangkok_focus    === false) return false;
    if (r.is_restaurant_focus === false) return false;
    // Everything else (including undefined / null / needs_review) → allow
    return true;
  }

  function _scopeFilterBroad(r) {
    if (!r) return false;
    return (r.scope_market || '') !== 'out_of_scope_location';
  }

  /* ─── FIX 3: Score (uses canonical totalReviews) ─────────────────────────── */
  function _computeScore(r) {
    if (!r) return { score: 0, growthRate: 0, growth: 0, totalReviews: 0, creatorScore: 0 };

    // Pre-computed from canonical.py (most accurate)
    if (r._score !== undefined && r._growthRate !== undefined) {
      return {
        score:        r._score        || 0,
        growthRate:   r._growthRate    || 0,
        growth:       r._growth        || 0,
        totalReviews: r.totalReviews   || 0,
        creatorScore: r.creator_signal_score || 0
      };
    }

    var total = r.totalReviews || 0;
    var growth = 0, growthRate = 0;

    if (r.newReviews30d > 0) {
      growth     = r.newReviews30d;
      growthRate = growth / Math.max(total - growth, 1);
    } else if (r.velocityPct > 0) {
      growthRate = r.velocityPct / 100;
      growth     = Math.round(growthRate * Math.max(total / (1 + growthRate), 1));
    } else {
      // Qualitative fallback for curated records
      var velBase = { rising: 0.12, stable: 0.04, declining: 0.005 }[r.trendVelocity] || 0.04;
      growthRate  = Math.max(velBase + ((r.overlapSignal || 0) / 10) * 0.06, 0);
      growth      = Math.round(growthRate * Math.max(total, 1));
    }

    var dampener = Math.log(total + 10);
    var score    = dampener > 0 ? growthRate * Math.log(total + 1) / dampener : 0;

    // Rating tilt
    var rating = r.rating_gmaps || r.rating_score || 0;
    if (rating > 0) score = score * (0.7 + 0.3 * (rating / 5));

    return {
      score:        Math.max(score, 0),
      growthRate:   Math.max(growthRate, 0),
      growth:       Math.max(Math.round(growth), 0),
      totalReviews: total,
      creatorScore: r.creator_signal_score || 0
    };
  }

  /* ─── Trend labels ───────────────────────────────────────────────────────── */
  function _trendLabel(s, r) {
    var gr = (s && s.growthRate) || 0;
    var tr = (s && s.totalReviews) || (r && r.totalReviews) || 0;
    var cs = (s && s.creatorScore) || 0;
    if (cs > 0.5 && tr < 200)  return 'Social Buzz';
    if (tr < 300 && tr > 0 && (gr > 0.03 || ((r && r.rating_gmaps) || 0) >= 4.5)) return 'Emerging';
    if (gr > 0.5)  return 'Rising Fast';
    if (gr > 0.15) return 'Gaining Momentum';
    if (gr > 0.05) return 'Steady Growth';
    if (gr > 0.01) return 'Also Trending';
    if (gr < -0.05) return 'Cooling Down';
    return 'Stable';
  }

  function _trendEmoji(label) {
    return { 'Rising Fast': '\uD83D\uDD25', 'Gaining Momentum': '\uD83D\uDCC8', 'Steady Growth': '\u2197\uFE0F',
             'Also Trending': '\u2197\uFE0F', 'Emerging': '\uD83C\uDD95', 'Social Buzz': '\uD83D\uDCF2',
             'Under Watch': '\uD83D\uDC40', 'Cooling Down': '\u2744\uFE0F', 'Stable': '\u2192' }[label] || '\u2192';
  }

  /* ─── Freshness rotation ─────────────────────────────────────────────────── */
  function _rotate(list, n, mult) {
    var desired  = n || 8;
    var poolSize = Math.min(list.length, desired * (mult || 2));
    if (poolSize <= desired) return list.slice(0, desired);
    var now = new Date();
    var doy = Math.floor((now - new Date(now.getFullYear(), 0, 0)) / 86400000);
    var off = doy % Math.max(poolSize - desired, 1);
    var out = [];
    for (var i = 0; i < desired; i++) out.push(list[(off + i) % poolSize]);
    return out;
  }

  /* ─── Core counts ────────────────────────────────────────────────────────── */
  function getDbTotalCount()  { return _config().restaurantCount || 270; }
  function getLastUpdated()   { return _config().lastUpdated || ''; }
  function getCreatorCount()  { var l = _influencers(); return l.length || _config().creatorCount || 0; }
  function getCategoryCount() { return Math.max(getCategoryList().length, _config().categoryCount || 0); }
  function getDetailedRestaurantCount() { return _mergeAllRestaurants().filter(_scopeFilter).length; }
  function getRisingCount() {
    return _mergeAllRestaurants().filter(_scopeFilter).filter(function (r) {
      return r.trendVelocity === 'rising' || (_computeScore(r).growthRate || 0) > 0.05;
    }).length;
  }

  /* ─── Restaurant list ────────────────────────────────────────────────────── */
  function getRestaurantList(opts) {
    var list = _mergeAllRestaurants().filter(_scopeFilter);
    if (!opts) return _sortByScore(list);

    if (opts.signal   && opts.signal   !== 'all') list = list.filter(function (r) { return r.signalStrength === opts.signal; });
    if (opts.velocity && opts.velocity !== 'all') list = list.filter(function (r) { return r.trendVelocity === opts.velocity; });
    if (opts.budget   && opts.budget   !== 'all') list = list.filter(function (r) { return String(r.budget) === String(opts.budget); });
    if (opts.type     && opts.type     !== 'all') {
      list = list.filter(function (r) {
        var c = (r.cuisine_normalized || r.cuisine || '').toLowerCase();
        var v = (r.venue_type || r.type || '').toLowerCase();
        var q = opts.type.toLowerCase();
        return v === q || c === q || c.indexOf(q) >= 0;
      });
    }
    if (opts.search) {
      var q = opts.search.toLowerCase();
      list = list.filter(function (r) {
        return (r.name || '').toLowerCase().indexOf(q) >= 0 ||
               (r.cuisine_normalized || r.cuisine || '').toLowerCase().indexOf(q) >= 0 ||
               (r.area_normalized    || r.area    || '').toLowerCase().indexOf(q) >= 0;
      });
    }
    var sort = opts.sort || 'score';
    if (sort === 'velocity') return _sortByVelocity(list);
    if (sort === 'reviews')  return _sortByReviews(list);
    if (sort === 'signal')   return _sortBySignal(list);
    return _sortByScore(list);
  }

  /* ─── Ranked lists ────────────────────────────────────────────────────────── */
  function getTrendingRestaurants(n) {
    var desired = n || 8;
    var all = _mergeAllRestaurants().filter(_scopeFilter).map(function (r) {
      var s = _computeScore(r);
      var label = r._trendLabel || r.trend_label || _trendLabel(s, r);
      return Object.assign({}, r, {
        _score:       s.score,
        _growthRate:  s.growthRate,
        _growth:      s.growth,
        _trendLabel:  label,
        _trendEmoji:  r._trendEmoji || _trendEmoji(label),
        _growthMetric: r._growthMetric || (s.growthRate > 0.1 ? ('+' + Math.round(s.growthRate * 100) + '% in 30d') : ''),
        cuisine:      r.cuisine_normalized || r.cuisine || '',
        area:         r.area_normalized    || r.area    || ''
      });
    });

    var scraped  = all.filter(function (r) { return  r._fromDB && r._score > 0; });
    var curated  = all.filter(function (r) { return !r._fromDB && r._score > 0; });
    scraped.sort(function (a, b) { return b._score - a._score; });
    curated.sort(function (a, b) { return b._score - a._score; });

    var maxCurated = Math.floor(desired * 0.4);
    var combined   = scraped.concat(curated.slice(0, maxCurated));
    combined.sort(function (a, b) { return b._score - a._score; });

    var rotated = _rotate(combined, desired, 2);

    // Fill remainder with DB records sorted by reviews
    if (rotated.length < desired) {
      var seen = {};
      rotated.forEach(function (r) { seen[r.id || r.name] = true; });
      var extras = all.filter(function (r) { return !seen[r.id || r.name]; })
        .sort(function (a, b) { return (b.totalReviews || 0) - (a.totalReviews || 0); })
        .slice(0, desired - rotated.length);
      rotated = rotated.concat(extras);
    }
    return rotated;
  }

  function getEmergingRestaurants(n) {
    var desired = n || 8;
    var THRESHOLD = 300;
    var candidates = _mergeAllRestaurants().filter(_scopeFilter).map(function (r) {
      var s = _computeScore(r);
      return Object.assign({}, r, {
        _score: s.score, _growthRate: s.growthRate, _growth: s.growth,
        _trendLabel: 'Emerging', _trendEmoji: '\uD83C\uDD95',
        cuisine: r.cuisine_normalized || r.cuisine || '',
        area:    r.area_normalized    || r.area    || ''
      });
    }).filter(function (r) {
      var rev = r.totalReviews || 0;
      return rev > 0 && rev < THRESHOLD &&
        (r._isEmerging || r.trend_label === 'Emerging' || r._growthRate > 0.01 ||
         (r.rating_gmaps || 0) >= 4.3 || (r.creator_signal_score || 0) > 0.1);
    }).sort(function (a, b) {
      if (Math.abs(b._growthRate - a._growthRate) > 0.005) return b._growthRate - a._growthRate;
      return b._score - a._score;
    });
    return _rotate(candidates, desired, 2);
  }

  function getPopularRestaurants(n) {
    return _mergeAllRestaurants().filter(_scopeFilter).map(function (r) {
      var s = _computeScore(r);
      var label = _trendLabel(s, r);
      return Object.assign({}, r, {
        _score: s.score, _growthRate: s.growthRate,
        _trendLabel: label, _trendEmoji: _trendEmoji(label),
        cuisine: r.cuisine_normalized || r.cuisine || '',
        area:    r.area_normalized    || r.area    || ''
      });
    }).sort(function (a, b) { return (b.totalReviews || 0) - (a.totalReviews || 0); })
      .slice(0, n || 8);
  }

  function getFeaturedRestaurants(n) { return getTrendingRestaurants(n || 5); }

  /* ─── Spotlight ──────────────────────────────────────────────────────────── */
  function getWeeklySpotlight() {
    var sig = _signals();
    var wh  = sig.weeklyHighlight || {};
    var rest = null;
    if (wh.restaurant) {
      rest = _mergeAllRestaurants().filter(function (r) { return r.name === wh.restaurant; })[0] || null;
    }
    if (!rest) {
      var top = getTrendingRestaurants(3);
      rest = top.filter(function (r) { return r._growthMetric; })[0] || top[0] || null;
    }
    return {
      restaurant: rest,
      title: wh.title || (rest ? ('\uD83D\uDCC8 ' + (rest.name || '') + ' — Trending') : ''),
      desc:  wh.desc  || (rest ? (rest.trend_reason || rest.cmNote || '') : ''),
      trend: wh.trend || (rest ? (rest.trendVelocity || 'rising') : 'stable')
    };
  }

  /* ─── Per-category (FIX 2) ───────────────────────────────────────────────── */
  function getCategoryTopN(cuisineLabel, n) {
    if (!cuisineLabel) return [];
    var q = cuisineLabel.toLowerCase();
    return _mergeAllRestaurants().filter(_scopeFilter).filter(function (r) {
      var c = (r.cuisine_normalized || r.cuisine || '').toLowerCase();
      return c === q || c.indexOf(q) >= 0;
    }).map(function (r) {
      var s = _computeScore(r);
      return Object.assign({}, r, { _score: s.score });
    }).sort(function (a, b) {
      if (Math.abs(b._score - a._score) > 0.001) return b._score - a._score;
      return (b.totalReviews || 0) - (a.totalReviews || 0);
    }).slice(0, n || 5);
  }

  function getEmergingByCategory(cuisineLabel, n) {
    if (!cuisineLabel) return [];
    var q = cuisineLabel.toLowerCase();
    return _mergeAllRestaurants().filter(_scopeFilter).filter(function (r) {
      var c = (r.cuisine_normalized || r.cuisine || '').toLowerCase();
      return (c === q || c.indexOf(q) >= 0) && (r.totalReviews || 0) < 300;
    }).map(function (r) {
      var s = _computeScore(r);
      return Object.assign({}, r, { _score: s.score, _growthRate: s.growthRate });
    }).sort(function (a, b) { return b._growthRate - a._growthRate; }).slice(0, n || 3);
  }

  function getSocialBuzzRestaurants(n) {
    return _mergeAllRestaurants().filter(_scopeFilter)
      .filter(function (r) { return (r.creator_signal_score || 0) > 0.05; })
      .sort(function (a, b) { return (b.creator_signal_score || 0) - (a.creator_signal_score || 0); })
      .slice(0, n || 6);
  }

  function getViralCandidates(n) {
    return _mergeAllRestaurants().filter(_scopeFilter)
      .filter(function (r) { return r.is_viral_candidate === true; })
      .sort(function (a, b) { return (b.creator_signal_score || 0) - (a.creator_signal_score || 0); })
      .slice(0, n || 5);
  }

  /* ─── Categories ─────────────────────────────────────────────────────────── */
  function getCategoryList() {
    var counts = {};
    _mergeAllRestaurants().filter(_scopeFilter).forEach(function (r) {
      var c = r.cuisine_normalized || r.cuisine || '';
      if (c) counts[c] = (counts[c] || 0) + 1;
    });
    return Object.keys(counts).map(function (c) { return { id: c, label: c, count: counts[c] }; })
      .sort(function (a, b) { return b.count - a.count; });
  }

  function getCategoryBlocks(categories, perCategory) {
    perCategory = perCategory || 4;
    var merged = _mergeAllRestaurants().filter(_scopeFilter).map(function (r) {
      var s = _computeScore(r);
      return Object.assign({}, r, { _score: s.score, cuisine: r.cuisine_normalized || r.cuisine || '' });
    });
    return (categories || []).map(function (cat) {
      var q = (cat.cuisine || cat.label || '').toLowerCase();
      var matches = merged.filter(function (r) {
        return (r.cuisine || '').toLowerCase().indexOf(q) >= 0;
      }).sort(function (a, b) { return b._score - a._score; }).slice(0, perCategory);
      return Object.assign({}, cat, { restaurants: matches });
    });
  }

  /* ─── Creator stats ──────────────────────────────────────────────────────── */
  function getCreatorStats() {
    var l = _influencers();
    return {
      total: l.length || _config().creatorCount || 0,
      mega:  l.filter(function (c) { return c.tier === 'Mega';  }).length,
      macro: l.filter(function (c) { return c.tier === 'Macro'; }).length,
      mid:   l.filter(function (c) { return c.tier === 'Mid';   }).length
    };
  }

  /* ─── Lookup ─────────────────────────────────────────────────────────────── */
  function getRestaurantById(id) {
    return _mergeAllRestaurants().filter(function (r) { return r.id === id; })[0] || null;
  }
  function getRestaurantByName(name) {
    var n = (name || '').toLowerCase();
    return _mergeAllRestaurants().filter(function (r) { return (r.name || '').toLowerCase() === n; })[0] || null;
  }

  /* ─── Stats + inject ─────────────────────────────────────────────────────── */
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

  function injectStats() {
    try {
      var s = getAllStats();
      ['statRestaurants','statDashTotal','creatorStatRestaurants','partnerStatRestaurants'].forEach(function (id) {
        var el = document.getElementById(id); if (el) el.textContent = s.dbTotal + '+';
      });
      var catEl  = document.getElementById('statCategories');  if (catEl)  catEl.textContent  = s.categories + '+';
      var creEl  = document.getElementById('statCreators');    if (creEl)  creEl.textContent  = s.creators   + '+';
      var riseEl = document.getElementById('statDashRising');  if (riseEl) riseEl.textContent = '\u2191 ' + s.rising;
      var dateEl = document.getElementById('weeklyUpdatedDate');
      if (dateEl)  dateEl.textContent = s.lastUpdated;
      var badgeEl = document.getElementById('weeklyUpdatedBadge');
      if (badgeEl) badgeEl.style.display = 'flex';
    } catch (e) {
      console.error('[CM] injectStats error:', e);
    }
  }

  /* ─── Sort helpers ───────────────────────────────────────────────────────── */
  function _sortByScore(list) {
    return list.slice().sort(function (a, b) {
      var sa = _computeScore(a).score, sb = _computeScore(b).score;
      if (Math.abs(sb - sa) > 0.001) return sb - sa;
      return (b.totalReviews || 0) - (a.totalReviews || 0);
    });
  }
  function _sortByVelocity(list) {
    var vo = { rising: 3, stable: 2, declining: 1 };
    return list.slice().sort(function (a, b) {
      var vd = (vo[b.trendVelocity] || 0) - (vo[a.trendVelocity] || 0);
      return vd !== 0 ? vd : (b.overlapSignal || 0) - (a.overlapSignal || 0);
    });
  }
  function _sortByReviews(list) {
    return list.slice().sort(function (a, b) { return (b.totalReviews || 0) - (a.totalReviews || 0); });
  }
  function _sortBySignal(list) {
    var so = { 'very-strong': 4, strong: 3, moderate: 2, weak: 1 };
    return list.slice().sort(function (a, b) {
      var sd = (so[b.signalStrength] || 0) - (so[a.signalStrength] || 0);
      return sd !== 0 ? sd : (b.overlapSignal || 0) - (a.overlapSignal || 0);
    });
  }

  /* ─── Export ─────────────────────────────────────────────────────────────── */
  try {
    global.ChefMinistryData = {
      // Counts
      getDbTotalCount: getDbTotalCount,
      getDetailedRestaurantCount: getDetailedRestaurantCount,
      getRisingCount: getRisingCount,
      getCreatorCount: getCreatorCount,
      getCategoryCount: getCategoryCount,
      getLastUpdated: getLastUpdated,
      // Lists
      getRestaurantList: getRestaurantList,
      getFeaturedRestaurants: getFeaturedRestaurants,
      getTrendingRestaurants: getTrendingRestaurants,
      getEmergingRestaurants: getEmergingRestaurants,
      getPopularRestaurants: getPopularRestaurants,
      getWeeklySpotlight: getWeeklySpotlight,
      getCategoryList: getCategoryList,
      getCategoryBlocks: getCategoryBlocks,
      getCategoryTopN: getCategoryTopN,
      getEmergingByCategory: getEmergingByCategory,
      getSocialBuzzRestaurants: getSocialBuzzRestaurants,
      getViralCandidates: getViralCandidates,
      // Lookup
      getCreatorStats: getCreatorStats,
      getRestaurantById: getRestaurantById,
      getRestaurantByName: getRestaurantByName,
      // Utilities (public aliases)
      computeScore:     _computeScore,
      trendLabel:       _trendLabel,
      trendEmoji:       _trendEmoji,
      scopeFilter:      _scopeFilter,
      scopeFilterBroad: _scopeFilterBroad,
      mergeAll:         _mergeAllRestaurants,
      // Stats
      getAllStats: getAllStats,
      injectStats: injectStats
    };
    console.log('[CM] dataService v6 loaded — ' + _mergeAllRestaurants().filter(_scopeFilter).length + ' in-scope restaurants');
  } catch (e) {
    console.error('[CM] dataService export error:', e);
  }

}(typeof window !== 'undefined' ? window : this));
