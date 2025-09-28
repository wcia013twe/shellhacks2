"""
Comprehensive UI Manager for Test Application

This module contains all UI screens for the test management system:
- Title Screen (main menu)
- Setup Test Screen (create new tests)
- Load Test Screen (load existing tests)
- User Start Test Screen (user-friendly test launcher)
- Post Test Screen (after test completion)
- Process Reports Screen (placeholder)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import platform


class TestUIManager:
    """Main UI Manager handling all application screens."""
    
    def __init__(self):
        """Initialize the test UI manager."""
        self.root = tk.Tk()
        self.root.title("Eye Tracking Test Manager")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Current test data (will be populated from forms)
        self.current_test_data = {}
        
        # Initialize shared eye tracker instance (will be created when needed)
        self.eye_tracker = None
        
        # Setup trackpad gesture support
        self.setup_trackpad_gestures()
        
        # Initialize with title screen
        self.show_title_screen()
    
    def clear_window(self):
        """Clear all widgets from the window."""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_header(self, title, subtitle=""):
        """Create a consistent header for all screens."""
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        title_label = ttk.Label(header_frame, text=title, font=('Arial', 18, 'bold'))
        title_label.pack()
        
        if subtitle:
            subtitle_label = ttk.Label(header_frame, text=subtitle, font=('Arial', 10), foreground='gray')
            subtitle_label.pack()
        
        # Add separator
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x', padx=20, pady=(10, 20))
        
        return header_frame
    
    def create_placeholder_image(self, parent, width=200, height=150):
        """Create a placeholder image area."""
        placeholder_frame = ttk.Frame(parent, relief='solid', borderwidth=1)
        placeholder_frame.configure(width=width, height=height)
        placeholder_frame.pack_propagate(False)
        
        placeholder_label = ttk.Label(
            placeholder_frame,
            text="📷\nImage Placeholder\n(Future Feature)",
            justify='center',
            font=('Arial', 10),
            foreground='gray'
        )
        placeholder_label.pack(expand=True)
        
        return placeholder_frame
    
    def setup_trackpad_gestures(self):
        """Setup trackpad gesture support for the window."""
        # Bind mouse wheel events (includes trackpad two-finger scroll)
        self.root.bind("<MouseWheel>", self.handle_trackpad_scroll)
        self.root.bind("<Shift-MouseWheel>", self.handle_trackpad_horizontal_scroll)
        
        # For Linux systems
        self.root.bind("<Button-4>", self.handle_trackpad_scroll)
        self.root.bind("<Button-5>", self.handle_trackpad_scroll)
        self.root.bind("<Shift-Button-4>", self.handle_trackpad_horizontal_scroll)
        self.root.bind("<Shift-Button-5>", self.handle_trackpad_horizontal_scroll)
        
        # Trackpad pinch gestures (Control + wheel)
        self.root.bind("<Control-MouseWheel>", self.handle_trackpad_zoom)
        
        # Two-finger tap gesture (right-click equivalent)
        self.root.bind("<Button-3>", self.handle_two_finger_tap)
        
        # Make window focusable for gesture events
        self.root.focus_set()
        
        print("✅ Trackpad gesture support enabled:")
        print("   • Two-finger scroll: Navigate content")
        print("   • Shift + two-finger scroll: Horizontal scroll") 
        print("   • Ctrl + two-finger scroll: Zoom in/out")
        print("   • Two-finger tap: Context menu (right-click)")
    
    def handle_trackpad_scroll(self, event):
        """Handle two-finger vertical scroll gestures."""
        try:
            # Check if we have a scrollable widget in focus
            widget = self.root.focus_get()
            
            # Handle different scroll directions
            if hasattr(event, 'delta'):
                # Windows
                scroll_direction = 1 if event.delta > 0 else -1
            else:
                # Linux/Mac
                scroll_direction = 1 if event.num == 4 else -1
            
            # Find scrollable content
            scrollable_widget = self.find_scrollable_widget(widget)
            
            if scrollable_widget:
                if hasattr(scrollable_widget, 'yview_scroll'):
                    scrollable_widget.yview_scroll(-scroll_direction, "units")
                    return "break"
            
            # If no specific scrollable widget, try to scroll the whole window
            self.scroll_window_content(scroll_direction)
            
        except Exception as e:
            print(f"Scroll gesture error: {e}")
    
    def handle_trackpad_horizontal_scroll(self, event):
        """Handle two-finger horizontal scroll gestures (with Shift)."""
        try:
            widget = self.root.focus_get()
            
            if hasattr(event, 'delta'):
                scroll_direction = 1 if event.delta > 0 else -1
            else:
                scroll_direction = 1 if event.num == 4 else -1
            
            # Find horizontally scrollable content
            scrollable_widget = self.find_scrollable_widget(widget)
            
            if scrollable_widget and hasattr(scrollable_widget, 'xview_scroll'):
                scrollable_widget.xview_scroll(-scroll_direction, "units")
                return "break"
                
        except Exception as e:
            print(f"Horizontal scroll gesture error: {e}")
    
    def handle_trackpad_zoom(self, event):
        """Handle pinch-to-zoom gestures (Ctrl + two-finger scroll)."""
        try:
            if hasattr(event, 'delta'):
                zoom_direction = 1 if event.delta > 0 else -1
            else:
                zoom_direction = 1 if event.num == 4 else -1
            
            # Get current window size
            current_width = self.root.winfo_width()
            current_height = self.root.winfo_height()
            
            # Calculate new size (zoom in/out by 10%)
            zoom_factor = 1.1 if zoom_direction > 0 else 0.9
            new_width = int(current_width * zoom_factor)
            new_height = int(current_height * zoom_factor)
            
            # Set reasonable bounds
            min_width, min_height = 600, 400
            max_width, max_height = 1400, 1000
            
            new_width = max(min_width, min(max_width, new_width))
            new_height = max(min_height, min(max_height, new_height))
            
            # Apply new size
            self.root.geometry(f"{new_width}x{new_height}")
            
            print(f"🔍 Zoom {'in' if zoom_direction > 0 else 'out'}: {new_width}x{new_height}")
            
        except Exception as e:
            print(f"Zoom gesture error: {e}")
    
    def handle_two_finger_tap(self, event):
        """Handle two-finger tap gesture (context menu)."""
        try:
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="📋 Copy Window Info", command=self.copy_window_info)
            context_menu.add_command(label="🔄 Refresh Screen", command=self.refresh_current_screen)
            context_menu.add_separator()
            context_menu.add_command(label="🏠 Go to Main Menu", command=self.show_title_screen)
            context_menu.add_command(label="⚙️ Window Settings", command=self.show_window_settings)
            
            # Show menu at cursor position
            context_menu.post(event.x_root, event.y_root)
            
        except Exception as e:
            print(f"Two-finger tap gesture error: {e}")
    
    def find_scrollable_widget(self, widget):
        """Find the nearest scrollable widget in the widget hierarchy."""
        while widget:
            if hasattr(widget, 'yview_scroll') or hasattr(widget, 'xview_scroll'):
                return widget
            widget = widget.master
        return None
    
    def scroll_window_content(self, direction):
        """Scroll the main window content if possible."""
        try:
            # Try to find any canvas or scrollable frame
            for child in self.root.winfo_children():
                if isinstance(child, tk.Canvas) and hasattr(child, 'yview_scroll'):
                    child.yview_scroll(-direction, "units")
                    break
        except Exception as e:
            print(f"Window scroll error: {e}")
    
    def copy_window_info(self):
        """Copy current window information to clipboard."""
        try:
            info = f"Eye Tracking Test Manager\nSize: {self.root.winfo_width()}x{self.root.winfo_height()}\nPosition: {self.root.winfo_x()},{self.root.winfo_y()}"
            self.root.clipboard_clear()
            self.root.clipboard_append(info)
            print("📋 Window info copied to clipboard")
        except:
            print("❌ Could not copy to clipboard")
    
    def refresh_current_screen(self):
        """Refresh the current screen."""
        print("🔄 Refreshing current screen...")
        # This would call the current screen's refresh method
        # For now, just update the display
        self.root.update()
    
    def show_window_settings(self):
        """Show window settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Window Settings")
        settings_window.geometry("300x200")
        
        ttk.Label(settings_window, text="Trackpad Gesture Settings", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Gesture status
        status_frame = ttk.Frame(settings_window)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(status_frame, text="✅ Two-finger scroll: Enabled").pack(anchor='w')
        ttk.Label(status_frame, text="✅ Pinch zoom: Enabled").pack(anchor='w') 
        ttk.Label(status_frame, text="✅ Two-finger tap: Enabled").pack(anchor='w')
        
        # Current window info
        info_frame = ttk.LabelFrame(settings_window, text="Current Window", padding=10)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(info_frame, text=f"Size: {self.root.winfo_width()}x{self.root.winfo_height()}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Platform: {platform.system()}").pack(anchor='w')
        
        ttk.Button(settings_window, text="Close", command=settings_window.destroy).pack(pady=10)
    
    def canvas_trackpad_scroll(self, canvas, event):
        """Handle trackpad scrolling specifically for canvas widgets."""
        try:
            if hasattr(event, 'delta'):
                # Windows
                scroll_amount = -1 if event.delta > 0 else 1
            else:
                # Linux/Mac
                scroll_amount = -1 if event.num == 4 else 1
            
            # Scroll the canvas
            canvas.yview_scroll(scroll_amount, "units")
            return "break"  # Prevent event propagation
            
        except Exception as e:
            print(f"Canvas scroll error: {e}")
    
    # ==================== TITLE SCREEN ====================
    def show_title_screen(self):
        """Display the main title screen with three main buttons."""
        self.clear_window()
        self.create_header("Eye Tracking Test Manager")
        
        # Main content frame
        content_frame = ttk.Frame(self.root)
        content_frame.pack(expand=True, fill='both', padx=20)
        
        # Placeholder image at top
        image_frame = ttk.Frame(content_frame)
        image_frame.pack(pady=20)
        self.create_placeholder_image(image_frame, 300, 200)
        
        # Button container
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(expand=True, pady=40)
        
        # Main action buttons
        setup_btn = ttk.Button(
            button_frame,
            text="Setup Test",
            command=self.show_setup_test_screen,
            width=20,
            style='Accent.TButton'
        )
        setup_btn.pack(pady=10)
        
        load_btn = ttk.Button(
            button_frame,
            text="Load Test",
            command=self.show_load_test_screen,
            width=20
        )
        load_btn.pack(pady=10)
        
        reports_btn = ttk.Button(
            button_frame,
            text="Process Reports",
            command=self.show_process_reports_screen,
            width=20
        )
        reports_btn.pack(pady=10)
        
        # No status bar needed
    
    # ==================== SETUP TEST SCREEN ====================
    def show_setup_test_screen(self):
        """Display the setup test configuration screen."""
        self.clear_window()
        self.create_header("Setup New Test", "Configure test parameters and settings")
        
        # Main content with scrollbar and trackpad support
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable trackpad scrolling on canvas
        canvas.bind("<MouseWheel>", lambda e: self.canvas_trackpad_scroll(canvas, e))
        canvas.bind("<Button-4>", lambda e: self.canvas_trackpad_scroll(canvas, e))
        canvas.bind("<Button-5>", lambda e: self.canvas_trackpad_scroll(canvas, e))
        
        # Make canvas focusable for gestures
        canvas.focus_set()
        
        # Form container (expanded to use more window width)
        form_frame = ttk.Frame(scrollable_frame)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # No start setup button needed - form is ready to use
        
        # Form fields
        self.setup_entries = {}
        
        # Filename
        self.create_form_field(form_frame, "Filename:", "filename", "youtube_2min_test")
        
        # URL
        self.create_form_field(form_frame, "URL:", "url", "https://www.youtube.com")
        
        # Duration (minutes only)
        duration_frame = ttk.Frame(form_frame)
        duration_frame.pack(fill='x', pady=8)
        
        ttk.Label(duration_frame, text="Duration (minutes only):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 3))
        
        self.setup_entries['duration'] = ttk.Entry(duration_frame, font=('Arial', 11))
        self.setup_entries['duration'].pack(fill='x', pady=2, ipady=4)
        self.setup_entries['duration'].insert(0, "2")
        self.setup_entries['duration'].configure(foreground='gray')
        
        # Bind validation to duration entry
        self.setup_entries['duration'].bind('<KeyPress>', self.validate_duration_input)
        self.setup_entries['duration'].bind('<FocusIn>', lambda e: self.on_duration_focus_in())
        self.setup_entries['duration'].bind('<FocusOut>', lambda e: self.on_duration_focus_out())
        

        
        # Component Importance Configuration
        component_frame = ttk.Frame(form_frame)
        component_frame.pack(fill='x', pady=20, ipady=5)
        ttk.Label(component_frame, text="Component Configuration:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        # Store component configuration results
        self.component_config_data = None
        
        # Button container for component configuration
        btn_container = ttk.Frame(component_frame)
        btn_container.pack(fill='x', pady=5)
        
        self.config_btn = ttk.Button(
            btn_container,
            text="Configure Component Importance",
            command=self.launch_component_config_browser
        )
        self.config_btn.pack(side='left')
        

        
        # Status label for component configuration
        self.component_status_var = tk.StringVar(value="No component configuration set")
        component_status_label = ttk.Label(
            component_frame, 
            textvariable=self.component_status_var, 
            foreground='gray',
            font=('Arial', 9)
        )
        component_status_label.pack(pady=(5, 0))
        
        # Destination Profile Path
        dest_frame = ttk.Frame(form_frame)
        dest_frame.pack(fill='x', pady=10)
        ttk.Label(dest_frame, text="Destination of Profile:").pack(anchor='w')
        
        path_frame = ttk.Frame(dest_frame)
        path_frame.pack(fill='x', pady=5)
        
        self.dest_path_var = tk.StringVar(value="No path selected")
        self.dest_path_label = ttk.Label(path_frame, textvariable=self.dest_path_var, foreground='gray')
        self.dest_path_label.pack(side='left', fill='x', expand=True)
        
        browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_destination)
        browse_btn.pack(side='right', padx=(10, 0))
        
        # Save and navigation buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill='x', pady=30)
        
        save_btn = ttk.Button(button_frame, text="Save Test Configuration", command=self.save_test_config)
        save_btn.pack(side='left')
        
        back_btn = ttk.Button(button_frame, text="Back to Main Menu", command=self.confirm_back_to_main)
        back_btn.pack(side='right')
        
        # Pack scrollable content
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
    
    def create_form_field(self, parent, label_text, field_name, placeholder=""):
        """Create a labeled entry field with placeholder."""
        field_frame = ttk.Frame(parent)
        field_frame.pack(fill='x', pady=8)
        
        ttk.Label(field_frame, text=label_text, font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 3))
        
        entry = ttk.Entry(field_frame, font=('Arial', 11))
        entry.pack(fill='x', pady=2, ipady=4)
        
        if placeholder:
            entry.insert(0, placeholder)
            entry.configure(foreground='gray')
            
            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.configure(foreground='black')
            
            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.configure(foreground='gray')
            
            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
        
        self.setup_entries[field_name] = entry
        return entry
    
    def start_setup_process(self):
        """Handle start setup button click."""
        messagebox.showinfo("Setup Started", "Test setup process initiated!")
    
    def launch_component_config_browser(self):
        """Launch browser to configure component importance using the element ranking script."""
        # Get URL from form
        url = self.setup_entries['url'].get().strip()
        
        # Check if URL is empty or is placeholder
        if not url or url == "https://www.youtube.com" or url.startswith("https://youtube.com") or url.startswith("https://www.youtube.com"):
            # Use placeholder URL for demo
            url_to_use = "https://www.youtube.com"
        elif url in ["", "Enter URL here", "https://"]:
            # URL is empty or invalid
            messagebox.showerror("URL Required", 
                               "Please enter a valid URL before configuring component importance.\n\n" +
                               "The browser needs to open the target website to identify important elements.")
            return
        else:
            url_to_use = url
        
        # Disable button during configuration
        self.config_btn.config(state='disabled', text="Launching Browser...")
        self.component_status_var.set("Opening browser for element configuration...")
        
        # Launch browser with element ranking script
        try:
            # Try multiple import methods to ensure compatibility
            try:
                from ..browser import BrowserManager
            except ImportError:
                try:
                    from src.browser import BrowserManager
                except ImportError:
                    import sys
                    import os
                    browser_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'browser')
                    sys.path.insert(0, browser_path)
                    from browser_manager import BrowserManager
            
            browser_manager = BrowserManager()
            
            # Debug URL thoroughly
            print(f"🔍 Debug - Raw URL from form: '{url}'")
            print(f"🔍 Debug - URL length: {len(url)}")
            print(f"🔍 Debug - URL repr: {repr(url)}")
            print(f"🔍 Debug - Final URL to use: '{url_to_use}'")
            print(f"🔍 Debug - Final URL repr: {repr(url_to_use)}")
            
            # Create a callback to handle the component configuration
            def on_browser_ready():
                print("🌐 Browser ready - injecting element ranking script...")
                self.inject_element_ranking_script(browser_manager)
            
            def browser_thread():
                try:
                    # Launch browser with callback
                    success, result = browser_manager.launch_browser(
                        url_to_use,
                        main_window=None,  # Don't hide the setup window
                        on_ready_callback=on_browser_ready
                    )
                    
                    if success:
                        print("✅ Component configuration browser closed")
                        
                        # Monitor for ESC key completion signal
                        try:
                            import time
                            timeout = 300  # 5 minutes timeout
                            start_time = time.time()
                            
                            while time.time() - start_time < timeout:
                                try:
                                    # Check if title changed to completion signal
                                    title = browser_manager.driver.title
                                    if title == 'ELEMENT_RANKING_COMPLETE':
                                        print("🎯 ESC detected - closing browser...")
                                        browser_manager.close()
                                        break
                                    time.sleep(0.5)  # Check every 500ms
                                except:
                                    # Browser already closed
                                    break
                        except Exception as monitor_error:
                            print(f"Monitor error: {monitor_error}")
                        
                        # Handle any pending alerts before checking component data
                        try:
                            # Check if there's an alert and dismiss it
                            alert = browser_manager.driver.switch_to.alert
                            alert_text = alert.text
                            print(f"📋 Dismissing completion alert: {alert_text[:50]}...")
                            alert.accept()  # Dismiss the alert
                        except:
                            # No alert present, continue normally
                            pass
                        
                        # Small delay to ensure alert is properly dismissed
                        time.sleep(0.5)
                        
                        # Check if we received component data
                        try:
                            # Try to get component config from browser's window object
                            component_data = browser_manager.inject_javascript("return window.__componentConfig || null;")
                            if component_data:
                                self.temp_component_data = component_data
                                print("🔄 Retrieved component data from browser:", component_data)
                        except Exception as data_error:
                            print(f"⚠️ Could not retrieve component data: {data_error}")
                        
                        if hasattr(self, 'temp_component_data') and self.temp_component_data:
                            self.component_config_data = self.temp_component_data
                            self.component_status_var.set(f"✅ Configuration complete - {len(self.component_config_data.get('ranks', {}))} importance levels set")
                            print("📊 Component configuration data received:", self.component_config_data)
                        else:
                            self.component_status_var.set("⚠️ No configuration data received")
                    else:
                        print(f"❌ Browser launch failed: {result}")
                        self.component_status_var.set("❌ Browser launch failed")
                        
                except Exception as e:
                    print(f"Browser configuration error: {e}")
                    self.component_status_var.set("❌ Configuration failed")
                finally:
                    # Re-enable button
                    self.config_btn.config(state='normal', text="Configure Component Importance")
            
            # Start browser in separate thread
            import threading
            browser_thread_obj = threading.Thread(target=browser_thread, daemon=True)
            browser_thread_obj.start()
            
        except ImportError:
            messagebox.showerror("Error", "Browser manager not available. Component configuration requires browser integration.")
            self.config_btn.config(state='normal', text="Configure Component Importance")
            self.component_status_var.set("❌ Browser not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch browser for component configuration: {e}")
            self.config_btn.config(state='normal', text="Configure Component Importance")
            self.component_status_var.set("❌ Configuration failed")
    
    def inject_element_ranking_script(self, browser_manager):
        """Inject the element ranking JavaScript into the browser."""
        print("🔧 Preparing to inject element ranking script...")
        
        # Wait a moment for page to fully load
        import time
        time.sleep(2)
        
        element_ranking_script = r"""
            // Element Ranking Script for Eye Tracking Component Configuration
            (() => {
            // ===== internal class prefix & helpers =====
            const INTERNAL_PREFIX = "__gaze_";
            const CLASS_PENDING = `${INTERNAL_PREFIX}glowP`;   // blue
            const CLASS_RANKED  = `${INTERNAL_PREFIX}glowG`;   // green

            const isInternalClass = (c) => c && c.startsWith(INTERNAL_PREFIX);
            const hasDigits = (s) => /\d/.test(s);
            const stableClass = (c) => c && c.length <= 32 && !hasDigits(c) && !isInternalClass(c);
            const unique = (sel) => { try { return document.querySelectorAll(sel).length === 1; } catch { return false; } };

            const attrCandidates = (el) => {
                const out = [];
                for (const a of el.attributes || []) {
                const k = a.name;
                if (k.startsWith("data-") || k === "aria-label" || k === "name" || k === "role") {
                    out.push(`[${CSS.escape ? CSS.escape(k) : k}="${a.value}"]`);
                }
                }
                return out;
            };

            // Temporarily remove ALL internal classes from a node, run fn(), then restore
            const withoutInternalClasses = (el, fn) => {
                if (!(el instanceof Element)) return fn();
                const removed = [];
                el.classList.forEach((c) => { if (isInternalClass(c)) { el.classList.remove(c); removed.push(c); } });
                try { return fn(); } finally { removed.forEach((c) => el.classList.add(c)); }
            };

            // Build a unique, robust selector (no html/body; ignore our glow classes)
            const selectorFor = (el) => withoutInternalClasses(el, () => {
                if (!(el instanceof Element)) return null;

                // 1) Unique ID
                if (el.id && unique(`#${CSS.escape ? CSS.escape(el.id) : el.id}`)) {
                return `#${CSS.escape ? CSS.escape(el.id) : el.id}`;
                }

                // 2) Stable attributes
                for (const a of attrCandidates(el)) {
                const sel = `${el.tagName.toLowerCase()}${a}`;
                if (unique(sel)) return sel;
                }

                // 3) Tag + stable classes (<=2)
                const classes = [...(el.classList || [])].filter(stableClass).slice(0, 2);
                if (classes.length) {
                const sel = `${el.tagName.toLowerCase()}` + classes.map(c => `.${CSS.escape ? CSS.escape(c) : c}`).join("");
                if (unique(sel)) return sel;
                }

                // 4) Tag:nth-of-type
                const tag = el.tagName.toLowerCase();
                let sibIndex = 1, sib = el;
                while ((sib = sib.previousElementSibling)) if (sib.tagName === el.tagName) sibIndex++;
                let base = `${tag}:nth-of-type(${sibIndex})`;
                if (unique(base)) return base;

                // 5) Minimal parent chain (stop at body; don’t include it)
                const cleanParentSel = (p) => withoutInternalClasses(p, () => {
                if (p.id && unique(`#${CSS.escape ? CSS.escape(p.id) : p.id}`)) {
                    return `#${CSS.escape ? CSS.escape(p.id) : p.id}`;
                }
                for (const a of attrCandidates(p)) {
                    const s = `${p.tagName.toLowerCase()}${a}`;
                    if (unique(s)) return s;
                }
                const pcs = [...(p.classList || [])].filter(stableClass).slice(0,2);
                if (pcs.length) return p.tagName.toLowerCase() + pcs.map(c=>`.`+(CSS.escape?CSS.escape(c):c)).join("");
                let n=1, x=p; while ((x = x.previousElementSibling)) if (x.tagName===p.tagName) n++;
                return `${p.tagName.toLowerCase()}:nth-of-type(${n})`;
                });

                const chain = [base];
                let p = el.parentElement;
                while (p && p !== document.body) {
                const pSel = cleanParentSel(p);
                const candidate = `${pSel} > ${chain.join(" > ")}`;
                if (unique(candidate)) return candidate;
                chain.unshift(pSel);
                p = p.parentElement;
                }
                return chain.join(" > ");
            });

            // ===== styles =====
            const ensureStyle = () => {
                if (document.getElementById("__gazeSetupMulti")) return;
                const s = document.createElement("style");
                s.id = "__gazeSetupMulti";
                s.textContent = `
                .${CLASS_PENDING}{
                    outline:3px solid #1e90ff!important; outline-offset:2px!important;
                    box-shadow:0 0 10px #1e90ff, 0 0 20px rgba(30,144,255,.6)!important;
                    border-radius:6px!important; transition:box-shadow .15s
                }
                .${CLASS_RANKED}{
                    outline:3px solid #2e7d32!important; outline-offset:2px!important;
                    box-shadow:0 0 10px #2e7d32, 0 0 20px rgba(46,125,50,.5)!important;
                    border-radius:6px!important; transition:box-shadow .15s
                }
                .${INTERNAL_PREFIX}toast{
                    position:fixed; z-index:2147483647; left:50%; top:12px; transform:translateX(-50%);
                    background:rgba(20,22,26,.92); color:#e6f0ff; padding:8px 12px; border-radius:8px;
                    font:13px/1.45 system-ui; box-shadow:0 6px 18px rgba(0,0,0,.35); pointer-events:none
                }
                .${INTERNAL_PREFIX}hud{
                    position:fixed; z-index:2147483647; background:#0b1220; color:#e6f0ff; padding:6px;
                    border-radius:10px; box-shadow:0 10px 30px rgba(0,0,0,.45); display:flex; gap:6px; align-items:center;
                }
                .${INTERNAL_PREFIX}btn{
                    min-width:28px; min-height:28px; border-radius:8px; border:1px solid #2b3652;
                    background:#121b2f; color:#cfe1ff; cursor:pointer; font:600 13px/1 system-ui
                }
                .${INTERNAL_PREFIX}btn:hover{ background:#1a2540 }
                .${INTERNAL_PREFIX}small{ opacity:.8; font:12px/1.2 system-ui; margin-left:6px }
                `;
                document.head.appendChild(s);
            };

            const toast = (msg, ms=1200) => {
                const el = document.createElement("div");
                el.className = `${INTERNAL_PREFIX}toast`; el.textContent = msg;
                document.documentElement.appendChild(el);
                setTimeout(() => el.remove(), ms);
            };

            // ===== state: many-per-rank + toggle removal =====
            if (window.__gazeSetup?.end) window.__gazeSetup.end(true);
            ensureStyle();

            const selectedByEl = new Map();     // Element -> { rank, selector, tag }
            let pendingEl = null;
            let hud = null;

            // glow helpers
            const markPending   = (el) => el && (el.classList.remove(CLASS_RANKED), el.classList.add(CLASS_PENDING));
            const unmarkPending = (el) => el && el.classList.remove(CLASS_PENDING);
            const markRanked    = (el) => el && (el.classList.remove(CLASS_PENDING), el.classList.add(CLASS_RANKED));
            const unmarkRanked  = (el) => el && el.classList.remove(CLASS_RANKED);

            const hideHUD = () => { hud?.remove(); hud = null; };
            const showHUD = (x, y, onPick) => {
                hideHUD();
                hud = document.createElement("div"); hud.className=`${INTERNAL_PREFIX}hud`; hud.tabIndex=-1;
                const mk = (n)=>{ const b=document.createElement("button"); b.className=`${INTERNAL_PREFIX}btn`; b.textContent=n; b.onclick=(e)=>{e.stopPropagation(); onPick(n); hideHUD();}; return b; };
                for(let i=1;i<=5;i++) hud.appendChild(mk(i));
                const tip=document.createElement("span"); tip.className=`${INTERNAL_PREFIX}small`; tip.textContent="1–5 to rank • Esc to finish"; hud.appendChild(tip);
                const pad=8, w=220, h=40, left=Math.min(Math.max(x-w/2,pad), innerWidth-w-pad), top=Math.min(Math.max(y+12,pad), innerHeight-h-pad);
                Object.assign(hud.style,{left:left+"px", top:top+"px", position:"fixed"}); document.documentElement.appendChild(hud); hud.focus({preventScroll:true});
            };

            const clearPending = () => { if (pendingEl) unmarkPending(pendingEl); pendingEl = null; hideHUD(); };

            const removeSelection = (el) => {
                const rec = selectedByEl.get(el);
                if (!rec) return;
                selectedByEl.delete(el);
                unmarkRanked(el);
                toast(`Removed rank ${rec.rank} from <${el.tagName.toLowerCase()}>`);
            };

            const assignRank = (el, rank) => {
                const prev = selectedByEl.get(el);
                if (prev) {
                if (prev.rank === rank) { toast(`Already rank ${rank}`); clearPending(); return; }
                }
                const selector = selectorFor(el);
                selectedByEl.set(el, { rank, selector, tag: el.tagName.toLowerCase() });
                markRanked(el);
                clearPending();
                toast(`Assigned rank ${rank} to <${el.tagName.toLowerCase()}>`);
            };

            const onKeyDown = (e) => {
                if (e.key === "Escape") { e.preventDefault(); end(); return; }
                const num = Number(e.key);
                if (pendingEl && Number.isInteger(num) && num>=1 && num<=5) {
                e.preventDefault(); assignRank(pendingEl, num);
                }
            };

            const onPointerDown = (e) => {
                const inHUD = e.target.closest(`.${INTERNAL_PREFIX}hud`);
                if (!(e.altKey && e.button === 0)) { if (!inHUD) clearPending(); return; }
                e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();

                const el = document.elementFromPoint(e.clientX, e.clientY);
                if (!el) return;

                if (selectedByEl.has(el)) { clearPending(); removeSelection(el); return; }

                clearPending();
                pendingEl = el;
                markPending(el);
                showHUD(e.clientX, e.clientY, (rank)=>assignRank(el, rank));
            };

            const buildProfile = () => {
                const ranks = {};
                for (const [, rec] of selectedByEl.entries()) {
                const k = String(rec.rank);
                (ranks[k] ||= []).push({ selector: rec.selector, tag: rec.tag });
                }
                return {
                version: 1,
                url: location.href,
                origin: location.origin,
                path: location.pathname,
                saved_at: Date.now(),
                ranks
                };
            };

            // Save to a real file (Drive/OneDrive/Dropbox desktop folders work)
            const saveToFile = async (profile, filename = "gaze_profile.json") => {
                const data = JSON.stringify(profile, null, 2);
                if (window.showSaveFilePicker) {
                const handle = await window.showSaveFilePicker({
                    suggestedName: filename,
                    types: [{ description: "JSON", accept: { "application/json": [".json"] } }]
                });
                const w = await handle.createWritable();
                await w.write(data);
                await w.close();
                toast(`Saved ${handle.name}`);
                return handle;
                } else {
                // Fallback: normal download
                const a = document.createElement("a");
                a.download = filename;
                a.href = URL.createObjectURL(new Blob([data], { type: "application/json" }));
                a.click();
                URL.revokeObjectURL(a.href);
                toast("Saved (downloaded)");
                return null;
                }
            };

            const end = async ({ silent = false } = {}) => {
                removeEventListener("pointerdown", onPointerDown, true);
                removeEventListener("keydown", onKeyDown, true);
                clearPending();
                for (const el of Array.from(selectedByEl.keys())) unmarkRanked(el);

                const profile = buildProfile();
                if (!silent) {
                console.log("📁 Setup profile:", profile);
                console.log("JSON:", JSON.stringify(profile, null, 2));
                }
                try { await saveToFile(profile, "gaze_profile.json"); } catch (err) { console.warn("Save cancelled/failed:", err); }
                window.__gazeSetup = undefined;
                return profile;
            };

            addEventListener("pointerdown", onPointerDown, true);
            addEventListener("keydown", onKeyDown, true);

            window.__gazeSetup = {
                end, // async; shows Save dialog; returns profile
                export: () => { const p = buildProfile(); console.log("📤 JSON:", JSON.stringify(p, null, 2)); return p; },
            };

            console.log("🟦 Setup: Alt+Click to add (blue → 1–5 → green), Alt+Click AGAIN to remove. Press Esc to save as gaze_profile.json.");
            })();

        """
        
        try:
            # Inject the script
            print("🚀 Injecting element ranking script...")
            result = browser_manager.inject_javascript(element_ranking_script)
            
            if result is not None:
                print("✅ Element ranking script injected successfully!")
                
                # Verify script was loaded by checking for the global object
                verification = browser_manager.inject_javascript("return typeof window.__gazeSetup;")
                if verification == "object":
                    print("🎯 Element ranking system is active and ready!")
                    self.component_status_var.set("🎯 Alt+Click elements to rank them (1-5), press Escape when done")
                else:
                    print("⚠️ Script injection may have failed - verification failed")
                    self.component_status_var.set("⚠️ Component configuration may not be working properly")
            else:
                print("❌ Script injection returned None")
                self.component_status_var.set("❌ Failed to inject component configuration script")
            
            # Set up a timer to check for results
            self.check_for_component_data(browser_manager)
            
        except Exception as e:
            print(f"❌ Failed to inject element ranking script: {e}")
            self.component_status_var.set(f"❌ Script injection failed: {e}")
    
    def check_for_component_data(self, browser_manager):
        """Periodically check if the browser has component configuration data."""
        def check_data():
            try:
                # Check if the configuration is complete
                result = browser_manager.driver.execute_script("""
                    return window.__componentConfig || null;
                """)
                
                if result:
                    # Configuration data received
                    self.temp_component_data = result
                    print("📊 Received component configuration data:", result)
                    return True
                    
            except Exception as e:
                print(f"Error checking component data: {e}")
                return False
            
            # Schedule next check in 1 second
            self.root.after(1000, check_data)
            return False
        
            # Start checking
        check_data()
    


    def browse_destination(self):
        """Open file browser for destination path selection."""
        folder_path = filedialog.askdirectory(title="Select Destination Folder")
        if folder_path:
            self.dest_path_var.set(folder_path)
    
    def save_test_config(self):
        """Save the test configuration to JSON files."""
        import json
        import os
        from datetime import datetime
        
        # Check if destination path is set
        destination_path = self.dest_path_var.get().strip()
        if not destination_path:
            messagebox.showerror("Error", "Please select a destination folder before saving the configuration.")
            return
        
        # Validate destination path exists
        if not os.path.exists(destination_path):
            messagebox.showerror("Error", f"Destination path does not exist: {destination_path}")
            return
        
        # Collect test configuration data (filename, URL, duration)
        test_config = {}
        for field_name, entry in self.setup_entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showerror("Error", f"Please fill in the {field_name} field.")
                return
            test_config[field_name] = value
        
        # Add metadata
        test_config['created_at'] = datetime.now().isoformat()
        test_config['config_version'] = '1.0'
        
        # Create filename for the test config
        config_filename = test_config.get('filename', 'test_config')
        if not config_filename.endswith('.json'):
            config_filename += '_config.json'
        else:
            config_filename = config_filename.replace('.json', '_config.json')
        
        config_file_path = os.path.join(destination_path, config_filename)
        
        try:
            # Create the final configuration filename (removing _config suffix for cleaner name)
            final_filename = test_config.get('filename', 'test_config')
            if final_filename.endswith('_config'):
                final_filename = final_filename[:-7]  # Remove _config suffix
            if not final_filename.endswith('.json'):
                final_filename += '.json'
            
            final_file_path = os.path.join(destination_path, final_filename)
            
            # Handle component configuration and create single combined file
            component_info = ""
            files_created_list = []
            
            if hasattr(self, 'component_config_data') and self.component_config_data:
                # Create flat configuration structure matching the desired format
                flat_config = {
                    'origin': self.component_config_data.get('origin', ''),
                    'path': self.component_config_data.get('path', '/'),
                    'url': self.component_config_data.get('url', test_config['url']),
                    'duration': test_config['duration'],
                    'created_at': test_config['created_at'],
                    'ranks': self.component_config_data.get('ranks', {})
                }
                
                # Save the flat configuration structure
                with open(final_file_path, 'w', encoding='utf-8') as f:
                    json.dump(flat_config, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Complete test configuration saved to: {final_file_path}")
                files_created_list.append(f"{final_filename} (Complete Test Configuration)")
                
                component_ranks = len(self.component_config_data.get('ranks', {}))
                
            else:
                # Save basic config only if no component data - use flat structure
                basic_config = {
                    'origin': '',
                    'path': '/',
                    'url': test_config['url'],
                    'duration': test_config['duration'],
                    'created_at': test_config['created_at'],
                    'ranks': {}
                }
                
                with open(final_file_path, 'w', encoding='utf-8') as f:
                    json.dump(basic_config, f, indent=2, ensure_ascii=False)
                
                print(f"� Basic test configuration saved to: {final_file_path}")
                files_created_list.append(f"{final_filename} (Basic Configuration)")
                component_info = "\n\nComponent Configuration: ⚠️ Not configured yet\n💡 Configure components for enhanced testing"
            
            # Show success message with the single created file
            files_created = "\n".join([f"• {file_info}" for file_info in files_created_list])
            
            messagebox.showinfo("Configuration Saved Successfully!", 
                              f"Test configuration saved to:\n{destination_path}\n\n"
                              f"File created:\n{files_created}"
                              f"\n\nTest Details:\n• Filename: {test_config.get('filename', 'N/A')}\n• URL: {test_config.get('url', 'N/A')}\n• Duration: {test_config.get('duration', 'N/A')} minutes"
                              f"{component_info}")
            
            # Store for later use
            stored_data = {
                'test_config': test_config,
                'component_config': self.component_config_data if hasattr(self, 'component_config_data') else None,
                'saved_to': destination_path,
                'config_file': final_file_path,
                'files_created': files_created_list,
                'has_combined_config': hasattr(self, 'component_config_data') and self.component_config_data is not None
            }
            
            self.current_test_data = stored_data
            
            print("✅ Test configuration saved successfully!")
            
            # Navigate back to main menu after successful save
            self.show_title_screen()
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save configuration files:\n\n{str(e)}")
            print(f"❌ Save error: {e}")
    
    def validate_duration_input(self, event):
        """Validate that duration input contains only digits."""
        # Allow backspace, delete, tab, escape, enter
        if event.keysym in ('BackSpace', 'Delete', 'Tab', 'Escape', 'Return'):
            return True
        
        # Allow digits only
        if event.char.isdigit():
            return True
        
        # Block all other characters
        return "break"
    
    def on_duration_focus_in(self):
        """Handle focus in for duration entry."""
        entry = self.setup_entries['duration']
        if entry.get() == "2" and entry.cget('foreground') == 'gray':
            entry.delete(0, tk.END)
            entry.configure(foreground='black')
    
    def on_duration_focus_out(self):
        """Handle focus out for duration entry."""
        entry = self.setup_entries['duration']
        if not entry.get():
            entry.insert(0, "2")
            entry.configure(foreground='gray')
    
    def confirm_back_to_main(self):
        """Confirm with user before going back to main menu without saving."""
        result = messagebox.askyesno(
            "Confirm Navigation",
            "Are you sure you want to go back to the main menu?\n\nAny unsaved configuration will be lost.",
            icon='warning'
        )
        if result:
            self.show_title_screen()
    
    # ==================== LOAD TEST SCREEN ====================
    def show_load_test_screen(self):
        """Display the load test screen for selecting existing tests."""
        self.clear_window()
        self.create_header("Load Existing Test", "Select a profile to load test")
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # File selection area
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(file_frame, text="Select Test Profile (.json):").pack(anchor='w')
        
        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill='x', pady=10)
        
        self.loaded_file_var = tk.StringVar(value="No file selected")
        file_label = ttk.Label(path_frame, textvariable=self.loaded_file_var, foreground='gray')
        file_label.pack(side='left', fill='x', expand=True)
        
        browse_file_btn = ttk.Button(path_frame, text="Browse Files", command=self.browse_test_file)
        browse_file_btn.pack(side='right')
        
        # Test details section
        details_frame = ttk.LabelFrame(main_frame, text="Test Details", padding=15)
        details_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Create details display
        self.details_text = tk.Text(details_frame, height=15, wrap='word', state='disabled')
        self.details_text.pack(fill='both', expand=True)
        
        # Initially show placeholder
        self.update_test_details("No test file loaded. Please select a .json test profile above.")
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        self.start_test_btn = ttk.Button(
            button_frame,
            text="Start Test",
            command=self.show_user_start_screen,
            state='disabled'
        )
        self.start_test_btn.pack(side='left')
        
        back_btn = ttk.Button(button_frame, text="Back to Main Menu", command=self.show_title_screen)
        back_btn.pack(side='right')
    
    def browse_test_file(self):
        """Open file browser for test profile selection."""
        file_path = filedialog.askopenfilename(
            title="Select Test Profile",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.loaded_file_var.set(os.path.basename(file_path))
            
            try:
                # Actually load and parse the JSON file
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_test_data = json.load(f)
                
                # Add the file path to the loaded data
                loaded_test_data['source_file'] = file_path
                
                self.current_test_data = loaded_test_data
                self.update_test_details()
                self.start_test_btn.config(state='normal')
                
                print(f"✅ Successfully loaded test file: {os.path.basename(file_path)}")
                
            except json.JSONDecodeError as e:
                # Handle invalid JSON
                messagebox.showerror(
                    "Invalid JSON File", 
                    f"The selected file is not a valid JSON file.\n\nError: {str(e)}"
                )
                self.loaded_file_var.set("Invalid JSON file")
                self.update_test_details("❌ Invalid JSON file selected. Please choose a valid .json test profile.")
                
            except Exception as e:
                # Handle other file reading errors
                messagebox.showerror(
                    "File Error", 
                    f"Unable to read the selected file.\n\nError: {str(e)}"
                )
                self.loaded_file_var.set("Error reading file")
                self.update_test_details("❌ Error reading file. Please try selecting a different file.")
    
    def update_test_details(self, message=None):
        """Update the test details display with actual JSON content."""
        self.details_text.config(state='normal')
        self.details_text.delete('1.0', tk.END)
        
        if message:
            self.details_text.insert('1.0', message)
        else:
            # Display the actual JSON content in a readable format
            import json
            
            details = "📁 Loaded Test Configuration:\n"
            details += "=" * 50 + "\n\n"
            
            # Show source file info
            if 'source_file' in self.current_test_data:
                details += f"📂 Source File: {os.path.basename(self.current_test_data['source_file'])}\n"
                details += f"📍 Full Path: {self.current_test_data['source_file']}\n\n"
            
            # Show formatted JSON content
            try:
                # Create a copy without the source_file for cleaner display
                display_data = {k: v for k, v in self.current_test_data.items() if k != 'source_file'}
                
                # Format as readable JSON
                formatted_json = json.dumps(display_data, indent=2, ensure_ascii=False)
                
                details += "📋 Test Configuration (JSON Content):\n"
                details += "-" * 30 + "\n"
                details += formatted_json
                
            except Exception as e:
                # Fallback to simple key-value display if JSON formatting fails
                details += "📋 Test Configuration (Key-Value):\n"
                details += "-" * 30 + "\n"
                
                for key, value in self.current_test_data.items():
                    if key != 'source_file':
                        if isinstance(value, dict):
                            details += f"{key}:\n"
                            for sub_key, sub_value in value.items():
                                details += f"  • {sub_key}: {sub_value}\n"
                        else:
                            details += f"{key}: {value}\n"
            
            self.details_text.insert('1.0', details)
        
        self.details_text.config(state='disabled')
    
    # ==================== USER START TEST SCREEN ====================
    def show_user_start_screen(self):
        """Display user-friendly test start screen."""
        self.clear_window()
        self.create_header("Ready to Start Test", "Review test details and begin when ready")
        
        # Create scrollable main content
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable trackpad scrolling on canvas
        canvas.bind("<MouseWheel>", lambda e: self.canvas_trackpad_scroll(canvas, e))
        canvas.bind("<Button-4>", lambda e: self.canvas_trackpad_scroll(canvas, e))
        canvas.bind("<Button-5>", lambda e: self.canvas_trackpad_scroll(canvas, e))
        canvas.focus_set()
        
        # Content frame with reduced padding
        main_frame = ttk.Frame(scrollable_frame)
        main_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Test info card (more compact)
        card_frame = ttk.LabelFrame(main_frame, text="Test Information", padding=15)
        card_frame.pack(fill='x', pady=(0, 15))
        
        # Test name (large)
        name_label = ttk.Label(
            card_frame,
            text=self.current_test_data.get('usershown', 'Test Name'),
            font=('Arial', 14, 'bold')
        )
        name_label.pack(pady=(0, 8))
        
        # URL
        url_frame = ttk.Frame(card_frame)
        url_frame.pack(fill='x', pady=3)
        ttk.Label(url_frame, text="Website:", font=('Arial', 10, 'bold')).pack(side='left')
        ttk.Label(url_frame, text=self.current_test_data.get('url', 'N/A')).pack(side='left', padx=(10, 0))
        
        # Duration
        duration_frame = ttk.Frame(card_frame)
        duration_frame.pack(fill='x', pady=3)
        ttk.Label(duration_frame, text="Duration:", font=('Arial', 10, 'bold')).pack(side='left')
        ttk.Label(duration_frame, text=self.current_test_data.get('duration', 'N/A')).pack(side='left', padx=(10, 0))
        
        # Instructions (more compact)
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructions", padding=12)
        instructions_frame.pack(fill='x', pady=(0, 15))
        
        instructions_text = """1. Click 'Start Test' when you're ready to begin
2. The browser will open automatically to the specified website  
3. Browse naturally - the eye tracker will monitor your activity
4. The test will automatically end after the specified duration
5. Keep your head steady and eyes focused on the screen"""
        
        ttk.Label(instructions_frame, text=instructions_text, justify='left', font=('Arial', 9)).pack()
        
        # Smaller placeholder image or remove it to save space
        image_frame = ttk.Frame(main_frame)
        image_frame.pack(pady=10)
        self.create_placeholder_image(image_frame, 200, 100)
        
        # IMPORTANT: Action buttons - always visible at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 10))
        
        start_btn = ttk.Button(
            button_frame,
            text="🚀 Start Test",
            command=self.start_actual_test,
            style='Accent.TButton'
        )
        start_btn.pack(side='left')
        
        back_btn = ttk.Button(button_frame, text="Back", command=self.show_load_test_screen)
        back_btn.pack(side='right')
        
        # Pack scrollable content
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        # Force canvas to update and ensure buttons are visible
        self.root.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def start_actual_test(self):
        """Start the actual test with eye tracker calibration first."""
        # Show calibration dialog and start calibration
        self.show_calibration_dialog()
    
    def show_calibration_dialog(self):
        """Show calibration preparation dialog."""
        # Create calibration dialog with adjusted size
        calibration_window = tk.Toplevel(self.root)
        calibration_window.title("Eye Tracker Calibration")
        calibration_window.geometry("400x280")
        calibration_window.configure(bg='#f0f0f0')
        calibration_window.transient(self.root)
        calibration_window.grab_set()
        
        # Center the window
        calibration_window.update_idletasks()
        x = (calibration_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (calibration_window.winfo_screenheight() // 2) - (280 // 2)
        calibration_window.geometry(f"+{x}+{y}")
        
        # Header - more compact
        header_frame = ttk.Frame(calibration_window)
        header_frame.pack(fill='x', padx=15, pady=15)
        
        ttk.Label(header_frame, text="🎯 Eye Tracker Calibration", 
                 font=('Arial', 14, 'bold')).pack()
        ttk.Label(header_frame, text="Get ready for calibration", 
                 font=('Arial', 9), foreground='gray').pack(pady=(3, 0))
        
        # Simplified Instructions
        instructions_frame = ttk.LabelFrame(calibration_window, text="Quick Setup", padding=12)
        instructions_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Much shorter, simplified text
        instructions_text = """• Sit 18-24 inches from your camera
• Ensure good lighting on your face  
• Follow the green dots with your eyes
• Keep your head still during calibration
• Takes about 60 seconds"""
        
        ttk.Label(instructions_frame, text=instructions_text, justify='left', 
                 font=('Arial', 9)).pack(anchor='w')
        
        # Action buttons - ensure they're always visible
        button_frame = ttk.Frame(calibration_window)
        button_frame.pack(side='bottom', fill='x', padx=15, pady=15)
        
        # Info label for calibration status
        self.calibration_status_var = tk.StringVar(value="")
        status_label = ttk.Label(calibration_window, textvariable=self.calibration_status_var, foreground='blue', font=('Arial', 9))
        status_label.pack(side='bottom', pady=(0, 5))

        def on_start_calibration():
            self.calibration_status_var.set("Calibration may take up to a minute. Please follow the on-screen instructions.")
            calibration_window.update_idletasks()
            self.start_eye_tracker_calibration(calibration_window)

        start_cal_btn = ttk.Button(
            button_frame,
            text="🚀 Start Calibration",
            command=on_start_calibration,
            style='Accent.TButton'
        )
        start_cal_btn.pack(side='left')

        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=calibration_window.destroy
        )
        cancel_btn.pack(side='right')

        # Force the window to update and ensure proper sizing
        calibration_window.update_idletasks()
    
    def start_eye_tracker_calibration(self, calibration_window):
        """Start the eye tracker calibration process."""
        try:
            # Import EyeTracker
            import sys
            import os
            
            # Add src and project root to path
            current_dir = os.path.dirname(__file__)
            src_dir = os.path.dirname(current_dir)
            project_root = os.path.dirname(src_dir)
            
            sys.path.insert(0, src_dir)
            sys.path.insert(0, project_root)
            
            from src.eye_tracking.EyeTracker import EyeTracker
            
            # Close calibration dialog
            calibration_window.destroy()
            
            # Hide main window during calibration
            self.root.withdraw()
            
            # Initialize shared eye tracker instance if not already created
            if self.eye_tracker is None:
                print("🔧 Initializing EyeTracker for calibration...")
                self.eye_tracker = EyeTracker()
            
            print("🎯 Starting calibration with 25 points...")
            calibration_success = self.eye_tracker.recalibrate(25)
            
            # Show main window again
            self.root.deiconify()
            
            if calibration_success:
                # Calibration successful, proceed with test
                messagebox.showinfo("Calibration Complete", 
                                  "✅ Eye tracker calibration completed successfully!\n\n" +
                                  "🚀 The test will now begin.\n" +
                                  "The browser will open to start your session.")
                self.proceed_with_test_after_calibration()
            else:
                # Calibration failed or cancelled
                messagebox.showwarning("Calibration Cancelled", 
                                     "⚠️ Eye tracker calibration was cancelled.\n\n" +
                                     "The test cannot proceed without calibration.\n" +
                                     "Please try again when ready.")
                
        except Exception as e:
            # Show main window again in case of error
            self.root.deiconify()
            messagebox.showerror("Calibration Error", 
                               f"❌ Failed to start eye tracker calibration:\n\n{str(e)}\n\n" +
                               "You can proceed with the test, but eye tracking may not work properly.")
            # Ask user if they want to proceed anyway
            proceed = messagebox.askyesno("Continue Without Calibration?", 
                                        "Would you like to continue with the test anyway?\n\n" +
                                        "⚠️ Eye tracking data may not be accurate.")
            if proceed:
                self.proceed_with_test_after_calibration()
    
    def proceed_with_test_after_calibration(self):
        """Continue with the actual test after calibration is complete."""
        import threading, time
        try:
            import sys, os
            
            # Add src and project root to path
            current_dir = os.path.dirname(__file__)
            src_dir = os.path.dirname(current_dir)
            project_root = os.path.dirname(src_dir)
            
            sys.path.insert(0, src_dir)
            sys.path.insert(0, project_root)
            
            from src.gui.integrated_test_runner import IntegratedTestManager

            # Duration in minutes (float)
            duration_str = self.current_test_data.get('duration', '2')
            try:
                if 'min' in duration_str.lower():
                    duration = float(duration_str.lower().replace('min', '').replace('utes', '').strip())
                else:
                    duration = float(duration_str)
            except:
                duration = 2.0
            duration_sec = int(duration * 60)

            # Use the calibrated eye tracker instance
            if self.eye_tracker is None:
                print("⚠️ No eye tracker calibrated - test will run without gaze tracking")
                tracker = None
            else:
                print("✅ Using calibrated eye tracker for gaze data collection")
                tracker = self.eye_tracker
            
            # Start browser with eye tracker integration
            test_manager = IntegratedTestManager(self.current_test_data, eye_tracker=tracker)
            
            def on_test_complete():
                print("✅ Test completed - returning to post-test screen")
                # Stop eye tracker gaze tracking but keep calibration
                if tracker and hasattr(tracker, 'tracking_active'):
                    tracker.tracking_active = False
                # Note: We keep the eye tracker instance for potential future tests
                self.root.deiconify()
                self.show_post_test_screen()

            # Start browser with integrated eye tracking
            def browser_thread():
                test_manager.start_test_with_browser(completion_callback=on_test_complete)

            threading.Thread(target=browser_thread, daemon=True).start()

            # Hide the current window while test runs
            self.root.withdraw()
            messagebox.showinfo("Test Started", 
                f"🚀 Eye tracking test has begun!\n\n🌐 The browser will open shortly\n👁️ Eye tracking is now active\n⏱️ Test will run for {duration} minutes.")

            # Wait for the test duration, then show report
            def finish_after_time():
                time.sleep(duration_sec)
                print("⏰ Test duration complete. Closing browser and showing report.")
                # Attempt to close browser
                try:
                    if hasattr(test_manager, 'browser_manager') and hasattr(test_manager.browser_manager, 'close_browser'):
                        test_manager.browser_manager.close_browser()
                except Exception as e:
                    print(f"Error closing browser: {e}")
                # Show report
                self.root.after(0, self.show_post_test_screen)

            threading.Thread(target=finish_after_time, daemon=True).start()

        except ImportError as e:
            messagebox.showinfo("Demo Mode", 
                "⚠️ Test integration not available.\n\nRunning in demo mode...\nThis will simulate a test completion.")
            self.root.after(3000, self.show_post_test_screen)
    
    # ==================== POST TEST SCREEN ====================
    def show_post_test_screen(self):
        """Display screen shown after test completion."""
        self.clear_window()
        self.create_header("Test Completed", "Your eye tracking session has finished")
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=40, pady=30)
        
        # Completion message
        completion_frame = ttk.LabelFrame(main_frame, text="Test Results", padding=20)
        completion_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(
            completion_frame,
            text="✅ Test Completed Successfully!",
            font=('Arial', 14, 'bold'),
            foreground='green'
        ).pack(pady=10)
        
        # Test summary
        summary_text = f"""Test: {self.current_test_data.get('usershown', 'N/A')}
Duration: {self.current_test_data.get('duration', 'N/A')}
Website: {self.current_test_data.get('url', 'N/A')}

Eye tracking data has been saved and is ready for analysis."""
        
        ttk.Label(completion_frame, text=summary_text, justify='center').pack()
        
        # Placeholder for results visualization
        results_frame = ttk.LabelFrame(main_frame, text="Results Preview", padding=15)
        results_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.create_placeholder_image(results_frame, 300, 200)
        ttk.Label(results_frame, text="Results visualization will appear here", foreground='gray').pack(pady=10)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        another_test_btn = ttk.Button(
            button_frame,
            text="Start Another Test",
            command=self.show_user_start_screen
        )
        another_test_btn.pack(side='left')
        
        main_menu_btn = ttk.Button(
            button_frame,
            text="Main Menu",
            command=self.show_title_screen
        )
        main_menu_btn.pack(side='right')
    
    # ==================== PROCESS REPORTS SCREEN ====================
    def show_process_reports_screen(self):
        """Display the process reports screen (placeholder)."""
        self.clear_window()
        self.create_header("Process Reports", "Analyze and generate test reports")
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Placeholder content
        placeholder_frame = ttk.LabelFrame(main_frame, text="Report Processing", padding=30)
        placeholder_frame.pack(fill='both', expand=True)
        
        self.create_placeholder_image(placeholder_frame, 200, 150)
        
        ttk.Label(
            placeholder_frame,
            text="Report processing functionality\nwill be implemented here",
            justify='center',
            font=('Arial', 12),
            foreground='gray'
        ).pack(pady=20)
        
        # Back button
        back_btn = ttk.Button(main_frame, text="Back to Main Menu", command=self.show_title_screen)
        back_btn.pack(pady=20)
    
    def run(self):
        """Start the application."""
        # Configure styles
        style = ttk.Style()
        try:
            style.theme_use('clam')  # Modern theme
        except:
            pass  # Use default if clam not available
        
        self.root.mainloop()


# Main execution
if __name__ == "__main__":
    app = TestUIManager()
    app.run()