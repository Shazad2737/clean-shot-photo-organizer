"""
Reusable GUI components for the photo organizer.
"""

import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QSpinBox, QCheckBox, QProgressBar,
                               QFileDialog, QMessageBox, QGroupBox, QFrame,
                               QSlider, QComboBox, QScrollArea)
from PySide6.QtCore import Qt
from gui.simple_beautiful_styles import WIDGET_STYLES, COLORS, BUTTON_STYLES


class SettingsWidget(QGroupBox):
    """Enhanced widget for application settings."""
    
    def __init__(self, parent=None):
        super().__init__("⚙️ Detection Settings", parent)
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Setup the enhanced settings UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Blur detection section
        blur_frame = QFrame()
        blur_layout = QVBoxLayout(blur_frame)
        blur_layout.setSpacing(10)
        
        blur_label = QLabel("🔍 Blur Detection")
        blur_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {COLORS['primary']};
            }}
        """)
        blur_layout.addWidget(blur_label)
        
        blur_control_layout = QHBoxLayout()
        blur_control_layout.addWidget(QLabel("Threshold:"))
        self.blur_threshold = QSpinBox()
        self.blur_threshold.setRange(0, 500)
        self.blur_threshold.setValue(100)
        self.blur_threshold.setToolTip("Lower values detect more blurry images (0-500)")
        blur_control_layout.addWidget(self.blur_threshold)
        blur_control_layout.addStretch()
        blur_layout.addLayout(blur_control_layout)
        
        # Blur slider for better control
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(0, 500)
        self.blur_slider.setValue(100)
        self.blur_slider.valueChanged.connect(self.blur_threshold.setValue)
        self.blur_threshold.valueChanged.connect(self.blur_slider.setValue)
        blur_layout.addWidget(self.blur_slider)
        
        layout.addWidget(blur_frame)
        
        # Duplicate detection section
        duplicate_frame = QFrame()
        duplicate_layout = QVBoxLayout(duplicate_frame)
        duplicate_layout.setSpacing(10)
        
        duplicate_label = QLabel("🔄 Duplicate Detection")
        duplicate_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {COLORS['primary']};
            }}
        """)
        duplicate_layout.addWidget(duplicate_label)
        
        duplicate_control_layout = QHBoxLayout()
        duplicate_control_layout.addWidget(QLabel("Similarity:"))
        self.similarity_threshold = QSpinBox()
        self.similarity_threshold.setRange(0, 20)
        self.similarity_threshold.setValue(5)
        self.similarity_threshold.setToolTip("Lower values detect more similar images as duplicates (0-20)")
        duplicate_control_layout.addWidget(self.similarity_threshold)
        duplicate_control_layout.addStretch()
        duplicate_layout.addLayout(duplicate_control_layout)
        
        # Similarity slider
        self.similarity_slider = QSlider(Qt.Horizontal)
        self.similarity_slider.setRange(0, 20)
        self.similarity_slider.setValue(5)
        self.similarity_slider.valueChanged.connect(self.similarity_threshold.setValue)
        self.similarity_threshold.valueChanged.connect(self.similarity_slider.setValue)
        duplicate_layout.addWidget(self.similarity_slider)
        
        layout.addWidget(duplicate_frame)
        
        # Face detection section
        face_frame = QFrame()
        face_layout = QVBoxLayout(face_frame)
        face_layout.setSpacing(10)
        
        face_label = QLabel("👤 Face Detection")
        face_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {COLORS['primary']};
            }}
        """)
        face_layout.addWidget(face_label)
        
        self.face_checkbox = QCheckBox("Enable Face Detection")
        self.face_checkbox.setChecked(True)
        self.face_checkbox.setToolTip("Detect and copy photos with faces to a separate folder")
        face_layout.addWidget(self.face_checkbox)
        
        layout.addWidget(face_frame)
    
    def apply_styles(self):
        """Apply modern styles to the settings widget."""
        self.setStyleSheet(WIDGET_STYLES['group_box'])
    
    def get_settings(self):
        """Get current settings values."""
        return {
            'blur_threshold': self.blur_threshold.value(),
            'similarity_threshold': self.similarity_threshold.value(),
            'enable_face_detection': self.face_checkbox.isChecked()
        }


class ProgressWidget(QWidget):
    """Enhanced widget for displaying progress and status."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Setup the enhanced progress UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Progress bar with modern styling
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(25)
        layout.addWidget(self.progress_bar)
        
        # Status label with better styling
        self.status_label = QLabel("✅ Ready to process photos")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(40)
        layout.addWidget(self.status_label)
        
        # Processing info label
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_light']};
                font-size: 12px;
            }}
        """)
        layout.addWidget(self.info_label)
    
    def apply_styles(self):
        """Apply modern styles to the progress widget."""
        self.progress_bar.setStyleSheet(WIDGET_STYLES['progress_bar'])
        self.status_label.setStyleSheet(WIDGET_STYLES['label'])
    
    def show_progress(self, show=True):
        """Show or hide progress bar."""
        self.progress_bar.setVisible(show)
    
    def update_progress(self, value):
        """Update progress bar value."""
        self.progress_bar.setValue(value)
    
    def update_status(self, text):
        """Update status label text."""
        self.status_label.setText(text)


class ResultsWidget(QWidget):
    """Enhanced widget for displaying processing results."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Setup the enhanced results UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Results container with scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        
        results_container = QWidget()
        self.results_layout = QVBoxLayout(results_container)
        self.results_layout.setSpacing(10)
        
        # Results label with better formatting
        self.results_label = QLabel("")
        self.results_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.results_label.setWordWrap(True)
        self.results_label.setMinimumHeight(200)
        self.results_layout.addWidget(self.results_label)
        
        scroll_area.setWidget(results_container)
        layout.addWidget(scroll_area)
    
    def apply_styles(self):
        """Apply modern styles to the results widget."""
        self.results_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                font-size: 14px;
                line-height: 1.5;
                padding: 15px;
                background-color: {COLORS['light']};
                border-radius: 8px;
            }}
        """)
    
    def display_results(self, results):
        """Display processing results with enhanced formatting."""
        # Create formatted results with icons and better layout
        results_text = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif;">
            <h3 style="color: {COLORS['success']}; margin-bottom: 20px;">✅ Processing Complete!</h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                <div style="background-color: {COLORS['surface']}; padding: 15px; border-radius: 8px; border-left: 4px solid {COLORS['primary']};">
                    <h4 style="color: {COLORS['primary']}; margin: 0 0 5px 0;">📊 Total Photos</h4>
                    <p style="font-size: 24px; font-weight: bold; color: {COLORS['success']}; margin: 0;">{results['total_processed']}</p>
                </div>
                
                <div style="background-color: {COLORS['surface']}; padding: 15px; border-radius: 8px; border-left: 4px solid {COLORS['success']};">
                    <h4 style="color: {COLORS['primary']}; margin: 0 0 5px 0;">✨ Good Photos</h4>
                    <p style="font-size: 24px; font-weight: bold; color: {COLORS['success']}; margin: 0;">{results['good_photos']}</p>
                </div>
                
                <div style="background-color: {COLORS['surface']}; padding: 15px; border-radius: 8px; border-left: 4px solid {COLORS['warning']};">
                    <h4 style="color: {COLORS['primary']}; margin: 0 0 5px 0;">📷 Blurry Photos</h4>
                    <p style="font-size: 24px; font-weight: bold; color: {COLORS['warning']}; margin: 0;">{results['blurry_photos']}</p>
                </div>
                
                <div style="background-color: {COLORS['surface']}; padding: 15px; border-radius: 8px; border-left: 4px solid {COLORS['danger']};">
                    <h4 style="color: {COLORS['primary']}; margin: 0 0 5px 0;">🔄 Duplicate Photos</h4>
                    <p style="font-size: 24px; font-weight: bold; color: {COLORS['danger']}; margin: 0;">{results['duplicate_photos']}</p>
                </div>
            </div>
            
            <div style="background-color: {COLORS['surface']}; padding: 15px; border-radius: 8px; border-left: 4px solid {COLORS['secondary']};">
                <h4 style="color: {COLORS['primary']}; margin: 0 0 5px 0;">👤 Photos with Faces</h4>
                <p style="font-size: 24px; font-weight: bold; color: {COLORS['secondary']}; margin: 0;">{results['face_photos']}</p>
            </div>
        </div>
        """
        
        self.results_label.setText(results_text)
    
    def clear_results(self):
        """Clear results display."""
        self.results_label.setText("")
