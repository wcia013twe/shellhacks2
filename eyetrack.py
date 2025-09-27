from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v2
import cv2

# Initialize gesture engine and video capture
gestures = EyeGestures_v2()
cap = VideoCapture(0)  # Use DirectShow backend  
calibrate = True
screen_width = 500
screen_height= 500

# Process each frame    npm create vite@latest my-vite-app
while True:
  ret, frame = cap.read()
  event, cevent = gestures.step(frame,
    calibrate,
    screen_width,
    screen_height,
    context="my_context")

  if event:
    cursor_x, cursor_y = event.point[0], event.point[1]
    fixation = event.fixation
    # calibration_radius: radius for data collection during calibration