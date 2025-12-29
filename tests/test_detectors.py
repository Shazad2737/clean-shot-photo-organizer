"""
Unit tests for image detection algorithms.
"""

import unittest
import tempfile
import os
import numpy as np
from PIL import Image
import cv2

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.detectors import BlurDetector, DuplicateDetector, FaceDetector


class TestBlurDetector(unittest.TestCase):
    """Test blur detection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = BlurDetector(threshold=100)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_blurry_image_detection(self):
        """Test detection of blurry images."""
        # Create a blurry test image
        blurry_img = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        blurry_img = cv2.GaussianBlur(blurry_img, (15, 15), 0)
        
        # Save image
        img_path = os.path.join(self.temp_dir, "blurry_test.jpg")
        cv2.imwrite(img_path, blurry_img)
        
        # Test detection
        is_blurry, blur_score = self.detector.is_blurry(img_path)
        self.assertTrue(is_blurry, "Should detect blurry image")
        self.assertIsNotNone(blur_score, "Should return blur score")
    
    def test_sharp_image_detection(self):
        """Test detection of sharp images."""
        # Create a sharp test image with edges
        sharp_img = np.zeros((100, 100), dtype=np.uint8)
        sharp_img[40:60, 40:60] = 255  # White square
        
        # Save image
        img_path = os.path.join(self.temp_dir, "sharp_test.jpg")
        cv2.imwrite(img_path, sharp_img)
        
        # Test detection
        is_blurry, blur_score = self.detector.is_blurry(img_path)
        self.assertFalse(is_blurry, "Should not detect sharp image as blurry")
        self.assertIsNotNone(blur_score, "Should return blur score")
    
    def test_invalid_image_path(self):
        """Test handling of invalid image paths."""
        invalid_path = os.path.join(self.temp_dir, "nonexistent.jpg")
        is_blurry, blur_score = self.detector.is_blurry(invalid_path)
        self.assertFalse(is_blurry, "Should return False for invalid path")
        self.assertIsNone(blur_score, "Should return None blur score for invalid path")


class TestDuplicateDetector(unittest.TestCase):
    """Test duplicate detection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = DuplicateDetector(similarity_threshold=5)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_identical_images(self):
        """Test detection of identical images."""
        # Create two identical images
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 100), color='red')
        
        img1_path = os.path.join(self.temp_dir, "img1.jpg")
        img2_path = os.path.join(self.temp_dir, "img2.jpg")
        
        img1.save(img1_path)
        img2.save(img2_path)
        
        # Test first image (should not be duplicate)
        is_dup1, diff_score1, original1 = self.detector.is_duplicate(img1_path)
        self.assertFalse(is_dup1, "First image should not be duplicate")
        
        # Test second image (should be duplicate)
        is_dup2, diff_score2, original2 = self.detector.is_duplicate(img2_path)
        self.assertTrue(is_dup2, "Second identical image should be duplicate")
        self.assertIsNotNone(diff_score2, "Should return diff score for duplicate")
        self.assertIsNotNone(original2, "Should return original filename for duplicate")
    
    def test_different_images(self):
        """Test that different images are not detected as duplicates."""
        # Create two different images with patterns (solid colors hash identically)
        import numpy as np
        # Image 1: Horizontal stripes
        arr1 = np.zeros((100, 100, 3), dtype=np.uint8)
        arr1[0:50, :] = [255, 0, 0]  # Red top half
        arr1[50:100, :] = [0, 255, 0]  # Green bottom half
        img1 = Image.fromarray(arr1)
        
        # Image 2: Vertical stripes  
        arr2 = np.zeros((100, 100, 3), dtype=np.uint8)
        arr2[:, 0:50] = [0, 0, 255]  # Blue left half
        arr2[:, 50:100] = [255, 255, 0]  # Yellow right half
        img2 = Image.fromarray(arr2)
        
        img1_path = os.path.join(self.temp_dir, "img1.jpg")
        img2_path = os.path.join(self.temp_dir, "img2.jpg")
        
        img1.save(img1_path)
        img2.save(img2_path)

        
        # Test both images
        is_dup1, diff_score1, original1 = self.detector.is_duplicate(img1_path)
        is_dup2, diff_score2, original2 = self.detector.is_duplicate(img2_path)
        
        self.assertFalse(is_dup1, "First image should not be duplicate")
        self.assertFalse(is_dup2, "Different image should not be duplicate")


class TestFaceDetector(unittest.TestCase):
    """Test face detection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = FaceDetector()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_no_faces_image(self):
        """Test image with no faces."""
        # Create a simple image with no faces
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img_path = os.path.join(self.temp_dir, "no_faces.jpg")
        cv2.imwrite(img_path, img)
        
        face_count = self.detector.detect_faces(img_path)
        self.assertEqual(face_count, 0, "Should detect no faces in simple image")
    
    def test_invalid_image_path(self):
        """Test handling of invalid image paths."""
        invalid_path = os.path.join(self.temp_dir, "nonexistent.jpg")
        face_count = self.detector.detect_faces(invalid_path)
        self.assertEqual(face_count, 0, "Should return 0 for invalid path")


if __name__ == '__main__':
    unittest.main()
