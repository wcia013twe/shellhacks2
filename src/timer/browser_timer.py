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

from ..report import ReportManager
from ..overlay import OverlayInjector


class BrowserTimer:
    """Manages timing and automatic closure for browser sessions."""
    
    def __init__(self):
        """Initialize the browser timer."""
        self.timer_thread = None
        self.timer_active = False
        self.webview_window = None
        self.report_manager = ReportManager()
        self.overlay_injector = OverlayInjector()
    
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
                print("⏰ Time limit reached!")
                
                # Set webview window for overlay injection
                self.overlay_injector.set_webview_window(self.webview_window)
                
                # Inject component overlays into the browser
                self.overlay_injector.inject_component_overlays()
                
                # Show the analysis report
                self.report_manager.show_component_analysis_report()
                
                print("   Browser will remain open - close it manually when finished")
                self.timer_active = False
        
        self.timer_thread = threading.Thread(target=timer_function, daemon=True)
        self.timer_thread.start()
    
    def close_browser(self):
        """Browser closing is now handled manually by the user."""
        print("Note: Timer no longer closes browser automatically")
        print("      Please close the browser manually when finished")
    
    def stop_timer(self):
        """Stop the active timer."""
        if self.timer_active:
            self.timer_active = False
            print("Timer manually stopped.")
    
    def is_active(self):
        """Check if timer is currently active."""
        return self.timer_active