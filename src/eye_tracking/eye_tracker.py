import os
import sys
import cv2
import pygame
import numpy as np

# Platform-specific transparency imports
try:
    import ctypes
    from ctypes import wintypes
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

pygame.init()
pygame.font.init()

# Get the display dimensions
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# Set up the screen - start opaque for setup
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Position window at top-left
screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
pygame.display.set_caption("EyeGestures v3 - Camera Setup")
font_size = 48
bold_font = pygame.font.Font(None, font_size)
bold_font.set_bold(True)  # Set the font to bold

def make_window_transparent():
    """Make the pygame window transparent on Windows."""
    if not WINDOWS_AVAILABLE:
        print("⚠️ Transparency not available on this platform")
        return False
    
    try:
        # Get window handle
        hwnd = pygame.display.get_wm_info()["window"]
        
        # Windows API constants
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x00080000
        WS_EX_TRANSPARENT = 0x00000020
        
        # Get current window style
        user32 = ctypes.windll.user32
        current_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        
        # Add layered and transparent styles
        new_style = current_style | WS_EX_LAYERED
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
        
        # Set transparency (0 = fully transparent, 255 = fully opaque)
        user32.SetLayeredWindowAttributes(hwnd, 0, 200, 2)  # 200/255 = ~78% opacity
        
        print("✅ Window transparency enabled")
        return True
        
    except Exception as e:
        print(f"❌ Failed to set transparency: {e}")
        return False

# Note: Window starts opaque for calibration phase

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}/..')

from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v3

gestures = EyeGestures_v3()
cap = VideoCapture(0)

x = np.arange(0, 1.1, 0.2)
y = np.arange(0, 1.1, 0.2)

xx, yy = np.meshgrid(x, y)

# Configuration
max_calibration_points = 20

targets = [
    (0.6,0.3,0.1,0.05,"target_1"),
    (0.8,0.6,0.15,0.1,"target_2"),
    (0.1,0.9,0.1,0.1,"target_3")
]

# Create calibration map with 20 points
calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
n_points = min(len(calibration_map), max_calibration_points)
np.random.shuffle(calibration_map)
calibration_map = calibration_map[:n_points]  # Take exactly 20 points
gestures.uploadCalibrationMap(calibration_map, context="my_context")
gestures.setFixation(1.0)

def switch_to_calibration_mode():
    """Switch from setup to calibration mode."""
    global current_mode
    current_mode = CALIBRATION_MODE
    pygame.display.set_caption("EyeGestures v3 - Calibration Mode")
    print("📷 Face detected! Starting calibration...")
    print("   Look at each red circle as it appears")

def switch_to_tracking_mode():
    """Switch from calibration to transparent tracking mode."""
    global current_mode
    current_mode = TRACKING_MODE
    make_window_transparent()
    pygame.display.set_caption("EyeGestures v3 - Transparent Tracking")
    print("🎯 Calibration complete! Switching to transparent tracking mode")
    print("   Press 'T' to toggle transparency, 'R' to recalibrate, 'Q' to quit")
# Initialize Pygame
# Set up colors
RED = (255, 0, 0)              # Calibration points
YELLOW = (255, 255, 0)         # User gaze during calibration  
PINK = (255, 192, 203)         # Tracking gaze (transparent mode)
BLUE = (100, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)              # Calibration background
WHITE = (255, 255, 255)
TRANSPARENT_BLACK = (0, 0, 0, 0)  # Fully transparent

clock = pygame.time.Clock()

# Application states
SETUP_MODE = "setup"
CALIBRATION_MODE = "calibration"
TRACKING_MODE = "tracking"

