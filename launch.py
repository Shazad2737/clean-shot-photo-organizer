#!/usr/bin/env python3
"""
Launcher script for CLEAN SHOT Photo Organizer.
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the CLEAN SHOT application."""
    # Add src to Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        from main import main as app_main
        print("🚀 Starting CLEAN SHOT Photo Organizer...")
        app_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
