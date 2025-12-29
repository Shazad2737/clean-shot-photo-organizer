# 6. Implementation

## 6.1 Project Structure

```
clean-shot-photo-organizer/
├── src/
│   ├── main.py                    # Application entry point (1916 lines)
│   ├── core/                       # Core detection algorithms
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── detectors.py           # Blur, Duplicate, Face detection
│   │   ├── enhanced_processor.py  # Enhanced processing features
│   │   ├── photo_processor.py     # Photo processing logic
│   │   └── workers.py             # Background processing threads
│   ├── gui/                        # User interface components
│   │   ├── __init__.py
│   │   ├── beautiful_components.py # Enhanced UI components
│   │   ├── components.py          # Core UI widgets
│   │   ├── modern_styles.py       # Modern CSS styles
│   │   ├── styles.py              # Base styles
│   │   └── theme.py               # Theme management & animations
│   └── utils/                      # Utility modules
│       ├── __init__.py
│       └── validators.py          # Input validation
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── test_detectors.py          # Detector unit tests
│   ├── test_enhanced_processor.py # Processor tests
│   ├── test_validators.py         # Validator tests
│   └── test_photos/               # Test image fixtures
├── docs/                           # Project documentation
├── assets/                         # Application assets
├── requirements.txt               # Python dependencies
├── README.md                      # Project readme
└── LICENSE                        # MIT License
```

## 6.2 Core Module Implementation

### 6.2.1 BlurDetector (`src/core/detectors.py`)

The blur detector implements a multi-metric approach for robust blur detection:

**Key Features:**
- Image normalization to max 800px dimension
- Combined Laplacian (70%) and Sobel (30%) scoring
- Configurable threshold with sensible defaults

**Implementation Details:**

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `__init__(threshold, max_dimension)` | Initialize with detection parameters | None |
| `get_blur_score(image_path)` | Calculate blur score for image | `float` or `None` |
| `is_blurry(image_path)` | Check if image is blurry | `Tuple[bool, float]` |

### 6.2.2 DuplicateDetector (`src/core/detectors.py`)

Multi-hash perceptual comparison for accurate duplicate detection:

**Key Features:**
- Three hash types: Average, Perceptual, Difference
- Weighted comparison with pHash emphasis
- Reset functionality between sessions
- Hash storage for seen images

**Implementation Details:**

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `__init__(similarity_threshold, hash_size)` | Initialize detector | None |
| `reset()` | Clear seen hashes for new session | None |
| `_compute_hashes(img)` | Compute all hash types | `Dict` |
| `_calculate_weighted_diff(hashes1, hashes2)` | Weighted hash comparison | `float` |
| `is_duplicate(image_path)` | Check for duplicate | `Tuple[bool, float, str]` |
| `seen_count` | Property: number of seen images | `int` |

### 6.2.3 FaceDetector (`src/core/detectors.py`)

OpenCV Haar cascade-based face detection:

**Key Features:**
- Pre-trained Haar cascade classifier
- Grayscale conversion for detection
- Configurable detection parameters

**Implementation Details:**

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `__init__()` | Load Haar cascade classifier | None |
| `detect_faces(image_path)` | Count faces in image | `int` |

## 6.3 Worker Thread Implementation

### 6.3.1 BaseProcessor (`src/core/workers.py`)

Base class providing pause/resume/stop functionality:

**Signals:**
- `progress_updated(int)` - Progress percentage
- `status_updated(str)` - Status message
- `log_message(str)` - Log output

**Methods:**
- `pause()` - Pause processing
- `resume()` - Resume processing
- `stop()` - Stop processing
- `check_paused()` - Wait while paused

### 6.3.2 PhotoProcessor (`src/core/workers.py`)

Main processing thread for photo organization:

**Processing Flow:**
1. Scan folder for image files
2. For each image:
   - Check if blurry → Move to `Blurry_Photos/`
   - Check if duplicate → Move to `Duplicate_Photos/`
   - Check for faces → Copy to `Face_Photos/`
3. Log all operations
4. Emit completion signal with results

**Signals:**
- `finished_processing(dict)` - Results dictionary

### 6.3.3 FaceSearchProcessor (`src/core/workers.py`)

Face recognition search using DeepFace:

**Processing Flow:**
1. Load reference face image
2. Scan search folder for images
3. For each image with faces:
   - Verify against reference using DeepFace
   - Calculate similarity score
4. Emit matches as found

**Signals:**
- `finished_search(dict)` - Search results
- `face_found(str, float)` - Individual match found

## 6.4 GUI Implementation

### 6.4.1 ThemeManager (`src/gui/theme.py`)

Centralized theme management with dark/light theme support:

**Themes Available:**
- `DARK_THEME` - Default dark mode
- `LIGHT_THEME` - Light mode option

**CSS Generation:**
- Complete Qt stylesheet generation
- Component-specific styling
- Animation duration constants

### 6.4.2 Animated Widgets

**AnimatedButton:**
- Scale animation on hover (1.05x)
- Smooth easing with OutBack curve
- Pointing hand cursor

**GlowCard:**
- Drop shadow effect
- Blur radius animation on hover (20→40)
- OutCubic easing

**FadeLabel:**
- Opacity effect
- Fade-in animation on creation
- 400ms duration

### 6.4.3 UI Components (`src/gui/components.py`)

**SettingsWidget:**
- Blur threshold slider with presets
- Similarity threshold slider with presets
- Face detection toggle

**ProgressWidget:**
- Progress bar component
- Status label
- Show/hide functionality

**ResultsWidget:**
- Statistics display grid
- Category-specific styling
- Clear functionality

## 6.5 Validation Implementation

### InputValidator (`src/utils/validators.py`)

Comprehensive input validation:

| Method | Validates | Returns |
|--------|-----------|---------|
| `validate_folder_path(path)` | Folder existence, permissions | `(bool, str)` |
| `validate_image_files(folder)` | Image file presence | `(bool, str, List)` |
| `validate_thresholds(blur, sim)` | Threshold ranges | `(bool, str)` |
| `validate_file_size(path, max)` | File size limits | `(bool, str)` |

**Supported Image Extensions:**
`.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.tif`, `.gif`, `.webp`, `.heic`, `.heif`, `.raw`, `.cr2`, `.nef`, `.arw`, `.orf`, `.dng`
