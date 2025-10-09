"""
Input validation utilities.
"""

import os
from pathlib import Path
from typing import List, Tuple


class InputValidator:
    """Validates user inputs and file paths."""
    
    SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp')
    
    @staticmethod
    def validate_folder_path(folder_path: str) -> Tuple[bool, str]:
        """
        Validate folder path.
        
        Args:
            folder_path: Path to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not folder_path:
            return False, "No folder path provided"
        
        if not os.path.exists(folder_path):
            return False, "Folder does not exist"
        
        if not os.path.isdir(folder_path):
            return False, "Path is not a directory"
        
        if not os.access(folder_path, os.R_OK):
            return False, "No read permission for folder"
        
        if not os.access(folder_path, os.W_OK):
            return False, "No write permission for folder"
        
        return True, ""
    
    @staticmethod
    def validate_image_files(folder_path: str) -> Tuple[bool, str, List[str]]:
        """
        Validate that folder contains image files.
        
        Args:
            folder_path: Path to folder to check
            
        Returns:
            Tuple of (has_images, error_message, image_files)
        """
        try:
            files = os.listdir(folder_path)
            image_files = [f for f in files 
                          if f.lower().endswith(InputValidator.SUPPORTED_IMAGE_EXTENSIONS)]
            
            if not image_files:
                return False, "No image files found in folder", []
            
            return True, "", image_files
            
        except Exception as e:
            return False, f"Error reading folder: {str(e)}", []
    
    @staticmethod
    def validate_thresholds(blur_threshold: int, similarity_threshold: int) -> Tuple[bool, str]:
        """
        Validate threshold values.
        
        Args:
            blur_threshold: Blur detection threshold
            similarity_threshold: Similarity detection threshold
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if blur_threshold < 0 or blur_threshold > 1000:
            return False, "Blur threshold must be between 0 and 1000"
        
        if similarity_threshold < 0 or similarity_threshold > 50:
            return False, "Similarity threshold must be between 0 and 50"
        
        return True, ""
    
    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: int = 100) -> Tuple[bool, str]:
        """
        Validate file size.
        
        Args:
            file_path: Path to file to check
            max_size_mb: Maximum file size in MB
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            file_size = os.path.getsize(file_path)
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if file_size > max_size_bytes:
                return False, f"File too large: {file_size / (1024*1024):.1f}MB (max: {max_size_mb}MB)"
            
            return True, ""
            
        except Exception as e:
            return False, f"Error checking file size: {str(e)}"
