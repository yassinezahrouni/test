import pandas as pd
import re

# File paths
input_file_path = "/Users/yassinezahrouni/coding/test/NewsData/20241215.export.CSV"
output_excel_path = "/Users/yassinezahrouni/coding/test/NewsData/20241215_extracted_links_full_countries_cities.xlsx"

# Predefined list of full country names (expand as needed)
full_countries = [
    "Rwanda", "Germany", "Canada", "Panama", "Nicaragua", "Congo", 
    "United Kingdom", "Belgium", "United States", "France"
]

# Predefined list of full city names (expand as needed)
full_cities = [
    "Waterloo", "London", "Panama City", "New York", "Berlin", "Kigali", "Kinshasa", "Toronto"
]

# Regular expression to match URLs
url_pattern = r'https?://[^\s]+'  # Matches anything starting with http/https until whitespace

# Initialize a list to store the extracted data
extracted_data = []

# Read the input file line by line
with open(input_file_path, "r") as file:
    for line in file:
        # Extract the URL
        urls = re.findall(url_pattern, line)
        url = urls[0] if urls else "No URL Found"
        
        # Extract full country names
        found_countries = [country for country in full_countries if country in line]
        country_list = ", ".join(found_countries) if found_countries else "No Country Found"
        
        # Extract full city names
        found_cities = [city for city in full_cities if city in line]
        city_list = ", ".join(found_cities) if found_cities else "No City Found"
        
        # Append the extracted data
        extracted_data.append({"URL": url, "Countries": country_list, "Cities": city_list})

# Create a DataFrame from the extracted data
df = pd.DataFrame(extracted_data)

# Save the DataFrame to an Excel file
df.to_excel(output_excel_path, index=False, engine="openpyxl")

print(f"Data successfully extracted and saved to: {output_excel_path}")
