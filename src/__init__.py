"""
Source module initialization.
"""

# Import all main components
from .gui import SimpleBrowserLauncher
from .timer import BrowserTimer
from .browser import BrowserManager
from .eye_tracking import EyeTracker

__all__ = [
    'SimpleBrowserLauncher',
    'BrowserTimer', 
    'BrowserManager',
    'EyeTracker'
]