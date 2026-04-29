import random

class GameEngine:
    def __init__(self, countries_list):
        # Initialize GameEngine with the source data and core state variables
        self.countries_list = countries_list
        self.guessed_countries = set()  # A set to track guessed countries
        self.current_target = None
        self.score = 0
        self.time_left = 60 # Placeholder for time-based mode
        
    def start_shape_quiz(self):
        # Select a random country that hasn't been guessed yet.
        # Create a list of countries not in the guessed_countries set
        available_countries = [
            country for country in self.countries_list 
            if country.name not in self.guessed_countries
        ]
        
        if not available_countries:
            self.current_target = None
            return None # all countries have been guessed
            
        # Randomly select country from the remaining countries
        self.current_target = random.choice(available_countries)
        return self.current_target

    def check_answer(self, guess_text):
        # Compare the user's string input with self.current_target.name
        if self.current_target is None:
            return False
            
        # Case-insensitive comparison and stripping whitespace
        target_name = self.current_target.name.strip().lower()
        user_guess = guess_text.strip().lower()
        
        if user_guess == target_name:
            # Prevent duplicate selections
            self.guessed_countries.add(self.current_target.name)
            self.score += 10 # placeholder scoring
            return True
            
        return False

    def get_hint(self):
        # Return one info from the current_target
        if self.current_target is None:
            return "No active country to guess."
        
        return f"The capital of this country is {self.current_target.capital}."