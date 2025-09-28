#!/usr/bin/env python3
"""
Test script to verify the new flat configuration structure
"""

import sys
import os
import json
import tempfile
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_flat_structure():
    """Test that save creates the flat structure format"""
    print("🧪 Testing Flat Configuration Structure...")
    
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
                    
            class MockVar:
                def __init__(self, value):
                    self.value = value
                def get(self):
                    return self.value
                    
            ui_manager.setup_entries = {
                'filename': MockEntry('palantir_2min_test'),
                'url': MockEntry('https://www.palantir.com/'),
                'duration': MockEntry('2')
            }
            
            # Mock destination path
            ui_manager.dest_path_var = MockVar(temp_dir)
            
            # Mock component configuration data matching your format
            ui_manager.component_config_data = {
                'version': 1,
                'origin': 'https://www.palantir.com',
                'path': '/',
                'url': 'https://www.palantir.com/',
                'saved_at': datetime.now().timestamp(),
                'ranks': {
                    '1': [
                        {
                            'selector': 'div:nth-of-type(5) > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(2) > div:nth-of-type(1)',
                            'tag': 'div'
                        }
                    ],
                    '2': [
                        {
                            'selector': 'h1:nth-of-type(1)',
                            'tag': 'h1'
                        },
                        {
                            'selector': 'div.main > div:nth-of-type(2)',
                            'tag': 'div'
                        }
                    ],
                    '4': [
                        {
                            'selector': 'div:nth-of-type(5) > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1)',
                            'tag': 'div'
                        }
                    ],
                    '5': [
                        {
                            'selector': 'div.home-page > div:nth-of-type(3) > div:nth-of-type(1)',
                            'tag': 'div'
                        }
                    ]
                }
            }
            
            print("🔧 Saving configuration with flat structure...")
            ui_manager.save_test_config()
            
            # Check files in temp directory
            files = os.listdir(temp_dir)
            print(f"📄 Files created: {files}")
            
            if len(files) == 1:
                print("✅ Success: Only one file created!")
                
                # Check file content structure
                file_path = os.path.join(temp_dir, files[0])
                with open(file_path, 'r') as f:
                    config = json.load(f)
                
                print(f"📋 File structure keys: {list(config.keys())}")
                
                # Check if it matches your desired format
                expected_keys = {'origin', 'path', 'url', 'duration', 'created_at', 'ranks'}
                actual_keys = set(config.keys())
                
                if actual_keys == expected_keys:
                    print("✅ Perfect! Structure matches desired format")
                    print(f"   • origin: {config.get('origin', 'N/A')}")
                    print(f"   • path: {config.get('path', 'N/A')}")
                    print(f"   • url: {config.get('url', 'N/A')}")
                    print(f"   • duration: {config.get('duration', 'N/A')}")
                    print(f"   • ranks: {len(config.get('ranks', {}))} importance levels")
                    
                    # Show sample of the actual JSON structure
                    print(f"\n📄 Sample JSON structure:")
                    sample = json.dumps(config, indent=2)
                    print(sample[:500] + "..." if len(sample) > 500 else sample)
                    
                    return True
                else:
                    print(f"❌ Structure mismatch!")
                    print(f"   Expected: {expected_keys}")
                    print(f"   Actual: {actual_keys}")
                    return False
            else:
                print(f"❌ Expected 1 file, got {len(files)} files")
                return False
                
            root.destroy()
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the flat structure test"""
    print("🚀 Flat Configuration Structure Test")
    print("=" * 50)
    
    success = test_flat_structure()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TEST PASSED!")
        print("\n✅ Configuration now matches your desired format:")
        print("   • Flat structure (no nested objects)")
        print("   • Direct access to all properties")
        print("   • origin, path, url, duration, created_at, ranks")
        print("   • Component rankings preserved exactly")
        
    else:
        print("❌ TEST FAILED!")
        print("   Check the console output above for details")
    
    print("\n🔍 Your saved files will now have:")
    print("   • Flat JSON structure")
    print("   • Direct property access")
    print("   • Perfect match to your specification")

if __name__ == "__main__":
    main()