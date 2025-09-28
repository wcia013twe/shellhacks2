"""
Test script for mouse tracking (testing mode) - sends mouse coordinates to browser gazePlay system.
"""
                    print(f"[TEST] ❌ Error processing mouse position: {e}")
                    time.sleep(0.5)owser to Wikipedia home page.
"""



from src.eye_tracking.EyeTracker import EyeTracker
import threading
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager



def run_calibration_and_tracking_with_config(config, debug=False):
    """
    Run calibration, then eye tracking and open browser to config['url'] for config['duration'] minutes.
    Args:
        config (dict): Must contain 'url' and 'duration' (minutes as string or number)
        debug (bool): If True, enables debug mode for tracker and logs seconds remaining
    """

    # TESTING MODE: Skip eye tracker calibration, use mouse instead
    tracker = None  # We don't need the eye tracker for mouse testing
    print("[TEST] 🖱️ MOUSE TESTING MODE - Skipping eye tracker calibration")
    print(f"[TEST] Opening Selenium browser to {config.get('url')} and will track mouse movements...")

    # Will be set after browser is launched
    driver = None

    # Define tracking thread (but do not start yet)
    def tracking_thread():
        print("[TEST] 🖱️ Mouse tracking thread started - sending mouse position to browser...")
        print("[TEST] 💡 Move your mouse around to simulate gaze points!")
        gaze_count = 0
        import pyautogui
        
        try:
            while driver is not None:
                try:
                    # Get current mouse position
                    x, y = pyautogui.position()
                    gaze_count += 1
                    
                    # Print every 10th position to avoid spam
                    if gaze_count % 10 == 0:
                        print(f"[TEST] �️ Mouse #{gaze_count}: ({x}, {y})")
                        
                        # Method 1: Try direct __gazePlay.record call
                        try:
                            result = driver.execute_script("""
                                if (window.__gazePlay && typeof window.__gazePlay.record === 'function') {
                                    window.__gazePlay.record(arguments[0], arguments[1], 'device');
                                    console.log('✅ gazePlay.record called with:', arguments[0], arguments[1]);
                                    return true;
                                } else {
                                    console.error('❌ __gazePlay not found or record not a function');
                                    return false;
                                }
                            """, x, y)
                            
                        if not result and gaze_count <= 5:
                            print("[TEST] ⚠️ __gazePlay.record call failed - trying alternatives...")
                    except Exception as e:
                        if gaze_count <= 5:
                            print(f"[TEST] ❌ Method 1 failed: {e}")                        # Method 2: Store in global array as backup
                        try:
                            driver.execute_script("""
                                if (!window.__gazePoints) window.__gazePoints = [];
                                window.__gazePoints.push({
                                    x: arguments[0], 
                                    y: arguments[1], 
                                    timestamp: Date.now(),
                                    type: 'device'
                                });
                            if (window.__gazePoints.length % 50 === 0) {
                                console.log('📦 Stored ' + window.__gazePoints.length + ' gaze points so far');
                            }
                        """, x, y)
                    except Exception as e:
                        if gaze_count <= 5:
                            print(f"[TEST] ❌ Method 2 (backup storage) failed: {e}")                        # Method 3: Trigger custom event as another backup
                        try:
                            driver.execute_script("""
                                const event = new CustomEvent('gazepoint', {
                                    detail: { x: arguments[0], y: arguments[1], type: 'device' }
                                });
                                window.dispatchEvent(event);
                                console.log('� Dispatched gazepoint event:', arguments[0], arguments[1]);
                            """, x, y)
                        except Exception as e:
                            print(f"[TEST] ❌ Method 3 (custom event) failed: {e}")
                        
                        # Slow down a bit to avoid overwhelming the browser
                        time.sleep(0.1)
                        
                    except Exception as e:
                        print(f"[TEST] ❌ Error processing gaze point: {e}")
        except KeyboardInterrupt:
            print("[TEST] 🛑 Mouse tracking interrupted by user")
        except Exception as e:
            print(f"[TEST] ❌ Mouse tracking error: {e}")
        finally:
            print(f"[TEST] 🛑 Mouse tracking thread stopped - sent {gaze_count} mouse positions")
            # No cleanup needed for mouse tracking

  # ...existing code for browser setup, JS injection, etc...


    # Get URL and duration from config
    url = config.get('url', 'https://www.wikipedia.org')
    duration_str = str(config.get('duration', '2'))
    try:
        if 'min' in duration_str.lower():
            duration = float(duration_str.lower().replace('min', '').replace('utes', '').strip())
        else:
            duration = float(duration_str)
    except:
        duration = 0.5
    
    duration_sec = int(duration * 60)  # Convert minutes to seconds
    print(f"[TEST] Test duration: {duration} minutes ({duration_sec} seconds)")


    # Open Selenium browser to specified URL
    print(f"[TEST] Opening Selenium browser to {url} ...")
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # === Option 3: Disable web security and site isolation for local testing (CSP bypass) ===
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome_dev_test")  # Required for --disable-web-security
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)

    # ...existing code for browser setup, JS injection, etc...

    # Wait for page to fully load before injecting JS
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except Exception as e:
        print(f"[TEST] Warning: Page did not load in time: {e}")

    # === Inject config as profile into localStorage ===
    # Compute the profile key as in the JS PROFILE_KEY logic
    profile_key = f"__gaze_profile__{config['origin']}{config['path']}"
    try:
        driver.execute_script("localStorage.setItem(arguments[0], JSON.stringify(arguments[1]));", profile_key, config)
        print(f"[TEST] Injected config as profile into localStorage with key: {profile_key}")
    except Exception as e:
        print(f"[TEST] Could not inject config into localStorage: {e}")

    # === Inject gazePlay JS snippet (robust method) ===
    gaze_play_js = '''(() => {
  // ===== profile key & coord conversions =====
  const PROFILE_KEY = "__gaze_profile__" + window.location.origin + window.location.pathname;
  const toClient = (x, y, kind="client") => {
    const vv = window.visualViewport;
    if (kind === "client") return { x, y };
    if (kind === "page")   return { x: x - (vv?.pageLeft ?? window.scrollX), y: y - (vv?.pageTop ?? window.scrollY) };
    if (kind === "normalized") return { x: x * window.innerWidth, y: y * window.innerHeight };
    if (kind === "device") { const dpr = window.devicePixelRatio || 1; return { x: x / dpr, y: y / dpr }; }
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
  const profile = (() => { try { return JSON.parse(localStorage.getItem(PROFILE_KEY) || "null"); } catch { return null; } })();
  if (!profile?.ranks) console.warn("⚠️ No saved gaze profile for this URL. Run the Setup first.");

  // Flatten ranks to an ordered list: [{rank, selector, resolve}]
  const recs = [];
  if (profile?.ranks) {
    const orderedRanks = Object.keys(profile.ranks).map(Number).sort((a,b)=>a-b); // 1..5
    for (const rank of orderedRanks) {
      const val = profile.ranks[String(rank)];
      const arr = Array.isArray(val) ? val : (val ? [val] : []);
      for (const info of arr) {
        const selector = info.selector;
        const resolve = () => { try { return document.querySelector(selector); } catch { return null; } };
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
      if (n.parentElement) { n = n.parentElement; continue; }
      const root = n.getRootNode?.(); if (root?.host) { n = root.host; continue; }
      const frameEl = n.ownerDocument?.defaultView?.frameElement; if (frameEl) { n = frameEl; continue; }
      break;
    }
    return false;
  };

  // ===== core API: feed gaze samples =====
  const record = (x, y, kind="client") => {
    console.log("x:", x, "y:", y);
    const { x: cx, y: cy } = toClient(x, y, kind);
    const el = deepEl(cx, cy);

    // find first (best-rank) selector whose resolved node contains this point
    let hitRank = null, hitSelector = null;
    for (const rec of recs) {
      const target = rec.resolve();
      if (isWithin(el, target)) { hitRank = rec.rank; hitSelector = rec.selector; break; }
    }

    if (hitRank) {
      byRankCounts[`r${hitRank}`]++;
      occurrencesBySelector[hitSelector] = (occurrencesBySelector[hitSelector] || 0) + 1;
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
      console.log("sample →", r ? `rank ${r}` : "unmatched", { byRankCounts, occurrencesBySelector });
    };
    addEventListener("click", _h, true);
    console.log("🟦 Play test ON: Alt+Click to sample (Esc to stop)");
    const key = (ev)=>{ if(ev.key==="Escape"){ clickOff(); removeEventListener("keydown", key, true); } };
    addEventListener("keydown", key, true);
  };
  const clickOff = () => { if(!_h) return; removeEventListener("click", _h, true); _h=null; console.log("🟦 Play test OFF"); };

  // ===== end: return the two JSON maps =====
  const end = () => {
    clickOff();
    // Log for convenience
    console.log("🏷️ ranksBySelector =", JSON.stringify(ranksBySelector, null, 2));
    console.log("🔢 occurrencesBySelector =", JSON.stringify(occurrencesBySelector, null, 2));
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

  // expose API
  window.__gazePlay = {
    record, clickOn, clickOff, end,
    // state/refs:
    countsByRank: byRankCounts,
    ranksBySelector, occurrencesBySelector,
    profile, recs,
    // debug:
    debugSelectors
  };

  console.log(profile ? "✅ Play ready. Stream __gazePlay.record(x,y,kind). Call __gazePlay.end() for the two JSON maps." :
                        "⚠️ No profile found. Run Setup on this URL first.");
})();
'''

    try:
        print("🚀 Injecting gazePlay JS...")
        result = driver.execute_script(gaze_play_js)
        print("✅ gazePlay JS injected.")
        # Verify script was loaded by checking for the global object
        verification = driver.execute_script("return typeof window.__gazePlay;")
        if verification == "object":
            print("🎯 gazePlay system is active and ready!")
        else:
            print("⚠️ Script injection may have failed - verification failed")
        # Re-inject after a short delay to survive SPA reloads or late scripts
        import time as _time
        _time.sleep(2)
        driver.execute_script(gaze_play_js)
        print("[TEST] Re-injected gazePlay JS after delay.")
        verification2 = driver.execute_script("return typeof window.__gazePlay;")
        if verification2 == "object":
            print("🎯 gazePlay system is active after re-injection!")
        else:
            print("⚠️ Script re-injection may have failed - verification failed")
    except Exception as e:
        print(f"[TEST] Could not inject gazePlay JS: {e}")

    try:
        print("🚀 Injecting gazePlay JS...")
        result = driver.execute_script(gaze_play_js)
        print("✅ gazePlay JS injected.")
        # Verify script was loaded by checking for the global object
        verification = driver.execute_script("return typeof window.__gazePlay;")
        if verification == "object":
            print("🎯 gazePlay system is active and ready!")
            
            # Detailed verification
            try:
                gazeplay_info = driver.execute_script("""
                    return {
                        hasGazePlay: typeof window.__gazePlay !== 'undefined',
                        hasRecord: typeof window.__gazePlay?.record === 'function',
                        hasEnd: typeof window.__gazePlay?.end === 'function',
                        profileExists: !!window.__gazePlay?.profile,
                        url: window.location.href
                    };
                """)
                print(f"[TEST] 🔍 Browser verification: {gazeplay_info}")
                
                if not gazeplay_info.get('hasRecord'):
                    print("[TEST] ❌ __gazePlay.record function not found!")
                elif not gazeplay_info.get('profileExists'):
                    print("[TEST] ⚠️ No profile found - gaze recording may not work properly")
                else:
                    print("[TEST] ✅ All gazePlay functions verified!")
                
            except Exception as e:
                print(f"[TEST] ⚠️ Verification error: {e}")
            
            print("📍 Starting eye tracking thread to send gaze points...")
            # Now start the tracking thread (driver and gazePlay are ready)
            t = threading.Thread(target=tracking_thread, daemon=False)
            t.start()
        else:
            print("⚠️ Script injection may have failed - verification failed")
        # Re-inject after a short delay to survive SPA reloads or late scripts
        import time as _time
        _time.sleep(2)
        driver.execute_script(gaze_play_js)
        print("[TEST] Re-injected gazePlay JS after delay.")
        verification2 = driver.execute_script("return typeof window.__gazePlay;")
        if verification2 == "object":
            print("🎯 gazePlay system is active after re-injection!")
        else:
            print("⚠️ Script re-injection may have failed - verification failed")
    except Exception as e:
        print(f"[TEST] Could not inject gazePlay JS: {e}")


    # Show countdown timer
    print(f"\n⏰ Starting {duration_sec}-second test countdown...")
    for sec in range(duration_sec, 0, -1):
        mins, secs = divmod(sec, 60)
        if sec % 10 == 0 or sec <= 10:  # Print every 10 seconds, and final 10 seconds
            if mins > 0:
                print(f"⏱️  Time remaining: {mins}:{secs:02d} ({sec}s total)")
            else:
                print(f"⏱️  Time remaining: {sec} seconds")
        time.sleep(1)
    print("🏁 Test time completed!")


    print("[TEST] Test complete. Closing browser and eye tracker.")

    # At the end, get results from multiple sources
    import json
    
    print("\n🔍 Collecting gaze data from browser...")
    
    # Method 1: Try __gazePlay.end()
    try:
        gazeplay_result = driver.execute_script("return window.__gazePlay ? window.__gazePlay.end() : null;")
        if gazeplay_result is None:
            print("[TEST] ❌ __gazePlay is not defined in the browser context!")
        else:
            print("[TEST] ✅ GazePlay results:")
            print(json.dumps(gazeplay_result, indent=2))
    except Exception as e:
        print(f"[TEST] ❌ Could not get gazePlay results: {e}")
    
    # Method 2: Check backup gaze points array
    try:
        backup_points = driver.execute_script("return window.__gazePoints || [];")
        if backup_points:
            print(f"\n[TEST] ✅ Found {len(backup_points)} backup gaze points:")
            for i, point in enumerate(backup_points[-10:]):  # Show last 10 points
                print(f"  Point {i+1}: ({point['x']:.1f}, {point['y']:.1f}) at {point['timestamp']}")
            if len(backup_points) > 10:
                print(f"  ... and {len(backup_points)-10} more points")
        else:
            print("[TEST] ❌ No backup gaze points found")
    except Exception as e:
        print(f"[TEST] ❌ Could not get backup points: {e}")
    
    # Method 3: Check console logs for evidence of gaze point reception
    try:
        console_check = driver.execute_script("""
            return {
                gazePlayExists: typeof window.__gazePlay !== 'undefined',
                backupPointsCount: (window.__gazePoints || []).length,
                currentUrl: window.location.href
            };
        """)
        print(f"\n[TEST] 📊 Final browser state: {console_check}")
    except Exception as e:
        print(f"[TEST] ❌ Could not check final browser state: {e}")

    # Close the browser after test is complete
    try:
        if driver is not None:
            # driver.quit()
            # print("[TEST] Browser closed.")
            pass
    except Exception as e:
        print(f"[TEST] Error closing browser: {e}")

    # Attempt to close the eye tracker cleanly
    if t.is_alive():
        print("[TEST] Waiting for eye tracker thread to finish...")
        t.join(timeout=5)
    # Use the new kill() method
    if hasattr(tracker, 'kill'):
        tracker.kill()
    print("[TEST] Eye tracker closed.")

    return out


# Example usage:
if __name__ == "__main__":
    # Example config dict
    config = {
        "origin": "https://fr.wikipedia.org",
        "path": "/wiki/Wikip%C3%A9dia:Accueil_principal",
        "url": "https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Accueil_principal",
        "duration": "3",
        "created_at": "2025-09-28T07:09:27.978942",
        "ranks": {
            "1": [
                {"selector": "#bodyContent", "tag": "div"}
            ],
            "3": [
                {"selector": "img[data-file-width=\"449\"]", "tag": "img"},
                {"selector": "td:nth-of-type(1) > span:nth-of-type(1) > a:nth-of-type(1)", "tag": "a"},
                {"selector": "td:nth-of-type(2) > span:nth-of-type(1) > a:nth-of-type(1)", "tag": "a"}
            ],
            "4": [
                {"selector": "#Wikipédia", "tag": "h2"},
                {"selector": "#firstHeading", "tag": "h1"},
                {"selector": "#vector-appearance-pinned-container", "tag": "div"}
            ]
        }
    }
    out = run_calibration_and_tracking_with_config(config, debug=True)
    print(json.dumps(out, indent=2))
