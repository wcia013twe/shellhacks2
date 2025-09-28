"""
Test the improved browser timing with Chrome and timer coordination
"""
import sys
import time
sys.path.append('src')

from browser.browser_manager import BrowserManager

def test_timing():
    print("🔧 Testing Browser + Timer Timing")
    print("=" * 40)
    
    browser = BrowserManager()
    
    start_time = time.time()
    
    def ready_callback():
        load_time = time.time() - start_time
        print(f"✅ Browser ready after {load_time:.2f} seconds")
        print("🕐 Timer would start NOW (not before)")
    
    print("🚀 Launching browser with timing callback...")
    
    try:
        success, result = browser.launch_browser(
            "https://github.com", 
            None, 
            ready_callback
        )
        
        if success:
            total_time = time.time() - start_time
            print(f"📊 Total session time: {total_time:.2f} seconds")
        else:
            print(f"❌ Failed: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        browser.close_browser()

if __name__ == "__main__":
    test_timing()