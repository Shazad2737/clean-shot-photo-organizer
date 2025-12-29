# 5. Tools & Technologies

## 5.1 Technology Stack Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     TECHNOLOGY STACK                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    PROGRAMMING LANGUAGE                  │    │
│  │                   Python 3.11+                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌───────────────────────┬─────────────────────────────────┐    │
│  │    GUI FRAMEWORK      │    COMPUTER VISION              │    │
│  │    PySide6 6.5+       │    OpenCV 4.5+                  │    │
│  │    Qt 6               │    cv2                          │    │
│  └───────────────────────┴─────────────────────────────────┘    │
│                                                                  │
│  ┌───────────────────────┬─────────────────────────────────┐    │
│  │  IMAGE PROCESSING     │    HASHING                      │    │
│  │  Pillow 10.0+         │    ImageHash 4.3+               │    │
│  │  PIL                  │    Perceptual Hashing           │    │
│  └───────────────────────┴─────────────────────────────────┘    │
│                                                                  │
│  ┌───────────────────────┬─────────────────────────────────┐    │
│  │   NUMERICAL           │    FACE RECOGNITION (Optional)  │    │
│  │   NumPy 1.21+         │    DeepFace                     │    │
│  │   Array Operations    │    TensorFlow 2.x               │    │
│  └───────────────────────┴─────────────────────────────────┘    │
│                                                                  │
│  ┌───────────────────────┬─────────────────────────────────┐    │
│  │   TESTING             │    VERSION CONTROL              │    │
│  │   pytest 7.0+         │    Git                          │    │
│  │   pytest-cov 4.0+     │    GitHub                       │    │
│  └───────────────────────┴─────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 5.2 Core Dependencies

### 5.2.1 Python 3.11+
- **Purpose**: Primary programming language
- **Features Used**: Type hints, dataclasses, pathlib, async/await
- **Selection Reason**: Modern language features, excellent library ecosystem

### 5.2.2 PySide6 (Qt for Python)
- **Version**: 6.5.0+
- **Purpose**: Cross-platform GUI framework
- **Components Used**:
  - `QMainWindow`, `QWidget` - Window management
  - `QThread`, `QMutex`, `QWaitCondition` - Threading
  - `Signal`, `Slot` - Event communication
  - `QPropertyAnimation` - Smooth animations
  - `QGraphicsDropShadowEffect` - Visual effects

**Why PySide6 over alternatives:**
| Framework | Pros | Cons |
|-----------|------|------|
| **PySide6** ✓ | Modern, LGPL licensed, Qt 6 | Larger package size |
| PyQt6 | Mature, Qt 6 | GPL/Commercial license |
| Tkinter | Built-in, simple | Outdated look, limited |
| wxPython | Native look | Less modern API |

### 5.2.3 OpenCV (cv2)
- **Version**: 4.5.0+
- **Purpose**: Computer vision algorithms
- **Functions Used**:
  - `cv2.imread()`, `cv2.cvtColor()` - Image loading
  - `cv2.Laplacian()`, `cv2.Sobel()` - Blur detection
  - `cv2.CascadeClassifier` - Face detection (Haar)
  - `cv2.resize()` - Image normalization

### 5.2.4 Pillow (PIL)
- **Version**: 10.0.0+
- **Purpose**: Image processing and manipulation
- **Functions Used**:
  - `Image.open()` - Cross-format image loading
  - `Image.resize()` - Thumbnail generation
  - `Image.convert()` - Color mode conversion

### 5.2.5 ImageHash
- **Version**: 4.3.0+
- **Purpose**: Perceptual image hashing
- **Hash Types**:
  - `imagehash.average_hash()` - Average pixel hash
  - `imagehash.phash()` - Perceptual hash (DCT-based)
  - `imagehash.dhash()` - Difference hash

### 5.2.6 NumPy
- **Version**: 1.21.0+
- **Purpose**: Numerical computations
- **Usage**: Array operations, statistical calculations (mean, variance)

## 5.3 Optional Dependencies

### 5.3.1 DeepFace
- **Purpose**: Advanced face recognition
- **Backend**: TensorFlow 2.x
- **Models**: VGG-Face, OpenFace, Facenet, DeepFace
- **Note**: Optional - application works without it

## 5.4 Development Tools

### 5.4.1 Testing
| Tool | Version | Purpose |
|------|---------|---------|
| pytest | 7.0+ | Test framework |
| pytest-cov | 4.0+ | Coverage reporting |

### 5.4.2 Development Environment
| Tool | Purpose |
|------|---------|
| VS Code / PyCharm | IDE |
| Git | Version control |
| GitHub | Repository hosting |
| pip | Package management |

## 5.5 Requirements Installation

```bash
# Core requirements
pip install opencv-python>=4.5.0
pip install Pillow>=10.0.0
pip install PySide6>=6.5.0
pip install imagehash>=4.3.0
pip install numpy>=1.21.0

# Testing dependencies
pip install pytest>=7.0.0
pip install pytest-cov>=4.0.0

# Optional: Advanced face recognition
pip install deepface
pip install tensorflow>=2.0.0
```

## 5.6 System Requirements

### Minimum Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Windows 10 / Linux / macOS | Windows 11 |
| Python | 3.9 | 3.11+ |
| RAM | 4 GB | 8 GB+ |
| Disk | 500 MB | 1 GB+ |
| CPU | Dual-core | Quad-core+ |

### For Large Collections (1000+ photos)
- 8 GB RAM recommended
- SSD for faster file operations
- Multi-core CPU for parallel processing
