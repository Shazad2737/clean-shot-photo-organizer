#!/usr/bin/env python3
"""
Simple launcher for CLEAN SHOT Photo Organizer.
This script handles all the import path issues.
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the CLEAN SHOT application."""
    print("🚀 Starting CLEAN SHOT Photo Organizer...")
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    src_dir = script_dir / "src"
    
    # Add src directory to Python path
    sys.path.insert(0, str(src_dir))
    
    try:
        # Import and run the application
        from main import main as app_main
        app_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you're in the project directory")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check that all files are present")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure all dependencies are installed")
        print("2. Check that you have a display (GUI applications need a screen)")
        sys.exit(1)

if __name__ == "__main__":
    main()
