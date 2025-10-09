"""
Unit tests for input validation.
"""

import unittest
import tempfile
import os

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.validators import InputValidator


class TestInputValidator(unittest.TestCase):
    """Test input validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_valid_folder_path(self):
        """Test validation of valid folder path."""
        is_valid, error_msg = InputValidator.validate_folder_path(self.temp_dir)
        self.assertTrue(is_valid, f"Valid folder should pass validation: {error_msg}")
        self.assertEqual(error_msg, "")
    
    def test_nonexistent_folder_path(self):
        """Test validation of nonexistent folder path."""
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent")
        is_valid, error_msg = InputValidator.validate_folder_path(nonexistent_path)
        self.assertFalse(is_valid, "Nonexistent folder should fail validation")
        self.assertIn("does not exist", error_msg)
    
    def test_empty_folder_path(self):
        """Test validation of empty folder path."""
        is_valid, error_msg = InputValidator.validate_folder_path("")
        self.assertFalse(is_valid, "Empty path should fail validation")
        self.assertIn("No folder path provided", error_msg)
    
    def test_image_files_validation(self):
        """Test validation of folder with image files."""
        # Create test image files
        from PIL import Image
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 100), color='blue')
        
        img1.save(os.path.join(self.temp_dir, "test1.jpg"))
        img2.save(os.path.join(self.temp_dir, "test2.png"))
        
        has_images, error_msg, image_files = InputValidator.validate_image_files(self.temp_dir)
        self.assertTrue(has_images, f"Folder with images should pass validation: {error_msg}")
        self.assertEqual(len(image_files), 2)
        self.assertIn("test1.jpg", image_files)
        self.assertIn("test2.png", image_files)
    
    def test_no_image_files_validation(self):
        """Test validation of folder with no image files."""
        # Create a text file
        with open(os.path.join(self.temp_dir, "test.txt"), 'w') as f:
            f.write("test content")
        
        has_images, error_msg, image_files = InputValidator.validate_image_files(self.temp_dir)
        self.assertFalse(has_images, "Folder without images should fail validation")
        self.assertIn("No image files found", error_msg)
        self.assertEqual(len(image_files), 0)
    
    def test_valid_thresholds(self):
        """Test validation of valid threshold values."""
        is_valid, error_msg = InputValidator.validate_thresholds(100, 5)
        self.assertTrue(is_valid, f"Valid thresholds should pass validation: {error_msg}")
        self.assertEqual(error_msg, "")
    
    def test_invalid_blur_threshold(self):
        """Test validation of invalid blur threshold."""
        is_valid, error_msg = InputValidator.validate_thresholds(-1, 5)
        self.assertFalse(is_valid, "Negative blur threshold should fail validation")
        self.assertIn("Blur threshold must be between 0 and 1000", error_msg)
        
        is_valid, error_msg = InputValidator.validate_thresholds(1001, 5)
        self.assertFalse(is_valid, "Too high blur threshold should fail validation")
        self.assertIn("Blur threshold must be between 0 and 1000", error_msg)
    
    def test_invalid_similarity_threshold(self):
        """Test validation of invalid similarity threshold."""
        is_valid, error_msg = InputValidator.validate_thresholds(100, -1)
        self.assertFalse(is_valid, "Negative similarity threshold should fail validation")
        self.assertIn("Similarity threshold must be between 0 and 50", error_msg)
        
        is_valid, error_msg = InputValidator.validate_thresholds(100, 51)
        self.assertFalse(is_valid, "Too high similarity threshold should fail validation")
        self.assertIn("Similarity threshold must be between 0 and 50", error_msg)
    
    def test_file_size_validation(self):
        """Test file size validation."""
        # Create a small file
        small_file = os.path.join(self.temp_dir, "small.txt")
        with open(small_file, 'w') as f:
            f.write("small content")
        
        is_valid, error_msg = InputValidator.validate_file_size(small_file, max_size_mb=1)
        self.assertTrue(is_valid, f"Small file should pass validation: {error_msg}")
        self.assertEqual(error_msg, "")
    
    def test_large_file_validation(self):
        """Test validation of large files."""
        # Create a large file (simulate)
        large_file = os.path.join(self.temp_dir, "large.txt")
        with open(large_file, 'w') as f:
            f.write("x" * (2 * 1024 * 1024))  # 2MB file
        
        is_valid, error_msg = InputValidator.validate_file_size(large_file, max_size_mb=1)
        self.assertFalse(is_valid, "Large file should fail validation")
        self.assertIn("File too large", error_msg)


if __name__ == '__main__':
    unittest.main()
