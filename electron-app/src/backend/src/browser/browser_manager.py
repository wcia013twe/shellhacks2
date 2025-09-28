"""
Browser management module.

This module handles browser window creation, launching, and management
using the pywebview library.
"""

try:
    import webview
except ImportError:
    webview = None
from tkinter import messagebox


class BrowserManager:
    """Manages browser window creation and launching."""
    
    def __init__(self):
        """Initialize the browser manager."""
        self.webview_window = None
    
    def is_webview_available(self):
        """Check if pywebview is available."""
        return webview is not None
    
    def validate_url(self, url):
        """Validate and normalize the URL."""
        if not url:
            return None, "Please enter a URL"
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        return url, None
    
    def launch_browser(self, url, main_window=None):
        """
        Launch browser with the specified URL.
        
        Args:
            url: URL to open
            main_window: Main tkinter window to hide during browser session
            
        Returns:
            tuple: (success: bool, webview_window or error_message)
        """
        if not self.is_webview_available():
            error_msg = "PyWebView is not installed.\\nInstall it with: pip install pywebview"
            if main_window:
                messagebox.showerror("Error", error_msg)
            return False, error_msg
        
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
            
            # Create browser window
            self.webview_window = webview.create_window(
                'Browser', 
                validated_url, 
                width=1024, 
                height=768, 
                fullscreen=False, 
                maximized=True
            )
            
            # Start browser (this blocks until browser closes)
            webview.start()
            
            # Show main window again if provided
            if main_window:
                main_window.deiconify()
            
            return True, self.webview_window
            
        except Exception as e:
            error_msg = f"Failed to launch browser: {e}"
            if main_window:
                messagebox.showerror("Error", error_msg)
            return False, error_msg
    
    def get_webview_window(self):
        """Get the current webview window."""
        return self.webview_window