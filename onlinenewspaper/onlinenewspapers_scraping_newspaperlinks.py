import json
from playwright.sync_api import sync_playwright

def scrape_newspapers(input_file, output_file):
    """Scrapes newspaper names and links from each country's page."""
    
    # Load the input JSON file
    with open(input_file, 'r', encoding='utf-8') as file:
        countries = json.load(file)
    
    newspapers = []  # List to hold the newspapers' data

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        for country in countries:
            country_name = country.get("name", "Unknown")
            country_link = country.get("link")
            
            if not country_link:
                print(f"Skipping {country_name}, no link available.")
                continue
            
            try:
                page = browser.new_page()
                page.goto(country_link, timeout=60000)  # Load the page
                print(f"Processing country: {country_name} - {country_link}")
                
                # Locate the correct table structure and find the `<td class="t3b">`
                content_table = page.locator("table.t0 > tbody > tr > td > table.t3 > tbody > tr > td.t3b")
                if content_table.count() == 0:
                    print(f"No content found for {country_name}.")
                    continue
                
                # Extract the `<ul><li><a>` structure within the content table
                newspaper_elements = content_table.locator("ul > li > a[class='but']")
                
                for i in range(newspaper_elements.count()):
                    element = newspaper_elements.nth(i)
                    newspaper_name = element.text_content().strip()
                    newspaper_link = element.get_attribute("href")
                    
                    # Add the data to the newspapers list
                    if newspaper_name and newspaper_link:
                        newspapers.append({
                            "country": country_name,
                            "name": newspaper_name,
                            "link": newspaper_link
                        })
            
            except Exception as e:
                print(f"Failed to process {country_name}: {e}")
            finally:
                page.close()
        
        browser.close()
    
    # Save the newspapers data to the output JSON file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(newspapers, file, indent=4, ensure_ascii=False)
    
    print(f"Scraping completed. Data saved to {output_file}")

# Example usage
if __name__ == "__main__":
    input_file = "onlinenewspapers_countries_links.json"  # Input JSON file
    output_file = "onlinenewspapers_scraped_newspapers.json"  # Output JSON file
    scrape_newspapers(input_file, output_file)
