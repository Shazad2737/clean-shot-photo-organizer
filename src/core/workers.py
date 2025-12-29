# ========== Worker Threads ==========
"""
Background worker threads for photo processing and face search.
Uses enhanced detector classes from core.detectors.
"""

import os
import io
import tempfile
import shutil
import logging
from datetime import datetime
from typing import Optional, Tuple, Dict, List
from pathlib import Path

# Image processing libraries
from PIL import Image, UnidentifiedImageError
import numpy as np
import cv2

# Qt threading
from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition
from PySide6.QtGui import QPixmap

# Local imports
from core.config import IMAGE_EXTENSIONS, DEFAULTS, ProcessingSession
from core.detectors import BlurDetector, DuplicateDetector

# ========== DeepFace availability ==========
DEEPFACE_AVAILABLE = False
DEEPFACE_ERROR = None
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except Exception as e:
    DEEPFACE_AVAILABLE = False
    DEEPFACE_ERROR = str(e)
    logging.warning("DeepFace not available: %s", e)


class BaseProcessor(QThread):
    """Base class for background processing threads with pause/stop support."""
    
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
    """Background thread for face recognition search."""
    
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
        
        Only returns match if:
        1. DeepFace confirms same person (verified=True)
        2. Distance is well below threshold (stricter than default)
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
            detector_backends = ["retinaface", "opencv", "ssd"]  # retinaface first for better accuracy

            for backend in detector_backends:
                try:
                    result = DeepFace.verify(
                        img1_path=tmp1,
                        img2_path=tmp2,
                        model_name="ArcFace",
                        detector_backend=backend,
                        enforce_detection=True,
                        distance_metric="cosine",
                        align=True,
                        silent=True
                    )
                    break
                except Exception as deep_err:
                    error_str = str(deep_err).lower()
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

            # Cleanup temp PNGs
            for p, is_temp in ((tmp1, tmp1_is_temp), (tmp2, tmp2_is_temp)):
                if is_temp:
                    try:
                        if p and Path(p).exists():
                            os.unlink(p)
                    except Exception:
                        pass

            if result is None:
                self.log_message.emit(f"⚠️ No face detected in {Path(img2_path).name} - skipping")
                return False, 0.0

            is_verified = bool(result.get("verified", False))
            distance = float(result.get("distance", 1.0))
            model_threshold = float(result.get("threshold", 0.68))

            # Calculate similarity as (1 - distance)
            # For cosine distance: 0 = identical, 1 = completely different
            similarity = max(0.0, min(1.0, 1.0 - distance))
            
            # User threshold is a similarity value (e.g., 0.85 means 85% similar)
            # Convert to distance: distance must be less than (1 - user_threshold)
            max_distance = 1.0 - self.similarity_threshold
            
            # Log all details for debugging
            self.log_message.emit(
                f"📊 {Path(img2_path).name}: distance={distance:.4f}, "
                f"similarity={similarity:.1%}, model_thresh={model_threshold:.4f}, "
                f"verified={is_verified}"
            )
            
            # Match criteria: verified by model AND distance below our stricter threshold
            is_match = is_verified and (distance < max_distance)
            
            if is_match:
                self.log_message.emit(
                    f"✅ MATCH FOUND: {Path(img2_path).name} | "
                    f"similarity={similarity:.1%}, distance={distance:.4f}"
                )
                return True, similarity
            
            if not is_verified:
                # DeepFace says not the same person
                pass  # Already logged above
            else:
                # DeepFace says same person but below our stricter threshold
                self.log_message.emit(
                    f"⚠️ Weak match rejected: {Path(img2_path).name} "
                    f"(similarity {similarity:.1%} < required {self.similarity_threshold:.0%})"
                )

            return False, similarity

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
                    (DEFAULTS["THUMBNAIL_SIZE"], DEFAULTS["THUMBNAIL_SIZE"]),
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
                scale = DEFAULTS["THUMBNAIL_SIZE"] / float(max_side)
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
        """Pre-process and validate image before face detection."""
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
                if f.suffix.lower() in IMAGE_EXTENSIONS
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

                if self._is_stopped:
                    self.log_message.emit("Processing stopped by user")
                    break

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
    """
    Background thread for photo organization (blur/duplicate detection).
    Uses enhanced detector classes from core.detectors.
    """
    
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
        self.session_manager = ProcessingSession()
        
        # Initialize enhanced detectors
        self.blur_detector = BlurDetector(threshold=blur_threshold)
        self.duplicate_detector = DuplicateDetector(similarity_threshold=similarity_threshold)

    def run(self) -> None:
        try:
            # Reset duplicate detector for fresh session
            self.duplicate_detector.reset()
            
            categories = ["Good_Photos", "Blurry_Photos", "Duplicate_Photos"]
            for category in categories:
                category_path = self.folder_path / category
                category_path.mkdir(parents=True, exist_ok=True)

            files = [
                f for f in self.folder_path.iterdir()
                if f.suffix.lower() in IMAGE_EXTENSIONS
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

                # Check for duplicates using enhanced detector
                is_dup, diff_score, original_name = self.duplicate_detector.is_duplicate(str(image_path))
                if is_dup:
                    target = "Duplicate_Photos"
                    results["duplicate"] += 1
                    self.log_message.emit(
                        f"Duplicate: {image_path.name} matches {original_name} (diff: {diff_score:.1f})"
                    )
                else:
                    # Check for blur using enhanced detector
                    is_blur, blur_score = self.blur_detector.is_blurry(str(image_path))
                    if is_blur:
                        target = "Blurry_Photos"
                        results["blurry"] += 1
                        self.log_message.emit(
                            f"Blurry: {image_path.name} (score: {blur_score:.1f}, threshold: {self.blur_threshold})"
                        )
                    else:
                        target = "Good_Photos"
                        results["good"] += 1
                        self.log_message.emit(f"Good: {image_path.name}")

                try:
                    dest = self.folder_path / target / image_path.name
                    shutil.copy2(str(image_path), str(dest))
                except Exception as e:
                    self.log_message.emit(f"Copy failed for {image_path.name}: {e}")

            settings = {
                "blur_threshold": self.blur_threshold,
                "similarity_threshold": self.similarity_threshold
            }
            self.session_manager.save(results, str(self.folder_path), settings)

            self.finished_processing.emit(results)

        except Exception as e:
            self.log_message.emit(f"Processing error: {e}")
            self.status_updated.emit(f"Error: {e}")
