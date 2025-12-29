"""
Enhanced photo processor with preview mode and batch processing.
"""

import os
import shutil
import logging
from typing import Dict, List, Optional, Tuple
from PySide6.QtCore import QThread, Signal
from pathlib import Path

from core.detectors import BlurDetector, DuplicateDetector, FaceDetector
from utils.file_utils import FileManager
from utils.validators import InputValidator


class ProcessingResult:
    """Result of processing a single image."""
    
    def __init__(self, filename: str, category: str, confidence: float, 
                 blur_score: Optional[float] = None, duplicate_score: Optional[float] = None,
                 face_count: int = 0):
        self.filename = filename
        self.category = category
        self.confidence = confidence
        self.blur_score = blur_score
        self.duplicate_score = duplicate_score
        self.face_count = face_count


class EnhancedPhotoProcessor(QThread):
    """Enhanced photo processor with preview mode and batch processing."""
    
    progress_updated = Signal(int)
    status_updated = Signal(str)
    finished_processing = Signal(dict)
    preview_ready = Signal(list)  # Emits list of ProcessingResult objects
    
    def __init__(self, folder_path: str, blur_threshold: int = 100, 
                 similarity_threshold: int = 5, enable_face_detection: bool = True):
        """
        Initialize enhanced photo processor.
        
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
        
        # Preview mode
        self.preview_mode = False
        self.preview_results: List[ProcessingResult] = []
    
    def set_preview_mode(self, enabled: bool) -> None:
        """Enable or disable preview mode."""
        self.preview_mode = enabled
    
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
    
    def _analyze_image(self, file_path: str) -> ProcessingResult:
        """
        Analyze a single image and return processing result.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            ProcessingResult object with analysis details
        """
        filename = os.path.basename(file_path)
        blur_score = None
        duplicate_score = None
        face_count = 0
        category = "Good_Photos"
        confidence = 1.0
        
        try:
            # Check for blur using enhanced detector (returns tuple)
            is_blurry, blur_score = self.blur_detector.is_blurry(file_path)
            if is_blurry:
                category = "Blurry_Photos"
                confidence = 0.8
            
            # Check for duplicates (returns 3 values now)
            is_duplicate, duplicate_score, original_name = self.duplicate_detector.is_duplicate(file_path)
            if is_duplicate:
                category = "Duplicate_Photos"
                confidence = 0.9
            
            # Check for faces
            if self.face_detector:
                face_count = self.face_detector.detect_faces(file_path)
                if face_count > 0 and category == "Good_Photos":
                    confidence = 0.95  # Higher confidence for photos with faces
            
            return ProcessingResult(
                filename=filename,
                category=category,
                confidence=confidence,
                blur_score=blur_score,
                duplicate_score=duplicate_score,
                face_count=face_count
            )

            
        except Exception as e:
            logging.error(f"Error analyzing {filename}: {e}")
            return ProcessingResult(
                filename=filename,
                category="Good_Photos",
                confidence=1.0  # Default confidence even on error
            )
    
    def _process_single_image(self, filename: str, index: int, total_files: int, 
                            apply_changes: bool = True) -> Optional[ProcessingResult]:
        """
        Process a single image file.
        
        Args:
            filename: Name of the image file
            index: Current file index
            total_files: Total number of files
            apply_changes: Whether to actually move files or just analyze
            
        Returns:
            ProcessingResult object
        """
        file_path = os.path.join(self.folder_path, filename)
        
        # Update progress
        progress = int((index + 1) / total_files * 100)
        self.progress_updated.emit(progress)
        self.status_updated.emit(f"Processing: {filename}")
        
        if not os.path.exists(file_path):
            logging.warning(f"File not found: {file_path}")
            return None
        
        # Analyze the image
        result = self._analyze_image(file_path)
        
        if apply_changes:
            self.results['total_processed'] += 1
            
            # Update category counts
            if result.category == "Blurry_Photos":
                self.results['blurry_photos'] += 1
            elif result.category == "Duplicate_Photos":
                self.results['duplicate_photos'] += 1
            else:
                self.results['good_photos'] += 1
            
            # Handle face detection
            if result.face_count > 0:
                self.results['face_photos'] += 1
                if apply_changes:
                    face_path = os.path.join(self.folder_path, "Face_Photos", filename)
                    self.file_manager.safe_copy(file_path, face_path)
            
            # Move file to appropriate folder
            if result.category != "Good_Photos":
                target_path = os.path.join(self.folder_path, result.category, filename)
                self.file_manager.safe_move(file_path, target_path)
        
        return result
    
    def run_preview(self) -> None:
        """Run preview mode - analyze without moving files."""
        try:
            self.status_updated.emit("Running preview analysis...")
            
            # Get image files
            image_files = self._get_image_files()
            total_files = len(image_files)
            
            if total_files == 0:
                self.status_updated.emit("No image files found!")
                return
            
            self.preview_results = []
            
            # Analyze each image
            for index, filename in enumerate(image_files):
                result = self._process_single_image(filename, index, total_files, apply_changes=False)
                if result:
                    self.preview_results.append(result)
            
            self.status_updated.emit("Preview analysis completed!")
            self.preview_ready.emit(self.preview_results)
            
        except Exception as e:
            logging.error(f"Preview error: {e}")
            self.status_updated.emit(f"Preview error: {str(e)}")
    
    def run(self) -> None:
        """Main processing function."""
        try:
            if self.preview_mode:
                self.run_preview()
                return
            
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
                self._process_single_image(filename, index, total_files, apply_changes=True)
            
            self.status_updated.emit("Processing completed!")
            self.finished_processing.emit(self.results)
            
        except Exception as e:
            logging.error(f"Processing error: {e}")
            self.status_updated.emit(f"Error: {str(e)}")
    
    def apply_preview_results(self, selected_results: List[ProcessingResult]) -> None:
        """Apply selected preview results."""
        try:
            self._create_category_folders()
            
            for result in selected_results:
                if result.category != "Good_Photos":
                    file_path = os.path.join(self.folder_path, result.filename)
                    target_path = os.path.join(self.folder_path, result.category, result.filename)
                    self.file_manager.safe_move(file_path, target_path)
                    
                    # Update results
                    self.results['total_processed'] += 1
                    if result.category == "Blurry_Photos":
                        self.results['blurry_photos'] += 1
                    elif result.category == "Duplicate_Photos":
                        self.results['duplicate_photos'] += 1
                
                if result.face_count > 0:
                    file_path = os.path.join(self.folder_path, result.filename)
                    face_path = os.path.join(self.folder_path, "Face_Photos", result.filename)
                    self.file_manager.safe_copy(file_path, face_path)
                    self.results['face_photos'] += 1
            
            self.finished_processing.emit(self.results)
            
        except Exception as e:
            logging.error(f"Error applying preview results: {e}")
            self.status_updated.emit(f"Error: {str(e)}")
