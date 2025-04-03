import json
import time
import subprocess
import re
from newspaper import Article
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# **🔹 Define Supplier Country**
supplier_country = "Tunisia"

# **🔹 File Paths**
input_json_path = "/Users/yassinezahrouni/coding/test/All_sources_Links/All_NewsSourcesURLs.json"
article_urls_json_path = f"/Users/yassinezahrouni/coding/test/All_sources_Links/{supplier_country}_newsarticle_URLs.json"
output_json_path = f"/Users/yassinezahrouni/coding/test/All_sources_Links/ArticleDetails_{supplier_country}.json"

# **🔹 Run Article URL Extraction First**
print(f"🚀 Extracting article URLs for {supplier_country}...")
subprocess.run(["python", "/Users/yassinezahrouni/coding/test/All_sources_Links/Scraping_URLofArticles.py", supplier_country, input_json_path])

# **🔹 Read Extracted Article URLs**
try:
    with open(article_urls_json_path, "r", encoding="utf-8") as f:
        article_entries = json.load(f)
    print(f"✅ Loaded {len(article_entries)} article URLs for {supplier_country}.")
except FileNotFoundError:
    print(f"❌ Error: {article_urls_json_path} not found. Exiting.")
    exit()

# **🔹 Selenium Options**
def get_browser():
    """Creates and returns a new Selenium browser session."""
    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-images")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return webdriver.Chrome(options=options)

# **🔹 Restart browser after every N articles**
MAX_ARTICLES_PER_SESSION = 10
browser = get_browser()
article_results = []


def extract_article_text(soup):
    """Extracts main article text while removing unrelated content (cookies, ads, banners, etc.)."""
    
    # **🔹 Step 1: Identify main content container**
    article_container = soup.find("article")  # Look for <article> tag first
    if not article_container:
        article_container = soup.find("div", {"class": re.compile(r".*content.*|.*article.*", re.IGNORECASE)})

    # **🔹 Step 2: Extract paragraphs from main container**
    if article_container:
        paragraphs = article_container.find_all("p")
    else:
        paragraphs = soup.find_all("p")  # If no <article> or <div>, extract all <p> tags

    # **🔹 Step 3: Remove unwanted sections (cookie banners, ads, footers, sidebars)**
    unwanted_keywords = [
        "cookie", "privacy", "terms of service", "advertisement", "subscribe", "related articles",
        "footer", "disclaimer", "tracking", "ads", "sponsored"
    ]

    article_text = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text and not any(keyword in text.lower() for keyword in unwanted_keywords):
            article_text.append(text)

    # **🔹 Step 4: Join paragraphs into a full article text**
    full_text = " ".join(article_text)

    # **🔹 Step 5: Ensure text is long enough to be a real article**
    return full_text if len(full_text) > 300 else None  # Less than 300 chars is likely not an article

def extract_pub_date(soup):
    """Extracts the publication date from multiple sources (meta tags, time tags, and visible text)."""
    
    # **🔹 Check <time> tag with datetime attribute**
    time_tag = soup.find("time", {"datetime": True})
    if time_tag:
        return time_tag["datetime"]

    # **🔹 Check various meta tags for the publication date**
    meta_patterns = [
        {"property": "article:published_time"},
        {"name": "article:published_time"},
        {"property": "og:article:published_time"},
        {"name": "date"},
        {"name": "publish_date"},
        {"name": "pubdate"},
        {"name": "dcterms.created"},
    ]
    for pattern in meta_patterns:
        meta_tag = soup.find("meta", pattern)
        if meta_tag and meta_tag.get("content"):
            return meta_tag["content"]

    # **🔹 Backup: Try finding a date inside the visible text**
    date_match = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", soup.get_text())
    if date_match:
        return date_match.group(1)

    return None  # **If no date is found, return None**



def extract_article_details(entry):
    """Scrapes an article URL and extracts headline, pub date, article text, and source."""

    url = entry["Article_link"]
    global browser

    try:
        browser.get(url)
        time.sleep(2)
        html = browser.page_source
    except Exception as e:
        print(json.dumps({"error": f"❌ Error loading page: {e}"}))
        return None

    soup = BeautifulSoup(html, "html.parser")

    # **🔹 Extract Headline**
    headline = soup.find("h1")
    headline = headline.get_text(strip=True) if headline else "Headline not found"

    # **🔹 Extract Pub Date**
    pub_date = extract_pub_date(soup)

    # **🔹 Primary Extraction: Use Newspaper3k First**
    try:
        article = Article(url)
        article.download()
        article.parse()
        article_text = article.text  # Get text from Newspaper3k
    except Exception:
        article_text = None  # If Newspaper3k fails, fallback to BeautifulSoup

    # **🔹 Fallback Extraction: Use Improved BeautifulSoup if Needed**
    if not article_text or len(article_text) < 300:
        article_text = extract_article_text(soup)

    return {
        "Source_name": entry["Source_name"],
        "Article_link": url,
        "Country": entry["Country"],
        "Source_Link": urlparse(url).netloc,
        "Headline": headline,
        "Pub_date": pub_date if pub_date else "Date not found",
        "Article_text": article_text if article_text else "Article text not found",
    }


# **🔹 Process Articles with Session Restart**
for index, entry in enumerate(article_entries):
    # **Restart browser every N articles**
    if index > 0 and index % MAX_ARTICLES_PER_SESSION == 0:
        print("🔄 Restarting browser to prevent session crashes...")
        browser.quit()
        browser = get_browser()

    data = extract_article_details(entry)
    if data:
        article_results.append(data)
    time.sleep(2)

# **🔹 Save Output**
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(article_results, f, indent=4, ensure_ascii=False)

print(f"✅ Successfully saved extracted articles to {output_json_path}")

# **🔹 Close browser session**
browser.quit()
