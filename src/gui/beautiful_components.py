"""
Beautiful, modern GUI components with stunning visual design.
"""

import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QSpinBox, QCheckBox, QProgressBar,
                               QFileDialog, QMessageBox, QGroupBox, QFrame,
                               QSlider, QComboBox, QScrollArea, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QColor, QFont, QPalette
from gui.modern_styles import WIDGET_STYLES, COLORS, GRADIENTS, BUTTON_STYLES


class BeautifulSettingsWidget(QGroupBox):
    """Beautiful settings widget with modern design."""
    
    def __init__(self, parent=None):
        super().__init__("⚙️ Detection Settings", parent)
        self.setup_ui()
        self.apply_beautiful_styles()
    
    def setup_ui(self):
        """Setup the beautiful settings UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        
        # Blur detection section
        blur_frame = QFrame()
        blur_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['white']};
                border: 2px solid {COLORS['primary_light']};
                border-radius: 16px;
                padding: 20px;
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(102, 126, 234, 30))
        shadow.setOffset(0, 4)
        blur_frame.setGraphicsEffect(shadow)
        
        blur_layout = QVBoxLayout(blur_frame)
        blur_layout.setSpacing(15)
        
        blur_label = QLabel("🔍 Blur Detection")
        blur_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: 700;
                color: {COLORS['primary']};
                margin-bottom: 10px;
            }}
        """)
        blur_layout.addWidget(blur_label)
        
        blur_control_layout = QHBoxLayout()
        blur_control_layout.addWidget(QLabel("Threshold:"))
        self.blur_threshold = QSpinBox()
        self.blur_threshold.setRange(0, 500)
        self.blur_threshold.setValue(100)
        self.blur_threshold.setToolTip("Lower values detect more blurry images (0-500)")
        self.blur_threshold.setStyleSheet(WIDGET_STYLES['spin_box'])
        blur_control_layout.addWidget(self.blur_threshold)
        blur_control_layout.addStretch()
        blur_layout.addLayout(blur_control_layout)
        
        # Beautiful blur slider
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(0, 500)
        self.blur_slider.setValue(100)
        self.blur_slider.setStyleSheet(WIDGET_STYLES['slider'])
        self.blur_slider.valueChanged.connect(self.blur_threshold.setValue)
        self.blur_threshold.valueChanged.connect(self.blur_slider.setValue)
        blur_layout.addWidget(self.blur_slider)
        
        layout.addWidget(blur_frame)
        
        # Duplicate detection section
        duplicate_frame = QFrame()
        duplicate_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['white']};
                border: 2px solid {COLORS['warning']};
                border-radius: 16px;
                padding: 20px;
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(237, 137, 54, 30))
        shadow.setOffset(0, 4)
        duplicate_frame.setGraphicsEffect(shadow)
        
        duplicate_layout = QVBoxLayout(duplicate_frame)
        duplicate_layout.setSpacing(15)
        
        duplicate_label = QLabel("🔄 Duplicate Detection")
        duplicate_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: 700;
                color: {COLORS['warning']};
                margin-bottom: 10px;
            }}
        """)
        duplicate_layout.addWidget(duplicate_label)
        
        duplicate_control_layout = QHBoxLayout()
        duplicate_control_layout.addWidget(QLabel("Similarity:"))
        self.similarity_threshold = QSpinBox()
        self.similarity_threshold.setRange(0, 20)
        self.similarity_threshold.setValue(5)
        self.similarity_threshold.setToolTip("Lower values detect more similar images as duplicates (0-20)")
        self.similarity_threshold.setStyleSheet(WIDGET_STYLES['spin_box'])
        duplicate_control_layout.addWidget(self.similarity_threshold)
        duplicate_control_layout.addStretch()
        duplicate_layout.addLayout(duplicate_control_layout)
        
        # Beautiful similarity slider
        self.similarity_slider = QSlider(Qt.Horizontal)
        self.similarity_slider.setRange(0, 20)
        self.similarity_slider.setValue(5)
        self.similarity_slider.setStyleSheet(WIDGET_STYLES['slider'])
        self.similarity_slider.valueChanged.connect(self.similarity_threshold.setValue)
        self.similarity_threshold.valueChanged.connect(self.similarity_slider.setValue)
        duplicate_layout.addWidget(self.similarity_slider)
        
        layout.addWidget(duplicate_frame)
        
        # Face detection section
        face_frame = QFrame()
        face_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['white']};
                border: 2px solid {COLORS['success']};
                border-radius: 16px;
                padding: 20px;
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(72, 187, 120, 30))
        shadow.setOffset(0, 4)
        face_frame.setGraphicsEffect(shadow)
        
        face_layout = QVBoxLayout(face_frame)
        face_layout.setSpacing(15)
        
        face_label = QLabel("👤 Face Detection")
        face_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: 700;
                color: {COLORS['success']};
                margin-bottom: 10px;
            }}
        """)
        face_layout.addWidget(face_label)
        
        self.face_checkbox = QCheckBox("Enable Face Detection")
        self.face_checkbox.setChecked(True)
        self.face_checkbox.setToolTip("Detect and copy photos with faces to a separate folder")
        self.face_checkbox.setStyleSheet(WIDGET_STYLES['check_box'])
        face_layout.addWidget(self.face_checkbox)
        
        layout.addWidget(face_frame)
    
    def apply_beautiful_styles(self):
        """Apply beautiful modern styles."""
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 700;
                font-size: 20px;
                color: {COLORS['text_primary']};
                border: none;
                margin-top: 15px;
                padding-top: 15px;
                background: transparent;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 12px 0 12px;
                background: {COLORS['white']};
                color: {COLORS['primary']};
            }}
        """)
    
    def get_settings(self):
        """Get current settings values."""
        return {
            'blur_threshold': self.blur_threshold.value(),
            'similarity_threshold': self.similarity_threshold.value(),
            'enable_face_detection': self.face_checkbox.isChecked()
        }


class BeautifulProgressWidget(QWidget):
    """Beautiful progress widget with modern design."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.apply_beautiful_styles()
    
    def setup_ui(self):
        """Setup the beautiful progress UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Beautiful progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setStyleSheet(WIDGET_STYLES['progress_bar'])
        layout.addWidget(self.progress_bar)
        
        # Beautiful status label
        self.status_label = QLabel("✨ Ready to process photos")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(50)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {COLORS['text_primary']};
                padding: 15px;
                background: {COLORS['light']};
                border-radius: 12px;
                border: 2px solid {COLORS['primary_light']};
            }}
        """)
        layout.addWidget(self.status_label)
        
        # Processing info label
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 13px;
                font-weight: 500;
            }}
        """)
        layout.addWidget(self.info_label)
    
    def apply_beautiful_styles(self):
        """Apply beautiful modern styles."""
        pass  # Styles applied in setup_ui
    
    def show_progress(self, show=True):
        """Show or hide progress bar."""
        self.progress_bar.setVisible(show)
    
    def update_progress(self, value):
        """Update progress bar value."""
        self.progress_bar.setValue(value)
    
    def update_status(self, text):
        """Update status label text."""
        self.status_label.setText(text)


class BeautifulResultsWidget(QWidget):
    """Beautiful results widget with stunning visual design."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.apply_beautiful_styles()
    
    def setup_ui(self):
        """Setup the beautiful results UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Beautiful results container with scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(102, 126, 234, 0.3);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(102, 126, 234, 0.5);
            }
        """)
        
        results_container = QWidget()
        self.results_layout = QVBoxLayout(results_container)
        self.results_layout.setSpacing(15)
        
        # Beautiful results label
        self.results_label = QLabel("")
        self.results_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.results_label.setWordWrap(True)
        self.results_label.setMinimumHeight(300)
        self.results_label.setStyleSheet(WIDGET_STYLES['results_display'])
        self.results_layout.addWidget(self.results_label)
        
        scroll_area.setWidget(results_container)
        layout.addWidget(scroll_area)
    
    def apply_beautiful_styles(self):
        """Apply beautiful modern styles."""
        pass  # Styles applied in setup_ui
    
    def display_results(self, results):
        """Display processing results with stunning visual formatting."""
        # Create beautiful HTML results with modern design
        results_text = f"""
        <div style="font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: {COLORS['success']}; font-size: 28px; font-weight: 700; margin: 0 0 10px 0;">
                    ✨ Processing Complete!
                </h2>
                <p style="color: {COLORS['text_secondary']}; font-size: 16px; margin: 0;">
                    Your photos have been beautifully organized
                </p>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div style="background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['primary_dark']}); padding: 25px; border-radius: 16px; text-align: center; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);">
                    <div style="font-size: 32px; margin-bottom: 10px;">📊</div>
                    <h3 style="color: white; margin: 0 0 8px 0; font-size: 18px; font-weight: 600;">Total Photos</h3>
                    <p style="font-size: 36px; font-weight: 800; color: white; margin: 0;">{results['total_processed']}</p>
                </div>
                
                <div style="background: linear-gradient(135deg, {COLORS['success']}, #38a169); padding: 25px; border-radius: 16px; text-align: center; box-shadow: 0 8px 25px rgba(72, 187, 120, 0.2);">
                    <div style="font-size: 32px; margin-bottom: 10px;">✨</div>
                    <h3 style="color: white; margin: 0 0 8px 0; font-size: 18px; font-weight: 600;">Good Photos</h3>
                    <p style="font-size: 36px; font-weight: 800; color: white; margin: 0;">{results['good_photos']}</p>
                </div>
                
                <div style="background: linear-gradient(135deg, {COLORS['warning']}, #dd6b20); padding: 25px; border-radius: 16px; text-align: center; box-shadow: 0 8px 25px rgba(237, 137, 54, 0.2);">
                    <div style="font-size: 32px; margin-bottom: 10px;">📷</div>
                    <h3 style="color: white; margin: 0 0 8px 0; font-size: 18px; font-weight: 600;">Blurry Photos</h3>
                    <p style="font-size: 36px; font-weight: 800; color: white; margin: 0;">{results['blurry_photos']}</p>
                </div>
                
                <div style="background: linear-gradient(135deg, {COLORS['danger']}, #e53e3e); padding: 25px; border-radius: 16px; text-align: center; box-shadow: 0 8px 25px rgba(245, 101, 101, 0.2);">
                    <div style="font-size: 32px; margin-bottom: 10px;">🔄</div>
                    <h3 style="color: white; margin: 0 0 8px 0; font-size: 18px; font-weight: 600;">Duplicate Photos</h3>
                    <p style="font-size: 36px; font-weight: 800; color: white; margin: 0;">{results['duplicate_photos']}</p>
                </div>
            </div>
            
            <div style="background: linear-gradient(135deg, {COLORS['info']}, #3182ce); padding: 25px; border-radius: 16px; text-align: center; box-shadow: 0 8px 25px rgba(66, 153, 225, 0.2); margin-bottom: 20px;">
                <div style="font-size: 32px; margin-bottom: 10px;">👤</div>
                <h3 style="color: white; margin: 0 0 8px 0; font-size: 18px; font-weight: 600;">Photos with Faces</h3>
                <p style="font-size: 36px; font-weight: 800; color: white; margin: 0;">{results['face_photos']}</p>
            </div>
            
            <div style="text-align: center; padding: 20px; background: {COLORS['light']}; border-radius: 12px; border-left: 4px solid {COLORS['success']};">
                <p style="color: {COLORS['text_primary']}; font-size: 16px; font-weight: 600; margin: 0;">
                    🎯 Your photos are now beautifully organized and ready to enjoy!
                </p>
            </div>
        </div>
        """
        
        self.results_label.setText(results_text)
    
    def clear_results(self):
        """Clear results display."""
        self.results_label.setText("")
