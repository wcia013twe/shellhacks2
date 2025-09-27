"""
Eye tracking module initialization.
"""

# Lazy-loaded EyeTracker to avoid importing eyeGestures until needed
class EyeTracker:
    """Lazy-loaded EyeTracker that only imports dependencies when actually used."""
    
    def __init__(self):
        """Initialize without loading dependencies."""
        print("🎯 EyeTracker initialized (dependencies will load when started)")
    
    def start(self):
        """Start the eye tracking system - loads dependencies only when called."""
        print("📦 Loading eye tracking dependencies...")
        try:
            # Import and run the eye tracker script
            from . import eye_tracker
            # The eye_tracker module will execute its main loop
            print("✅ Eye tracker dependencies loaded and running")
        except ImportError as e:
            print(f"❌ Eye tracking dependencies not available: {e}")
            print("💡 Install with: pip install eyeGestures")
        except Exception as e:
            print(f"❌ Error starting eye tracker: {e}")

__all__ = ['EyeTracker']