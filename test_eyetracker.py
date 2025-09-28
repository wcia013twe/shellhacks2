"""
Simple EyeTracker Test - Handle compatibility issues
"""

import sys
import os
import warnings

# Suppress all the annoying warnings
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress all TensorFlow messages
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN

# Add path
sys.path.append('src/eye_tracking')

def test_eyetracker():
    """Test the EyeTracker with better error handling"""
    
    print("🎯 Testing EyeTracker...")
    print("=" * 40)
    
    try:
        from EyeTracker import EyeTracker
        
        print("✅ EyeTracker imported successfully")
        
        # Create tracker
        tracker = EyeTracker()
        print("✅ EyeTracker initialized")
        
        # Test calibration
        print("\n🎯 Starting calibration test...")
        print("   Look for the fullscreen window with blue/yellow circles")
        print("   Press ESC or Q to cancel if needed")
        
        success = tracker.recalibrate()  # Start with fewer points for testing
        
        if success:
            print("✅ Calibration completed!")
            
            print("\n👁️  Testing gaze tracking...")
            print("   Getting 5 gaze readings...")
            i = 0
            while 1:
                i += 1
                gaze = tracker.get_gaze()
                if gaze:
                    x, y = gaze['position']
                    print(f"   Reading {i+1}: Gaze at ({x:.0f}, {y:.0f})")
                else:
                    print(f"   Reading {i+1}: No gaze data")
                
                import time
                time.sleep(1)
                
        else:
            print("❌ Calibration was cancelled or failed")
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure eyeGestures is installed properly")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("   This might be a compatibility issue")
        
    finally:
        try:
            tracker.cleanup()
        except:
            pass
        print("\n🧹 Cleanup completed")


if __name__ == "__main__":
    test_eyetracker()