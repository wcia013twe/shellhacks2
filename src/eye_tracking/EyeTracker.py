"""
EyeTracker Class - Unified eye tracking with calibration and tracking
"""

import os
import sys
import cv2
import pygame
import numpy as np
import time
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN for consistency

# Add eyeGestures path
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}/..')

try:
    from eyeGestures.utils import VideoCapture
    from eyeGestures import EyeGestures_v3
except ImportError as e:
    print(f"❌ Error importing eyeGestures: {e}")
    print("Make sure the eyeGestures library is properly installed")
    sys.exit(1)


class EyeTracker:
    """
    Unified EyeTracker class that handles calibration and tracking
    
    Usage:
        tracker = EyeTracker()
        tracker.recalibrate(25)  # Calibrate with 25 points
        tracker.track()          # Print X,Y coordinates continuously
    """
    
    def __init__(self):
        """Initialize the eye tracker"""
        print("🔧 Initializing EyeTracker...")
        
        try:
            # Initialize pygame for calibration window
            pygame.init()
            pygame.font.init()
            
            # Get screen dimensions
            screen_info = pygame.display.Info()
            self.screen_width = screen_info.current_w
            self.screen_height = screen_info.current_h
            
            # Initialize EyeGestures and camera with error handling
            print("📷 Initializing camera and eye tracking...")
            self.gestures = EyeGestures_v3()
            self.cap = VideoCapture(0)
            
        except Exception as e:
            print(f"❌ Error during initialization: {e}")
            print("🔧 Trying alternative initialization...")
            try:
                # Alternative initialization without some features
                self.gestures = EyeGestures_v3()
                self.cap = VideoCapture(0)
            except Exception as e2:
                print(f"❌ Critical error: {e2}")
                raise
        
        # Calibration state
        self.calibration_map = None
        self.n_points = 0
        self.is_calibrated = False
        
        # Colors for pygame
        self.RED = (255, 0, 100)
        self.BLUE = (100, 0, 255)
        self.GREEN = (0, 255, 0)
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 255, 0)  # For eye tracking indicator
        
        # Timing settings
        self.CALIBRATION_DURATION = 1.5  # seconds per calibration point
        
        # Learning parameters
        self.LEARNING_RATE = 0.8
        self.REGULARIZATION = 0.1
        
        print("✅ EyeTracker initialized")
    
    
    def recalibrate(self, num_points=25):
        """
        Calibrate the eye tracker with specified number of points
        
        Args:
            num_points (int): Number of calibration points (minimum 12)
            
        Returns:
            bool: True if calibration successful, False if cancelled
        """
        print(f"🎯 Starting calibration with {num_points} points...")
        
        # Generate calibration points
        self._generate_calibration_points(num_points)
        
        # Run calibration window
        success = self._run_calibration_window()
        
        if success:
            self.is_calibrated = True
            print("✅ Calibration completed successfully!")
        else:
            print("❌ Calibration cancelled or failed")
            
        return success
    
    
    def _generate_calibration_points(self, num_points):
        """Generate calibration points with guaranteed corner/edge coverage"""
        
        # Ensure minimum points
        # if num_points < 12:
        #     num_points = 12
        #     print(f"⚠️  Minimum 12 points required. Using {num_points} points.")
        
        # Essential points: 4 corners + 4 edge midpoints + center = 9 points
        essential_points = [
            # 4 corners
            [0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0],
            # 4 edge midpoints
            [0.5, 0.0], [1.0, 0.5], [0.5, 1.0], [0.0, 0.5],
            # Center
            [0.5, 0.5]
        ]
        
        # Calculate remaining points
        remaining_points = num_points - len(essential_points)
        
        if remaining_points > 0:
            # Generate additional strategic points
            if remaining_points <= 7:  # 16 points total
                additional_points = [
                    [0.25, 0.25], [0.75, 0.25], [0.25, 0.75], [0.75, 0.75],
                    [0.25, 0.5], [0.75, 0.5], [0.5, 0.25]
                ][:remaining_points]
            elif remaining_points <= 15:  # 20-24 points total
                additional_points = [
                    [0.25, 0.25], [0.75, 0.25], [0.25, 0.75], [0.75, 0.75],
                    [0.25, 0.5], [0.75, 0.5], [0.5, 0.25], [0.5, 0.75],
                    [0.15, 0.15], [0.85, 0.15], [0.15, 0.85], [0.85, 0.85],
                    [0.33, 0.33], [0.67, 0.33], [0.33, 0.67]
                ][:remaining_points]
            else:  # 25+ points
                additional_points = []
                step = 0.2 if remaining_points < 25 else 0.15
                for x in np.arange(0.15, 0.95, step):
                    for y in np.arange(0.15, 0.95, step):
                        if len(additional_points) < remaining_points:
                            point = [round(x, 2), round(y, 2)]
                            if not any(abs(point[0] - ep[0]) < 0.1 and abs(point[1] - ep[1]) < 0.1 
                                     for ep in essential_points):
                                additional_points.append(point)
            
            all_points = essential_points + additional_points[:remaining_points]
        else:
            all_points = essential_points
        
        # Convert to numpy array and randomize
        self.calibration_map = np.array(all_points)
        np.random.shuffle(self.calibration_map)
        self.n_points = len(self.calibration_map)
        
        # Upload to gestures system
        self.gestures.uploadCalibrationMap(self.calibration_map, context="tracker")
        self.gestures.setFixation(1.0)
        
        print(f"📍 Generated {self.n_points} calibration points")
    
    
    def _run_calibration_window(self):
        """Run the interactive calibration window"""
        
        # Set up pygame window with fullscreen and focus
        screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("EyeTracker Calibration")
        
        # Bring window to front without forcing always-on-top
        # import os
        # if os.name == 'nt':  # Windows
        #     try:
        #         import ctypes
        #         hwnd = pygame.display.get_wm_info()["window"]
        #         # Just bring to front and give focus, don't make always-on-top
        #         ctypes.windll.user32.SetForegroundWindow(hwnd)
        #         ctypes.windll.user32.BringWindowToTop(hwnd)
        #         # Activate the window to ensure it has focus
        #         ctypes.windll.user32.SetActiveWindow(hwnd)
        #     except:
        #         pass
        
        bold_font = pygame.font.Font(None, 48)
        bold_font.set_bold(True)
        
        # Calibration state
        iterator = 0
        prev_x, prev_y = 0, 0
        calibration_start_time = 0
        calibration_point_displayed = False
        
        clock = pygame.time.Clock()
        calibration_running = True
        
        print(f"👁️  Calibration window opened. Look at each blue circle for {self.CALIBRATION_DURATION} seconds.")
        print("    Press ESC to cancel calibration")
        
        while calibration_running and iterator < self.n_points:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    calibration_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        print("❌ Calibration cancelled by user")
                        pygame.display.quit()
                        pygame.quit()
                        return False
            
            # Get camera frame
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.flip(frame, axis=1)
            
            # Run calibration step with error handling
            try:
                event_result, calibration = self.gestures.step(
                    frame, True, self.screen_width, self.screen_height, context="tracker"
                )
                
                if event_result is None or calibration is None:
                    continue
                    
            except Exception as e:
                print(f"⚠️  Eye tracking step error: {e}")
                continue
            
            # Clear screen
            screen.fill((0, 0, 0))
            
            # Display camera feed (small preview)
            screen.blit(
                pygame.surfarray.make_surface(np.rot90(event_result.sub_frame)),
                (0, 0)
            )
            
            # Calibration timing logic
            current_time = pygame.time.get_ticks() / 1000.0
            
            # Check for new calibration point
            if calibration.point[0] != prev_x or calibration.point[1] != prev_y:
                if not calibration_point_displayed:
                    calibration_start_time = current_time
                    calibration_point_displayed = True
                    prev_x, prev_y = calibration.point[0], calibration.point[1]
                    print(f"📍 Point {iterator + 1}/{self.n_points} - Look at the blue circle")
            
            # Check if time elapsed for this point
            if calibration_point_displayed and (current_time - calibration_start_time >= self.CALIBRATION_DURATION):
                iterator += 1
                calibration_point_displayed = False
                print(f"✓ Point {iterator}/{self.n_points} completed")
            
            # Draw yellow circle showing where eyes are currently looking
            if event_result.point is not None:
                pygame.draw.circle(screen, self.YELLOW, event_result.point, 15)
                # Add small outline for visibility
                pygame.draw.circle(screen, self.WHITE, event_result.point, 15, 2)
            
            # Draw calibration target (blue circle)
            pygame.draw.circle(screen, self.BLUE, calibration.point, 40)
            
            # Show progress
            progress_text = bold_font.render(f"{iterator}/{self.n_points}", True, self.WHITE)
            progress_rect = progress_text.get_rect(center=calibration.point)
            screen.blit(progress_text, progress_rect)
            
 
            # Show gaze tracking info
            gaze_x, gaze_y = event_result.point
           
            
            # Show instructions
            instruction_font = pygame.font.SysFont('Arial', 20)
            instructions = [
                "Look at the BLUE circle to calibrate",
                "YELLOW circle shows where your eyes are tracked", 
                "Press ESC or Q to cancel calibration"
            ]
            for i, instruction in enumerate(instructions):
                text = instruction_font.render(instruction, True, self.WHITE)
                screen.blit(text, (10, self.screen_height - 80 + i * 25))
            
            pygame.display.flip()
            clock.tick(60)
        
        # Clean up pygame display
        pygame.display.quit()
        
        return iterator >= self.n_points
    
    
    def track(self, print_interval=5, debug=False):
        """
        Start continuous gaze tracking and print X,Y coordinates
        
        Args:
            print_interval (int): Print every N frames to avoid spam
            debug (bool): If True, shows visual debug window with gaze circle
        """
        if not self.is_calibrated:
            print("⚠️  Eye tracker not calibrated! Call recalibrate() first.")
            return
        
        print("👁️  Starting gaze tracking...")
        if debug:
            print("    🐛 Debug mode: Visual window will show gaze circle")
            print("    Press ESC or Q to stop, Ctrl+C for emergency stop")
        else:
            print("    Press Ctrl+C to stop")
        print("    Gaze coordinates (X, Y):")
        print("-" * 40)
        
        # Initialize debug window if requested
        debug_screen = None
        if debug:
            # Create transparent overlay window
            import os
            if os.name == 'nt':  # Windows
                os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
            
            debug_screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.NOFRAME)
            pygame.display.set_caption("EyeTracker Debug - Gaze Overlay")
            
            # Set a magenta colorkey for transparency
            magenta = (255, 0, 255)  # Bright magenta - will be transparent
            debug_screen.set_colorkey(magenta)
            
            # Make window transparent and always on top (Windows)
            if os.name == 'nt':
                try:
                    import ctypes
                    from ctypes import wintypes
                    hwnd = pygame.display.get_wm_info()["window"]
                    
                    # Make window layered for transparency
                    ctypes.windll.user32.SetWindowLongW(hwnd, -20, 0x80000 | 0x20)  # WS_EX_LAYERED | WS_EX_TRANSPARENT
                    # Use colorkey transparency - magenta becomes fully transparent
                    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0xFF00FF, 0, 1)  # Magenta colorkey
                    
                    # Make it topmost but click-through
                    ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)  # TOPMOST | NOMOVE | NOSIZE
                except:
                    print("⚠️  Could not create transparent overlay, using regular window")
            
            # Store the magenta color for clearing
            self.transparent_color = magenta
            
            debug_font = pygame.font.SysFont('Arial', 16)
        
        try:
            frame_count = 0
            clock = pygame.time.Clock() if debug else None
            
            while True:
                gaze = self.get_gaze()
                
                if gaze is not None:
                    frame_count += 1
                    x, y = gaze['position']
                    
                    # Print every N frames
                    if frame_count % print_interval == 0:
                        print(f"Gaze: ({x:4.0f}, {y:4.0f}) | "
                              f"Fixation: {gaze['fixation']} | "
                              f"Algorithm: {gaze['algorithm']}")
                    
                    # Debug visualization - transparent overlay with yellow gaze circle
                    if debug and debug_screen is not None:
                        # Handle pygame events
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                raise KeyboardInterrupt
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                                    raise KeyboardInterrupt
                        
                        # Clear screen with transparent magenta (will be invisible)
                        debug_screen.fill(self.transparent_color)
                        
                        # Only draw the gaze point - simple yellow circle
                        pygame.draw.circle(debug_screen, self.YELLOW, (int(x), int(y)), 20)
                        # Add subtle white outline for better visibility
                        pygame.draw.circle(debug_screen, self.WHITE, (int(x), int(y)), 20, 2)
                        
                        # Optional: Small coordinate text in corner (minimal)
                        coord_text = debug_font.render(f"({x:.0f}, {y:.0f})", True, self.WHITE)
                        debug_screen.blit(coord_text, (10, 10))
                        
                        pygame.display.flip()
                        clock.tick(30)  # 30 FPS for debug window
                
                if not debug:
                    time.sleep(0.05)  # 20 FPS for non-debug mode
                
        except KeyboardInterrupt:
            print("\n🛑 Gaze tracking stopped")
        finally:
            if debug and debug_screen is not None:
                pygame.display.quit()
    
    
    def track_debug(self, print_interval=5):
        """
        Convenience method for debug tracking with visual feedback
        
        Args:
            print_interval (int): Print every N frames to avoid spam
        """
        self.track(print_interval=print_interval, debug=True)
    
    
    def get_gaze(self):
        """
        Get current gaze position (single reading)
        
        Returns:
            dict: {'position': (x, y), 'fixation': bool, 'algorithm': str} or None
        """
        if not self.is_calibrated:
            return None
        
        try:
            ret, frame = self.cap.read()
            if not ret:
                return None
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.flip(frame, axis=1)
            
            # Get gaze data (not calibrating)
            event_result, _ = self.gestures.step(
                frame, False, self.screen_width, self.screen_height, context="tracker"
            )
            
            if event_result is not None:
                return {
                    'position': event_result.point,
                    'fixation': event_result.fixation,
                    'algorithm': self.gestures.whichAlgorithm(context="tracker"),
                    'saccades': event_result.saccades
                }
        except Exception as e:
            print(f"❌ Error getting gaze: {e}")
        
        return None
    
    
    def cleanup(self):
        """Clean up resources"""
        try:
            pygame.quit()
        except:
            pass
        print("🧹 EyeTracker cleaned up")


# Example usage
if __name__ == "__main__":
    tracker = EyeTracker()
    
    # Calibrate
    if tracker.recalibrate(25):
        # Start tracking
        tracker.track(debug=True)
    
    # Cleanup
    tracker.cleanup()