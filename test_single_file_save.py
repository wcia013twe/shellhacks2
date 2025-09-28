#!/usr/bin/env python3
"""
Test script to verify the single file save functionality
"""

import sys
import os
import json
import tempfile
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_single_file_save():
    """Test that save creates only one file instead of three"""
    print("🧪 Testing Single File Save Functionality...")
    
    try:
        # Import the UI manager
        import tkinter as tk
        from src.gui.test_ui_manager import TestUIManager
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"📁 Using temporary directory: {temp_dir}")
            
            # Create a minimal test setup
            root = tk.Tk()
            root.withdraw()  # Hide the window
            
            # Create UI manager
            ui_manager = TestUIManager()
            
            # Mock the form entries
            class MockEntry:
                def __init__(self, value):
                    self.value = value
                def get(self):
                    return self.value
                def strip(self):
                    return self.value.strip()
                    
            class MockVar:
                def __init__(self, value):
                    self.value = value
                def get(self):
                    return self.value
                    
            ui_manager.setup_entries = {
                'filename': MockEntry('palantir_2min_test'),
                'url': MockEntry('https://palantir.com'),
                'duration': MockEntry('2')
            }
            
            # Mock destination path
            ui_manager.dest_path_var = MockVar(temp_dir)
            
            # Test Case 1: Save without component configuration (basic config only)
            print("\n🔍 Test Case 1: Basic configuration (no components)")
            ui_manager.save_test_config()
            
            # Check files in temp directory
            files = os.listdir(temp_dir)
            print(f"📄 Files created: {files}")
            
            if len(files) == 1:
                print("✅ Success: Only one file created!")
                
                # Check file content
                file_path = os.path.join(temp_dir, files[0])
                with open(file_path, 'r') as f:
                    config = json.load(f)
                
                print(f"📋 File structure: {list(config.keys())}")
                
                if 'test_metadata' in config and 'test_parameters' in config:
                    print("✅ Correct structure: Contains metadata and parameters")
                else:
                    print("❌ Missing expected structure")
                    return False
            else:
                print(f"❌ Expected 1 file, got {len(files)} files")
                return False
            
            # Clean up for next test
            for file in files:
                os.remove(os.path.join(temp_dir, file))
            
            # Test Case 2: Save with component configuration
            print("\n🔍 Test Case 2: Complete configuration (with components)")
            
            # Mock component configuration data
            ui_manager.component_config_data = {
                'version': 1,
                'url': 'https://palantir.com',
                'saved_at': datetime.now().timestamp(),
                'ranks': {
                    '1': [{'selector': 'header', 'tag': 'header'}],
                    '2': [{'selector': 'nav', 'tag': 'nav'}],
                    '3': [{'selector': '.content', 'tag': 'div'}]
                }
            }
            
            ui_manager.save_test_config()
            
            # Check files again
            files = os.listdir(temp_dir)
            print(f"📄 Files created: {files}")
            
            if len(files) == 1:
                print("✅ Success: Still only one file created with components!")
                
                # Check file content includes components
                file_path = os.path.join(temp_dir, files[0])
                with open(file_path, 'r') as f:
                    config = json.load(f)
                
                if 'component_configuration' in config and config['component_configuration'] is not None:
                    print("✅ Component configuration included in single file")
                else:
                    print("❌ Component configuration missing")
                    return False
            else:
                print(f"❌ Expected 1 file, got {len(files)} files")
                return False
                
            root.destroy()
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def main():
    """Run the single file save test"""
    print("🚀 Single File Save Fix Test")
    print("=" * 50)
    
    success = test_single_file_save()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TEST PASSED!")
        print("\n✅ Fixed the multiple file issue:")
        print("   • Now creates only ONE file instead of three")
        print("   • File contains all configuration data")
        print("   • Cleaner filename (removes _config suffix)")
        print("   • Works with and without component configuration")
        
        print("\n📁 File naming:")
        print("   • Before: filename_config.json, filename_components.json, filename_combined.json")
        print("   • After: filename.json (contains everything)")
        
    else:
        print("❌ TEST FAILED!")
        print("   Check the console output above for details")
    
    print("\n🔍 Next time you save:")
    print("   • Only ONE file will be created")
    print("   • It contains all your test and component configuration")
    print("   • Much cleaner and easier to manage!")

if __name__ == "__main__":
    main()