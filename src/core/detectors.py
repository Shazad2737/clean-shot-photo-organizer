"""
Image detection algorithms for blur, duplicates, and faces.

Enhanced with:
- Multi-metric blur detection (Laplacian + Sobel)
- Multi-hash duplicate detection (average + pHash + dHash)
- Image normalization for consistent results
- Reset functionality for session management
"""

import cv2
import logging
from PIL import Image
import imagehash
import numpy as np
from typing import Tuple, Dict, List, Optional


class BlurDetector:
    """
    Detects blurry images using multiple metrics:
    1. Laplacian variance (edge detection)
    2. Sobel gradient magnitude
    
    Images are normalized to a standard size for consistent comparison.
    """
    
    def __init__(self, threshold: int = 100, max_dimension: int = 800):
        """
        Initialize blur detector.
        
        Args:
            threshold: Combined blur score threshold below which image is considered blurry
            max_dimension: Maximum dimension to resize images to for consistent comparison
        """
        self.threshold = threshold
        self.max_dimension = max_dimension
    
    def get_blur_score(self, image_path: str) -> Optional[float]:
        """
        Calculate blur score for an image.
        
        Higher scores indicate sharper images.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Blur score (float) or None if image cannot be read
        """
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                logging.warning(f"Could not read image: {image_path}")
                return None
            
            # Normalize image size for consistent comparison
            h, w = img.shape[:2]
            if max(h, w) > self.max_dimension:
                scale = self.max_dimension / max(h, w)
                img = cv2.resize(img, None, fx=scale, fy=scale, 
                               interpolation=cv2.INTER_AREA)
            
            # Method 1: Laplacian variance (primary metric)
            laplacian = cv2.Laplacian(img, cv2.CV_64F)
            laplacian_var = laplacian.var()
            
            # Method 2: Sobel gradient magnitude (secondary metric)
            sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(sobelx**2 + sobely**2).mean()
            
            # Combined score: weighted average
            blur_score = (laplacian_var * 0.7) + (gradient_magnitude * 0.3)
            
            return blur_score
            
        except Exception as e:
            logging.error(f"Blur detection error for {image_path}: {e}")
            return None
    
    def is_blurry(self, image_path: str) -> Tuple[bool, Optional[float]]:
        """
        Check if image is blurry.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (is_blurry: bool, blur_score: float or None)
        """
        blur_score = self.get_blur_score(image_path)
        
        if blur_score is None:
            return False, None
        
        is_blur = blur_score < self.threshold
        return is_blur, blur_score


class DuplicateDetector:
    """
    Detects duplicate images using multiple perceptual hashing algorithms:
    1. Average hash - good for overall similarity
    2. Perceptual hash (pHash) - robust to scaling/compression
    3. Difference hash (dHash) - captures gradients
    
    Uses weighted voting for more accurate detection.
    """
    
    def __init__(self, similarity_threshold: int = 5, hash_size: int = 16):
        """
        Initialize duplicate detector.
        
        Args:
            similarity_threshold: Maximum weighted hash difference to consider images similar
            hash_size: Size of the perceptual hash (larger = more precise)
        """
        self.similarity_threshold = similarity_threshold
        self.hash_size = hash_size
        self.seen_hashes: List[Dict] = []
    
    def reset(self) -> None:
        """Clear all seen hashes. Call this between processing sessions."""
        self.seen_hashes.clear()
        logging.info("DuplicateDetector: Hash cache cleared")
    
    def _compute_hashes(self, img: Image.Image) -> Dict:
        """Compute all hash types for an image."""
        return {
            'avg': imagehash.average_hash(img, hash_size=self.hash_size),
            'phash': imagehash.phash(img, hash_size=self.hash_size),
            'dhash': imagehash.dhash(img, hash_size=self.hash_size),
        }
    
    def _calculate_weighted_diff(self, hashes1: Dict, hashes2: Dict) -> float:
        """
        Calculate weighted difference between two hash sets.
        
        pHash gets highest weight as it's most robust.
        """
        avg_diff = hashes1['avg'] - hashes2['avg']
        p_diff = hashes1['phash'] - hashes2['phash']
        d_diff = hashes1['dhash'] - hashes2['dhash']
        
        # Weighted: pHash most important (50%), others 25% each
        return (avg_diff * 0.25) + (p_diff * 0.5) + (d_diff * 0.25)
    
    def is_duplicate(self, image_path: str) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        Check if image is a duplicate of any previously seen image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (is_duplicate: bool, diff_score: float or None, original_filename: str or None)
        """
        try:
            img = Image.open(image_path)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Compute hashes
            current_hashes = self._compute_hashes(img)
            current_hashes['path'] = image_path
            
            # Compare against seen images
            for seen in self.seen_hashes:
                weighted_diff = self._calculate_weighted_diff(current_hashes, seen)
                
                if weighted_diff <= self.similarity_threshold:
                    original_path = seen.get('path', 'unknown')
                    original_name = original_path.split('\\')[-1].split('/')[-1]
                    
                    logging.debug(
                        f"Duplicate found: {image_path} matches {original_name} "
                        f"(diff: {weighted_diff:.1f})"
                    )
                    return True, weighted_diff, original_name
            
            # Not a duplicate, add to seen hashes
            self.seen_hashes.append(current_hashes)
            return False, None, None
            
        except Exception as e:
            logging.error(f"Duplicate detection error for {image_path}: {e}")
            return False, None, None
    
    @property
    def seen_count(self) -> int:
        """Return the number of images seen so far."""
        return len(self.seen_hashes)


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
