"""
Enhanced main application window with modern UI design.
"""

import os
import logging
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                               QPushButton, QFileDialog, QMessageBox, QLabel,
                               QFrame, QSpacerItem, QSizePolicy, QMenuBar, QStatusBar,
                               QSplitter, QScrollArea, QTextEdit)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon, QAction

from core.photo_processor import PhotoProcessor
from utils.validators import InputValidator
from gui.components import SettingsWidget, ProgressWidget, ResultsWidget
from gui.styles import APPLICATION_STYLE, BUTTON_STYLES, COLORS


class EnhancedMainWindow(QMainWindow):
    """Enhanced main application window with modern UI design."""
    
    def __init__(self):
        super().__init__()
        self.current_folder = ""
        self.processor = None
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.apply_styles()
    
    def setup_ui(self):
        """Setup the enhanced UI."""
        self.setWindowTitle("CLEAN SHOT - AI Photo Organizer")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section
        self.create_header_section(main_layout)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel (settings and controls)
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel (progress and results)
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 500])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
    
    def create_header_section(self, layout):
        """Create the header section with title and folder selection."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Box)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("📸 CLEAN SHOT - AI Photo Organizer")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {COLORS['primary']};
                margin-bottom: 10px;
            }}
        """)
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Intelligent photo organization with AI-powered detection")
        subtitle_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {COLORS['text_light']};
                margin-bottom: 20px;
            }}
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        # Folder selection
        folder_layout = QHBoxLayout()
        folder_layout.setSpacing(15)
        
        self.folder_label = QLabel("📁 No folder selected")
        self.folder_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: {COLORS['text_light']};
                padding: 12px;
                background-color: {COLORS['light']};
                border: 2px dashed {COLORS['border']};
                border-radius: 8px;
                min-height: 20px;
            }}
        """)
        self.folder_label.setWordWrap(True)
        
        self.select_btn = QPushButton("📂 Browse Folder")
        self.select_btn.setStyleSheet(BUTTON_STYLES['primary'])
        self.select_btn.clicked.connect(self.select_folder)
        
        folder_layout.addWidget(self.folder_label, 1)
        folder_layout.addWidget(self.select_btn)
        
        header_layout.addLayout(folder_layout)
        layout.addWidget(header_frame)
    
    def create_left_panel(self):
        """Create the left panel with settings and controls."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(20)
        
        # Settings section
        self.settings_widget = SettingsWidget()
        left_layout.addWidget(self.settings_widget)
        
        # Action buttons
        button_frame = QFrame()
        button_frame.setFrameStyle(QFrame.Box)
        button_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        
        button_layout = QVBoxLayout(button_frame)
        button_layout.setSpacing(15)
        
        # Process button
        self.process_btn = QPushButton("🚀 Start Processing")
        self.process_btn.setStyleSheet(BUTTON_STYLES['success'])
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setEnabled(False)
        button_layout.addWidget(self.process_btn)
        
        # Undo button
        self.undo_btn = QPushButton("↩️ Undo Last Operation")
        self.undo_btn.setStyleSheet(BUTTON_STYLES['danger'])
        self.undo_btn.clicked.connect(self.undo_last_operation)
        self.undo_btn.setEnabled(False)
        button_layout.addWidget(self.undo_btn)
        
        # Clear results button
        self.clear_btn = QPushButton("🗑️ Clear Results")
        self.clear_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        self.clear_btn.clicked.connect(self.clear_results)
        button_layout.addWidget(self.clear_btn)
        
        left_layout.addWidget(button_frame)
        left_layout.addStretch()
        
        return left_widget
    
    def create_right_panel(self):
        """Create the right panel with progress and results."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(20)
        
        # Progress section
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.Box)
        progress_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setSpacing(15)
        
        # Progress title
        progress_title = QLabel("📊 Processing Status")
        progress_title.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {COLORS['primary']};
                margin-bottom: 10px;
            }}
        """)
        progress_layout.addWidget(progress_title)
        
        # Progress widget
        self.progress_widget = ProgressWidget()
        progress_layout.addWidget(self.progress_widget)
        
        right_layout.addWidget(progress_frame)
        
        # Results section
        results_frame = QFrame()
        results_frame.setFrameStyle(QFrame.Box)
        results_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        
        results_layout = QVBoxLayout(results_frame)
        results_layout.setSpacing(15)
        
        # Results title
        results_title = QLabel("📈 Processing Results")
        results_title.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {COLORS['primary']};
                margin-bottom: 10px;
            }}
        """)
        results_layout.addWidget(results_title)
        
        # Results widget
        self.results_widget = ResultsWidget()
        results_layout.addWidget(self.results_widget)
        
        right_layout.addWidget(results_frame)
        
        return right_widget
    
    def setup_menu(self):
        """Setup the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        open_action = QAction('&Open Folder', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.select_folder)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('&Edit')
        
        undo_action = QAction('&Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.undo_last_operation)
        edit_menu.addAction(undo_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to process photos")
    
    def apply_styles(self):
        """Apply modern styles to the application."""
        self.setStyleSheet(APPLICATION_STYLE)
    
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
            self.folder_label.setText(f"📁 {folder_name} ({len(image_files)} images)")
            self.folder_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 16px;
                    color: {COLORS['success']};
                    padding: 12px;
                    background-color: {COLORS['light']};
                    border: 2px solid {COLORS['success']};
                    border-radius: 8px;
                    min-height: 20px;
                }}
            """)
            self.process_btn.setEnabled(True)
            self.progress_widget.update_status(f"✅ Folder selected with {len(image_files)} images. Ready to process!")
            self.results_widget.clear_results()
            self.status_bar.showMessage(f"Selected folder: {folder_name} ({len(image_files)} images)")
    
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
        self.status_bar.showMessage("Processing photos...")
        
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
                self.undo_btn.setText(f"↩️ Undo Last Operation ({undo_count} available)")
        
        # Display results
        self.results_widget.display_results(results)
        
        # Update status
        self.status_bar.showMessage(f"Processing complete: {results['total_processed']} photos processed")
        
        # Show completion message
        QMessageBox.information(
            self, 
            "✅ Processing Complete", 
            "Photo organization finished!\n\n"
            f"📊 Processed {results['total_processed']} photos\n"
            f"🔄 Found {results['duplicate_photos']} duplicates\n"
            f"📷 Found {results['blurry_photos']} blurry photos\n"
            f"👤 Found {results['face_photos']} photos with faces"
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
                self.undo_btn.setText(f"↩️ Undo Last Operation ({undo_count} available)")
            else:
                self.undo_btn.setText("↩️ Undo Last Operation")
                self.undo_btn.setEnabled(False)
            self.status_bar.showMessage("Last operation undone")
        else:
            QMessageBox.warning(self, "Undo Failed", "No operations to undo or undo failed.")
    
    def clear_results(self):
        """Clear all results and reset the interface."""
        self.results_widget.clear_results()
        self.progress_widget.update_status("Ready to process photos")
        self.status_bar.showMessage("Results cleared")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About CLEAN SHOT",
            "CLEAN SHOT - AI Photo Organizer\n\n"
            "Version 2.0.0\n"
            "An intelligent photo organization tool with AI-powered detection.\n\n"
            "Features:\n"
            "• Blur detection\n"
            "• Duplicate detection\n"
            "• Face recognition\n"
            "• Undo functionality\n"
            "• Modern UI design"
        )
    
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
