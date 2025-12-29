# ========== Theme and UI System ==========
"""
Unified theme management and animated UI widgets for CLEAN SHOT Photo Organizer.
This is the single source of truth for all styling in the application.
"""

from typing import Any, Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QByteArray
from PySide6.QtGui import QColor, QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer


# ========== Theme Definitions ==========

DARK_THEME: Dict[str, str] = {
    # Primary brand colors
    "PRIMARY": "#7C3AED",
    "PRIMARY_LIGHT": "#A78BFA",
    "PRIMARY_DARK": "#6D28D9",
    
    # Accent colors
    "ACCENT": "#06B6D4",
    "ACCENT_LIGHT": "#67E8F9",
    "ACCENT_DARK": "#0891B2",
    
    # Background colors
    "BACKGROUND": "#0F172A",
    "BACKGROUND_ALT": "#1E1B4B",
    "SURFACE": "#1E293B",
    "SURFACE_LIGHT": "#334155",
    "SURFACE_ELEVATED": "#3B4252",
    
    # Text colors
    "TEXT_PRIMARY": "#F8FAFC",
    "TEXT_SECONDARY": "#94A3B8",
    "TEXT_MUTED": "#64748B",
    "TEXT_INVERSE": "#0F172A",
    
    # Status colors
    "SUCCESS": "#10B981",
    "SUCCESS_LIGHT": "#34D399",
    "WARNING": "#F59E0B",
    "WARNING_LIGHT": "#FBBF24",
    "DANGER": "#EF4444",
    "DANGER_LIGHT": "#F87171",
    "INFO": "#3B82F6",
    "INFO_LIGHT": "#60A5FA",
    
    # Border and effects
    "BORDER": "#475569",
    "BORDER_LIGHT": "#64748B",
    "SHADOW": "rgba(0, 0, 0, 0.3)",
    "GLOW": "rgba(124, 58, 237, 0.3)",
    
    # Gradients
    "GRADIENT_START": "#7C3AED",
    "GRADIENT_END": "#06B6D4",
    
    # Component dimensions
    "BUTTON_RADIUS": "12px",
    "BUTTON_HEIGHT": "44px",
    "CARD_RADIUS": "16px",
    "INPUT_RADIUS": "8px",
}

LIGHT_THEME: Dict[str, str] = {
    # Primary brand colors (same as dark for consistency)
    "PRIMARY": "#7C3AED",
    "PRIMARY_LIGHT": "#A78BFA",
    "PRIMARY_DARK": "#6D28D9",
    
    # Accent colors
    "ACCENT": "#06B6D4",
    "ACCENT_LIGHT": "#67E8F9",
    "ACCENT_DARK": "#0891B2",
    
    # Background colors
    "BACKGROUND": "#F8FAFC",
    "BACKGROUND_ALT": "#F1F5F9",
    "SURFACE": "#FFFFFF",
    "SURFACE_LIGHT": "#F1F5F9",
    "SURFACE_ELEVATED": "#FFFFFF",
    
    # Text colors
    "TEXT_PRIMARY": "#0F172A",
    "TEXT_SECONDARY": "#475569",
    "TEXT_MUTED": "#94A3B8",
    "TEXT_INVERSE": "#F8FAFC",
    
    # Status colors
    "SUCCESS": "#10B981",
    "SUCCESS_LIGHT": "#D1FAE5",
    "WARNING": "#F59E0B",
    "WARNING_LIGHT": "#FEF3C7",
    "DANGER": "#EF4444",
    "DANGER_LIGHT": "#FEE2E2",
    "INFO": "#3B82F6",
    "INFO_LIGHT": "#DBEAFE",
    
    # Border and effects
    "BORDER": "#E2E8F0",
    "BORDER_LIGHT": "#CBD5E1",
    "SHADOW": "rgba(0, 0, 0, 0.1)",
    "GLOW": "rgba(124, 58, 237, 0.2)",
    
    # Gradients
    "GRADIENT_START": "#7C3AED",
    "GRADIENT_END": "#06B6D4",
    
    # Component dimensions
    "BUTTON_RADIUS": "12px",
    "BUTTON_HEIGHT": "44px",
    "CARD_RADIUS": "16px",
    "INPUT_RADIUS": "8px",
}


