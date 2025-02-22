import json
import os
import time
import requests
import newspaper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse


Country = 'Tunisia'

# Define JSON file paths
NewsWebsitesPerCountry_filepath1 = 'allyoucanread/allyoucanread_news_sources_websites.json'
NewsWebsitesPerCountry_filepath2 = 'onlinenewspaper/onlinenewspapers_scraped_newspapers.json'

# Define output directory and file
output_dir = "All_sources_Links"
os.makedirs(output_dir, exist_ok=True)  # Create folder if not exists
output_file = os.path.join(output_dir, "tunisia_article_links.json")

### **Step 1: Extract News Websites for Tunisia**
def get_news_websites(filepath, country):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        # Extract name and link where the country matches
        news_sources = {(entry["name"], entry["link"]) for entry in data if entry.get("Country") == country}

        return news_sources

    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return set()  # Return an empty set if an error occurs

# Extract websites from both files and remove duplicates
news_sources1 = get_news_websites(NewsWebsitesPerCountry_filepath1, Country)
news_sources2 = get_news_websites(NewsWebsitesPerCountry_filepath2, Country)
all_news_sources = news_sources1.union(news_sources2)

print(f"\nTotal news websites found for {Country}: {len(all_news_sources)}")
for name, link in sorted(all_news_sources):
    print(f"{name}: {link}")

### **Step 2: Check If Website is Reachable**
def is_website_accessible(website):
    """Check if the website is reachable."""
    try:
        response = requests.get(website, timeout=5)  # Timeout after 5 seconds
        return response.status_code == 200
    except requests.RequestException:
        return False  # Return False if the request fails

### **Step 3: Extract Article URLs Using Both Approaches**
def extract_with_selenium(website):
    """Extract article URLs from a website using Selenium."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Extract domain from website (e.g., "africanmanager.com" from "https://africanmanager.com")
    website_domain = urlparse(website).netloc

    # Open the website
    driver.get(website)

    # Scroll to load more articles
    for _ in range(3):  # Scroll 3 times
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for new content to load

    # Get page source after scrolling
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Extract article URLs
    selenium_urls = set()
    for link in soup.find_all("a", href=True):
        url = link["href"]

        # Extract domain from the article URL
        article_domain = urlparse(url).netloc

        # Ensure the article URL contains the domain part of the website before adding
        if website_domain in article_domain:
            selenium_urls.add(url)

    driver.quit()  # Close the browser
    return selenium_urls

def extract_with_newspaper(website):
    """Extract article URLs from a website using Newspaper3k."""
    try:
        news_source = newspaper.build(website, memoize_articles=False)
        newspaper_urls = set()

        # Extract domain from website (e.g., "africanmanager.com")
        website_domain = urlparse(website).netloc

        for article in news_source.articles:
            try:
                # Extract domain from the article URL
                article_domain = urlparse(article.url).netloc

                # Ensure the article URL contains the domain part of the website before adding
                if website_domain in article_domain:
                    newspaper_urls.add(article.url)

            except Exception as e:
                print(f"Skipping an article due to error: {e}")

        return newspaper_urls

    except Exception as e:
        print(f"Error extracting from {website}: {e}")
        return set()  # Return an empty set in case of failure


### **Step 4: Loop Through Each News Website and Extract Article Links**
all_articles = []

for name, website in all_news_sources:
    print(f"\nChecking website: {name} ({website})")

    # Validate website URL
    if not website.startswith("http"):
        website = "https://" + website

    # Check if the website is accessible
    if not is_website_accessible(website):
        print(f"❌ Skipping {name} - Website not accessible.")
        continue  # Skip this website if it is unreachable

    print(f"✅ Website is accessible: {name}")

    selenium_results = extract_with_selenium(website)
    newspaper_results = extract_with_newspaper(website)

    # Merge and remove duplicates
    site_articles = selenium_results.union(newspaper_results)

    # Store results
    for url in site_articles:
        all_articles.append({
            "Country": Country,
            "Website": name,
            "Article Link": url
        })

    print(f"🔹 Found {len(site_articles)} articles from {name}")

# Save the extracted articles to a JSON file
with open(output_file, "w", encoding="utf-8") as outfile:
    json.dump(all_articles, outfile, ensure_ascii=False, indent=4)

# Print final results
print("\n✅ Final Extracted Article Links (No Duplicates) Saved to JSON File:")
for article in all_articles:
    print(f"{article['Website']}: {article['Article Link']}")

print(f"\nTotal number of unique article links: {len(all_articles)}")
print(f"Data saved to: {output_file}")
