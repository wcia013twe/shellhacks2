"""
Browser management module using Selenium WebDriver.

This module provides a real browser experience with full JavaScript injection
capabilities, bypassing iframe restrictions that block sites like GitHub.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import messagebox
import threading
import time
import tempfile
import os

from .play_script import PLAY_SCRIPT


class BrowserManager:
    """Manages Selenium WebDriver browser with JavaScript injection capabilities."""
    
    def __init__(self):
        """Initialize the Selenium browser manager."""
        self.driver = None
        self.eye_tracker = None
        self.tracking_thread = None
        self.tracking_active = False
        self.gaze_play_injected = False
        
    def validate_url(self, url):
        """Validate and normalize the URL."""
        if not url:
            return None, "Please enter a URL"
        
        # Clean up any malformed URLs first
        url = url.strip()
        
        # Fix common malformed patterns
        if url.startswith('https://https://'):
            url = url.replace('https://https://', 'https://')
        elif url.startswith('http://https://'):
            url = url.replace('http://https://', 'https://')
        elif url.startswith('https://http://'):
            url = url.replace('https://http://', 'http://')
            
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        return url, None
    
    def _create_chrome_options(self):
        """Create Chrome options for optimal browsing experience."""
        chrome_options = Options()
        
        # Disable security restrictions for JavaScript injection
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Performance optimizations
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Window settings
        chrome_options.add_argument("--start-maximized")
        
        # Remove "Chrome is being controlled" banner
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        return chrome_options
    
    def _inject_sidebar_overlay(self):
        """Sidebar overlay disabled - clean browser experience."""
        pass  # No sidebar injection for clean browser experience
    
    def launch_browser(self, url, main_window=None, on_ready_callback=None):
        """
        Launch Selenium Chrome browser with the specified URL.
        
        Args:
            url: URL to open
            main_window: Main tkinter window to hide during browser session
            on_ready_callback: Function to call when browser is fully loaded and ready
            
        Returns:
            tuple: (success: bool, driver or error_message)
        """
        # Validate URL
        validated_url, error = self.validate_url(url)
        if error:
            if main_window:
                messagebox.showerror("Error", error)
            return False, error
        
        try:
            # Hide main window if provided
            if main_window:
                main_window.withdraw()
            
            # Setup Chrome options
            chrome_options = self._create_chrome_options()
            
            # Create WebDriver with automatic driver management
            print("🚀 Starting Chrome browser...")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Navigate to URL
            print(f"🌐 Loading: {validated_url}")
            self.driver.get(validated_url)
            self.gaze_play_injected = False
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Inject sidebar overlay (skip if fails due to security policies)
            try:
                self._inject_sidebar_overlay()
            except Exception as e:
                print(f"⚠️ Sidebar injection skipped (security restrictions): {str(e)[:100]}...")
                # Continue without sidebar - this is not critical
            
            print("✅ Browser launched successfully!")
            print("💡 Features:")
            print("   • Clean browsing experience without overlays")
            print("   • All websites work (no iframe restrictions!)")
            print("   • Full JavaScript injection support")
            self._ensure_gaze_play_bootstrap()

            
            # Call ready callback now that browser is fully loaded
            if on_ready_callback:
                try:
                    on_ready_callback()
                    print("✅ Ready callback executed")
                except Exception as e:
                    print(f"⚠️ Ready callback error: {e}")
            
            # Start monitoring (non-blocking)
            self._start_browser_monitor(main_window)
            
            return True, self.driver
            
        except WebDriverException as e:
            error_msg = f"Failed to launch browser: {e}"
            if main_window:
                messagebox.showerror("Error", error_msg)
            return False, error_msg
    
    def _start_browser_monitor(self, main_window):
        """Monitor browser and handle cleanup when closed."""
        try:
            while self.driver:
                # Check if browser is still open
                try:
                    self.driver.current_url
                    time.sleep(1)
                except Exception as e:
                    # Browser closed or connection lost
                    if "No connection could be made" in str(e):
                        print("🔌 Browser connection lost")
                    else:
                        print("👋 Browser closed by user")
                    break
        except Exception as e:
            print(f"⚠️ Browser monitor error: {e}")
        finally:
            # Cleanup and restore main window
            self.close_browser()
            if main_window:
                main_window.deiconify()
    
    def inject_javascript(self, script):
        """Inject custom JavaScript into the current page."""
        if self.driver:
            try:
                return self.driver.execute_script(script)
            except Exception as e:
                # Check if browser session is lost
                if "No connection could be made" in str(e) or "Connection refused" in str(e):
                    print("🔌 Browser session lost - stopping gaze tracking")
                    self.tracking_active = False
                    self.driver = None
                else:
                    print(f"⚠️ JavaScript injection failed: {e}")
                return None
        return None
    
    def navigate_to(self, url):
        """Navigate to a new URL."""
        if self.driver:
            try:
                validated_url, error = self.validate_url(url)
                if error:
                    return False
                
                self.driver.get(validated_url)
                self.gaze_play_injected = False
                
                # Wait for page load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                self._ensure_gaze_play_bootstrap()
                return True
                
            except Exception as e:
                print(f"⚠️ Navigation failed: {e}")
                return False
        return False
    
    def integrate_eye_tracker(self, eye_tracker):
        """Integrate eye tracking with real-time gaze overlay."""
        self.eye_tracker = eye_tracker
        
        # Inject eye tracking overlay
        overlay_script = """
        // Create gaze overlay
        if (!window.gazeOverlay) {
            const overlay = document.createElement('div');
            overlay.id = 'gaze-overlay';
            overlay.style.cssText = `
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                pointer-events: none; z-index: 999998; background: transparent;
            `;
            
            const gazeCircle = document.createElement('div');
            gazeCircle.id = 'gaze-circle';
            gazeCircle.style.cssText = `
                position: absolute; width: 40px; height: 40px;
                border: 3px solid #FFD700; border-radius: 50%;
                transform: translate(-50%, -50%); display: none;
                background: rgba(255, 215, 0, 0.2);
                box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
            `;
            
            overlay.appendChild(gazeCircle);
            document.body.appendChild(overlay);
            
            window.gazeOverlay = {
                update: (x, y, fixating) => {
                    gazeCircle.style.left = x + 'px';
                    gazeCircle.style.top = y + 'px';
                    gazeCircle.style.display = 'block';
                    gazeCircle.style.borderColor = fixating ? '#00FF00' : '#FFD700';
                    gazeCircle.style.background = fixating ? 'rgba(0, 255, 0, 0.3)' : 'rgba(255, 215, 0, 0.2)';
                },
                hide: () => gazeCircle.style.display = 'none'
            };
        }
        """
        
        self.inject_javascript(overlay_script)
        
        # Start gaze tracking thread
        def gaze_loop():
            self.tracking_active = True
            self._ensure_gaze_play_bootstrap()
            last_record_ts = 0.0
            consecutive_errors = 0
            max_consecutive_errors = 5
            
            while self.tracking_active and self.driver:
                try:
                    # Check if driver is still valid
                    if not self.driver:
                        print("🔌 Browser driver lost - stopping gaze tracking")
                        break
                        
                    gaze = self.eye_tracker.get_gaze()
                    if gaze and gaze.get('position') is not None:
                        position = gaze['position']
                        # Handle numpy array or tuple/list positions safely
                        if hasattr(position, '__len__') and len(position) >= 2:
                            try:
                                x, y = float(position[0]), float(position[1])
                                # Validate coordinates are reasonable
                                if 0 <= x <= 10000 and 0 <= y <= 10000:
                                    fixating = gaze.get('fixation', False)

                                    overlay_script = (
                                        f"if(window.gazeOverlay) "
                                        f"window.gazeOverlay.update({x}, {y}, "
                                        f"{str(fixating).lower()});"
                                    )
                                    self.inject_javascript(overlay_script)

                                    now = time.time()
                                    if (self.gaze_play_injected and 
                                        now - last_record_ts >= 1.0):
                                        record_js = (
                                            "if(window.__gazePlay?.record){"
                                            f"window.__gazePlay.record("
                                            f"{x:.2f}, {y:.2f}, 'device');"
                                            "}"
                                        )
                                        self.inject_javascript(record_js)
                                        last_record_ts = now
                                        
                                # Reset error counter on success
                                consecutive_errors = 0
                                        
                            except (ValueError, TypeError, IndexError):
                                # Skip invalid position data
                                pass

                    time.sleep(0.033)  # ~30 FPS
                    
                except Exception as e:
                    consecutive_errors += 1
                    print(f"⚠️ Gaze tracking error ({consecutive_errors}): {e}")
                    
                    # Stop tracking if too many consecutive errors
                    if consecutive_errors >= max_consecutive_errors:
                        print(f"🛑 Too many consecutive errors ({consecutive_errors}), "
                              f"stopping gaze tracking")
                        self.tracking_active = False
                        break
                        
                    time.sleep(0.1)
            
            print("👁️ Gaze tracking loop ended")

        self.tracking_thread = threading.Thread(target=gaze_loop, daemon=True)
        self.tracking_thread.start()
        print("✅ Eye tracker integrated!")
    
    def close_browser(self):
        """Close the browser and cleanup."""
        self.tracking_active = False
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
        
        self.gaze_play_injected = False
        print("👋 Browser closed")
    
    def get_webview_window(self):
        """Get the current driver (compatibility method)."""
        return self.driver
    
    def is_browser_alive(self):
        """Check if the browser session is still active."""
        if not self.driver:
            return False
        try:
            self.driver.current_url
            return True
        except Exception:
            return False

    def _ensure_gaze_play_bootstrap(self):
        """Inject the gaze play JavaScript runtime if it isn't already available."""
        if not self.driver or self.gaze_play_injected:
            return

        try:
            self.driver.execute_script(PLAY_SCRIPT)
            self.gaze_play_injected = True
            print("✔ __gazePlay runtime loaded")
        except Exception as e:
            print(f"⚠️ Could not inject __gazePlay runtime: {e}")

    def finalize_gaze_play(self):
        """Flush the gaze play counters and log the selector summaries."""
        if not self.driver:
            return None

        try:
            script = (
                "if (window.__gazePlay && typeof window.__gazePlay.end === 'function') {"
                "const out = window.__gazePlay.end();"
                "if (out) {"
                "console.log(out.ranksBySelector, out.occurrencesBySelector);"
                "return out;"
                "}"
                "}"
                "return null;"
            )
            return self.inject_javascript(script)
        except Exception as e:
            print(f"⚠️ Failed to finalize gaze play data: {e}")
            return None
