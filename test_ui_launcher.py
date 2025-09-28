"""
Launcher for the new Test UI Manager

This script launches the comprehensive test management UI
as requested by the user.
"""

import sys
import os

# Add the src directory to the path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.test_ui_manager import TestUIManager

if __name__ == "__main__":
    print("🚀 Launching Test UI Manager...")
    print("Features:")
    print("  • Title Screen with 3 main options")
    print("  • Setup Test: Create new test configurations")
    print("  • Load Test: Load existing test profiles")
    print("  • User Start Test: User-friendly test launcher")
    print("  • Post Test: After completion screen")
    print("  • Process Reports: Analysis placeholder")
    print("  • Placeholder images throughout")
    print("\n" + "="*50)
    
    app = TestUIManager()
    app.run()