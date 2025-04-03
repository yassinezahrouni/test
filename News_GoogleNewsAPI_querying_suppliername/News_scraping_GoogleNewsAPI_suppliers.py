import json
import pandas as pd
import requests
import urllib.parse
from datetime import datetime
from deep_translator import GoogleTranslator

# Replace with your own API key and CX
API_KEY = "AIzaSyBo03D2rKdBJRfUsL9GvyRcWzDoxIMfCdg"  # Replace with your API key
CX = "9725ead1807594275"

# Define the Excel file path
excel_file = "/Users/yassinezahrouni/coding/test/CountryIndexes/DB_SupplyChain_MA.xlsx"

# Read the sheets for suppliers and shipments
suppliers_df = pd.read_excel(excel_file, sheet_name="Suppliers", engine="openpyxl")
segments_df = pd.read_excel(excel_file, sheet_name="ShipmentSegments", engine="openpyxl")

# Function to determine Google News domain based on country
def get_google_news_domain(country):
    country_domains = {
        "Germany": "DE",
        "Japan": "JP",
        "United States": "US",
        "France": "FR",
        "United Kingdom": "GB",
        "China": "CN",
        "South Korea": "KR"
    }
    return country_domains.get(country, "US")  # Default to US if country is known, otherwise use global search

# Function to filter out social media & Wikipedia sources
def is_valid_news_source(article):
    """Checks if the article is from a valid news source and not social media or Wikipedia."""
    invalid_sources = ["twitter.com", "facebook.com", "instagram.com", 
                       "tiktok.com", "linkedin.com", "reddit.com", "pinterest.com", "wikipedia.org"]

    if "link" in article:
        article_url = article["link"]
        for source in invalid_sources:
            if source in article_url:
                return False  # Exclude if it's a social media or Wikipedia link
    return True

# Function to perform Google News search
def google_news_search(query, country=None):
    google_domain = get_google_news_domain(country) if country else "US"    # Use global search if no country
    encoded_query = urllib.parse.quote(query)                               # Properly encode the query for URL
    url = f"https://www.googleapis.com/customsearch/v1?q={encoded_query}&cx={CX}&key={API_KEY}&num=10&gl={google_domain}&sort=date"
    
    print(f"Querying: {url}")  # Debugging output

    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("items", [])
        
        # Filter out social media and Wikipedia articles
        articles = [article for article in articles if is_valid_news_source(article)]

        # Initialize translator
        translator = GoogleTranslator(source='auto', target='en')

        # Store articles
        collected_articles = []
        for article in articles:
            # Extract publication date
            published_time = "Unknown"
            try:
                meta_tags = article.get("pagemap", {}).get("metatags", [{}])[0]
                if "article:published_time" in meta_tags:
                    published_time = meta_tags["article:published_time"]
                elif "og:updated_time" in meta_tags:
                    published_time = meta_tags["og:updated_time"]
            except (IndexError, KeyError):
                pass

            # Translate title and snippet
            title = article.get("title", "No Title")
            snippet = article.get("snippet", "")

            try:
                translated_title = translator.translate(title)
                translated_snippet = translator.translate(snippet)
            except Exception as e:
                print(f"Translation error: {e}")
                translated_title = title
                translated_snippet = snippet

            collected_articles.append({
                "title": translated_title,
                "snippet": translated_snippet,
                "link": article.get("link", ""),
                "published_time": published_time
            })

        print(f"Articles found: {len(collected_articles)}")  # Debugging output
        return collected_articles
    else:
        print(f"Error fetching news: {response.status_code}")  # Debugging output
    return []

# Output storage
news_results = []
queried_items = set()  # Store already queried suppliers and roads

# Process suppliers
for _, supplier in suppliers_df.iterrows():
    supplier_name = str(supplier["name"]).strip()  # Ensure it's a string
    supplier_country = str(supplier["Country"]).strip()  # Use country for better localization

    if pd.notna(supplier_name) and pd.notna(supplier_country):
        if supplier_name in queried_items:
            continue  # Skip if already queried

        formatted_supplier_name = supplier_name.replace(" ", "+")  # Replace spaces with `+` for Google Search
        query_text = f"{formatted_supplier_name}"

        print(f"Processing supplier: {query_text}")  # Debugging output
        articles = google_news_search(query_text, supplier_country)

        if articles:
            news_results.append({"query": query_text, "type": "Supplier", "supplier": supplier_name, "results": articles})

        # Mark this supplier as queried
        queried_items.add(supplier_name)

# Process shipment roads
for _, segment in segments_df.iterrows():
    segment_type = str(segment["Segment description"]).lower()  # Ensure it's a string
    roads = str(segment["Roads"]).strip()
    road_country = str(segment["Country of roads"]).strip() if pd.notna(segment["Country of roads"]) else None  # Check if country is missing

    if pd.notna(roads):  
        routes = [route.strip() for route in roads.split(";")]

        for route in routes:
            if route in queried_items:
                continue  # Skip if already queried

            if road_country:
                query_text = f"{route} {road_country}"  # Ground transport queries include country
                category = "Ground Route"
            else:
                query_text = route  # Ocean transport queries do not include country
                category = "Ocean Route"

            print(f"Processing road: {query_text}")  # Debugging output
            articles = google_news_search(query_text, road_country)  # Query with country for ground, None for ocean

            if articles:
                news_results.append({"query": query_text, "type": "Road", "category": category, "results": articles})

            # Mark this road as queried
            queried_items.add(route)

# Save all results in a single JSON
output_file = "supply_chain_news_results_translated.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(news_results, f, ensure_ascii=False, indent=4)

print(f"Collected news data saved to {output_file}")
