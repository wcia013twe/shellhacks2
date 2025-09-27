"""
Simple Browser Launcher Application

This is the main entry point for the Simple Browser Launcher application.
It imports and runs the GUI from the gui module.
"""

from gui import SimpleBrowserLauncher


def main():
    """Main function to run the browser launcher application."""
    app = SimpleBrowserLauncher()
    app.run()


if __name__ == "__main__":
    main()