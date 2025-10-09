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
        is_blurry = self.detector.is_blurry(img_path)
        self.assertTrue(is_blurry, "Should detect blurry image")
    
    def test_sharp_image_detection(self):
        """Test detection of sharp images."""
        # Create a sharp test image with edges
        sharp_img = np.zeros((100, 100), dtype=np.uint8)
        sharp_img[40:60, 40:60] = 255  # White square
        
        # Save image
        img_path = os.path.join(self.temp_dir, "sharp_test.jpg")
        cv2.imwrite(img_path, sharp_img)
        
        # Test detection
        is_blurry = self.detector.is_blurry(img_path)
        self.assertFalse(is_blurry, "Should not detect sharp image as blurry")
    
    def test_invalid_image_path(self):
        """Test handling of invalid image paths."""
        invalid_path = os.path.join(self.temp_dir, "nonexistent.jpg")
        is_blurry = self.detector.is_blurry(invalid_path)
        self.assertFalse(is_blurry, "Should return False for invalid path")


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
        is_dup1, _ = self.detector.is_duplicate(img1_path)
        self.assertFalse(is_dup1, "First image should not be duplicate")
        
        # Test second image (should be duplicate)
        is_dup2, _ = self.detector.is_duplicate(img2_path)
        self.assertTrue(is_dup2, "Second identical image should be duplicate")
    
    def test_different_images(self):
        """Test that different images are not detected as duplicates."""
        # Create two different images
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 100), color='blue')
        
        img1_path = os.path.join(self.temp_dir, "img1.jpg")
        img2_path = os.path.join(self.temp_dir, "img2.jpg")
        
        img1.save(img1_path)
        img2.save(img2_path)
        
        # Test both images
        is_dup1, _ = self.detector.is_duplicate(img1_path)
        is_dup2, _ = self.detector.is_duplicate(img2_path)
        
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
