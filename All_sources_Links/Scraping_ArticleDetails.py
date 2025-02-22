import json
import time
import re
from newspaper import Article
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# **🔹 Define the supplier country**
supplier_country = "Tunisia"

# **🔹 File paths**
input_json_path = "/Users/yassinezahrouni/coding/test/allyoucanread/allyoucanread_news_sources_websites.json"
output_json_path = f"/Users/yassinezahrouni/coding/test/All_sources_Links/ArticleDetails_{supplier_country}.json"

# **🔹 Set up Selenium Options**
options = Options()
options.headless = True  # **Run in headless mode**
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-images")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# **🔹 Initialize a single Selenium browser session**
browser = webdriver.Chrome(options=options)

def extract_article_details(entry):
    """Scrapes an article URL using Selenium and extracts details, while keeping input info."""
    
    url = entry["link"]  # Extract URL from input JSON
    try:
        browser.get(url)
        time.sleep(2)  # **Wait for page to load fully**
        html = browser.page_source
    except Exception as e:
        print(json.dumps({"error": f"❌ Error loading page: {e}"}))
        return None

    soup = BeautifulSoup(html, "html.parser")

    # **🔹 Extract Headline**
    headline = soup.find("h1")
    headline = headline.get_text(strip=True) if headline else "Headline not found"

    # **🔹 Extract Full Article Text (More Robust)**
    article_text = extract_article_text(soup)

    # **🔹 Extract Source (Base Domain)**
    source = urlparse(url).netloc

    # **🔹 Extract Pub Date (Improved)**
    pub_date = extract_pub_date(soup)

    # **🔹 Use Newspaper3k if Missing Data**
    if not headline or not pub_date or not article_text:
        print("⚠️ Missing data. Using Newspaper3k as fallback...")
        time.sleep(1)
        article_data = extract_fallback_newspaper(url)

        if not headline or headline == "Headline not found":
            headline = article_data["headline"]
        if not pub_date:
            pub_date = article_data["pub_date"]
        if not article_text:
            article_text = article_data["article_text"]

    # **🔹 Validate if this is a real article**
    if not is_valid_article(url, headline, pub_date, article_text):
        print(f"❌ Skipping non-article page: {url}")
        return None

    # **🔹 Create JSON Response (Includes Input Details & Renames "link" to "Article_link")**
    return {
        "Source_name": entry["name"],
        "Article_link": entry["link"],
        "Country": entry["Country"],
        "Source_Link": source,
        "Headline": headline,
        "Pub_date": pub_date if pub_date else "Date not found",
        "Article_text": article_text if article_text else "Article text not found",
    }

def extract_article_text(soup):
    """Extracts article text and removes cookie banners & unrelated text."""
    unwanted_classes = ["cookie", "banner", "advertisement", "related", "subscribe", "footer"]

    paragraphs = []
    for p in soup.find_all("p"):
        if not any(cls in p.get("class", []) for cls in unwanted_classes):
            paragraphs.append(p.get_text(strip=True))

    article_text = " ".join(paragraphs)
    
    # ✅ Backup: Check <div> or <article> if <p> is missing
    if not article_text or len(article_text) < 200:
        div_text = soup.find("div", {"class": re.compile(r".*article.*|.*content.*", re.IGNORECASE)})
        if div_text:
            article_text = div_text.get_text(strip=True)

    return article_text if article_text and len(article_text) > 200 else None

def extract_pub_date(soup):
    """Extracts publication date from multiple sources."""
    
    time_tag = soup.find("time", {"datetime": True})
    if time_tag:
        return time_tag["datetime"]

    meta_patterns = [
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

    # ✅ Backup: Search for a date inside the visible article text
    date_match = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", soup.get_text())
    if date_match:
        return date_match.group(1)

    return None  

def extract_fallback_newspaper(url):
    """Extracts article details using Newspaper3k as a backup method."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return {
            "headline": article.title if article.title else None,
            "pub_date": str(article.publish_date) if article.publish_date else None,
            "article_text": article.text if article.text else None
        }
    except Exception:
        return {"headline": None, "pub_date": None, "article_text": None}

def is_valid_article(url, headline, pub_date, article_text):
    """Loosened check for valid article URLs."""
    
    if not headline or headline == "Headline not found":
        print(f"🔍 Debug: Skipping {url} because no headline found.")
        return False  

    if not article_text or len(article_text) < 200:  
        print(f"🔍 Debug: Skipping {url} because text is too short.")
        return False

    # ✅ Loosened: Allow more URL formats
    path_segments = urlparse(url).path.strip("/").split("/")
    
    if len(path_segments) > 1:
        return True  # ✅ Allow URLs with at least 1 subdirectory

    return False  

# **🔹 Read Input JSON and Filter for the Supplier Country**
with open(input_json_path, "r", encoding="utf-8") as f:
    all_sources = json.load(f)

# **🔹 Filter URLs for the supplier country**
urls = [entry for entry in all_sources if entry["Country"] == supplier_country]

# **🔹 Extract Articles and Store in List**
article_results = []
for entry in urls:
    article_data = extract_article_details(entry)
    if article_data:
        article_results.append(article_data)
    time.sleep(2)  # **Pause between requests to prevent rate limiting**

# **🔹 Save Output JSON**
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(article_results, f, indent=4, ensure_ascii=False)

print(f"✅ Successfully saved extracted articles to {output_json_path}")

# **🔹 Close browser session after all articles are processed**
browser.quit()
