import feedparser
import json
import datetime
import os
import requests
from bs4 import BeautifulSoup
import time

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
            dt = datetime.datetime(*published_parsed[:6])
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
    """
    Saves the given data to a JSON file at the specified output file path.
    
    Args:
        data (list): The list of dictionaries to save.
        output_file (str): The output file path.
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    rss_url = "http://rssfeeds.webwire.com/webwire-recentheadlines"
    # Append the current date to the filename (e.g., webwire_recent_headlines_2025-02-09.json)
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join("webwire", f"webwire_recent_headlines_{today_date}.json")
    
    print("Scraping RSS feed...")
    rss_data = scrape_rss_feed(rss_url)
    save_to_json(rss_data, output_file)
    print("Scraping complete.")
