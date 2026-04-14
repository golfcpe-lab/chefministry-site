/* ChefMinistry Data Service (FIXED VERSION) */

(function (global) {
  'use strict';

  var CM = global.ChefMinistryData = global.ChefMinistryData || {};

  var CM_SIGNALS = global.CM_SIGNALS || {};
  var CM_RESTAURANTS = global.CM_RESTAURANTS || [];
  var CM_EXTERNAL_RESTAURANTS = global.CM_EXTERNAL_RESTAURANTS || [];

  function _mergeAllRestaurants() {
    return [].concat(CM_RESTAURANTS || [], CM_EXTERNAL_RESTAURANTS || []);
  }

  /* =========================
     FIX 1: Scope Filter (CRITICAL)
  ========================= */
  function _scopeFilter(r) {
    if (!r) return false;

    // ❌ exclude only when explicitly out of scope
    if (r.scope_market === 'out_of_scope_location') return false;
    if (r.scope_market === 'out_of_scope_format') return false;

    if (
      r.venue_type === 'kiosk' ||
      r.venue_type === 'street_food' ||
      r.venue_type === 'food_stand' ||
      r.venue_type === 'takeaway_only'
    ) {
      return false;
    }

    // ✅ tolerant logic (สำคัญมาก)
    if (r.is_bangkok_focus === false) return false;
    if (r.is_restaurant_focus === false) return false;

    return true;
  }

  /* =========================
     Helpers
  ========================= */
  function _getReviews(r) {
    return r.reviews_gmaps || r.reviews_wongnai || 0;
  }

  function _getRating(r) {
    return r.rating_score || r.rating_gmaps || r.rating_wongnai || 0;
  }

  function _computeScore(r) {
    var reviews = _getReviews(r);
    var rating = _getRating(r);

    return (reviews > 0 ? Math.log(reviews + 1) : 0) * (rating / 5);
  }

  /* =========================
     Core API
  ========================= */

  CM.getRestaurantList = function () {
    return _mergeAllRestaurants().filter(_scopeFilter);
  };

  CM.getTrendingRestaurants = function (n) {
    return CM.getRestaurantList()
      .map(function (r) {
        r._score = _computeScore(r);
        return r;
      })
      .sort(function (a, b) {
        return b._score - a._score;
      })
      .slice(0, n || 10);
  };

  CM.getEmergingRestaurants = function (n) {
    return CM.getRestaurantList()
      .filter(function (r) {
        return _getReviews(r) < 100;
      })
      .slice(0, n || 10);
  };

  /* =========================
     FIX 2: Missing Functions (CRASH CAUSE)
  ========================= */

  CM.getCategoryTopN = function (category, n) {
    return CM.getRestaurantList()
      .filter(function (r) {
        return (r.cuisine_normalized || '').toLowerCase() === category.toLowerCase();
      })
      .slice(0, n || 3);
  };

  CM.getEmergingByCategory = function (category, n) {
    return CM.getRestaurantList()
      .filter(function (r) {
        return (
          (r.cuisine_normalized || '').toLowerCase() === category.toLowerCase() &&
          _getReviews(r) < 100
        );
      })
      .slice(0, n || 3);
  };

  CM.getSocialBuzzRestaurants = function (n) {
    return CM.getRestaurantList().slice(0, n || 5);
  };

  CM.getViralCandidates = function (n) {
    return CM.getRestaurantList().slice(0, n || 5);
  };

  /* =========================
     Stats (safe)
  ========================= */
  CM.injectStats = function () {
    try {
      var count = CM.getRestaurantList().length;

      var el = document.querySelector('[data-stat="restaurant-count"]');
      if (el) el.textContent = count + '+';
    } catch (e) {
      console.error('injectStats error', e);
    }
  };

})(window);