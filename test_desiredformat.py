import xmltodict
import requests
from googletrans import Translator
from datetime import datetime
from bs4 import BeautifulSoup
import json
import os

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

def fetch_full_article(url: str) -> str:
    """
    Fetch the full article content from the given URL.
    Args:
        url (str): The URL of the full article.
    Returns:
        str: The full text of the article.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Attempt to extract the main article content
        # This may vary depending on the website's structure
        # Here, we'll try to extract all paragraph texts
        paragraphs = soup.find_all('p')
        full_text = ' '.join([para.get_text() for para in paragraphs])
        
        if not full_text:
            return "Full article content not available."
        
        return full_text
    except Exception as e:
        return f"Error fetching full article: {e}"

# List of RSS feeds with their sources
rss_feeds = [
    {"source": "Babnet", "url": "https://www.babnet.net/feed.php"},
    {"source": "Mosaique FM", "url": "https://www.mosaiquefm.net/rss"},
    {"source": "Business News", "url": "https://www.businessnews.com.tn/rss.xml"},
    {"source": "Webdo", "url": "https://www.webdo.tn/fr/rss"},
    {"source": "Tunisie Numerique", "url": "https://www.tunisienumerique.com/feed-actualites-tunisie.xml"},
    {"source": "Kapitalis", "url": "https://kapitalis.com/tunisie/feed/"},
    {"source": "La presse", "url": "https://lapresse.tn/feed/"},
    {"source": "Realités", "url": "https://realites.com.tn/fr/feed/"},
    {"source": "Tunisie focus", "url": "https://www.tunisiefocus.com/feed/"},
]

# Dictionary to store the count of headlines per source
news_counts = {feed["source"]: 0 for feed in rss_feeds}

# List to store all articles
articles = []

# Fetch and process news from all RSS feeds
print("Fetching and processing news headlines...")

for feed in rss_feeds:
    source = feed["source"]
    rss_url = feed["url"]
    try:
        data = getRSS(rss_url)
        # Navigate to the list of items; RSS structure may vary
        items = []
        if 'rss' in data and 'channel' in data['rss']:
            items = data['rss']['channel']['item']
        elif 'feed' in data and 'entry' in data['feed']:
            items = data['feed']['entry']
        else:
            print(f"Unrecognized RSS format for source: {source}")
            continue

        for item in items:
            # Different RSS feeds may use different keys for publication date and other fields
            pub_date = item.get('pubDate') or item.get('published') or item.get('dc:date')
            if pub_date and is_today(pub_date):
                original_title = item.get('title', 'No title')
                description = item.get('description') or item.get('summary') or "No description available"
                link = item.get('link')
                if isinstance(link, dict):
                    link = link.get('@href', 'No link available')

                # Translate title to English
                translated_title = translate_text(original_title)

                # Fetch full article content
                full_article = fetch_full_article(link) if link != 'No link available' else "No link available."

                # Extract category if available
                category = item.get('category') or "Uncategorized"

                # Extract publication time in ISO format
                try:
                    pub_date_dt = parse_date(pub_date)
                    publication_time = pub_date_dt.isoformat()
                except Exception as e:
                    publication_time = "Unknown publication time"

                # Create the article dictionary
                article = {
                    "title": translated_title,
                    "category": category,
                    "summary": description,
                    "link": link,
                    "publication_time": publication_time,
                    "full_article": full_article,
                    "source": source
                }

                articles.append(article)
                news_counts[source] += 1

    except Exception as e:
        print(f"Error fetching news from {source}: {e}")

# Output the results
output = {
    "translated_news_headlines": articles,
    "summary_of_extracted_news": news_counts
}

# Define the target directory with the relative path
target_directory = os.path.join('NewsData', 'NewsData_withDate')

# Create the directory if it doesn't exist
os.makedirs(target_directory, exist_ok=True)

# Get the current date in YYYY-MM-DD format
current_date = datetime.now().strftime('%Y-%m-%d')

# Define the filename with the current date
filename = f'news_tunisia_{current_date}.json'

# Define the full path to the file
file_path = os.path.join(target_directory, filename)

# Save the output to the JSON file in the specified directory with the date in the filename
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

print(f"News headlines have been successfully fetched and saved to '{file_path}'.")