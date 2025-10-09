"""
Image detection algorithms for blur, duplicates, and faces.
"""

import cv2
import logging
from PIL import Image
import imagehash
import numpy as np
from typing import Tuple, Set, Optional


class BlurDetector:
    """Detects blurry images using Laplacian variance."""
    
    def __init__(self, threshold: int = 100):
        """
        Initialize blur detector.
        
        Args:
            threshold: Laplacian variance threshold below which image is considered blurry
        """
        self.threshold = threshold
    
    def is_blurry(self, image_path: str) -> bool:
        """
        Check if image is blurry using Laplacian variance.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if image is blurry, False otherwise
        """
        try:
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                logging.warning(f"Could not read image: {image_path}")
                return False
            
            laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
            return laplacian_var < self.threshold
        except Exception as e:
            logging.error(f"Blur detection error for {image_path}: {e}")
            return False


class DuplicateDetector:
    """Detects duplicate images using perceptual hashing."""
    
    def __init__(self, similarity_threshold: int = 5, hash_size: int = 16):
        """
        Initialize duplicate detector.
        
        Args:
            similarity_threshold: Maximum hash difference to consider images similar
            hash_size: Size of the perceptual hash
        """
        self.similarity_threshold = similarity_threshold
        self.hash_size = hash_size
        self.seen_hashes: Set[imagehash.ImageHash] = set()
    
    def is_duplicate(self, image_path: str) -> Tuple[bool, Optional[imagehash.ImageHash]]:
        """
        Check if image is duplicate using perceptual hashing.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (is_duplicate, hash_value)
        """
        try:
            img = Image.open(image_path)
            img_hash = imagehash.average_hash(img, self.hash_size)
            
            for existing_hash in self.seen_hashes:
                if img_hash - existing_hash <= self.similarity_threshold:
                    return True, existing_hash
            
            self.seen_hashes.add(img_hash)
            return False, img_hash
        except Exception as e:
            logging.error(f"Duplicate detection error for {image_path}: {e}")
            return False, None


class FaceDetector:
    """Detects faces in images using OpenCV Haar cascades."""
    
    def __init__(self):
        """Initialize face detector with Haar cascade classifier."""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def detect_faces(self, image_path: str) -> int:
        """
        Detect faces in image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Number of faces detected
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                logging.warning(f"Could not read image: {image_path}")
                return 0
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            return len(faces)
        except Exception as e:
            logging.error(f"Face detection error for {image_path}: {e}")
            return 0
