#!/usr/bin/env python3
"""
Test script to verify eye tracker integration works correctly
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_eye_tracker_import():
    """Test that EyeTracker can be imported correctly"""
    print("🔍 Testing EyeTracker import...")
    
    try:
        from src.eye_tracking.EyeTracker import EyeTracker
        print("✅ EyeTracker imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import EyeTracker: {e}")
        return False

def test_integrated_test_runner_import():
    """Test that IntegratedTestManager can be imported correctly"""
    print("🔍 Testing IntegratedTestManager import...")
    
    try:
        from src.gui.integrated_test_runner import IntegratedTestManager
        print("✅ IntegratedTestManager imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import IntegratedTestManager: {e}")
        return False

def test_integration_creation():
    """Test that we can create the integration objects"""
    print("🔍 Testing integration object creation...")
    
    try:
        from src.eye_tracking.EyeTracker import EyeTracker
        from src.gui.integrated_test_runner import IntegratedTestManager
        
        # Test data
        test_data = {
            'filename': 'test',
            'url': 'https://google.com',
            'duration': '2'
        }
        
        # Create eye tracker (don't calibrate)
        tracker = EyeTracker()
        tracker.is_calibrated = True  # Simulate calibration
        print("✅ EyeTracker created")
        
        # Create test manager with eye tracker
        test_manager = IntegratedTestManager(test_data, eye_tracker=tracker)
        print("✅ IntegratedTestManager created with eye tracker")
        
        # Cleanup
        if hasattr(tracker, 'cap') and tracker.cap:
            try:
                tracker.cap.release()
            except:
                pass
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create integration objects: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🧪 Eye Tracker Integration Test")
    print("=" * 50)
    
    tests = [
        test_eye_tracker_import,
        test_integrated_test_runner_import,
        test_integration_creation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
            print()
    
    print("=" * 50)
    if all(results):
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Integration should work correctly:")
        print("   • EyeTracker imports successfully")
        print("   • IntegratedTestManager imports successfully") 
        print("   • Objects can be created together")
        print("\n🚀 The 'test integration not available' error should be fixed!")
        
    else:
        print("❌ SOME TESTS FAILED!")
        print("   Check the error messages above for details")
        
        failed_tests = []
        test_names = ["EyeTracker import", "IntegratedTestManager import", "Integration creation"]
        for i, result in enumerate(results):
            if not result:
                failed_tests.append(test_names[i])
        
        print(f"   Failed tests: {', '.join(failed_tests)}")

if __name__ == "__main__":
    main()