# ========== Gradients ==========

def get_gradients(theme: Dict[str, str]) -> Dict[str, str]:
    """Generate gradient definitions for the given theme."""
    return {
        "primary": f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {theme['GRADIENT_START']}, stop:1 {theme['GRADIENT_END']})",
        "primary_vertical": f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {theme['GRADIENT_START']}, stop:1 {theme['GRADIENT_END']})",
        "primary_diagonal": f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {theme['GRADIENT_START']}, stop:1 {theme['GRADIENT_END']})",
        "success": f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {theme['SUCCESS']}, stop:1 {theme['SUCCESS_LIGHT']})",
        "warning": f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {theme['WARNING']}, stop:1 {theme['WARNING_LIGHT']})",
        "danger": f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {theme['DANGER']}, stop:1 {theme['DANGER_LIGHT']})",
        "info": f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {theme['INFO']}, stop:1 {theme['INFO_LIGHT']})",
        "surface": f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {theme['BACKGROUND']}, stop:0.5 {theme['BACKGROUND_ALT']}, stop:1 {theme['BACKGROUND']})",
    }


# ========== CSS Generation ==========

def get_theme_css(theme_name: str = "dark") -> str:
    """Generate complete CSS stylesheet for the application theme."""
    theme = DARK_THEME if theme_name == "dark" else LIGHT_THEME
    gradients = get_gradients(theme)

    return f"""
        /* ========== Base Styles ========== */
        QWidget {{
            background: transparent;
            font-family: 'Poppins', 'Inter', 'Segoe UI', system-ui, sans-serif;
            font-size: 13px;
            color: {theme["TEXT_PRIMARY"]};
        }}

        QMainWindow {{
            background: {gradients["surface"]};
        }}

        /* ========== Scrollbars ========== */
        QScrollBar:vertical {{
            border: none;
            background: {theme["SURFACE"]};
            width: 10px;
            margin: 0;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical {{
            background: {theme["PRIMARY"]};
            min-height: 30px;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {theme["PRIMARY_LIGHT"]};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}

        QScrollBar:horizontal {{
            background: {theme["SURFACE"]};
            height: 10px;
            border-radius: 5px;
        }}

        QScrollBar::handle:horizontal {{
            background: {theme["SURFACE_LIGHT"]};
            border-radius: 5px;
            min-width: 30px;
        }}

        QScrollArea {{
            background: transparent;
            border: none;
        }}

        /* ========== Tab Widget ========== */
        QTabWidget::pane {{
            border: none;
            background: transparent;
        }}

        QTabBar {{
            background: transparent;
        }}

        QTabBar::tab {{
            background: {theme["SURFACE"]};
            color: {theme["TEXT_SECONDARY"]};
            padding: 12px 24px;
            margin-right: 8px;
            border-radius: {theme["BUTTON_RADIUS"]};
            border: 1px solid {theme["BORDER"]};
            font-weight: 500;
        }}

        QTabBar::tab:selected {{
            background: {gradients["primary"]};
            color: white;
            border: none;
            font-weight: 600;
        }}

        QTabBar::tab:hover:!selected {{
            background: {theme["SURFACE_LIGHT"]};
            color: {theme["TEXT_PRIMARY"]};
            border-color: {theme["PRIMARY"]};
        }}

        /* ========== Labels ========== */
        QLabel {{
            color: {theme["TEXT_PRIMARY"]};
        }}

        QLabel.title {{
            font-size: 28px;
            font-weight: 800;
            color: {theme["PRIMARY"]};
        }}

        QLabel.subtitle {{
            font-size: 14px;
            color: {theme["TEXT_SECONDARY"]};
            font-weight: 400;
        }}

        /* ========== Group Box ========== */
        QGroupBox {{
            font-size: 14px;
            font-weight: 600;
            color: {theme["TEXT_PRIMARY"]};
            border: 1px solid {theme["BORDER"]};
            border-radius: {theme["CARD_RADIUS"]};
            margin-top: 1em;
            padding: 20px;
            padding-top: 1.5em;
            background: {theme["SURFACE"]};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
        }}

        /* ========== Text Edit ========== */
        QTextEdit {{
            background: {theme["SURFACE"]};
            border: 1px solid {theme["BORDER"]};
            border-radius: {theme["CARD_RADIUS"]};
            padding: 12px;
            color: {theme["TEXT_PRIMARY"]};
            font-family: 'JetBrains Mono', 'Cascadia Code', 'Consolas', monospace;
            font-size: 12px;
            selection-background-color: {theme["PRIMARY"]};
        }}

        /* ========== List Widget ========== */
        QListWidget {{
            background: {theme["SURFACE"]};
            border: 1px solid {theme["BORDER"]};
            border-radius: {theme["CARD_RADIUS"]};
            padding: 8px;
            outline: none;
        }}

        QListWidget::item {{
            background: {theme["SURFACE"]};
            border-radius: 8px;
            padding: 8px;
            margin: 2px;
        }}

        QListWidget::item:hover {{
            background: {theme["SURFACE_LIGHT"]};
        }}

        QListWidget::item:selected {{
            background: {gradients["primary"]};
            color: white;
        }}

        /* ========== Input Controls ========== */
        QSpinBox, QDoubleSpinBox {{
            background: {theme["SURFACE"]};
            border: 1px solid {theme["BORDER"]};
            border-radius: {theme["INPUT_RADIUS"]};
            padding: 8px 12px;
            color: {theme["TEXT_PRIMARY"]};
            font-weight: 500;
            min-height: 36px;
            selection-background-color: {theme["PRIMARY"]};
        }}

        QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {theme["PRIMARY"]};
        }}

        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {theme["PRIMARY"]};
            background: {theme["SURFACE_LIGHT"]};
        }}

        QSpinBox::up-button, QSpinBox::down-button,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
            border: none;
            background: {theme["SURFACE_LIGHT"]};
            border-radius: 4px;
            width: 20px;
        }}

        /* ========== Slider ========== */
        QSlider::groove:horizontal {{
            background: {theme["SURFACE_LIGHT"]};
            height: 6px;
            border-radius: 3px;
        }}

        QSlider::handle:horizontal {{
            background: {gradients["primary"]};
            width: 20px;
            height: 20px;
            margin: -7px 0;
            border-radius: 10px;
            border: 2px solid white;
        }}

        QSlider::sub-page:horizontal {{
            background: {gradients["primary"]};
            border-radius: 3px;
        }}

        /* ========== Progress Bar ========== */
        QProgressBar {{
            border: none;
            background: {theme["SURFACE"]};
            border-radius: 10px;
            height: 10px;
            text-align: center;
        }}

        QProgressBar::chunk {{
            background: {gradients["primary"]};
            border-radius: 10px;
        }}

        /* ========== Check Box ========== */
        QCheckBox {{
            color: {theme["TEXT_PRIMARY"]};
            font-size: 14px;
            font-weight: 500;
            spacing: 8px;
        }}

        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {theme["BORDER"]};
            border-radius: 6px;
            background: {theme["SURFACE"]};
        }}

        QCheckBox::indicator:checked {{
            background: {gradients["primary"]};
            border-color: {theme["PRIMARY"]};
        }}

        QCheckBox::indicator:hover {{
            border-color: {theme["PRIMARY_LIGHT"]};
        }}

        /* ========== Buttons ========== */
        QPushButton[variant="primary"] {{
            background: {gradients["primary"]};
            color: white;
            border: none;
            border-radius: {theme["BUTTON_RADIUS"]};
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
            min-height: {theme["BUTTON_HEIGHT"]};
        }}

        QPushButton[variant="primary"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {theme["PRIMARY_LIGHT"]}, stop:1 {theme["ACCENT_LIGHT"]});
        }}

        QPushButton[variant="primary"]:pressed {{
            background: {theme["PRIMARY_DARK"]};
        }}

        QPushButton[variant="primary"]:disabled {{
            background: {theme["SURFACE_LIGHT"]};
            color: {theme["TEXT_MUTED"]};
        }}

        QPushButton[variant="secondary"] {{
            background: transparent;
            color: {theme["TEXT_PRIMARY"]};
            border: 2px solid {theme["PRIMARY"]};
            border-radius: {theme["BUTTON_RADIUS"]};
            padding: 10px 22px;
            font-weight: 600;
            min-height: {theme["BUTTON_HEIGHT"]};
        }}

        QPushButton[variant="secondary"]:hover {{
            background: {theme["PRIMARY"]};
            color: white;
            border-color: {theme["PRIMARY"]};
        }}

        QPushButton[variant="ghost"] {{
            background: transparent;
            color: {theme["TEXT_SECONDARY"]};
            border: none;
            border-radius: {theme["BUTTON_RADIUS"]};
            padding: 8px 16px;
            font-weight: 500;
        }}

        QPushButton[variant="ghost"]:hover {{
            background: {theme["SURFACE_LIGHT"]};
            color: {theme["TEXT_PRIMARY"]};
        }}

        QPushButton[variant="success"] {{
            background: {gradients["success"]};
            color: white;
            border: none;
            border-radius: {theme["BUTTON_RADIUS"]};
            padding: 12px 24px;
            font-weight: 600;
            min-height: {theme["BUTTON_HEIGHT"]};
        }}

        QPushButton[variant="success"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {theme["SUCCESS_LIGHT"]}, stop:1 {theme["SUCCESS"]});
        }}

        QPushButton[variant="danger"] {{
            background: {gradients["danger"]};
            color: white;
            border: none;
            border-radius: {theme["BUTTON_RADIUS"]};
            padding: 12px 24px;
            font-weight: 600;
            min-height: {theme["BUTTON_HEIGHT"]};
        }}

        QPushButton[variant="danger"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {theme["DANGER_LIGHT"]}, stop:1 {theme["DANGER"]});
        }}

        QPushButton[variant="icon"] {{
            background: {theme["SURFACE"]};
            color: {theme["TEXT_PRIMARY"]};
            border: 1px solid {theme["BORDER"]};
            border-radius: 10px;
            padding: 10px;
            min-width: 40px;
            min-height: 40px;
        }}

        QPushButton[variant="icon"]:hover {{
            background: {theme["SURFACE_LIGHT"]};
            border-color: {theme["PRIMARY"]};
        }}

        QPushButton[variant="icon"]:disabled {{
            background: {theme["SURFACE"]};
            color: {theme["TEXT_MUTED"]};
            border-color: {theme["SURFACE_LIGHT"]};
        }}

        QPushButton[variant="threshold"] {{
            background: {theme["SURFACE"]};
            color: {theme["TEXT_PRIMARY"]};
            border: 2px solid {theme["BORDER"]};
            border-radius: 10px;
            padding: 8px 16px;
            font-weight: 500;
            font-size: 12px;
        }}

        QPushButton[variant="threshold"]:hover {{
            border-color: {theme["PRIMARY"]};
            background: {theme["SURFACE_LIGHT"]};
        }}

        QPushButton[variant="threshold"]:checked {{
            background: {gradients["primary"]};
            color: white;
            border-color: {theme["PRIMARY"]};
            font-weight: 600;
        }}

        /* ========== Menu Bar ========== */
        QMenuBar {{
            background: {theme["SURFACE"]};
            border-bottom: 1px solid {theme["BORDER"]};
            padding: 4px;
        }}

        QMenuBar::item {{
            background: transparent;
            padding: 8px 16px;
            border-radius: 6px;
            color: {theme["TEXT_PRIMARY"]};
        }}

        QMenuBar::item:selected {{
            background: {theme["PRIMARY_LIGHT"]};
            color: {theme["PRIMARY"]};
        }}

        QMenu {{
            background: {theme["SURFACE"]};
            border: 1px solid {theme["BORDER"]};
            border-radius: 8px;
            padding: 4px;
        }}

        QMenu::item {{
            padding: 8px 24px;
            border-radius: 4px;
        }}

        QMenu::item:selected {{
            background: {theme["PRIMARY"]};
            color: white;
        }}

        /* ========== Status Bar ========== */
        QStatusBar {{
            background: {theme["SURFACE"]};
            border-top: 1px solid {theme["BORDER"]};
            color: {theme["TEXT_SECONDARY"]};
            font-size: 13px;
        }}

        /* ========== Splitter ========== */
        QSplitter::handle {{
            background: {theme["BORDER"]};
            width: 2px;
        }}

        QSplitter::handle:hover {{
            background: {theme["PRIMARY"]};
        }}

        /* ========== Tool Tip ========== */
        QToolTip {{
            background: {theme["SURFACE"]};
            color: {theme["TEXT_PRIMARY"]};
            border: 1px solid {theme["BORDER"]};
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
        }}

        /* ========== Message Box ========== */
        QMessageBox {{
            background: {theme["SURFACE"]};
        }}
        
        QMessageBox QLabel {{
            color: {theme["TEXT_PRIMARY"]};
        }}
    """


