import xmltodict
import requests
from googletrans import Translator
from datetime import datetime

# Initialize the Google Translator
translator = Translator()

def getRSS(url: str) -> dict:
    """
    Fetch the RSS feed and parse it into a dictionary.
    """
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    return xmltodict.parse(response.content)

def translate_text(text: str) -> str:
    """
    Translate text to English using Google Translate.
    """
    try:
        translated_text = translator.translate(text, src='auto', dest='en').text
        return translated_text
    except Exception as e:
        return f"Translation Error: {e}"

def parse_date(pub_date: str) -> datetime:
    """
    Try to parse the publication date using multiple formats.
    Args:
        pub_date (str): The publication date string from the RSS feed.
    Returns:
        datetime: A datetime object if parsing succeeds.
    """
    date_formats = [
        "%a, %d %b %Y %H:%M:%S %z",  # Standard RSS format
        "%a, %d %b %Y %H:%M:%S%z",   # Standard RSS with no space before timezone
        "%Y-%m-%dT%H:%M:%S%z",       # ISO 8601 with seconds
        "%Y-%m-%dT%H:%M%z",          # ISO 8601 without seconds
    ]
    for date_format in date_formats:
        try:
            return datetime.strptime(pub_date, date_format)
        except ValueError:
            continue
    raise ValueError(f"Date format not recognized: {pub_date}")

def is_today(pub_date: str) -> bool:
    """
    Check if the given publication date is from today.
    Args:
        pub_date (str): The publication date string from the RSS feed.
    Returns:
        bool: True if the publication date is today, False otherwise.
    """
    try:
        pub_date_dt = parse_date(pub_date)
        today = datetime.now(pub_date_dt.tzinfo).date()
        return pub_date_dt.date() == today
    except Exception as e:
        print(f"Error parsing date: {e}")
        return False

# List of RSS feeds with their sources
rss_feeds = [
    {"source": "Babnet", "url": "https://www.babnet.net/feed.php"},
    {"source": "Mosaique FM", "url": "https://www.mosaiquefm.net/rss"},
    {"source": "Business News", "url": "https://www.businessnews.com.tn/rss.xml"},
    {"source": "Webdo", "url": "https://www.webdo.tn/fr/rss"}
]

# Dictionary to store the count of headlines per source
news_counts = {feed["source"]: 0 for feed in rss_feeds}

# Fetch and process news from all RSS feeds
print("Translated News Headlines:")
print("-" * 50)
news_counter = 1

for feed in rss_feeds:
    source = feed["source"]
    rss_url = feed["url"]
    try:
        data = getRSS(rss_url)
        for item in data['rss']['channel']['item']:
            pub_date = item.get('pubDate', None)
            if pub_date and is_today(pub_date):
                original_title = item['title']
                description = item.get('description', "No description available")
                link = item['link']
                
                # Translate title to English
                translated_title = translate_text(original_title)
                
                # Display the news with its number and source
                print(f"{news_counter}. Source: {source}")
                print(f"Original Title: {original_title}")
                print(f"Translated Title: {translated_title}")
                print(f"Description: {description}")
                print(f"Link: {link}")
                print("-" * 50)
                
                # Increment counters
                news_counter += 1
                news_counts[source] += 1
    except Exception as e:
        print(f"Error fetching news from {source}: {e}")

# Summary of news counts per source
print("\nSummary of Extracted News:")
print("-" * 50)
for source, count in news_counts.items():
    print(f"Source: {source}, Headlines Extracted: {count}")
print("-" * 50)
