import requests
import time
import re
from bs4 import BeautifulSoup

# Provided API key for the Directions API
API_KEY = "AIzaSyDxz5uhfKwQBAAyeafBw8-aZdyGvxd-Mxk"

# Define the origin and destination addresses
origin = "Port of Hamburg, Hamburg"
destination = "Allach-Untermenzing, Munich"
mode = "driving"  # Use driving mode for car routes

# Specify departure time (as a Unix timestamp); here we use the current time
departure_time = int(time.time())

# Google Maps Directions API endpoint
url = "https://maps.googleapis.com/maps/api/directions/json"

# Set up the API parameters including departure_time and traffic_model
params = {
    "origin": origin,
    "destination": destination,
    "mode": mode,
    "departure_time": departure_time,
    "traffic_model": "best_guess",  # Optional: can be optimistic, pessimistic, or best_guess
    "key": API_KEY
}

# Make the GET request to the Directions API
response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    if data["status"] == "OK":
        route = data["routes"][0]
        route_summary = route.get("summary", "No summary provided")
        print("Route Summary:", route_summary)
        
        # Print warnings if present
        warnings = route.get("warnings", [])
        if warnings:
            print("\nRoute Warnings:")
            for warning in warnings:
                print(" -", warning)
        else:
            print("\nNo route warnings.")
        
        # Extract overall leg details
        leg = route["legs"][0]
        overall_distance = leg["distance"]["text"]
        overall_duration = leg["duration"]["text"]
        print("\nOverall Distance:", overall_distance)
        print("Overall Duration:", overall_duration)
        print("\nDetailed Steps:")
        
        # Initialize a set to collect unique important road phrases.
        extracted_phrases = set()
        
        # Regex pattern to capture any word starting with A followed by digits,
        # and optionally followed by one or more spaces and a "toward" clause.
        # This pattern will capture either just the road (e.g., "A9") or 
        # "A9 toward München/Erfurt" if present.
        pattern = re.compile(r'\b(A\d+(?:\s+toward\s+[A-Za-z0-9\/\s-]+)?)\b')
        
        for step in leg["steps"]:
            instruction_html = step["html_instructions"]
            soup = BeautifulSoup(instruction_html, "html.parser")
            instruction_text = soup.get_text()
            distance_text = step["distance"]["text"]
            duration_text = step["duration"]["text"]
            print(f" - {instruction_text} (Distance: {distance_text}, Duration: {duration_text})")
            
            matches = pattern.findall(instruction_text)
            for match in matches:
                # Clean up the captured phrase
                extracted_phrases.add(match.strip())
        
        # Print out the unique extracted important road phrases
        print("\nExtracted Important Ways:")
        if extracted_phrases:
            for phrase in sorted(extracted_phrases):
                print(" -", phrase)
        else:
            print("No important ways extracted.")
    else:
        print("Error in API response:", data["status"])
        if "error_message" in data:
            print("Error Message:", data["error_message"])
else:
    print("HTTP Error:", response.status_code)
