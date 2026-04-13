import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
from DataManager import DataManager
from MapView import MapView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map Guessing Game - World Explorer")
        self.resize(1024, 768)
        
        # 1. Initialize Data
        self.data_manager = DataManager()
        self.data_manager.load_from_json('countries.json')
        
        # 2. Setup UI Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Add a title label
        self.label = QLabel("Explore the World! Click a country to learn more.")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)
        
        # 3. Add the Map View
        self.map_view = MapView()
        self.layout.addWidget(self.map_view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())