#!/usr/bin/env python3
"""
Standalone Eye Tracker Script

Run this script to start the eye tracking calibration system independently.
This is separate from the main browser launcher application.
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main function to run the standalone eye tracker."""
    print("=" * 60)
    print("🎯 STANDALONE EYE TRACKER")
    print("=" * 60)
    print()
    print("This will start the eye tracking calibration system.")
    print("Make sure you have a webcam connected and working.")
    print()
    print("Controls during calibration:")
    print("  - Look at each red calibration point as it appears")
    print("  - Press 'Q' to quit at any time")
    print("  - Press 'R' to restart calibration (after completion)")
    print("  - Press 'T' to toggle transparency (in tracking mode)")
    print()
    
    # Import and start the eye tracker
    try:
        from eye_tracking import EyeTracker
        
        print("Starting eye tracker...")
        print("🔄 Initializing...")
        
        tracker = EyeTracker()
        tracker.start()
        
    except KeyboardInterrupt:
        print("\n🔄 Eye tracker stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Make sure you have installed the required packages:")
        print("   pip install eyeGestures opencv-python pygame numpy")
        return 1
    except Exception as e:
        print(f"❌ Error running eye tracker: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n✅ Eye tracker session complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())