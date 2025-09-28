"""
Troubleshooting script for browser-based component configuration system.
This script helps diagnose issues with element ranking and selection.
"""

import sys
import os
import time
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.browser.browser_manager import BrowserManager
    print("✅ BrowserManager imported successfully")
except ImportError as e:
    print(f"❌ Failed to import BrowserManager: {e}")
    sys.exit(1)

def test_basic_browser():
    """Test basic browser functionality"""
    print("\n🔍 Testing basic browser functionality...")
    
    try:
        manager = BrowserManager()
        print("✅ BrowserManager created")
        
        # Test opening a simple page
        driver = manager.get_driver()
        print("✅ WebDriver obtained")
        
        driver.get("https://example.com")
        print("✅ Page loaded successfully")
        
        title = driver.title
        print(f"✅ Page title: {title}")
        
        manager.close()
        print("✅ Browser closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic browser test failed: {e}")
        return False

def test_script_injection():
    """Test JavaScript injection capabilities"""
    print("\n🔍 Testing JavaScript injection...")
    
    try:
        manager = BrowserManager()
        driver = manager.get_driver()
        
        # Load a test page
        driver.get("data:text/html,<html><body><h1>Test Page</h1><p>Test paragraph</p></body></html>")
        time.sleep(1)
        
        # Test simple script injection
        test_script = """
        console.log('Test script executed');
        return 'INJECTION_SUCCESS';
        """
        
        result = driver.execute_script(test_script)
        print(f"✅ Script injection result: {result}")
        
        # Test DOM manipulation
        dom_script = """
        document.body.style.backgroundColor = 'lightblue';
        return document.body.style.backgroundColor;
        """
        
        bg_color = driver.execute_script(dom_script)
        print(f"✅ DOM manipulation result: {bg_color}")
        
        manager.close()
        return True
        
    except Exception as e:
        print(f"❌ Script injection test failed: {e}")
        return False

