"""
Simple Browser Launcher Application

This is the main entry point for the Simple Browser Launcher application.
It imports and runs the GUI from the modular src package.

Features:
- Browser launching with time limits
- Timer-based browsing sessions
- Modular architecture for easy extension
"""

from src.gui import SimpleBrowserLauncher


def main():
    """Main function to run the browser launcher application."""
    print("Starting Simple Browser Launcher...")
    print("Features: Time-limited browsing, Timer-based sessions")
    
    app = SimpleBrowserLauncher()
    app.run()


if __name__ == "__main__":
    main()