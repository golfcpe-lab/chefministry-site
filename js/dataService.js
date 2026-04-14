/**
 * ChefMinistry — Shared Data Service
 * Single source of truth for all pages.
 *
 * v4 — Bangkok-Focus + Scope Classification Edition
 *
 * KEY CHANGE (v4):
 *   All default discovery surfaces (Trending, Emerging, Popular, Spotlight,
 *   Discover, Velocity Rank) now apply a Bangkok + restaurant scope filter
 *   BEFORE ranking.  Only records with:
 *     is_bangkok_focus === true  AND  is_restaurant_focus === true
 *   appear in default output.
 *
 *   The filter is implemented once in _scopeFilter() and called consistently
 *   across all list/ranking functions.  Records missing these fields (legacy
 *   curated entries) are treated as in-scope so the curated list keeps working.
 *
 * Scoring formula (unchanged from v3):
 *   growth_rate = growth / max(base, 1)
 *   score       = growth_rate × log(total+1) / log(total+10)   ← size-dampened
 *
 * "จัดอันดับจากการเปลี่ยนแปลงของรีวิว ไม่ใช่จำนวนรีวิวรวม"
 */

(function (global) {
  'use strict';

  /* --- Private accessors -------------------------------------------------- */

  function _restaurants() {
    return (typeof CM_RESTAURANTS !== 'undefined') ? CM_RESTAURANTS : [];
  }
  function _influencers() {
    return (typeof CM_INFLUENCERS !== 'undefined') ? CM_INFLUENCERS : [];
  }
  function _config() {
    return (typeof CM_CONFIG !== 'undefined') ? CM_CONFIG : {
      restaurantCount: 270, creatorCount: 31, categoryCount: 20,
      lastUpdated: '2026-04-14', updateFrequency: 'daily', coverage: 'Bangkok'
    };
  }
  function _signals() {
    return (typeof CM_SIGNALS !== 'undefined') ? CM_SIGNALS : {};
  }
  function _external() {
    return (typeof CM_EXTERNAL_RESTAURANTS !== 'undefined') ? CM_EXTERNAL_RESTAURANTS : [];
  }


  /* --- Scope filter (v4 — Bangkok + restaurant focus) ---------------------- */

  /**
   * Default scope: Bangkok restaurants (and cafes) only.
   *
   * Returns true  → record should appear in default discovery output.
   * Returns false → record should be excluded from default discovery output.
   *
   * Rules:
   *   1. If the record has explicit classification fields (from Python pipeline):
   *      - is_bangkok_focus must be true
   *      - is_restaurant_focus must be true
   *   2. If the record has NO classification fields (legacy curated entries in
   *      CM_RESTAURANTS that predate the classifier):
   *      - Allow through by default so the curated list keeps working.
   *      - The curated list is manually maintained and assumed Bangkok-only.
   *   3. If the record has a scope_market field that is explicitly out-of-scope:
   *      - Exclude regardless of the boolean flags.
   *
   * @param {Object} r  — restaurant record
   * @returns {boolean}
   */
  function _scopeFilter(r) {
    var sm = r.scope_market;

    // Explicit out-of-scope markers → always exclude
    if (sm === 'out_of_scope_location' || sm === 'out_of_scope_format') {
      return false;
    }

    // Record has been classified → trust the boolean flags
    if (r.is_bangkok_focus !== undefined && r.is_restaurant_focus !== undefined) {
      return r.is_bangkok_focus === true && r.is_restaurant_focus === true;
    }

    // Legacy curated record with no classification fields → allow through
    // (curated list is manually curated for Bangkok restaurants)
    return true;
  }

  /**
   * Broader scope: includes needs_review records (for admin/debug views).
   * Not used in public-facing pages.
   */
  function _scopeFilterBroad(r) {
    var sm = r.scope_market;
    if (sm === 'out_of_scope_location') return false;  // out of city → always exclude
    return true;
  }

  /* --- Growth Scoring Engine (v3 — anti-dominance edition) ------------------- */

  /**
   * Compute normalized growth score for any restaurant object.
   *
   * v3 FIX — Two problems with the old formula:
   *   OLD: score = growthRate * log(total+1)
   *        → large restaurants (total=2000) produce log(2001)=7.6, small (total=30) log(31)=3.4
   *        → even at equal growthRate, large restaurants score 2× higher = dominance
   *   OLD curated fallback: rising=0.35, which beats ALL real scraped DB restaurants
   *        → static curated list always wins, same 10 names every time
   *
   * NEW FORMULA:
   *   score = growthRate * log(total+1) / log(total+10)
   *   This is a size-dampening divisor: as total grows, log(total+10) grows too,
   *   reducing the advantage of very large restaurants. At total=30: divisor≈3.5;
   *   at total=2000: divisor≈7.7. Net effect: size advantage is compressed ~50%.
   *
   * NEW CURATED FALLBACK:
   *   rising=0.12 (was 0.35) — now competitive with real DB data, not dominant.
   *
   * PRE-COMPUTED PRIORITY:
   *   If the DB export already set _score/_growthRate (via export_signals.py v3),
   *   use those directly and skip re-computation to stay consistent with DB truth.
   *
   * @param {Object} r  — restaurant object (curated or scraped)
   * @returns {{ growth, growthRate, totalReviews, score }}
   */
  function _computeScore(r) {
    var total = r.totalReviews || 0;

    // ── Priority 1: pre-computed by Python export (most accurate) ────────────
    if (r._score !== undefined && r._growthRate !== undefined) {
      return {
        growth:       r._growth       || 0,
        growthRate:   r._growthRate   || 0,
        totalReviews: total,
        score:        r._score        || 0,
        creatorScore: r.creator_signal_score || 0,
      };
    }

    var growth, growthRate;

    // ── Priority 2: real scraped review delta ─────────────────────────────────
    if (r.newReviews30d !== undefined && r.newReviews30d > 0) {
      var newRev    = r.newReviews30d;
      var baseCount = Math.max(total - newRev, 1);
      growth     = newRev;
      growthRate = newRev / baseCount;

    // ── Priority 3: velocityPct from DB ───────────────────────────────────────
    } else if (r.velocityPct !== undefined && r.velocityPct > 0) {
      growthRate = r.velocityPct / 100;
      growth     = Math.round(growthRate * Math.max(total / (1 + growthRate), 1));

    // ── Priority 4: curated qualitative fallback (REDUCED to prevent dominance)
    } else {
      // FIX: was 0.35/0.08 — too high, always beat real DB restaurants.
      // Now 0.12/0.04 — curated competes but doesn't automatically win.
      var velBase      = {rising: 0.12, stable: 0.04, declining: 0.005}[r.trendVelocity] || 0.04;
      var overlapBoost = ((r.overlapSignal || 0) / 10) * 0.06;  // was 0.18, now smaller
      growthRate = Math.max(velBase + overlapBoost, 0);
      growth     = Math.round(growthRate * Math.max(total, 1));
    }

    // ── NEW size-dampened score formula ───────────────────────────────────────
    // OLD: growthRate * log(total+1)           ← large restaurants dominate
    // NEW: growthRate * log(total+1) / log(total+10) ← dampens large-base advantage
    var sizeDampener = Math.log(total + 10);   // grows with size → reduces advantage
    var score        = growthRate * Math.log(total + 1) / sizeDampener;

    // Creator signal boost — rewards social buzz before reviews catch up
    var cScore = r.creator_signal_score || 0;
    if (cScore > 0 && total < 200) {
      score = score * (1 + cScore * 0.2);  // up to +20% for viral candidates
    }

    // Light rating quality tilt
    if (r.rating_score && r.rating_score > 0) {
      score = score * (0.7 + 0.3 * (r.rating_score / 5));
    }

    return {
      growth:       Math.max(Math.round(growth), 0),
      growthRate:   Math.max(growthRate, 0),
      totalReviews: total,
      score:        Math.max(score, 0),
      creatorScore: cScore,
    };
  }

  /**
   * Daily freshness rotation — prevents same restaurants from locking top slots forever.
   * Uses deterministic day-of-year seed so results are consistent within a day
   * but rotate across days.
   *
   * @param {Array}  list     — scored + sorted restaurant list
   * @param {number} n        — desired output count
   * @param {number} poolMult — how many × n to consider as the rotation pool
   * @returns {Array}
   */
  function _applyFreshnessRotation(list, n, poolMult) {
    var desired  = n || 8;
    var poolSize = Math.min(list.length, desired * (poolMult || 2));
    if (poolSize <= desired) return list.slice(0, desired);

    var pool = list.slice(0, poolSize);

    // Day-of-year offset for rotation (changes daily, consistent within day)
    var now    = new Date();
    var dayOfYear = Math.floor((now - new Date(now.getFullYear(), 0, 0)) / 86400000);
    var offset = dayOfYear % Math.max(poolSize - desired, 1);

    // Rotate: take from offset, wrap around pool
    var result = [];
    for (var i = 0; i < desired; i++) {
      result.push(pool[(offset + i) % poolSize]);
    }
    return result;
  }

  /** Human-readable trend label based on growth rate + review size */
  function _trendLabel(scoreObj) {
    var gr = scoreObj.growthRate;
    var tr = scoreObj.totalReviews;
    if (tr < 200 && gr > 0.05)  return 'Emerging';          // FIX: was <100, now <200
    if (gr > 0.5)                return 'Rising Fast';
    if (gr > 0.2)                return 'Gaining Momentum';
    if (gr > 0.05)               return 'Steady Growth';
    if (gr < -0.05)              return 'Cooling Down';
    return 'Stable';
  }

  /** Emoji prefix for trend label */
  function _trendEmoji(label) {
    return {'Rising Fast': '🔥', 'Emerging': '🆕', 'Gaining Momentum': '📈',
            'Steady Growth': '↗️', 'Cooling Down': '❄️', 'Stable': '→'}[label] || '→';
  }

  /* --- Core counts --------------------------------------------------------- */

  function getDbTotalCount()            { return _config().restaurantCount; }
  function getDetailedRestaurantCount() { return _restaurants().length; }
  function getRisingCount()             { return _restaurants().filter(function(r){ return r.trendVelocity==='rising'; }).length; }
  function getLastUpdated()             { return _config().lastUpdated; }

  function getCreatorCount() {
    var l = _influencers(); return l.length > 0 ? l.length : _config().creatorCount;
  }
  function getCategoryCount() {
    return Math.max(getCategoryList().length, _config().categoryCount);
  }

  /* --- Restaurant list + filtering ----------------------------------------- */

  function getRestaurantList(opts) {
    var list = _restaurants().slice();
    if (!opts) return _sortBySignal(list);

    if (opts.signal   && opts.signal   !== 'all') list = list.filter(function(r){ return r.signalStrength===opts.signal; });
    if (opts.velocity && opts.velocity !== 'all') list = list.filter(function(r){ return r.trendVelocity===opts.velocity; });
    if (opts.budget   && opts.budget   !== 'all') list = list.filter(function(r){ return String(r.budget)===String(opts.budget); });
    if (opts.type     && opts.type     !== 'all') list = list.filter(function(r){ return r.type===opts.type; });

    if (opts.search && opts.search.trim()) {
      var q = opts.search.trim().toLowerCase();
      list = list.filter(function(r){
        return (r.name||'').toLowerCase().indexOf(q)>=0
          || (r.cuisine||'').toLowerCase().indexOf(q)>=0
          || (r.area||'').toLowerCase().indexOf(q)>=0;
      });
    }

    var sort = opts.sort || 'signal';
    if (sort==='velocity') return _sortByVelocity(list);
    if (sort==='reviews')  return _sortByReviews(list);
    if (sort==='score')    return _sortByScore(list);
    return _sortBySignal(list);
  }

  /* --- Three ranked lists --------------------------------------------------- */

  /**
   * A. TRENDING — balanced growth score (size-normalised, freshness-rotated).
   *
   * v3 FIX:
   * - Uses new size-dampened _computeScore (no large-restaurant dominance)
   * - Applies daily rotation so the same restaurants don't lock top slots
   * - Ensures a mix: at most 40% of results from static curated list
   * - Includes restaurants even with growthRate=0 if they have real scraped data
   *   (previously filtered out → only curated made it through)
   *
   * @param {number} [n=8]
   */
  function getTrendingRestaurants(n) {
    var desired = n || 8;
    // ── v4: apply Bangkok + restaurant scope filter before scoring ────────────
    var all     = _mergeAllRestaurants().filter(_scopeFilter).map(function(r) {
      var s = _computeScore(r);
      var label = r._trendLabel || _trendLabel(s);
      return Object.assign({}, r, {
        _score:      s.score,
        _growthRate: s.growthRate,
        _growth:     s.growth,
        _trendLabel: label,
        _trendEmoji: r._trendEmoji || _trendEmoji(label),
        _isCurated:  !r.source || r.source === undefined  // curated if no source field from DB
      });
    });

    // Separate scraped (DB) vs curated — scraped gets priority
    var scraped  = all.filter(function(r){ return r.source && r._score > 0; });
    var curated  = all.filter(function(r){ return !r.source && r._score > 0; });

    // Sort each by score
    scraped.sort(function(a,b){ return b._score - a._score; });
    curated.sort(function(a,b){ return b._score - a._score; });

    // Cap curated at 40% of desired slots so real data always has majority
    var maxCurated = Math.floor(desired * 0.4);
    var combined   = scraped.concat(curated.slice(0, maxCurated));
    combined.sort(function(a,b){ return b._score - a._score; });

    // Apply freshness rotation so same restaurants don't repeat across days
    return _applyFreshnessRotation(combined, desired, 2);
  }

  /**
   * B. EMERGING — new restaurants with low review count but good signals.
   *
   * v3 FIX:
   * - Threshold raised from 100 → 200 (more restaurants qualify)
   * - Accepts restaurants with growthRate=0 if they have high rating (new signal)
   * - Sorted by combined score (growthRate + rating proxy), not just growthRate
   * - Pulls from DB _isEmerging flag if pre-computed by export_signals.py
   *
   * @param {number} [n=8]
   */
  function getEmergingRestaurants(n) {
    var desired   = n || 8;
    var THRESHOLD = 200;   // FIX: was 100, raised to include more restaurants

    return _mergeAllRestaurants()
      .filter(_scopeFilter)  // ── v4: Bangkok + restaurant scope first ─────
      .map(function(r) {
        var s = _computeScore(r);
        return Object.assign({}, r, {
          _score:      s.score,
          _growthRate: s.growthRate,
          _growth:     s.growth,
          _trendLabel: 'Emerging',
          _trendEmoji: '🆕'
        });
      })
      .filter(function(r) {
        var rev = r.totalReviews || 0;
        // Include if: small review count AND (some growth OR pre-tagged as emerging OR high rating)
        return rev < THRESHOLD
          && rev > 0
          && (r._growthRate > 0.01 || r._isEmerging === true || (r.velocityPct||0) > 0 || r.rating_score >= 4.5);
      })
      .sort(function(a,b) {
        // Sort by combined: growthRate first, then by _score, then by totalReviews desc (more validated)
        var scoreDiff = b._growthRate - a._growthRate;
        if (Math.abs(scoreDiff) > 0.01) return scoreDiff;
        return b._score - a._score;
      })
      .slice(0, desired);
  }

  /**
   * C. POPULAR — established restaurants sorted by total review volume.
   * @param {number} [n=8]
   */
  function getPopularRestaurants(n) {
    return _mergeAllRestaurants()
      .filter(_scopeFilter)  // ── v4: Bangkok + restaurant scope ────────────
      .map(function(r) {
        var s = _computeScore(r);
        return Object.assign({}, r, {
          _score: s.score, _growthRate: s.growthRate, _growth: s.growth,
          _trendLabel: _trendLabel(s), _trendEmoji: _trendEmoji(_trendLabel(s))
        });
      })
      .sort(function(a,b){ return (b.totalReviews||0) - (a.totalReviews||0); })
      .slice(0, n || 8);
  }

  /* --- Featured / spotlight ------------------------------------------------- */

  /** Top N by growth score — now powered by getTrendingRestaurants. */
  function getFeaturedRestaurants(n) {
    return getTrendingRestaurants(n || 5);
  }

  /**
   * Weekly spotlight — top trending restaurant from real growth data.
   * v4: getTrendingRestaurants already applies _scopeFilter, so spotlight
   * is always Bangkok + restaurant focus.
   */
  function getWeeklySpotlight() {
    var sig = _signals();
    var wh  = sig.weeklyHighlight || {};
    var rest = null;

    if (wh.restaurant) {
      rest = _restaurants().find(function(r){ return r.name===wh.restaurant; }) || null;
    }
    if (!rest) {
      var t = getTrendingRestaurants(1);
      rest  = t[0] || null;
    }

    return {
      restaurant: rest,
      title: wh.title || (rest ? ('📈 ' + (rest.name||'') + ' — Trending สัปดาห์นี้') : ''),
      desc:  wh.desc  || (rest ? (rest.cmNote||'') : ''),
      trend: wh.trend || (rest ? rest.trendVelocity : 'stable')
    };
  }

  /* --- Merge helper --------------------------------------------------------- */

  function _mergeAllRestaurants() {
    var curated = _restaurants().slice();
    var names   = {};
    curated.forEach(function(r){ names[(r.name||'').trim().toLowerCase()] = true; });

    var ext = _external()
      .filter(function(r){
        var n = (r.name||r.name_en||'').trim().toLowerCase();
        return n && !names[n];
      })
      .map(function(r){
        return Object.assign({}, r, {
          name: r.name||r.name_en||'',
          tags: r.tags||[], occasions: r.occasions||[],
          totalReviews: r.totalReviews||r.last_count||0
        });
      });

    return curated.concat(ext);
  }

  /* --- Categories ----------------------------------------------------------- */

  function getCategoryList() {
    var labels = {
      'fine-dining':'Fine Dining','casual-dining':'Casual Dining',
      'street-food':'Street Food','omakase':'Omakase','steakhouse':'Steakhouse',
      'food-court':'Food Court','local':'Local / Everyday'
    };
    var counts = {};
    _restaurants().forEach(function(r){ if(r.type) counts[r.type]=(counts[r.type]||0)+1; });
    return Object.keys(counts).map(function(t){
      return {id:t, label:labels[t]||t, count:counts[t]};
    }).sort(function(a,b){ return b.count-a.count; });
  }

  /* --- Creator stats -------------------------------------------------------- */

  function getCreatorStats() {
    var l = _influencers();
    return {
      total: l.length>0 ? l.length : _config().creatorCount,
      mega:  l.filter(function(c){ return c.tier==='Mega';  }).length,
      macro: l.filter(function(c){ return c.tier==='Macro'; }).length,
      mid:   l.filter(function(c){ return c.tier==='Mid';   }).length
    };
  }

  /* --- Restaurant lookup ---------------------------------------------------- */

  function getRestaurantById(id) {
    return _restaurants().find(function(r){ return r.id===id; }) || null;
  }

  /* --- Unified stats bundle ------------------------------------------------- */

  function getAllStats() {
    return {
      dbTotal: getDbTotalCount(), detailed: getDetailedRestaurantCount(),
      rising:  getRisingCount(),  creators: getCreatorCount(),
      categories: getCategoryCount(), lastUpdated: getLastUpdated()
    };
  }

  /* --- DOM helper ----------------------------------------------------------- */

  function injectStats() {
    var s = getAllStats();
    ['statRestaurants','statDashTotal','creatorStatRestaurants','partnerStatRestaurants'].forEach(function(id){
      var el=document.getElementById(id); if(el) el.textContent=s.dbTotal+'+';
    });
    var catEl=document.getElementById('statCategories'); if(catEl) catEl.textContent=s.categories+'+';
    var creEl=document.getElementById('statCreators');   if(creEl) creEl.textContent=s.creators+'+';
    var riseEl=document.getElementById('statDashRising');if(riseEl) riseEl.textContent='↑ '+s.rising;
    var dateEl=document.getElementById('weeklyUpdatedDate');
    var badgeEl=document.getElementById('weeklyUpdatedBadge');
    if(dateEl)  dateEl.textContent=s.lastUpdated;
    if(badgeEl) badgeEl.style.display='flex';
  }

  /* --- Sort helpers --------------------------------------------------------- */

  function _velOrder(v){ return v==='rising'?3:v==='stable'?2:v==='declining'?1:0; }
  function _sigOrder(s){ return s==='very-strong'?4:s==='strong'?3:s==='moderate'?2:s==='weak'?1:0; }

  function _sortBySignal(list){
    return list.sort(function(a,b){
      var sd=_sigOrder(b.signalStrength)-_sigOrder(a.signalStrength);
      return sd!==0?sd:(b.overlapSignal||0)-(a.overlapSignal||0);
    });
  }
  function _sortByVelocity(list){
    return list.sort(function(a,b){
      var vd=_velOrder(b.trendVelocity)-_velOrder(a.trendVelocity);
      return vd!==0?vd:(b.overlapSignal||0)-(a.overlapSignal||0);
    });
  }
  function _sortByReviews(list){
    return list.sort(function(a,b){ return (b.totalReviews||0)-(a.totalReviews||0); });
  }
  function _sortByScore(list){
    return list.sort(function(a,b){ return _computeScore(b).score-_computeScore(a).score; });
  }

  /* --- Export --------------------------------------------------------------- */

  global.ChefMinistryData = {
    getDbTotalCount, getDetailedRestaurantCount, getRisingCount,
    getCreatorCount, getCategoryCount, getLastUpdated,

    getRestaurantList, getFeaturedRestaurants,
    getTrendingRestaurants, getEmergingRestaurants, getPopularRestaurants,
    getWeeklySpotlight, getCategoryList, getCreatorStats, getRestaurantById,

    computeScore: _computeScore,
    trendLabel:   _trendLabel,
    trendEmoji:   _trendEmoji,

    // v4: expose scope filter so page scripts can use the same logic
    scopeFilter:      _scopeFilter,
    scopeFilterBroad: _scopeFilterBroad,
    mergeAll:         _mergeAllRestaurants,

    // Per-category helpers
    getCategoryTopN, getEmergingByCategory,

    // Creator / social signals
    getSocialBuzzRestaurants, getViralCandidates,

    getAllStats, injectStats
  };

}(typeof window !== 'undefined' ? window : this));
