"""
Core modules for photo processing functionality.
"""

from .photo_processor import PhotoProcessor
from .detectors import BlurDetector, DuplicateDetector, FaceDetector

__all__ = ['PhotoProcessor', 'BlurDetector', 'DuplicateDetector', 'FaceDetector']
