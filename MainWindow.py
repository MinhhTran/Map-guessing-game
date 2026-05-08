import sys
from PyQt6.QtWidgets import (QMainWindow, QApplication, QVBoxLayout, QWidget,
                             QLabel, QHBoxLayout, QLineEdit, QPushButton,
                             QStackedWidget, QDialog, QMessageBox, QGraphicsView,
                             QGraphicsScene, QGraphicsPathItem)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QBrush, QPen, QPixmap
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
        self.explore_map_view.country_clicked.connect(self.on_map_clicked)
        
        self.shape_map_view = MapView()
        self.shape_map_view.render_map(countries_dict)
        self.shape_map_view.country_clicked.connect(self.on_map_clicked)

        self.time_map_view = MapView()
        self.time_map_view.render_map(countries_dict)
        self.time_map_view.country_clicked.connect(self.on_map_clicked)

        self.flag_map_view = MapView()
        self.flag_map_view.render_map(countries_dict)
        self.flag_map_view.country_clicked.connect(self.on_map_clicked)

        # 4. Initialize the quiz to save state
        self.shape_dialog = ShapeQuizDialog(self, self.engine, self.shape_map_view)
        self.time_attack_dialog = TimeAttackDialog(self, self.engine, self.time_map_view)
        self.flag_dialog = FlagQuizDialog(self, self.engine, self.flag_map_view)

        # for time attack mode
        self.time_attack_timer = QTimer(self)
        self.time_attack_timer.timeout.connect(self.update_timer)

        # 5. Create the different screens
        self.init_main_menu()
        self.init_explore_screen()
        self.init_shape_screen()
        self.init_time_screen()
        self.init_flag_screen()
        
        # 6. Add screens to the stack
        self.stacked_widget.addWidget(self.menu_widget) # Index 0
        self.stacked_widget.addWidget(self.explore_widget) # Index 1
        self.stacked_widget.addWidget(self.shape_widget) # Index 2
        self.stacked_widget.addWidget(self.time_widget) # Index 3
        self.stacked_widget.addWidget(self.flag_widget) # Index 4

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
        
        btn_time = QPushButton("Time Attack")
        btn_time.clicked.connect(lambda: self.start_mode('time'))
        
        btn_flag = QPushButton("Flag Master")
        btn_flag.clicked.connect(lambda: self.start_mode('flag'))

        btn_reset = QPushButton("Reset All Progress")
        btn_reset.clicked.connect(self.trigger_progress_reset)
        
        # Add buttons to menu layout
        for btn in [btn_explore, btn_shape, btn_time, btn_flag, btn_reset]:
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
        
        # Button to re-open the hidden quiz dialog
        show_quiz_btn = QPushButton("Show Quiz Window")
        show_quiz_btn.clicked.connect(self.show_current_quiz_dialog)
        
        top_bar.addWidget(back_btn)
        top_bar.addWidget(QLabel("Mode: Shape Quiz"))
        top_bar.addWidget(show_quiz_btn)
        top_bar.addStretch()
        
        layout.addLayout(top_bar)
        layout.addWidget(self.shape_map_view) # Add the Shape Map

    def init_flag_screen(self):
        self.flag_widget = QWidget()
        layout = QVBoxLayout(self.flag_widget)
        
        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Back to Menu")
        back_btn.clicked.connect(self.go_to_menu)
        
        show_quiz_btn = QPushButton("Show Quiz Window")
        show_quiz_btn.clicked.connect(self.show_current_quiz_dialog)
        
        top_bar.addWidget(back_btn)
        top_bar.addWidget(QLabel("Mode: Flag Master"))
        top_bar.addWidget(show_quiz_btn)
        top_bar.addStretch()
        
        layout.addLayout(top_bar)
        layout.addWidget(self.flag_map_view)

    def start_mode(self, mode_name):
        # Switch to the map screen and set up the chosen mode
        if mode_name == 'explore':
            self.engine.set_mode('explore')
            self.stacked_widget.setCurrentIndex(1)
            QTimer.singleShot(0, self.fit_maps_in_view)
            self.explore_map_view.update_heatmap(self.engine.continent_mastery['explore'], self.engine.guessed_countries['explore'])

        elif mode_name == 'shape':
            # Initialize the shuffled queue in the engine
            self.engine.start_quiz_session('shape')
            self.stacked_widget.setCurrentIndex(2)
            QTimer.singleShot(0, self.fit_maps_in_view)
            self.shape_map_view.update_heatmap(self.engine.continent_mastery['shape'], self.engine.guessed_countries['shape'])
            
            # Start the first question and show the dialog
            self.shape_dialog.next_question()
            self.shape_dialog.show()
        
        elif mode_name == 'time':
            self.engine.start_quiz_session('time')
            self.stacked_widget.setCurrentIndex(3)
            QTimer.singleShot(0, self.fit_maps_in_view)

            self.time_map_view.update_heatmap(self.engine.continent_mastery['time'], self.engine.guessed_countries['time'])
            self.restart_time_attack()
            
            # Reset and start the time attack mode
            self.time_attack_dialog.guess_input.setEnabled(True)
            self.time_attack_dialog.info_label.setText("")
            self.time_attack_dialog.next_question()
            self.time_attack_dialog.show()
            
            # Start the 120s timer
            self.engine.time_left = 120
            self.time_attack_dialog.update_time_label(self.engine.time_left)
            self.time_attack_timer.start(1000) # Decrement every 10s

        elif mode_name == 'flag':
            self.engine.start_quiz_session('flag')
            self.stacked_widget.setCurrentIndex(4)
            QTimer.singleShot(0, self.fit_maps_in_view)
            self.flag_map_view.update_heatmap(self.engine.continent_mastery['flag'], self.engine.guessed_countries['flag'])
            
            self.flag_dialog.next_question()
            self.flag_dialog.show()

    def go_to_menu(self):
        # Return to the main menu screen
        self.stacked_widget.setCurrentIndex(0)
        if hasattr(self, 'shape_dialog'):
            self.shape_dialog.hide()
            
        if hasattr(self, 'time_attack_dialog'):
            self.time_attack_dialog.hide()

        if hasattr(self, 'time_attack_timer') and self.time_attack_timer.isActive():
            self.time_attack_timer.stop()
            self.engine.score = 0
            self.engine.time_left = 120
            self.engine.session_queue.clear()

        if hasattr(self, 'flag_dialog'):
            self.flag_dialog.hide()

        self.engine.current_mode = None
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
                    f"Country: {country_data.name}\n"
                )

                if not country_data.capital or country_data.capital == "N/A":
                    info_text += "Capital: No capital\n"
                else:
                    info_text += f"Capital: {country_data.capital}\n"
                
                info_text += f"Population: {country_data.population}\n"

                if not country_data.currencies:
                    info_text += "Currency: No currency\n"
                else:
                    info_text += f"Currencies: {country_data.currencies}\n"

                if not country_data.languages:
                    info_text += "Language: No language\n"
                else:
                    info_text += f"Languages: {country_data.languages}\n"

                info_text += f"Country code: {country_data.cca3}\n"

                QTimer.singleShot(200, lambda: QMessageBox.information(self, "Country Discovered!", info_text))

    def fit_maps_in_view(self):
        if hasattr(self, 'explore_map_view') and self.explore_map_view.scene.items():
            self.explore_map_view.fitInView(self.explore_map_view.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

        if hasattr(self, 'shape_map_view') and self.shape_map_view.scene.items():
            self.shape_map_view.fitInView(self.shape_map_view.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

        if hasattr(self, 'flag_map_view') and self.flag_map_view.scene.items():
            self.flag_map_view.fitInView(self.flag_map_view.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

        if hasattr(self, 'time_map_view') and self.time_map_view.scene.items():
            self.time_map_view.fitInView(self.time_map_view.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fit_maps_in_view()

    def trigger_progress_reset(self):
        # Double check with the user
        reply = QMessageBox.question(self, 'Reset Progress', 
                                     'Are you sure?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.engine.reset_all_progress()
            
            # Render the map again to clear the progress
            countries_dict = self.data_manager.countries_dict
            
            self.explore_map_view.scene.clear()
            self.explore_map_view.render_map(countries_dict)
            
            self.shape_map_view.scene.clear()
            self.shape_map_view.render_map(countries_dict)

            self.time_map_view.scene.clear()
            self.time_map_view.render_map(countries_dict)

            self.flag_map_view.scene.clear()
            self.flag_map_view.render_map(countries_dict)
            
            QMessageBox.information(self, "Success", "All progress has been reset!")

    def update_timer(self):
        # Decrement the timer every second (time attack mode)
        self.engine.time_left -= 1
        
        if self.time_attack_dialog.isVisible():
            self.time_attack_dialog.update_time_label(self.engine.time_left)
            
        if self.engine.time_left <= 0:
            self.time_attack_timer.stop()
            self.time_attack_dialog.end_game()

    def show_current_quiz_dialog(self):
        # Open quiz window based on the current game mode
        if self.engine.current_mode == 'shape':
            self.shape_dialog.show()
        elif self.engine.current_mode == 'time':
            self.time_attack_dialog.show()
        elif self.engine.current_mode == 'flag':
            self.flag_dialog.show()

    def init_time_screen(self):
        self.time_widget = QWidget()
        layout = QVBoxLayout(self.time_widget)
        
        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Back to Menu")
        back_btn.clicked.connect(self.go_to_menu)
        
        show_quiz_btn = QPushButton("Show Quiz Window")
        show_quiz_btn.clicked.connect(self.time_attack_dialog.show)
        
        restart_btn = QPushButton("Restart Time Attack")
        restart_btn.clicked.connect(self.restart_time_attack)
        
        top_bar.addWidget(back_btn)
        top_bar.addWidget(QLabel("Mode: Time Attack"))
        top_bar.addWidget(show_quiz_btn)
        top_bar.addWidget(restart_btn)
        top_bar.addStretch()
        
        layout.addLayout(top_bar)
        layout.addWidget(self.time_map_view) 

    def restart_time_attack(self):
        # Reset the timer, score, and create new quiz
        self.time_attack_timer.stop()
        
        self.engine.score = 0
        self.engine.time_left = 120
        self.engine.start_quiz_session('time')
        
        # Reset the dialog UI
        self.time_attack_dialog.guess_input.setEnabled(True)
        self.time_attack_dialog.submit_btn.setEnabled(True)
        self.time_attack_dialog.hint_btn.setEnabled(True)
        self.time_attack_dialog.info_label.setText("Game Restarted")
        self.time_attack_dialog.info_label.setStyleSheet("color: blue; font-weight: bold;")
        
        self.time_attack_dialog.update_time_label(self.engine.time_left)
        self.time_attack_dialog.next_question()
        self.time_attack_dialog.show()
        
        self.time_attack_timer.start(1000)

class ShapeQuizDialog(QDialog):
    # Pop-up window for the shape quiz
    def __init__(self, parent=None, engine=None, map_view=None):
        super().__init__(parent)
        self.engine = engine
        self.map_view = map_view
        self.setWindowTitle("Shape Quiz")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        self.score_label = QLabel(f"Score: {self.engine.score}")
        layout.addWidget(self.score_label)

        self.distance_label = QLabel(f"Distance Traveled: {self.engine.total_distance:.1f} km")
        layout.addWidget(self.distance_label)

        self.shape_label = QLabel("Guess this shape")
        self.shape_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.shape_label)

        self.shape_scene = QGraphicsScene()
        self.shape_view = QGraphicsView(self.shape_scene)
        self.shape_view.setFixedSize(800, 500)
        #self.shape_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        #self.shape_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.shape_view.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
            shape_item.setBrush(QBrush(Qt.GlobalColor.green))
            #outline_pen = QPen(Qt.GlobalColor.black)
            #outline_pen.setWidth(0) # always 1 pixel wide
            #shape_item.setPen(outline_pen)
            shape_item.setPen(QPen(Qt.PenStyle.NoPen))
            self.shape_scene.addItem(shape_item)
        
            # Scale the view to fit the shape perfectly
            self.shape_scene.setSceneRect(shape_item.boundingRect())
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
            current_target = self.engine.current_target
            # self.map_view.highlight_country(current_target.code, green)
            self.map_view.update_heatmap(self.engine.continent_mastery[self.engine.current_mode],
                                         self.engine.guessed_countries[self.engine.current_mode])
            self.distance_label.setText(f"Distance Traveled: {self.engine.total_distance:.1f} km")
            
            reveal_text = (
                f"Country: {current_target.name}\n"
            )
            if not current_target.capital or current_target.capital == "N/A":
                reveal_text += "Capital: No capital\n"
            else:
                reveal_text += f"Capital: {current_target.capital}\n"
                
            reveal_text += f"Population: {current_target.population}\n"

            if not current_target.currencies:
                reveal_text += "Currency: No currency\n"
            else:
                reveal_text += f"Currencies: {current_target.currencies}\n"

            if not current_target.languages:
                reveal_text += "Language: No language\n"
            else:
                reveal_text += f"Languages: {current_target.languages}\n"

            reveal_text += f"Country code: {current_target.cca3}\n"

            QMessageBox.information(self, "Correct Answer!", reveal_text)
            self.next_question()
        else:
            self.score_label.setText(f"Score: {self.engine.score} | Incorrect!")
            self.guess_input.clear()

    def show_hint(self):
        hint = self.engine.get_hint()
        QMessageBox.information(self, "Hint", hint)

class TimeAttackDialog(QDialog):
    def __init__(self, parent=None, engine=None, map_view=None):
        super().__init__(parent)
        self.engine = engine
        self.map_view = map_view
        self.setWindowTitle("Time Attack!")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Header layout (timer and score)
        header_layout = QHBoxLayout()
        self.time_label = QLabel("Time Left: 120s")
        self.time_label.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
        self.score_label = QLabel(f"Score: {self.engine.score}")
        self.score_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        header_layout.addWidget(self.time_label)
        header_layout.addStretch()
        header_layout.addWidget(self.score_label)
        layout.addLayout(header_layout)
        
        # Shape viewer
        self.shape_label = QLabel("Guess this shape")
        self.shape_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.shape_label)
        
        self.shape_scene = QGraphicsScene()
        self.shape_view = QGraphicsView(self.shape_scene)
        self.shape_view.setFixedSize(800, 400)
        self.shape_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.shape_view)
        
        # Info label (Replace QMessageBox for fast pacing)
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.info_label)
        
        # Input field
        self.guess_input = QLineEdit()
        self.guess_input.setPlaceholderText("Type fast and hit Enter...")
        self.guess_input.returnPressed.connect(self.submit_guess)
        layout.addWidget(self.guess_input)

        # buttons
        btn_layout = QHBoxLayout()
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.submit_guess)
        
        self.hint_btn = QPushButton("Hint")
        self.hint_btn.clicked.connect(self.show_hint)
        
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.hint_btn)
        layout.addLayout(btn_layout)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
    
    def show_hint(self):
        hint = self.engine.get_hint()
        QMessageBox.information(self, "Hint", hint)

    def update_time_label(self, time_left):
        self.time_label.setText(f"Time Left: {time_left}s")

    def display_shape(self, country_path):
        self.shape_scene.clear()
        if country_path:
            shape_item = QGraphicsPathItem(country_path)
            shape_item.setBrush(QBrush(Qt.GlobalColor.green))
            shape_item.setPen(QPen(Qt.PenStyle.NoPen))
            self.shape_scene.addItem(shape_item)
            self.shape_scene.setSceneRect(shape_item.boundingRect())
            self.shape_view.fitInView(shape_item.boundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def next_question(self):
        target = self.engine.next_quiz_target()
        if target:
            self.score_label.setText(f"Score: {self.engine.score}")
            self.guess_input.clear()
            country_path = self.map_view.get_country_path(target.code)
            if country_path:
                self.display_shape(country_path)
        else:
            self.end_game()

    def submit_guess(self):
        guess_text = self.guess_input.text()
        if not guess_text: return
        
        if self.engine.check_answer(guess_text):
            current_target = self.engine.current_target
            # Highlight country in green on the main map
            self.map_view.highlight_country(current_target.code, "green")
            
            # Show info without blocking the UI
            self.info_label.setText(f"Correct! {current_target.name} - Capital: {current_target.capital}")
            self.next_question()
        else:
            self.info_label.setText("Keep trying!")
            self.info_label.setStyleSheet("color: orange; font-weight: bold;")
            self.guess_input.clear()
            
    def end_game(self):
        self.guess_input.setDisabled(True)
        self.submit_btn.setDisabled(True)
        self.hint_btn.setDisabled(True)
        QMessageBox.information(self, "Time's Up!", f"Game Over!\nFinal Score: {self.engine.score}")
        self.hide()

class FlagQuizDialog(QDialog):
    def __init__(self, parent=None, engine=None, map_view=None):
        super().__init__(parent)
        self.engine = engine
        self.map_view = map_view
        self.setWindowTitle("Flag Master Quiz")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        self.score_label = QLabel(f"Score: {self.engine.score}")
        layout.addWidget(self.score_label)
        self.distance_label = QLabel(f"Distance Traveled: {self.engine.total_distance:.1f} km")
        layout.addWidget(self.distance_label)
        
        self.instruction_label = QLabel("Guess the country from this flag!")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.instruction_label)
        
        # Use QLabel to display the flag image
        self.flag_label = QLabel()
        self.flag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.flag_label)
        
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
        event.ignore()
        self.hide()

    def display_flag(self, country_code):
        # Construct the path to the flag image using the country code
        flag_path = f"flags/{country_code.lower()}.png"
        pixmap = QPixmap(flag_path)
        
        if not pixmap.isNull():
            # Scale the image to fit nicely within the dialog
            pixmap = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.flag_label.setPixmap(pixmap)
        else:
            self.flag_label.setText(f"Flag image not found for code: {country_code}")

    def next_question(self):
        target = self.engine.next_quiz_target()
        if target:
            self.score_label.setText(f"Score: {self.engine.score}")
            self.guess_input.clear()
            self.display_flag(target.cca3)
        else:
            QMessageBox.information(self, "Quiz Over", f"You finished the quiz! Final Score: {self.engine.score}")
            self.hide()

    def submit_guess(self):
        guess_text = self.guess_input.text()
        if not guess_text:
            return
        
        if self.engine.check_answer(guess_text):
            current_target = self.engine.current_target
            self.map_view.update_heatmap(self.engine.continent_mastery[self.engine.current_mode],
                                         self.engine.guessed_countries[self.engine.current_mode])
            self.distance_label.setText(f"Distance Traveled: {self.engine.total_distance:.1f} km")
            
            reveal_text = (
                f"Country: {current_target.name}\n"
            )
            if not current_target.capital or current_target.capital == "N/A":
                reveal_text += "Capital: No capital\n"
            else:
                reveal_text += f"Capital: {current_target.capital}\n"
                
            reveal_text += f"Population: {current_target.population}\n"

            if not current_target.currencies:
                reveal_text += "Currency: No currency\n"
            else:
                reveal_text += f"Currencies: {current_target.currencies}\n"

            if not current_target.languages:
                reveal_text += "Language: No language\n"
            else:
                reveal_text += f"Languages: {current_target.languages}\n"

            reveal_text += f"Country code: {current_target.cca3}\n"

            QMessageBox.information(self, "Correct Answer!", reveal_text)
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