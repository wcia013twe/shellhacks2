"""
GUI module for the Simple Browser Launcher application.

This module contains the SimpleBrowserLauncher class which provides
a tkinter-based graphical user interface for launching web browsers.
"""

import tkinter as tk
from tkinter import ttk, messagebox
try:
    import webview
except ImportError:
    webview = None


class SimpleBrowserLauncher:
    """A GUI application for launching a simple web browser."""
    
    def __init__(self):
        """Initialize the browser launcher GUI."""
        self.root = tk.Tk()
        self.root.title("Simple Browser Launcher")
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface components."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill='both')

        # URL input section
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(url_frame, text="Enter URL:").pack(side='left')
        self.url_entry = ttk.Entry(url_frame, width=40)
        self.url_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        self.url_entry.insert(0, "https://google.com")

        # Quick links section
        quick_links_frame = ttk.Frame(main_frame)
        quick_links_frame.pack(fill='x', pady=(0, 10))
        quick_links = [
            ("YouTube", "https://www.youtube.com"),
            ("Wikipedia", "https://en.wikipedia.org/wiki/Main_Page"),
            ("GitHub", "https://github.com"),
        ]
        for name, url in quick_links:
            btn = ttk.Button(
                quick_links_frame,
                text=name,
                command=lambda u=url: self.load_quick_link(u)
            )
            btn.pack(side='left', padx=2)

        # Launch button
        self.launch_btn = ttk.Button(
            main_frame,
            text="Open Browser",
            command=self.launch_browser
        )
        self.launch_btn.pack(pady=10)

        # Status label
        self.status_var = tk.StringVar(value="Ready - Enter a URL and click Open Browser")
        self.status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            foreground='gray'
        )
        self.status_label.pack(pady=(5, 0))

        # Bind Enter key to launch browser
        self.url_entry.bind('<Return>', lambda e: self.launch_browser())

    def launch_browser(self):
        """Launch the browser with the entered URL."""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        if webview is None:
            messagebox.showerror(
                "Error", 
                "PyWebView is not installed.\nInstall it with: pip install pywebview"
            )
            return

        self.status_var.set(f"Launching: {url}")
        self.launch_btn.config(state='disabled')
        
        try:
            self.root.withdraw()
            # Open browser window maximized (not fullscreen)
            webview.create_window(
                'Browser', 
                url, 
                width=1024, 
                height=768, 
                fullscreen=False, 
                maximized=True
            )
            webview.start()
            self.root.deiconify()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch browser:\n{e}")
            self.status_var.set("Error launching browser")
        finally:
            self.launch_btn.config(state='normal')
            self.status_var.set("Ready - Enter a URL and click Open Browser")

    def load_quick_link(self, url):
        """Load a quick link URL into the entry field and launch browser."""
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        self.launch_browser()

    def run(self):
        """Start the GUI application."""
        self.url_entry.focus_set()
        self.url_entry.select_range(0, 'end')
        self.root.mainloop()