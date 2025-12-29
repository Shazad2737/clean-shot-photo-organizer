# ========== Modern Redesigned Main Window ==========
"""
Premium redesigned UI for CLEAN SHOT Photo Organizer.
Features: Sidebar navigation, drag-drop zone, photo preview grid, live stats panel.
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QProgressBar,
    QFileDialog, QMessageBox, QStackedWidget, QSpinBox,
    QGraphicsDropShadowEffect, QSizePolicy, QSlider, QCheckBox,
    QToolTip, QApplication
)
from PySide6.QtCore import (
    Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer,
    QSize, QMimeData, QPoint, QRect
)
from PySide6.QtGui import (
    QColor, QPalette, QFont, QPixmap, QPainter, QBrush, QPen,
    QDragEnterEvent, QDropEvent, QLinearGradient, QIcon
)

from gui.theme import (
    DARK_THEME, LIGHT_THEME, ThemeManager, get_theme_css,
    AnimatedButton, GlowCard, FadeLabel, PulseWidget
)
from gui.icons import IconManager, get_icon, get_pixmap

# ========== Constants ==========

SIDEBAR_WIDTH = 72
SIDEBAR_EXPANDED_WIDTH = 200
STATS_PANEL_WIDTH = 280


# ========== Sidebar Navigation ==========

class SidebarButton(QPushButton):
    """Animated sidebar navigation button with icon and tooltip."""
    
    def __init__(self, icon_name: str, tooltip: str, parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self.tooltip_text = tooltip
        self._is_active = False
        self.setFixedSize(56, 56)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(tooltip)
        self.update_style()
        
        # Animation
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def update_style(self):
        theme = ThemeManager.get_current_theme()
        if self._is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {theme['PRIMARY']}, stop:1 {theme['ACCENT']});
                    border: none;
                    border-radius: 12px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {theme['PRIMARY_LIGHT']}, stop:1 {theme['ACCENT_LIGHT']});
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 12px;
                }}
                QPushButton:hover {{
                    background: {theme['SURFACE_LIGHT']};
                }}
            """)
        
        # Update icon
        color = "#FFFFFF" if self._is_active else theme['TEXT_SECONDARY']
        self.setIcon(get_icon(self.icon_name, 24, color))
        self.setIconSize(QSize(24, 24))
    
    def set_active(self, active: bool):
        self._is_active = active
        self.update_style()


class Sidebar(QFrame):
    """Modern sidebar navigation with icon buttons."""
    
    navigation_clicked = Signal(int)  # Emits index of clicked item
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(SIDEBAR_WIDTH)
        self.buttons: List[SidebarButton] = []
        self.setup_ui()
    
    def setup_ui(self):
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            QFrame {{
                background: {theme['SURFACE']};
                border-right: 1px solid {theme['BORDER']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(8)
        
        # Logo
        logo_btn = QPushButton()
        logo_btn.setFixedSize(56, 56)
        logo_btn.setIcon(get_icon("camera", 28, theme['PRIMARY']))
        logo_btn.setIconSize(QSize(28, 28))
        logo_btn.setStyleSheet(f"""
            QPushButton {{
                background: {theme['SURFACE_LIGHT']};
                border: none;
                border-radius: 12px;
            }}
        """)
        logo_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(logo_btn, 0, Qt.AlignCenter)
        
        layout.addSpacing(20)
        
        # Navigation buttons
        nav_items = [
            ("folder_open", "Organize Photos"),
            ("user", "Face Search"),
            ("clock", "History"),
            ("settings", "Settings"),
        ]
        
        for i, (icon, tooltip) in enumerate(nav_items):
            btn = SidebarButton(icon, tooltip)
            btn.clicked.connect(lambda checked, idx=i: self._on_button_clicked(idx))
            self.buttons.append(btn)
            layout.addWidget(btn, 0, Qt.AlignCenter)
        
        # Set first button active
        if self.buttons:
            self.buttons[0].set_active(True)
        
        layout.addStretch()
        
        # Theme toggle at bottom
        theme_btn = SidebarButton("moon", "Toggle Theme")
        theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(theme_btn, 0, Qt.AlignCenter)
        
        # Help button
        help_btn = SidebarButton("help", "Help & About")
        layout.addWidget(help_btn, 0, Qt.AlignCenter)
    
    def _on_button_clicked(self, index: int):
        for i, btn in enumerate(self.buttons):
            btn.set_active(i == index)
        self.navigation_clicked.emit(index)
    
    def _toggle_theme(self):
        ThemeManager.toggle_theme()
        # Would need to refresh the whole app styling


# ========== Drag & Drop Zone ==========

class DropZone(QFrame):
    """Animated drag-and-drop zone for folder selection."""
    
    folder_selected = Signal(str)  # Emits selected folder path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(200)
        self._is_hovering = False
        self.setup_ui()
        
        # Pulse animation for border
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._update_pulse)
        self._pulse_value = 0
        self._pulse_direction = 1
    
    def setup_ui(self):
        theme = ThemeManager.get_current_theme()
        self.update_style()
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)
        
        # Icon
        self.icon_label = QLabel()
        self.icon_label.setPixmap(get_pixmap("folder_open", 64, theme['PRIMARY']))
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)
        
        # Title
        self.title_label = QLabel("Drop your photos folder here")
        self.title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {theme['TEXT_PRIMARY']};
            background: transparent;
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Subtitle
        self.subtitle_label = QLabel("or click to browse")
        self.subtitle_label.setStyleSheet(f"""
            font-size: 14px;
            color: {theme['TEXT_MUTED']};
            background: transparent;
        """)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.subtitle_label)
        
        # Browse button
        self.browse_btn = AnimatedButton("Browse Folder")
        self.browse_btn.setProperty("variant", "secondary")
        self.browse_btn.setFixedWidth(160)
        self.browse_btn.clicked.connect(self._browse_folder)
        layout.addWidget(self.browse_btn, 0, Qt.AlignCenter)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(124, 58, 237, 40))
        self.setGraphicsEffect(shadow)
    
    def update_style(self, hovering=False):
        theme = ThemeManager.get_current_theme()
        border_color = theme['PRIMARY'] if hovering else theme['BORDER']
        bg_color = theme['SURFACE_LIGHT'] if hovering else theme['SURFACE']
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border: 2px dashed {border_color};
                border-radius: 20px;
            }}
        """)
    
    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Photo Folder", "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            self.folder_selected.emit(folder)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and os.path.isdir(urls[0].toLocalFile()):
                event.acceptProposedAction()
                self._is_hovering = True
                self.update_style(hovering=True)
                self._pulse_timer.start(50)
    
    def dragLeaveEvent(self, event):
        self._is_hovering = False
        self.update_style(hovering=False)
        self._pulse_timer.stop()
    
    def dropEvent(self, event: QDropEvent):
        self._is_hovering = False
        self.update_style(hovering=False)
        self._pulse_timer.stop()
        
        urls = event.mimeData().urls()
        if urls:
            folder = urls[0].toLocalFile()
            if os.path.isdir(folder):
                self.folder_selected.emit(folder)
    
    def _update_pulse(self):
        # Simple pulse animation
        self._pulse_value += self._pulse_direction * 5
        if self._pulse_value >= 100:
            self._pulse_direction = -1
        elif self._pulse_value <= 0:
            self._pulse_direction = 1


# ========== Photo Preview Grid ==========

class PhotoThumbnail(QFrame):
    """Single photo thumbnail with status badge."""
    
    clicked = Signal(str)  # Emits photo path
    
    def __init__(self, path: str, status: str = "pending", parent=None):
        super().__init__(parent)
        self.path = path
        self.status = status  # pending, good, blurry, duplicate, face
        self.setFixedSize(100, 100)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(path)  # Show full path on hover
        self.setup_ui()
    
    def setup_ui(self):
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            QFrame {{
                background: {theme['SURFACE_LIGHT']};
                border: 1px solid {theme['BORDER']};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border-color: {theme['PRIMARY']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)
        
        # Thumbnail image
        self.image_label = QLabel()
        self.image_label.setFixedSize(92, 72)
        self.image_label.setStyleSheet(f"""
            background: {theme['SURFACE']};
            border-radius: 8px;
        """)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        
        # Load thumbnail
        self._load_thumbnail()
        layout.addWidget(self.image_label)
        
        # Status badge
        self.badge = QLabel()
        self.badge.setFixedSize(20, 20)
        self.badge.setAlignment(Qt.AlignCenter)
        self.update_status(self.status)
        
        # Position badge in top-right corner
        self.badge.setParent(self)
        self.badge.move(76, 4)
    
    def _load_thumbnail(self):
        """Load thumbnail image with multiple fallback methods."""
        try:
            # Check if file exists
            if not os.path.exists(self.path):
                logging.warning(f"Image file not found: {self.path}")
                self.image_label.setText("❌")
                return
            
            # Try QPixmap first (fast for common formats)
            pixmap = QPixmap(self.path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(92, 72, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled)
                return
            
            # Fallback to PIL for HEIC and other formats
            try:
                from PIL import Image
                import io
                
                with Image.open(self.path) as img:
                    img = img.convert('RGB')
                    img.thumbnail((92, 72), Image.Resampling.LANCZOS)
                    
                    # Convert to QPixmap
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    buffer.seek(0)
                    
                    pixmap = QPixmap()
                    pixmap.loadFromData(buffer.getvalue())
                    if not pixmap.isNull():
                        self.image_label.setPixmap(pixmap)
                        return
            except Exception as pil_err:
                logging.debug(f"PIL fallback failed for {self.path}: {pil_err}")
            
            self.image_label.setText("📷")
        except Exception as e:
            logging.warning(f"Failed to load thumbnail for {self.path}: {e}")
            self.image_label.setText("📷")
    
    def update_status(self, status: str):
        self.status = status
        theme = ThemeManager.get_current_theme()
        
        status_config = {
            "pending": ("⏳", theme['TEXT_MUTED'], theme['SURFACE']),
            "good": ("✓", "#FFFFFF", theme['SUCCESS']),
            "blurry": ("⚠", "#FFFFFF", theme['WARNING']),
            "duplicate": ("📋", "#FFFFFF", theme['DANGER']),
            "face": ("👤", "#FFFFFF", theme['ACCENT']),
        }
        
        icon, text_color, bg_color = status_config.get(status, status_config["pending"])
        self.badge.setText(icon)
        self.badge.setStyleSheet(f"""
            QLabel {{
                background: {bg_color};
                color: {text_color};
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            }}
        """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.path)


class PhotoPreviewGrid(QScrollArea):
    """Scrollable grid of photo thumbnails."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thumbnails: Dict[str, PhotoThumbnail] = {}
        self.setup_ui()
    
    def setup_ui(self):
        theme = ThemeManager.get_current_theme()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {theme['SURFACE']};
                width: 8px;
                margin: 0;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {theme['BORDER']};
                min-height: 30px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {theme['PRIMARY']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)
        
        # Container widget
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setContentsMargins(0, 0, 12, 0)  # Right margin for scrollbar
        
        self.setWidget(self.container)
        
        # Placeholder when empty
        self.placeholder = QLabel("Photos will appear here during processing")
        self.placeholder.setStyleSheet(f"""
            color: {theme['TEXT_MUTED']};
            font-size: 14px;
            padding: 40px;
        """)
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.grid_layout.addWidget(self.placeholder, 0, 0, 1, 4)
    
    def add_photo(self, path: str, status: str = "pending"):
        """Add a photo thumbnail to the grid."""
        if self.placeholder.isVisible():
            self.placeholder.hide()
        
        if path not in self.thumbnails:
            thumbnail = PhotoThumbnail(path, status)
            self.thumbnails[path] = thumbnail
            
            # Calculate position
            count = len(self.thumbnails)
            row = (count - 1) // 4
            col = (count - 1) % 4
            self.grid_layout.addWidget(thumbnail, row, col)
    
    def update_photo_status(self, path: str, status: str):
        """Update the status of a photo thumbnail."""
        if path in self.thumbnails:
            self.thumbnails[path].update_status(status)
    
    def clear(self):
        """Clear all thumbnails."""
        for thumb in self.thumbnails.values():
            thumb.deleteLater()
        self.thumbnails.clear()
        self.placeholder.show()


