import json
import os
import requests

def fetch_flags(json_path, output_folder):
    # 1. Load the country data
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            countries = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_path} not found.")
        return

    print(f"Starting download for {len(countries)} flags...")

    # 2. Process each country
    for country in countries:
        # Get the cca3 code
        code = country.get('cca3', 'unknown').lower()
        
        # Get the PNG URL from the flags object
        flag_url = country.get('flags', {}).get('png')

        if not flag_url or code == 'unknown':
            print(f"Skipping {country.get('name', {}).get('common', 'Unknown')}: Missing data.")
            continue

        file_path = os.path.join(output_folder, f"{code}.png")

        # 3. Download and save the image
        try:
            response = requests.get(flag_url, stream=True)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"Successfully saved: {file_path}")
            else:
                print(f"Failed to download {code}: Status {response.status_code}")
        except Exception as e:
            print(f"Error downloading {code}: {e}")

    print("\ndone")

if __name__ == "__main__":
    fetch_flags('countries.json', 'flags')