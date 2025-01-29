import json

# Load the JSON file
input_file = "onlinenewspaper/onlinenewspapers_scraped_newspapers.json"
output_file = "onlinenewspaper/updated_onlinenewspapers_scraped_newspapers.json"

# List of US states
us_states = {"Alabama", "Alaska", "Arizona", "Arkansas", "California",
              "Colorado", "Connecticut", "Delaware", "Florida", "Georgia",
                "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas",
                  "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts",
                    "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
                      "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
                        "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma",
                          "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", 
                           "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
                            "Washington", "West Virginia", "Wisconsin", "Wyoming"}

# Read the JSON data
with open(input_file, "r", encoding="utf-8") as file:
    newspapers = json.load(file)

# Process the data
for newspaper in newspapers:
    country = newspaper["country"]
    
    if country in us_states:  # If it's a US state
        newspaper["state"] = country  # Store the state name
        newspaper["country"] = "USA"  # Replace country with USA
    else:
        newspaper["state"] = ""  # Keep state empty for real countries

# Save the updated JSON
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(newspapers, file, indent=4)

print("Updated JSON file saved successfully.")

