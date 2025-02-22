import json
import os
import asyncio
from playwright.async_api import async_playwright

# File paths
input_json_path = "/Users/yassinezahrouni/coding/test/All_sources_Links/tunisia_article_links.json"
output_json_path = "/users/yassinezahrouni/coding/test/All_sources_Links/NewsArticles_tunisia.json"

# Ensure output directory exists
os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

# Function to extract article details using Playwright
async def extract_article_details(browser, article_entry):
    article_url = article_entry.get("Article Link")
    if not article_url:
        return None  # Skip if no URL

    try:
        context = await browser.new_context()  # New browser context per page
        page = await context.new_page()
        await page.goto(article_url, timeout=15000)  # 15 sec timeout

        # Extract article headline (title)
        headline = await page.title()

        # Extract article text (best-effort: use <article> tag or body)
        article_text = await page.evaluate("""
            () => {
                let article = document.querySelector('article') || document.body;
                return article ? article.innerText.trim() : "";
            }
        """)

        if not article_text:  # Skip empty articles
            return None

        # Extract publication date (if available)
        pub_date = await page.evaluate("""
            () => {
                let dateElement = document.querySelector('time') || document.querySelector('[datetime]');
                return dateElement ? dateElement.getAttribute('datetime') || dateElement.innerText.trim() : null;
            }
        """)

        await context.close()  # Free up resources

        # Format the extracted data while keeping original attributes
        return {
            "Country": article_entry.get("Country", "Unknown"),
            "Website": article_entry.get("Website", "Unknown"),
            "Article Link": article_url,
            "headline": headline.strip() if headline else None,
            "publication_date": pub_date.strip() if pub_date else None,
            "text": article_text
        }

    except Exception as e:
        print(f"Skipping article {article_url} due to error: {e}")
        return None

# Function to process all articles in parallel
async def scrape_articles():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Run in headless mode

        # Load article links from input JSON
        with open(input_json_path, "r", encoding="utf-8") as infile:
            articles_data = json.load(infile)

        # Process articles in parallel
        tasks = [extract_article_details(browser, entry) for entry in articles_data]
        results = await asyncio.gather(*tasks)

        # Remove None values (failed extractions)
        extracted_articles = [article for article in results if article]

        # Save results to JSON
        with open(output_json_path, "w", encoding="utf-8") as outfile:
            json.dump(extracted_articles, outfile, indent=4, ensure_ascii=False)

        print(f"Extracted {len(extracted_articles)} articles saved to {output_json_path}")

# Run the scraper
asyncio.run(scrape_articles())
