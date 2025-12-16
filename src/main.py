# ========== Environment & Core Setup (must be first) ==========
import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

import sys
import logging
import json
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List, Set
from pathlib import Path
import io
import tempfile

# Pillow (single, clean import)
from PIL import Image, ImageFile, UnidentifiedImageError
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Numeric / image libs
import numpy as np
import cv2
import imagehash
import shutil

# Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QFileDialog, QMessageBox,
    QProgressBar, QLabel, QTabWidget, QGroupBox,
    QSpinBox, QTextEdit, QScrollArea,
    QListWidget, QListWidgetItem, QDoubleSpinBox,
    QSizePolicy, QFrame, QGraphicsDropShadowEffect,
    QStackedWidget, QGraphicsOpacityEffect, QSlider
)
from PySide6.QtCore import (
    QThread, Signal, Qt, QTime, QSize, QTimer,
    QMutex, QWaitCondition, QPropertyAnimation,
    QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup,
    Property
)
from PySide6.QtGui import (
    QFont, QColor, QPalette, QPixmap, QIcon,
    QPainter, QLinearGradient, QBrush, QPen
)

# ========== DeepFace availability ==========
DEEPFACE_AVAILABLE = False
DEEPFACE_ERROR = None
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    print("✅ DeepFace available for face recognition")
except Exception as e:
    DEEPFACE_AVAILABLE = False
    DEEPFACE_ERROR = str(e)
    print(f"⚠️ DeepFace NOT available: {e}")
    logging.warning("DeepFace not available: %s", e)

# ========== Logging ==========
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ========== Modern Color Themes ==========
class ThemeManager:
    """Manages themes and animations"""

    DARK_THEME = {
        "PRIMARY": "#7C3AED",
        "PRIMARY_LIGHT": "#A78BFA",
        "ACCENT": "#06B6D4",
        "ACCENT_LIGHT": "#67E8F9",
        "BACKGROUND": "#0F172A",
        "SURFACE": "#1E293B",
        "SURFACE_LIGHT": "#334155",
        "TEXT_PRIMARY": "#F8FAFC",
        "TEXT_SECONDARY": "#94A3B8",
        "TEXT_MUTED": "#64748B",
        "SUCCESS": "#10B981",
        "WARNING": "#F59E0B",
        "DANGER": "#EF4444",
        "BORDER": "#475569",
        "SHADOW": "rgba(0, 0, 0, 0.3)",
        "GLOW": "rgba(124, 58, 237, 0.3)",
        "GRADIENT_START": "#7C3AED",
        "GRADIENT_END": "#06B6D4",
        "BUTTON_RADIUS": "12px",
        "BUTTON_HEIGHT": "44px",
        "CARD_RADIUS": "16px",
    }

    LIGHT_THEME = {
        "PRIMARY": "#7C3AED",
        "PRIMARY_LIGHT": "#A78BFA",
        "ACCENT": "#06B6D4",
        "ACCENT_LIGHT": "#67E8F9",
        "BACKGROUND": "#F8FAFC",
        "SURFACE": "#FFFFFF",
        "SURFACE_LIGHT": "#F1F5F9",
        "TEXT_PRIMARY": "#0F172A",
        "TEXT_SECONDARY": "#475569",
        "TEXT_MUTED": "#94A3B8",
        "SUCCESS": "#10B981",
        "WARNING": "#F59E0B",
        "DANGER": "#EF4444",
        "BORDER": "#E2E8F0",
        "SHADOW": "rgba(148, 163, 184, 0.1)",
        "GLOW": "rgba(124, 58, 237, 0.1)",
        "GRADIENT_START": "#7C3AED",
        "GRADIENT_END": "#06B6D4",
        "BUTTON_RADIUS": "12px",
        "BUTTON_HEIGHT": "44px",
        "CARD_RADIUS": "16px",
    }

    @classmethod
    def get_theme_css(cls, theme_name: str = "dark") -> str:
        theme = cls.DARK_THEME if theme_name == "dark" else cls.LIGHT_THEME

        return f"""
            QWidget {{
                background: transparent;
                font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
                font-size: 13px;
                color: {theme["TEXT_PRIMARY"]};
            }}

            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {theme["BACKGROUND"]}, stop:1 #111827);
            }}

            QScrollBar:vertical {{
                border: none;
                background: {theme["SURFACE"]};
                width: 10px;
                margin: 0px;
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

            QTabWidget::pane {{
                border: none;
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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme["GRADIENT_START"]}, stop:1 {theme["GRADIENT_END"]});
                color: white;
                border: none;
                font-weight: 600;
                box-shadow: 0 4px 12px {theme["GLOW"]};
            }}

            QTabBar::tab:hover:!selected {{
                background: {theme["SURFACE_LIGHT"]};
                color: {theme["TEXT_PRIMARY"]};
                border-color: {theme["PRIMARY"]};
            }}

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

            QGroupBox {{
                font-size: 14px;
                font-weight: 600;
                color: {theme["TEXT_PRIMARY"]};
                border: none;
                margin-top: 1em;
                padding-top: 0.5em;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }}

            QTextEdit {{
                background: {theme["SURFACE"]};
                border: 1px solid {theme["BORDER"]};
                border-radius: {theme["CARD_RADIUS"]};
                padding: 12px;
                color: {theme["TEXT_PRIMARY"]};
                font-family: 'JetBrains Mono', 'Cascadia Code', monospace;
                font-size: 12px;
                selection-background-color: {theme["PRIMARY"]};
            }}

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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme["PRIMARY"]}, stop:1 {theme["ACCENT"]});
                color: white;
            }}

            QSpinBox, QDoubleSpinBox {{
                background: {theme["SURFACE"]};
                border: 1px solid {theme["BORDER"]};
                border-radius: 8px;
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

            QSlider::groove:horizontal {{
                background: {theme["SURFACE_LIGHT"]};
                height: 6px;
                border-radius: 3px;
            }}

            QSlider::handle:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme["GRADIENT_START"]}, stop:1 {theme["GRADIENT_END"]});
                width: 20px;
                height: 20px;
                margin: -7px 0;
                border-radius: 10px;
                border: 2px solid white;
            }}

            QSlider::sub-page:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme["GRADIENT_START"]}, stop:1 {theme["GRADIENT_END"]});
                border-radius: 3px;
            }}

            QProgressBar {{
                border: none;
                background: {theme["SURFACE"]};
                border-radius: 10px;
                height: 10px;
                text-align: center;
            }}

            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme["GRADIENT_START"]}, stop:1 {theme["GRADIENT_END"]});
                border-radius: 10px;
            }}

            QPushButton[variant="primary"] {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme["GRADIENT_START"]}, stop:1 {theme["GRADIENT_END"]});
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
                box-shadow: 0 8px 20px {theme["GLOW"]};
            }}

            QPushButton[variant="primary"]:pressed {{
                background: {theme["PRIMARY"]};
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
                box-shadow: 0 4px 12px {theme["GLOW"]};
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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme["SUCCESS"]}, stop:1 #34D399);
                color: white;
                border: none;
                border-radius: {theme["BUTTON_RADIUS"]};
                padding: 12px 24px;
                font-weight: 600;
                min-height: {theme["BUTTON_HEIGHT"]};
            }}

            QPushButton[variant="success"]:hover {{
                box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
            }}

            QPushButton[variant="danger"] {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme["DANGER"]}, stop:1 #F87171);
                color: white;
                border: none;
                border-radius: {theme["BUTTON_RADIUS"]};
                padding: 12px 24px;
                font-weight: 600;
                min-height: {theme["BUTTON_HEIGHT"]};
            }}

            QPushButton[variant="danger"]:hover {{
                box-shadow: 0 8px 20px rgba(239, 68, 68, 0.3);
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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme["GRADIENT_START"]}, stop:1 {theme["GRADIENT_END"]});
                color: white;
                border-color: {theme["PRIMARY"]};
                font-weight: 600;
            }}
        """

# ========== Animated Widgets ==========
class AnimatedButton(QPushButton):
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

