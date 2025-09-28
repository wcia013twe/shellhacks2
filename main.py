"""
Simple Browser Launcher Application

This is the main entry point for the Simple Browser Launcher application.
It imports and runs the GUI from the modular src package.

Features:
- Selenium WebDriver browser (no iframe restrictions!)
- JavaScript injection support
- Eye tracking integration
- Timer-based browsing sessions
- Modular architecture for easy extension
"""

import sys
import argparse
from src.gui import SimpleBrowserLauncher


def test_selenium_browser():
    """Test the new Selenium WebDriver browser."""
    print("🚀 Testing Selenium WebDriver Browser")
    print("=" * 50)
    
    try:
        from src.browser.browser_manager import BrowserManager
        
        # Create browser manager
        browser = BrowserManager()
        print("✅ Selenium browser manager created")
        
        # Get URL from user
        default_url = "https://github.com"
        url = input(f"\nEnter URL to test (or press Enter for {default_url}): ").strip()
        if not url:
            url = default_url
        
        print(f"\n🌐 Launching browser with: {url}")
        print("💡 This will open a real Chrome browser with:")
        print("   • No iframe restrictions (GitHub, YouTube, etc. will work!)")
        print("   • Sidebar overlay with quick navigation")
        print("   • JavaScript injection capabilities")
        print("   • Eye tracking support (if configured)")
        print()
        
        # Launch browser
        success, result = browser.launch_browser(url)
        
        if success:
            print("\n🎉 Browser launched successfully!")
            print("\n📋 Try these features:")
            print("   1. Click the ☰ button (top-left) to open sidebar")
            print("   2. Navigate to GitHub, YouTube, any site - they all work!")
            print("   3. Use the sidebar links for quick navigation")
            print("\n🔧 Developer features:")
            print("   • F12 for DevTools")
            print("   • Full JavaScript console access")
            print("   • No security restrictions")
            
            # Interactive commands
            print("\n" + "="*30)
            print("Interactive Commands (while browser is open):")
            print("  t - Test eye tracker integration")
            print("  j - Inject test JavaScript")
            print("  n - Navigate to new URL")
            print("  q - Quit")
            print("="*30)
            
            while browser.driver:
                try:
                    command = input("\nCommand (t/j/n/q): ").strip().lower()
                    
                    if command == 'q':
                        break
                    elif command == 't':
                        test_eye_tracker_integration(browser)
                    elif command == 'j':
                        inject_test_javascript(browser)
                    elif command == 'n':
                        new_url = input("Enter new URL: ").strip()
                        if new_url and browser.navigate_to(new_url):
                            print(f"✅ Navigated to: {new_url}")
                        else:
                            print("❌ Navigation failed")
                    else:
                        print("❓ Unknown command")
                        
                except KeyboardInterrupt:
                    break
                except:
                    # Browser might be closed
                    break
            
            browser.close_browser()
            
        else:
            print(f"❌ Failed to launch browser: {result}")
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure to install: pip install selenium webdriver-manager")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_eye_tracker_integration(browser):
    """Test eye tracker integration."""
    print("\n👁️ Testing Eye Tracker Integration...")
    
    try:
        from src.eye_tracking.EyeTracker import EyeTracker
        
        print("📷 Initializing eye tracker...")
        eye_tracker = EyeTracker()
        
        calibrate = input("Calibrate eye tracker? (y/n): ").strip().lower()
        if calibrate == 'y':
            num_points = input("Calibration points (default 25): ").strip()
            try:
                num_points = int(num_points) if num_points else 25
            except:
                num_points = 25
                
            print(f"🎯 Calibrating with {num_points} points...")
            if eye_tracker.recalibrate(num_points):
                print("✅ Calibration successful!")
                
                # Integrate with browser
                browser.integrate_eye_tracker(eye_tracker)
                print("✅ Eye tracking overlay active!")
                print("👁️ Look around to see your gaze position!")
                print("   💛 Yellow circle = Looking around")
                print("   💚 Green circle = Fixating")
                
                input("Press Enter to stop eye tracking...")
                browser.tracking_active = False
                
            else:
                print("❌ Calibration cancelled")
        else:
            print("⏭️ Skipping calibration")
            
    except ImportError:
        print("❌ EyeTracker not found")
    except Exception as e:
        print(f"❌ Eye tracker error: {e}")


def inject_test_javascript(browser):
    """Test JavaScript injection."""
    print("\n🔧 JavaScript Injection Test")
    
    test_scripts = {
        "1": {
            "name": "Highlight all links",
            "script": """
                document.querySelectorAll('a').forEach((link, i) => {
                    link.style.background = `hsl(${i * 30}, 70%, 80%)`;
                    link.style.padding = '2px 4px';
                    link.style.borderRadius = '3px';
                });
                return 'Links highlighted!';
            """
        },
        "2": {
            "name": "Add floating message",
            "script": """
                const msg = document.createElement('div');
                msg.innerHTML = '🎉 JavaScript Works!';
                msg.style.cssText = `
                    position: fixed; top: 100px; right: 20px; z-index: 999999;
                    background: #4CAF50; color: white; padding: 15px;
                    border-radius: 8px; font-family: Arial; font-size: 16px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                `;
                document.body.appendChild(msg);
                setTimeout(() => msg.remove(), 5000);
                return 'Message added!';
            """
        },
        "3": {
            "name": "Rainbow page background",
            "script": """
                let hue = 0;
                const rainbow = setInterval(() => {
                    document.body.style.background = `hsl(${hue}, 50%, 95%)`;
                    hue = (hue + 1) % 360;
                }, 50);
                setTimeout(() => {
                    clearInterval(rainbow);
                    document.body.style.background = '';
                }, 10000);
                return 'Rainbow background started!';
            """
        }
    }
    
    print("\nAvailable test scripts:")
    for key, script in test_scripts.items():
        print(f"  {key}. {script['name']}")
    print("  c. Custom JavaScript")
    
    choice = input("Choose script (1/2/3/c): ").strip()
    
    if choice in test_scripts:
        script = test_scripts[choice]["script"]
        print(f"🚀 Running: {test_scripts[choice]['name']}")
    elif choice.lower() == 'c':
        print("Enter JavaScript (end with empty line):")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        script = '\n'.join(lines)
    else:
        print("❌ Invalid choice")
        return
    
    try:
        result = browser.inject_javascript(script)
        print(f"✅ JavaScript executed!")
        if result:
            print(f"📋 Result: {result}")
    except Exception as e:
        print(f"❌ JavaScript failed: {e}")


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description="Browser Launcher with Selenium Support")
    parser.add_argument(
        "--selenium", 
        action="store_true", 
        help="Launch Selenium WebDriver browser (recommended)"
    )
    
    args = parser.parse_args()
    
    if args.selenium:
        test_selenium_browser()
    else:
        print("🚀 Starting Browser Launcher...")
        print("💡 Use --selenium for the new Selenium browser (recommended)")
        print("Features: No iframe restrictions, JavaScript injection, eye tracking")
        print()
        
        app = SimpleBrowserLauncher()
        app.run()


if __name__ == "__main__":
    main()