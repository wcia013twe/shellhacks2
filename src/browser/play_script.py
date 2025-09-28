# noqa: E501
"""JavaScript payloads for browser-based gaze runtime."""

PLAY_SCRIPT = r"""
(() => {
  // ===== profile key & coord conversions =====
  const PROFILE_KEY = (u = location) =>
    `gaze_profile`;

  const toClient = (x, y, kind="client") => {
    const vv = window.visualViewport;
    if (kind === "client") return { x, y };
    if (kind === "page")
      return {
        x: x - (vv?.pageLeft ?? window.scrollX),
        y: y - (vv?.pageTop ?? window.scrollY),
      };
    if (kind === "normalized")
      return { x: x * window.innerWidth, y: y * window.innerHeight };
    if (kind === "device") {
      const dpr = window.devicePixelRatio || 1;
      return { x: x / dpr, y: y / dpr };
    }
    throw new Error("unknown coord kind");
  };

  // ===== deepest hit test (shadow DOM + same-origin iframes) =====
  const deepEl = (clientX, clientY, rootDoc=document) => {
    let el = rootDoc.elementFromPoint(clientX, clientY);
    if (!el) return null;

    // descend into open shadow roots
    while (el && el.shadowRoot?.elementFromPoint) {
      const deeper = el.shadowRoot.elementFromPoint(clientX, clientY);
      if (!deeper || deeper === el) break;
      el = deeper;
    }

    // descend into same-origin iframes
    if (el?.tagName === "IFRAME") {
      const r = el.getBoundingClientRect();
      try {
        const d = el.contentDocument;
        if (d) {
          const inside = deepEl(clientX - r.left, clientY - r.top, d);
          if (inside) return inside;
        }
      } catch { /* cross-origin: ignore */ }
    }
    return el;
  };

  // ===== load profile from localStorage =====
  const profileKey = PROFILE_KEY();
  console.log(`🔍 Looking for profile key: "${profileKey}"`);
  
  const profile = (() => {
    try {
      const stored = localStorage.getItem(profileKey);
      console.log(`📦 localStorage content for "${profileKey}":`, stored ? "found" : "not found");
      if (!stored) {
        console.log("🗂️ Available localStorage keys:", Object.keys(localStorage));
      }
      return JSON.parse(stored || "null");
    } catch (e) {
      console.error(`❌ Error parsing profile from localStorage:`, e);
      return null;
    }
  })();
  
  if (!profile?.ranks) {
    console.warn(`⚠️ No saved gaze profile for this URL (${profileKey}). Run the Setup first.`);
    console.log("💡 To create a profile, you need to run a setup process that saves selector rankings to localStorage");
  } else {
    console.log(`✅ Loaded profile with ${Object.keys(profile.ranks).length} ranks:`, profile);
  }

  // Flatten ranks to an ordered list: [{rank, selector, resolve}]
  const recs = [];
  if (profile?.ranks) {
    const orderedRanks = Object.keys(profile.ranks)
      .map(Number)
      .sort((a, b) => a - b); // 1..5
    for (const rank of orderedRanks) {
      const val = profile.ranks[String(rank)];
      const arr = Array.isArray(val) ? val : (val ? [val] : []);
      for (const info of arr) {
        const selector = info.selector;
        const resolve = () => {
          try {
            return document.querySelector(selector);
          } catch {
            return null;
          }
        };
        recs.push({ rank, selector, resolve });
      }
    }
  }

  // ===== build selector-keyed maps =====
  const ranksBySelector = {};
  for (const { rank, selector } of recs) {
    if (!(selector in ranksBySelector) || rank < ranksBySelector[selector]) {
      ranksBySelector[selector] = rank; // keep best (lowest) rank per selector
    }
  }
  const occurrencesBySelector = {};
  Object.keys(ranksBySelector).forEach(sel => occurrencesBySelector[sel] = 0);

  // optional summary by rank
  const byRankCounts = { r1:0, r2:0, r3:0, r4:0, r5:0, unmatched:0 };

  // true if `candidate` is (or is inside) `target`
  const isWithin = (candidate, target) => {
    if (!candidate || !target) return false;
    let n = candidate instanceof Element ? candidate : candidate?.parentElement;
    while (n) {
      if (n === target) return true;
      if (n.parentElement) {
        n = n.parentElement;
        continue;
      }
      const root = n.getRootNode?.();
      if (root?.host) {
        n = root.host;
        continue;
      }
      const frameEl = n.ownerDocument?.defaultView?.frameElement;
      if (frameEl) {
        n = frameEl;
        continue;
      }
      break;
    }
    return false;
  };

  // ===== core API: feed gaze samples =====
  const record = (x, y, kind="client") => {
    const { x: cx, y: cy } = toClient(x, y, kind);
    const el = deepEl(cx, cy);

    // find first (best-rank) selector whose resolved node contains this point
    let hitRank = null, hitSelector = null;
    for (const rec of recs) {
      const target = rec.resolve();
      if (isWithin(el, target)) {
        hitRank = rec.rank;
        hitSelector = rec.selector;
        break;
      }
    }

    if (hitRank) {
      byRankCounts[`r${hitRank}`]++;
      occurrencesBySelector[hitSelector] =
        (occurrencesBySelector[hitSelector] || 0) + 1;
      return hitRank;
    } else {
      byRankCounts.unmatched++;
      return null;
    }
  };

  // ===== optional tester: Alt+Click to sample points (no highlight) =====
  let _h = null;
  const clickOn = () => {
    if (_h) return;
    _h = (e) => {
      if (!e.altKey || e.button!==0) return;
      e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
      const r = record(e.clientX, e.clientY, "client");
      console.log("sample →", r ? `rank ${r}` : "unmatched", {
        byRankCounts,
        occurrencesBySelector,
      });
    };
    addEventListener("click", _h, true);
    console.log("🟦 Play test ON: Alt+Click to sample (Esc to stop)");
    const key = (ev) => {
      if (ev.key === "Escape") {
        clickOff();
        removeEventListener("keydown", key, true);
      }
    };
    addEventListener("keydown", key, true);
  };
  const clickOff = () => {
    if (!_h) return;
    removeEventListener("click", _h, true);
    _h = null;
    console.log("🟦 Play test OFF");
  };

  // ===== end: return the two JSON maps =====
  const end = () => {
    clickOff();
    // Log for convenience
    console.log(
      "🏷️ ranksBySelector =",
      JSON.stringify(ranksBySelector, null, 2)
    );
    console.log(
      "🔢 occurrencesBySelector =",
      JSON.stringify(occurrencesBySelector, null, 2)
    );
    return { ranksBySelector, occurrencesBySelector };
  };

  // ===== debug helper (optional): see which selectors resolve right now =====
  const debugSelectors = () => {
    const rows = Object.keys(ranksBySelector).map(sel => {
      let ok = false;
      try { ok = !!document.querySelector(sel); } catch { ok = false; }
      return { selector: sel, resolves: ok };
    });
    console.table(rows);
    return rows;
  };

  // ===== debug helper: create a test profile =====
  const createTestProfile = (testSelectors = {}) => {
    const defaultTestProfile = {
      ranks: {
        "1": [{ selector: "h1" }],
        "2": [{ selector: "nav" }, { selector: ".navigation" }],
        "3": [{ selector: "main" }, { selector: ".content" }],
        "4": [{ selector: "button" }, { selector: ".btn" }],
        "5": [{ selector: "footer" }, { selector: ".footer" }]
      }
    };
    
    const profileToSave = Object.keys(testSelectors).length > 0 
      ? { ranks: testSelectors } 
      : defaultTestProfile;
      
    const key = PROFILE_KEY();
    localStorage.setItem(key, JSON.stringify(profileToSave));
    console.log(`✅ Created test profile for ${key}:`, profileToSave);
    console.log("🔄 Reload the page to use the new profile");
    return profileToSave;
  };

  // expose API
  window.__gazePlay = {
    record, clickOn, clickOff, end,
    // state/refs:
    countsByRank: byRankCounts,
    ranksBySelector, occurrencesBySelector,
    profile, recs,
    // debug:
    debugSelectors, createTestProfile
  };

  console.log(
    profile
      ? "✅ Play ready. Stream __gazePlay.record(x,y,kind). Call __gazePlay.end() for the two JSON maps."
      : "⚠️ No profile found. Run Setup on this URL first."
  );
})();
"""
