from DataManager import DataManager

manager = DataManager()
manager.load_from_json('countries.json')

# Test O(1) Dictionary Lookup
switzerland = manager.countries_dict.get('ch')
if switzerland:
    print(switzerland.get_info())

# Test List for Game Logic
import random
random_country = random.choice(manager.get_all_countries())
print(f"\nRandomly selected for Shape Quiz: {random_country.name}")