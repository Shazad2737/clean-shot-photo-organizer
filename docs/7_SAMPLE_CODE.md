# 7. Sample Code

## 7.1 Blur Detection Algorithm

```python
class BlurDetector:
    """
    Detects blurry images using multiple metrics:
    1. Laplacian variance (edge detection)
    2. Sobel gradient magnitude
    
    Images are normalized to a standard size for consistent comparison.
    """
    
    def __init__(self, threshold: int = 100, max_dimension: int = 800):
        """
        Initialize blur detector.
        
        Args:
            threshold: Combined blur score threshold below which image is considered blurry
            max_dimension: Maximum dimension to resize images to for consistent comparison
        """
        self.threshold = threshold
        self.max_dimension = max_dimension
    
    def get_blur_score(self, image_path: str) -> Optional[float]:
        """
        Calculate blur score for an image.
        Higher scores indicate sharper images.
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Resize for consistent comparison
            h, w = image.shape[:2]
            if max(h, w) > self.max_dimension:
                scale = self.max_dimension / max(h, w)
                image = cv2.resize(image, None, fx=scale, fy=scale)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance (primary metric)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            laplacian_score = laplacian.var()
            
            # Calculate Sobel gradient magnitude (secondary metric)
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            sobel_score = sobel_magnitude.mean()
            
            # Combine scores (weighted average)
            combined_score = (laplacian_score * 0.7) + (sobel_score * 0.3)
            
            return combined_score
            
        except Exception as e:
            logging.error(f"Error calculating blur score for {image_path}: {e}")
            return None
    
    def is_blurry(self, image_path: str) -> Tuple[bool, Optional[float]]:
        """Check if image is blurry."""
        score = self.get_blur_score(image_path)
        if score is None:
            return False, None
        return score < self.threshold, score
```

## 7.2 Duplicate Detection with Multi-Hash

```python
class DuplicateDetector:
    """
    Detects duplicate images using multiple perceptual hashing algorithms:
    1. Average hash - good for overall similarity
    2. Perceptual hash (pHash) - robust to scaling/compression
    3. Difference hash (dHash) - sensitive to structural changes
    """
    
    def __init__(self, similarity_threshold: int = 5, hash_size: int = 16):
        self.similarity_threshold = similarity_threshold
        self.hash_size = hash_size
        self.seen_hashes: Dict[str, Dict] = {}  # filename -> {ahash, phash, dhash}
    
    def reset(self):
        """Clear all seen hashes. Call this between processing sessions."""
        self.seen_hashes.clear()
    
    def _compute_hashes(self, img: Image.Image) -> Dict:
        """Compute all hash types for an image."""
        return {
            'ahash': imagehash.average_hash(img, hash_size=self.hash_size),
            'phash': imagehash.phash(img, hash_size=self.hash_size),
            'dhash': imagehash.dhash(img, hash_size=self.hash_size)
        }
    
    def _calculate_weighted_diff(self, hashes1: Dict, hashes2: Dict) -> float:
        """
        Calculate weighted difference between two hash sets.
        pHash gets highest weight as it's most robust.
        """
        ahash_diff = hashes1['ahash'] - hashes2['ahash']
        phash_diff = hashes1['phash'] - hashes2['phash']
        dhash_diff = hashes1['dhash'] - hashes2['dhash']
        
        # Weighted combination (pHash is most reliable)
        weighted_diff = (ahash_diff * 0.25) + (phash_diff * 0.50) + (dhash_diff * 0.25)
        return weighted_diff
    
    def is_duplicate(self, image_path: str) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        Check if image is a duplicate of any previously seen image.
        
        Returns:
            Tuple of (is_duplicate, diff_score, original_filename)
        """
        try:
            img = Image.open(image_path)
            current_hashes = self._compute_hashes(img)
            
            min_diff = float('inf')
            match_filename = None
            
            # Compare against all seen images
            for filename, stored_hashes in self.seen_hashes.items():
                diff = self._calculate_weighted_diff(current_hashes, stored_hashes)
                if diff < min_diff:
                    min_diff = diff
                    match_filename = filename
            
            # Store current image's hashes
            basename = os.path.basename(image_path)
            self.seen_hashes[basename] = current_hashes
            
            # Check if duplicate
            if min_diff <= self.similarity_threshold:
                return True, min_diff, match_filename
            
            return False, min_diff if match_filename else None, None
            
        except Exception as e:
            logging.error(f"Error checking duplicate for {image_path}: {e}")
            return False, None, None
```

## 7.3 Face Detection with Haar Cascades

```python
class FaceDetector:
    """Detects faces in images using OpenCV Haar cascades."""
    
    def __init__(self):
        """Initialize face detector with Haar cascade classifier."""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def detect_faces(self, image_path: str) -> int:
        """
        Detect faces in image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Number of faces detected
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return 0
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            return len(faces)
            
        except Exception as e:
            logging.error(f"Error detecting faces in {image_path}: {e}")
            return 0
```

