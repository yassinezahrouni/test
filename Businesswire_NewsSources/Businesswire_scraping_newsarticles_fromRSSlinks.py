import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime


# Input and output file paths
input_file = "Businesswire_NewsSources/businesswire_rss_links.json"  # The file with RSS links

current_date = datetime.now().strftime("%Y-%m-%d")
output_file = f"Businesswire_NewsSources/Businesswire_scraped_articles_{current_date}.json"  # The output JSON file


def parse_rss_feed(rss_url, category):
    """Fetch and parse RSS feed, extracting articles."""
    articles = []
    try:
        # Ensure URL is properly formatted
        rss_url = "https:" + rss_url if rss_url.startswith("//") else rss_url
        
        # Fetch RSS feed
        response = requests.get(rss_url, timeout=10)
        response.raise_for_status()  # Raise error for bad response

        # Parse XML content
        root = ET.fromstring(response.content)

        # Find all items in the RSS feed
        for item in root.findall(".//item"):
            title = item.findtext("title", "").strip()
            pub_date = item.findtext("pubDate", "").strip()
            description = item.findtext("description", "").strip()
            link = item.findtext("link", "").strip()

            if title and link:  # Ensure valid data
                articles.append({
                    "article_category": category,
                    "article_title": title,
                    "article_pubdate": pub_date,
                    "article_description": description,
                    "article_link": link
                })
    except Exception as e:
        print(f"Error fetching {rss_url}: {e}")
    
    return articles

# Load the RSS feed URLs from the cleaned JSON file
with open(input_file, "r", encoding="utf-8") as file:
    rss_sources = json.load(file)

# Scrape articles from all RSS feeds
all_articles = []
for source in rss_sources:
    category = source.get("category", "Unknown Category")
    rss_link = source.get("rss_link", "")

    if rss_link:
        articles = parse_rss_feed(rss_link, category)
        all_articles.extend(articles)

# Save the scraped articles to a JSON file
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(all_articles, file, indent=4, ensure_ascii=False)

print(f"Scraped articles saved to {output_file}")