# ========== Animated Widgets ==========

class AnimatedButton(QPushButton):
    """Button with hover animation effect."""
    
    def __init__(self, text: str = "", parent: QWidget = None):
        super().__init__(text, parent)
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.OutBack)
        self.setCursor(Qt.PointingHandCursor)

    def enterEvent(self, event):
        try:
            self._animation.stop()
            self._animation.setStartValue(self.geometry())
            self._animation.setEndValue(self.geometry().adjusted(-2, -2, 4, 4))
            self._animation.start()
        except Exception:
            pass
        super().enterEvent(event)

    def leaveEvent(self, event):
        try:
            self._animation.stop()
            self._animation.setStartValue(self.geometry())
            self._animation.setEndValue(self.geometry().adjusted(2, 2, -4, -4))
            self._animation.start()
        except Exception:
            pass
        super().leaveEvent(event)


class GlowCard(QFrame):
    """Card with glow effect on hover."""
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(30)
        self.shadow.setOffset(0, 4)
        self.shadow.setColor(QColor(124, 58, 237, 80))
        self.setGraphicsEffect(self.shadow)

        self.hover_animation = QPropertyAnimation(self.shadow, b"blurRadius")
        self.hover_animation.setDuration(300)
        self.hover_animation.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        try:
            self.hover_animation.stop()
            self.hover_animation.setStartValue(self.shadow.blurRadius())
            self.hover_animation.setEndValue(50)
            self.hover_animation.start()
        except Exception:
            pass
        super().enterEvent(event)

    def leaveEvent(self, event):
        try:
            self.hover_animation.stop()
            self.hover_animation.setStartValue(self.shadow.blurRadius())
            self.hover_animation.setEndValue(30)
            self.hover_animation.start()
        except Exception:
            pass
        super().leaveEvent(event)