# Main application variables
running = True
current_mode = SETUP_MODE  # Start with setup phase
iterator = 0
prev_x = 0
prev_y = 0
calibration_completed = False
face_detected_frames = 0
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:  # Quit with 'Q'
                print("🔄 Shutting down...")
                # Clean up camera
                try:
                    cap.release()
                    print("📷 Camera released")
                except:
                    pass
                # Force quit everything
                pygame.quit()
                import sys
                sys.exit(0)
            elif event.key == pygame.K_SPACE and current_mode == SETUP_MODE:  # Skip setup
                switch_to_calibration_mode()
                print("⏭️ Setup skipped, starting calibration...")
            elif event.key == pygame.K_t and current_mode == TRACKING_MODE:  # Toggle transparency
                make_window_transparent()
                print("🔄 Transparency toggled")
            elif event.key == pygame.K_r:  # Restart from setup
                current_mode = SETUP_MODE
                iterator = 0
                prev_x = prev_y = 0
                face_detected_frames = 0
                # Make window opaque for setup
                if WINDOWS_AVAILABLE:
                    try:
                        hwnd = pygame.display.get_wm_info()["window"]
                        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 255, 2)
                        pygame.display.set_caption("EyeGestures v3 - Camera Setup")
                    except:
                        pass
                print("🔄 Restarting from camera setup...")

    # ========== SETUP MODE (Simple Face Detection) ==========
    if current_mode == SETUP_MODE:
        screen.fill(BLACK)
        
        # Show setup message FIRST, before camera processing
        font = pygame.font.SysFont('Arial', 30)
        text1 = font.render("Setting up camera...", True, WHITE)
        text2 = font.render("Look at the camera", True, WHITE)
        text3 = font.render("Press SPACE to start calibration", True, (150, 150, 150))
        
        screen.blit(text1, (50, screen_height // 2 - 50))
        screen.blit(text2, (50, screen_height // 2))
        screen.blit(text3, (50, screen_height // 2 + 100))
        
        # Update display immediately so user sees the message
        pygame.display.flip()
        
        # Now try camera processing
        try:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = np.flip(frame, axis=1)
                
                # Determine if we're still calibrating
                calibrate = (iterator < n_points and current_mode == CALIBRATION_MODE)
                gaze_event, calibration = gestures.step(frame, calibrate, screen_width, screen_height, context="my_context")
                
                # Check if face detected
                if gaze_event is not None:
                    face_detected_frames += 1
                    if face_detected_frames > 10:  # Much simpler threshold
                        switch_to_calibration_mode()
        except Exception as e:
            # If camera fails, show error message
            error_font = pygame.font.SysFont('Arial', 24)
            error_text = error_font.render("Camera not available - Press SPACE to continue", True, (255, 255, 0))
            screen.blit(error_text, (50, screen_height // 2 + 150))

    # ========== CALIBRATION MODE ==========
    elif current_mode == CALIBRATION_MODE:
        # Black background for calibration
        screen.fill(BLACK)
        
        # Show calibration instructions
        instruction_font = pygame.font.SysFont('Arial', 24)
        instruction_text = instruction_font.render("Look at the red circles - Calibration in progress", True, WHITE)
        screen.blit(instruction_text, (50, 50))
        
        # Show overall progress
        progress_text = bold_font.render(f"Progress: {iterator}/{n_points}", True, WHITE)
        screen.blit(progress_text, (50, 100))
        
        # Process camera for calibration
        try:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = np.flip(frame, axis=1)
                
                # Determine if we're still calibrating
                calibrate = (iterator < n_points and current_mode == CALIBRATION_MODE)
                gaze_event, calibration = gestures.step(frame, calibrate, screen_width, screen_height, context="my_context")
                
                if calibration is not None:
                    # Draw red calibration point
                    pygame.draw.circle(screen, RED, calibration.point, 25)
                    pygame.draw.circle(screen, WHITE, calibration.point, 25, 3)  # White border
                    
                    # Show progress ON the calibration target (current point number)
                    current_point = iterator + 1 if iterator < n_points else n_points
                    progress_on_target = bold_font.render(f"{current_point}", True, WHITE)
                    target_x, target_y = calibration.point
                    text_rect = progress_on_target.get_rect(center=(target_x, target_y))
                    screen.blit(progress_on_target, text_rect)
                    
                    # Show current gaze position in yellow
                    if gaze_event and gaze_event.point is not None:
                        try:
                            gaze_pos = (int(gaze_event.point[0]), int(gaze_event.point[1]))
                            pygame.draw.circle(screen, YELLOW, gaze_pos, 15)
                            pygame.draw.circle(screen, WHITE, gaze_pos, 15, 2)
                        except (IndexError, TypeError):
                            pass  # Skip if point is invalid
                    
                    # Update calibration progress
                    if calibration.point[0] != prev_x or calibration.point[1] != prev_y:
                        iterator += 1
                        prev_x = calibration.point[0]
                        prev_y = calibration.point[1]
                        print(f"📍 Calibration point {iterator}/{n_points} completed")
                        
                        # Check if calibration is complete
                        if iterator >= n_points:
                            switch_to_tracking_mode()
                
        except Exception as e:
            # Show error if camera processing fails
            error_text = instruction_font.render("Camera error - Press R to restart", True, (255, 255, 0))
            screen.blit(error_text, (50, 150))
    
    # ========== TRACKING MODE ==========
    elif current_mode == TRACKING_MODE:
        # Transparent background
        screen.fill(TRANSPARENT_BLACK)
        
        # Process camera for tracking
        try:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = np.flip(frame, axis=1)
                
                # Get gaze tracking
                gaze_event, _ = gestures.step(frame, False, screen_width, screen_height, context="my_context")
                
                # Show transparent pink gaze point
                if gaze_event and gaze_event.point is not None:
                    try:
                        gaze_radius = 25
                        
                        # Get gaze position as integers
                        gaze_x = int(gaze_event.point[0])
                        gaze_y = int(gaze_event.point[1])
                        
                        # Draw semi-transparent pink circle for gaze
                        gaze_surface = pygame.Surface((gaze_radius * 3, gaze_radius * 3), pygame.SRCALPHA)
                        pygame.draw.circle(gaze_surface, (*PINK, 150), (gaze_radius * 1.5, gaze_radius * 1.5), gaze_radius)
                        pygame.draw.circle(gaze_surface, (*WHITE, 200), (gaze_radius * 1.5, gaze_radius * 1.5), gaze_radius, 3)
                        
                        # Position the gaze circle
                        surface_x = gaze_x - gaze_radius * 1.5
                        surface_y = gaze_y - gaze_radius * 1.5
                        screen.blit(gaze_surface, (surface_x, surface_y))
                    except (IndexError, TypeError, ValueError):
                        pass  # Skip if point is invalid
        except Exception as e:
            pass  # Continue even if camera fails
        
        # Optional: Show small status indicator in corner
        status_font = pygame.font.SysFont('Arial', 16)
        status_surface = pygame.Surface((200, 60), pygame.SRCALPHA)
        pygame.draw.rect(status_surface, (*BLACK, 100), (0, 0, 200, 60))
        
        status_text1 = status_font.render("Eye Tracking Active", True, WHITE)
        status_text2 = status_font.render("Press 'R' to recalibrate", True, WHITE)
        status_text3 = status_font.render("Press 'Q' to quit", True, WHITE)
        
        status_surface.blit(status_text1, (10, 5))
        status_surface.blit(status_text2, (10, 22))
        status_surface.blit(status_text3, (10, 39))
        
        screen.blit(status_surface, (screen_width - 210, 10))

    pygame.display.flip()
    clock.tick(60)

# Clean up and quit
print("🧹 Cleaning up...")
try:
    cap.release()
    print("📷 Camera released")
except:
    pass

# Quit Pygame
pygame.quit()
print("✅ Eye tracker closed")
