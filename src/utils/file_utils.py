"""
File management utilities with undo functionality.
"""

import os
import shutil
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class OperationLogger:
    """Logs file operations for undo functionality."""
    
    def __init__(self, log_file: str = "operations.json"):
        """
        Initialize operation logger.
        
        Args:
            log_file: Path to the operations log file
        """
        self.log_file = log_file
        self.operations: List[Dict] = []
        self.load_operations()
    
    def load_operations(self):
        """Load operations from log file."""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    self.operations = json.load(f)
        except Exception as e:
            logging.error(f"Error loading operations: {e}")
            self.operations = []
    
    def save_operations(self):
        """Save operations to log file."""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.operations, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving operations: {e}")
    
    def log_operation(self, operation_type: str, source: str, destination: str, 
                     timestamp: str = None):
        """
        Log a file operation.
        
        Args:
            operation_type: Type of operation (move, copy, delete)
            source: Source file path
            destination: Destination file path
            timestamp: Operation timestamp
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        operation = {
            'type': operation_type,
            'source': source,
            'destination': destination,
            'timestamp': timestamp
        }
        
        self.operations.append(operation)
        self.save_operations()
    
    def get_undo_operations(self, session_id: str = None) -> List[Dict]:
        """
        Get operations that can be undone.
        
        Args:
            session_id: Optional session ID to filter operations
            
        Returns:
            List of operations that can be undone
        """
        if session_id:
            return [op for op in self.operations if op.get('session_id') == session_id]
        return self.operations.copy()
    
    def clear_operations(self):
        """Clear all logged operations."""
        self.operations = []
        self.save_operations()


class FileManager:
    """Enhanced file manager with undo support."""
    
    def __init__(self, base_path: str):
        """
        Initialize file manager.
        
        Args:
            base_path: Base path for file operations
        """
        self.base_path = Path(base_path)
        self.operation_logger = OperationLogger()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def safe_move(self, source: str, destination: str) -> bool:
        """
        Safely move a file with logging.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            
            # Move file
            shutil.move(source, destination)
            
            # Log operation
            self.operation_logger.log_operation(
                'move', source, destination
            )
            
            logging.info(f"Moved {source} to {destination}")
            return True
            
        except Exception as e:
            logging.error(f"Error moving file {source}: {e}")
            return False
    
    def safe_copy(self, source: str, destination: str) -> bool:
        """
        Safely copy a file with logging.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            
            # Copy file
            shutil.copy2(source, destination)
            
            # Log operation
            self.operation_logger.log_operation(
                'copy', source, destination
            )
            
            logging.info(f"Copied {source} to {destination}")
            return True
            
        except Exception as e:
            logging.error(f"Error copying file {source}: {e}")
            return False
    
    def undo_last_operation(self) -> bool:
        """
        Undo the last file operation.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.operation_logger.operations:
            return False
        
        try:
            last_op = self.operation_logger.operations[-1]
            
            if last_op['type'] == 'move':
                # Move file back to original location
                shutil.move(last_op['destination'], last_op['source'])
            elif last_op['type'] == 'copy':
                # Delete the copied file
                os.remove(last_op['destination'])
            
            # Remove from operations log
            self.operation_logger.operations.pop()
            self.operation_logger.save_operations()
            
            logging.info(f"Undid operation: {last_op}")
            return True
            
        except Exception as e:
            logging.error(f"Error undoing operation: {e}")
            return False
    
    def get_undo_count(self) -> int:
        """Get number of operations that can be undone."""
        return len(self.operation_logger.operations)
    
    def clear_operations(self):
        """Clear all logged operations."""
        self.operation_logger.clear_operations()
