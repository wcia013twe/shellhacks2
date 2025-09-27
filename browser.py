"""
Legacy browser launcher - single file version.

This file contains the original single-file implementation.
For the modular version, use main.py which imports from gui.py
"""

# Import the new modular version
from gui import SimpleBrowserLauncher


if __name__ == "__main__":
    print("Running legacy browser.py - consider using main.py for the modular version")
    app = SimpleBrowserLauncher()
    app.run()
