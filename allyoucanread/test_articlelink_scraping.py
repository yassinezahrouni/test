from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import newspaper
import os


# Set website URL
website = "https://www.cnnchile.com"

### **Approach 1: Selenium to Extract Article URLs**
def extract_with_selenium():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

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
        if "cnnchile.com" in url or url.startswith("/"):
            if url.startswith("/"):
                url = website + url  # Convert relative URLs to absolute
            selenium_urls.add(url)

    driver.quit()  # Close the browser
    return selenium_urls


### **Approach 2: Newspaper3k to Extract Article URLs**
def extract_with_newspaper():
    news_source = newspaper.build(website, memoize_articles=False)
    newspaper_urls = set()

    for article in news_source.articles:
        try:
            newspaper_urls.add(article.url)
        except Exception as e:
            print(f"Skipping an article due to error: {e}")

    return newspaper_urls


### **Combine Both Methods & Remove Duplicates**
selenium_results = extract_with_selenium()
newspaper_results = extract_with_newspaper()

# Merge results and remove duplicates
combined_urls = selenium_results.union(newspaper_results)

# Print the extracted URLs
print("\nFinal Extracted Article URLs (No Duplicates):")
for url in combined_urls:
    print(url)

# Print total count of unique article URLs
print(f"\nTotal number of unique article links: {len(combined_urls)}")