# ========== Configuration Management ==========
class AppConfig:
    THEME = ThemeManager.DARK_THEME

    DEFAULTS = {
        "BLUR_THRESHOLD": 100,
        "SIMILARITY_THRESHOLD": 20,  # Adjusted for 16x16 multi-hash detection
        "FACE_MATCH_THRESHOLD": 0.85,
        "THUMBNAIL_SIZE": 72,
        "SESSION_FILE": "clean_shot_session.json"
    }

    IMAGE_EXTENSIONS = (
        '.jpg', '.jpeg', '.png', '.bmp', '.webp',
        '.heic', '.heif', '.tiff', '.tif',
        '.raw', '.cr2', '.nef', '.arw', '.orf', '.dng'
    )

    BLUR_PRESETS = {
        "Soft": 50,
        "Normal": 100,
        "Strict": 200,
        "Very Strict": 350
    }

    SIMILARITY_PRESETS = {
        "Loose": 40,      # Allow more variation (scaled for 16x16 hash)
        "Normal": 20,     # Good balance for most photos
        "Strict": 10,     # More strict matching
        "Very Strict": 5  # Nearly identical images only
    }

# ========== Session Management ==========
class ProcessingSession:
    def __init__(self, session_file: str = None):
        self.session_file = session_file or AppConfig.DEFAULTS["SESSION_FILE"]

    def save(self, results: Dict, folder: str, settings: Dict) -> bool:
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "folder": folder,
                "results": results,
                "settings": settings
            }
            with open(self.session_file, 'w') as f:
                json.dump(data, f, indent=2)
            logging.info(f"Session saved to {self.session_file}")
            return True
        except Exception as e:
            logging.error(f"Failed to save session: {e}")
            return False

    def load_last(self) -> Optional[Dict]:
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load session: {e}")
        return None

# ========== UI Helper Utilities ==========
def apply_modern_card_style(widget: QWidget, color: str = None) -> None:
    bg_color = color or AppConfig.THEME["SURFACE"]
    widget.setStyleSheet(f"""
        background: {bg_color};
        border: 1px solid {AppConfig.THEME["BORDER"]};
        border-radius: {AppConfig.THEME["CARD_RADIUS"]};
        padding: 20px;
    """)
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(25)
    shadow.setOffset(0, 4)
    try:
        vals = AppConfig.THEME["SHADOW"][5:-1].split(",")
        rgba = [int(v.strip()) for v in vals]
        shadow.setColor(QColor(*rgba))
    except Exception:
        shadow.setColor(QColor(0, 0, 0, 60))
    widget.setGraphicsEffect(shadow)

def create_threshold_button(text: str, value: Any, is_active: bool = False) -> QPushButton:
    btn = AnimatedButton(text)
    btn.setProperty("variant", "threshold")
    btn.setCheckable(True)
    btn.setChecked(is_active)
    btn.setCursor(Qt.PointingHandCursor)
    btn.value = value
    return btn

def create_gradient_label(text: str, font_size: int = 28, parent=None) -> FadeLabel:
    label = FadeLabel(text, parent)
    label.setStyleSheet(f"""
        font-size: {font_size}px;
        font-weight: 800;
        color: {AppConfig.THEME["PRIMARY"]};
    """)
    return label

# ========== Worker Threads ==========
class BaseProcessor(QThread):
    progress_updated = Signal(int)
    status_updated = Signal(str)
    log_message = Signal(str)

    def __init__(self):
        super().__init__()
        self._is_paused = False
        self._is_stopped = False
        self._pause_cond = QWaitCondition()
        self._pause_lock = QMutex()

    def pause(self) -> None:
        self._is_paused = True
        self.log_message.emit("Processing paused")

    def resume(self) -> None:
        self._is_paused = False
        self._pause_cond.wakeAll()
        self.log_message.emit("Processing resumed")

    def stop(self) -> None:
        self._is_stopped = True
        self.resume()

    def check_paused(self) -> None:
        while self._is_paused:
            self._pause_lock.lock()
            self._pause_cond.wait(self._pause_lock)
            self._pause_lock.unlock()

    def __del__(self):
        try:
            self.quit()
            self.wait(1000)
        except Exception:
            pass

