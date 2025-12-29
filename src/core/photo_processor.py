"""
Main photo processing logic with threading support.
"""

import os
import shutil
import logging
from typing import Dict, List
from PySide6.QtCore import QThread, Signal

from core.detectors import BlurDetector, DuplicateDetector, FaceDetector
from utils.file_utils import FileManager
from utils.validators import InputValidator


class PhotoProcessor(QThread):
    """Handles photo processing in a separate thread."""
    
    progress_updated = Signal(int)
    status_updated = Signal(str)
    finished_processing = Signal(dict)
    
    def __init__(self, folder_path: str, blur_threshold: int = 100, 
                 similarity_threshold: int = 5, enable_face_detection: bool = True):
        """
        Initialize photo processor.
        
        Args:
            folder_path: Path to folder containing photos
            blur_threshold: Threshold for blur detection
            similarity_threshold: Threshold for duplicate detection
            enable_face_detection: Whether to enable face detection
        """
        super().__init__()
        self.folder_path = folder_path
        self.enable_face_detection = enable_face_detection
        
        # Initialize file manager with undo support
        self.file_manager = FileManager(folder_path)
        
        # Initialize detectors
        self.blur_detector = BlurDetector(blur_threshold)
        self.duplicate_detector = DuplicateDetector(similarity_threshold)
        self.face_detector = FaceDetector() if enable_face_detection else None
        
        # Results tracking
        self.results = {
            'total_processed': 0,
            'good_photos': 0,
            'blurry_photos': 0,
            'duplicate_photos': 0,
            'face_photos': 0
        }
    
    def _get_image_files(self) -> List[str]:
        """Get list of image files in the folder."""
        try:
            return [f for f in os.listdir(self.folder_path) 
                   if f.lower().endswith(InputValidator.SUPPORTED_IMAGE_EXTENSIONS)]
        except Exception as e:
            logging.error(f"Error getting image files: {e}")
            return []
    
    def _create_category_folders(self) -> None:
        """Create category folders for organizing photos."""
        categories = ["Good_Photos", "Blurry_Photos", "Duplicate_Photos", "Face_Photos"]
        for category in categories:
            try:
                os.makedirs(os.path.join(self.folder_path, category), exist_ok=True)
            except Exception as e:
                logging.error(f"Error creating folder {category}: {e}")
    
    def _process_single_image(self, filename: str, index: int, total_files: int) -> None:
        """
        Process a single image file.
        
        Args:
            filename: Name of the image file
            index: Current file index
            total_files: Total number of files
        """
        file_path = os.path.join(self.folder_path, filename)
        
        # Update progress
        progress = int((index + 1) / total_files * 100)
        self.progress_updated.emit(progress)
        self.status_updated.emit(f"Processing: {filename}")
        
        if not os.path.exists(file_path):
            logging.warning(f"File not found: {file_path}")
            return
        
        self.results['total_processed'] += 1
        target_category = "Good_Photos"
        
        try:
            # Check for duplicates first
            is_duplicate, _, _ = self.duplicate_detector.is_duplicate(file_path)
            if is_duplicate:
                target_category = "Duplicate_Photos"
                self.results['duplicate_photos'] += 1
            else:
                # Check for blur
                is_blurry, _ = self.blur_detector.is_blurry(file_path)
                if is_blurry:
                    target_category = "Blurry_Photos"
                    self.results['blurry_photos'] += 1
                else:
                    self.results['good_photos'] += 1
                
                # Face detection (only for non-duplicates)
                if self.face_detector and self.face_detector.detect_faces(file_path) > 0:
                    face_path = os.path.join(self.folder_path, "Face_Photos", filename)
                    shutil.copy2(file_path, face_path)
                    self.results['face_photos'] += 1
            
            # Move file to appropriate folder using file manager
            if target_category != "Good_Photos" or not is_duplicate:
                target_path = os.path.join(self.folder_path, target_category, filename)
                self.file_manager.safe_move(file_path, target_path)
                
        except Exception as e:
            logging.error(f"Error processing {filename}: {e}")
            self.status_updated.emit(f"Error processing {filename}: {str(e)}")
    
    def run(self) -> None:
        """Main processing function."""
        try:
            # Create category folders
            self._create_category_folders()
            
            # Get image files
            image_files = self._get_image_files()
            total_files = len(image_files)
            
            if total_files == 0:
                self.status_updated.emit("No image files found!")
                return
            
            # Process each image
            for index, filename in enumerate(image_files):
                self._process_single_image(filename, index, total_files)
            
            self.status_updated.emit("Processing completed!")
            self.finished_processing.emit(self.results)
            
        except Exception as e:
            logging.error(f"Processing error: {e}")
            self.status_updated.emit(f"Error: {str(e)}")
