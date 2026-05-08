import unittest
import os
from GameEngine import GameEngine
from DataManager import DataManager

# Mock Country class to simulate data loading without needing the actual JSON or country.py
class MockCountry:
    def __init__(self, name, code, capital, region, cca3=""):
        self.name = name
        self.code = code
        self.capital = capital
        self.region = region
        self.cca3 = cca3
        self.borders = []

    def get_distance_to(self, other_country):
        # Mock Haversine distance return
        return 500.0

class TestMapGuessingGame(unittest.TestCase):

    def setUp(self):
        # Set up a controlled dataset for testing the game logic
        self.finland = MockCountry("Finland", "fi", "Helsinki", "Europe", "FIN")
        self.sweden = MockCountry("Sweden", "se", "Stockholm", "Europe", "SWE")
        self.czech = MockCountry("Czech Republic", "cz", "Prague", "Europe", "CZE")
        
        self.mock_countries = [self.finland, self.sweden, self.czech]
        
        # Initialize the GameEngine with mock data
        self.engine = GameEngine(self.mock_countries)

    def test_levenshtein_distance(self):
        # Test fuzzy string matching algorithm
        dist_exact = self.engine.calculate_levenshtein("finland", "finland")
        self.assertEqual(dist_exact, 0)
        
        dist_one_typo = self.engine.calculate_levenshtein("finlnd", "finland")
        self.assertEqual(dist_one_typo, 1)

        dist_two_typos = self.engine.calculate_levenshtein("filand", "finland")
        self.assertEqual(dist_two_typos, 1)
        
        dist_far = self.engine.calculate_levenshtein("sweden", "finland")
        self.assertGreater(dist_far, 2)

    def test_check_answer_exact_match(self):
        # Test basic shape mode where exact/case-insensitive match is required[cite: 1, 3]
        self.engine.set_mode('shape')
        self.engine.current_target = self.finland
        
        # Correct guess (case-insensitive and whitespace stripped)
        self.assertTrue(self.engine.check_answer("Finland"))
        self.assertTrue(self.engine.check_answer("  finland  "))
        
        # Incorrect guess
        self.assertFalse(self.engine.check_answer("Finlnd")) # Fails because threshold isn't active in shape mode
        self.assertFalse(self.engine.check_answer("Sweden"))

    def test_check_answer_fuzzy_match(self):
        # Test Time Attack mode which uses a Levenshtein distance threshold of 2[cite: 1, 3]
        self.engine.set_mode('time')
        self.engine.current_target = self.finland
        
        # Correct guesses within threshold[cite: 3]
        self.assertTrue(self.engine.check_answer("finland"))  # 0 distance
        
        self.engine.current_target = self.finland 
        self.assertTrue(self.engine.check_answer("finlnd"))   # 1 distance
        
        # Incorrect guess exceeding threshold
        self.engine.current_target = self.finland 
        self.assertFalse(self.engine.check_answer("fiiiinland")) # > 2 distance

    def test_boundary_special_characters(self):
        # Boundary test: Test countries with special names (e.g., two words)
        self.engine.set_mode('shape')
        self.engine.current_target = self.czech
        
        self.assertTrue(self.engine.check_answer("Czech Republic"))
        self.assertTrue(self.engine.check_answer("czech republic"))
        self.assertFalse(self.engine.check_answer("CzechRepublic"))

    def test_timer_initialization(self):
        # Verify that the timer properly initializes to 120s for Time Attack[cite: 1, 3]
        self.engine.set_mode('time')
        self.assertEqual(self.engine.time_left, 120)

    def test_data_manager_crash_prevention(self):
        # Test DataManager to prevent crashes if JSON fails
        data_manager = DataManager()
        data_manager.load_from_json('invalid_path.json')

        # DataManager creates an empty dictionary if it fails
        self.assertEqual(data_manager.countries_dict, {})

if __name__ == '__main__':
    unittest.main()