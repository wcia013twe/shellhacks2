"""
Comprehensive Launcher for Eye Tracking Test System

This launcher provides access to both the original browser launcher
and the new comprehensive test UI system.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Add src to path for imports
current_dir = os.path.dirname(__file__)
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)


class LauncherSelector:
    """Main launcher that lets users choose between UI modes."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Eye Tracking System Launcher")
        self.root.geometry("500x400")
        self.root.configure(bg='#f0f0f0')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the launcher interface."""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=20, pady=20)
        
        title_label = ttk.Label(
            header_frame,
            text="Eye Tracking Test System",
            font=('Arial', 18, 'bold')
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Choose your interface",
            font=('Arial', 10),
            foreground='gray'
        )
        subtitle_label.pack()
        
        # Separator
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x', padx=20, pady=10)
        
        # Main content
        content_frame = ttk.Frame(self.root)
        content_frame.pack(expand=True, fill='both', padx=40, pady=20)
        
        # Option 1: Comprehensive Test Manager
        comprehensive_frame = ttk.LabelFrame(content_frame, text="🧪 Comprehensive Test Manager", padding=15)
        comprehensive_frame.pack(fill='x', pady=(0, 15))
        
        comp_desc = """• Complete test configuration and management
• Setup tests with detailed parameters
• Load and manage test profiles
• User-friendly test execution
• Post-test analysis screens"""
        
        ttk.Label(comprehensive_frame, text=comp_desc, justify='left').pack(anchor='w')
        
        comp_btn = ttk.Button(
            comprehensive_frame,
            text="Launch Test Manager",
            command=self.launch_comprehensive_ui,
            style='Accent.TButton'
        )
        comp_btn.pack(pady=(10, 0))
        
        # Option 2: Simple Browser Launcher
        simple_frame = ttk.LabelFrame(content_frame, text="🌐 Simple Browser Launcher", padding=15)
        simple_frame.pack(fill='x', pady=(0, 15))
        
        simple_desc = """• Direct browser launcher
• Quick URL and timer setup
• Immediate test execution
• Original interface (compatible)"""
        
        ttk.Label(simple_frame, text=simple_desc, justify='left').pack(anchor='w')
        
        simple_btn = ttk.Button(
            simple_frame,
            text="Launch Browser Tool",
            command=self.launch_simple_ui
        )
        simple_btn.pack(pady=(10, 0))
        
        # Option 3: Integration Demo
        demo_frame = ttk.LabelFrame(content_frame, text="🔧 Integration Demo", padding=15)
        demo_frame.pack(fill='x')
        
        demo_desc = """• Test integration between new and old UI
• Sample test configuration
• Browser + Timer coordination demo"""
        
        ttk.Label(demo_frame, text=demo_desc, justify='left').pack(anchor='w')
        
        demo_btn = ttk.Button(
            demo_frame,
            text="Launch Integration Demo",
            command=self.launch_integration_demo
        )
        demo_btn.pack(pady=(10, 0))
        
        # Footer
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(side='bottom', fill='x', padx=20, pady=10)
        
        footer_label = ttk.Label(
            footer_frame,
            text="All interfaces support eye tracking integration • Selenium browser • No iframe restrictions",
            font=('Arial', 8),
            foreground='gray'
        )
        footer_label.pack()
    
    def launch_comprehensive_ui(self):
        """Launch the comprehensive test UI manager."""
        try:
            from src.gui.test_ui_manager import TestUIManager
            
            self.root.withdraw()  # Hide launcher
            
            app = TestUIManager()
            app.run()
            
            self.root.deiconify()  # Show launcher again when done
            
        except ImportError as e:
            messagebox.showerror("Error", f"Could not load Test UI Manager: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Test UI Manager: {e}")
    
    def launch_simple_ui(self):
        """Launch the simple browser launcher."""
        try:
            from src.gui.main_window import SimpleBrowserLauncher
            
            self.root.withdraw()  # Hide launcher
            
            app = SimpleBrowserLauncher()
            app.run()
            
            self.root.deiconify()  # Show launcher again when done
            
        except ImportError as e:
            messagebox.showerror("Error", f"Could not load Simple Browser Launcher: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Simple Browser: {e}")
    
    def launch_integration_demo(self):
        """Launch the integration demo."""
        try:
            from src.gui.integrated_test_runner import ModifiedMainWindow
            
            # Sample test data for demo
            sample_data = {
                'filename': 'demo_youtube_test',
                'usershown': 'YouTube Focus Demo Test',
                'url': 'https://www.youtube.com',
                'duration': '1',  # 1 minute for demo
                'description': 'Demo test showing integration between new UI and existing browser functionality.'
            }
            
            self.root.withdraw()  # Hide launcher
            
            app = ModifiedMainWindow(sample_data)
            app.run()
            
            self.root.deiconify()  # Show launcher again when done
            
        except ImportError as e:
            messagebox.showerror("Error", f"Could not load Integration Demo: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Integration Demo: {e}")
    
    def run(self):
        """Start the launcher."""
        # Configure styles
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass
        
        self.root.mainloop()


if __name__ == "__main__":
    print("🚀 Eye Tracking System Launcher")
    print("=" * 40)
    print("Available interfaces:")
    print("  1. Comprehensive Test Manager - Full featured test setup and management")
    print("  2. Simple Browser Launcher - Direct browser access with timers") 
    print("  3. Integration Demo - Shows new + old UI working together")
    print("\nLaunching interface selector...")
    
    launcher = LauncherSelector()
    launcher.run()