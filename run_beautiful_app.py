#!/usr/bin/env python3
"""
Beautiful launcher for CLEAN SHOT Photo Organizer with stunning UI.
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the beautiful CLEAN SHOT application."""
    print("🎨 Starting CLEAN SHOT Photo Organizer with Beautiful UI...")
    print("✨ Loading stunning modern interface...")
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    src_dir = script_dir / "src"
    
    # Add src directory to Python path
    sys.path.insert(0, str(src_dir))
    
    try:
        # Import and run the beautiful application
        from PySide6.QtWidgets import QApplication
        from gui.beautiful_main_window import BeautifulMainWindow
        
        # Create application with beautiful properties
        app = QApplication(sys.argv)
        app.setApplicationName("CLEAN SHOT")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("Clean Shot")
        
        # Set beautiful application icon and properties
        app.setStyle('Fusion')  # Use Fusion style for modern look
        
        # Create and show beautiful main window
        window = BeautifulMainWindow()
        window.show()
        
        print("🎉 Beautiful UI loaded successfully!")
        print("✨ Enjoy the stunning modern interface!")
        
        # Run the beautiful application
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you're in the project directory")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check that all files are present")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting beautiful application: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure all dependencies are installed")
        print("2. Check that you have a display (GUI applications need a screen)")
        print("3. Try running: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
