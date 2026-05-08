import random
import json
import os

class GameEngine:
    def __init__(self, countries_list):
        # Initialize GameEngine with the source data and core state variables
        self.countries_list = countries_list
        self.current_mode = None  # Track which mode the user is currently playing
        self.current_target = None
        self.score = 0
        self.time_left = 120
        self.session_queue = [] # remaining countries for shape quiz
        self.cca3_lookup = {c.cca3: c.name for c in countries_list if hasattr(c, 'cca3')} # convert code to normal name
        self.failed_attempts = 0

        # Track progress separately for each game mode
        self.progress = {
            'explore': set(),
            'shape': set(),
            'time': set(),
            'flag': set()
        }

        # State variables
        self.total_distance = 0.0
        self.previous_target = None
        self.continent_mastery = {'explore': {}, 'shape': {}, 'time': {}, 'flag': {}}
        self.guessed_countries = {'explore': set(), 'shape': set(), 'time': set(), 'flag': set()}
        
        # Load permanent user data on initialization
        self.load_userdata()

    def set_mode(self, mode_name):
        # Updates the engine's current mode.
        if mode_name in self.progress:
            self.current_mode = mode_name
            self.current_target = None
            self.score = 0
            
            if mode_name == 'time':
                self.time_left = 120
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

        self.previous_target = None # reset previous target
        return self.next_quiz_target()

    def next_quiz_target(self):
        # Pop the next country from the queue
        if not self.session_queue:
            self.current_target = None
            return None # All countries guessed
            
        self.current_target = self.session_queue.pop()
        self.failed_attempts = 0
        return self.current_target
    
    def calculate_levenshtein(self, s1, s2):
        # Calculate Levenshtein distance between two strings
        if len(s1) < len(s2):
            return self.calculate_levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
            
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]
    
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
            distance = self.calculate_levenshtein(user_guess, target_name)
            threshold = 2
            if distance <= threshold:
                is_correct = True

        if is_correct:
            # Prevent duplicate selections
            self.progress[self.current_mode].add(self.current_target.name)
            self.score += 10 # placeholder scoring

            # Update mastery level
            region = getattr(self.current_target, 'region', 'Unknown')
            mode = self.current_mode
            self.continent_mastery[mode][region] = self.continent_mastery[mode].get(region, 0) + 1
            self.guessed_countries[mode].add(self.current_target.code)
            
            # Update distance traveled
            if self.previous_target:
                distance = self.previous_target.get_distance_to(self.current_target)
                self.total_distance += distance
                
            self.previous_target = self.current_target
            
            # Save the updated progress to JSON
            self.save_userdata()
            return True
        
        self.failed_attempts += 1
        return False

    def get_hint(self):
        if self.current_target is None:
            return "No active country to guess."
        
        if self.current_mode == 'time' or self.current_mode == 'shape':
            hint_text = ""            
            if not self.current_target.capital or self.current_target.capital == "N/A":
                hint_text += "Capital: No capital"
            else:
                hint_text += f"Capital: {self.current_target.capital}\n"

            hint_text += f"Region: {self.current_target.region}\n"

            if not self.current_target.borders:
                hint_text += "This is an island nation."
            else:
                neighbor_code = random.choice(self.current_target.borders)
                
                # Convert country code to common name
                neighbor_name = self.cca3_lookup.get(neighbor_code, neighbor_code)
                hint_text += f"Neighbor: {neighbor_name}"

            return hint_text.strip()
        
        elif self.current_mode == 'flag':
            if self.failed_attempts == 0:
                return "Try making a guess first"
                
            hint_text = ""
            
            # Hint 1
            if self.failed_attempts >= 1:
                hint_text += f"Region: {self.current_target.region}\n"
                
            # Hint 2
            if self.failed_attempts >= 2:
                if not self.current_target.capital or self.current_target.capital == "N/A":
                    hint_text += "This country doesn't have a capital"
                else:
                    hint_text += f"Capital: {self.current_target.capital}\n"
                
            # Hint 3
            if self.failed_attempts >= 3:
                if not self.current_target.borders:
                    hint_text += "This is an island nation.\n"
                else:
                    neighbor_code = random.choice(self.current_target.borders)
                    neighbor_name = self.cca3_lookup.get(neighbor_code, neighbor_code)
                    hint_text += f"Neighbor: {neighbor_name}\n"
                    
            return hint_text.strip()
    
    def get_progress_for_map(self, mode_name):
        # Return the list of explored countries for each mode
        if mode_name in self.progress:
            return list(self.progress[mode_name])
        return []
    
    def skip_target(self):
        if self.current_target:
            # Insert at index 0 so it gets popped last
            self.session_queue.insert(0, self.current_target)
            self.failed_attempts = 0
    
    def load_userdata(self):
        if os.path.exists('userdata.json'):
            try:
                with open('userdata.json', 'r') as f:
                    data = json.load(f)
                    self.total_distance = data.get('total_distance', 0.0)
                    
                    mastery = data.get('continent_mastery', {})
                    guessed = data.get('guessed_countries', {})
                    
                    # Catch old save files and migrate them to shape-based mode
                    if isinstance(guessed, list): 
                        self.guessed_countries['shape'] = set(guessed)
                        self.continent_mastery['shape'] = mastery
                    else:
                        self.continent_mastery = mastery
                        self.guessed_countries = {k: set(v) for k, v in guessed.items()}
            except Exception as e:
                print(f"Error loading userdata: {e}")

    def save_userdata(self):
        data = {
            'total_distance': self.total_distance,
            'continent_mastery': self.continent_mastery,
            'guessed_countries': {k: list(v) for k, v in self.guessed_countries.items()} 
        }
        try:
            with open('userdata.json', 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving userdata: {e}")

    def reset_all_progress(self):
        # clear saved progress
        self.total_distance = 0.0
        self.continent_mastery = {
            'explore': {}, 
            'shape': {}, 
            'time': {}, 
            'flag': {}
        }
        self.guessed_countries = {
            'explore': set(), 
            'shape': set(), 
            'time': set(), 
            'flag': set()
        }
        self.progress = {
            'explore': set(),
            'shape': set(),
            'time': set(),
            'flag': set()
        }
        self.score = 0
        self.save_userdata()