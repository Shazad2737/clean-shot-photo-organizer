# CLEAN SHOT - AI Photo Organizer
## Project Report Documentation

---

## Table of Contents

| # | Section | Description |
|---|---------|-------------|
| 1 | [Introduction](1_INTRODUCTION.md) | Project overview, objectives, scope |
| 2 | [System Overview](2_SYSTEM_OVERVIEW.md) | Architecture, components, data flow |
| 3 | [Methodology](3_METHODOLOGY.md) | Development approach and lifecycle |
| 4 | [Design](4_DESIGN.md) | Algorithm design, UI design, data storage |
| 5 | [Tools & Technologies](5_TOOLS_AND_TECHNOLOGIES.md) | Tech stack, dependencies |
| 6 | [Implementation](6_IMPLEMENTATION.md) | Project structure, module details |
| 7 | [Sample Code](7_SAMPLE_CODE.md) | Key algorithm implementations |
| 8 | [Screenshots](8_SCREENSHOTS.md) | UI mockups and screenshot guide |
| 9 | [Testing](9_TESTING.md) | Test strategy, unit tests, coverage |
| 10 | [Conclusion](10_CONCLUSION.md) | Summary, future work, lessons learned |

---

## Quick Project Overview

**CLEAN SHOT** is an intelligent desktop application that automatically organizes photos using AI algorithms for:

- 🌫️ **Blur Detection** - Multi-metric Laplacian + Sobel scoring
- 📋 **Duplicate Finding** - Multi-hash perceptual comparison
- 👤 **Face Detection** - Haar cascade + optional DeepFace recognition

### Key Features

- ✅ 100% Offline - Complete privacy protection
- ⚡ Fast Processing - 1000+ images in <10 minutes  
- 🎨 Modern GUI - Dark theme with animations
- ↩️ Undo Support - Reversible file operations

### Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| GUI | PySide6 / Qt 6 |
| Computer Vision | OpenCV 4.5+ |
| Image Processing | Pillow, ImageHash |
| Face Recognition | DeepFace (optional) |
| Testing | pytest, pytest-cov |

---

## How to Use This Documentation

1. **For Understanding**: Read sections 1-3 for project context
2. **For Technical Details**: Read sections 4-7 for architecture and code
3. **For Visual Reference**: See section 8 for UI mockups
4. **For Quality Assurance**: See section 9 for testing details
5. **For Summary**: Read section 10 for conclusions and future work

---

## Document Generation

| Field | Value |
|-------|-------|
| Generated | December 2024 |
| Version | 1.0 |
| Format | Markdown |
| Author | Project Team |

---

**Repository**: https://github.com/Shazad2737/clean-shot-photo-organizer
