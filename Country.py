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
        """Returns a formatted string for the 'Explore' mode[cite: 48]."""
        lang_list = ", ".join(self.languages.values())
        curr_list = ", ".join([c['name'] for c in self.currencies.values()])
        return (f"Country: {self.name}\nCapital: {self.capital}\n"
                f"Population: {self.population:,}\nArea: {self.area:,} km²\n"
                f"Languages: {lang_list}\nCurrency: {curr_list}")

    def __repr__(self):
        return f"Country({self.name}, {self.code})"