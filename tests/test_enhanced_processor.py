"""
Unit tests for enhanced photo processor functionality.
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

from core.enhanced_processor import EnhancedPhotoProcessor, ProcessingResult


class TestProcessingResult(unittest.TestCase):
    """Test ProcessingResult class."""
    
    def test_processing_result_creation(self):
        """Test ProcessingResult object creation."""
        result = ProcessingResult(
            filename="test.jpg",
            category="Good_Photos",
            confidence=0.95,
            blur_score=150.5,
            duplicate_score=2,
            face_count=1
        )
        
        self.assertEqual(result.filename, "test.jpg")
        self.assertEqual(result.category, "Good_Photos")
        self.assertEqual(result.confidence, 0.95)
        self.assertEqual(result.blur_score, 150.5)
        self.assertEqual(result.duplicate_score, 2)
        self.assertEqual(result.face_count, 1)
    
    def test_processing_result_minimal(self):
        """Test ProcessingResult with minimal parameters."""
        result = ProcessingResult("test.jpg", "Blurry_Photos", 0.8)
        
        self.assertEqual(result.filename, "test.jpg")
        self.assertEqual(result.category, "Blurry_Photos")
        self.assertEqual(result.confidence, 0.8)
        self.assertIsNone(result.blur_score)
        self.assertIsNone(result.duplicate_score)
        self.assertEqual(result.face_count, 0)


class TestEnhancedPhotoProcessor(unittest.TestCase):
    """Test enhanced photo processor functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = EnhancedPhotoProcessor(
            self.temp_dir,
            blur_threshold=100,
            similarity_threshold=5,
            enable_face_detection=True
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_processor_initialization(self):
        """Test processor initialization."""
        self.assertEqual(self.processor.folder_path, self.temp_dir)
        self.assertEqual(self.processor.blur_detector.threshold, 100)
        self.assertEqual(self.processor.duplicate_detector.similarity_threshold, 5)
        self.assertIsNotNone(self.processor.face_detector)
        self.assertFalse(self.processor.preview_mode)
    
    def test_preview_mode_toggle(self):
        """Test preview mode toggle."""
        self.assertFalse(self.processor.preview_mode)
        
        self.processor.set_preview_mode(True)
        self.assertTrue(self.processor.preview_mode)
        
        self.processor.set_preview_mode(False)
        self.assertFalse(self.processor.preview_mode)
    
    def test_get_image_files(self):
        """Test getting image files from directory."""
        # Create test images
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 100), color='blue')
        img1.save(os.path.join(self.temp_dir, "test1.jpg"))
        img2.save(os.path.join(self.temp_dir, "test2.png"))
        
        # Create a text file (should be ignored)
        with open(os.path.join(self.temp_dir, "test.txt"), 'w') as f:
            f.write("test content")
        
        image_files = self.processor._get_image_files()
        self.assertEqual(len(image_files), 2)
        self.assertIn("test1.jpg", image_files)
        self.assertIn("test2.png", image_files)
        self.assertNotIn("test.txt", image_files)
    
    def test_create_category_folders(self):
        """Test creation of category folders."""
        self.processor._create_category_folders()
        
        expected_folders = ["Good_Photos", "Blurry_Photos", "Duplicate_Photos", "Face_Photos"]
        for folder in expected_folders:
            folder_path = os.path.join(self.temp_dir, folder)
            self.assertTrue(os.path.exists(folder_path))
            self.assertTrue(os.path.isdir(folder_path))
    
    def test_analyze_image_blurry(self):
        """Test image analysis for blurry image."""
        # Create a blurry test image
        blurry_img = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        blurry_img = cv2.GaussianBlur(blurry_img, (15, 15), 0)
        
        img_path = os.path.join(self.temp_dir, "blurry_test.jpg")
        cv2.imwrite(img_path, blurry_img)
        
        result = self.processor._analyze_image(img_path)
        
        self.assertEqual(result.filename, "blurry_test.jpg")
        self.assertEqual(result.category, "Blurry_Photos")
        self.assertIsNotNone(result.blur_score)
        self.assertLess(result.blur_score, 100)  # Should be below threshold
    
    def test_analyze_image_sharp(self):
        """Test image analysis for sharp image."""
        # Create a sharp test image with edges
        sharp_img = np.zeros((100, 100), dtype=np.uint8)
        sharp_img[40:60, 40:60] = 255  # White square
        
        img_path = os.path.join(self.temp_dir, "sharp_test.jpg")
        cv2.imwrite(img_path, sharp_img)
        
        result = self.processor._analyze_image(img_path)
        
        self.assertEqual(result.filename, "sharp_test.jpg")
        self.assertEqual(result.category, "Good_Photos")
        self.assertIsNotNone(result.blur_score)
        self.assertGreater(result.blur_score, 100)  # Should be above threshold
    
    def test_analyze_image_duplicate(self):
        """Test image analysis for duplicate detection."""
        # Create two identical images with patterns to avoid blur detection
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 100), color='red')
        
        # Add patterns to make them sharp and distinct
        img1_array = np.array(img1)
        img2_array = np.array(img2)
        
        # Add white diagonal line to img1
        for i in range(100):
            if 0 <= i < 100:
                img1_array[i, i] = [255, 255, 255]
        
        # Add same pattern to img2
        for i in range(100):
            if 0 <= i < 100:
                img2_array[i, i] = [255, 255, 255]
        
        img1 = Image.fromarray(img1_array)
        img2 = Image.fromarray(img2_array)
        
        img1_path = os.path.join(self.temp_dir, "img1.jpg")
        img2_path = os.path.join(self.temp_dir, "img2.jpg")
        
        img1.save(img1_path)
        img2.save(img2_path)
        
        # Analyze first image
        result1 = self.processor._analyze_image(img1_path)
        self.assertEqual(result1.category, "Good_Photos")
        
        # Analyze second image (should be duplicate)
        result2 = self.processor._analyze_image(img2_path)
        self.assertEqual(result2.category, "Duplicate_Photos")
        self.assertIsNotNone(result2.duplicate_score)
    
    def test_analyze_image_nonexistent(self):
        """Test image analysis for nonexistent file."""
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent.jpg")
        
        result = self.processor._analyze_image(nonexistent_path)
        
        self.assertEqual(result.filename, "nonexistent.jpg")
        self.assertEqual(result.category, "Good_Photos")
        self.assertEqual(result.confidence, 1.0)  # Default confidence even on error


if __name__ == '__main__':
    unittest.main()
