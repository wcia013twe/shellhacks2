"""
Integration bridge between the new UI system and existing browser functionality.

This module provides integration between the comprehensive test UI manager
and the existing browser/timer functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from timer import BrowserTimer
from browser import BrowserManager


class IntegratedTestManager:
    """Integration class that bridges new UI with existing browser functionality."""
    
    def __init__(self, test_data):
        """Initialize with test configuration data."""
        self.test_data = test_data
        self.timer_manager = BrowserTimer()
        self.browser_manager = BrowserManager()
        
    def start_test_with_browser(self, completion_callback=None):
        """Start the test using existing browser and timer functionality."""
        try:
            # Extract test parameters
            url = self.test_data.get('url', 'https://google.com')
            duration_str = self.test_data.get('duration', '2')
            
            # Parse duration (handle formats like "2min", "2 minutes", "2")
            try:
                if 'min' in duration_str.lower():
                    duration = float(duration_str.lower().replace('min', '').replace('utes', '').strip())
                else:
                    duration = float(duration_str)
            except:
                duration = 2.0  # Default fallback
            
            print(f"🚀 Starting test: {self.test_data.get('usershown', 'Test')}")
            print(f"🌐 URL: {url}")
            print(f"⏱️ Duration: {duration} minutes")
            
            def start_timer_when_ready():
                """Callback executed when browser is ready."""
                if duration > 0:
                    print(f"🕐 Starting {duration} minute timer...")
                    self.timer_manager.start_timer(duration, completion_callback)
                else:
                    print("✅ Browser ready! No time limit set.")
            
            def browser_thread():
                """Run browser in separate thread."""
                try:
                    success, result = self.browser_manager.launch_browser(
                        url, 
                        main_window=None,  # No main window to hide
                        on_ready_callback=start_timer_when_ready
                    )
                    
                    if success:
                        print("✅ Test completed successfully")
                    else:
                        print(f"❌ Test failed: {result}")
                    
                    # Stop timer when browser closes
                    self.timer_manager.stop_timer()
                    
                    # Call completion callback if provided
                    if completion_callback:
                        completion_callback()
                        
                except Exception as e:
                    print(f"Browser thread error: {e}")
                    if completion_callback:
                        completion_callback()
            
            # Start browser in separate thread
            browser_thread_obj = threading.Thread(target=browser_thread, daemon=True)
            browser_thread_obj.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to start test: {e}")
            return False


class ModifiedMainWindow:
    """Modified version of the original main window that can be called from the new UI."""
    
    def __init__(self, test_data=None):
        """Initialize with optional test data."""
        self.root = tk.Tk()
        self.root.title("Eye Tracking Test Runner")
        self.root.geometry("600x400")
        
        # Initialize component managers
        self.timer_manager = BrowserTimer()
        self.browser_manager = BrowserManager()
        
        # Store test data if provided
        self.test_data = test_data or {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Eye Tracking Test Runner",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        if self.test_data:
            # Show test information if data provided
            info_frame = ttk.LabelFrame(main_frame, text="Test Configuration", padding=15)
            info_frame.pack(fill='x', pady=(0, 20))
            
            info_text = f"""Test Name: {self.test_data.get('usershown', 'N/A')}
