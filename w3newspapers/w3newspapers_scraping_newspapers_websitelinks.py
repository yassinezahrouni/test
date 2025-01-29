import json
from playwright.sync_api import sync_playwright

# Load the JSON file containing country links
input_file = "w3newspapers/w3newspapers_scraped_countrynewspaperlist.json"
output_file = "w3newspapers/w3newspapers_scraped_newspapers.json"

# List of countries with issues
problematic_countries = {"South Sudan", "Mexico", "Barbados"}

# Read the JSON data and filter only problematic countries
with open(input_file, "r", encoding="utf-8") as file:
    country_data = [entry for entry in json.load(file) if entry["country"] in problematic_countries]

# Function to scrape newspapers from problematic country-specific pages
def scrape_problematic_newspapers(country_data):
    newspapers = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()
        try:
            for entry in country_data:
                country_name = entry["country"]
                state_name = entry["state"]
                country_link = entry["link"]
                
                print(f"Processing problematic country: {country_name}")  # Print processing status
                
                try:
                    page.goto(country_link, timeout=60000)  # Load country page
                    page.wait_for_load_state("networkidle")  # Ensure the page fully loads
                    newspaper_links = page.query_selector_all("div#centercontent_desk ul li a")
                    if newspaper_links:
                        for link in newspaper_links:
                            newspapers.append({
                                "country": country_name,
                                "state": state_name,
                                "name": link.inner_text().strip(),
                                "link": link.get_attribute("href")
                            })
                    else:
                        print(f"Warning: No valid newspaper links found for {country_name}")
                except Exception as e:
                    print(f"Failed to scrape {country_name}: {e}")
                    continue
        except Exception as e:
            print(f"Error scraping problematic newspapers: {e}")
        finally:
            browser.close()
    return newspapers

# Scrape newspapers from problematic country links
scraped_problematic_newspapers = scrape_problematic_newspapers(country_data)

# Append new data to existing output file
try:
    with open(output_file, "r", encoding="utf-8") as file:
        existing_data = json.load(file)
except FileNotFoundError:
    existing_data = []

# Merge the new data with existing data
updated_data = existing_data + scraped_problematic_newspapers

# Save the updated scraped data
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(updated_data, file, indent=4)

print("Updated newspaper data with problematic countries saved successfully.")