# ========== Stats Panel ==========

class CircularProgress(QWidget):
    """Circular progress indicator."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)
        self._value = 0
        self._max_value = 100
    
    def set_value(self, value: int):
        self._value = min(value, self._max_value)
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        theme = ThemeManager.get_current_theme()
        
        # Background circle
        pen = QPen(QColor(theme['SURFACE_LIGHT']))
        pen.setWidth(10)
        painter.setPen(pen)
        painter.drawArc(15, 15, 90, 90, 0, 360 * 16)
        
        # Progress arc
        if self._value > 0:
            gradient = QLinearGradient(0, 0, 120, 120)
            gradient.setColorAt(0, QColor(theme['PRIMARY']))
            gradient.setColorAt(1, QColor(theme['ACCENT']))
            
            pen = QPen(QBrush(gradient), 10)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            
            span = int(-360 * 16 * (self._value / self._max_value))
            painter.drawArc(15, 15, 90, 90, 90 * 16, span)
        
        # Center text
        painter.setPen(QColor(theme['TEXT_PRIMARY']))
        font = QFont("Segoe UI", 20, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRect(0, 0, 120, 120), Qt.AlignCenter, f"{self._value}%")


class StatItem(QFrame):
    """Single stat item with icon, label, and value."""
    
    def __init__(self, icon: str, label: str, value: str = "0", 
                 color: str = None, parent=None):
        super().__init__(parent)
        self.color = color
        self.setup_ui(icon, label, value)
    
    def setup_ui(self, icon: str, label: str, value: str):
        theme = ThemeManager.get_current_theme()
        accent = self.color or theme['PRIMARY']
        
        self.setStyleSheet(f"""
            StatItem {{
                background: {theme['SURFACE']};
                border: 1px solid {theme['BORDER']};
                border-left: 3px solid {accent};
                border-radius: 8px;
            }}
            StatItem QLabel {{
                background: transparent;
                border: none;
            }}
            StatItem QWidget {{
                background: transparent;
                border: none;
            }}
        """)
        self.setObjectName("StatItem")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 18px; background: transparent; border: none;")
        layout.addWidget(icon_label)
        
        # Text container
        text_container = QWidget()
        text_container.setStyleSheet("background: transparent; border: none;")
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            font-size: 12px;
            color: {theme['TEXT_MUTED']};
            background: transparent;
            border: none;
        """)
        text_layout.addWidget(label_widget)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 700;
            color: {accent};
            background: transparent;
            border: none;
        """)
        text_layout.addWidget(self.value_label)
        
        layout.addWidget(text_container)
        layout.addStretch()
    
    def set_value(self, value):
        self.value_label.setText(str(value))


class StatsPanel(QFrame):
    """Right-side statistics panel with live updates."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(STATS_PANEL_WIDTH)
        self._start_time = None
        self._processed_count = 0
        self.setup_ui()
    
    def setup_ui(self):
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            QFrame {{
                background: {theme['SURFACE']};
                border-left: 1px solid {theme['BORDER']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(16)
        
        # Title with status indicator
        title_row = QHBoxLayout()
        
        title = QLabel("Live Statistics")
        title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {theme['TEXT_PRIMARY']};
        """)
        title_row.addWidget(title)
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet(f"color: {theme['TEXT_MUTED']}; font-size: 12px;")
        title_row.addWidget(self.status_indicator)
        title_row.addStretch()
        
        layout.addLayout(title_row)
        
        # Status text
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"""
            color: {theme['TEXT_MUTED']};
            font-size: 12px;
            padding: 4px 0;
        """)
        layout.addWidget(self.status_label)
        
        # Circular progress
        progress_container = QWidget()
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setAlignment(Qt.AlignCenter)
        
        self.circular_progress = CircularProgress()
        progress_layout.addWidget(self.circular_progress)
        layout.addWidget(progress_container)
        
        # Speed indicator
        speed_container = QFrame()
        speed_container.setObjectName("speedContainer")
        speed_container.setStyleSheet(f"""
            #speedContainer {{
                background: {theme['SURFACE_LIGHT']};
                border-radius: 8px;
                border: none;
            }}
            #speedContainer QLabel {{
                background: transparent;
                border: none;
            }}
            #speedContainer QWidget {{
                background: transparent;
                border: none;
            }}
        """)
        speed_layout = QHBoxLayout(speed_container)
        speed_layout.setContentsMargins(12, 8, 12, 8)
        speed_layout.setSpacing(8)
        
        speed_icon = QLabel("⚡")
        speed_icon.setStyleSheet("font-size: 16px; background: transparent;")
        speed_layout.addWidget(speed_icon)
        
        speed_info = QWidget()
        speed_info_layout = QVBoxLayout(speed_info)
        speed_info_layout.setContentsMargins(0, 0, 0, 0)
        speed_info_layout.setSpacing(0)
        
        speed_label = QLabel("Processing Speed")
        speed_label.setStyleSheet(f"font-size: 10px; color: {theme['TEXT_MUTED']}; background: transparent;")
        speed_info_layout.addWidget(speed_label)
        
        self.speed_value = QLabel("-- img/s")
        self.speed_value.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {theme['ACCENT']}; background: transparent;")
        speed_info_layout.addWidget(self.speed_value)
        
        speed_layout.addWidget(speed_info)
        speed_layout.addStretch()
        
        self.total_label = QLabel("0")
        self.total_label.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {theme['PRIMARY']}; background: transparent;")
        speed_layout.addWidget(self.total_label)
        
        layout.addWidget(speed_container)
        
        # Stats
        stats_container = QWidget()
        stats_container.setStyleSheet("background: transparent; border: none;")
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)
        
        self.good_stat = StatItem("✨", "Good Photos", "0", theme['SUCCESS'])
        stats_layout.addWidget(self.good_stat)
        
        self.blurry_stat = StatItem("🌫️", "Blurry", "0", theme['WARNING'])
        stats_layout.addWidget(self.blurry_stat)
        
        self.duplicate_stat = StatItem("📋", "Duplicates", "0", theme['DANGER'])
        stats_layout.addWidget(self.duplicate_stat)
        
        self.face_stat = StatItem("👤", "Matches", "0", theme['ACCENT'])
        stats_layout.addWidget(self.face_stat)
        
        layout.addWidget(stats_container)
        
        # Current file being processed
        current_container = QFrame()
        current_container.setObjectName("currentContainer")
        current_container.setStyleSheet(f"""
            #currentContainer {{
                background: {theme['SURFACE_LIGHT']};
                border-radius: 8px;
                border-left: 2px solid {theme['PRIMARY']};
            }}
            #currentContainer QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        current_layout = QVBoxLayout(current_container)
        current_layout.setContentsMargins(12, 8, 12, 8)
        current_layout.setSpacing(2)
        
        current_title = QLabel("Currently Processing")
        current_title.setStyleSheet(f"font-size: 10px; color: {theme['TEXT_MUTED']}; background: transparent;")
        current_layout.addWidget(current_title)
        
        self.current_file = QLabel("—")
        self.current_file.setStyleSheet(f"""
            font-size: 12px;
            color: {theme['TEXT_PRIMARY']};
            background: transparent;
        """)
        self.current_file.setWordWrap(True)
        current_layout.addWidget(self.current_file)
        
        layout.addWidget(current_container)
        
        layout.addStretch()
        
        # Action buttons at bottom
        action_container = QWidget()
        action_layout = QVBoxLayout(action_container)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(10)
        
        self.undo_btn = AnimatedButton("↩️ Undo Last")
        self.undo_btn.setProperty("variant", "secondary")
        self.undo_btn.setEnabled(False)
        action_layout.addWidget(self.undo_btn)
        
        self.export_btn = AnimatedButton("📊 Export Report")
        self.export_btn.setProperty("variant", "ghost")
        action_layout.addWidget(self.export_btn)
        
        layout.addWidget(action_container)
    
    def start_processing(self):
        """Called when processing starts."""
        theme = ThemeManager.get_current_theme()
        self._start_time = datetime.now()
        self._processed_count = 0
        self.status_indicator.setStyleSheet(f"color: {theme['SUCCESS']}; font-size: 12px;")
        self.status_label.setText("Processing...")
        self.status_label.setStyleSheet(f"color: {theme['SUCCESS']}; font-size: 12px;")
    
    def stop_processing(self):
        """Called when processing stops."""
        theme = ThemeManager.get_current_theme()
        self._start_time = None
        self.status_indicator.setStyleSheet(f"color: {theme['TEXT_MUTED']}; font-size: 12px;")
        self.status_label.setText("Complete")
        self.status_label.setStyleSheet(f"color: {theme['SUCCESS']}; font-size: 12px;")
        self.current_file.setText("—")
    
    def set_current_file(self, filename: str):
        """Update the current file being processed."""
        # Truncate long filenames
        if len(filename) > 25:
            filename = filename[:22] + "..."
        self.current_file.setText(filename)
    
    def set_status(self, text: str):
        """Update status text."""
        self.status_label.setText(text)
    
    def update_stats(self, good=0, blurry=0, duplicates=0, faces=0, progress=0):
        """Update all statistics."""
        self.good_stat.set_value(good)
        self.blurry_stat.set_value(blurry)
        self.duplicate_stat.set_value(duplicates)
        self.face_stat.set_value(faces)
        self.circular_progress.set_value(progress)
        
        # Update total count
        total = good + blurry + duplicates
        self.total_label.setText(str(total))
        self._processed_count = total
        
        # Calculate speed
        if self._start_time and total > 0:
            elapsed = (datetime.now() - self._start_time).total_seconds()
            if elapsed > 0:
                speed = total / elapsed
                self.speed_value.setText(f"{speed:.1f} img/s")
    
    def reset(self):
        """Reset all stats to zero."""
        theme = ThemeManager.get_current_theme()
        self.update_stats(0, 0, 0, 0, 0)
        self.speed_value.setText("-- img/s")
        self.total_label.setText("0")
        self.current_file.setText("—")
        self.status_label.setText("Ready")
        self.status_indicator.setStyleSheet(f"color: {theme['TEXT_MUTED']}; font-size: 12px;")
        self._start_time = None
        self._processed_count = 0



