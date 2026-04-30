import random

class GameEngine:
    def __init__(self, countries_list):
        # Initialize GameEngine with the source data and core state variables
        self.countries_list = countries_list
        self.current_mode = None  # Track which mode the user is currently playing
        self.current_target = None
        self.score = 0
        self.time_left = 60 # Placeholder for time-based mode
        self.session_queue = [] # remaining countries for shape quiz

        # Track progress separately for each game mode
        self.progress = {
            'explore': set(),
            'shape': set(),
            'time': set(),
            'flag': set()
        }
    
    def set_mode(self, mode_name):
        # Updates the engine's current mode.
        if mode_name in self.progress:
            self.current_mode = mode_name
            self.current_target = None
            # Code to reset self.score or self.time_left (not sure)
            if mode_name == 'time':
                self.time_left = 60
            else:
                self.time_left = 0
        else:
            raise ValueError(f"Invalid game mode: {mode_name}")

    def explore_country(self, country_code):
        # Take the country code clicked on the map, mark explored, return
        # the Country object so the UI can display its info.
        self.set_mode('explore')
        
        # Find the country object using its code (since MapView clicks usually return codes)
        country = next((c for c in self.countries_list if c.code == country_code), None)
        
        if country:
            # Add to exploration progress for map painting
            self.progress['explore'].add(country.name)
            return country
            
        return None
    
    def start_quiz_session(self, mode_name):
        # initialize the queue for shape and flag mode
        self.set_mode(mode_name)

        available_countries = [
            country for country in self.countries_list 
            if country.name not in self.progress[mode_name]
        ]
        
        # Fisher-Yates randomize
        random.shuffle(available_countries)
        self.session_queue = available_countries
 
        return self.next_quiz_target()

    def next_quiz_target(self):
        # Pop the next country from the queue
        if not self.session_queue:
            self.current_target = None
            return None # All countries guessed
            
        self.current_target = self.session_queue.pop()
        return self.current_target
    
    def check_answer(self, guess_text):
        # Compare the user's string input with self.current_target.name
        if self.current_target is None or self.current_mode is None:
            return False
            
        # Case-insensitive comparison and stripping whitespace
        target_name = self.current_target.name.strip().lower()
        user_guess = guess_text.strip().lower()
        is_correct = False
        
        if user_guess == target_name:
            is_correct = True
        # Fuzzy match for Time Attack (Levenshtein distance)
        elif self.current_mode == 'time':
            pass 
            '''Levenshtein threshold (later)'''

        if is_correct:
            # Prevent duplicate selections
            self.progress[self.current_mode].add(self.current_target.name)
            self.score += 10 # placeholder scoring
            return True
            
        return False

    def get_hint(self):
        # Return one info from the current_target
        if self.current_target is None:
            return "No active country to guess."
        return f"The capital of this country is {self.current_target.capital}."
    
    def get_progress_for_map(self, mode_name):
        # Returns the list of explored countries for each mode
        if mode_name in self.progress:
            return list(self.progress[mode_name])
        return []