"""
Example usage of the EyeTracker class
"""

import sys
import os

# Add the eye_tracking module to path
sys.path.append('c:/Code/Shell 2025/project2/shellhacks2/src/eye_tracking')

from EyeTracker import EyeTracker


def example_basic_usage():
    """Basic example: calibrate then track"""
    
    # Create tracker instance
    tracker = EyeTracker()
    
    try:
        # Calibrate with 25 points
        print("Starting calibration...")
        success = tracker.recalibrate(25)
        
        if success:
            print("Calibration successful! Starting tracking...")
            
            # Start continuous tracking (prints X,Y coordinates)
            tracker.track()
        else:
            print("Calibration failed or cancelled")
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        tracker.cleanup()


def example_single_readings():
    """Example: Get individual gaze readings"""
    
    tracker = EyeTracker()
    
    try:
        # Calibrate first
        if tracker.recalibrate(20):
            print("Getting 10 gaze readings...")
            
            for i in range(10):
                gaze = tracker.get_gaze()
                
                if gaze:
                    x, y = gaze['position']
                    print(f"Reading {i+1}: Gaze at ({x:.0f}, {y:.0f})")
                else:
                    print(f"Reading {i+1}: No gaze data")
                
                import time
                time.sleep(1)  # Wait 1 second between readings
                
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        tracker.cleanup()


def example_use_in_another_script():
    """Example: How to use EyeTracker in your own application"""
    
    # This is how you'd use it in your own Python script
    tracker = EyeTracker()
    
    # Calibrate once
    tracker.recalibrate(25)
    
    # Then use gaze data in your application
    while True:
        gaze = tracker.get_gaze()
        
        if gaze:
            x, y = gaze['position']
            
            # Your application logic here
            if x < 500:
                print("Looking left")
            elif x > 1400:
                print("Looking right")
            else:
                print("Looking center")
        
        # Your main application loop continues...
        import time
        time.sleep(0.1)


if __name__ == "__main__":
    print("🎯 EyeTracker Class Examples")
    print("=" * 40)
    print("1. Basic Usage (calibrate + continuous tracking)")
    print("2. Single Readings (calibrate + individual readings)")
    print("3. Integration Example (how to use in your app)")
    
    choice = input("\nChoose example (1-3): ").strip()
    
    if choice == "1":
        example_basic_usage()
    elif choice == "2":
        example_single_readings()
    elif choice == "3":
        example_use_in_another_script()
    else:
        print("Invalid choice, running basic usage...")
        example_basic_usage()