class FadeLabel(QLabel):
    """Label with fade-in animation."""
    
    def __init__(self, text: str = "", parent: QWidget = None):
        super().__init__(text, parent)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_in()

    def fade_in(self):
        try:
            self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.animation.setDuration(500)
            self.animation.setStartValue(0)
            self.animation.setEndValue(1)
            self.animation.setEasingCurve(QEasingCurve.InOutCubic)
            self.animation.start()
        except Exception:
            pass


class PulseWidget(QWidget):
    """Widget with pulsing animation for loading states."""
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self._animation = None
        
    def start_pulse(self):
        """Start the pulsing animation."""
        if self._animation:
            self._animation.stop()
        
        self._animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self._animation.setDuration(1000)
        self._animation.setStartValue(0.3)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(QEasingCurve.InOutSine)
        self._animation.setLoopCount(-1)  # Infinite loop
        self._animation.start()
        
    def stop_pulse(self):
        """Stop the pulsing animation."""
        if self._animation:
            self._animation.stop()
        self.opacity_effect.setOpacity(1.0)


# ========== UI Helper Functions ==========

def apply_modern_card_style(widget: QWidget, theme: Dict[str, str] = None, color: str = None) -> None:
    """Apply modern card styling to a widget."""
    if theme is None:
        theme = DARK_THEME
    bg_color = color or theme["SURFACE"]
    widget.setStyleSheet(f"""
        background: {bg_color};
        border: 1px solid {theme["BORDER"]};
        border-radius: {theme["CARD_RADIUS"]};
        padding: 20px;
    """)
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(25)
    shadow.setOffset(0, 4)
    try:
        vals = theme["SHADOW"][5:-1].split(",")
        rgba = [int(v.strip()) for v in vals]
        shadow.setColor(QColor(*rgba))
    except Exception:
        shadow.setColor(QColor(0, 0, 0, 60))
    widget.setGraphicsEffect(shadow)


