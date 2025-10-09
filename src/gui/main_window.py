"""
Main application window for the photo organizer.
"""

import os
import logging
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                               QPushButton, QFileDialog, QMessageBox, QLabel)
from PySide6.QtCore import Qt

from core.photo_processor import PhotoProcessor
from utils.validators import InputValidator
from gui.components import SettingsWidget, ProgressWidget, ResultsWidget


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.current_folder = ""
        self.processor = None
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the main UI."""
        self.setWindowTitle("CLEAN SHOT - AI Photo Organizer")
        self.setGeometry(100, 100, 700, 500)
        self.setMinimumSize(600, 400)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Select a folder containing photos")
        self.folder_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        self.select_btn = QPushButton("Browse Folder")
        self.select_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.select_btn.clicked.connect(self.select_folder)
        
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.select_btn)
        folder_layout.addStretch()
        
        # Settings widget
        self.settings_widget = SettingsWidget()
        
        # Progress widget
        self.progress_widget = ProgressWidget()
        
        # Process and Undo buttons
        button_layout = QHBoxLayout()
        
        self.process_btn = QPushButton("Start Processing")
        self.process_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setEnabled(False)
        
        self.undo_btn = QPushButton("Undo Last Operation")
        self.undo_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.undo_btn.clicked.connect(self.undo_last_operation)
        self.undo_btn.setEnabled(False)
        
        button_layout.addWidget(self.process_btn)
        button_layout.addWidget(self.undo_btn)
        
        # Results widget
        self.results_widget = ResultsWidget()
        
        # Add all to layout
        layout.addLayout(folder_layout)
        layout.addWidget(self.settings_widget)
        layout.addWidget(self.progress_widget)
        layout.addLayout(button_layout)
        layout.addWidget(self.results_widget)
        layout.addStretch()
    
    def setup_connections(self):
        """Setup signal connections."""
        pass  # Connections will be made when processor is created
    
    def select_folder(self):
        """Select folder containing photos."""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Photo Folder",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder:
            # Validate folder
            is_valid, error_msg = InputValidator.validate_folder_path(folder)
            if not is_valid:
                QMessageBox.warning(self, "Invalid Folder", error_msg)
                return
            
            # Check for image files
            has_images, error_msg, image_files = InputValidator.validate_image_files(folder)
            if not has_images:
                QMessageBox.warning(self, "No Images", error_msg)
                return
            
            self.current_folder = folder
            folder_name = os.path.basename(folder)
            self.folder_label.setText(f"Selected: {folder_name} ({len(image_files)} images)")
            self.folder_label.setStyleSheet("font-weight: bold; color: #27ae60;")
            self.process_btn.setEnabled(True)
            self.progress_widget.update_status(f"Folder selected with {len(image_files)} images. Click 'Start Processing'.")
            self.results_widget.clear_results()
    
    def start_processing(self):
        """Start photo processing."""
        if not self.current_folder:
            QMessageBox.warning(self, "Error", "Please select a folder first.")
            return
        
        # Get and validate settings
        settings = self.settings_widget.get_settings()
        is_valid, error_msg = InputValidator.validate_thresholds(
            settings['blur_threshold'], 
            settings['similarity_threshold']
        )
        if not is_valid:
            QMessageBox.warning(self, "Invalid Settings", error_msg)
            return
        
        # Disable UI during processing
        self.process_btn.setEnabled(False)
        self.undo_btn.setEnabled(False)
        self.select_btn.setEnabled(False)
        self.progress_widget.show_progress(True)
        self.results_widget.clear_results()
        
        # Create processor
        self.processor = PhotoProcessor(
            self.current_folder,
            settings['blur_threshold'],
            settings['similarity_threshold'],
            settings['enable_face_detection']
        )
        
        # Connect signals
        self.processor.progress_updated.connect(self.progress_widget.update_progress)
        self.processor.status_updated.connect(self.progress_widget.update_status)
        self.processor.finished_processing.connect(self.processing_finished)
        
        # Start processing
        self.processor.start()
    
    def processing_finished(self, results):
        """Handle processing completion."""
        # Re-enable UI
        self.process_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        self.progress_widget.show_progress(False)
        
        # Enable undo button if there are operations to undo
        if self.processor and hasattr(self.processor, 'file_manager'):
            undo_count = self.processor.file_manager.get_undo_count()
            self.undo_btn.setEnabled(undo_count > 0)
            if undo_count > 0:
                self.undo_btn.setText(f"Undo Last Operation ({undo_count} available)")
        
        # Display results
        self.results_widget.display_results(results)
        
        # Show completion message
        QMessageBox.information(
            self, 
            "Complete", 
            "Photo organization finished!\n\n"
            f"Processed {results['total_processed']} photos.\n"
            f"Found {results['duplicate_photos']} duplicates and "
            f"{results['blurry_photos']} blurry photos."
        )
    
    def undo_last_operation(self):
        """Undo the last file operation."""
        if not self.processor or not hasattr(self.processor, 'file_manager'):
            QMessageBox.warning(self, "No Operations", "No operations to undo.")
            return
        
        if self.processor.file_manager.undo_last_operation():
            QMessageBox.information(self, "Undo Complete", "Last operation has been undone.")
            # Update undo button
            undo_count = self.processor.file_manager.get_undo_count()
            if undo_count > 0:
                self.undo_btn.setText(f"Undo Last Operation ({undo_count} available)")
            else:
                self.undo_btn.setText("Undo Last Operation")
                self.undo_btn.setEnabled(False)
        else:
            QMessageBox.warning(self, "Undo Failed", "No operations to undo or undo failed.")
    
    def closeEvent(self, event):
        """Handle application close."""
        if self.processor and self.processor.isRunning():
            reply = QMessageBox.question(
                self, 
                "Exit Application",
                "Processing is still running. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.processor.terminate()
                self.processor.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
