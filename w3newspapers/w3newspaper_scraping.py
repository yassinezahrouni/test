import json
from playwright.sync_api import sync_playwright

# List of US states
us_states = {"Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"}

# Function to scrape newspaper links and names from W3Newspapers
def scrape_w3newspapers():
    url = "https://www.w3newspapers.com"
    newspapers = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()
        try:
            page.goto(url, timeout=60000)  # Wait up to 60 seconds for the page to load
            page.wait_for_selector("div#rightcontent li a", timeout=10000)
            page.wait_for_selector("div#centercontent_desk div.countries li a", timeout=10000)
            
            # Scrape from rightcontent (US States)
            rightcontent_links = page.query_selector_all("div#rightcontent li a")
            for link in rightcontent_links:
                state_name = link.inner_text()
                newspapers.append({
                    "name": state_name,
                    "link": "https://www.w3newspapers.com" + link.get_attribute("href"),
                    "country": "USA",  # Set country to USA for states
                    "state": state_name  # Store the state name
                })
            
            # Scrape from centercontent_desk under countries
            country_links = page.query_selector_all("div#centercontent_desk div.countries li a")
            for link in country_links:
                country_name = link.inner_text()
                newspapers.append({
                    "name": country_name,
                    "link": "https://www.w3newspapers.com" + link.get_attribute("href"),
                    "country": country_name,  # Use the country name directly
                    "state": ""  # Leave state empty for real countries
                })
        except Exception as e:
            print(f"Error scraping {url}: {e}")
        finally:
            browser.close()
    return newspapers

# Scrape the newspapers
newspapers = scrape_w3newspapers()

# Save the scraped data
output_file = "w3newspapers/w3newspapers_scraped_countrynewspaperlist.json"
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(newspapers, file, indent=4)

print("Scraped newspaper data saved successfully.")