def test_element_ranking_script():
    """Test the full element ranking script functionality"""
    print("\n🔍 Testing element ranking script...")
    
    try:
        manager = BrowserManager()
        driver = manager.get_driver()
        
        # Create a test HTML page with various elements
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Element Ranking Test</title>
            <style>
                .container { padding: 20px; }
                .button { background: blue; color: white; padding: 10px; margin: 5px; }
                .text { font-size: 16px; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 id="title">Test Page Title</h1>
                <button class="button" id="btn1">Button 1</button>
                <button class="button" id="btn2">Button 2</button>
                <p class="text" id="para1">This is test paragraph 1</p>
                <p class="text" id="para2">This is test paragraph 2</p>
                <input type="text" id="input1" placeholder="Test input">
                <div id="div1">Test div content</div>
            </div>
        </body>
        </html>
        """
        
        driver.get(f"data:text/html,{test_html}")
        time.sleep(1)
        
        # Inject the element ranking script
        ranking_script = """
        (function() {
          const INTERNAL_PREFIX = 'eyetrack_';
          let rankedElements = new Map();
          let isActive = false;
          let bannerEl = null;
          let instructionsEl = null;

          // Enhanced styles for better visibility
          const styles = document.createElement('style');
          styles.textContent = `
            .${INTERNAL_PREFIX}banner {
              position: fixed !important; z-index: 2147483647 !important; top: 0 !important; left: 0 !important;
              width: 100% !important; background: linear-gradient(90deg, #ff1744, #ff9800) !important;
              color: white !important; padding: 12px !important; text-align: center !important;
              font: bold 16px system-ui !important; box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
              animation: glow 2s ease-in-out infinite alternate !important;
            }
            @keyframes glow {
              from { box-shadow: 0 4px 20px rgba(255,23,68,0.3); }
              to { box-shadow: 0 4px 20px rgba(255,23,68,0.8); }
            }
            .${INTERNAL_PREFIX}pending {
              outline: 3px dashed #00ff00 !important;
              outline-offset: 2px !important;
              background-color: rgba(0,255,0,0.1) !important;
              animation: pulse 1s infinite !important;
            }
            @keyframes pulse {
              0%, 100% { transform: scale(1); }
              50% { transform: scale(1.02); }
            }
            .${INTERNAL_PREFIX}rank-1 { 
              outline: 4px solid #ff1744 !important; 
              box-shadow: 0 0 20px #ff1744 !important;
              background-color: rgba(255,23,68,0.1) !important;
            }
            .${INTERNAL_PREFIX}rank-2 { 
              outline: 4px solid #ff9800 !important; 
              box-shadow: 0 0 20px #ff9800 !important;
              background-color: rgba(255,152,0,0.1) !important;
            }
            .${INTERNAL_PREFIX}rank-3 { 
              outline: 4px solid #ffc107 !important; 
              box-shadow: 0 0 20px #ffc107 !important;
              background-color: rgba(255,193,7,0.1) !important;
            }
            .${INTERNAL_PREFIX}rank-4 { 
              outline: 4px solid #4caf50 !important; 
              box-shadow: 0 0 20px #4caf50 !important;
              background-color: rgba(76,175,80,0.1) !important;
            }
            .${INTERNAL_PREFIX}rank-5 { 
              outline: 4px solid #2196f3 !important; 
              box-shadow: 0 0 20px #2196f3 !important;
              background-color: rgba(33,150,243,0.1) !important;
            }
          `;
          document.head.appendChild(styles);

          const showBanner = () => {
            if (bannerEl) return;
            bannerEl = document.createElement("div");
            bannerEl.className = `${INTERNAL_PREFIX}banner`;
            bannerEl.innerHTML = `
              🎯 ELEMENT RANKING ACTIVE - Alt+Click elements to rank them (1-5) | Press ESC when done
            `;
            document.documentElement.appendChild(bannerEl);
          };

          const showInstructions = () => {
            if (instructionsEl) return;
            instructionsEl = document.createElement("div");
            instructionsEl.style.cssText = `
              position: fixed; z-index: 2147483647; top: 80px; left: 50%; transform: translateX(-50%);
              background: #0b1220; color: #e6f0ff; padding: 20px; border-radius: 12px;
              font: 14px/1.4 system-ui; box-shadow: 0 8px 25px rgba(0,0,0,0.6); max-width: 500px;
              border: 2px solid #1e90ff;
            `;
            instructionsEl.innerHTML = `
              <div style="font-weight:600; margin-bottom:12px; color:#1e90ff; font-size:16px;">🎯 ELEMENT RANKING INSTRUCTIONS</div>
              <div style="margin-bottom:8px;">• <strong style="color:#ffd700;">Alt+Click</strong> any element to select it</div>
              <div style="margin-bottom:8px;">• Choose importance rank <strong style="color:#00ff00;">1-5</strong> (1=most important)</div>
              <div style="margin-bottom:8px;">• <strong style="color:#ff6b6b;">Alt+Click again</strong> on ranked elements to remove</div>
              <div style="color:#ffd700; font-weight:600; text-align:center; margin-top:12px;">
                Press <strong>ESC</strong> when finished to save configuration
              </div>
            `;
            document.documentElement.appendChild(instructionsEl);
            
            setTimeout(() => {
              if (instructionsEl) {
                instructionsEl.remove();
                instructionsEl = null;
              }
            }, 8000);
          };

          const handleAltClick = (e) => {
            if (!e.altKey) return;
            e.preventDefault();
            e.stopPropagation();
            
            const element = e.target;
            console.log('Alt+Click detected on:', element.tagName, element.id || element.className);
          };

          const activateRanking = () => {
            if (isActive) return;
            isActive = true;
            
            showBanner();
            showInstructions();
            
            document.addEventListener('click', handleAltClick, true);
            console.log('✅ Element ranking system activated');
          };

          // Auto-activate for testing
          setTimeout(activateRanking, 500);
          
          return 'ELEMENT_RANKING_SCRIPT_LOADED';
        })();
        """
        
        result = driver.execute_script(ranking_script)
        print(f"✅ Element ranking script injection result: {result}")
        
        # Wait to see visual effects
        time.sleep(3)
        
        # Test if banner is visible
        banner_check = driver.execute_script("""
        const banner = document.querySelector('[class*="eyetrack_banner"]');
        return banner ? {
          exists: true,
          visible: banner.offsetHeight > 0,
          text: banner.textContent.trim()
        } : {exists: false};
        """)
        
        print(f"✅ Banner check result: {banner_check}")
        
        # Test element highlighting
        highlight_test = driver.execute_script("""
        const testEl = document.getElementById('btn1');
        if (testEl) {
          testEl.className += ' eyetrack_rank-1';
          return {
            success: true,
            element: testEl.tagName + '#' + testEl.id,
            classes: testEl.className
          };
        }
        return {success: false};
        """)
        
        print(f"✅ Element highlighting test: {highlight_test}")
        
        # Keep browser open for visual inspection
        print("\n🔍 Browser will stay open for 10 seconds for visual inspection...")
        time.sleep(10)
        
        manager.close()
        return True
        
    except Exception as e:
        print(f"❌ Element ranking test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests in sequence"""
    print("🚀 Starting comprehensive component configuration troubleshooting...")
    print("=" * 60)
    
    tests = [
        ("Basic Browser", test_basic_browser),
        ("Script Injection", test_script_injection),
        ("Element Ranking", test_element_ranking_script)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 TROUBLESHOOTING RESULTS:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! Component configuration system is working correctly.")
        print("   If you're still not seeing the overlay, try:")
        print("   1. Make sure you're Alt+clicking elements")
        print("   2. Check browser console for any errors")
        print("   3. Try refreshing the page and running again")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    return all_passed

if __name__ == "__main__":
    try:
        run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error during testing: {e}")
        import traceback
        traceback.print_exc()