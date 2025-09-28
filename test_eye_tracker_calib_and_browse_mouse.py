"""
Test script for eye tracking - sends                 try:
                    # Get current gaze position from eye tracker
                    position = tracker.get_current_gaze_position()
                    
                    # Check if we got a valid position (handle numpy arrays properly)
                    if position is not None and len(position) == 2:
                        try:
                            # Convert to regular Python numbers to avoid numpy array issues
                            x, y = float(position[0]), float(position[1])
                            gaze_count += 1
                            
                            # Print every 10th position to avoid spam
                            if gaze_count % 10 == 0:
                                print(f"[TEST] 👁️ Gaze #{gaze_count}: ({x:.1f}, {y:.1f})")
                        except (ValueError, TypeError, IndexError) as e:
                            # Skip this iteration if position data is invalid
                            time.sleep(0.1)
                            continue
                    else:
                        # No gaze detected, continue to next iteration
                        time.sleep(0.1)
                        continuedinates to browser gazePlay system.
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
    Run mouse tracking and open browser to config['url'] for config['duration'] minutes.
    Args:
        config (dict): Must contain 'url' and 'duration' (minutes as string or number)
        debug (bool): If True, enables debug mode for tracker and logs seconds remaining
    """

    # Initialize and calibrate eye tracker
    tracker = EyeTracker()
    print("[TEST] 👁️ Starting eye tracker calibration...")
    calibrated = tracker.recalibrate(25)
    if not calibrated:
        print("[TEST] ❌ Calibration failed or cancelled.")
        return
    print(f"[TEST] ✅ Calibration complete. Opening Selenium browser to {config.get('url')} and will track gaze...")

    # Will be set after browser is launched
    driver = None

    # Define tracking thread (but do not start yet) - USING MOUSE FOR TESTING
    def tracking_thread():
        print("[TEST] �️ Eye tracking thread started - sending gaze position to browser...")
        print("[TEST] � Look around to generate gaze points!")
        gaze_count = 0
        
        try:
            while driver is not None:
                try:
                    # Get current gaze position from eye tracker
                    position = tracker.get_current_gaze_position()
                    if position is not None:
                        x, y = position
                        gaze_count += 1
                        
                        # Print every 10th position to avoid spam
                        if gaze_count % 10 == 0:
                            print(f"[TEST] �️ Gaze #{gaze_count}: ({x:.1f}, {y:.1f})")
                    else:
                        # No gaze detected, continue to next iteration
                        time.sleep(0.1)
                        continue
                    
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
                            print(f"[TEST] ❌ Method 1 failed: {e}")
                    
                    # Method 2: Store in global array as backup
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
                            print(f"[TEST] ❌ Method 2 (backup storage) failed: {e}")
                    
                    # Method 3: Trigger custom event as another backup
                    try:
                        driver.execute_script("""
                            const event = new CustomEvent('gazepoint', {
                                detail: { x: arguments[0], y: arguments[1], type: 'device' }
                            });
                            window.dispatchEvent(event);
                        """, x, y)
                    except Exception as e:
                        if gaze_count <= 5:
                            print(f"[TEST] ❌ Method 3 (custom event) failed: {e}")
                    
                    # Sample every 100ms to get smooth tracking
                    time.sleep(0.1)
                        
                except Exception as e:
                    print(f"[TEST] ❌ Error processing gaze position: {e}")
                    time.sleep(0.5)
        except KeyboardInterrupt:
            print("[TEST] 🛑 Eye tracking interrupted by user")
        except Exception as e:
            print(f"[TEST] ❌ Eye tracking error: {e}")
        finally:
            print(f"[TEST] 🛑 Eye tracking thread stopped - sent {gaze_count} gaze points")
            # Cleanup eye tracker resources
            if hasattr(tracker, 'cap') and tracker.cap:
                try:
                    tracker.cap.release()
                except Exception:
                    pass

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
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome_dev_test")  # Required for --disable-web-security
    chrome_options.add_argument("--start-maximized")  # Start browser maximized
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    
    # Set browser to fullscreen mode for accurate gaze coordinate mapping
    print("[TEST] 📺 Setting browser to fullscreen mode...")
    try:
        driver.fullscreen_window()
        print("[TEST] ✅ Browser is now in fullscreen mode")
    except Exception as e:
        print(f"[TEST] ⚠️ Could not set fullscreen mode: {e}")
        # Fallback to maximize if fullscreen fails
        try:
            driver.maximize_window()
            print("[TEST] ✅ Browser maximized as fallback")
        except Exception as e2:
            print(f"[TEST] ⚠️ Could not maximize window: {e2}")

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
    // if shadow root, recurse
    if (el.shadowRoot) {
      const inner = deepEl(clientX, clientY, el.shadowRoot);
      if (inner) el = inner;
    }
    // if same-origin iframe, recurse
    if (el.tagName === "IFRAME") {
      try {
        const inner = deepEl(clientX, clientY, el.contentDocument);
        if (inner) el = inner;
      } catch { /* cross-origin */ }
    }
    return el;
  };

  // ===== selector ranking & counting =====
  const ranksBySelector = {}; // selector -> numeric rank
  const occurrencesBySelector = {}; // selector -> count
  const byRankCounts = new Array(5).fill(0); // counts by rank (0=rank1, 1=rank2, etc.)
  const recs = []; // all recorded interactions

  let profile;
  try {
    profile = JSON.parse(localStorage.getItem(PROFILE_KEY));
    if (profile && profile.selectors && Array.isArray(profile.selectors)) {
      profile.selectors.forEach(sel => {
        ranksBySelector[sel.selector] = sel.rank;
        occurrencesBySelector[sel.selector] = 0;
      });
    }
  } catch { profile = null; }

  // ===== recording & click handlers =====
  const record = (x, y, kind="client") => {
    const { x: clientX, y: clientY } = toClient(x, y, kind);
    const el = deepEl(clientX, clientY);
    if (!el || el === document.documentElement || el === document.body) return;

    const tag = el.tagName.toLowerCase();
    const id = el.id ? `#${el.id}` : "";
    const cls = el.className && typeof el.className === "string" ? 
      el.className.split(" ").filter(c => c).map(c => `.${c}`).join("") : "";
    const selector = tag + id + cls;

    if (ranksBySelector[selector] !== undefined) {
      const rank = ranksBySelector[selector];
      occurrencesBySelector[selector]++;
      if (rank >= 1 && rank <= 5) byRankCounts[rank - 1]++;
    }

    recs.push({ x: clientX, y: clientY, selector, timestamp: Date.now() });
  };

  const clickOn = () => {
    document.addEventListener("click", e => record(e.clientX, e.clientY, "client"), { passive: true });
  };

  const clickOff = () => {
    document.removeEventListener("click", record);
  };

  const end = () => ({
    ranksBySelector,
    occurrencesBySelector
  });

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
            
            print("📍 Starting eye tracking thread to send gaze coordinates...")
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
        print(f"[TEST] Could not close browser: {e}")


if __name__ == "__main__":
    # Example config - simulating a config that was passed from the UI
    test_config = {
        'url': 'https://www.wikipedia.org',
        'duration': '0.5',  # 0.5 minutes = 30 seconds for testing
        'origin': 'https://www.wikipedia.org',
        'path': '/',
        'selectors': [
            {'selector': 'a', 'rank': 1},
            {'selector': '.mw-headline', 'rank': 2},
            {'selector': 'p', 'rank': 3}
        ]
    }
    
    run_calibration_and_tracking_with_config(test_config, debug=True)