def create_threshold_button(text: str, value: Any, is_active: bool = False) -> AnimatedButton:
    """Create a threshold selection button."""
    btn = AnimatedButton(text)
    btn.setProperty("variant", "threshold")
    btn.setCheckable(True)
    btn.setChecked(is_active)
    btn.setCursor(Qt.PointingHandCursor)
    btn.value = value
    return btn


def create_gradient_label(text: str, theme: Dict[str, str] = None, font_size: int = 28, parent=None) -> FadeLabel:
    """Create a label with gradient styling."""
    if theme is None:
        theme = DARK_THEME
    label = FadeLabel(text, parent)
    label.setStyleSheet(f"""
        font-size: {font_size}px;
        font-weight: 800;
        color: {theme["PRIMARY"]};
    """)
    return label


def create_status_badge(text: str, status: str = "info", theme: Dict[str, str] = None) -> QLabel:
    """Create a colored status badge label."""
    if theme is None:
        theme = DARK_THEME
    
    colors = {
        "success": (theme["SUCCESS"], theme["SUCCESS_LIGHT"]),
        "warning": (theme["WARNING"], theme["WARNING_LIGHT"]),
        "danger": (theme["DANGER"], theme["DANGER_LIGHT"]),
        "info": (theme["INFO"], theme["INFO_LIGHT"]),
    }
    
    fg_color, bg_color = colors.get(status, colors["info"])
    
    label = QLabel(text)
    label.setStyleSheet(f"""
        background: {bg_color};
        color: {fg_color};
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 12px;
    """)
    return label


