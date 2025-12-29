# ========== Reusable GUI Components ==========
"""
Reusable GUI components for the CLEAN SHOT Photo Organizer.
Uses consolidated theme system from theme.py.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSpinBox, QCheckBox, QProgressBar,
    QFileDialog, QMessageBox, QGroupBox, QFrame,
    QSlider, QComboBox, QScrollArea, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor

from gui.theme import (
    DARK_THEME, LIGHT_THEME, ThemeManager,
    AnimatedButton, GlowCard, FadeLabel, PulseWidget,
    apply_modern_card_style, get_theme_css
)


def get_current_colors():
    """Get the current theme colors."""
    return ThemeManager.get_current_theme()


class SettingsWidget(QGroupBox):
    """Enhanced widget for application settings with modern styling."""
    
    def __init__(self, parent=None):
        super().__init__("⚙️ Detection Settings", parent)
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Setup the enhanced settings UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        colors = get_current_colors()
        
        # Blur detection section
        blur_frame = QFrame()
        blur_layout = QVBoxLayout(blur_frame)
        blur_layout.setSpacing(10)
        
        blur_label = QLabel("🔍 Blur Detection")
        blur_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {colors['PRIMARY']};
                background: transparent;
                border: none;
            }}
        """)
        blur_layout.addWidget(blur_label)
        
        blur_desc = QLabel("Detect and separate blurry/unfocused photos")
        blur_desc.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {colors['TEXT_SECONDARY']};
                background: transparent;
                border: none;
            }}
        """)
        blur_layout.addWidget(blur_desc)
        
        blur_control_layout = QHBoxLayout()
        threshold_label = QLabel("Threshold:")
        threshold_label.setStyleSheet("background: transparent; border: none;")
        blur_control_layout.addWidget(threshold_label)
        
        self.blur_threshold = QSpinBox()
        self.blur_threshold.setRange(0, 500)
        self.blur_threshold.setValue(100)
        self.blur_threshold.setToolTip("Lower values detect more blurry images (0-500)")
        self.blur_threshold.setFixedWidth(100)
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
                color: {colors['ACCENT']};
                background: transparent;
                border: none;
            }}
        """)
        duplicate_layout.addWidget(duplicate_label)
        
        dup_desc = QLabel("Find and group similar or duplicate photos")
        dup_desc.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {colors['TEXT_SECONDARY']};
                background: transparent;
                border: none;
            }}
        """)
        duplicate_layout.addWidget(dup_desc)
        
        duplicate_control_layout = QHBoxLayout()
        sim_label = QLabel("Similarity:")
        sim_label.setStyleSheet("background: transparent; border: none;")
        duplicate_control_layout.addWidget(sim_label)
        
        self.similarity_threshold = QSpinBox()
        self.similarity_threshold.setRange(0, 50)
        self.similarity_threshold.setValue(20)
        self.similarity_threshold.setToolTip("Lower values = stricter matching (0-50)")
        self.similarity_threshold.setFixedWidth(100)
        duplicate_control_layout.addWidget(self.similarity_threshold)
        duplicate_control_layout.addStretch()
        duplicate_layout.addLayout(duplicate_control_layout)
        
        # Similarity slider
        self.similarity_slider = QSlider(Qt.Horizontal)
        self.similarity_slider.setRange(0, 50)
        self.similarity_slider.setValue(20)
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
                color: {colors['SUCCESS']};
                background: transparent;
                border: none;
            }}
        """)
        face_layout.addWidget(face_label)
        
        face_desc = QLabel("Detect and categorize photos containing faces")
        face_desc.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {colors['TEXT_SECONDARY']};
                background: transparent;
                border: none;
            }}
        """)
        face_layout.addWidget(face_desc)
        
        self.face_checkbox = QCheckBox("Enable Face Detection")
        self.face_checkbox.setChecked(True)
        self.face_checkbox.setToolTip("Detect and copy photos with faces to a separate folder")
        face_layout.addWidget(self.face_checkbox)
        
        layout.addWidget(face_frame)
    
    def apply_styles(self):
        """Apply modern styles to the settings widget."""
        colors = get_current_colors()
        self.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: 600;
                color: {colors['TEXT_PRIMARY']};
                border: 1px solid {colors['BORDER']};
                border-radius: {colors['CARD_RADIUS']};
                margin-top: 1em;
                padding: 20px;
                padding-top: 1.5em;
                background: {colors['SURFACE']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }}
            QFrame {{
                background: transparent;
                border: none;
            }}
        """)
    
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
        layout.setContentsMargins(0, 0, 0, 0)
        
        colors = get_current_colors()
        
        # Progress bar with modern styling
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(20)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label with better styling
        self.status_label = QLabel("✅ Ready to process photos")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(40)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {colors['TEXT_PRIMARY']};
                padding: 10px;
            }}
        """)
        layout.addWidget(self.status_label)
        
        # Processing info label
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet(f"""
            QLabel {{
                color: {colors['TEXT_MUTED']};
                font-size: 12px;
            }}
        """)
        layout.addWidget(self.info_label)
    
    def apply_styles(self):
        """Apply modern styles to the progress widget."""
        pass  # Styles applied inline for this widget
    
    def show_progress(self, show=True):
        """Show or hide progress bar."""
        self.progress_bar.setVisible(show)
    
    def update_progress(self, value):
        """Update progress bar value."""
        self.progress_bar.setValue(value)
    
    def update_status(self, text):
        """Update status label text."""
        self.status_label.setText(text)
    
    def update_info(self, text):
        """Update info label text."""
        self.info_label.setText(text)


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
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Results container with scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        results_container = QWidget()
        results_container.setStyleSheet("background: transparent;")
        self.results_layout = QVBoxLayout(results_container)
        self.results_layout.setSpacing(10)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        
        # Results label with better formatting
        self.results_label = QLabel("")
        self.results_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.results_label.setWordWrap(True)
        self.results_label.setMinimumHeight(200)
        self.results_label.setTextFormat(Qt.RichText)
        self.results_layout.addWidget(self.results_label)
        self.results_layout.addStretch()
        
        scroll_area.setWidget(results_container)
        layout.addWidget(scroll_area)
    
    def apply_styles(self):
        """Apply modern styles to the results widget."""
        colors = get_current_colors()
        self.results_label.setStyleSheet(f"""
            QLabel {{
                color: {colors['TEXT_PRIMARY']};
                font-size: 14px;
                line-height: 1.5;
                padding: 15px;
                background-color: {colors['SURFACE']};
                border-radius: 12px;
                border: 1px solid {colors['BORDER']};
            }}
        """)
    
    def display_results(self, results):
        """Display processing results with enhanced formatting."""
        colors = get_current_colors()
        
        # Handle both dict and object-like access
        total = results.get('total_processed', results.get('total', 0))
        good = results.get('good_photos', results.get('good', 0))
        blurry = results.get('blurry_photos', results.get('blurry', 0))
        duplicates = results.get('duplicate_photos', results.get('duplicates', 0))
        faces = results.get('face_photos', results.get('faces', 0))
        
        results_text = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; color: {colors['TEXT_PRIMARY']};">
            <h3 style="color: {colors['SUCCESS']}; margin-bottom: 20px;">✅ Processing Complete!</h3>
            
            <table style="width: 100%; border-collapse: separate; border-spacing: 0 10px;">
                <tr>
                    <td style="background: {colors['SURFACE_LIGHT']}; padding: 15px; border-radius: 8px; border-left: 4px solid {colors['PRIMARY']};">
                        <div style="color: {colors['TEXT_SECONDARY']}; font-size: 12px;">📊 Total Photos</div>
                        <div style="font-size: 24px; font-weight: bold; color: {colors['TEXT_PRIMARY']};">{total}</div>
                    </td>
                    <td style="width: 10px;"></td>
                    <td style="background: {colors['SURFACE_LIGHT']}; padding: 15px; border-radius: 8px; border-left: 4px solid {colors['SUCCESS']};">
                        <div style="color: {colors['TEXT_SECONDARY']}; font-size: 12px;">✨ Good Photos</div>
                        <div style="font-size: 24px; font-weight: bold; color: {colors['SUCCESS']};">{good}</div>
                    </td>
                </tr>
                <tr>
                    <td style="background: {colors['SURFACE_LIGHT']}; padding: 15px; border-radius: 8px; border-left: 4px solid {colors['WARNING']};">
                        <div style="color: {colors['TEXT_SECONDARY']}; font-size: 12px;">📷 Blurry Photos</div>
                        <div style="font-size: 24px; font-weight: bold; color: {colors['WARNING']};">{blurry}</div>
                    </td>
                    <td style="width: 10px;"></td>
                    <td style="background: {colors['SURFACE_LIGHT']}; padding: 15px; border-radius: 8px; border-left: 4px solid {colors['DANGER']};">
                        <div style="color: {colors['TEXT_SECONDARY']}; font-size: 12px;">🔄 Duplicates</div>
                        <div style="font-size: 24px; font-weight: bold; color: {colors['DANGER']};">{duplicates}</div>
                    </td>
                </tr>
                <tr>
                    <td colspan="3" style="background: {colors['SURFACE_LIGHT']}; padding: 15px; border-radius: 8px; border-left: 4px solid {colors['ACCENT']};">
                        <div style="color: {colors['TEXT_SECONDARY']}; font-size: 12px;">👤 Photos with Faces</div>
                        <div style="font-size: 24px; font-weight: bold; color: {colors['ACCENT']};">{faces}</div>
                    </td>
                </tr>
            </table>
        </div>
        """
        
        self.results_label.setText(results_text)
    
    def clear_results(self):
        """Clear results display."""
        self.results_label.setText("")