## 7.4 Background Photo Processing

```python
class PhotoProcessor(BaseProcessor):
    """Background thread for photo organization."""
    
    finished_processing = Signal(dict)
    
    def __init__(self, folder_path: str, blur_threshold: int = 100, 
                 similarity_threshold: int = 5):
        super().__init__()
        self.folder_path = folder_path
        
        # Initialize enhanced detectors
        self.blur_detector = BlurDetector(threshold=blur_threshold)
        self.duplicate_detector = DuplicateDetector(
            similarity_threshold=similarity_threshold
        )
    
    def run(self):
        """Main processing loop."""
        results = {
            'total': 0, 'good': 0, 'blurry': 0, 
            'duplicate': 0, 'face': 0, 'errors': []
        }
        
        # Find all image files
        image_files = [
            f for f in os.listdir(self.folder_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'))
        ]
        
        results['total'] = len(image_files)
        
        for i, filename in enumerate(image_files):
            self.check_paused()
            if self._is_stopped:
                break
            
            filepath = os.path.join(self.folder_path, filename)
            
            # Update progress
            progress = int((i + 1) / len(image_files) * 100)
            self.progress_updated.emit(progress)
            self.status_updated.emit(f"Processing: {filename}")
            
            try:
                # Check for blur
                is_blurry, blur_score = self.blur_detector.is_blurry(filepath)
                if is_blurry:
                    self._move_to_category(filepath, 'Blurry_Photos')
                    results['blurry'] += 1
                    continue
                
                # Check for duplicate
                is_dup, diff_score, original = self.duplicate_detector.is_duplicate(filepath)
                if is_dup:
                    self._move_to_category(filepath, 'Duplicate_Photos')
                    results['duplicate'] += 1
                    continue
                
                # Good photo
                results['good'] += 1
                
            except Exception as e:
                results['errors'].append(f"{filename}: {str(e)}")
        
        self.finished_processing.emit(results)
```

## 7.5 Input Validation

```python
class InputValidator:
    """Validates user inputs and file paths."""
    
    SUPPORTED_IMAGE_EXTENSIONS = (
        '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp',
        '.heic', '.heif', '.raw', '.cr2', '.nef', '.arw', '.orf', '.dng'
    )
    
    @staticmethod
    def validate_folder_path(folder_path: str) -> Tuple[bool, str]:
        """Validate folder path exists and has proper permissions."""
        if not folder_path:
            return False, "No folder path provided"
        
        if not os.path.exists(folder_path):
            return False, "Folder does not exist"
        
        if not os.path.isdir(folder_path):
            return False, "Path is not a directory"
        
        if not os.access(folder_path, os.R_OK):
            return False, "No read permission for folder"
        
        if not os.access(folder_path, os.W_OK):
            return False, "No write permission for folder"
        
        return True, ""
    
    @staticmethod
    def validate_thresholds(blur_threshold: int, 
                           similarity_threshold: int) -> Tuple[bool, str]:
        """Validate threshold values are within acceptable ranges."""
        if blur_threshold < 0 or blur_threshold > 1000:
            return False, "Blur threshold must be between 0 and 1000"
        
        if similarity_threshold < 0 or similarity_threshold > 50:
            return False, "Similarity threshold must be between 0 and 50"
        
        return True, ""
```

## 7.6 Theme CSS Generation

```python
def get_theme_css(theme_name: str = "dark") -> str:
    """Generate complete CSS stylesheet for the application theme."""
    theme = DARK_THEME if theme_name == "dark" else LIGHT_THEME
    
    return f"""
    /* Main Window */
    QMainWindow {{
        background-color: {theme['BACKGROUND']};
    }}
    
    /* Buttons */
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                    stop:0 {theme['PRIMARY']}, 
                                    stop:1 {theme['ACCENT']});
        color: {theme['TEXT_PRIMARY']};
        border: none;
        border-radius: {theme['BUTTON_RADIUS']};
        padding: 12px 24px;
        font-weight: 600;
        min-height: {theme['BUTTON_HEIGHT']};
    }}
    
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                    stop:0 {theme['PRIMARY_LIGHT']}, 
                                    stop:1 {theme['ACCENT_LIGHT']});
    }}
    
    /* Cards */
    QFrame {{
        background-color: {theme['SURFACE']};
        border-radius: {theme['CARD_RADIUS']};
        border: 1px solid {theme['BORDER']};
    }}
    
    /* Progress Bar */
    QProgressBar {{
        background-color: {theme['SURFACE']};
        border-radius: 8px;
        text-align: center;
        color: {theme['TEXT_PRIMARY']};
    }}
    
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                    stop:0 {theme['PRIMARY']}, 
                                    stop:1 {theme['ACCENT']});
        border-radius: 8px;
    }}
    """
```
