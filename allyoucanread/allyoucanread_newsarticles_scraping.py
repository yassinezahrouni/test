import json
import os
import datetime
from playwright.sync_api import sync_playwright

# Load the list of news websites from the input JSON file
input_file = "allyoucanread/allyoucanread_news_sources_websites.json"

def load_news_sources(file_path):
    """Loads the list of news websites from the input JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_articles_from_page(page, source):
    """Extracts news articles from a given news page."""
    articles = []
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Try different possible article selectors
    article_elements = page.query_selector_all("article") or \
                       page.query_selector_all("div.news-item") or \
                       page.query_selector_all("div.post")

    for article in article_elements:
        try:
            headline_element = article.query_selector("h1, h2, h3, a")
            link_element = article.query_selector("a[href]")
            date_element = article.query_selector("time")

            headline = headline_element.inner_text(strip=True) if headline_element else "Unknown"
            article_url = link_element.get_attribute("href") if link_element else ""
            article_url = page.url if not article_url.startswith("http") else article_url
            publishing_date = date_element.get_attribute("datetime") if date_element else today_date
            category_element = article.query_selector("div.category, span.category")
            category = category_element.inner_text(strip=True) if category_element else "Unknown"
            
            # Open the article page and extract full text
            page.goto(article_url, timeout=10000)
            article_text = page.inner_text("body")[:1000]  # Limit text to avoid huge files

            articles.append({
                "name": source["name"],
                "Source_url": source["url"],
                "Country": source["Country"],
                "Headline": headline,
                "Publishing date": publishing_date,
                "Article Text": article_text,
                "Article category": category,
                "Article URL": article_url
            })

            page.go_back()  # Return to main page
        except Exception as e:
            print(f"Skipping an article due to error: {e}")

    return articles

def scrape_news_articles():
    """Scrapes news articles from the list of sources and saves them to a JSON file."""
    sources = load_news_sources(input_file)
    all_articles = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for source in sources:
            print(f"Scraping news from {source['name']} ({source['url']})...")
            try:
                page.goto(source["url"], timeout=10000)
                articles = extract_articles_from_page(page, source)
                all_articles.extend(articles)
            except Exception as e:
                print(f"Failed to scrape {source['name']}: {e}")

        browser.close()

        # ------------------- FIXED INDENTATION -------------------
        # Save extracted articles to the output JSON file
        output_dir = "allyoucanread"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "allyoucanread_sources_articles.json")

        with open(output_file, "w", encoding="utf-8") as outfile:
            json.dump(all_articles, outfile, ensure_ascii=False, indent=4)

        print(f"Scraped {len(all_articles)} newspaper records. Data saved to {output_file}")

# Run the scraper
scrape_news_articles()
