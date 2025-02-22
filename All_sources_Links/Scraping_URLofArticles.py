import sys
import os
sys.path.append("/Users/yassinezahrouni/coding/test/All_sources_Links") 
from Checking_IfWebsiteURL_StillValid import check_page_validity_or_replace 
import  re
import datetime
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests

# 🔹 CHANGE THIS VARIABLE TO SCRAPE A DIFFERENT NEWS WEBSITE
website = "https://www.jeuneafrique.com/pays/tunisie/"

# 🔹 Extract only the base URL (without paths) from the given `website`
parsed_website = urlparse(website)
base_url = f"{parsed_website.scheme}://{parsed_website.netloc}"


### **Step 1: Fetch Page Content Using Playwright (With Scrolling)**
def fetch_page_with_playwright(url):

    # check for validity of the website first, in case the website in the DB is not up to date
    new_url = check_page_validity_or_replace(url)
    if new_url:
        url = new_url  # ✅ Only replace if a valid URL is found


    """Fetches the full page HTML using Playwright with scrolling and waiting."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()
        try:
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")  # Wait for full page load

            # **🔹 Scroll down to load dynamically loaded content**
            for _ in range(5):  
                page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)  

            content = page.content()  # Get the page's HTML content
            print("\n🔍 DEBUG: Page Content Fetched ✅")  # Print confirmation
            return content
        except Exception as e:
            print(f"❌ Playwright failed to access {url}: {e}")
            return None
        finally:
            browser.close()


def is_article_page(url):
    """Checks if a given URL contains article-related elements (headline, meta tags, long text)."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return False  # Skip if page is not accessible
    except requests.exceptions.RequestException:
        return False  # Skip if request fails

    soup = BeautifulSoup(response.text, "html.parser")

    # **🔹 Check for a meaningful `<title>` tag**
    title = soup.title.string if soup.title else ""
    if not title or len(title) < 10:  # Skip pages with very short/nonexistent titles
        return False

    # **🔹 Check for `<meta>` tags indicating it's an article**
    meta_article = soup.find("meta", {"property": "og:type"})
    if meta_article and "article" in meta_article.get("content", "").lower():
        return True

    meta_news = soup.find("meta", {"name": "news_article"})
    if meta_news and "article" in meta_news.get("content", "").lower():
        return True

    # **🔹 Check if the page contains a `<time>` element**
    if soup.find("time") or soup.find(attrs={"datetime": True}):  
        return True

    # **🔹 Check if there are large paragraphs of text (indicating a full article)**
    paragraphs = soup.find_all("p")
    total_text = " ".join([p.get_text() for p in paragraphs])
    if len(total_text.split()) > 300:  # More than 300 words suggests an article
        return True

    return False  # Otherwise, it's not an article




### **Step 2: Extract & Filter Article Links (No Date Filtering)**
def extract_article_links(page_content, base_url):
    """Extracts article links, converts relative URLs to absolute, and validates if they are actual articles."""
    if not page_content:
        print("❌ No content retrieved, skipping extraction.")
        return []

    soup = BeautifulSoup(page_content, "html.parser")
    unique_articles = set()

    for link in soup.find_all("a", href=True):
        url = link["href"]
        if not url:  # Skip empty URLs
            continue

        # **🔹 Convert relative URLs to absolute using only the base domain**
        if url.startswith("http"):  
            final_url = url  # Keep absolute URLs as they are
        elif url.startswith("/"):  
            final_url = base_url + url  # Convert relative URLs using the cleaned base URL
        elif url[0].isalnum():  # If it starts with a letter (A-Z, a-z) or number (0-9)
            final_url = base_url + "/" + url  # Convert it to absolute by adding "/"
        else:
            continue  # Skip invalid URLs

        # **🔹 Extract path segments from URL**
        path_segments = urlparse(final_url).path.strip("/").split("/")

        # **🔹 Condition 1: At least one substring has 3+ hyphens ("-")**
        has_three_hyphens = any(segment.count("-") >= 3 for segment in path_segments)

        # **🔹 Condition 2: At least one substring has 1 hyphen ("-") and at least 3 digits ("123")**
        has_hyphen_and_numbers = any(re.search(r"-.*\d{3,}", segment) for segment in path_segments)

        # **🔹 Final Check: Either the page has article attributes OR it meets the URL conditions**
        #if is_article_page(final_url) and (has_three_hyphens or has_hyphen_and_numbers):
        if (has_three_hyphens or has_hyphen_and_numbers):
            unique_articles.add(final_url)

    # Convert the set back to a sorted list of dictionaries
    sorted_articles = sorted(unique_articles)  # Sorting URLs alphabetically
    return [{"url": url} for url in sorted_articles]




### **Step 3: Run Everything**
def main():
    # Fetch the page with Playwright
    page_content = fetch_page_with_playwright(website)

    # Extract and filter article links (removing duplicates)
    extracted_articles = extract_article_links(page_content, base_url)

    # Print the extracted articles
    print("\n✅ Final Extracted Articles (Sorted):")
    for article in extracted_articles:
        print(f"📌 {article['url']}")

    print(f"\nTotal number of unique articles extracted: {len(extracted_articles)}")

# Run the main function
if __name__ == "__main__":
    main()