import sys
from PyQt6.QtWidgets import (QMainWindow, QApplication, QVBoxLayout, QWidget,
                             QLabel, QHBoxLayout, QLineEdit, QPushButton,
                             QStackedWidget, QDialog, QMessageBox, QGraphicsView,
                             QGraphicsScene, QGraphicsPathItem)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QBrush, QColor
from DataManager import DataManager
from MapView import MapView
from GameEngine import GameEngine

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map Guessing Game - World Explorer")
        self.resize(1280, 960)
        
        # 1. Initialize Data and Engine
        self.data_manager = DataManager()
        self.data_manager.load_from_json('countries.json')
        countries_dict = self.data_manager.countries_dict
        countries_list = list(countries_dict.values())
        self.engine = GameEngine(countries_list)
        
        # 2. Main Layout using QStackedWidget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # 3. Create separate mapss for separate progress
        self.explore_map_view = MapView()
        self.explore_map_view.render_map(countries_dict)
        
        self.shape_map_view = MapView()
        self.shape_map_view.render_map(countries_dict)

        # 4. Initialize the quiz to save state
        self.shape_dialog = ShapeQuizDialog(self, self.engine, self.shape_map_view)

        # 5. Create the different screens
        self.init_main_menu()
        self.init_explore_screen()
        self.init_shape_screen()
        
        # 6. Add screens to the stack
        self.stacked_widget.addWidget(self.menu_widget) # Index 0
        self.stacked_widget.addWidget(self.explore_widget) # Index 1
        self.stacked_widget.addWidget(self.shape_widget) # Index 2

    def init_main_menu(self):
        # The very first window
        self.menu_widget = QWidget()
        layout = QVBoxLayout(self.menu_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("WORLD EXPLORER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title.font()
        font.setPointSize(24)
        title.setFont(font)
        layout.addWidget(title)
        
        # Mode Buttons
        btn_explore = QPushButton("Explore Mode")
        btn_explore.clicked.connect(lambda: self.start_mode('explore'))
        
        btn_shape = QPushButton("Shape Quiz")
        btn_shape.clicked.connect(lambda: self.start_mode('shape'))
        
        btn_time = QPushButton("Time Attack (in progress)")
        btn_shape.clicked.connect(lambda: self.start_mode('shape')) #placeholder
        
        btn_flag = QPushButton("Flag Master (in progress)")
        btn_shape.clicked.connect(lambda: self.start_mode('shape')) #placeholder
        
        # Add buttons to menu layout
        for btn in [btn_explore, btn_shape, btn_time, btn_flag]:
            btn.setFixedSize(300, 50)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def init_explore_screen(self):
        self.explore_widget = QWidget()
        layout = QVBoxLayout(self.explore_widget)
        
        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Back to Menu")
        back_btn.clicked.connect(self.go_to_menu)
        
        top_bar.addWidget(back_btn)
        top_bar.addWidget(QLabel("Mode: Explore"))
        top_bar.addStretch()
        
        layout.addLayout(top_bar)
        layout.addWidget(self.explore_map_view) # Add the Explore Map

    def init_shape_screen(self):
        self.shape_widget = QWidget()
        layout = QVBoxLayout(self.shape_widget)
        
        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Back to Menu")
        back_btn.clicked.connect(self.go_to_menu)
        
        # Button to re-open the hidden quiz dialog!
        show_quiz_btn = QPushButton("Show Quiz Window")
        show_quiz_btn.clicked.connect(self.shape_dialog.show)
        
        top_bar.addWidget(back_btn)
        top_bar.addWidget(QLabel("Mode: Shape Quiz"))
        top_bar.addWidget(show_quiz_btn)
        top_bar.addStretch()
        
        layout.addLayout(top_bar)
        layout.addWidget(self.shape_map_view) # Add the Shape Map

    def start_mode(self, mode_name):
        # Switch to the map screen and set up the chosen mode
        if mode_name == 'explore':
            self.engine.set_mode('explore')
            self.stacked_widget.setCurrentIndex(1)
            
        elif mode_name == 'shape':
            # Initialize the shuffled queue in the engine
            self.engine.start_quiz_session('shape')
            self.stacked_widget.setCurrentIndex(2)
            
            # Start the first question and show the dialog
            self.shape_dialog.next_question()
            self.shape_dialog.show()

    def go_to_menu(self):
        # Return to the main menu screen
        self.stacked_widget.setCurrentIndex(0)
        self.shape_dialog.hide()

    def on_map_clicked(self, country_code):
        # handle what happens when a country is clicked
        if self.engine.current_mode == 'explore':
            country_data = self.engine.explore_country(country_code)
            if country_data:
                # Paint the country on the map
                if hasattr(self.explore_map_view, 'highlight_country'):
                    self.explore_map_view.highlight_country(country_code, "green")
                
                # Show the pop-up information window
                info_text = (
                    f"Name: {country_data.name}\n"
                    f"Capital: {country_data.capital}\n"
                    f"Population: {country_data.population:,}\n"
                    f"Area: {country_data.area:,.0f} km²"
                )
                QTimer.singleShot(200, lambda: QMessageBox.information(self, "Country Discovered!", info_text))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'map_view') and self.explore_map_view.scene.items():
            self.explore_map_view.fitInView(self.explore_map_view.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

class ShapeQuizDialog(QDialog):
    # Pop-up window for the shape quiz
    def __init__(self, parent=None, engine=None, map_view=None):
        super().__init__(parent)
        self.engine = engine
        self.map_view = map_view
        self.setWindowTitle("Shape Quiz")
        self.resize(300, 200)
        
        layout = QVBoxLayout(self)
        
        self.score_label = QLabel(f"Score: {self.engine.score}")
        layout.addWidget(self.score_label)

        self.shape_label = QLabel("Guess this shape")
        self.shape_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.shape_label)

        self.shape_scene = QGraphicsScene()
        self.shape_view = QGraphicsView(self.shape_scene)
        self.shape_view.setFixedSize(250, 150)
        layout.addWidget(self.shape_view)
        
        self.guess_input = QLineEdit()
        self.guess_input.setPlaceholderText("Type country name here...")
        self.guess_input.returnPressed.connect(self.submit_guess)
        layout.addWidget(self.guess_input)
        
        btn_layout = QHBoxLayout()
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.submit_guess)
        
        self.hint_btn = QPushButton("Hint")
        self.hint_btn.clicked.connect(self.show_hint)
        
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.hint_btn)
        layout.addLayout(btn_layout)

    def closeEvent(self, event):
        # the window will be hidden instead of closed
        event.ignore()
        self.hide()

    def display_shape(self, country_path):
        self.shape_scene.clear()
        # Create a new item using the path and add it to the mini-scene
        if country_path:
            shape_item = QGraphicsPathItem(country_path)
            shape_item.setBrush(QBrush(Qt.GlobalColor.blue))
            self.shape_scene.addItem(shape_item)
        
        # Scale the view to fit the shape perfectly
            self.shape_view.fitInView(shape_item.boundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        
    def next_question(self):
        target = self.engine.next_quiz_target()
        if target:
            self.score_label.setText(f"Score: {self.engine.score}")
            self.shape_label.setText(f"Guess this shape! (Code: {target.code})")
            self.guess_input.clear()

            country_path = self.map_view.get_country_path(target.code)
            if country_path:
                self.display_shape(country_path)
            else:
                print(f"Warning: Could not find path for {target.code}")
        else:
            QMessageBox.information(self, "Quiz Over", f"You finished the quiz! Final Score: {self.engine.score}")
            self.hide() # Hide the window

    def submit_guess(self):
        guess_text = self.guess_input.text()
        if not guess_text:
            return
            
        if self.engine.check_answer(guess_text):
            # If correct, update map and get next question
            self.map_view.highlight_country(self.engine.current_target.code, "green")
            self.next_question()
        else:
            self.score_label.setText(f"Score: {self.engine.score} | Incorrect!")
            self.guess_input.clear()

    def show_hint(self):
        hint = self.engine.get_hint()
        QMessageBox.information(self, "Hint", hint)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())