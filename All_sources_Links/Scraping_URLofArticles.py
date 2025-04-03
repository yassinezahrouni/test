import sys
import json
import os
import re
import datetime
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests

# **🔹 Get country & input JSON file from arguments**
if len(sys.argv) < 3:
    print("❌ Error: Missing arguments. Usage: python Scraping_URLofArticles.py <Country> <Input_JSON_Path>")
    sys.exit(1)

supplier_country = sys.argv[1]  # **Country from argument**
input_json_path = sys.argv[2]   # **Input JSON file path**

# **🔹 Output JSON Path**
output_json_path = f"/Users/yassinezahrouni/coding/test/All_sources_Links/{supplier_country}_newsarticle_URLs.json"

### **Step 1: Load Already Processed Websites**
def get_already_processed_websites():
    """Reads the existing JSON file to check which websites have already been processed."""
    if not os.path.exists(output_json_path):
        return set()  # No file yet → nothing processed
    
    with open(output_json_path, "r", encoding="utf-8") as f:
        try:
            existing_data = json.load(f)
            return {entry["Source_name"] for entry in existing_data}  # Get unique website names
        except json.JSONDecodeError:
            return set()  # Handle JSON corruption (treat as empty)

already_processed_websites = get_already_processed_websites()

### **Step 2: Fetch Page Content Using Playwright**
def fetch_page_with_playwright(url):
    """Fetches the full page HTML using Playwright with scrolling and waiting."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()
        try:
            print(f"🌍 Processing website: {url}")  # ✅ Print which website is currently being processed
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")

            for _ in range(5):  
                page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)

            content = page.content()
            print(f"✅ Successfully loaded page: {url}\n")  # ✅ Confirmation of successful page load
            return content
        except Exception as e:
            print(f"❌ Playwright failed to access {url}: {e}")
            return None
        finally:
            browser.close()

# **🔹 Define Social Media Domains to Exclude**
SOCIAL_MEDIA_DOMAINS = [
    "facebook.com", "fb.com", "instagram.com", "linkedin.com", "twitter.com", "x.com",
    "tiktok.com", "youtube.com", "reddit.com", "snapchat.com", "whatsapp.com",
    "wa.me", "telegram.me", "t.me"
]

def is_social_media_url(url):
    """Checks if the URL belongs to a social media platform."""
    domain = urlparse(url).netloc.lower()
    return any(social_domain in domain for social_domain in SOCIAL_MEDIA_DOMAINS)

def extract_article_links(page_content, base_url):
    """Extracts article links, converts relative URLs to absolute, and filters out social media URLs."""
    if not page_content:
        return []

    soup = BeautifulSoup(page_content, "html.parser")
    unique_articles = set()

    for link in soup.find_all("a", href=True):
        url = link["href"]
        if not url:
            continue

        # **🔹 Convert relative URLs to absolute using base URL**
        if url.startswith("http"):  
            final_url = url
        elif url.startswith("/"):  
            final_url = base_url + url  
        elif url[0].isalnum():  
            final_url = base_url + "/" + url  
        else:
            continue  

        # **🔹 Filter out social media links**
        if is_social_media_url(final_url):
            print(f"⚠️ Skipping social media link: {final_url}")
            continue  

        # **🔹 Extract path segments from URL**
        path_segments = urlparse(final_url).path.strip("/").split("/")
        has_three_hyphens = any(segment.count("-") >= 3 for segment in path_segments)
        has_hyphen_and_numbers = any(re.search(r"-.*\d{3,}", segment) for segment in path_segments)

        if has_three_hyphens or has_hyphen_and_numbers:
            unique_articles.add(final_url)

    print(f"✅ Found {len(unique_articles)} article links from {base_url}\n")  # ✅ Print the number of articles extracted
    return sorted(unique_articles)


### **Step 4: Main Execution**
def main():
    # **🔹 Load Input JSON**
    try:
        with open(input_json_path, "r", encoding="utf-8") as f:
            news_sources = json.load(f)
        
        # **Filter sources for the given country**
        news_sources = [source for source in news_sources if source.get("Country") == supplier_country]
        if not news_sources:
            print(f"❌ No sources found for {supplier_country}. Exiting.")
            sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Error: {input_json_path} not found.")
        sys.exit(1)

    # **🔹 Extract Articles from Each News Source**
    all_articles = []
    for source in news_sources:
        source_name = source["name"]
        source_url = source["link"]
        country = source["Country"]

        # **✅ Skip if already processed**
        if source_name in already_processed_websites:
            print(f"⚠️ Skipping already processed site: {source_name} ({source_url})\n")
            continue  

        print(f"🔍 Extracting from: {source_name} ({source_url})\n")

        # **🔹 Fetch Page Content**
        page_content = fetch_page_with_playwright(source_url)
        base_url = f"{urlparse(source_url).scheme}://{urlparse(source_url).netloc}"

        # **🔹 Extract Article Links**
        extracted_links = extract_article_links(page_content, base_url)

        for article_url in extracted_links:
            all_articles.append({
                "Source_name": source_name,
                "Article_link": article_url,
                "Country": country
            })

    # **🔹 Append New Articles to JSON**
    if all_articles:
        try:
            with open(output_json_path, "r", encoding="utf-8") as f:
                existing_articles = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_articles = []

        combined_articles = existing_articles + all_articles  

        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(combined_articles, f, indent=4, ensure_ascii=False)

        print(f"✅ Successfully saved {len(all_articles)} extracted articles to {output_json_path}\n")
    else:
        print("✅ No new articles to save. Everything was already processed.\n")

if __name__ == "__main__":
    main()
