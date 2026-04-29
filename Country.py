import math

class Country:
    def __init__(self, name, capital, population, latlng, languages, currencies, area, code):
        self.name = name
        self.capital = capital
        self.population = population
        self.coordinate = tuple(latlng)  # (lat, long) for Haversine
        self.languages = languages
        self.currencies = currencies
        self.area = area
        self.code = code.lower()  # Matches SVG 'id' (e.g., 'dz')

    def get_info(self):
        # Returns a formatted string for the 'explore' mode
        lang_list = ", ".join(self.languages.values())
        curr_list = ", ".join([c['name'] for c in self.currencies.values()])
        return (f"Country: {self.name}\nCapital: {self.capital}\n"
                f"Population: {self.population:,}\nArea: {self.area:,} km²\n"
                f"Languages: {lang_list}\nCurrency: {curr_list}")

    def get_distance_to(self, other_country):
        # Haversine formula to calculate distance (km) between 2 countries
        # Earth radius (km)
        R = 6371.0 

        # Extract and convert coordinates to radians
        lat1 = math.radians(self.coordinate[0])
        lon1 = math.radians(self.coordinate[1])
        lat2 = math.radians(other_country.coordinate[0])
        lon2 = math.radians(other_country.coordinate[1])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Haversine formula
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance
    
    def __repr__(self):
        return f"Country({self.name}, {self.code})"