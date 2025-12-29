# ========== Configuration Management ==========
"""
Application configuration constants and session management.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict

# Image extensions supported by the application
IMAGE_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.bmp', '.webp',
    '.heic', '.heif', '.tiff', '.tif',
    '.raw', '.cr2', '.nef', '.arw', '.orf', '.dng'
)

# Default settings
DEFAULTS = {
    "BLUR_THRESHOLD": 100,
    "SIMILARITY_THRESHOLD": 20,
    "FACE_MATCH_THRESHOLD": 0.85,
    "THUMBNAIL_SIZE": 72,
    "SESSION_FILE": "clean_shot_session.json"
}

# Blur detection presets
BLUR_PRESETS = {
    "Soft": 50,
    "Normal": 100,
    "Strict": 200,
    "Very Strict": 350
}

# Similarity detection presets
SIMILARITY_PRESETS = {
    "Loose": 40,
    "Normal": 20,
    "Strict": 10,
    "Very Strict": 5
}


class ProcessingSession:
    """Manages saving and loading of processing sessions."""
    
    def __init__(self, session_file: str = None):
        self.session_file = session_file or DEFAULTS["SESSION_FILE"]

    def save(self, results: Dict, folder: str, settings: Dict) -> bool:
        """Save processing session to file."""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "folder": folder,
                "results": results,
                "settings": settings
            }
            with open(self.session_file, 'w') as f:
                json.dump(data, f, indent=2)
            logging.info(f"Session saved to {self.session_file}")
            return True
        except Exception as e:
            logging.error(f"Failed to save session: {e}")
            return False

    def load_last(self) -> Optional[Dict]:
        """Load last session from file."""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load session: {e}")
        return None
