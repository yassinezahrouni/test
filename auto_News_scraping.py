import requests
import xmltodict
from googletrans import Translator
from datetime import datetime
from bs4 import BeautifulSoup

# Initialize the Google Translator
translator = Translator()

def find_top_news_sites():
    """
    Search for the top Tunisian news websites using a query.
    Returns:
        list: List of top 10 news websites.
    """
    query = "top Tunisian news websites"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"}
    response = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract search results
    sites = []
    for link in soup.find_all("a", href=True):
        href = link.get("href")
        if "http" in href and "google.com" not in href:
            site = href.split("&")[0].split("=")[-1]
            if site not in sites:
                sites.append(site)
        if len(sites) >= 10:  # Limit to top 10 sites
            break
    return sites

def find_rss_feed(website):
    """
    Attempt to discover the RSS feed URL of a website.
    Args:
        website (str): The website URL.
    Returns:
        str: RSS feed URL or None if not found.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"}
    paths = ["/rss", "/feed", "/feeds", "/rss.xml"]
    
    # Check common RSS paths
    for path in paths:
        rss_url = f"{website.rstrip('/')}{path}"
        response = requests.get(rss_url, headers=headers)
        if response.status_code == 200 and "<rss" in response.text.lower():
            return rss_url

    # Inspect <link> tags for RSS feeds
    response = requests.get(website, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    link_tag = soup.find("link", {"type": "application/rss+xml"})
    if link_tag and link_tag.get("href"):
        return link_tag["href"]
    return None

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

# Automatically find top 10 Tunisian news websites and their RSS feeds
print("Finding top Tunisian news websites...")
news_sites = find_top_news_sites()
rss_feeds = []

for site in news_sites:
    rss_feed = find_rss_feed(site)
    if rss_feed:
        rss_feeds.append({"source": site, "url": rss_feed})
    if len(rss_feeds) >= 10:
        break

# Fetch and process news from all RSS feeds
print("Translated News Headlines:")
print("-" * 50)
news_counter = 1
news_counts = {feed["source"]: 0 for feed in rss_feeds}

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
