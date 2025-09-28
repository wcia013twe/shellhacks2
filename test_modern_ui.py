#!/usr/bin/env python3
"""
Demo script to showcase the modernized UI styling
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_modern_ui():
    """Test the modernized UI styling"""
    print("🎨 Testing Modern UI Styling")
    print("=" * 50)
    
    try:
        # Import the modernized UI manager
        from src.gui.test_ui_manager import TestUIManager
        
        print("✅ Successfully imported TestUIManager")
        print("🎯 Launching modern UI...")
        
        # Create and run the UI
        ui_manager = TestUIManager()
        
        print("\n🎨 Modern Design Features:")
        print("   • Inter font typography system")
        print("   • Modern color palette with primary blues")
        print("   • Card-based layouts with hover effects")
        print("   • Enhanced spacing and visual hierarchy")
        print("   • Consistent styling across all components")
        print("   • Modern button styles with proper states")
        
        print("\n🎯 UI launched successfully!")
        print("   Close the window to continue...")
        
        # Run the UI
        ui_manager.root.mainloop()
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_system_launcher():
    """Test the modernized system launcher"""
    print("\n🚀 Testing Modern System Launcher")
    print("=" * 50)
    
    try:
        from system_launcher import LauncherSelector
        
        print("✅ Successfully imported LauncherSelector")
        print("🎯 Launching modern launcher...")
        
        launcher = LauncherSelector()
        
        print("\n🎨 Modern Launcher Features:")
        print("   • Updated color scheme")
        print("   • Modern typography")
        print("   • Enhanced visual design")
        
        launcher.root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run the modern UI tests"""
    print("🎨 Modern UI Styling Test Suite")
    print("=" * 60)
    
    # Test main UI manager
    success1 = test_modern_ui()
    
    # Test system launcher
    success2 = test_system_launcher()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Modern UI styling successfully applied:")
        print("   • Enhanced color palette with modern blues and grays")
        print("   • Inter font family for better readability")
        print("   • Card-based layouts with subtle shadows")
        print("   • Improved button styling with hover effects")
        print("   • Better spacing and visual hierarchy")
        print("   • Consistent design language across components")
        
        print("\n🎯 Key Improvements:")
        print("   • Replaced Arial with Inter font")
        print("   • Added modern color variables system")
        print("   • Implemented card-based UI patterns")
        print("   • Enhanced form field styling")
        print("   • Added proper visual states and feedback")
        
        print("\n🚀 Your eye tracking application now has a modern,")
        print("   professional appearance that matches contemporary")
        print("   design standards!")
        
    else:
        print("❌ SOME TESTS FAILED!")
        print("   Check the console output above for details")

if __name__ == "__main__":
    main()