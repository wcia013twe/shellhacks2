# Eye Tracking Test System - UI Documentation

## Overview

The Eye Tracking Test System now features a comprehensive multi-screen UI system built with tkinter that provides complete test management capabilities from setup to execution to analysis.

## UI Components Created

### 1. System Launcher (`system_launcher.py`)

**Main entry point** that lets users choose between different interface modes:

- **Comprehensive Test Manager**: Full-featured test management system
- **Simple Browser Launcher**: Original direct browser interface
- **Integration Demo**: Shows integration between new and existing systems

### 2. Comprehensive Test UI Manager (`src/gui/test_ui_manager.py`)

**Complete test management system** with the following screens:

#### Title Screen

- Three main buttons: `Setup Test | Load Test | Process Reports`
- Placeholder image display
- Clean, modern interface design (no status text)

#### Setup Test Screen

- **Direct form access** (no start setup button needed)
- Form fields with updated placeholders:
  - `filename`: "youtube_2min_test"
  - `usershown`: "User friendly test name eg Youtube 2 Minute Test"
  - `URL`: "https://youtube.com"
  - `Duration (minutes only)`: Integer input validation, numeric only
  - `description`: Multi-line text area
- **Configure Component Importance** button (opens popup with sliders)
- **Destination of Profile** with file explorer integration
- Save button and **Back to Main Menu** with unsaved changes warning

#### Load Test Screen

- File browser for `.json` test profiles
- **Test Details** section showing:
  - Filename, user shown name, URL, duration, description
  - Component configuration percentages
  - Profile location
- **Start Test** button (enabled after file selection)

#### User Start Test Screen

- User-friendly display of test information:
  - Large test name display
  - Website URL
  - Test duration
- Instructions for the user
- Placeholder image
- **🚀 Start Test** button

#### Post Test Screen

- "✅ Test Completed Successfully!" message
- Test summary information
- Results preview placeholder
- **Start Another Test** and **Main Menu** buttons

#### Process Reports Screen

- Placeholder for future report processing functionality

### 3. Integrated Test Runner (`src/gui/integrated_test_runner.py`)

**Bridge between new UI and existing browser functionality**:

- `IntegratedTestManager` class that connects test data with browser/timer systems
- `ModifiedMainWindow` that can run standalone or with test configuration
- Full integration with existing Selenium browser and timer functionality

### 4. Original Browser Launcher (`src/gui/main_window.py`)

**Enhanced version** of the original interface:

- Threading integration for proper timer coordination
- Selenium WebDriver support
- All original functionality preserved

## Key Features Implemented

### ✅ UI Requirements Met

- **Title screen** with three main buttons ✓
- **Setup Test** screen with all requested form fields ✓
- **Load Test** screen with file browser and details ✓
- **User Start Test** screen with user-friendly display ✓
- **Post Test** screen for test completion ✓
- **Component importance** configuration dialog ✓
- **File explorer** integration for profile destinations ✓
- **Placeholder images** throughout the interface ✓

### ✅ Technical Features

- **Separate window management** (not in main_window.py) ✓
- **Navigation** between all screens ✓
- **Form validation** and placeholder text handling ✓
- **Integration** with existing browser/timer systems ✓
- **Threading** for non-blocking browser operations ✓
- **Modern tkinter styling** with consistent design ✓
- **Trackpad gesture support** for enhanced user experience ✓

### ✅ Trackpad Gesture Features

- **Two-finger scroll**: Navigate through scrollable content (vertical)
- **Shift + two-finger scroll**: Horizontal scrolling support
- **Ctrl + two-finger scroll**: Pinch-to-zoom window resizing (600x400 to 1400x1000)
- **Two-finger tap**: Context menu with navigation shortcuts
- **Cross-platform support**: Windows, macOS, and Linux trackpad compatibility
- **Smart widget detection**: Automatically finds and scrolls appropriate content areas
- **Enhanced canvas scrolling**: Improved scrolling in setup screen and other scrollable areas

### ✅ Integration Capabilities

- Can launch existing browser system with test configurations
- Preserves all original functionality
- Proper timer coordination with browser sessions
- Selenium WebDriver with no iframe restrictions

## How to Run

### Option 1: Complete System Launcher

```bash
python system_launcher.py
```

Opens interface selector with all three options.

### Option 2: Direct Test Manager

```bash
python test_ui_launcher.py
```

Directly launches the comprehensive test management UI.

### Option 3: Original Browser Launcher

```bash
python main.py
```

Launches the original/enhanced browser interface.

### Option 4: Integration Demo

```bash
python src/gui/integrated_test_runner.py
```

Shows integration example with sample test data.

### Option 5: Trackpad Gesture Demo

```bash
python trackpad_demo.py
```

Interactive demo showcasing all trackpad gesture capabilities.

## File Structure

```
shellhacks2/
├── system_launcher.py              # Main launcher selector
├── test_ui_launcher.py             # Direct test manager launcher
├── main.py                         # Original browser launcher
├── src/
│   ├── gui/
│   │   ├── test_ui_manager.py      # Comprehensive UI manager
│   │   ├── integrated_test_runner.py  # Integration bridge
│   │   └── main_window.py          # Original/enhanced browser UI
│   ├── browser/
│   │   └── browser_manager.py      # Selenium browser integration
│   └── timer/
│       └── browser_timer.py        # Timer functionality
```

## Design Philosophy

The UI system follows these principles:

1. **Progressive Enhancement**: Original functionality is preserved and enhanced
2. **Modular Design**: Each screen is self-contained and reusable
3. **User Experience**: Clear navigation, placeholder text, and visual feedback
4. **Integration Ready**: New UI can seamlessly use existing browser/timer systems
5. **Extensible**: Easy to add new screens or modify existing ones

## Future Enhancements

The UI framework supports easy addition of:

- Real JSON file save/load functionality
- Actual eye tracking data integration
- Results visualization and analysis
- Advanced component configuration
- User preferences and settings
- Multi-language support

All UI components are designed as placeholders for the logic you mentioned not to implement, making it easy to add the actual data handling, file operations, and eye tracking integration later.