class StatCard(GlowCard):
    """A styled card for displaying statistics."""
    
    def __init__(self, title: str, value: str = "0", icon: str = "📊", 
                 accent_color: str = None, parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon = icon
        self.accent_color = accent_color or get_current_colors()['PRIMARY']
        self.setup_ui()
    
    def setup_ui(self):
        colors = get_current_colors()
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 16, 20, 16)
        
        # Icon and title row
        header = QHBoxLayout()
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet(f"font-size: 20px; background: transparent;")
        header.addWidget(icon_label)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 500;
            color: {colors['TEXT_SECONDARY']};
            background: transparent;
        """)
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Value
        self.value_label = QLabel(str(self.value))
        self.value_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: 700;
            color: {self.accent_color};
            background: transparent;
        """)
        layout.addWidget(self.value_label)
        
        # Card styling
        self.setStyleSheet(f"""
            QFrame {{
                background: {colors['SURFACE']};
                border: 1px solid {colors['BORDER']};
                border-radius: 12px;
                border-left: 4px solid {self.accent_color};
            }}
        """)
    
    def set_value(self, value):
        """Update the displayed value."""
        self.value = value
        self.value_label.setText(str(value))


class ActionButton(AnimatedButton):
    """Pre-styled action button with variant support."""
    
    def __init__(self, text: str, variant: str = "primary", parent=None):
        super().__init__(text, parent)
        self.setProperty("variant", variant)
        self.setCursor(Qt.PointingHandCursor)


# Re-export animated widgets for convenience
__all__ = [
    'SettingsWidget',
    'ProgressWidget', 
    'ResultsWidget',
    'StatCard',
    'ActionButton',
    'AnimatedButton',
    'GlowCard',
    'FadeLabel',
    'PulseWidget',
    'get_current_colors',
]