# ========== Theme Manager ==========

class ThemeManager:
    """Manages application themes and provides theme-related utilities."""
    
    DARK_THEME = DARK_THEME
    LIGHT_THEME = LIGHT_THEME
    
    _current_theme = "dark"
    
    @classmethod
    def get_current_theme(cls) -> Dict[str, str]:
        """Get the current theme dictionary."""
        return DARK_THEME if cls._current_theme == "dark" else LIGHT_THEME
    
    @classmethod
    def set_theme(cls, theme_name: str) -> None:
        """Set the current theme."""
        cls._current_theme = theme_name
    
    @classmethod
    def toggle_theme(cls) -> str:
        """Toggle between dark and light theme. Returns the new theme name."""
        cls._current_theme = "light" if cls._current_theme == "dark" else "dark"
        return cls._current_theme
    
    @classmethod
    def get_theme_css(cls, theme_name: str = None) -> str:
        """Generate CSS for the specified theme (or current theme if not specified)."""
        if theme_name is None:
            theme_name = cls._current_theme
        return get_theme_css(theme_name)
    
    @classmethod
    def get_gradients(cls, theme_name: str = None) -> Dict[str, str]:
        """Get gradients for the specified theme."""
        if theme_name is None:
            theme_name = cls._current_theme
        theme = DARK_THEME if theme_name == "dark" else LIGHT_THEME
        return get_gradients(theme)


# For backward compatibility - export at module level
def get_theme(theme_name: str = "dark") -> Dict[str, str]:
    """Get theme dictionary by name."""
    return DARK_THEME if theme_name == "dark" else LIGHT_THEME
