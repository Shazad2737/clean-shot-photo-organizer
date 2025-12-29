# 9. Testing

## 9.1 Testing Strategy

CLEAN SHOT employs a comprehensive testing strategy covering unit tests, integration tests, and manual validation.

```
┌─────────────────────────────────────────────────────────────────┐
│                      TESTING PYRAMID                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                        /\                                        │
│                       /  \                                       │
│                      /    \      Manual/UI Testing               │
│                     /      \     (Exploratory)                   │
│                    /────────\                                    │
│                   /          \                                   │
│                  /            \   Integration Tests              │
│                 /              \  (Component interaction)        │
│                /────────────────\                                │
│               /                  \                               │
│              /                    \  Unit Tests                  │
│             /                      \ (Individual functions)      │
│            /________________________\                            │
│                                                                  │
│            ████████████████████████████  ~70% Unit Tests         │
│            ████████████████              ~20% Integration        │
│            ████████                      ~10% Manual             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 9.2 Unit Test Coverage

### 9.2.1 Test Files

| Test File | Module Tested | Test Count |
|-----------|---------------|------------|
| `test_detectors.py` | `core/detectors.py` | 15+ tests |
| `test_validators.py` | `utils/validators.py` | 12+ tests |
| `test_enhanced_processor.py` | `core/enhanced_processor.py` | 10+ tests |

### 9.2.2 Detector Tests (`test_detectors.py`)

```python
class TestBlurDetector:
    """Unit tests for blur detection."""
    
    def test_init_default_threshold(self):
        """Test default threshold initialization."""
        detector = BlurDetector()
        assert detector.threshold == 100
    
    def test_init_custom_threshold(self):
        """Test custom threshold initialization."""
        detector = BlurDetector(threshold=50)
        assert detector.threshold == 50
    
    def test_sharp_image_detection(self):
        """Test that sharp images are not detected as blurry."""
        detector = BlurDetector(threshold=100)
        is_blurry, score = detector.is_blurry("test_photos/sharp.jpg")
        assert is_blurry == False
        assert score > 100
    
    def test_blurry_image_detection(self):
        """Test that blurry images are detected correctly."""
        detector = BlurDetector(threshold=100)
        is_blurry, score = detector.is_blurry("test_photos/blurry.jpg")
        assert is_blurry == True
        assert score < 100


class TestDuplicateDetector:
    """Unit tests for duplicate detection."""
    
    def test_init_and_reset(self):
        """Test initialization and reset functionality."""
        detector = DuplicateDetector()
        assert detector.seen_count == 0
        
        detector.is_duplicate("test_photos/image1.jpg")
        assert detector.seen_count == 1
        
        detector.reset()
        assert detector.seen_count == 0
    
    def test_identical_images_detected(self):
        """Test that identical images are detected as duplicates."""
        detector = DuplicateDetector(similarity_threshold=5)
        
        # First image is never duplicate
        is_dup1, _, _ = detector.is_duplicate("test_photos/image1.jpg")
        assert is_dup1 == False
        
        # Identical image should be duplicate
        is_dup2, diff, original = detector.is_duplicate("test_photos/image1_copy.jpg")
        assert is_dup2 == True
        assert diff < 5


class TestFaceDetector:
    """Unit tests for face detection."""
    
    def test_face_detection_with_faces(self):
        """Test detection on image with faces."""
        detector = FaceDetector()
        face_count = detector.detect_faces("test_photos/portrait.jpg")
        assert face_count >= 1
    
    def test_face_detection_without_faces(self):
        """Test detection on image without faces."""
        detector = FaceDetector()
        face_count = detector.detect_faces("test_photos/landscape.jpg")
        assert face_count == 0
```

### 9.2.3 Validator Tests (`test_validators.py`)

```python
class TestInputValidator:
    """Unit tests for input validation."""
    
    def test_valid_folder_path(self):
        """Test validation of existing folder."""
        is_valid, error = InputValidator.validate_folder_path("tests/test_photos")
        assert is_valid == True
        assert error == ""
    
    def test_invalid_folder_path(self):
        """Test validation of non-existent folder."""
        is_valid, error = InputValidator.validate_folder_path("/nonexistent/path")
        assert is_valid == False
        assert "does not exist" in error
    
    def test_empty_folder_path(self):
        """Test validation of empty path."""
        is_valid, error = InputValidator.validate_folder_path("")
        assert is_valid == False
        assert "No folder path" in error
    
    def test_valid_thresholds(self):
        """Test valid threshold values."""
        is_valid, error = InputValidator.validate_thresholds(100, 20)
        assert is_valid == True
    
    def test_invalid_blur_threshold(self):
        """Test invalid blur threshold."""
        is_valid, error = InputValidator.validate_thresholds(1500, 20)
        assert is_valid == False
        assert "Blur threshold" in error
    
    def test_invalid_similarity_threshold(self):
        """Test invalid similarity threshold."""
        is_valid, error = InputValidator.validate_thresholds(100, 75)
        assert is_valid == False
        assert "Similarity threshold" in error
```

## 9.3 Running Tests

### Command Line

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_detectors.py

# Run with verbose output
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=src/ --cov-report=html

# Run specific test class
python -m pytest tests/test_detectors.py::TestBlurDetector

# Run specific test method
python -m pytest tests/test_detectors.py::TestBlurDetector::test_sharp_image_detection
```

### Using Test Runner Script

```bash
python run_tests.py
```

## 9.4 Test Results

### Sample Test Output

```
============================= test session starts ==============================
platform win32 -- Python 3.11.5, pytest-7.4.0, pluggy-1.3.0
rootdir: D:\project\clean-shot-photo-organizer
plugins: cov-4.1.0
collected 37 items

tests/test_detectors.py ................                                [43%]
tests/test_validators.py ............                                   [76%]
tests/test_enhanced_processor.py ..........                             [100%]

============================= 37 passed in 4.52s ===============================
```

### Coverage Report

| Module | Statements | Missing | Coverage |
|--------|------------|---------|----------|
| `core/detectors.py` | 180 | 12 | 93% |
| `utils/validators.py` | 65 | 3 | 95% |
| `core/enhanced_processor.py` | 210 | 25 | 88% |
| **Total** | **455** | **40** | **91%** |

## 9.5 Manual Testing Checklist

### Functional Testing

- [ ] Application launches without errors
- [ ] Folder selection dialog works correctly
- [ ] Blur threshold slider updates value
- [ ] Similarity threshold slider updates value
- [ ] Face detection toggle works
- [ ] Start Processing button initiates processing
- [ ] Progress bar updates during processing
- [ ] Status messages display correctly
- [ ] Results display after completion
- [ ] Undo button reverses last operation
- [ ] Face Search modal opens and functions

### Edge Case Testing

- [ ] Empty folder handling
- [ ] Folder with no images
- [ ] Very large images (>50MB)
- [ ] Corrupted image files
- [ ] Read-only folders
- [ ] Unicode filenames
- [ ] Network paths (if applicable)

### Performance Testing

- [ ] 100 photos: < 1 minute
- [ ] 500 photos: < 5 minutes
- [ ] 1000 photos: < 10 minutes
- [ ] Memory usage stays under 2GB

## 9.6 Known Test Limitations

1. **Test Photos Required**: Unit tests require test images in `tests/test_photos/`
2. **DeepFace Tests**: Face recognition tests skipped if DeepFace not installed
3. **Platform-Specific**: Some path tests may behave differently on Linux/macOS
