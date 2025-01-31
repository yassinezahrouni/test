import json

# Load the JSON data from file
input_file = "Businesswire_NewsSources/cleaned_output_file.json"  # Replace with your actual filename
output_file = "Businesswire_NewsSources/businesswire_rss_links.json"

with open(input_file, "r", encoding="utf-8") as file:
    data = json.load(file)

# Filter out elements where "category" is empty, whitespace, or "Specific Categories"
filtered_data = [entry for entry in data if entry["category"].strip() and entry["category"] != "Specific Categories"]

# Write the cleaned data to a new file
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(filtered_data, file, indent=4, ensure_ascii=False)

print(f"Filtered data saved to {output_file}")

