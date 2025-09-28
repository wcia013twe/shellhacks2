"""
GUI module for the Simple Browser Launcher application.

This module contains the SimpleBrowserLauncher class which provides
a tkinter-based graphical user interface for launching web browsers.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import webbrowser
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
        self.timer_thread = None
        self.timer_active = False
        self.webview_window = None
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
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        if webview is None:
            messagebox.showerror(
                "Error", 
                "PyWebView is not installed.\nInstall it with: pip install pywebview"
            )
            return

        # Update status with time limit info
        if time_limit > 0:
            self.status_var.set(f"Launching: {url} (Time limit: {time_limit} min)")
        else:
            self.status_var.set(f"Launching: {url} (No time limit)")
            
        self.launch_btn.config(state='disabled')
        
        try:
            self.root.withdraw()
            
            # Start timer if time limit is set
            if time_limit > 0:
                self.start_timer(time_limit)
            else:
                print("Time limit set to 0 - Browser session is unlimited")
            
            # Open browser window maximized (not fullscreen)
            self.webview_window = webview.create_window(
                'Browser', 
                url, 
                width=1024, 
                height=768, 
                fullscreen=False, 
                maximized=True
            )
            webview.start()
            self.root.deiconify()
            
            # Stop timer when browser closes
            self.timer_active = False
            print("Browser session ended.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch browser:\n{e}")
            self.status_var.set("Error launching browser")
        finally:
            self.launch_btn.config(state='normal')
            self.status_var.set("Ready - Enter a URL and click Open Browser")

    def start_timer(self, time_limit_minutes):
        """Start a timer to close the browser after the specified time limit."""
        self.timer_active = True
        
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
                        if hasattr(webview, '_windows') and len(webview._windows) == 0:
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
            
            # Method 1: Use stored window reference
            if self.webview_window:
                try:
                    print("Closing using stored window reference")
                    self.webview_window.destroy()
                    print("Window destroyed successfully")
                except Exception as e:
                    print(f"Error with stored window reference: {e}")
            
            # Method 2: Destroy all windows
            if hasattr(webview, '_windows') and webview._windows:
                print(f"Found {len(webview._windows)} windows to close")
                windows_to_close = list(webview._windows)  # Create a copy
                for window in windows_to_close:
                    try:
                        print(f"Closing window: {window}")
                        window.destroy()
                        print(f"Window {window} closed successfully")
                    except Exception as e:
                        print(f"Error closing individual window: {e}")
            
            # Method 3: Call webview.destroy()
            try:
                print("Calling webview.destroy()")
                webview.destroy()
                print("webview.destroy() completed")
            except Exception as e:
                print(f"Error with webview.destroy(): {e}")
            
            # Method 4: Try alternative termination methods
            try:
                if hasattr(webview, '_terminate'):
                    print("Calling webview._terminate()")
                    webview._terminate()
                elif hasattr(webview, 'stop'):
                    print("Calling webview.stop()")
                    webview.stop()
            except Exception as e:
                print(f"Error with alternative termination: {e}")
                
            print("Browser close sequence completed")
                
        except Exception as e:
            print(f"Error in close_browser method: {e}")

    def stop_timer(self):
        """Stop the active timer."""
        if self.timer_active:
            self.timer_active = False
            print("Timer manually stopped.")

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
    def load_file(self, file_path):
        """Load a local file into the browser."""
    # Check if the file exists
        if not os.path.isfile(file_path):
            messagebox.showerror("Error", f"File not found: {file_path}")
            return

        # Validate file extension (optional, based on your requirements)
        valid_extensions = {'.html', '.htm'}
        if not Path(file_path).suffix.lower() in valid_extensions:
            messagebox.showerror("Error", "Invalid file type. Only HTML files are supported.")
            return

        # Convert the file path to a file:// URL
        try:
            file_url = Path(file_path).absolute().as_uri()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert file path to URL:\n{e}")
            return

        # Check if PyWebView is installed
        if webview is None:
            messagebox.showerror(
                "Error",
                "PyWebView is not installed.\nInstall it with: pip install pywebview"
            )
            return

        self.status_var.set(f"Loading file: {file_path}")
        self.launch_btn.config(state='disabled')

        try:
            # Hide the root window (optional)
            self.root.withdraw()

            # Open the file in the browser window
            self.webview_window = webview.create_window(
                'File Viewer',
                file_url,
                width=1024,
                height=768,
                fullscreen=False,
                maximized=True
            )
            webview.start()
            self.status_var.set(f"File loaded successfully: {file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")
            self.status_var.set("Error loading file")

        finally:
            # Restore the root window and reset the UI
            self.root.deiconify()
            self.launch_btn.config(state='normal')
            self.status_var.set("Ready - Enter a URL or load a file")