class FaceSearchProcessor(BaseProcessor):
    finished_search = Signal(dict)
    face_found = Signal(str, float)

    def __init__(
        self,
        reference_face_path: str,
        search_folder_path: str,
        similarity_threshold: float = 0.85
    ):
        super().__init__()
        self.reference_face_path: str = reference_face_path
        self.search_folder_path: Path = Path(search_folder_path)
        self.similarity_threshold: float = similarity_threshold
        self.session_manager = ProcessingSession()

    def _ensure_png_for_deepface(self, path_str: str) -> Tuple[str, bool]:
        """
        Convert arbitrary image to a PNG temp file for DeepFace, or return original path on failure.
        Returns (path_to_use, is_temp).
        """
        try:
            ext = Path(path_str).suffix.lower()
            if ext in ('.png', '.jpg', '.jpeg'):
                return path_str, False

            with open(path_str, 'rb') as f:
                data = f.read()

            try:
                img = Image.open(io.BytesIO(data))
                img = img.convert('RGB')
            except Exception:
                nparr = np.frombuffer(data, np.uint8)
                cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if cv_img is None:
                    raise RuntimeError("Cannot decode image for DeepFace")
                cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv_img)

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            img.save(tmp.name, format='PNG')
            tmp.close()
            return tmp.name, True
        except Exception as e:
            self.log_message.emit(f"Could not convert {Path(path_str).name} to PNG for DeepFace: {e}")
            return path_str, False

    def verify_face_match(self, img1_path: str, img2_path: str) -> Tuple[bool, float]:
        """
        Robust face verification using DeepFace.
        Returns: (is_match: bool, similarity: float [0..1])
        """
        if not DEEPFACE_AVAILABLE:
            return False, 0.0

        try:
            if not os.path.exists(img1_path) or not os.path.exists(img2_path):
                self.log_message.emit("Reference or target image missing.")
                return False, 0.0

            tmp1, tmp1_is_temp = self._ensure_png_for_deepface(img1_path)
            tmp2, tmp2_is_temp = self._ensure_png_for_deepface(img2_path)

            last_exception = None
            result = None
            detector_backends = ["opencv", "retinaface", "ssd"]

            for backend in detector_backends:
                try:
                    result = DeepFace.verify(
                        img1_path=tmp1,
                        img2_path=tmp2,
                        model_name="ArcFace",
                        detector_backend=backend,
                        enforce_detection=True,  # CRITICAL: Only compare actual faces, not entire images
                        distance_metric="cosine",
                        align=True,
                        silent=True
                    )
                    break
                except Exception as deep_err:
                    error_str = str(deep_err).lower()
                    # If face not detected, try next backend
                    if "face" in error_str and ("detect" in error_str or "found" in error_str or "could not" in error_str):
                        last_exception = deep_err
                        result = None
                        continue
                    else:
                        last_exception = deep_err
                        self.log_message.emit(
                            f"DeepFace backend {backend} error for {Path(img2_path).name}: {str(deep_err)[:100]}"
                        )
                        result = None
                        continue

            # Cleanup temp PNGs we created
            for p, is_temp in ((tmp1, tmp1_is_temp), (tmp2, tmp2_is_temp)):
                if is_temp:
                    try:
                        if p and Path(p).exists():
                            os.unlink(p)
                    except Exception:
                        pass

            if result is None:
                # Face not detected in one or both images
                self.log_message.emit(f"⚠️ No face detected in {Path(img2_path).name} - skipping")
                return False, 0.0

            is_verified = bool(result.get("verified", False))
            distance = float(result.get("distance", 1.0))
            threshold = float(result.get("threshold", 0.4))

            if threshold > 0:
                normalized_similarity = max(0.0, 1.0 - (distance / threshold))
                normalized_similarity = min(1.0, normalized_similarity)
            else:
                normalized_similarity = max(0.0, min(1.0, 1.0 - distance))

            raw_similarity = max(0.0, min(1.0, 1.0 - distance))
            
            # Use raw similarity directly compared to user's threshold
            # This is more intuitive: if user sets 70% threshold, images with >=70% similarity match
            is_match = raw_similarity >= self.similarity_threshold
            
            if is_match:
                self.log_message.emit(
                    f"✅ MATCH FOUND: {Path(img2_path).name} | "
                    f"similarity={raw_similarity:.1%}, distance={distance:.4f}"
                )
                return True, raw_similarity
            
            # Log why it didn't match
            self.log_message.emit(
                f"No match for {Path(img2_path).name}: similarity {raw_similarity:.1%} < required {self.similarity_threshold:.0%}"
            )

            return False, raw_similarity

        except Exception as e:
            err = str(e)
            img_name = Path(img2_path).name if 'img2_path' in locals() else 'unknown'
            error_display = err[:120] + "..." if len(err) > 120 else err
            self.log_message.emit(f"Error processing {img_name}: {error_display}")
            return False, 0.0

    def create_thumbnail(self, image_path: Path) -> Optional[QPixmap]:
        """Create a thumbnail robustly using PIL, fallback to OpenCV."""
        try:
            with open(str(image_path), 'rb') as f:
                raw = f.read()

            try:
                pil_img = Image.open(io.BytesIO(raw))
                pil_img.thumbnail(
                    (AppConfig.DEFAULTS["THUMBNAIL_SIZE"],
                     AppConfig.DEFAULTS["THUMBNAIL_SIZE"]),
                    Image.Resampling.LANCZOS
                )
                img_byte_arr = io.BytesIO()
                pil_img.save(img_byte_arr, format='PNG')
                pixmap = QPixmap()
                pixmap.loadFromData(img_byte_arr.getvalue())
                return pixmap
            except Exception:
                nparr = np.frombuffer(raw, np.uint8)
                cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if cv_img is None:
                    self.log_message.emit(f"Thumbnail: cannot decode {image_path.name}")
                    return None

                h, w = cv_img.shape[:2]
                max_side = max(h, w)
                scale = AppConfig.DEFAULTS["THUMBNAIL_SIZE"] / float(max_side)
                if scale < 1.0:
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    cv_img = cv2.resize(cv_img, (new_w, new_h), interpolation=cv2.INTER_AREA)

                success, png = cv2.imencode('.png', cv_img)
                if not success:
                    return None
                pixmap = QPixmap()
                pixmap.loadFromData(png.tobytes())
                return pixmap
        except Exception as e:
            self.log_message.emit(f"Thumbnail creation failed for {image_path.name}: {e}")
            return None

    def pre_process_image(self, image_path: Path) -> bool:
        """Pre-process and validate image before face detection"""
        try:
            if not image_path.exists():
                self.log_message.emit(f"File missing: {image_path.name}")
                return False

            try:
                with open(str(image_path), 'rb') as f:
                    raw = f.read()
            except Exception as e:
                self.log_message.emit(f"Failed to open {image_path.name}: {e}")
                return False

            try:
                img = Image.open(io.BytesIO(raw))
                img.load()
                if getattr(img, "size", None) is None:
                    self.log_message.emit(f"No dimensions found for {image_path.name}")
                    return False
                return True
            except (UnidentifiedImageError, OSError, ValueError):
                try:
                    nparr = np.frombuffer(raw, np.uint8)
                    cv_img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
                    if cv_img is None:
                        self.log_message.emit(f"cv2 can't decode {image_path.name}")
                        return False
                    return True
                except Exception as cv_err:
                    self.log_message.emit(
                        f"Both PIL & OpenCV failed for {image_path.name}: {str(cv_err)[:100]}"
                    )
                    return False

        except Exception as e:
            self.log_message.emit(f"Unexpected preprocess error for {image_path.name}: {e}")
            return False

    def run(self) -> None:
        try:
            if not DEEPFACE_AVAILABLE:
                self.status_updated.emit("DeepFace unavailable")
                self.log_message.emit("DeepFace unavailable - aborting search")
                return

            self.log_message.emit("=" * 40)
            self.log_message.emit("Starting face search (strict DeepFace mode)")

            image_files = [
                f for f in self.search_folder_path.iterdir()
                if f.suffix.lower() in AppConfig.IMAGE_EXTENSIONS
            ]

            valid_images = []
            for image_path in image_files:
                if self.pre_process_image(image_path):
                    valid_images.append(image_path)
                else:
                    self.log_message.emit(f"Skipping invalid image: {image_path.name}")

            total = len(valid_images)
            skipped = len(image_files) - total

            if skipped > 0:
                self.log_message.emit(f"Skipped {skipped} invalid/unreadable images")

            if total == 0:
                self.status_updated.emit("No valid images found")
                return

            self.log_message.emit(f"Searching {total} valid images")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_folder = self.search_folder_path / f"Matched_Faces_{timestamp}"
            out_folder.mkdir(parents=True, exist_ok=True)

            matched: List[Tuple[str, float]] = []
            for idx, image_path in enumerate(valid_images):
                if self._is_stopped:
                    self.log_message.emit("Processing stopped by user")
                    return

                self.check_paused()

                progress = int((idx + 1) / total * 100)
                self.progress_updated.emit(progress)
                self.status_updated.emit(f"Checking {image_path.name}")

                is_match, sim = self.verify_face_match(
                    str(self.reference_face_path),
                    str(image_path)
                )

                if is_match:
                    dest = out_folder / image_path.name
                    try:
                        shutil.copy2(str(image_path), str(dest))
                    except Exception as e:
                        self.log_message.emit(f"Could not copy {image_path.name}: {e}")

                    matched.append((image_path.name, sim))
                    self.face_found.emit(image_path.name, sim)
                    self.log_message.emit(f"✅ MATCH: {image_path.name} (sim: {sim:.2%})")

            settings = {
                "similarity_threshold": self.similarity_threshold,
                "reference_face": str(self.reference_face_path)
            }
            self.session_manager.save(
                {
                    "matched": matched,
                    "total_searched": total,
                    "skipped": skipped,
                    "output_folder": str(out_folder)
                },
                str(self.search_folder_path),
                settings
            )

            results = {
                "total_searched": total,
                "skipped": skipped,
                "matched": len(matched),
                "matched_files": matched,
                "output_folder": str(out_folder),
                "method": "DeepFace (strict)"
            }

            self.log_message.emit("=" * 40)
            self.log_message.emit("Search complete!")
            self.log_message.emit(f"• Valid images processed: {total}")
            self.log_message.emit(f"• Invalid images skipped: {skipped}")
            self.log_message.emit(f"• Matches found: {len(matched)}")
            self.log_message.emit(f"• Output folder: {out_folder.name}")
            self.log_message.emit("=" * 40)

            self.finished_search.emit(results)

        except Exception as e:
            self.log_message.emit(f"❌ Error in face search: {e}")
            self.status_updated.emit(f"Error: {e}")


