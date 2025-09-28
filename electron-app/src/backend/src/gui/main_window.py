"""
Main GUI application for the Simple Browser Launcher.

This module contains the main application class that coordinates
all the different components (GUI, timer, browser, eye tracking).
"""

import tkinter as tk
from tkinter import ttk, messagebox

from ..timer import BrowserTimer
from ..browser import BrowserManager
from ..eye_tracking import EyeTracker


class SimpleBrowserLauncher:
    """A GUI application for launching a simple web browser with timer and eye tracking."""
    
    def __init__(self):
        """Initialize the browser launcher GUI."""
        self.root = tk.Tk()
        self.root.title("Simple Browser Launcher")
        
        # Initialize component managers
        self.timer_manager = BrowserTimer()
        self.browser_manager = BrowserManager()
        self.eye_tracker = EyeTracker()
        
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

        # Time limit input section
        time_frame = ttk.Frame(main_frame)
        time_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(time_frame, text="Time Limit (minutes):").pack(side='left')
        self.time_entry = ttk.Entry(time_frame, width=10)
        self.time_entry.pack(side='left', padx=(5, 10))
        self.time_entry.insert(0, "2")  # Default 2 minutes
        ttk.Label(time_frame, text="(0 = no limit)", foreground='gray').pack(side='left')

        # Eye tracking option section
        tracking_frame = ttk.Frame(main_frame)
        tracking_frame.pack(fill='x', pady=(0, 10))
        self.eye_tracking_var = tk.BooleanVar(value=True)
        eye_tracking_check = ttk.Checkbutton(
            tracking_frame,
            text="Enable Eye Tracking (experimental)",
            variable=self.eye_tracking_var
        )
        eye_tracking_check.pack(side='left')

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
        time_limit_str = self.time_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
            
        # Validate time limit
        try:
            time_limit = float(time_limit_str) if time_limit_str else 0
            if time_limit < 0:
                messagebox.showerror("Error", "Time limit cannot be negative")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for time limit")
            return

        # Update status with configuration info
        config_info = []
        if time_limit > 0:
            config_info.append(f"Time limit: {time_limit} min")
        else:
            config_info.append("No time limit")
            
        if self.eye_tracking_var.get():
            config_info.append("Eye tracking enabled")
            
        self.status_var.set(f"Launching: {url} ({', '.join(config_info)})")
        self.launch_btn.config(state='disabled')
        
        try:
            # Start eye tracking if enabled
            if self.eye_tracking_var.get():
                self.eye_tracker.start_tracking()
            
            # Start timer if time limit is set (start it in a separate thread to not block)
            if time_limit > 0:
                # Start timer - it will wait for browser initialization
                self.timer_manager.start_timer(time_limit, None)
            else:
                print("Time limit set to 0 - Browser session is unlimited")
            
            # Launch browser (this will block until browser closes)
            success, result = self.browser_manager.launch_browser(url, self.root)
            
            # The browser launch is complete at this point (either closed by user or timer)
            
            # Stop eye tracking when browser closes
            if self.eye_tracking_var.get():
                tracking_summary = self.eye_tracker.stop_tracking()
                if tracking_summary:
                    print(f"Eye tracking summary: {tracking_summary}")
            
            # Stop timer when browser closes
            self.timer_manager.stop_timer()
            print("Browser session ended.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch browser: {e}")
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