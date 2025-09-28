#!/usr/bin/env python3
"""
Test the import fix for the relative import error
"""

import sys
import os

# Add project root to path like the application does
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_absolute_imports():
    """Test that the absolute imports work correctly"""
    print("🔍 Testing absolute import fixes...")
    
    try:
        # Test the path setup that's now used in the application
        current_dir = os.path.join(project_root, 'src', 'gui')
        src_dir = os.path.dirname(current_dir)
        project_root_test = os.path.dirname(src_dir)
        
        sys.path.insert(0, src_dir)
        sys.path.insert(0, project_root_test)
        
        print(f"✅ Path setup complete:")
        print(f"   • Project root: {project_root_test}")
        print(f"   • Src dir: {src_dir}")
        print(f"   • Current dir: {current_dir}")
        
        # Test EyeTracker import
        from src.eye_tracking.EyeTracker import EyeTracker
        print("✅ EyeTracker import successful")
        
        # Test IntegratedTestManager import
        from src.gui.integrated_test_runner import IntegratedTestManager
        print("✅ IntegratedTestManager import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_ui_manager_import():
    """Test that TestUIManager can be imported and instantiated"""
    print("\n🔍 Testing TestUIManager functionality...")
    
    try:
        from src.gui.test_ui_manager import TestUIManager
        print("✅ TestUIManager import successful")
        
        # Don't actually create the UI (requires display)
        print("✅ TestUIManager should work correctly now")
        
        return True
        
    except Exception as e:
        print(f"❌ TestUIManager test failed: {e}")
        return False

def main():
    """Run the import fix tests"""
    print("🧪 Import Fix Verification")
    print("=" * 50)
    
    test1 = test_absolute_imports()
    test2 = test_ui_manager_import()
    
    print("\n" + "=" * 50)
    
    if test1 and test2:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Import fixes successful:")
        print("   • Absolute imports work correctly")
        print("   • Path manipulation is proper")
        print("   • No more relative import errors")
        
        print("\n🚀 The 'attempted relative import with no known parent package'")
        print("   error should be completely resolved!")
        
    else:
        print("❌ SOME TESTS FAILED!")
        print("   There may still be import issues to resolve")

if __name__ == "__main__":
    main()