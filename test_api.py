import requests
import os
from dotenv import load_dotenv

load_dotenv()
NASA_API_KEY = os.getenv("API_KEY")

url = "https://api.nasa.gov/neo/rest/v1/feed"

params = {
    "start_date": '2025-11-11',
    "end_date": '2025-11-12',
    "api_key": NASA_API_KEY,
}

resp = requests.get(url, params=params)

data = resp.json()

# print(data.keys())

# print(data["near_earth_objects"]["2025-11-11"][0].keys())

# print(data["near_earth_objects"]["2025-11-11"][0]['close_approach_data'][0].keys())

# print(data["near_earth_objects"]["2025-11-11"][0]['close_approach_data'][0]['miss_distance']['astronomical'])
print(resp.raise_for_status())

# print(data["near_earth_objects"]["2025-11-11"][0])