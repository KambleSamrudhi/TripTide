// triptide/static/js/profile.js

(function () {
  const STORAGE_KEY = "triptide_profile";

  function loadProfile() {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try {
        return JSON.parse(raw);
      } catch (e) {
        // If corrupted, fall through and create a new one
      }
    }

    // Create a new anonymous profile if none exists
    const newProfile = {
      user_id: (crypto && crypto.randomUUID)
        ? crypto.randomUUID()
        : "uid_" + Date.now() + "_" + Math.random().toString(16).slice(2),
      created_at: new Date().toISOString(),
      last_seen_at: new Date().toISOString(),
      metrics: {
        explore_page_views: 0,
        view_stay_clicks: 0,
        searches: 0
      }
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(newProfile));
    return newProfile;
  }

  function saveProfile(profile) {
    profile.last_seen_at = new Date().toISOString();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
  }

      function incrementMetric(name) {
    const profile = loadProfile();
    if (!profile.metrics[name]) {
      profile.metrics[name] = 0;
    }
    profile.metrics[name] += 1;
    saveProfile(profile);
  }

  function setUxScore(score) {
    const profile = loadProfile();

    if (!profile.ux) {
      profile.ux = {
        last_score: 0,
        num_submissions: 0,
        avg_score: 0
      };
    }

    profile.ux.last_score = score;
    profile.ux.num_submissions += 1;
    profile.ux.avg_score =
      ((profile.ux.avg_score * (profile.ux.num_submissions - 1)) + score) /
      profile.ux.num_submissions;

    saveProfile(profile);
  }

  // Initialize profile once per page load
  const profile = loadProfile();



  // Example: count explore page views (optional, safe everywhere)
  if (window.location.pathname.toLowerCase().includes("explore")) {
    incrementMetric("explore_page_views");
  }

  // Track "View Stay" clicks (will work with the change in explore.js below)
  document.addEventListener("click", function (e) {
    const link = e.target.closest("a.book-link");
    if (link) {
      incrementMetric("view_stay_clicks");
    }
  });

  // Expose for debugging / later use
  window.TriptideProfile = {
    getProfile: loadProfile,
    incrementMetric,
    setUxScore
  };
})();