# ========== Settings Page ==========

class SettingsPage(QScrollArea):
    """Settings configuration page."""
    
    settings_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        theme = ThemeManager.get_current_theme()
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {theme['SURFACE']};
                width: 8px;
                margin: 0;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {theme['BORDER']};
                min-height: 30px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {theme['PRIMARY']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 42, 30)  # Extra right margin for scrollbar
        layout.setSpacing(24)
        
        # Title
        title = QLabel("⚙️ Detection Settings")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {theme['TEXT_PRIMARY']};
        """)
        layout.addWidget(title)
        
        # Blur detection card
        blur_card = GlowCard()
        blur_layout = QVBoxLayout(blur_card)
        blur_layout.setSpacing(16)
        
        blur_title = QLabel("🔍 Blur Detection")
        blur_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {theme['PRIMARY']};
            background: transparent;
        """)
        blur_layout.addWidget(blur_title)
        
        blur_desc = QLabel("Adjust sensitivity for detecting blurry or unfocused photos")
        blur_desc.setStyleSheet(f"color: {theme['TEXT_MUTED']}; background: transparent;")
        blur_layout.addWidget(blur_desc)
        
        blur_control = QHBoxLayout()
        blur_control.addWidget(QLabel("Threshold:"))
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(50, 350)
        self.blur_slider.setValue(100)
        blur_control.addWidget(self.blur_slider)
        self.blur_value = QLabel("100")
        self.blur_value.setStyleSheet(f"color: {theme['PRIMARY']}; font-weight: bold;")
        blur_control.addWidget(self.blur_value)
        blur_layout.addLayout(blur_control)
        
        self.blur_slider.valueChanged.connect(lambda v: self.blur_value.setText(str(v)))
        
        layout.addWidget(blur_card)
        
        # Duplicate detection card
        dup_card = GlowCard()
        dup_layout = QVBoxLayout(dup_card)
        dup_layout.setSpacing(16)
        
        dup_title = QLabel("📋 Duplicate Detection")
        dup_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {theme['ACCENT']};
            background: transparent;
        """)
        dup_layout.addWidget(dup_title)
        
        dup_desc = QLabel("Set how similar photos need to be to count as duplicates")
        dup_desc.setStyleSheet(f"color: {theme['TEXT_MUTED']}; background: transparent;")
        dup_layout.addWidget(dup_desc)
        
        dup_control = QHBoxLayout()
        dup_control.addWidget(QLabel("Similarity:"))
        self.dup_slider = QSlider(Qt.Horizontal)
        self.dup_slider.setRange(5, 40)
        self.dup_slider.setValue(20)
        dup_control.addWidget(self.dup_slider)
        self.dup_value = QLabel("20")
        self.dup_value.setStyleSheet(f"color: {theme['ACCENT']}; font-weight: bold;")
        dup_control.addWidget(self.dup_value)
        dup_layout.addLayout(dup_control)
        
        self.dup_slider.valueChanged.connect(lambda v: self.dup_value.setText(str(v)))
        
        layout.addWidget(dup_card)
        
        # Face detection card
        face_card = GlowCard()
        face_layout = QVBoxLayout(face_card)
        face_layout.setSpacing(16)
        
        face_title = QLabel("👤 Face Detection")
        face_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {theme['SUCCESS']};
            background: transparent;
        """)
        face_layout.addWidget(face_title)
        
        self.face_checkbox = QCheckBox("Enable face detection and categorization")
        self.face_checkbox.setChecked(True)
        self.face_checkbox.setStyleSheet(f"color: {theme['TEXT_PRIMARY']};")
        face_layout.addWidget(self.face_checkbox)
        
        layout.addWidget(face_card)
        layout.addStretch()
        
        self.setWidget(container)
    
    def get_settings(self) -> dict:
        return {
            'blur_threshold': self.blur_slider.value(),
            'similarity_threshold': self.dup_slider.value(),
            'enable_face_detection': self.face_checkbox.isChecked()
        }


