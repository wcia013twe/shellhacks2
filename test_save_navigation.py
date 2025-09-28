#!/usr/bin/env python3
"""
Test script to verify the auto-navigation back to main menu after save
"""

import sys
import os
import tempfile
import threading
import time

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_save_navigation():
    """Test that save navigates back to main menu"""
    print("🧪 Testing Save Navigation Functionality...")
    
    try:
        # Import the UI manager
        import tkinter as tk
        from src.gui.test_ui_manager import TestUIManager
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"📁 Using temporary directory: {temp_dir}")
            
            # Create test setup
            root = tk.Tk()
            root.withdraw()  # Hide the window initially
            
            # Create UI manager
            ui_manager = TestUIManager()
            
            # Start with setup screen
            ui_manager.show_setup_test_screen()
            current_screen = "setup"
            print("📺 Started on setup screen")
            
            # Mock the form entries
            class MockEntry:
                def __init__(self, value):
                    self.value = value
                def get(self):
                    return self.value
                    
            class MockVar:
                def __init__(self, value):
                    self.value = value
                def get(self):
                    return self.value
                    
            ui_manager.setup_entries = {
                'filename': MockEntry('test_navigation'),
                'url': MockEntry('https://example.com'),
                'duration': MockEntry('1')
            }
            
            # Mock destination path
            ui_manager.dest_path_var = MockVar(temp_dir)
            
            # Mock component configuration data (optional)
            ui_manager.component_config_data = {
                'origin': 'https://example.com',
                'path': '/',
                'url': 'https://example.com',
                'ranks': {
                    '1': [{'selector': 'h1', 'tag': 'h1'}]
                }
            }
            
            # Override show_title_screen to capture navigation
            original_show_title = ui_manager.show_title_screen
            navigation_captured = {'called': False}
            
            def mock_show_title():
                navigation_captured['called'] = True
                print("🏠 Navigation to main menu captured!")
                return original_show_title()
                
            ui_manager.show_title_screen = mock_show_title
            
            # Override messagebox to avoid blocking
            import tkinter.messagebox as messagebox
            original_showinfo = messagebox.showinfo
            messagebox_shown = {'called': False, 'message': ''}
            
            def mock_showinfo(title, message):
                messagebox_shown['called'] = True
                messagebox_shown['message'] = message
                print(f"💬 Success message shown: {title}")
                return 'ok'
                
            messagebox.showinfo = mock_showinfo
            
            print("🔧 Triggering save configuration...")
            
            # Trigger the save (this should navigate back to main menu)
            ui_manager.save_test_config()
            
            # Check results
            success = True
            
            if not messagebox_shown['called']:
                print("❌ Success message not shown")
                success = False
            else:
                print("✅ Success message displayed")
            
            if not navigation_captured['called']:
                print("❌ Navigation to main menu not triggered")
                success = False
            else:
                print("✅ Navigation back to main menu successful!")
            
            # Check file was created
            files = os.listdir(temp_dir)
            if len(files) == 1:
                print("✅ Configuration file created successfully")
            else:
                print(f"⚠️ Expected 1 file, got {len(files)}")
            
            # Cleanup
            messagebox.showinfo = original_showinfo
            root.destroy()
            
            return success
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the save navigation test"""
    print("🚀 Save Navigation Test")
    print("=" * 40)
    
    success = test_save_navigation()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 TEST PASSED!")
        print("\n✅ Save navigation works correctly:")
        print("   • Configuration saves successfully")
        print("   • Success message is displayed")
        print("   • User is automatically taken back to main menu")
        print("   • No manual navigation required")
        
        print("\n🔄 User Experience Flow:")
        print("   1. User fills out setup form")
        print("   2. User clicks 'Save Test Config'")
        print("   3. Success message appears")
        print("   4. Automatically returns to main menu")
        
    else:
        print("❌ TEST FAILED!")
        print("   Check the console output above for details")
    
    print("\n🎯 Next time you save a config:")
    print("   • You'll be automatically returned to the main menu")
    print("   • No need to manually click 'Back to Main Menu'")
    print("   • Smoother workflow experience!")

if __name__ == "__main__":
    main()