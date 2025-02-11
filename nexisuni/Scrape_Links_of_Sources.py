import requests
import json
import os
import time
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Your Google Custom Search credentials:
API_KEY_NEWS = "AIzaSyBhgM9ucPG5vSqo7eqSE6MXp0GmTLPs-MQ"
CX = "9725ead1807594275"

# For some known sources we know the region from their domain.
custom_region_mapping = {
    "nytimes.com": "United States",
    "theguardian.com": "United Kingdom",
    # Add other custom mappings as needed.
}

def simplify_url(url):
    """
    Simplify the URL by extracting only the scheme and netloc.
    For example, 'https://www.news-press.com/story/...' becomes 'https://www.news-press.com'
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
    except Exception as e:
        print(f"Error simplifying URL {url}: {e}")
    return url

def guess_region_from_url(url):
    """
    Attempt to guess the region (or country) from the URL.
    First, check our custom mappings.
    Otherwise, try to extract a country-code TLD and map it.
    """
    for key, region in custom_region_mapping.items():
        if key in url:
            return region

    # Try to extract a two-letter country code from the domain.
    m = re.search(r'\.([a-z]{2})(?:/|$)', url, re.IGNORECASE)
    if m:
        tld = m.group(1).lower()
        mapping = {
            'uk': 'United Kingdom',
            'au': 'Australia',
            'ca': 'Canada',
            'us': 'United States',
            'in': 'India',
            'de': 'Germany',
            'fr': 'France',
            'it': 'Italy',
            'es': 'Spain',
            'nl': 'Netherlands',
            'za': 'South Africa',
            'br': 'Brazil'
            # Add more mappings as needed.
        }
        return mapping.get(tld, "")
    return ""

def extract_region_from_meta(url):
    """
    Attempts to extract region information from meta tags on the homepage.
    Looks for a meta tag like: <meta name="geo.region" content="US-CA">
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return ""
        soup = BeautifulSoup(response.text, "html.parser")
        meta = soup.find("meta", attrs={"name": "geo.region"})
        if meta and meta.get("content"):
            return meta["content"].strip()
        return ""
    except Exception as e:
        print(f"Error extracting meta region from {url}: {e}")
        return ""

def get_region_from_ip(url):
    """
    Use an IP geolocation API (using ipinfo.io) to get the country code based on the website's domain.
    Note: This may not always reflect the editorial focus of a news site.
    """
    try:
        base_url = simplify_url(url)
        # Extract domain (e.g., "www.example.com")
        domain = base_url.split("://")[1]
        response = requests.get(f"https://ipinfo.io/{domain}/json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("country", "").strip()
        return ""
    except Exception as e:
        print(f"Error geolocating {url}: {e}")
        return ""

def determine_region(url):
    """
    Combine several methods to determine the region:
    1. Use TLD-based guessing (and custom mappings).
    2. If that fails, try scraping the homepage meta tags.
    3. Finally, fall back on IP geolocation.
    """
    region = guess_region_from_url(url)
    if region:
        return region
    region = extract_region_from_meta(url)
    if region:
        return region
    region = get_region_from_ip(url)
    return region

def get_search_result(query):
    """
    Use the Google Custom Search API to perform a search.
    Return the first result if available.
    """
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY_NEWS,
        "cx": CX,
        "q": query,
    }
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            return data["items"][0]
    else:
        print(f"Error for query '{query}': {response.status_code} {response.text}")
    return None

def main():
    # Load news source names from file 'nexisuni/nexislexis_sourceslist'
    input_file = "nexisuni/nexislexis_sourceslist"
    if not os.path.exists(input_file):
        print(f"Input file '{input_file}' does not exist.")
        return
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Remove any empty lines and strip whitespace.
    news_sources = [line.strip() for line in lines if line.strip()]

    results = []
    
    for source in news_sources:
        # Append " news" to refine the search query.
        query = source + " news"
        print(f"Searching for: {query}")
        result = get_search_result(query)
        if result:
            # Get the raw link as returned by the search result.
            raw_link = result.get("link", "")
            # Simplify the link to get the base URL.
            base_link = simplify_url(raw_link)
            # Use our combined method to determine the region.
            region = determine_region(base_link)
            results.append({
                "newspaper": source,
                "link": raw_link,
                "base_link": base_link,
                "region": region
            })
        else:
            results.append({
                "newspaper": source,
                "link": "",
                "base_link": "",
                "region": ""
            })
        # Pause briefly to avoid hitting API rate limits.
        time.sleep(1)
        
    # Ensure the output folder exists.
    output_dir = "nexisuni"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "enriched_news_sources.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"Saved {len(results)} entries to {output_file}")

if __name__ == "__main__":
    main()
