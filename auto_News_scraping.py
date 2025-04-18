import os
import json
import xmltodict
import requests
from googletrans import Translator
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from newspaper import Article  # Optional: Requires newspaper3k

# Configure logging
logging.basicConfig(
    filename='news_scraper.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize the Google Translator
translator = Translator()

def get_rss(url: str) -> dict:
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
        logging.error(f"Translation error: {e}")
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
        logging.error(f"Error parsing date: {e}")
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
        # Using newspaper3k for better extraction
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        logging.error(f"Error fetching full article from {url}: {e}")
        return f"Error fetching full article: {e}"

def load_news_feeds(config_path: str, country: str) -> list:
    """
    Load the list of news feeds for the specified country from the configuration file.
    Args:
        config_path (str): Path to the JSON configuration file.
        country (str): The country for which to load news feeds.
    Returns:
        list: A list of dictionaries containing 'source' and 'url' keys.
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            feeds = json.load(f)
        return feeds.get(country, [])
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        return []

def validate_json(file_path: str):
    """
    Validate the JSON file to ensure it is properly formatted.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        logging.info(f"JSON file '{file_path}' is valid.")
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON format in file '{file_path}': {e}")

def main(country: str):
    # Path to the configuration file
    config_path = 'news_feeds.json'
    
    # Load news feeds for the specified country
    rss_feeds = load_news_feeds(config_path, country)
    
    if not rss_feeds:
        logging.warning(f"No RSS feeds found for country: {country}")
        print(f"No RSS feeds found for country: {country}")
        return
    
    # Dictionary to store the count of headlines per source
    news_counts = {feed["source"]: 0 for feed in rss_feeds}
    
    # List to store all articles
    articles = []
    
    # Fetch and process news from all RSS feeds
    logging.info(f"Fetching and processing news headlines for {country}...")
    print(f"Fetching and processing news headlines for {country}...")
    
    for feed in rss_feeds:
        source = feed["source"]
        rss_url = feed["url"]
        try:
            data = get_rss(rss_url)
            # Navigate to the list of items; RSS structure may vary
            items = []
            if 'rss' in data and 'channel' in data['rss']:
                items = data['rss']['channel']['item']
            elif 'feed' in data and 'entry' in data['feed']:
                items = data['feed']['entry']
            else:
                logging.warning(f"Unrecognized RSS format for source: {source}")
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
                        logging.error(f"Error parsing publication time: {e}")

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
            logging.error(f"Error fetching news from {source}: {e}")
            print(f"Error fetching news from {source}: {e}")
    
    if not articles:
        logging.info(f"No today's news found for country: {country}")
        print(f"No today's news found for country: {country}")
        return

    # Prepare the output
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
    
    # Define the filename with the current date and country
    filename = f'news_{country.lower()}_{current_date}.json'
    
    # Define the full path to the file
    file_path = os.path.join(target_directory, filename)
    
    # Save the output to the JSON file in the specified directory with the date in the filename
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
        logging.info(f"News headlines have been successfully fetched and saved to '{file_path}'.")
        print(f"News headlines have been successfully fetched and saved to '{file_path}'.")
    except Exception as e:
        logging.error(f"Error saving JSON file: {e}")
        print(f"Error saving JSON file: {e}")
        return

    # Validate the JSON file
    validate_json(file_path)

if __name__ == "__main__":
    # Specify the country you want to fetch news for
    # Example: "Poland"
    country_input = "Poland"
    main(country_input)
