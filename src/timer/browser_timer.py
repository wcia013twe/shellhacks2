"""
Timer module for browser session management.

This module handles timing functionality for the browser launcher,
including countdown timers and automatic browser closure.
"""

import threading
import time
try:
    import webview
except ImportError:
    webview = None


class BrowserTimer:
    """Manages timing and automatic closure for browser sessions."""
    
    def __init__(self):
        """Initialize the browser timer."""
        self.timer_thread = None
        self.timer_active = False
        self.webview_window = None
    
    def start_timer(self, time_limit_minutes, webview_window=None):
        """Start a timer to close the browser after the specified time limit."""
        self.timer_active = True
        self.webview_window = webview_window
        
        def timer_function():
            time_limit_seconds = int(time_limit_minutes * 60)
            
            print(f"Browser timer started: {time_limit_minutes} minutes ({time_limit_seconds} seconds)")
            
            # Wait a few seconds for the browser window to fully initialize
            initialization_delay = 3
            for i in range(initialization_delay):
                if not self.timer_active:
                    print("Timer stopped during initialization.")
                    return
                time.sleep(1)
            
            for remaining in range(time_limit_seconds - initialization_delay, 0, -1):
                # Check if timer should stop
                if not self.timer_active:
                    print("Timer stopped.")
                    return
                
                # Only check for window closure after initialization period
                # and only if we're more than 5 seconds into the countdown
                if remaining < time_limit_seconds - initialization_delay - 5:
                    try:
                        # Check if webview windows are still active
                        if (hasattr(webview, '_windows') and 
                            webview._windows is not None and 
                            len(webview._windows) == 0):
                            print("Browser window closed by user. Timer stopped.")
                            self.timer_active = False
                            return
                    except:
                        # If we can't reliably check, continue counting
                        pass
                
                minutes = remaining // 60
                seconds = remaining % 60
                print(f"Time remaining: {minutes:02d}:{seconds:02d}")
                time.sleep(1)
            
            if self.timer_active:
                print("Time limit reached! Closing browser...")
                self.close_browser()
                self.timer_active = False
        
        self.timer_thread = threading.Thread(target=timer_function, daemon=True)
        self.timer_thread.start()
    
    def close_browser(self):
        """Close the browser window using multiple methods."""
        try:
            print("Attempting to close browser window...")
            
            # Method 1: The correct pywebview approach - destroy individual windows
            windows_closed = False
            
            # First, let's see what webview attributes are available
            print(f"Webview available attributes: {[attr for attr in dir(webview) if not attr.startswith('_')]}")
            
            if hasattr(webview, 'windows') and webview.windows:
                print(f"Found {len(webview.windows)} windows in webview.windows")
                for window in webview.windows:
                    try:
                        print(f"Attempting to destroy window: {window}")
                        window.destroy()
                        print(f"Window destroyed successfully")
                        windows_closed = True
                    except Exception as e:
                        print(f"Error destroying window: {e}")
            
            # Method 2: Try the _windows attribute if windows doesn't exist
            elif hasattr(webview, '_windows') and webview._windows:
                print(f"Found {len(webview._windows)} windows in webview._windows")
                windows_to_close = list(webview._windows)  # Create a copy
                for window in windows_to_close:
                    try:
                        print(f"Attempting to destroy window: {window}")
                        window.destroy()
                        print(f"Window destroyed successfully")
                        windows_closed = True
                    except Exception as e:
                        print(f"Error destroying window: {e}")
            
            # Method 3: Use stored window reference if available
            if self.webview_window and not windows_closed:
                try:
                    print("Trying stored window reference")
                    self.webview_window.destroy()
                    print("Stored window destroyed successfully")
                    windows_closed = True
                except Exception as e:
                    print(f"Error with stored window reference: {e}")
            
            # Method 4: JavaScript approach to close from within
            if not windows_closed:
                try:
                    print("Attempting JavaScript window.close()")
                    # Try to evaluate JavaScript to close the window
                    if hasattr(webview, 'evaluate_js') and webview.windows:
                        for window in webview.windows:
                            try:
                                window.evaluate_js('window.close();')
                                print("JavaScript window.close() executed")
                                windows_closed = True
                                break
                            except:
                                pass
                except Exception as e:
                    print(f"Error with JavaScript close: {e}")
            
            # Method 5: Try to quit the webview application
            if not windows_closed:
                try:
                    print("Attempting webview application quit")
                    if hasattr(webview, 'config') and hasattr(webview.config, 'gui'):
                        if hasattr(webview.config.gui, 'destroy'):
                            webview.config.gui.destroy()
                            windows_closed = True
                            print("GUI destroyed via config")
                except Exception as e:
                    print(f"Error with GUI destroy: {e}")
            
            # Method 6: Final fallback message
            if not windows_closed:
                print("⚠️  NOTICE: Automatic browser close failed")
                print("   The browser window is still open - please close it manually")
                print("   This is a limitation of the current pywebview version")
            else:
                print("✅ Browser window closed successfully")
            
            print("Browser close sequence completed")
                
        except Exception as e:
            print(f"Error in close_browser method: {e}")
    
    def stop_timer(self):
        """Stop the active timer."""
        if self.timer_active:
            self.timer_active = False
            print("Timer manually stopped.")
    
    def is_active(self):
        """Check if timer is currently active."""
        return self.timer_active