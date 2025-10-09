"""
Simple but beautiful main window that works with Qt.
"""

import os
import logging
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                               QPushButton, QFileDialog, QMessageBox, QLabel,
                               QFrame, QSpacerItem, QSizePolicy, QMenuBar, QStatusBar,
                               QSplitter, QScrollArea, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon, QAction, QColor

from core.photo_processor import PhotoProcessor
from utils.validators import InputValidator
from gui.components import SettingsWidget, ProgressWidget, ResultsWidget
from gui.simple_beautiful_styles import APPLICATION_STYLE, BUTTON_STYLES, WIDGET_STYLES, COLORS


class SimpleBeautifulWindow(QMainWindow):
    """Simple but beautiful main application window."""
    
    def __init__(self):
        super().__init__()
        self.current_folder = ""
        self.processor = None
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.apply_beautiful_styles()
    
    def setup_ui(self):
        """Setup the beautiful UI."""
        self.setWindowTitle("📸 CLEAN SHOT - AI Photo Organizer")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(900, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # Beautiful header section
        self.create_beautiful_header(main_layout)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(3)
        main_layout.addWidget(splitter)
        
        # Left panel (settings and controls)
        left_panel = self.create_beautiful_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel (progress and results)
        right_panel = self.create_beautiful_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 600])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
    
    def create_beautiful_header(self, layout):
        """Create a beautiful header section."""
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary']};
                border-radius: 16px;
                padding: 25px;
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(102, 126, 234, 50))
        shadow.setOffset(0, 5)
        header_frame.setGraphicsEffect(shadow)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(15)
        
        # Beautiful title
        title_label = QLabel("📸 CLEAN SHOT")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                font-weight: 800;
                color: {COLORS['white']};
                margin-bottom: 10px;
            }}
        """)
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Beautiful subtitle
        subtitle_label = QLabel("AI-Powered Photo Organization")
        subtitle_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: 500;
                color: rgba(255, 255, 255, 0.9);
                margin-bottom: 20px;
            }}
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        # Beautiful folder selection
        folder_layout = QHBoxLayout()
        folder_layout.setSpacing(15)
        
        self.folder_label = QLabel("📁 No folder selected")
        self.folder_label.setStyleSheet(WIDGET_STYLES['folder_display'])
        self.folder_label.setWordWrap(True)
        
        self.select_btn = QPushButton("📂 Browse Folder")
        self.select_btn.setStyleSheet(BUTTON_STYLES['secondary'])
        self.select_btn.clicked.connect(self.select_folder)
        
        folder_layout.addWidget(self.folder_label, 1)
        folder_layout.addWidget(self.select_btn)
        
        header_layout.addLayout(folder_layout)
        layout.addWidget(header_frame)
    
    def create_beautiful_left_panel(self):
        """Create beautiful left panel with settings and controls."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(20)
        
        # Beautiful settings section
        settings_frame = QFrame()
        settings_frame.setStyleSheet(WIDGET_STYLES['card'])
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 3)
        settings_frame.setGraphicsEffect(shadow)
        
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setSpacing(20)
        settings_layout.setContentsMargins(20, 20, 20, 20)
        
        # Settings title
        settings_title = QLabel("⚙️ Detection Settings")
        settings_title.setStyleSheet(WIDGET_STYLES['label_title'])
        settings_title.setAlignment(Qt.AlignCenter)
        settings_layout.addWidget(settings_title)
        
        # Enhanced settings widget
        self.settings_widget = SettingsWidget()
        self.settings_widget.setStyleSheet("QGroupBox { border: none; }")
        settings_layout.addWidget(self.settings_widget)
        
        left_layout.addWidget(settings_frame)
        
        # Beautiful action buttons
        button_frame = QFrame()
        button_frame.setStyleSheet(WIDGET_STYLES['card'])
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 3)
        button_frame.setGraphicsEffect(shadow)
        
        button_layout = QVBoxLayout(button_frame)
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(20, 20, 20, 20)
        
        # Action buttons title
        actions_title = QLabel("🎯 Actions")
        actions_title.setStyleSheet(WIDGET_STYLES['label_title'])
        actions_title.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(actions_title)
        
        # Process button with beautiful styling
        self.process_btn = QPushButton("🚀 Start Processing")
        self.process_btn.setStyleSheet(BUTTON_STYLES['primary'])
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
    
    def create_beautiful_right_panel(self):
        """Create beautiful right panel with progress and results."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(20)
        
        # Beautiful progress section
        progress_frame = QFrame()
        progress_frame.setStyleSheet(WIDGET_STYLES['card'])
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 3)
        progress_frame.setGraphicsEffect(shadow)
        
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setSpacing(20)
        progress_layout.setContentsMargins(20, 20, 20, 20)
        
        # Progress title
        progress_title = QLabel("📊 Processing Status")
        progress_title.setStyleSheet(WIDGET_STYLES['label_title'])
        progress_title.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(progress_title)
        
        # Enhanced progress widget
        self.progress_widget = ProgressWidget()
        self.progress_widget.setStyleSheet("QWidget { background-color: transparent; }")
        progress_layout.addWidget(self.progress_widget)
        
        right_layout.addWidget(progress_frame)
        
        # Beautiful results section
        results_frame = QFrame()
        results_frame.setStyleSheet(WIDGET_STYLES['card'])
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 3)
        results_frame.setGraphicsEffect(shadow)
        
        results_layout = QVBoxLayout(results_frame)
        results_layout.setSpacing(20)
        results_layout.setContentsMargins(20, 20, 20, 20)
        
        # Results title
        results_title = QLabel("📈 Processing Results")
        results_title.setStyleSheet(WIDGET_STYLES['label_title'])
        results_title.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(results_title)
        
        # Enhanced results widget
        self.results_widget = ResultsWidget()
        self.results_widget.setStyleSheet("QWidget { background-color: transparent; }")
        results_layout.addWidget(self.results_widget)
        
        right_layout.addWidget(results_frame)
        
        return right_widget
    
    def setup_menu(self):
        """Setup beautiful application menu bar."""
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {COLORS['white']};
                border-bottom: 1px solid {COLORS['gray_light']};
                padding: 8px;
                font-weight: 500;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 6px;
                color: {COLORS['text_primary']};
            }}
            QMenuBar::item:selected {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['primary']};
            }}
        """)
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        open_action = QAction('📂 &Open Folder', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.select_folder)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('🚪 E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('&Edit')
        
        undo_action = QAction('↩️ &Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.undo_last_operation)
        edit_menu.addAction(undo_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('ℹ️ &About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup beautiful status bar."""
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {COLORS['white']};
                border-top: 1px solid {COLORS['gray_light']};
                color: {COLORS['text_secondary']};
                font-size: 13px;
                font-weight: 500;
                padding: 8px;
            }}
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✨ Ready to organize your photos with AI")
    
    def apply_beautiful_styles(self):
        """Apply beautiful modern styles."""
        self.setStyleSheet(APPLICATION_STYLE)
    
    def select_folder(self):
        """Select folder with beautiful feedback."""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "📂 Select Photo Folder",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder:
            # Validate folder
            is_valid, error_msg = InputValidator.validate_folder_path(folder)
            if not is_valid:
                QMessageBox.warning(self, "⚠️ Invalid Folder", error_msg)
                return
            
            # Check for image files
            has_images, error_msg, image_files = InputValidator.validate_image_files(folder)
            if not has_images:
                QMessageBox.warning(self, "📷 No Images", error_msg)
                return
            
            self.current_folder = folder
            folder_name = os.path.basename(folder)
            self.folder_label.setText(f"📁 {folder_name} ({len(image_files)} images)")
            self.folder_label.setStyleSheet(WIDGET_STYLES['folder_display_selected'])
            self.process_btn.setEnabled(True)
            self.progress_widget.update_status(f"✅ Folder selected with {len(image_files)} images. Ready to process!")
            self.results_widget.clear_results()
            self.status_bar.showMessage(f"📁 Selected: {folder_name} ({len(image_files)} images)")
    
    def start_processing(self):
        """Start processing with beautiful feedback."""
        if not self.current_folder:
            QMessageBox.warning(self, "⚠️ Error", "Please select a folder first.")
            return
        
        # Get and validate settings
        settings = self.settings_widget.get_settings()
        is_valid, error_msg = InputValidator.validate_thresholds(
            settings['blur_threshold'], 
            settings['similarity_threshold']
        )
        if not is_valid:
            QMessageBox.warning(self, "⚠️ Invalid Settings", error_msg)
            return
        
        # Disable UI during processing
        self.process_btn.setEnabled(False)
        self.undo_btn.setEnabled(False)
        self.select_btn.setEnabled(False)
        self.progress_widget.show_progress(True)
        self.results_widget.clear_results()
        self.status_bar.showMessage("🔄 Processing photos with AI...")
        
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
        """Handle processing completion with beautiful feedback."""
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
        self.status_bar.showMessage(f"✅ Processing complete: {results['total_processed']} photos organized")
        
        # Show beautiful completion message
        QMessageBox.information(
            self, 
            "🎉 Processing Complete!", 
            "✨ Photo organization finished!\n\n"
            f"📊 Processed {results['total_processed']} photos\n"
            f"🔄 Found {results['duplicate_photos']} duplicates\n"
            f"📷 Found {results['blurry_photos']} blurry photos\n"
            f"👤 Found {results['face_photos']} photos with faces\n\n"
            "🎯 Your photos are now beautifully organized!"
        )
    
    def undo_last_operation(self):
        """Undo with beautiful feedback."""
        if not self.processor or not hasattr(self.processor, 'file_manager'):
            QMessageBox.warning(self, "⚠️ No Operations", "No operations to undo.")
            return
        
        if self.processor.file_manager.undo_last_operation():
            QMessageBox.information(self, "↩️ Undo Complete", "Last operation has been undone.")
            # Update undo button
            undo_count = self.processor.file_manager.get_undo_count()
            if undo_count > 0:
                self.undo_btn.setText(f"↩️ Undo Last Operation ({undo_count} available)")
            else:
                self.undo_btn.setText("↩️ Undo Last Operation")
                self.undo_btn.setEnabled(False)
            self.status_bar.showMessage("↩️ Last operation undone")
        else:
            QMessageBox.warning(self, "❌ Undo Failed", "No operations to undo or undo failed.")
    
    def clear_results(self):
        """Clear results with beautiful feedback."""
        self.results_widget.clear_results()
        self.progress_widget.update_status("✨ Ready to process photos")
        self.status_bar.showMessage("🗑️ Results cleared")
    
    def show_about(self):
        """Show beautiful about dialog."""
        QMessageBox.about(
            self,
            "ℹ️ About CLEAN SHOT",
            "📸 CLEAN SHOT - AI Photo Organizer\n\n"
            "Version 2.0.0\n"
            "✨ Beautiful AI-powered photo organization\n\n"
            "🎯 Features:\n"
            "• 🔍 Advanced blur detection\n"
            "• 🔄 Smart duplicate detection\n"
            "• 👤 Face recognition\n"
            "• ↩️ Undo functionality\n"
            "• 🎨 Beautiful modern UI\n\n"
            "Made with ❤️ for photo enthusiasts"
        )
    
    def closeEvent(self, event):
        """Handle application close with confirmation."""
        if self.processor and self.processor.isRunning():
            reply = QMessageBox.question(
                self, 
                "🚪 Exit Application",
                "🔄 Processing is still running.\nAre you sure you want to exit?",
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
