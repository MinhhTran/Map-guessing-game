import sys
from PyQt6.QtWidgets import (QMainWindow, QApplication, QVBoxLayout, QWidget,
                             QLabel, QHBoxLayout, QLineEdit, QPushButton)
from PyQt6.QtCore import Qt
from DataManager import DataManager
from MapView import MapView
from GameEngine import GameEngine

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map Guessing Game - World Explorer")
        self.resize(1280, 960)
        
        # 1. Initialize Data
        self.data_manager = DataManager()
        self.data_manager.load_from_json('countries.json')
        countries = self.data_manager.countries_dict

        # Initialize Game Engine with a list of country objects
        self.engine = GameEngine(list(countries.values()))
        
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
        self.map_view.render_map(countries)
        self.layout.addWidget(self.map_view)

        # 4. Setup Quiz UI Controls (Hidden by default in Explore Mode)
        self.quiz_layout = QHBoxLayout()

        self.guess_input = QLineEdit()
        self.guess_input.setPlaceholderText("Type country name here...")
        # Pressing Enter in the line edit triggers the submit function
        self.guess_input.returnPressed.connect(self.on_guess_submitted)
        
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.on_guess_submitted)
        
        self.hint_btn = QPushButton("Hint")
        self.hint_btn.clicked.connect(self.on_hint_clicked)
        
        # Add widgets to the horizontal layout
        self.quiz_layout.addWidget(self.guess_input)
        self.quiz_layout.addWidget(self.submit_btn)
        self.quiz_layout.addWidget(self.hint_btn)
        
        # Add a button to switch from Explore to Quiz mode
        self.start_quiz_btn = QPushButton("Start Shape Quiz")
        self.start_quiz_btn.clicked.connect(self.setup_quiz_ui)
        self.layout.addWidget(self.start_quiz_btn)
        
        # Add the quiz layout to the main vertical layout
        self.layout.addLayout(self.quiz_layout)
        
        # Initially hide the quiz-specific controls
        self.guess_input.hide()
        self.submit_btn.hide()
        self.hint_btn.hide()

    def setup_quiz_ui(self):
        # Hide 'explore info and show 'quiz' control
        # Hide the mode switch button and update the label
        self.start_quiz_btn.hide()
        self.label.setText("Shape Quiz Mode: Guess the country!")
        
        # Show the quiz controls
        self.guess_input.show()
        self.submit_btn.show()
        self.hint_btn.show()
        
        # Start the first question
        self.next_question()

    def next_question(self):
        # Fetch the next country for quiz
        target = self.engine.start_shape_quiz()
        if target:
            self.label.setText(f"Score: {self.engine.score} | Guess the country!")
        else:
            self.label.setText(f"Quiz Complete! Final Score: {self.engine.score}")
            self.guess_input.hide()
            self.submit_btn.hide()
            self.hint_btn.hide()

    def on_guess_submitted(self):
        # when the user hit 'enter' or click 'submit'
        guess_text = self.guess_input.text()
        if not guess_text:
            return  # Ignore empty submissions
            
        is_correct = self.engine.check_answer(guess_text)
        
        if is_correct:
            #highlight the country
            self.map_view.highlight_country(self.engine.current_target.code, "green")

            self.guess_input.clear()
            self.next_question()
        else:
            self.label.setText(f"Score: {self.engine.score} | Incorrect guess. Try again!")
            self.guess_input.clear()

    def on_hint_clicked(self):
        # for when the user click 'hint'
        hint_text = self.engine.get_hint()
        self.label.setText(f"Score: {self.engine.score} | Hint: {hint_text}")
    
    def resizeEvent(self, event):
        #Ensure the map resizes dynamically when the window changes size
        super().resizeEvent(event)
        if hasattr(self, 'map_view') and self.map_view.scene.items():
            self.map_view.fitInView(self.map_view.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())