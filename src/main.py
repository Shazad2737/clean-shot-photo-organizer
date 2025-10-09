import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QWidget, QPushButton, QLabel, QProgressBar,
                               QFileDialog, QMessageBox)
from PySide6.QtCore import Qt

class SimpleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CLEAN SHOT - Simple Test")
        self.setGeometry(200, 200, 500, 300)
        self.init_ui()
        
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        self.label = QLabel("CLEAN SHOT - Photo Organizer\nSelect a folder to start")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        self.btn_folder = QPushButton("Browse Folder")
        self.btn_folder.clicked.connect(self.browse_folder)
        layout.addWidget(self.btn_folder)
        
        self.btn_process = QPushButton("Process Photos")
        self.btn_process.clicked.connect(self.process_photos)
        self.btn_process.setEnabled(False)
        layout.addWidget(self.btn_process)
        
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        self.status = QLabel("Ready")
        layout.addWidget(self.status)
        
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Photo Folder")
        if folder:
            self.label.setText(f"Folder: {os.path.basename(folder)}")
            self.btn_process.setEnabled(True)
            self.current_folder = folder
            
    def process_photos(self):
        self.status.setText("Processing photos...")
        self.progress.setValue(50)
        # Simulate processing
        self.status.setText("Processing complete!")
        self.progress.setValue(100)
        QMessageBox.information(self, "Complete", "Demo processing finished!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Windows")
    window = SimpleApp()
    window.show()
    sys.exit(app.exec())