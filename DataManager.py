import json
from Country import Country

class DataManager:
    def __init__(self):
        self.countries_list = []
        self.countries_dict = {}  # Key: iso_code from SVG, Value: Country object

    def load_from_json(self, path):
        # Parses the JSON file into Country objects
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for item in data:
                # Extracting data based on RestCountries API structure
                name = item.get('name', {}).get('common', 'Unknown')
                # Capital
                capital_list = item.get('capital', [])
                capital = capital_list[0] if capital_list else 'N/A'
                # Population
                population = item.get('population', 0)
                #Lat and Lon
                latlng = item.get('latlng', [0, 0])
                # Language
                languages = item.get('languages', {})
                #Currency
                currencies = item.get('currencies', {})
                # Area
                cca3 = item.get('cca3', '???')
                # Region
                region = item.get('region', {})
                # neighbor
                borders = item.get('borders', [])
                # Code
                flags = item.get('flags', {})
                svg_url = flags.get('svg', '')
                
                overrides = {
                    "Flag_of_the_Taliban": "af",
                    # the flag of afghanistan has a different structure
                }
                
                if svg_url:
                    # Extracts 'ki' from 'https://flagcdn.com/ki.svg'
                    code = svg_url.split('/')[-1].split('.')[0]
                    code = overrides.get(code, code).lower()
                else:
                    code = '??' # 2-letter code for SVG matching

                new_country = Country(name, capital, population, latlng, languages,
                                      currencies, cca3, region, borders, code)
                
                self.countries_list.append(new_country)
                self.countries_dict[new_country.code] = new_country
                
            print(f"Loaded {len(self.countries_list)} countries.")
        except Exception as e:
            print(f"Error loading JSON: {e}")

    def get_all_countries(self):
        return self.countries_list