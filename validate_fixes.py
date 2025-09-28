#!/usr/bin/env python3
"""
Quick validation test for browser error fixes - code inspection only
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_browser_manager_fixes():
    """Test that the BrowserManager code has the TrustedHTML fix"""
    print("🔧 Testing Browser Manager TrustedHTML Fix...")
    
    browser_manager_path = os.path.join(project_root, 'src', 'browser', 'browser_manager.py')
    
    try:
        with open(browser_manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for the fixed code patterns
        if 'innerHTML =' in content:
            print("❌ Still using innerHTML assignment (TrustedHTML risk)")
            return False
        
        if 'createElement(' in content and 'appendChild(' in content:
            print("✅ Using DOM manipulation instead of innerHTML")
        else:
            print("⚠️ DOM manipulation pattern not found")
            return False
        
        if 'sidebar.appendChild(panel)' in content:
            print("✅ Proper DOM assembly found")
        else:
            print("⚠️ Sidebar assembly pattern not found")
            return False
            
    except Exception as e:
        print(f"❌ Could not read browser manager: {e}")
        return False
    
    return True

def test_ui_manager_fixes():
    """Test that the UI Manager has alert handling fixes"""
    print("\n🎯 Testing UI Manager Alert Handling Fix...")
    
    ui_manager_path = os.path.join(project_root, 'src', 'gui', 'test_ui_manager.py')
    
    try:
        with open(ui_manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for alert handling code
        if 'alert.accept()' in content:
            print("✅ Alert dismissal handling found")
        else:
            print("⚠️ Alert dismissal pattern not found")
            return False
        
        if 'window.__componentConfig' in content:
            print("✅ Component config retrieval found")
        else:
            print("⚠️ Component config pattern not found")
            return False
        
        # Check for toast notification instead of alert
        if 'notificationToast' in content and 'alert(' not in content.replace('alert.accept', ''):
            print("✅ Toast notification used instead of alert")
        else:
            print("⚠️ Toast notification pattern incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Could not read UI manager: {e}")
        return False
    
    return True

def test_import_system():
    """Test that import system works"""
    print("\n📦 Testing Import System...")
    
    try:
        # Test BrowserManager import
        from src.browser.browser_manager import BrowserManager
        print("✅ BrowserManager import successful")
        
        # Test UI Manager import  
        from src.gui.test_ui_manager import TestUIManager
        print("✅ TestUIManager import successful")
        
        # Test that BrowserManager can be instantiated
        browser_manager = BrowserManager()
        print("✅ BrowserManager instantiation successful")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Instantiation error: {e}")
        return False
    
    return True

def run_validation():
    """Run validation tests for the fixes"""
    print("🚀 Browser Error Fixes Validation")
    print("=" * 50)
    
    results = []
    
    # Test 1: Browser Manager TrustedHTML fix
    browser_fix = test_browser_manager_fixes()
    results.append(("TrustedHTML Fix", browser_fix))
    
    # Test 2: UI Manager alert handling
    ui_fix = test_ui_manager_fixes()
    results.append(("Alert Handling Fix", ui_fix))
    
    # Test 3: Import system
    import_test = test_import_system()
    results.append(("Import System", import_test))
    
    # Report results
    print("\n" + "=" * 50)
    print("📊 VALIDATION RESULTS")
    print("=" * 50)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
        if not success:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("\n✅ Fixed Issues:")
        print("   • TrustedHTML assignment error (sidebar injection)")
        print("   • Alert interference (component configuration)")
        print("   • Element ranking uses toast notifications")
        print("   • Robust alert handling prevents data check failures")
        
        print("\n🔍 What was changed:")
        print("   1. Replaced innerHTML with DOM createElement/appendChild")
        print("   2. Added alert dismissal before component data check") 
        print("   3. Replaced blocking alert with toast notification")
        print("   4. Enhanced error handling and data retrieval")
        
        print("\n🚀 Ready for testing:")
        print("   • Component configuration button should work")
        print("   • Browser should launch without TrustedHTML errors")
        print("   • Element ranking should complete without interference")
    else:
        print("⚠️ Some validations failed. Check the code changes.")
    
    return all_passed

if __name__ == "__main__":
    run_validation()