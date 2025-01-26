import json
from playwright.sync_api import sync_playwright

def scrape_website_link(url):
    """Scrapes the website link from a given URL."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15"
        )
        page = context.new_page()
        
        try:
            page.goto(url, timeout=60000)  # Wait for the page to load
            print(f"Page loaded successfully: {url}")
            
            # Extract the website link (example: from an anchor tag or metadata)
            # Modify this selector to match your page structure
            website_link = page.locator("div.card-body.bg-light h1 a").first.get_attribute("href")
            return website_link
        
        except Exception as e:
            print(f"Failed to scrape website link from {url}: {e}")
            return None
        
        finally:
            browser.close()

def update_json_with_links(input_json_path, output_json_path):
    """Reads JSON, scrapes website links, and updates the JSON file."""
    with open(input_json_path, 'r', encoding='utf-8') as file:
        newspapers = json.load(file)
    
    for newspaper in newspapers:
        link = newspaper.get('paperboy_page')
        if link:
            print(f"Processing link: {link}")
            website_link = scrape_website_link(link)
            if website_link:
                newspaper['website'] = website_link
                print(f"Updated website link for {newspaper['name']}: {website_link}")
            else:
                print(f"Could not retrieve website link for {newspaper['name']}")
    
    # Save the updated JSON file
    with open(output_json_path, 'w', encoding='utf-8') as file:
        json.dump(newspapers, file, indent=4, ensure_ascii=False)
    print(f"JSON file updated successfully and saved to {output_json_path}")

# Example usage
if __name__ == "__main__":
    input_json_path = "newspaper_links_country.json"  # Input JSON file
    output_json_path = "newspapers_websitelinks.json"  # Output JSON file
    update_json_with_links(input_json_path, output_json_path)
