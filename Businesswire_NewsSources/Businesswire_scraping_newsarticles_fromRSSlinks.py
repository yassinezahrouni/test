import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import os


# Input and output file paths
input_file = "Businesswire_NewsSources/businesswire_rss_links.json"  

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

# Assume all_articles is already defined from your code
output_dir = "All_sources_Links"
os.makedirs(output_dir, exist_ok=True)
today = datetime.now()
formatted_date = today.strftime("%Y%m%d")  # format to avoid invalid filename characters
output_file = os.path.join(output_dir, f"consolidated_data_from_RSS_links_files_{formatted_date}.json")

# Read existing consolidated data if the file exists.
if os.path.exists(output_file):
    with open(output_file, "r", encoding="utf-8") as file:
        consolidated_data = json.load(file)
else:
    consolidated_data = {}

# Add the scraped articles under the key "scraped_articles".
consolidated_data["Businesswire_scraped_articles_links"] = all_articles

# Write the updated consolidated data back to the file.
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(consolidated_data, file, indent=4, ensure_ascii=False)

print(f"Scraped {len(all_articles)} articles to {output_file}")

print(f"Scraped articles saved to {output_file}")
