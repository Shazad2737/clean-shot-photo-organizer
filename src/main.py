import sys
import os
import logging
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QPushButton, QFileDialog, QMessageBox, 
                               QProgressBar, QLabel, QTabWidget, QGroupBox,
                               QSpinBox, QCheckBox, QFrame, QTextEdit, QScrollArea)
from PySide6.QtCore import QThread, Signal, Qt, QTimer, QTime
from PySide6.QtGui import QFont, QIcon, QPixmap, QColor, QPalette
import cv2
from PIL import Image
import imagehash
import shutil
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class StyledButton(QPushButton):
    """Custom styled button"""
    def __init__(self, text, primary=False):
        super().__init__(text)
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QPushButton:disabled {
                    background-color: #BDBDBD;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    color: #2196F3;
                    border: 2px solid #2196F3;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #E3F2FD;
                }
                QPushButton:pressed {
                    background-color: #BBDEFB;
                }
            """)
        self.setMinimumHeight(40)

class PhotoProcessor(QThread):
    progress_updated = Signal(int)
    status_updated = Signal(str)
    finished_processing = Signal(dict)
    log_message = Signal(str)

    def __init__(self, folder_path, blur_threshold=100, similarity_threshold=5):
        super().__init__()
        self.folder_path = folder_path
        self.blur_threshold = blur_threshold
        self.similarity_threshold = similarity_threshold

    def is_blurry(self, image_path):
        """Check if image is blurry using Laplacian variance"""
        try:
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                return False
            laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
            return laplacian_var < self.blur_threshold
        except Exception as e:
            self.log_message.emit(f"Blur detection error: {e}")
            return False

    def is_duplicate(self, image_path, seen_hashes):
        """Check if image is duplicate using perceptual hashing"""
        try:
            img = Image.open(image_path)
            img_hash = imagehash.average_hash(img)
            
            for existing_hash in seen_hashes:
                if img_hash - existing_hash <= self.similarity_threshold:
                    return True, existing_hash
            
            seen_hashes.add(img_hash)
            return False, img_hash
        except Exception as e:
            self.log_message.emit(f"Duplicate detection error: {e}")
            return False, None

    def run(self):
        """Main processing function"""
        try:
            # Create category folders
            categories = ["Good_Photos", "Blurry_Photos", "Duplicate_Photos"]
            for category in categories:
                os.makedirs(os.path.join(self.folder_path, category), exist_ok=True)

            # Get image files
            image_files = [f for f in os.listdir(self.folder_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))]
            
            total_files = len(image_files)
            if total_files == 0:
                self.status_updated.emit("No image files found!")
                return

            seen_hashes = set()
            results = {'processed': 0, 'good': 0, 'blurry': 0, 'duplicate': 0}

            # Process each image
            for index, filename in enumerate(image_files):
                file_path = os.path.join(self.folder_path, filename)
                
                # Update progress
                progress = int((index + 1) / total_files * 100)
                self.progress_updated.emit(progress)
                self.status_updated.emit(f"Processing: {filename}")
                
                if not os.path.exists(file_path):
                    continue

                results['processed'] += 1
                target_category = "Good_Photos"

                # Check for duplicates
                is_dup, _ = self.is_duplicate(file_path, seen_hashes)
                if is_dup:
                    target_category = "Duplicate_Photos"
                    results['duplicate'] += 1
                    self.log_message.emit(f"📋 Duplicate found: {filename}")
                elif self.is_blurry(file_path):
                    target_category = "Blurry_Photos"
                    results['blurry'] += 1
                    self.log_message.emit(f"📸 Blurry image: {filename}")
                else:
                    results['good'] += 1
                    self.log_message.emit(f"✅ Good image: {filename}")

                # Move file to appropriate folder
                target_path = os.path.join(self.folder_path, target_category, filename)
                shutil.move(file_path, target_path)

            self.finished_processing.emit(results)
            
        except Exception as e:
            self.log_message.emit(f"Error: {e}")
            self.status_updated.emit(f"Error: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CLEAN SHOT - AI Photo Organizer")
        self.setGeometry(100, 100, 900, 700)
        self.setup_ui()
        
    def setup_ui(self):
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QLabel {
                color: #333333;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2196F3;
            }
            QProgressBar {
                border: 1px solid #BDBDBD;
                border-radius: 3px;
                text-align: center;
                background-color: #E0E0E0;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QSpinBox {
                border: 1px solid #BDBDBD;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QTextEdit {
                border: 1px solid #BDBDBD;
                border-radius: 3px;
                background-color: white;
                font-family: 'Consolas', 'Monospace';
                font-size: 11px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("🧹 CLEAN SHOT - AI Photo Organizer")
        header.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header.setStyleSheet("color: #2196F3; padding: 10px 0;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Subtitle
        subtitle = QLabel("Automatically categorize photos by quality using AI")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #757575; padding-bottom: 10px;")
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #E0E0E0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
            QTabBar::tab:hover {
                background-color: #BBDEFB;
            }
        """)
        
        # Organizer Tab
        organizer_tab = QWidget()
        self.setup_organizer_tab(organizer_tab)
        self.tabs.addTab(organizer_tab, "📁 Organizer")
        
        # Settings Tab
        settings_tab = QWidget()
        self.setup_settings_tab(settings_tab)
        self.tabs.addTab(settings_tab, "⚙️ Settings")
        
        # Log Tab
        log_tab = QWidget()
        self.setup_log_tab(log_tab)
        self.tabs.addTab(log_tab, "📝 Log")
        
        main_layout.addWidget(self.tabs)
        
    def setup_organizer_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Folder Selection Card
        folder_card = QGroupBox("Folder Selection")
        folder_layout = QVBoxLayout(folder_card)
        
        folder_btn_layout = QHBoxLayout()
        self.folder_btn = StyledButton("📂 Browse Folder", primary=True)
        self.folder_btn.clicked.connect(self.select_folder)
        folder_btn_layout.addWidget(self.folder_btn)
        
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setStyleSheet("color: #757575; font-style: italic; padding: 5px;")
        folder_btn_layout.addWidget(self.folder_label, 1)
        
        folder_layout.addLayout(folder_btn_layout)
        
        # Folder info
        self.folder_info = QLabel("")
        self.folder_info.setStyleSheet("background-color: #E8F5E9; padding: 8px; border-radius: 5px;")
        self.folder_info.setVisible(False)
        folder_layout.addWidget(self.folder_info)
        
        layout.addWidget(folder_card)
        
        # Progress Card
        progress_card = QGroupBox("Processing Progress")
        progress_layout = QVBoxLayout(progress_card)
        
        # Progress bar with percentage
        progress_bar_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #8BC34A);
            }
        """)
        progress_bar_layout.addWidget(self.progress_bar)
        
        self.percentage_label = QLabel("0%")
        self.percentage_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.percentage_label.setStyleSheet("color: #2196F3; min-width: 50px;")
        progress_bar_layout.addWidget(self.percentage_label)
        
        progress_layout.addLayout(progress_bar_layout)
        
        # Status
        self.status_label = QLabel("Ready to organize photos")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #E3F2FD;
                padding: 10px;
                border-radius: 5px;
                border-left: 4px solid #2196F3;
            }
        """)
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_card)
        
        # Action Card
        action_card = QGroupBox("Actions")
        action_layout = QVBoxLayout(action_card)
        
        self.process_btn = StyledButton("🚀 Start Processing", primary=True)
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setEnabled(False)
        self.process_btn.setMinimumHeight(50)
        action_layout.addWidget(self.process_btn)
        
        layout.addWidget(action_card)
        
        # Results Card - WITH SCROLLING
        self.results_card = QGroupBox("Results")
        self.results_card.setVisible(False)
        results_layout = QVBoxLayout(self.results_card)
        
        # Create a scroll area for results
        results_scroll = QScrollArea()
        results_scroll.setWidgetResizable(True)
        results_scroll.setMinimumHeight(150)
        results_scroll.setMaximumHeight(250)
        results_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                background-color: white;
            }
            QScrollBar:vertical {
                border: none;
                background: #F5F5F5;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9E9E9E;
            }
        """)
        
        # Create container widget for scroll area
        results_container = QWidget()
        results_container_layout = QVBoxLayout(results_container)
        results_container_layout.setContentsMargins(10, 10, 10, 10)
        
        self.results_label = QLabel("")
        self.results_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                line-height: 1.5;
                padding: 10px;
            }
        """)
        self.results_label.setWordWrap(True)
        self.results_label.setTextFormat(Qt.RichText)
        self.results_label.setAlignment(Qt.AlignCenter)
        
        results_container_layout.addWidget(self.results_label)
        results_scroll.setWidget(results_container)
        
        results_layout.addWidget(results_scroll)
        layout.addWidget(self.results_card)
        
        layout.addStretch()
        
    def setup_settings_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Blur Detection Settings
        blur_card = QGroupBox("🔍 Blur Detection Settings")
        blur_layout = QVBoxLayout(blur_card)
        
        blur_info = QLabel("Lower threshold = more sensitive to blur\nRecommended: 50-150")
        blur_info.setStyleSheet("color: #757575; font-size: 11px; padding-bottom: 10px;")
        blur_layout.addWidget(blur_info)
        
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Blur Threshold:"))
        self.blur_spinbox = QSpinBox()
        self.blur_spinbox.setRange(10, 500)
        self.blur_spinbox.setValue(100)
        self.blur_spinbox.setSuffix(" px")
        self.blur_spinbox.setSingleStep(10)
        threshold_layout.addWidget(self.blur_spinbox)
        threshold_layout.addStretch()
        blur_layout.addLayout(threshold_layout)
        
        layout.addWidget(blur_card)
        
        # Duplicate Detection Settings
        duplicate_card = QGroupBox("📋 Duplicate Detection Settings")
        duplicate_layout = QVBoxLayout(duplicate_card)
        
        duplicate_info = QLabel("Lower sensitivity = more strict\nRecommended: 3-8")
        duplicate_info.setStyleSheet("color: #757575; font-size: 11px; padding-bottom: 10px;")
        duplicate_layout.addWidget(duplicate_info)
        
        sensitivity_layout = QHBoxLayout()
        sensitivity_layout.addWidget(QLabel("Similarity Sensitivity:"))
        self.sim_spinbox = QSpinBox()
        self.sim_spinbox.setRange(0, 20)
        self.sim_spinbox.setValue(5)
        sensitivity_layout.addWidget(self.sim_spinbox)
        sensitivity_layout.addStretch()
        duplicate_layout.addLayout(sensitivity_layout)
        
        layout.addWidget(duplicate_card)
        
        # Supported Formats
        format_card = QGroupBox("📷 Supported Formats")
        format_layout = QVBoxLayout(format_card)
        
        formats = QLabel("• JPG / JPEG\n• PNG\n• BMP\n• WEBP")
        formats.setStyleSheet("font-size: 12px; padding: 10px;")
        format_layout.addWidget(formats)
        
        layout.addWidget(format_card)
        
        layout.addStretch()
        
    def setup_log_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        log_label = QLabel("Processing Log")
        log_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(300)
        layout.addWidget(self.log_text)
        
        # Log controls
        log_controls = QHBoxLayout()
        self.clear_log_btn = StyledButton("Clear Log")
        self.clear_log_btn.clicked.connect(lambda: self.log_text.clear())
        log_controls.addWidget(self.clear_log_btn)
        
        log_controls.addStretch()
        layout.addLayout(log_controls)
        
        # Statistics
        stats_card = QGroupBox("📊 Statistics")
        stats_layout = QVBoxLayout(stats_card)
        
        self.stats_label = QLabel("No processing completed yet")
        self.stats_label.setStyleSheet("font-size: 12px; padding: 10px;")
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(stats_card)
        
        layout.addStretch()
        
    def add_log_message(self, message):
        """Add message to log"""
        timestamp = QTime.currentTime().toString("hh:mm:ss")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Photo Folder")
        if folder:
            self.current_folder = folder
            self.folder_label.setText(f"📁 {os.path.basename(folder)}")
            self.folder_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
            # Count images
            image_files = [f for f in os.listdir(folder) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))]
            
            self.folder_info.setText(f"📊 Found {len(image_files)} image(s) in folder")
            self.folder_info.setVisible(True)
            
            self.process_btn.setEnabled(True)
            self.status_label.setText(f"✅ Ready to process {len(image_files)} image(s)")
            
            self.add_log_message(f"Selected folder: {folder}")
            self.add_log_message(f"Found {len(image_files)} images")
            
    def start_processing(self):
        if not hasattr(self, 'current_folder'):
            QMessageBox.warning(self, "Warning", "Please select a folder first!")
            return
            
        self.process_btn.setEnabled(False)
        self.process_btn.setText("⏳ Processing...")
        self.results_card.setVisible(False)
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.percentage_label.setText("0%")
        
        self.add_log_message("=" * 50)
        self.add_log_message("Starting photo processing...")
        
        self.processor = PhotoProcessor(
            self.current_folder,
            self.blur_spinbox.value(),
            self.sim_spinbox.value()
        )
        
        self.processor.progress_updated.connect(self.update_progress)
        self.processor.status_updated.connect(self.status_label.setText)
        self.processor.finished_processing.connect(self.processing_finished)
        self.processor.log_message.connect(self.add_log_message)
        
        self.processor.start()
        
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.percentage_label.setText(f"{value}%")
        
    def processing_finished(self, results):
        self.process_btn.setEnabled(True)
        self.process_btn.setText("🚀 Start Processing")
        
        # Show results card
        self.results_card.setVisible(True)
        
        # Create results summary with HTML formatting
        results_text = f"""
        <div style='text-align: center; font-family: Arial, sans-serif;'>
            <h3 style='color: #4CAF50; margin-bottom: 20px;'>✅ Processing Complete!</h3>
            
            <div style='display: inline-block; text-align: left; margin: 10px; background-color: #E8F5E9; 
                 padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 500px;'>
                
                <div style='margin-bottom: 15px;'>
                    <div style='font-size: 16px; font-weight: bold; color: #2196F3; margin-bottom: 5px;'>📊 Total Processed</div>
                    <div style='font-size: 24px; color: #1976D2;'>{results['processed']} images</div>
                </div>
                
                <hr style='border: none; border-top: 1px solid #C8E6C9; margin: 15px 0;'>
                
                <div style='display: flex; flex-direction: column; gap: 10px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span style='font-weight: bold; color: #333;'>✅ Good Photos:</span>
                        <span style='font-size: 16px; color: #4CAF50;'>{results['good']} ({self.get_percentage(results['good'], results['processed'])}%)</span>
                    </div>
                    
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span style='font-weight: bold; color: #333;'>📸 Blurry Photos:</span>
                        <span style='font-size: 16px; color: #FF9800;'>{results['blurry']} ({self.get_percentage(results['blurry'], results['processed'])}%)</span>
                    </div>
                    
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span style='font-weight: bold; color: #333;'>📋 Duplicate Photos:</span>
                        <span style='font-size: 16px; color: #F44336;'>{results['duplicate']} ({self.get_percentage(results['duplicate'], results['processed'])}%)</span>
                    </div>
                </div>
            </div>
            
            <div style='margin-top: 20px; color: #757575; font-size: 12px; line-height: 1.4;'>
                <p>📁 <b>Check your folder for categorized photos:</b></p>
                <p style='margin: 5px 0;'>• <b>Good_Photos/</b> - Clear, high-quality images</p>
                <p style='margin: 5px 0;'>• <b>Blurry_Photos/</b> - Blurry or low-quality images</p>
                <p style='margin: 5px 0;'>• <b>Duplicate_Photos/</b> - Duplicate or similar images</p>
            </div>
        </div>
        """
        
        self.results_label.setText(results_text)
        
        # Update statistics
        stats_text = f"""
        Last Processing Results:
        • Total Images: {results['processed']}
        • Good Quality: {results['good']} ({self.get_percentage(results['good'], results['processed'])}%)
        • Blurry: {results['blurry']} ({self.get_percentage(results['blurry'], results['processed'])}%)
        • Duplicates: {results['duplicate']} ({self.get_percentage(results['duplicate'], results['processed'])}%)
        """
        self.stats_label.setText(stats_text)
        
        self.add_log_message(f"Processing complete!")
        self.add_log_message(f"Results: {results}")
        
        QMessageBox.information(self, "Success", 
                               f"Successfully processed {results['processed']} photos!\n\n"
                               f"Check the 'Results' section for details.")
        
    def get_percentage(self, part, whole):
        if whole == 0:
            return 0
        return round((part / whole) * 100)

def main():
    try:
        app = QApplication(sys.argv)
        
        # Set application style
        app.setStyle("Fusion")
        
        # Set application palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, QColor(51, 51, 51))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(51, 51, 51))
        palette.setColor(QPalette.Text, QColor(51, 51, 51))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(51, 51, 51))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.Highlight, QColor(33, 150, 243))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        app.setPalette(palette)
        
        window = MainWindow()
        window.show()
        
        logging.info("CLEAN SHOT started successfully")
        return app.exec()
        
    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())