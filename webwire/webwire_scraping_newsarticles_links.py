import feedparser
import json
import datetime
import os
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime

def get_article_text(link):
    """
    Visits the provided link and attempts to extract the article text.
    It first looks for common containers on BusinessWire pages, and if not found,
    falls back to extracting all paragraph text.
    
    Args:
        link (str): URL of the article.
        
    Returns:
        str: The concatenated article text or an empty string if not found.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ScraperBot/1.0)"}
        response = requests.get(link, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Failed to retrieve article: {link} (status code: {response.status_code})")
            return ""
        soup = BeautifulSoup(response.content, "html.parser")
        # Try common containers for BusinessWire articles.
        container = soup.find("div", class_="bw-release-body")
        if not container:
            container = soup.find("div", class_="release-body")
        if not container:
            container = soup.find("article")
        if container:
            paragraphs = container.find_all("p")
            article_text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            return article_text
        else:
            # Fallback: get all paragraphs
            paragraphs = soup.find_all("p")
            article_text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            return article_text
    except Exception as e:
        print(f"Error fetching article text from {link}: {e}")
        return ""

def scrape_rss_feed(url):
    """
    Scrapes the provided RSS feed URL and returns a list of dictionaries,
    each containing the headline, date, hour, link, and article text from the feed entries.
    
    Args:
        url (str): The URL of the RSS feed.
    
    Returns:
        list: A list of dictionaries with keys: "headline", "date", "hour", "link", "article text".
    """
    feed = feedparser.parse(url)
    data = []
    for entry in feed.entries:
        headline = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        
        # Process publication time into separate date and hour strings.
        published_parsed = entry.get("published_parsed")
        if published_parsed:
            dt = datetime(*published_parsed[:6])
            date_str = dt.strftime("%Y-%m-%d")
            hour_str = dt.strftime("%H:%M:%S")
        else:
            date_str = ""
            hour_str = ""
        
        print(f"Fetching article text for: {link}")
        article_text = get_article_text(link)
        # Pause briefly between article fetches.
        time.sleep(1)
        
        data.append({
            "headline": headline,
            "date": date_str,
            "hour": hour_str,
            "link": link,
            "article text": article_text
        })
    return data

def save_to_json(data, output_file):
    # Read existing data if the file exists; otherwise, start with an empty dictionary.
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            consolidated_data = json.load(f)
    else:
        consolidated_data = {}

    # Add/Update the weather alerts in the consolidated data.
    consolidated_data["Webwire_news"] = data

    # Write the updated data back to the consolidated file.
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(consolidated_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    rss_url = "http://rssfeeds.webwire.com/webwire-recentheadlines"
    #  Create the output directory if it doesn't exist.
    output_dir = "All_sources_Links"
    os.makedirs(output_dir, exist_ok=True)
    today = datetime.now()
    formatted_date = today.strftime("%Y%m%d")  # format to avoid invalid filename characters
    output_file = os.path.join(output_dir, f"consolidated_data_from_RSS_links_files_{formatted_date}.json")
    
    print("Scraping RSS feed...")
    rss_data = scrape_rss_feed(rss_url)
    save_to_json(rss_data, output_file)
    print("Scraping complete.")
