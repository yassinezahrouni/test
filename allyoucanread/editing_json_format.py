import json

# Load the JSON file
input_file = "allyoucanread/news_sources.json"
output_file = "allyoucanread/news_sources_adjusted.json"

# Read the original JSON data
with open(input_file, "r", encoding="utf-8") as file:
    news_data = json.load(file)

# Transform the data
adjusted_news_list = []
for country, newspapers in news_data.items():
    for newspaper in newspapers:
        newspaper["Country"] = country  # Add country field
        adjusted_news_list.append(newspaper)

# Save the adjusted JSON data
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(adjusted_news_list, file, indent=4)

print("Adjusted news sources saved successfully.")
