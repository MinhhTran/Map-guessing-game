import sys
from PyQt6.QtWidgets import (QMainWindow, QApplication, QVBoxLayout, QWidget,
                             QLabel, QHBoxLayout, QLineEdit, QPushButton,
                             QStackedWidget, QDialog, QMessageBox)
from PyQt6.QtCore import Qt
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
        countries = self.data_manager.countries_dict
        self.engine = GameEngine(list(countries.values()))
        
        # 2. Main Layout using QStackedWidget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create the different screens
        self.init_main_menu()
        self.init_game_screen(countries)
        
        # Add screens to the stack
        self.stacked_widget.addWidget(self.menu_widget) # Index 0
        self.stacked_widget.addWidget(self.game_widget) # Index 1

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

    def init_game_screen(self, countries):
        # Create the screen containing the map and the back button
        self.game_widget = QWidget()
        layout = QVBoxLayout(self.game_widget)
        
        # Top bar with a Back Button
        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Back to Menu")
        back_btn.setFixedWidth(150)
        back_btn.clicked.connect(self.go_to_menu)
        
        self.mode_label = QLabel("Mode: None")
        
        top_bar.addWidget(back_btn)
        top_bar.addWidget(self.mode_label)
        top_bar.addStretch()
        layout.addLayout(top_bar)
        
        # Add Map View
        self.map_view = MapView()
        self.map_view.render_map(countries)
        layout.addWidget(self.map_view)
        
        # (In progress) Connect the MapView's click event to MainWindow.
        # Add a custom signal to MapView later called 'country_clicked':
        # self.map_view.country_clicked.connect(self.on_map_clicked)

    def start_mode(self, mode_name):
        # Switche to the map screen and set up the chosen mode
        self.engine.set_mode(mode_name)
        self.mode_label.setText(f"Current Mode: {mode_name.capitalize()}")
        
        # Switch the UI to the map screen (Index 1)
        self.stacked_widget.setCurrentIndex(1)
        
        # (in progress): Refresh map colors based on self.engine.get_progress_for_map(mode_name)
        
        if mode_name == 'shape':
            # Launch the pop-up window for the shape quiz
            self.shape_dialog = ShapeQuizDialog(self, self.engine, self.map_view)
            self.shape_dialog.show()

    def go_to_menu(self):
        # Return to the main menu screen
        self.stacked_widget.setCurrentIndex(0)

    def on_map_clicked(self, country_code):
        # handle what happens when a country is clicked
        if self.engine.current_mode == 'explore':
            country_data = self.engine.explore_country(country_code)
            if country_data:
                # Paint the country on the map
                self.map_view.highlight_country(country_code, "blue")
                
                # Show the pop-up information window
                info_text = (
                    f"Name: {country_data.name}\n"
                    f"Capital: {country_data.capital}\n"
                    f"Population: {country_data.population:,}\n"
                    f"Area: {country_data.area:,.0f} km²"
                )
                QMessageBox.information(self, "Country Discovered!", info_text)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'map_view') and self.map_view.scene.items():
            self.map_view.fitInView(self.map_view.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

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

        # Placeholder for where the Shape (SVG) would be rendered
        self.shape_label = QLabel("(Country Shape goes here)")
        self.shape_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.shape_label)
        
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

        self.next_question()

    def next_question(self):
        target = self.engine.start_shape_quiz()
        if target:
            self.score_label.setText(f"Score: {self.engine.score}")
            self.shape_label.setText(f"Guess this shape! (Code: {target.code})")
            self.guess_input.clear()
        else:
            QMessageBox.information(self, "Quiz Over", f"You finished the quiz! Final Score: {self.engine.score}")
            self.accept() # Close the dialog

    def submit_guess(self):
        guess_text = self.guess_input.text()
        if not guess_text:
            return
            
        if self.engine.check_answer(guess_text):
            # Correct! Update map and get next question
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