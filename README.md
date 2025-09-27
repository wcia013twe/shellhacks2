# Simple Browser Launcher & Eye Tracker

This project consists of two separate, independent applications for web browsing and eye tracking.

## 📦 Installation

### Option 1: Install Everything

```bash
pip install -r requirements.txt  # Full freeze with exact versions
```

### Option 2: Install Minimal Dependencies

```bash
pip install -r requirements-minimal.txt  # Only essential packages
```

### Option 3: Install by Component

```bash
# For browser only
pip install pywebview PyQt5

# For eye tracking only
pip install eyeGestures opencv-python pygame numpy scikit-learn mediapipe
```

## Features

- **Time-Limited Browsing**: Set automatic browser close timers
- **Eye Tracking Integration**: Monitor user engagement (experimental)
- **Modular Architecture**: Clean separation of concerns
- **Easy Extension**: Add new features easily

## Project Structure

```
shellhacks2/
├── src/                    # Main source code
│   ├── gui/               # User interface components
│   │   ├── __init__.py
│   │   └── main_window.py # Main application window
│   ├── timer/             # Timer functionality
│   │   ├── __init__.py
│   │   └── browser_timer.py # Browser session timers
│   ├── browser/           # Browser management
│   │   ├── __init__.py
│   │   └── browser_manager.py # Browser launching and control
│   ├── eye_tracking/      # Eye tracking functionality
│   │   ├── __init__.py
│   │   └── eye_tracker.py # Eye tracking implementation
│   └── __init__.py
├── main.py               # Application entry point
├── gui.py               # Legacy monolithic file (deprecated)
├── browser.py           # Legacy compatibility wrapper
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:

```bash
python main.py
```

### Features:

1. **URL Input**: Enter any website URL
2. **Time Limit**: Set browsing session duration (0 = unlimited)
3. **Eye Tracking**: Enable experimental eye tracking monitoring
4. **Quick Links**: Fast access to popular sites

## Modules

### GUI Module (`src/gui/`)

- Main application window and user interface
- Coordinates all other modules
- Handles user interactions

### Timer Module (`src/timer/`)

- Manages browsing session timers
- Automatic browser closure
- Real-time countdown display

### Browser Module (`src/browser/`)

- Browser window creation and management
- URL validation and launching
- Cross-platform browser support

### Eye Tracking Module (`src/eye_tracking/`)

- Eye movement monitoring (placeholder implementation)
- Gaze pattern analysis
- User engagement metrics

## Development

### Adding New Features

The modular structure makes it easy to add new functionality:

1. Create a new module in `src/`
2. Add it to `src/__init__.py`
3. Import and use in `src/gui/main_window.py`

### Eye Tracking Implementation

To implement real eye tracking:

1. Uncomment dependencies in `requirements.txt`
2. Install: `pip install opencv-python mediapipe numpy`
3. Implement actual eye tracking in `src/eye_tracking/eye_tracker.py`

Example technologies:

- **OpenCV + MediaPipe**: Computer vision-based tracking
- **Tobii Eye Tracker**: Hardware-based professional tracking
- **WebGazer.js**: Web-based eye tracking

## Legacy Files

- `gui.py`: Original monolithic implementation (deprecated)
- `browser.py`: Compatibility wrapper for old references

Use `main.py` for the new modular version.
