import sys
import os
import logging
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QPushButton, QFileDialog, QMessageBox, 
                               QProgressBar, QLabel, QTabWidget, QGroupBox,
                               QLineEdit, QSpinBox, QCheckBox)
from PySide6.QtCore import QThread, Signal, Qt
import cv2
from PIL import Image
import imagehash
import shutil
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PhotoProcessor(QThread):
    progress_updated = Signal(int)
    status_updated = Signal(str)
    finished_processing = Signal(dict)

    def __init__(self, folder_path, blur_threshold=100, similarity_threshold=5, enable_face_detection=True):
        super().__init__()
        self.folder_path = folder_path
        self.blur_threshold = blur_threshold
        self.similarity_threshold = similarity_threshold
        self.enable_face_detection = enable_face_detection
        self.results = {
            'total_processed': 0,
            'good_photos': 0,
            'blurry_photos': 0,
            'duplicate_photos': 0,
            'face_photos': 0
        }

    def is_blurry(self, image_path):
        """Check if image is blurry using Laplacian variance"""
        try:
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                return False
            
            laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
            return laplacian_var < self.blur_threshold
        except Exception as e:
            logging.error(f"Blur detection error: {e}")
            return False

    def is_duplicate(self, image_path, seen_hashes, hash_size=16):
        """Check if image is duplicate using perceptual hashing"""
        try:
            img = Image.open(image_path)
            img_hash = imagehash.average_hash(img, hash_size)
            
            for existing_hash in seen_hashes:
                if img_hash - existing_hash <= self.similarity_threshold:
                    return True, existing_hash
            
            seen_hashes.add(img_hash)
            return False, img_hash
        except Exception as e:
            logging.error(f"Duplicate detection error: {e}")
            return False, None

    def detect_faces(self, image_path):
        """Detect faces in image"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return 0
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            return len(faces)
        except Exception as e:
            logging.error(f"Face detection error: {e}")
            return 0

    def run(self):
        """Main processing function"""
        try:
            # Create category folders
            categories = ["Good_Photos", "Blurry_Photos", "Duplicate_Photos", "Face_Photos"]
            for category in categories:
                os.makedirs(os.path.join(self.folder_path, category), exist_ok=True)

            # Get image files
            image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
            image_files = [f for f in os.listdir(self.folder_path) 
                          if f.lower().endswith(image_extensions)]
            total_files = len(image_files)
            
            if total_files == 0:
                self.status_updated.emit("No image files found!")
                return

            seen_hashes = set()
            
            for index, filename in enumerate(image_files):
                file_path = os.path.join(self.folder_path, filename)
                
                # Update progress
                progress = int((index + 1) / total_files * 100)
                self.progress_updated.emit(progress)
                self.status_updated.emit(f"Processing: {filename}")
                
                if not os.path.exists(file_path):
                    continue

                self.results['total_processed'] += 1
                target_category = "Good_Photos"

                # Check for duplicates
                is_dup, _ = self.is_duplicate(file_path, seen_hashes)
                if is_dup:
                    target_category = "Duplicate_Photos"
                    self.results['duplicate_photos'] += 1
                else:
                    # Check for blur
                    if self.is_blurry(file_path):
                        target_category = "Blurry_Photos"
                        self.results['blurry_photos'] += 1
                    else:
                        self.results['good_photos'] += 1

                    # Face detection
                    if self.enable_face_detection and self.detect_faces(file_path) > 0:
                        face_path = os.path.join(self.folder_path, "Face_Photos", filename)
                        shutil.copy2(file_path, face_path)
                        self.results['face_photos'] += 1

                # Move file to appropriate folder
                if target_category != "Good_Photos" or not is_dup:
                    target_path = os.path.join(self.folder_path, target_category, filename)
                    shutil.move(file_path, target_path)

            self.status_updated.emit("Processing completed!")
            self.finished_processing.emit(self.results)

        except Exception as e:
            logging.error(f"Processing error: {e}")
            self.status_updated.emit(f"Error: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CLEAN SHOT - AI Photo Organizer")
        self.setGeometry(100, 100, 600, 400)
        self.setup_ui()
        self.current_folder = ""

    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Select a folder containing photos")
        self.select_btn = QPushButton("Browse Folder")
        self.select_btn.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.select_btn)

        # Settings
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("Blur Threshold:"))
        self.blur_threshold = QSpinBox()
        self.blur_threshold.setRange(0, 500)
        self.blur_threshold.setValue(100)
        settings_layout.addWidget(self.blur_threshold)

        settings_layout.addWidget(QLabel("Similarity:"))
        self.similarity_threshold = QSpinBox()
        self.similarity_threshold.setRange(0, 20)
        self.similarity_threshold.setValue(5)
        settings_layout.addWidget(self.similarity_threshold)

        self.face_checkbox = QCheckBox("Enable Face Detection")
        self.face_checkbox.setChecked(True)
        settings_layout.addWidget(self.face_checkbox)

        # Progress
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Ready to process photos")

        # Process button
        self.process_btn = QPushButton("Start Processing")
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setEnabled(False)

        # Results
        self.results_label = QLabel("")
        self.results_label.setAlignment(Qt.AlignCenter)

        # Add all to layout
        layout.addLayout(folder_layout)
        layout.addLayout(settings_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(self.process_btn)
        layout.addWidget(self.results_label)
        layout.addStretch()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Photo Folder")
        if folder:
            self.current_folder = folder
            self.folder_label.setText(f"Selected: {os.path.basename(folder)}")
            self.process_btn.setEnabled(True)
            self.status_label.setText("Folder selected. Click 'Start Processing'.")

    def start_processing(self):
        if not self.current_folder:
            QMessageBox.warning(self, "Error", "Please select a folder first.")
            return

        self.process_btn.setEnabled(False)
        self.results_label.setText("")

        # Create processor
        self.processor = PhotoProcessor(
            self.current_folder,
            self.blur_threshold.value(),
            self.similarity_threshold.value(),
            self.face_checkbox.isChecked()
        )

        # Connect signals
        self.processor.progress_updated.connect(self.progress_bar.setValue)
        self.processor.status_updated.connect(self.status_label.setText)
        self.processor.finished_processing.connect(self.processing_finished)

        # Start processing
        self.processor.start()

    def processing_finished(self, results):
        self.process_btn.setEnabled(True)
        
        results_text = (f"✅ Processing Complete!\n\n"
                       f"Total Photos: {results['total_processed']}\n"
                       f"Good Photos: {results['good_photos']}\n"
                       f"Blurry Photos: {results['blurry_photos']}\n"
                       f"Duplicate Photos: {results['duplicate_photos']}\n"
                       f"Photos with Faces: {results['face_photos']}")
        
        self.results_label.setText(results_text)
        QMessageBox.information(self, "Complete", "Photo organization finished!")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CLEAN SHOT")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()