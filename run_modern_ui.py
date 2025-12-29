#!/usr/bin/env python3
"""
Launch the Modern Redesigned CLEAN SHOT Photo Organizer UI.

This is the premium redesigned interface featuring:
- Sidebar navigation
- Drag & drop folder selection
- Live photo preview grid
- Real-time statistics panel
- Glassmorphism design elements
"""

import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

# Suppress TensorFlow warnings
os.environ["TF_USE_LEGACY_KERAS"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)


def main():
    from gui.modern_main_window import run_modern_app
    run_modern_app()


if __name__ == "__main__":
    main()