URL: {self.test_data.get('url', 'N/A')}
Duration: {self.test_data.get('duration', 'N/A')}
Description: {self.test_data.get('description', 'N/A')[:100]}..."""
            
            ttk.Label(info_frame, text=info_text, justify='left').pack()
            
            # Quick start button for configured test
            start_configured_btn = ttk.Button(
                main_frame,
                text="🚀 Start Configured Test",
                command=self.start_configured_test
            )
            start_configured_btn.pack(pady=10)
            
            ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=20)
        
        # Original functionality
        # URL input section
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(url_frame, text="Enter URL:").pack(side='left')
        self.url_entry = ttk.Entry(url_frame, width=40)
        self.url_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        self.url_entry.insert(0, self.test_data.get('url', 'https://google.com'))
        
        # Time limit input section
        time_frame = ttk.Frame(main_frame)
        time_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(time_frame, text="Time Limit (minutes):").pack(side='left')
        self.time_entry = ttk.Entry(time_frame, width=10)
        self.time_entry.pack(side='left', padx=(5, 10))
        
        # Set default time from test data or use 2
        default_duration = self.test_data.get('duration', '2')
        if 'min' in str(default_duration).lower():
            default_duration = str(default_duration).lower().replace('min', '').replace('utes', '').strip()
        self.time_entry.insert(0, default_duration)
        
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
        self.launch_btn.pack(pady=20)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready - Configure test and click Open Browser")
        self.status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            foreground='gray'
        )
        self.status_label.pack(pady=(5, 0))
        
        # Bind Enter key to launch browser
        self.url_entry.bind('<Return>', lambda e: self.launch_browser())
    
    def start_configured_test(self):
        """Start the test with the configured data."""
        if not self.test_data:
            messagebox.showerror("Error", "No test configuration available")
            return
        
        # Create integrated test manager and start test
        test_manager = IntegratedTestManager(self.test_data)
        
        def on_test_complete():
            """Called when test completes."""
            self.status_var.set("Test completed successfully!")
            messagebox.showinfo("Test Complete", "Eye tracking test has finished!")
        
        self.status_var.set("Starting configured test...")
        success = test_manager.start_test_with_browser(completion_callback=on_test_complete)
        
        if not success:
            self.status_var.set("Failed to start test")
            messagebox.showerror("Error", "Failed to start the configured test")
    
    def launch_browser(self):
        """Launch the browser with manual configuration."""
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
        
        self.status_var.set("🚀 Starting Chrome browser...")
        self.launch_btn.config(state='disabled', text="Loading...")
        
        try:
            # Prepare timer callback to start only when browser is ready
            def start_timer_when_ready():
                if time_limit > 0:
                    print(f"🕐 Starting {time_limit} minute timer...")
                    self.timer_manager.start_timer(time_limit, None)
                    self.status_var.set(f"Browser ready! Timer: {time_limit} min")
                else:
                    print("✅ Browser ready! No time limit set.")
                    self.status_var.set("Browser ready! No time limit")
            
            # Launch browser in separate thread so UI doesn't freeze
            def browser_thread():
                try:
                    success, result = self.browser_manager.launch_browser(
                        url, 
                        self.root, 
                        start_timer_when_ready
                    )
                    
                    # Stop timer when browser closes
                    self.timer_manager.stop_timer()
                    print("Browser session ended.")
                    self.status_var.set("Browser session ended")
                    
                except Exception as e:
                    print(f"Browser thread error: {e}")
                finally:
                    # Re-enable the button
                    self.launch_btn.config(state='normal', text="Open Browser")
                    if not self.status_var.get().startswith("Browser session ended"):
                        self.status_var.set("Ready - Configure test and click Open Browser")
            
            # Start browser in separate thread
            if time_limit > 0:
                self.status_var.set("Loading browser... Timer will start when ready")
            else:
                self.status_var.set("Loading browser...")
            
            browser_thread_obj = threading.Thread(target=browser_thread, daemon=True)
            browser_thread_obj.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch browser: {e}")
            self.status_var.set("Error launching browser")
            self.launch_btn.config(state='normal', text="Open Browser")
    
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


# Example of how to integrate with the new UI system
def launch_integrated_test(test_data):
    """Launch the integrated test runner with specific test data."""
    app = ModifiedMainWindow(test_data)
    app.run()


if __name__ == "__main__":
    # Test with sample data
    sample_test_data = {
        'filename': 'sample_test',
        'usershown': 'Sample YouTube Test',
        'url': 'https://www.youtube.com',
        'duration': '2',
        'description': 'A sample test configuration for demonstration purposes.'
    }
    
    app = ModifiedMainWindow(sample_test_data)
    app.run()