class PhotoProcessor(BaseProcessor):
    finished_processing = Signal(dict)

    def __init__(
        self,
        folder_path: str,
        blur_threshold: int = 100,
        similarity_threshold: int = 5
    ):
        super().__init__()
        self.folder_path: Path = Path(folder_path)
        self.blur_threshold: int = blur_threshold
        self.similarity_threshold: int = similarity_threshold
        self.seen_hashes: List[Dict] = []  # Stores hash info dictionaries
        self.session_manager = ProcessingSession()

    def is_blurry(self, image_path: Path) -> bool:
        """
        Enhanced blur detection using multiple metrics:
        1. Laplacian variance (edge detection)
        2. Gradient magnitude (Sobel)
        3. Normalize by image size for fair comparison
        """
        try:
            img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                return False
            
            # Resize image to standard size for consistent comparison
            # This prevents high-res images from always appearing "sharp"
            h, w = img.shape[:2]
            max_dim = 800
            if max(h, w) > max_dim:
                scale = max_dim / max(h, w)
                img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
            
            # Method 1: Laplacian variance (primary method)
            laplacian = cv2.Laplacian(img, cv2.CV_64F)
            laplacian_var = laplacian.var()
            
            # Method 2: Sobel gradient magnitude
            sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(sobelx**2 + sobely**2).mean()
            
            # Combined scoring: weighted average of both metrics
            # Lower scores = more blurry
            blur_score = (laplacian_var * 0.7) + (gradient_magnitude * 0.3)
            
            is_blur = blur_score < self.blur_threshold
            
            if is_blur:
                self.log_message.emit(f"Blur score for {image_path.name}: {blur_score:.1f} (threshold: {self.blur_threshold})")
            
            return is_blur
            
        except Exception as e:
            self.log_message.emit(f"Blur error: {e}")
            return False

    def is_duplicate(self, image_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Enhanced duplicate detection using multiple hash algorithms:
        1. Average hash - good for overall similarity
        2. Perceptual hash (pHash) - robust to scaling/compression
        3. Difference hash (dHash) - captures gradients
        
        Uses larger hash size (16x16) for better precision.
        """
        try:
            img = Image.open(str(image_path))
            
            # Convert to RGB if needed (some formats may be in other modes)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Use larger hash size for better precision
            hash_size = 16
            
            # Calculate multiple hash types
            avg_hash = imagehash.average_hash(img, hash_size=hash_size)
            p_hash = imagehash.phash(img, hash_size=hash_size)
            d_hash = imagehash.dhash(img, hash_size=hash_size)
            
            # Store as combined hash info
            current_hashes = {
                'avg': avg_hash,
                'phash': p_hash,
                'dhash': d_hash,
                'path': str(image_path)
            }
            
            # Check against seen images using weighted voting
            for seen in self.seen_hashes:
                if isinstance(seen, dict):
                    # Calculate differences for each hash type
                    avg_diff = avg_hash - seen['avg']
                    p_diff = p_hash - seen['phash']
                    d_diff = d_hash - seen['dhash']
                    
                    # Weighted average: pHash is most robust, give it more weight
                    weighted_diff = (avg_diff * 0.25) + (p_diff * 0.5) + (d_diff * 0.25)
                    
                    # If weighted difference is below threshold, it's a duplicate
                    if weighted_diff <= self.similarity_threshold:
                        original_name = Path(seen['path']).name
                        self.log_message.emit(
                            f"Duplicate found: {image_path.name} matches {original_name} "
                            f"(diff: {weighted_diff:.1f}, threshold: {self.similarity_threshold})"
                        )
                        return True, original_name
                else:
                    # Backward compatibility with old hash format
                    if avg_hash - seen <= self.similarity_threshold:
                        return True, "previous image"
            
            self.seen_hashes.append(current_hashes)
            return False, None
            
        except Exception as e:
            self.log_message.emit(f"Duplicate error for {image_path.name}: {e}")
            return False, None

    def run(self) -> None:
        try:
            categories = ["Good_Photos", "Blurry_Photos", "Duplicate_Photos"]
            for category in categories:
                category_path = self.folder_path / category
                category_path.mkdir(parents=True, exist_ok=True)

            files = [
                f for f in self.folder_path.iterdir()
                if f.suffix.lower() in AppConfig.IMAGE_EXTENSIONS
            ]

            total = len(files)
            if total == 0:
                self.status_updated.emit("No images")
                return

            results = {"processed": 0, "good": 0, "blurry": 0, "duplicate": 0}

            for idx, image_path in enumerate(files):
                if self._is_stopped:
                    self.log_message.emit("Processing stopped by user")
                    return

                self.check_paused()

                if not image_path.exists():
                    continue

                progress = int((idx + 1) / total * 100)
                self.progress_updated.emit(progress)
                self.status_updated.emit(f"Processing {image_path.name}")

                results["processed"] += 1

                is_dup, _ = self.is_duplicate(image_path)
                if is_dup:
                    target = "Duplicate_Photos"
                    results["duplicate"] += 1
                    self.log_message.emit(f"Duplicate: {image_path.name}")
                elif self.is_blurry(image_path):
                    target = "Blurry_Photos"
                    results["blurry"] += 1
                    self.log_message.emit(f"Blurry: {image_path.name}")
                else:
                    target = "Good_Photos"
                    results["good"] += 1
                    self.log_message.emit(f"Good: {image_path.name}")

                try:
                    dest = self.folder_path / target / image_path.name
                    shutil.move(str(image_path), str(dest))
                except Exception as e:
                    self.log_message.emit(f"Move failed for {image_path.name}: {e}")

            settings = {
                "blur_threshold": self.blur_threshold,
                "similarity_threshold": self.similarity_threshold
            }
            self.session_manager.save(results, str(self.folder_path), settings)

            self.finished_processing.emit(results)

        except Exception as e:
            self.log_message.emit(f"Processing error: {e}")
            self.status_updated.emit(f"Error: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CLEAN SHOT — Photo Organizer & Face Search")
        self.setMinimumSize(1080, 720)

        self.session_manager = ProcessingSession()
        self.last_session = self.session_manager.load_last()

        self.log_text = None

        self.setup_palette()
        self.setup_ui()

        if not DEEPFACE_AVAILABLE:
            self.show_warning_message()

    def setup_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(AppConfig.THEME["BACKGROUND"]))
        palette.setColor(QPalette.WindowText, QColor(AppConfig.THEME["TEXT_PRIMARY"]))
        palette.setColor(QPalette.Base, QColor(AppConfig.THEME["SURFACE"]))
        palette.setColor(QPalette.AlternateBase, QColor(AppConfig.THEME["SURFACE_LIGHT"]))
        palette.setColor(QPalette.ToolTipBase, QColor(AppConfig.THEME["SURFACE"]))
        palette.setColor(QPalette.ToolTipText, QColor(AppConfig.THEME["TEXT_PRIMARY"]))
        palette.setColor(QPalette.Text, QColor(AppConfig.THEME["TEXT_PRIMARY"]))
        palette.setColor(QPalette.Button, QColor(AppConfig.THEME["SURFACE"]))
        palette.setColor(QPalette.ButtonText, QColor(AppConfig.THEME["TEXT_PRIMARY"]))
        palette.setColor(QPalette.BrightText, QColor(AppConfig.THEME["ACCENT"]))
        palette.setColor(QPalette.Highlight, QColor(AppConfig.THEME["PRIMARY"]))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)

    def show_warning_message(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Face Search Disabled")
        msg.setText("DeepFace is not available. Person-based face search will not work.")
        msg.setInformativeText(
            f"Install 'deepface' and 'tf-keras', then restart the app.\n\nDetails: {DEEPFACE_ERROR or 'Unknown'}"
        )
        msg.setStyleSheet("""
            QMessageBox {
                background: #1E293B;
                color: #F8FAFC;
            }
            QLabel {
                color: #F8FAFC;
            }
        """)
        msg.exec()

    def troubleshoot_image(self, image_path: str):
        try:
            img = Image.open(image_path)
            info = f"""
            📊 Image Analysis: {Path(image_path).name}

            • Size: {img.size[0]}x{img.size[1]} pixels
            • Mode: {img.mode}
            • Format: {img.format}
            • File size: {Path(image_path).stat().st_size // 1024} KB

            Image appears to be valid.
            """

            cv_img = cv2.imread(image_path)
            if cv_img is not None:
                info += f"""
            ✅ OpenCV can read this image.
            • Channels: {cv_img.shape[2] if len(cv_img.shape) > 2 else 1}
            • Data type: {cv_img.dtype}
            """
            else:
                info += "\n❌ OpenCV cannot read this image (might be corrupted)."

            QMessageBox.information(self, "Image Troubleshooter", info)

        except Exception as e:
            QMessageBox.warning(
                self,
                "Troubleshoot Failed",
                f"Cannot analyze {Path(image_path).name}:\n\n{str(e)}"
            )

    def setup_ui(self) -> None:
        self.setStyleSheet(ThemeManager.get_theme_css("dark"))

        central = QWidget()
        central.setObjectName("centralWidget")
        central.setStyleSheet("""
            #centralWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0F172A, stop:0.5 #1E1B4B, stop:1 #0F172A);
                border: none;
            }
        """)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        self.setCentralWidget(central)

        self.setup_header(main_layout)

        content_widget = GlowCard()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.setup_tabs(content_layout)

        main_layout.addWidget(content_widget)

    def setup_header(self, parent_layout: QVBoxLayout) -> None:
        header_widget = QWidget()
        header_widget.setMaximumHeight(80)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)

        self.logo_btn = AnimatedButton("📸")
        self.logo_btn.setProperty("variant", "icon")
        self.logo_btn.setFixedSize(48, 48)
        self.logo_btn.setFont(QFont("Segoe UI Emoji", 20))
        logo_layout.addWidget(self.logo_btn)

        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(10, 0, 0, 0)

        self.title_label = create_gradient_label("CLEAN SHOT", 32)
        self.subtitle_label = QLabel("AI Photo Organizer & Face Search")
        self.subtitle_label.setProperty("class", "subtitle")

        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)

        logo_layout.addWidget(title_container)
        header_layout.addWidget(logo_container)
        header_layout.addStretch()

        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(8)

        if self.last_session:
            session_btn = AnimatedButton("📁 Load Session")
            session_btn.setProperty("variant", "ghost")
            session_btn.clicked.connect(self.load_last_session)
            button_layout.addWidget(session_btn)

        self.theme_btn = AnimatedButton("🌙 Theme")
        self.theme_btn.setProperty("variant", "ghost")
        self.theme_btn.setCheckable(True)
        self.theme_btn.clicked.connect(self.toggle_theme)
        button_layout.addWidget(self.theme_btn)

        about_btn = AnimatedButton("ℹ️ About")
        about_btn.setProperty("variant", "ghost")
        about_btn.clicked.connect(self.show_about)
        button_layout.addWidget(about_btn)

        header_layout.addWidget(button_container)
        parent_layout.addWidget(header_widget)

    def setup_tabs(self, parent_layout: QVBoxLayout) -> None:
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
        """)

        self.setup_organizer_tab()
        self.setup_face_search_tab()
        self.setup_settings_tab()
        self.setup_log_tab()

        parent_layout.addWidget(self.tabs)

    def setup_organizer_tab(self) -> None:
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background: transparent;")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        folder_card = GlowCard()
        folder_layout = QVBoxLayout(folder_card)
        folder_layout.setSpacing(15)

        folder_title = QLabel("📁 Photo Organization")
        folder_title.setStyleSheet("font-size: 18px; font-weight: 600; color: #F8FAFC;")
        folder_layout.addWidget(folder_title)

        folder_subtitle = QLabel("Select a folder to organize photos by quality")
        folder_subtitle.setProperty("class", "subtitle")
        folder_layout.addWidget(folder_subtitle)

        folder_row = QHBoxLayout()
        self.folder_btn = AnimatedButton("Browse Folder")
        self.folder_btn.setProperty("variant", "primary")
        self.folder_btn.setIcon(QIcon.fromTheme("folder-open"))
        self.folder_btn.setIconSize(QSize(20, 20))
        self.folder_btn.clicked.connect(self.select_folder)
        folder_row.addWidget(self.folder_btn)

        self.folder_label = QLabel("No folder selected")
        self.folder_label.setProperty("class", "subtitle")
        self.folder_label.setWordWrap(True)
        folder_row.addWidget(self.folder_label, 1)

        folder_layout.addLayout(folder_row)
        content_layout.addWidget(folder_card)

        settings_card = GlowCard()
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setSpacing(15)

        settings_title = QLabel("⚙️ Detection Settings")
        settings_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #F8FAFC;")
        settings_layout.addWidget(settings_title)

        blur_group = QWidget()
        blur_layout = QHBoxLayout(blur_group)
        blur_layout.setContentsMargins(0, 0, 0, 0)

        blur_label = QLabel("Blur Detection:")
        blur_label.setProperty("class", "subtitle")
        blur_layout.addWidget(blur_label)

        threshold_container = QWidget()
        threshold_layout = QHBoxLayout(threshold_container)
        threshold_layout.setSpacing(8)

        self.blur_buttons: List[QPushButton] = []
        for preset_name, preset_value in AppConfig.BLUR_PRESETS.items():
            btn = create_threshold_button(preset_name, preset_value)
            btn.clicked.connect(lambda checked, v=preset_value: self.set_blur_threshold(v))
            threshold_layout.addWidget(btn)
            self.blur_buttons.append(btn)

        if len(self.blur_buttons) > 1:
            self.blur_buttons[1].setChecked(True)

        threshold_layout.addStretch()
        blur_layout.addWidget(threshold_container, 1)
        settings_layout.addWidget(blur_group)

        sim_group = QWidget()
        sim_layout = QHBoxLayout(sim_group)
        sim_layout.setContentsMargins(0, 0, 0, 0)

        sim_label = QLabel("Duplicate Sensitivity:")
        sim_label.setProperty("class", "subtitle")
        sim_layout.addWidget(sim_label)

        sim_container = QWidget()
        sim_buttons_layout = QHBoxLayout(sim_container)
        sim_buttons_layout.setSpacing(8)

        self.sim_buttons: List[QPushButton] = []
        for preset_name, preset_value in AppConfig.SIMILARITY_PRESETS.items():
            btn = create_threshold_button(preset_name, preset_value)
            btn.clicked.connect(lambda checked, v=preset_value: self.set_similarity_threshold(v))
            sim_buttons_layout.addWidget(btn)
            self.sim_buttons.append(btn)

        if len(self.sim_buttons) > 1:
            self.sim_buttons[1].setChecked(True)

        sim_buttons_layout.addStretch()
        sim_layout.addWidget(sim_container, 1)
        settings_layout.addWidget(sim_group)

        content_layout.addWidget(settings_card)

        progress_card = GlowCard()
        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setSpacing(15)

        progress_title = QLabel("📊 Processing Progress")
        progress_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #F8FAFC;")
        progress_layout.addWidget(progress_title)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)

        progress_info = QHBoxLayout()
        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet("font-weight: 600; color: #06B6D4;")
        progress_info.addWidget(self.percentage_label)

        progress_info.addStretch()

        self.status_label = QLabel("Ready to process")
        self.status_label.setProperty("class", "subtitle")
        progress_info.addWidget(self.status_label)

        progress_layout.addLayout(progress_info)
        content_layout.addWidget(progress_card)

        action_card = GlowCard()
        action_layout = QHBoxLayout(action_card)

        self.process_btn = AnimatedButton("🚀 Start Processing")
        self.process_btn.setProperty("variant", "success")
        self.process_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.process_btn.setIconSize(QSize(20, 20))
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setEnabled(False)
        action_layout.addWidget(self.process_btn)

        control_container = QWidget()
        control_layout = QHBoxLayout(control_container)
        control_layout.setSpacing(8)

        self.pause_btn = AnimatedButton("⏸")
        self.pause_btn.setProperty("variant", "icon")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.toggle_pause_processing)
        control_layout.addWidget(self.pause_btn)

        self.stop_btn = AnimatedButton("⏹")
        self.stop_btn.setProperty("variant", "icon")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_processing)
        control_layout.addWidget(self.stop_btn)

        action_layout.addWidget(control_container)
        action_layout.addStretch()
        content_layout.addWidget(action_card)

        self.results_card = GlowCard()
        self.results_card.setVisible(False)
        results_layout = QVBoxLayout(self.results_card)
        results_layout.setSpacing(15)

        results_title = QLabel("✅ Processing Results")
        results_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #10B981;")
        results_layout.addWidget(results_title)

        self.results_label = QLabel("")
        self.results_label.setProperty("class", "subtitle")
        self.results_label.setWordWrap(True)
        results_layout.addWidget(self.results_label)

        content_layout.addWidget(self.results_card)
        content_layout.addStretch()

        scroll.setWidget(content)
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(scroll)
        self.tabs.addTab(tab, "📁 Organizer")

    def setup_face_search_tab(self) -> None:
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        status_card = GlowCard()
        status_layout = QVBoxLayout(status_card)
        status_layout.setSpacing(10)

        status_icon = "✅" if DEEPFACE_AVAILABLE else "⚠️"
        status_color = AppConfig.THEME["SUCCESS"] if DEEPFACE_AVAILABLE else AppConfig.THEME["WARNING"]

        status_label = QLabel(f"{status_icon} Face Recognition Status")
        status_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {status_color};")
        status_layout.addWidget(status_label)

        status_text = (
            "DeepFace is ready for person-specific matching"
            if DEEPFACE_AVAILABLE
            else "DeepFace unavailable — install 'deepface' and 'tf-keras'"
        )
        status_subtitle = QLabel(status_text)
        status_subtitle.setProperty("class", "subtitle")
        status_layout.addWidget(status_subtitle)

        content_layout.addWidget(status_card)

        ref_card = GlowCard()
        ref_layout = QVBoxLayout(ref_card)
        ref_layout.setSpacing(15)

        ref_title = QLabel("👤 Reference Face")
        ref_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #F8FAFC;")
        ref_layout.addWidget(ref_title)

        ref_row = QHBoxLayout()
        self.ref_face_btn = AnimatedButton("Choose Face")
        self.ref_face_btn.setProperty("variant", "primary")
        self.ref_face_btn.setIcon(QIcon.fromTheme("image-x-generic"))
        self.ref_face_btn.clicked.connect(self.select_reference_face)
        ref_row.addWidget(self.ref_face_btn)

        self.ref_face_label = QLabel("No reference selected")
        self.ref_face_label.setProperty("class", "subtitle")
        self.ref_face_label.setWordWrap(True)
        ref_row.addWidget(self.ref_face_label, 1)

        ref_layout.addLayout(ref_row)
        content_layout.addWidget(ref_card)

        search_card = GlowCard()
        search_layout = QVBoxLayout(search_card)
        search_layout.setSpacing(15)

        search_title = QLabel("🔍 Search Folder")
        search_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #F8FAFC;")
        search_layout.addWidget(search_title)

        search_row = QHBoxLayout()
        self.search_folder_btn = AnimatedButton("Choose Folder")
        self.search_folder_btn.setProperty("variant", "secondary")
        self.search_folder_btn.setIcon(QIcon.fromTheme("folder"))
        self.search_folder_btn.clicked.connect(self.select_search_folder)
        search_row.addWidget(self.search_folder_btn)

        self.search_folder_label = QLabel("No folder selected")
        self.search_folder_label.setProperty("class", "subtitle")
        self.search_folder_label.setWordWrap(True)
        search_row.addWidget(self.search_folder_label, 1)

        search_layout.addLayout(search_row)
        content_layout.addWidget(search_card)

        sim_card = GlowCard()
        sim_layout = QVBoxLayout(sim_card)
        sim_layout.setSpacing(15)

        sim_title = QLabel("🎯 Match Sensitivity")
        sim_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #F8FAFC;")
        sim_layout.addWidget(sim_title)

        slider_container = QWidget()
        slider_layout = QHBoxLayout(slider_container)

        slider_label = QLabel("Similarity Threshold:")
        slider_label.setProperty("class", "subtitle")
        slider_layout.addWidget(slider_label)

        self.similarity_slider = QSlider(Qt.Horizontal)
        self.similarity_slider.setRange(50, 100)
        self.similarity_slider.setValue(int(AppConfig.DEFAULTS["FACE_MATCH_THRESHOLD"] * 100))
        self.similarity_slider.setTickPosition(QSlider.TicksBelow)
        self.similarity_slider.setTickInterval(5)
        slider_layout.addWidget(self.similarity_slider, 1)

        self.similarity_value = QLabel(f"{AppConfig.DEFAULTS['FACE_MATCH_THRESHOLD']:.2f}")
        self.similarity_value.setStyleSheet("font-weight: 600; min-width: 40px;")
        slider_layout.addWidget(self.similarity_value)

        sim_layout.addWidget(slider_container)

        labels_container = QWidget()
        labels_layout = QHBoxLayout(labels_container)
        labels_layout.setContentsMargins(0, 5, 0, 0)

        labels_layout.addWidget(QLabel("Loose"))
        labels_layout.addStretch()
        labels_layout.addWidget(QLabel("Normal"))
        labels_layout.addStretch()
        labels_layout.addWidget(QLabel("Strict"))

        sim_layout.addWidget(labels_container)
        content_layout.addWidget(sim_card)

        action_card = GlowCard()
        action_layout = QHBoxLayout(action_card)

        self.start_search_btn = AnimatedButton("🔍 Start Face Search")
        self.start_search_btn.setProperty("variant", "primary")
        self.start_search_btn.setEnabled(DEEPFACE_AVAILABLE)
        self.start_search_btn.clicked.connect(self.start_face_search)
        action_layout.addWidget(self.start_search_btn)

        control_container = QWidget()
        control_layout = QHBoxLayout(control_container)
        control_layout.setSpacing(8)

        self.face_pause_btn = AnimatedButton("⏸")
        self.face_pause_btn.setProperty("variant", "icon")
        self.face_pause_btn.setEnabled(False)
        self.face_pause_btn.clicked.connect(self.toggle_pause_face_search)
        control_layout.addWidget(self.face_pause_btn)

        self.face_stop_btn = AnimatedButton("⏹")
        self.face_stop_btn.setProperty("variant", "icon")
        self.face_stop_btn.setEnabled(False)
        self.face_stop_btn.clicked.connect(self.stop_face_search)
        control_layout.addWidget(self.face_stop_btn)

        troubleshoot_btn = AnimatedButton("🔧 Troubleshoot")
        troubleshoot_btn.setProperty("variant", "ghost")
        troubleshoot_btn.clicked.connect(self.troubleshoot_selected_image)
        control_layout.addWidget(troubleshoot_btn)

        action_layout.addWidget(control_container)
        action_layout.addStretch()

        self.face_search_progress = QProgressBar()
        self.face_search_progress.setFixedWidth(200)
        action_layout.addWidget(self.face_search_progress)

        content_layout.addWidget(action_card)

        self.face_results_card = GlowCard()
        self.face_results_card.setVisible(False)
        results_layout = QVBoxLayout(self.face_results_card)
        results_layout.setSpacing(15)

        results_title = QLabel("📊 Search Results")
        results_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #F8FAFC;")
        results_layout.addWidget(results_title)

        self.matched_list = QListWidget()
        self.matched_list.setIconSize(QSize(80, 80))
        self.matched_list.setStyleSheet("""
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #475569;
            }
        """)
        results_layout.addWidget(self.matched_list)

        self.face_results_summary = QLabel("")
        self.face_results_summary.setProperty("class", "subtitle")
        results_layout.addWidget(self.face_results_summary)

        content_layout.addWidget(self.face_results_card)
        content_layout.addStretch()

        self.similarity_slider.valueChanged.connect(
            lambda v: self.similarity_value.setText(f"{v/100:.2f}")
        )

        scroll.setWidget(content)
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(scroll)
        self.tabs.addTab(tab, "👤 Face Search")

    def troubleshoot_selected_image(self):
        if not hasattr(self, "search_folder_path") or not self.search_folder_path:
            QMessageBox.warning(self, "Warning", "Please select a search folder first.")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image to Troubleshoot",
            self.search_folder_path,
            "Images (*.jpg *.jpeg *.png *.bmp *.webp *.heic *.tiff *.dng);;All Files (*)"
        )

        if file_path:
            self.troubleshoot_image(file_path)

    def setup_settings_tab(self) -> None:
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        general_card = GlowCard()
        general_layout = QVBoxLayout(general_card)
        general_layout.setSpacing(15)

        general_title = QLabel("⚙️ General Settings")
        general_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #F8FAFC;")
        general_layout.addWidget(general_title)

        theme_row = QHBoxLayout()
        theme_label = QLabel("Theme:")
        theme_label.setProperty("class", "subtitle")
        theme_row.addWidget(theme_label)

        self.theme_toggle = AnimatedButton("Dark")
        self.theme_toggle.setProperty("variant", "threshold")
        self.theme_toggle.setCheckable(True)
        self.theme_toggle.clicked.connect(self.toggle_theme)
        theme_row.addWidget(self.theme_toggle)

        theme_row.addStretch()
        general_layout.addLayout(theme_row)

        content_layout.addWidget(general_card)

        session_card = GlowCard()
        session_layout = QVBoxLayout(session_card)
        session_layout.setSpacing(15)

        session_title = QLabel("💾 Session Management")
        session_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #F8FAFC;")
        session_layout.addWidget(session_title)

        session_buttons = QHBoxLayout()

        clear_btn = AnimatedButton("Clear Session Data")
        clear_btn.setProperty("variant", "ghost")
        clear_btn.clicked.connect(self.clear_session_data)
        session_buttons.addWidget(clear_btn)

        export_btn = AnimatedButton("Export Settings")
        export_btn.setProperty("variant", "ghost")
        export_btn.clicked.connect(self.export_settings)
        session_buttons.addWidget(export_btn)

        session_buttons.addStretch()
        session_layout.addLayout(session_buttons)

        content_layout.addWidget(session_card)
        content_layout.addStretch()

        scroll.setWidget(content)
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(scroll)
        self.tabs.addTab(tab, "⚙️ Settings")

    def setup_log_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)

        log_title = QLabel("📝 Activity Log")
        log_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #F8FAFC;")
        header_layout.addWidget(log_title)
        header_layout.addStretch()

        clear_btn = AnimatedButton("Clear Log")
        clear_btn.setProperty("variant", "ghost")
        clear_btn.clicked.connect(self.clear_log)
        header_layout.addWidget(clear_btn)

        export_btn = AnimatedButton("Export Log")
        export_btn.setProperty("variant", "ghost")
        export_btn.clicked.connect(self.export_log)
        header_layout.addWidget(export_btn)

        layout.addWidget(header)

        log_card = GlowCard()
        log_card_layout = QVBoxLayout(log_card)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: #1E293B;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 15px;
                color: #CBD5E1;
                font-family: 'JetBrains Mono', monospace;
                font-size: 12px;
                line-height: 1.5;
            }
        """)
        log_card_layout.addWidget(self.log_text)

        layout.addWidget(log_card)
        self.tabs.addTab(tab, "📝 Log")

    def show_about(self) -> None:
        about_dialog = QMessageBox(self)
        about_dialog.setWindowTitle("About Clean Shot")
        about_dialog.setText("""
            <h2 style="color: #7C3AED; margin-bottom: 10px;">CLEAN SHOT</h2>
            <p style="color: #94A3B8; margin-bottom: 15px;">
                <strong>AI Photo Organizer & Face Search</strong><br>
                Version 2.0 • Modern Dark Theme
            </p>
            <div style="background: #1E293B; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <p style="color: #CBD5E1; margin: 5px 0;">
                    ✨ <strong>Features:</strong><br>
                    • Smart photo organization<br>
                    • AI-powered face recognition<br>
                    • Modern dark/light themes<br>
                    • Real-time progress tracking<br>
                    • Session management
                </p>
            </div>
            <p style="color: #64748B; font-size: 12px; margin-top: 15px;">
                Made with ❤️ using PySide6 & TensorFlow
            </p>
        """)
        about_dialog.setStandardButtons(QMessageBox.Ok)
        about_dialog.setStyleSheet("""
            QMessageBox {
                background: #0F172A;
                color: #F8FAFC;
            }
            QLabel {
                color: #F8FAFC;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7C3AED, stop:1 #06B6D4);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #A78BFA, stop:1 #67E8F9);
            }
        """)
        about_dialog.exec()

    def toggle_theme(self) -> None:
        current_theme = "light" if self.theme_toggle.isChecked() else "dark"
        self.setStyleSheet(ThemeManager.get_theme_css(current_theme))
        self.theme_toggle.setText("Light" if current_theme == "light" else "Dark")

        if current_theme == "light":
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor("#F8FAFC"))
            palette.setColor(QPalette.WindowText, QColor("#0F172A"))
            self.setPalette(palette)
        else:
            self.setup_palette()

    def set_blur_threshold(self, value: int) -> None:
        for btn in self.blur_buttons:
            btn.setChecked(btn.value == value)
        self.add_log_message(f"Blur threshold set to: {value}")

    def set_similarity_threshold(self, value: int) -> None:
        for btn in self.sim_buttons:
            btn.setChecked(btn.value == value)
        self.add_log_message(f"Similarity threshold set to: {value}")

    def load_last_session(self) -> None:
        if self.last_session:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Last Session")

            timestamp = self.last_session.get('timestamp', '').split('T')[0]
            folder = Path(self.last_session.get('folder', '')).name

            msg_box.setText(f"""
                <h3 style="color: #7C3AED;">Last Session Found</h3>
                <p style="color: #94A3B8;">
                    <strong>Date:</strong> {timestamp}<br>
                    <strong>Folder:</strong> {folder}
                </p>
            """)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background: #1E293B;
                }
            """)

            msg_box.show()
            self.animate_widget(msg_box)

    def animate_widget(self, widget: QWidget) -> None:
        try:
            opacity_effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(opacity_effect)

            animation = QPropertyAnimation(opacity_effect, b"opacity")
            animation.setDuration(300)
            animation.setStartValue(0)
            animation.setEndValue(1)
            animation.setEasingCurve(QEasingCurve.InOutCubic)
            animation.start()
        except Exception:
            pass

    def clear_session_data(self) -> None:
        reply = QMessageBox.question(
            self,
            "Clear Session Data",
            "Are you sure you want to clear all saved session data?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if os.path.exists(AppConfig.DEFAULTS["SESSION_FILE"]):
                os.remove(AppConfig.DEFAULTS["SESSION_FILE"])
                self.last_session = None

                success_msg = QMessageBox(self)
                success_msg.setIcon(QMessageBox.Information)
                success_msg.setText("Session data cleared successfully!")
                success_msg.setStandardButtons(QMessageBox.Ok)
                success_msg.exec()

    def export_settings(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Settings",
            "clean_shot_settings.json",
            "JSON Files (*.json)"
        )

        if file_path:
            settings = {
                "face_match_threshold": self.similarity_slider.value() / 100
                if hasattr(self, 'similarity_slider') else 0.85,
                "export_date": datetime.now().isoformat()
            }

            try:
                with open(file_path, 'w') as f:
                    json.dump(settings, f, indent=2)
                self.add_log_message(f"Settings exported to: {file_path}")

                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Settings exported successfully to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export settings: {str(e)}"
                )

    def export_log(self) -> None:
        if not self.log_text:
            QMessageBox.warning(self, "Warning", "Log is empty!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Log",
            "clean_shot_log.txt",
            "Text Files (*.txt)"
        )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.log_text.toPlainText())
                self.add_log_message(f"Log exported to: {file_path}")

                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Log exported successfully to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export log: {str(e)}"
                )

    def clear_log(self) -> None:
        if self.log_text:
            self.log_text.clear()
            self.add_log_message("Log cleared")

    def add_log_message(self, message: str) -> None:
        if not self.log_text:
            return

        ts = QTime.currentTime().toString("hh:mm:ss")
        formatted_message = f"[{ts}] {message}"

        upper = message.upper()
        if "ERROR" in upper or "FAILED" in upper:
            formatted_message = f'<span style="color: #EF4444;">{formatted_message}</span>'
        elif "SUCCESS" in upper or "COMPLETE" in upper:
            formatted_message = f'<span style="color: #10B981;">{formatted_message}</span>'
        elif "WARNING" in upper or "CAUTION" in upper:
            formatted_message = f'<span style="color: #F59E0B;">{formatted_message}</span>'
        elif "MATCH" in upper:
            formatted_message = f'<span style="color: #06B6D4;">{formatted_message}</span>'

        self.log_text.append(formatted_message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def select_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Photo Folder")
        if not folder:
            return

        self.current_folder = folder
        folder_name = Path(folder).name

        self.folder_label.setText(folder_name)
        self.folder_label.setToolTip(folder)

        images = [
            f for f in Path(folder).iterdir()
            if f.suffix.lower() in AppConfig.IMAGE_EXTENSIONS
        ]

        self.add_log_message(f"📁 Selected folder: {folder} ({len(images)} images)")

        self.status_label.setText(f"Ready to process {len(images)} images")
        self.animate_widget(self.status_label)

        self.process_btn.setEnabled(len(images) > 0)
        self.process_btn.setIcon(QIcon.fromTheme("folder"))

    def start_processing(self) -> None:
        if not hasattr(self, "current_folder"):
            QMessageBox.warning(self, "Warning", "Please select a folder first.")
            return

        self.process_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)

        self.progress_bar.setValue(0)
        self.percentage_label.setText("0%")

        self.results_card.setVisible(False)

        self.add_log_message("🚀 Starting photo processing...")

        blur_threshold = AppConfig.DEFAULTS["BLUR_THRESHOLD"]
        similarity_threshold = AppConfig.DEFAULTS["SIMILARITY_THRESHOLD"]

        for btn in self.blur_buttons:
            if btn.isChecked():
                blur_threshold = btn.value
                break

        for btn in self.sim_buttons:
            if btn.isChecked():
                similarity_threshold = btn.value
                break

        self.processor = PhotoProcessor(
            self.current_folder,
            blur_threshold,
            similarity_threshold
        )

        self.processor.progress_updated.connect(self.update_progress)
        self.processor.status_updated.connect(self.status_label.setText)
        self.processor.finished_processing.connect(self.processing_finished)
        self.processor.log_message.connect(self.add_log_message)

        self.animate_widget(self.progress_bar)
        self.processor.start()

    def toggle_pause_processing(self) -> None:
        if hasattr(self, 'processor'):
            if self.processor._is_paused:
                self.processor.resume()
                self.pause_btn.setText("⏸")
                self.add_log_message("▶ Processing resumed")
            else:
                self.processor.pause()
                self.pause_btn.setText("▶")
                self.add_log_message("⏸ Processing paused")

    def stop_processing(self) -> None:
        if hasattr(self, 'processor'):
            self.processor.stop()
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.process_btn.setEnabled(True)
            self.add_log_message("⏹ Processing stopped by user")

    def update_progress(self, value: int) -> None:
        try:
            animation = QPropertyAnimation(self.progress_bar, b"value")
            animation.setDuration(300)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            animation.setStartValue(self.progress_bar.value())
            animation.setEndValue(value)
            animation.start()
        except Exception:
            self.progress_bar.setValue(value)

        self.percentage_label.setText(f"{value}%")

        if value < 30:
            self.progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #EF4444, stop:1 #F87171);
                }
            """)
        elif value < 70:
            self.progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #F59E0B, stop:1 #FBBF24);
                }
            """)
        else:
            self.progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #10B981, stop:1 #34D399);
                }
            """)

    def processing_finished(self, results: Dict) -> None:
        self.process_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setText("⏸")

        self.progress_bar.setValue(100)
        self.percentage_label.setText("100%")

        self.add_log_message("✅ Processing finished successfully!")

        text = (f"📊 <b>Processing Results:</b><br><br>"
                f"• 📸 <b>Processed:</b> {results['processed']} photos<br>"
                f"• ✅ <b>Good Photos:</b> {results['good']}<br>"
                f"• 🌫️ <b>Blurry Photos:</b> {results['blurry']}<br>"
                f"• 🔄 <b>Duplicates:</b> {results['duplicate']}")

        self.results_label.setText(text)
        self.results_card.setVisible(True)
        self.animate_widget(self.results_card)

        QMessageBox.information(
            self,
            "🎉 Processing Complete",
            (f"Successfully processed {results['processed']} photos!\n\n"
             f"• {results['good']} good photos\n"
             f"• {results['blurry']} blurry photos\n"
             f"• {results['duplicate']} duplicates")
        )

    def select_reference_face(self) -> None:
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Reference Face",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp *.webp *.heic *.tiff *.dng);;All Files (*)"
        )

        if file:
            self.reference_face_path = file
            file_name = Path(file).name

            self.ref_face_label.setText(file_name)
            self.ref_face_label.setToolTip(file)

            self.add_log_message(f"👤 Reference face selected: {file_name}")
            self.animate_widget(self.ref_face_label)

    def select_search_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Search Folder")

        if folder:
            self.search_folder_path = folder
            folder_name = Path(folder).name

            self.search_folder_label.setText(folder_name)
            self.search_folder_label.setToolTip(folder)

            images = [
                f for f in Path(folder).iterdir()
                if f.suffix.lower() in AppConfig.IMAGE_EXTENSIONS
            ]

            self.add_log_message(f"🔍 Search folder selected: {folder} ({len(images)} images)")
            self.animate_widget(self.search_folder_label)

    def start_face_search(self) -> None:
        if not DEEPFACE_AVAILABLE:
            QMessageBox.warning(self, "Unavailable", "DeepFace is not installed. Person-based search is disabled.")
            return

        if not hasattr(self, "reference_face_path") or not hasattr(self, "search_folder_path"):
            QMessageBox.warning(self, "Missing", "Please select reference face and search folder.")
            return

        self.start_search_btn.setEnabled(False)
        self.face_pause_btn.setEnabled(True)
        self.face_stop_btn.setEnabled(True)

        self.face_search_progress.setValue(0)
        self.matched_list.clear()
        self.face_results_card.setVisible(False)

        similarity_threshold = self.similarity_slider.value() / 100
        self.add_log_message(f"🔍 Starting face search (threshold: {similarity_threshold:.2f})...")

        self.face_processor = FaceSearchProcessor(
            self.reference_face_path,
            self.search_folder_path,
            similarity_threshold
        )

        self.face_processor.progress_updated.connect(self.face_search_progress.setValue)
        self.face_processor.status_updated.connect(self.update_face_search_status)
        self.face_processor.finished_search.connect(self.face_search_finished)

        # Connect signal directly to slot - Qt handles thread-safe queued connection automatically
        self.face_processor.face_found.connect(self.add_matched_face, Qt.QueuedConnection)

        self.face_processor.log_message.connect(self.add_log_message)

        self.animate_widget(self.face_search_progress)
        self.face_processor.start()

    def update_face_search_status(self, status: str) -> None:
        try:
            self.face_search_progress.setFormat(f"  {status}")
        except Exception:
            pass

    def toggle_pause_face_search(self) -> None:
        if hasattr(self, 'face_processor'):
            if self.face_processor._is_paused:
                self.face_processor.resume()
                self.face_pause_btn.setText("⏸")
                self.add_log_message("▶ Face search resumed")
            else:
                self.face_processor.pause()
                self.face_pause_btn.setText("▶")
                self.add_log_message("⏸ Face search paused")

    def stop_face_search(self) -> None:
        if hasattr(self, 'face_processor'):
            self.face_processor.stop()
            self.face_pause_btn.setEnabled(False)
            self.face_stop_btn.setEnabled(False)
            self.start_search_btn.setEnabled(True)
            self.add_log_message("⏹ Face search stopped by user")

    def add_matched_face(self, filename: str, similarity: float) -> None:
        """Add a matched face to the results list with its thumbnail."""
        if hasattr(self, "search_folder_path"):
            search_path = Path(self.search_folder_path)
        else:
            search_path = Path()

        image_path = search_path / filename
        
        # Log the match
        self.add_log_message(f"Adding matched face: {filename} ({similarity:.2%}) from {image_path}")

        item = QListWidgetItem()
        item.setText(f"{filename} — {similarity:.2%}")
        
        # Store the full path for later reference
        item.setData(Qt.UserRole + 1, str(image_path))

        # Create thumbnail directly in main thread
        thumbnail = self._create_thumbnail_safe(image_path)
        if thumbnail and not thumbnail.isNull():
            item.setIcon(QIcon(thumbnail))
            self.add_log_message(f"Thumbnail created for: {filename}")
        else:
            self.add_log_message(f"Failed to create thumbnail for: {filename}")

        if similarity >= 0.90:
            item.setForeground(QColor(AppConfig.THEME["SUCCESS"]))
            item.setData(Qt.UserRole, "high")
        elif similarity >= 0.80:
            item.setForeground(QColor(AppConfig.THEME["WARNING"]))
            item.setData(Qt.UserRole, "medium")
        else:
            item.setForeground(QColor(AppConfig.THEME["DANGER"]))
            item.setData(Qt.UserRole, "low")

        self.matched_list.addItem(item)
        self.matched_list.scrollToItem(item)

        if not self.face_results_card.isVisible():
            self.face_results_card.setVisible(True)
            self.animate_widget(self.face_results_card)
    
    def _create_thumbnail_safe(self, image_path: Path) -> Optional[QPixmap]:
        """Create thumbnail safely in the main GUI thread."""
        try:
            if not image_path.exists():
                self.add_log_message(f"Image not found: {image_path}")
                return None
            
            # Method 1: Try Qt native loading first (fastest for common formats)
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                thumb_size = AppConfig.DEFAULTS["THUMBNAIL_SIZE"]
                return pixmap.scaled(thumb_size, thumb_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Method 2: Use PIL for formats Qt doesn't support
            with open(str(image_path), 'rb') as f:
                raw = f.read()
            
            pil_img = Image.open(io.BytesIO(raw))
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            
            thumb_size = AppConfig.DEFAULTS["THUMBNAIL_SIZE"]
            pil_img.thumbnail((thumb_size, thumb_size), Image.Resampling.LANCZOS)
            
            img_byte_arr = io.BytesIO()
            pil_img.save(img_byte_arr, format='PNG')
            
            pixmap = QPixmap()
            pixmap.loadFromData(img_byte_arr.getvalue())
            return pixmap
            
        except Exception as e:
            self.add_log_message(f"Thumbnail error for {image_path.name}: {e}")
            return None

    def face_search_finished(self, results: Dict) -> None:
        self.start_search_btn.setEnabled(True)
        self.face_pause_btn.setEnabled(False)
        self.face_stop_btn.setEnabled(False)
        self.face_pause_btn.setText("⏸")

        self.face_search_progress.setValue(100)

        summary = (f"🔍 <b>Search Complete:</b><br><br>"
                   f"• 📊 <b>Searched:</b> {results['total_searched']} images<br>"
                   f"• ✅ <b>Matches Found:</b> {results['matched']}<br>"
                   f"• 📁 <b>Output Folder:</b> {Path(results['output_folder']).name}")

        self.face_results_summary.setText(summary)
        self.add_log_message(f"✅ Face search complete! Found {results['matched']} matches.")

        if results['matched'] > 0:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("🎉 Face Search Complete")
            msg.setText(f"Found {results['matched']} matching photos!")
            msg.setInformativeText(f"Saved to:\n{results['output_folder']}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        else:
            QMessageBox.information(
                self,
                "Face Search Complete",
                "No matching faces found in the search folder."
            )

def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Clean Shot")
    app.setApplicationDisplayName("Clean Shot - AI Photo Organizer")
    app.setStyle("Fusion")

    font = QFont("Inter", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    try:
        screen_geometry = app.primaryScreen().availableGeometry()
        window_geometry = window.frameGeometry()
        window.move(
            (screen_geometry.width() - window_geometry.width()) // 2,
            (screen_geometry.height() - window_geometry.height()) // 2
        )
    except Exception:
        pass

    logging.info("Clean Shot started with modern dark theme")
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
