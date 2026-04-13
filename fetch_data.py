import requests
import json

# The endpoint to get ALL countries with the specific fields
URL = "https://restcountries.com/v3.1/all?fields=name,capital,population,languages,currencies,area,latlng,flags,region"

def fetch_and_save_data():
    try:
        print("Fetching data from API...")
        response = requests.get(URL)
        response.raise_for_status() # Check if the request was successful
        
        # The "Raw JSON" data
        data = response.json()
        
        # Save to project folder as countries.json
        with open('countries.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
        print(f"Successfully saved data for {len(data)} countries to countries.json!")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_and_save_data()