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


class BrowserManager:
    """Manages Selenium WebDriver browser with JavaScript injection capabilities."""
    
    def __init__(self):
        """Initialize the Selenium browser manager."""
        self.driver = None
        self.eye_tracker = None
        self.tracking_thread = None
        self.tracking_active = False
        
    def validate_url(self, url):
        """Validate and normalize the URL."""
        if not url:
            return None, "Please enter a URL"
            
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
        """Inject a sidebar overlay into any website for navigation."""
        sidebar_script = """
        // Remove any existing sidebar
        const existingSidebar = document.getElementById('selenium-sidebar');
        if (existingSidebar) existingSidebar.remove();
        
        // Create sidebar overlay
        const sidebar = document.createElement('div');
        sidebar.id = 'selenium-sidebar';
        sidebar.innerHTML = `
            <div style="
                position: fixed; top: 0; left: -280px; width: 280px; height: 100vh;
                background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
                color: #e2e8f0; z-index: 999999; transition: left 0.3s ease;
                border-right: 2px solid #4a5568; font-family: Arial, sans-serif;
                display: flex; flex-direction: column;
            " id="sidebar-panel">
                <div style="padding: 15px; background: rgba(255,255,255,0.1); border-bottom: 1px solid #4a5568;">
                    <h3 style="margin: 0; font-size: 18px;">🌐 Quick Nav</h3>
                </div>
                <div style="flex: 1; overflow-y: auto; padding: 10px 0;">
                    <a href="https://www.google.com" style="display: block; padding: 10px 15px; color: #cbd5e0; text-decoration: none; border-left: 3px solid transparent;">🔍 Google</a>
                    <a href="https://github.com" style="display: block; padding: 10px 15px; color: #cbd5e0; text-decoration: none; border-left: 3px solid transparent;">🐙 GitHub</a>
                    <a href="https://stackoverflow.com" style="display: block; padding: 10px 15px; color: #cbd5e0; text-decoration: none; border-left: 3px solid transparent;">💻 Stack Overflow</a>
                    <a href="https://news.ycombinator.com" style="display: block; padding: 10px 15px; color: #cbd5e0; text-decoration: none; border-left: 3px solid transparent;">📰 Hacker News</a>
                    <a href="https://www.reddit.com" style="display: block; padding: 10px 15px; color: #cbd5e0; text-decoration: none; border-left: 3px solid transparent;">🤖 Reddit</a>
                    <a href="https://www.wikipedia.org" style="display: block; padding: 10px 15px; color: #cbd5e0; text-decoration: none; border-left: 3px solid transparent;">📚 Wikipedia</a>
                    <a href="https://www.youtube.com" style="display: block; padding: 10px 15px; color: #cbd5e0; text-decoration: none; border-left: 3px solid transparent;">🎥 YouTube</a>
                </div>
                <div style="padding: 10px 15px; border-top: 1px solid #4a5568; font-size: 12px; opacity: 0.8;">
                    <div>✅ No iframe restrictions!</div>
                </div>
            </div>
            
            <!-- Toggle Button -->
            <button style="
                position: fixed; top: 20px; left: 20px; z-index: 1000000;
                background: #4299e1; color: white; border: none; border-radius: 50%;
                width: 50px; height: 50px; cursor: pointer; font-size: 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3); transition: all 0.2s ease;
            " onclick="toggleSidebar()" id="sidebar-toggle">☰</button>
        `;
        
        // Add CSS for hover effects
        const style = document.createElement('style');
        style.textContent = `
            #selenium-sidebar a:hover {
                background: rgba(255,255,255,0.1) !important;
                border-left-color: #4299e1 !important;
            }
            #sidebar-toggle:hover {
                background: #3182ce !important;
                transform: scale(1.05);
            }
        `;
        document.head.appendChild(style);
        
        // Add sidebar to page
        document.body.appendChild(sidebar);
        
        // Toggle function
        window.toggleSidebar = function() {
            const panel = document.getElementById('sidebar-panel');
            const toggle = document.getElementById('sidebar-toggle');
            const isOpen = panel.style.left === '0px';
            
            if (isOpen) {
                panel.style.left = '-280px';
                toggle.textContent = '☰';
                toggle.style.left = '20px';
            } else {
                panel.style.left = '0px';
                toggle.textContent = '✖';
                toggle.style.left = '300px';
            }
        };
        
        // Handle navigation clicks
        document.querySelectorAll('#selenium-sidebar a').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                window.location.href = this.href;
            });
        });
        
        console.log('✅ Selenium sidebar injected successfully!');
        """
        
        try:
            self.driver.execute_script(sidebar_script)
        except Exception as e:
            print(f"⚠️ Could not inject sidebar: {e}")
    
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
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Inject sidebar overlay
            self._inject_sidebar_overlay()
            
            print("✅ Browser launched successfully!")
            print("💡 Features:")
            print("   • Click the ☰ button (top-left) to toggle sidebar")
            print("   • All websites work (no iframe restrictions!)")
            print("   • Full JavaScript injection support")
            
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
        """Monitor browser and handle cleanup when closed. This blocks until browser closes."""
        try:
            while self.driver:
                # Check if browser is still open
                try:
                    self.driver.current_url
                    time.sleep(1)
                except:
                    # Browser closed
                    break
        except:
            pass
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
                
                # Wait for load and re-inject sidebar
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                self._inject_sidebar_overlay()
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
            while self.tracking_active and self.driver:
                try:
                    gaze = self.eye_tracker.get_gaze()
                    if gaze and gaze['position']:
                        x, y = gaze['position']
                        fixating = gaze.get('fixation', False)
                        
                        script = f"if(window.gazeOverlay) window.gazeOverlay.update({x}, {y}, {str(fixating).lower()});"
                        self.inject_javascript(script)
                        
                    time.sleep(0.033)  # ~30 FPS
                except Exception as e:
                    print(f"⚠️ Gaze tracking error: {e}")
                    time.sleep(0.1)
        
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
        
        print("👋 Browser closed")
    
    def get_webview_window(self):
        """Get the current driver (compatibility method)."""
        return self.driver