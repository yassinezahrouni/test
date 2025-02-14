
import requests
import re
from bs4 import BeautifulSoup

# Provided API key for the Directions API
API_KEY = "AIzaSyBhgM9ucPG5vSqo7eqSE6MXp0GmTLPs-MQ"

# Define the origin and destination addresses
origin = "Port of Hamburg, Hamburg"
destination = "Allach-Untermenzing, Munich"
mode = "driving"  # using driving mode for car routes

# Google Maps Directions API endpoint
url = "https://maps.googleapis.com/maps/api/directions/json"

# Set up the API parameters
params = {
    "origin": origin,
    "destination": destination,
    "mode": mode,
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
        
        # Extract overall leg details
        leg = route["legs"][0]
        overall_distance = leg["distance"]["text"]
        overall_duration = leg["duration"]["text"]
        print("Overall Distance:", overall_distance)
        print("Overall Duration:", overall_duration)
        print("\nDetailed Steps:")
        
        # Initialize a list to collect the extracted road phrases
        extracted_phrases = []
        
        # Regex pattern:
        # \b - word boundary
        # (A\d+ matches A followed by one or more digits)
        # (?:\s+toward\s+[A-Za-z0-9\/\s-]+)? - optionally, one or more spaces, then "toward", then additional words/numbers (e.g., "München/Erfurt")
        # \b - word boundary at the end
        pattern = re.compile(r'\b(A\d+(?:\s+toward\s+[A-Za-z0-9\/\s-]+)?)\b')
        
        # Process each step in the leg
        for step in leg["steps"]:
            instruction_html = step["html_instructions"]
            soup = BeautifulSoup(instruction_html, "html.parser")
            instruction_text = soup.get_text()
            distance_text = step["distance"]["text"]
            duration_text = step["duration"]["text"]
            print(f" - {instruction_text} (Distance: {distance_text}, Duration: {duration_text})")
            
            # Apply the regex to extract matching phrases
            matches = pattern.findall(instruction_text)
            for match in matches:
                # Strip extra whitespace
                cleaned = match.strip()
                extracted_phrases.append(cleaned)
        
        # Remove duplicates while preserving order
        unique_phrases = []
        seen = set()
        for phrase in extracted_phrases:
            if phrase not in seen:
                unique_phrases.append(phrase)
                seen.add(phrase)
        
        # Print out the unique extracted road identifiers (important ways)
        print("\nExtracted Important Ways:")
        if unique_phrases:
            for phrase in unique_phrases:
                print(" -", phrase)
        else:
            print("No important ways extracted.")
    else:
        print("Error in API response:", data["status"])
        if "error_message" in data:
            print("Error Message:", data["error_message"])
else:
    print("HTTP Error:", response.status_code)