# ========== Dashboard Page ==========

class DashboardPage(QScrollArea):
    """Main dashboard with drop zone and photo preview."""
    
    start_processing = Signal()
    folder_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_folder = None
        self.setup_ui()
    
    def setup_ui(self):
        theme = ThemeManager.get_current_theme()
        
        # Setup scroll area
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {theme['SURFACE']};
                width: 8px;
                margin: 0;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {theme['BORDER']};
                min-height: 30px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {theme['PRIMARY']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)
        
        # Container widget
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 42, 30)  # Extra right margin for scrollbar
        layout.setSpacing(24)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        
        title = FadeLabel("Photo Organization")
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {theme['TEXT_PRIMARY']};
        """)
        title_layout.addWidget(title)
        
        subtitle = QLabel("Organize your photos by quality with AI detection")
        subtitle.setStyleSheet(f"color: {theme['TEXT_MUTED']}; font-size: 14px;")
        title_layout.addWidget(subtitle)
        
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        
        # Start button
        self.start_btn = AnimatedButton("🚀 Start Processing")
        self.start_btn.setProperty("variant", "primary")
        self.start_btn.setEnabled(False)
        self.start_btn.setMinimumWidth(180)
        self.start_btn.clicked.connect(lambda: self.start_processing.emit())
        header_layout.addWidget(self.start_btn)
        
        layout.addWidget(header)
        
        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.folder_selected.connect(self._on_folder_selected)
        layout.addWidget(self.drop_zone)
        
        # Selected folder indicator
        self.folder_indicator = QFrame()
        self.folder_indicator.setVisible(False)
        self.folder_indicator.setStyleSheet(f"""
            QFrame {{
                background: {theme['SURFACE']};
                border: 1px solid {theme['SUCCESS']};
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        indicator_layout = QHBoxLayout(self.folder_indicator)
        
        folder_icon = QLabel()
        folder_icon.setPixmap(get_pixmap("check_circle", 20, theme['SUCCESS']))
        indicator_layout.addWidget(folder_icon)
        
        self.folder_path_label = QLabel()
        self.folder_path_label.setStyleSheet(f"color: {theme['TEXT_PRIMARY']};")
        indicator_layout.addWidget(self.folder_path_label, 1)
        
        self.image_count_label = QLabel()
        self.image_count_label.setStyleSheet(f"color: {theme['TEXT_MUTED']};")
        indicator_layout.addWidget(self.image_count_label)
        
        change_btn = AnimatedButton("Change")
        change_btn.setProperty("variant", "ghost")
        change_btn.clicked.connect(self.drop_zone._browse_folder)
        indicator_layout.addWidget(change_btn)
        
        layout.addWidget(self.folder_indicator)
        
        # Photo preview section
        preview_title = QLabel("📷 Photo Preview")
        preview_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {theme['TEXT_PRIMARY']};
        """)
        layout.addWidget(preview_title)
        
        self.photo_grid = PhotoPreviewGrid()
        layout.addWidget(self.photo_grid, 1)
        
        # Set the container as the scroll widget
        self.setWidget(container)
    
    def _on_folder_selected(self, path: str):
        self.selected_folder = path
        theme = ThemeManager.get_current_theme()
        
        # Count images
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.heic', '.heif')
        try:
            images = [f for f in os.listdir(path) 
                     if f.lower().endswith(image_extensions)]
            count = len(images)
        except Exception:
            images = []
            count = 0
        
        # Update UI
        self.folder_path_label.setText(path)
        self.image_count_label.setText(f"{count} images found")
        self.folder_indicator.setVisible(True)
        self.drop_zone.setVisible(False)
        self.start_btn.setEnabled(count > 0)
        
        # Load photo previews (limit to first 50 for performance)
        self.photo_grid.clear()
        preview_count = min(len(images), 50)
        for i in range(preview_count):
            img_path = os.path.join(path, images[i])
            self.photo_grid.add_photo(img_path, "pending")
        
        # Emit signal
        self.folder_selected.emit(path)
    
    def reset(self):
        """Reset the dashboard to initial state."""
        self.selected_folder = None
        self.folder_indicator.setVisible(False)
        self.drop_zone.setVisible(True)
        self.start_btn.setEnabled(False)
        self.photo_grid.clear()


# ========== Face Search Page ==========

class FaceSearchPage(QScrollArea):
    """Complete face search page with reference face, folder selection, and results."""
    
    start_search = Signal(str, str, float)  # reference_path, folder_path, threshold
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.reference_face_path = None
        self.search_folder_path = None
        self.setup_ui()
    
    def setup_ui(self):
        theme = ThemeManager.get_current_theme()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {theme['SURFACE']};
                width: 8px;
                margin: 0;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {theme['BORDER']};
                min-height: 30px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {theme['PRIMARY']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 42, 30)  # Extra right margin for scrollbar
        layout.setSpacing(20)
        
        # Header
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)
        
        title = FadeLabel("👤 Face Search")
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {theme['TEXT_PRIMARY']};
        """)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Find photos containing a specific person using AI face recognition")
        subtitle.setStyleSheet(f"color: {theme['TEXT_MUTED']}; font-size: 14px;")
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # Status card - DeepFace availability
        status_card = GlowCard()
        status_layout = QHBoxLayout(status_card)
        status_layout.setSpacing(16)
        
        # Check if DeepFace is available
        try:
            from deepface import DeepFace
            deepface_available = True
        except ImportError:
            deepface_available = False
        
        status_icon = QLabel("✅" if deepface_available else "⚠️")
        status_icon.setStyleSheet(f"font-size: 24px; background: transparent;")
        status_layout.addWidget(status_icon)
        
        status_text = QWidget()
        status_text_layout = QVBoxLayout(status_text)
        status_text_layout.setContentsMargins(0, 0, 0, 0)
        status_text_layout.setSpacing(2)
        
        status_title = QLabel("Face Recognition Status")
        status_title.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {theme['SUCCESS'] if deepface_available else theme['WARNING']};
            background: transparent;
        """)
        status_text_layout.addWidget(status_title)
        
        status_desc = QLabel(
            "DeepFace is ready for person-specific matching" if deepface_available 
            else "DeepFace unavailable — install 'deepface' and 'tf-keras'"
        )
        status_desc.setStyleSheet(f"color: {theme['TEXT_MUTED']}; background: transparent;")
        status_text_layout.addWidget(status_desc)
        
        status_layout.addWidget(status_text, 1)
        layout.addWidget(status_card)
        
        # Reference face card
        ref_card = GlowCard()
        ref_layout = QVBoxLayout(ref_card)
        ref_layout.setSpacing(16)
        
        ref_title = QLabel("📷 Reference Face")
        ref_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {theme['PRIMARY']};
            background: transparent;
        """)
        ref_layout.addWidget(ref_title)
        
        ref_desc = QLabel("Select a photo of the person you want to find")
        ref_desc.setStyleSheet(f"color: {theme['TEXT_MUTED']}; background: transparent;")
        ref_layout.addWidget(ref_desc)
        
        ref_row = QHBoxLayout()
        
        # Reference thumbnail preview
        self.ref_thumbnail = QLabel()
        self.ref_thumbnail.setFixedSize(80, 80)
        self.ref_thumbnail.setStyleSheet(f"""
            background: {theme['SURFACE_LIGHT']};
            border: 2px dashed {theme['BORDER']};
            border-radius: 12px;
        """)
        self.ref_thumbnail.setAlignment(Qt.AlignCenter)
        self.ref_thumbnail.setText("👤")
        ref_row.addWidget(self.ref_thumbnail)
        
        ref_info = QWidget()
        ref_info_layout = QVBoxLayout(ref_info)
        ref_info_layout.setContentsMargins(12, 0, 0, 0)
        ref_info_layout.setSpacing(8)
        
        self.ref_label = QLabel("No reference selected")
        self.ref_label.setStyleSheet(f"color: {theme['TEXT_PRIMARY']}; background: transparent;")
        self.ref_label.setWordWrap(True)
        ref_info_layout.addWidget(self.ref_label)
        
        self.ref_btn = AnimatedButton("Choose Face Image")
        self.ref_btn.setProperty("variant", "primary")
        self.ref_btn.clicked.connect(self._select_reference_face)
        ref_info_layout.addWidget(self.ref_btn)
        
        ref_row.addWidget(ref_info, 1)
        ref_layout.addLayout(ref_row)
        layout.addWidget(ref_card)
        
        # Search folder card
        folder_card = GlowCard()
        folder_layout = QVBoxLayout(folder_card)
        folder_layout.setSpacing(16)
        
        folder_title = QLabel("📁 Search Folder")
        folder_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {theme['ACCENT']};
            background: transparent;
        """)
        folder_layout.addWidget(folder_title)
        
        folder_desc = QLabel("Select the folder to search for matching faces")
        folder_desc.setStyleSheet(f"color: {theme['TEXT_MUTED']}; background: transparent;")
        folder_layout.addWidget(folder_desc)
        
        folder_row = QHBoxLayout()
        
        self.folder_btn = AnimatedButton("Choose Folder")
        self.folder_btn.setProperty("variant", "secondary")
        self.folder_btn.clicked.connect(self._select_search_folder)
        folder_row.addWidget(self.folder_btn)
        
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setStyleSheet(f"color: {theme['TEXT_PRIMARY']}; background: transparent;")
        self.folder_label.setWordWrap(True)
        folder_row.addWidget(self.folder_label, 1)
        
        folder_layout.addLayout(folder_row)
        layout.addWidget(folder_card)
        
        # Similarity threshold card
        sim_card = GlowCard()
        sim_layout = QVBoxLayout(sim_card)
        sim_layout.setSpacing(16)
        
        sim_title = QLabel("🎯 Match Sensitivity")
        sim_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {theme['SUCCESS']};
            background: transparent;
        """)
        sim_layout.addWidget(sim_title)
        
        sim_desc = QLabel("Adjust how similar a face needs to be to count as a match")
        sim_desc.setStyleSheet(f"color: {theme['TEXT_MUTED']}; background: transparent;")
        sim_layout.addWidget(sim_desc)
        
        sim_control = QHBoxLayout()
        
        sim_label = QLabel("Threshold:")
        sim_label.setStyleSheet(f"color: {theme['TEXT_PRIMARY']}; background: transparent;")
        sim_control.addWidget(sim_label)
        
        self.similarity_slider = QSlider(Qt.Horizontal)
        self.similarity_slider.setRange(40, 80)  # 40% to 80% (stricter range)
        self.similarity_slider.setValue(60)  # Default 60% (max distance 0.40)
        self.similarity_slider.setTickPosition(QSlider.TicksBelow)
        self.similarity_slider.setTickInterval(10)
        sim_control.addWidget(self.similarity_slider, 1)
        
        self.similarity_value = QLabel("0.60")
        self.similarity_value.setStyleSheet(f"""
            font-weight: 600;
            color: {theme['SUCCESS']};
            min-width: 50px;
            background: transparent;
        """)
        sim_control.addWidget(self.similarity_value)
        
        self.similarity_slider.valueChanged.connect(
            lambda v: self.similarity_value.setText(f"{v/100:.2f}")
        )
        
        sim_layout.addLayout(sim_control)
        
        # Labels
        labels_row = QHBoxLayout()
        labels_row.setContentsMargins(60, 0, 60, 0)
        
        loose_label = QLabel("Loose")
        loose_label.setStyleSheet(f"color: {theme['TEXT_MUTED']}; font-size: 12px;")
        labels_row.addWidget(loose_label)
        labels_row.addStretch()
        
        normal_label = QLabel("Normal")
        normal_label.setStyleSheet(f"color: {theme['TEXT_MUTED']}; font-size: 12px;")
        labels_row.addWidget(normal_label)
        labels_row.addStretch()
        
        strict_label = QLabel("Strict")
        strict_label.setStyleSheet(f"color: {theme['TEXT_MUTED']}; font-size: 12px;")
        labels_row.addWidget(strict_label)
        
        sim_layout.addLayout(labels_row)
        layout.addWidget(sim_card)
        
        # Action bar
        action_card = GlowCard()
        action_layout = QHBoxLayout(action_card)
        
        self.start_btn = AnimatedButton("🔍 Start Face Search")
        self.start_btn.setProperty("variant", "success")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self._start_search)
        action_layout.addWidget(self.start_btn)
        
        control_container = QWidget()
        control_layout = QHBoxLayout(control_container)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(8)
        
        self.pause_btn = AnimatedButton("⏸")
        self.pause_btn.setProperty("variant", "icon")
        self.pause_btn.setEnabled(False)
        control_layout.addWidget(self.pause_btn)
        
        self.stop_btn = AnimatedButton("⏹")
        self.stop_btn.setProperty("variant", "icon")
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        action_layout.addWidget(control_container)
        action_layout.addStretch()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setValue(0)
        action_layout.addWidget(self.progress_bar)
        
        layout.addWidget(action_card)
        
        # Results section
        self.results_card = GlowCard()
        self.results_card.setVisible(False)
        results_layout = QVBoxLayout(self.results_card)
        results_layout.setSpacing(16)
        
        results_header = QHBoxLayout()
        
        results_title = QLabel("📊 Search Results")
        results_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {theme['SUCCESS']};
            background: transparent;
        """)
        results_header.addWidget(results_title)
        
        self.results_count = QLabel("0 matches found")
        self.results_count.setStyleSheet(f"color: {theme['TEXT_MUTED']}; background: transparent;")
        results_header.addWidget(self.results_count)
        results_header.addStretch()
        
        results_layout.addLayout(results_header)
        
        # Results grid
        self.results_grid = PhotoPreviewGrid()
        self.results_grid.setMinimumHeight(200)
        results_layout.addWidget(self.results_grid)
        
        layout.addWidget(self.results_card)
        layout.addStretch()
        
        self.setWidget(container)
    
    def _select_reference_face(self):
        """Select reference face image."""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Reference Face",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp *.webp *.heic *.tiff);;All Files (*)"
        )
        
        if file:
            self.reference_face_path = file
            filename = Path(file).name
            self.ref_label.setText(filename)
            self.ref_label.setToolTip(file)
            
            # Load thumbnail
            theme = ThemeManager.get_current_theme()
            try:
                pixmap = QPixmap(file)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(76, 76, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    self.ref_thumbnail.setPixmap(scaled)
                    self.ref_thumbnail.setStyleSheet(f"""
                        background: {theme['SURFACE_LIGHT']};
                        border: 2px solid {theme['SUCCESS']};
                        border-radius: 12px;
                    """)
            except Exception:
                pass
            
            self._update_start_button()
    
    def _select_search_folder(self):
        """Select folder to search for faces."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Search Folder", "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder:
            self.search_folder_path = folder
            
            # Count images
            image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.heic')
            try:
                images = [f for f in os.listdir(folder) 
                         if f.lower().endswith(image_extensions)]
                count = len(images)
            except Exception:
                count = 0
            
            self.folder_label.setText(f"{Path(folder).name} ({count} images)")
            self.folder_label.setToolTip(folder)
            
            self._update_start_button()
    
    def _update_start_button(self):
        """Enable start button if both reference and folder are selected."""
        has_ref = self.reference_face_path is not None
        has_folder = self.search_folder_path is not None
        self.start_btn.setEnabled(has_ref and has_folder)
    
    def _start_search(self):
        """Start face search."""
        if not self.reference_face_path or not self.search_folder_path:
            return
        
        threshold = self.similarity_slider.value() / 100
        self.start_search.emit(
            self.reference_face_path,
            self.search_folder_path,
            threshold
        )
        
        # Show results card
        self.results_card.setVisible(True)
        self.results_grid.clear()
        
        # Update button states
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
    
    def add_match(self, image_path: str, similarity: float):
        """Add a matched face to results."""
        logging.info(f"Adding match to results: {image_path} (sim: {similarity:.2%})")
        self.results_grid.add_photo(image_path, "face")
        count = len(self.results_grid.thumbnails)
        self.results_count.setText(f"{count} match{'es' if count != 1 else ''} found")
    
    def update_progress(self, value: int):
        """Update progress bar."""
        self.progress_bar.setValue(value)
    
    def search_finished(self):
        """Called when search is complete."""
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)


