# 2. System Overview

## 2.1 System Architecture

CLEAN SHOT follows a modular, layered architecture that separates concerns across distinct components:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER (GUI)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Main Window  │  │  Components  │  │  Theme & Animations  │  │
│  │  (main.py)   │  │ (Settings,   │  │  (theme.py,          │  │
│  │              │  │  Progress,   │  │   modern_styles.py)  │  │
│  │              │  │  Results)    │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                          │
│  ┌──────────────────────────┐  ┌─────────────────────────────┐  │
│  │    Worker Threads        │  │      Configuration          │  │
│  │  - PhotoProcessor        │  │  - AppConfig               │  │
│  │  - FaceSearchProcessor   │  │  - ProcessingSession       │  │
│  │  - BaseProcessor         │  │  - ThemeManager            │  │
│  └──────────────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CORE LAYER                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐   │
│  │ BlurDetector   │  │DuplicateDetector│  │  FaceDetector   │  │
│  │ - Laplacian    │  │ - Average Hash  │  │ - Haar Cascade  │  │
│  │ - Sobel        │  │ - pHash         │  │ - DeepFace      │  │
│  │                │  │ - dHash         │  │   (optional)    │  │
│  └────────────────┘  └────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    UTILITY LAYER                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  InputValidator │  │  File Manager   │  │    Logging      │ │
│  │  - Path check   │  │  - Move/Copy    │  │  - Operations   │ │
│  │  - Thresholds   │  │  - Undo support │  │  - Errors       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 2.2 Component Description

### 2.2.1 Presentation Layer (GUI)

| Component | File | Responsibility |
|-----------|------|----------------|
| MainWindow | `main.py` | Primary application window with all UI elements |
| SettingsWidget | `components.py` | Detection threshold configuration panel |
| ProgressWidget | `components.py` | Real-time progress display with status |
| ResultsWidget | `components.py` | Processing results and statistics display |
| ThemeManager | `theme.py` | Dark/Light theme CSS generation |
| AnimatedWidgets | `theme.py` | Animated buttons, cards, and labels |

### 2.2.2 Business Logic Layer

| Component | File | Responsibility |
|-----------|------|----------------|
| PhotoProcessor | `workers.py` | Background thread for photo organization |
| FaceSearchProcessor | `workers.py` | Background thread for face recognition |
| BaseProcessor | `workers.py` | Base class with pause/stop support |
| AppConfig | `main.py` | Application configuration and defaults |
| ProcessingSession | `main.py` | Session save/load functionality |

### 2.2.3 Core Layer (Detectors)

| Component | File | Responsibility |
|-----------|------|----------------|
| BlurDetector | `detectors.py` | Multi-metric blur detection (Laplacian + Sobel) |
| DuplicateDetector | `detectors.py` | Multi-hash duplicate detection (aHash + pHash + dHash) |
| FaceDetector | `detectors.py` | Face detection using Haar cascades |

### 2.2.4 Utility Layer

| Component | File | Responsibility |
|-----------|------|----------------|
| InputValidator | `validators.py` | Folder path and threshold validation |
| File Operations | (integrated) | Safe file move/copy with undo support |
| Logging | (integrated) | Operation and error logging |

## 2.3 Data Flow

```
┌─────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│  User Input │ ──▶ │  Input Validation   │ ──▶ │ Photo Discovery │
│  (Folder +  │     │  (Path, Thresholds) │     │ (Image Files)   │
│  Settings)  │     └─────────────────────┘     └─────────────────┘
└─────────────┘                                         │
                                                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Processing Pipeline                           │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────────┐   │
│  │ Blur Detection │─▶│Duplicate Check │─▶│ Face Detection (opt) │   │
│  │ (per image)    │  │ (per image)    │  │ (per good image)     │   │
│  └────────────────┘  └────────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      File Organization                               │
│  ┌───────────────┐  ┌─────────────────┐  ┌───────────────────────┐  │
│  │  Blurry_Photos│  │ Duplicate_Photos│  │  Face_Photos (copy)   │  │
│  └───────────────┘  └─────────────────┘  └───────────────────────┘  │
│  Good photos remain in original location                             │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────┐     ┌────────────────────┐
│  Operation Logging  │ ──▶ │  Results Display   │
│  (JSON file)        │     │  & Statistics      │
└─────────────────────┘     └────────────────────┘
```

## 2.4 Threading Model

The application uses Qt's threading model for responsive UI:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Main Thread (UI)                          │
│  - User interaction handling                                     │
│  - Progress display updates                                      │
│  - Result rendering                                              │
└─────────────────────────────────────────────────────────────────┘
        │                                    ▲
        │ Start Processing                   │ Signals
        ▼                                    │
┌─────────────────────────────────────────────────────────────────┐
│                      Worker Thread                               │
│  - PhotoProcessor or FaceSearchProcessor                        │
│  - Background image processing                                   │
│  - Emits progress_updated, status_updated, finished signals     │
└─────────────────────────────────────────────────────────────────┘
```

**Thread Communication Signals:**
- `progress_updated(int)` - Processing progress percentage
- `status_updated(str)` - Current processing status message
- `log_message(str)` - Log messages for display
- `finished_processing(dict)` - Processing results
- `face_found(str, float)` - Face match found with similarity

## 2.5 File Organization Structure

After processing, photos are organized as follows:

```
Selected Photo Folder/
├── Blurry_Photos/          # Photos below blur threshold
│   └── image1.jpg
├── Duplicate_Photos/       # Duplicate/similar photos
│   └── image2.jpg
├── Face_Photos/           # Photos containing faces (copies)
│   └── image3.jpg
├── image4.jpg             # Good photos (remain in place)
└── operations.json        # Undo operation log
```
