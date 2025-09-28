"""
Test UI Manager Application

This is the main entry point for the Test UI Manager application.
It provides a comprehensive interface for creating, configuring, and managing tests.

Features:
- Test configuration setup with JSON export
- Browser-based component importance ranking
- Element selection with Alt+Click functionality  
- Combined configuration file generation
- Test execution and management
- Modular architecture for easy extension
"""

import sys
import os

# Add the src directory to the path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.test_ui_manager import TestUIManager


def main():
    """Main function to launch the Test UI Manager."""
    print("🚀 Launching Test UI Manager...")
    print("Features:")
    print("  • Title Screen with 3 main options")
    print("  • Setup Test: Create new test configurations")
    print("  • Load Test: Load existing test profiles")
    print("  • User Start Test: User-friendly test launcher")
    print("  • Post Test: After completion screen")
    print("  • Process Reports: Analysis placeholder")
    print("  • Browser-based component configuration with Alt+Click ranking")
    print("  • Flat JSON structure export for testing")
    print("\n" + "="*50)
    
    try:
        app = TestUIManager()
        app.run()
    except Exception as e:
        print(f"❌ Failed to launch Test UI Manager: {e}")
        print("💡 Make sure all dependencies are installed and Chrome is available")
        sys.exit(1)


if __name__ == "__main__":
    main()