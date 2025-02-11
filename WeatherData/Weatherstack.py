import requests
import json

# Replace with your actual Weatherstack API key
api_key = "59b6cb4f4b24169cc1f71ea75d4fede4"
base_url = "http://api.weatherstack.com/forecast"

# Define the parameters for the API call
params = {
    "access_key": api_key,
    "query": "Munich",
    "forecast_days": 7
}

# Make the API request
response = requests.get(base_url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    # Print the forecast in a formatted manner
    print(json.dumps(data, indent=4))
else:
    print(f"Error: Unable to fetch data, status code {response.status_code}")
