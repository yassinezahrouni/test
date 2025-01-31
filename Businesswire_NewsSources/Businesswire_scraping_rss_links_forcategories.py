import json
from playwright.sync_api import sync_playwright

# Define the website URL
url = "https://www.businesswire.com/portal/site/home/news/industries/"
output_file = "Businesswire_NewsSources/businesswire_categories_rss.json"

# Function to scrape categories and their RSS links
def scrape_businesswire_rss():
    categories_data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()
        try:
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")  # Wait for full page load
            
            # Locate all categories
            category_rows = page.query_selector_all("div.epi table tbody tr[class*='epi']:not([class='epi']) td a")
            for category in category_rows:
                category_name = category.inner_text().strip()
                category_link = category.get_attribute("href")
                
                # Locate RSS link for category
                rss_element = category.evaluate_handle("el => el.closest('tr').querySelector('td.dataConstant.rss a')")
                rss_link = rss_element.get_attribute("href") if rss_element else None
                
                # Store category data
                categories_data.append({
                    "category": category_name,
                    "rss_link": rss_link
                })
        except Exception as e:
            print(f"Error scraping RSS links: {e}")
        finally:
            browser.close()
    return categories_data

# Scrape the categories and their RSS links
rss_data = scrape_businesswire_rss()

# Save the scraped RSS data
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(rss_data, file, indent=4)

print("Scraped RSS categories saved successfully.")