# ========== Main Window ==========

class ModernMainWindow(QMainWindow):
    """Modern redesigned main window with sidebar navigation and full backend integration."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CLEAN SHOT — AI Photo Organizer")
        self.setMinimumSize(1280, 800)
        self.resize(1400, 900)
        
        # Processing state
        self.current_folder = None
        self.processor = None
        self.face_processor = None
        self.log_messages = []
        
        self.setup_ui()
        self.apply_theme()
        self._log("Application started")
    
    def setup_ui(self):
        # Central widget
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.navigation_clicked.connect(self._on_navigation)
        main_layout.addWidget(self.sidebar)
        
        # Content area (stacked widget for pages)
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self.pages = QStackedWidget()
        
        # Create pages
        # 0: Organize Photos - main feature
        self.dashboard_page = DashboardPage()
        self.dashboard_page.folder_selected.connect(self._on_folder_selected)
        self.dashboard_page.start_processing.connect(self._start_processing)
        self.pages.addWidget(self.dashboard_page)
        
        # 1: Face search page
        self.face_search_page = FaceSearchPage()
        self.face_search_page.start_search.connect(self._start_face_search)
        self.pages.addWidget(self.face_search_page)
        
        # 2: History/Log page
        self._create_history_page()
        self.pages.addWidget(self.history_page)
        
        # 3: Settings page
        self.settings_page = SettingsPage()
        self.pages.addWidget(self.settings_page)
        
        content_layout.addWidget(self.pages, 1)
        
        # Stats panel
        self.stats_panel = StatsPanel()
        self.stats_panel.undo_btn.clicked.connect(self._undo_last_operation)
        self.stats_panel.export_btn.clicked.connect(self._export_results)
        content_layout.addWidget(self.stats_panel)
        
        main_layout.addWidget(content_container, 1)
    
    def _create_history_page(self):
        """Create the history/log page."""
        theme = ThemeManager.get_current_theme()
        
        self.history_page = QWidget()
        layout = QVBoxLayout(self.history_page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = FadeLabel("📜 Processing Log")
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {theme['TEXT_PRIMARY']};
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        clear_btn = AnimatedButton("🗑 Clear Log")
        clear_btn.setProperty("variant", "ghost")
        clear_btn.clicked.connect(self._clear_log)
        header_layout.addWidget(clear_btn)
        
        export_log_btn = AnimatedButton("📄 Export Log")
        export_log_btn.setProperty("variant", "secondary")
        export_log_btn.clicked.connect(self._export_log)
        header_layout.addWidget(export_log_btn)
        
        layout.addWidget(header)
        
        # Log display
        log_card = GlowCard()
        log_layout = QVBoxLayout(log_card)
        
        self.log_scroll = QScrollArea()
        self.log_scroll.setWidgetResizable(True)
        self.log_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.log_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.log_scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {theme['SURFACE']};
                width: 8px;
                margin: 0;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {theme['BORDER']};
                min-height: 30px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {theme['PRIMARY']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)
        
        self.log_container = QWidget()
        self.log_container.setStyleSheet("background: transparent;")
        self.log_container_layout = QVBoxLayout(self.log_container)
        self.log_container_layout.setContentsMargins(0, 0, 12, 0)  # Right margin for scrollbar
        self.log_container_layout.setSpacing(4)
        self.log_container_layout.addStretch()
        
        self.log_scroll.setWidget(self.log_container)
        log_layout.addWidget(self.log_scroll)
        
        layout.addWidget(log_card, 1)
    
    def apply_theme(self):
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {theme['BACKGROUND']}, stop:0.5 {theme['BACKGROUND_ALT']}, stop:1 {theme['BACKGROUND']});
            }}
            #centralWidget {{
                background: transparent;
            }}
        """)
        
        # Apply global theme CSS
        QApplication.instance().setStyleSheet(get_theme_css())
    
    def _on_navigation(self, index: int):
        self.pages.setCurrentIndex(index)
    
    def _on_folder_selected(self, path: str):
        self.current_folder = path
        self._log(f"📁 Folder selected: {path}")
    
    def _log(self, message: str):
        """Add a message to the log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        self.log_messages.append(full_message)
        
        # Add to log display
        if hasattr(self, 'log_container_layout'):
            theme = ThemeManager.get_current_theme()
            
            # Determine color based on message content
            upper = message.upper()
            if "ERROR" in upper or "FAILED" in upper:
                color = theme['DANGER']
            elif "SUCCESS" in upper or "COMPLETE" in upper or "✅" in message:
                color = theme['SUCCESS']
            elif "WARNING" in upper or "⚠" in message:
                color = theme['WARNING']
            elif "MATCH" in upper:
                color = theme['ACCENT']
            else:
                color = theme['TEXT_SECONDARY']
            
            label = QLabel(full_message)
            label.setStyleSheet(f"""
                color: {color};
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                background: transparent;
                padding: 2px 8px;
            """)
            label.setWordWrap(True)
            
            # Insert before the stretch
            count = self.log_container_layout.count()
            self.log_container_layout.insertWidget(count - 1, label)
            
            # Scroll to bottom
            QTimer.singleShot(100, lambda: self.log_scroll.verticalScrollBar().setValue(
                self.log_scroll.verticalScrollBar().maximum()
            ))
        
        logging.info(message)
    
    def _clear_log(self):
        """Clear all log messages."""
        self.log_messages.clear()
        
        # Remove all labels from log container
        for i in reversed(range(self.log_container_layout.count())):
            item = self.log_container_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        self.log_container_layout.addStretch()
        self._log("Log cleared")
    
    def _export_log(self):
        """Export log to a text file."""
        if not self.log_messages:
            QMessageBox.warning(self, "Warning", "Log is empty!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Log", "clean_shot_log.txt", "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write('\n'.join(self.log_messages))
                self._log(f"Log exported to: {file_path}")
                QMessageBox.information(self, "Success", f"Log exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export log: {e}")
    
    def _start_processing(self):
        """Start photo processing with the actual PhotoProcessor."""
        folder = self.dashboard_page.selected_folder
        
        if not folder:
            QMessageBox.warning(self, "Warning", "Please select a folder first.")
            return
        
        self.current_folder = folder
        
        # Reset tracking
        self._good_count = 0
        self._blurry_count = 0
        self._duplicate_count = 0
        
        # Get settings
        settings = self.settings_page.get_settings()
        blur_threshold = settings.get('blur_threshold', 100)
        similarity_threshold = settings.get('similarity_threshold', 20)
        
        self._log(f"🚀 Starting processing: blur={blur_threshold}, similarity={similarity_threshold}")
        
        try:
            from core.workers import PhotoProcessor
            
            self.processor = PhotoProcessor(
                folder,
                blur_threshold,
                similarity_threshold
            )
            
            # Connect signals
            self.processor.progress_updated.connect(self._update_progress)
            self.processor.status_updated.connect(self._update_status)
            self.processor.log_message.connect(self._on_log_message)
            self.processor.finished_processing.connect(self._processing_finished)
            
            # Update UI state
            self.dashboard_page.start_btn.setEnabled(False)
            self.stats_panel.start_processing()
            self.stats_panel.update_stats(0, 0, 0, 0, 0)
            
            # Start processing
            self.processor.start()
            
        except ImportError as e:
            self._log(f"❌ Failed to import PhotoProcessor: {e}")
            QMessageBox.warning(
                self, "Import Error",
                "Could not load photo processor. Make sure all dependencies are installed."
            )
    
    def _on_log_message(self, message: str):
        """Handle log messages and update live stats."""
        self._log(message)
        
        # Parse log message to update live stats
        upper = message.upper()
        if message.startswith("Good:"):
            self._good_count += 1
        elif message.startswith("Blurry:"):
            self._blurry_count += 1
        elif message.startswith("Duplicate:"):
            self._duplicate_count += 1
        
        # Extract filename from message
        if ":" in message and not message.startswith("["):
            parts = message.split(":", 1)
            if len(parts) > 1:
                filename = parts[1].strip().split(" ")[0]
                if filename:
                    self.stats_panel.set_current_file(filename)
        
        # Update live stats (without changing progress)
        current_progress = self.stats_panel.circular_progress._value
        self.stats_panel.update_stats(
            good=self._good_count,
            blurry=self._blurry_count,
            duplicates=self._duplicate_count,
            faces=0,
            progress=current_progress
        )
    
    def _update_progress(self, value: int):
        """Update progress in stats panel."""
        self.stats_panel.circular_progress.set_value(value)
        
        # Also update the full stats with current progress
        self.stats_panel.update_stats(
            good=getattr(self, '_good_count', 0),
            blurry=getattr(self, '_blurry_count', 0),
            duplicates=getattr(self, '_duplicate_count', 0),
            faces=0,
            progress=value
        )
    
    def _update_status(self, status: str):
        """Update status display."""
        self.stats_panel.set_status(status)
        if "Processing" in status:
            # Extract filename
            parts = status.split(" ", 1)
            if len(parts) > 1:
                self.stats_panel.set_current_file(parts[1])
    
    def _processing_finished(self, results: dict):
        """Handle processing completion."""
        self._log("✅ Processing complete!")
        self._log(f"📊 Results: {results['processed']} processed, {results['good']} good, {results['blurry']} blurry, {results['duplicate']} duplicates")
        
        # Stop the stats panel processing state
        self.stats_panel.stop_processing()
        
        # Update stats panel with final results
        self.stats_panel.update_stats(
            good=results.get('good', 0),
            blurry=results.get('blurry', 0),
            duplicates=results.get('duplicate', 0),
            faces=0,
            progress=100
        )
        
        # Enable undo (to delete copied files)
        self.stats_panel.undo_btn.setEnabled(True)
        
        # Re-enable start button (originals still exist since we copy)
        self.dashboard_page.start_btn.setEnabled(True)
        
        QMessageBox.information(
            self,
            "🎉 Processing Complete",
            f"Successfully organized {results['processed']} photos!\n\n"
            f"• {results['good']} good photos\n"
            f"• {results['blurry']} blurry photos\n"
            f"• {results['duplicate']} duplicates\n\n"
            "Photos have been copied to categorized folders.\n"
            "Original files remain untouched."
        )
    
    def _start_face_search(self, reference_path: str, folder_path: str, threshold: float):
        """Start face search with the actual FaceSearchProcessor."""
        self._log(f"🔍 Starting face search: threshold={threshold:.2f}")
        
        # Reset face match tracking
        self._face_match_count = 0
        self._face_total_searched = 0
        
        try:
            from core.workers import FaceSearchProcessor
            
            self.face_processor = FaceSearchProcessor(
                reference_path,
                folder_path,
                threshold
            )
            
            # Connect signals
            self.face_processor.progress_updated.connect(self._on_face_search_progress)
            self.face_processor.status_updated.connect(self._on_face_search_status)
            self.face_processor.log_message.connect(self._log)
            self.face_processor.face_found.connect(self._on_face_found)
            self.face_processor.finished_search.connect(self._on_face_search_finished)
            
            # Connect pause/stop buttons
            self.face_search_page.pause_btn.clicked.connect(self._toggle_face_search_pause)
            self.face_search_page.stop_btn.clicked.connect(self._stop_face_search)
            
            # Start stats panel for face search
            self.stats_panel.start_processing()
            self.stats_panel.set_status("Face Search...")
            self.stats_panel.update_stats(0, 0, 0, 0, 0)
            
            # Start processing
            self.face_processor.start()
            
        except ImportError as e:
            self._log(f"❌ Failed to import FaceSearchProcessor: {e}")
            QMessageBox.warning(
                self, "Import Error",
                "Could not load face search processor. Make sure DeepFace is installed."
            )
    
    def _on_face_search_progress(self, value: int):
        """Update progress for face search."""
        self.face_search_page.update_progress(value)
        self.stats_panel.circular_progress.set_value(value)
        self._face_total_searched = value  # Approximate
        
        # Update stats panel
        self.stats_panel.update_stats(
            good=0,
            blurry=0,
            duplicates=0,
            faces=getattr(self, '_face_match_count', 0),
            progress=value
        )
    
    def _on_face_search_status(self, status: str):
        """Update status for face search."""
        self._log(f"Status: {status}")
        self.stats_panel.set_status(status)
        
        # Extract filename from status
        if status.startswith("Checking "):
            filename = status.replace("Checking ", "")
            self.stats_panel.set_current_file(filename)
    
    def _toggle_face_search_pause(self):
        """Toggle pause/resume for face search."""
        if hasattr(self, 'face_processor') and self.face_processor:
            if self.face_processor._is_paused:
                self.face_processor.resume()
                self.face_search_page.pause_btn.setText("⏸")
                self._log("▶ Face search resumed")
            else:
                self.face_processor.pause()
                self.face_search_page.pause_btn.setText("▶")
                self._log("⏸ Face search paused")
    
    def _stop_face_search(self):
        """Stop face search."""
        if hasattr(self, 'face_processor') and self.face_processor:
            self.face_processor.stop()
            self.face_search_page.search_finished()
            self.stats_panel.stop_processing()
            self.stats_panel.set_status("Stopped")
            self._log("⏹ Face search stopped by user")
    
    def _on_face_found(self, filename: str, similarity: float):
        """Handle found face match."""
        # Increment match counter
        self._face_match_count = getattr(self, '_face_match_count', 0) + 1
        
        if hasattr(self, 'face_search_page'):
            folder = self.face_search_page.search_folder_path
            if folder:
                full_path = os.path.join(folder, filename)
                self.face_search_page.add_match(full_path, similarity)
        
        # Update stats panel with new match count
        current_progress = self.stats_panel.circular_progress._value
        self.stats_panel.update_stats(
            good=0,
            blurry=0,
            duplicates=0,
            faces=self._face_match_count,
            progress=current_progress
        )
    
    def _on_face_search_finished(self, results: dict):
        """Handle face search completion."""
        if hasattr(self, 'face_search_page'):
            self.face_search_page.search_finished()
        
        # Stop stats panel
        self.stats_panel.stop_processing()
        
        matched = results.get('matched', 0)
        total = results.get('total_searched', 0)
        output_folder = results.get('output_folder', '')
        
        # Update final stats
        self.stats_panel.update_stats(
            good=0,
            blurry=0,
            duplicates=0,
            faces=matched,
            progress=100
        )
        
        self._log(f"✅ Face search complete: {matched} matches out of {total} images")
        
        QMessageBox.information(
            self,
            "Face Search Complete",
            f"Found {matched} matching photos out of {total} scanned.\n\n"
            f"Results saved to:\n{output_folder}"
        )
    
    def _undo_last_operation(self):
        """Undo the last processing operation by deleting copied files."""
        if not self.current_folder:
            QMessageBox.warning(self, "Warning", "No recent operation to undo.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Undo",
            "This will delete the copied files from categorized folders.\n"
            "Original files are not affected.\n\n"
            "Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        folder = Path(self.current_folder)
        categories = ["Good_Photos", "Blurry_Photos", "Duplicate_Photos"]
        
        deleted_count = 0
        try:
            for category in categories:
                category_path = folder / category
                if category_path.exists():
                    for file in category_path.iterdir():
                        if file.is_file():
                            try:
                                file.unlink()  # Delete the file
                                deleted_count += 1
                            except Exception:
                                pass
                    
                    # Try to remove empty directory
                    try:
                        category_path.rmdir()
                    except OSError:
                        pass  # Not empty
            
            self._log(f"🗑️ Undo complete: {deleted_count} copied files deleted")
            self.stats_panel.undo_btn.setEnabled(False)
            self.stats_panel.reset()
            
            QMessageBox.information(
                self,
                "Undo Complete",
                f"Deleted {deleted_count} copied files from categorized folders."
            )
            
        except Exception as e:
            self._log(f"❌ Undo failed: {e}")
            QMessageBox.critical(self, "Error", f"Failed to undo: {e}")
    
    def _export_results(self):
        """Export processing results to JSON."""
        if not self.current_folder:
            QMessageBox.warning(self, "Warning", "No results to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "clean_shot_results.json", "JSON Files (*.json)"
        )
        
        if file_path:
            import json
            
            results = {
                "folder": self.current_folder,
                "timestamp": datetime.now().isoformat(),
                "settings": self.settings_page.get_settings(),
                "log": self.log_messages[-100:]  # Last 100 messages
            }
            
            try:
                with open(file_path, 'w') as f:
                    json.dump(results, f, indent=2)
                self._log(f"📊 Results exported to: {file_path}")
                QMessageBox.information(self, "Success", f"Results exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {e}")


# ========== Launch Function ==========

def run_modern_app():
    """Launch the modern redesigned application."""
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = ModernMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    run_modern_app()

