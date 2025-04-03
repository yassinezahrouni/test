import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# Path to the JSON file containing magazine links
input_file_path = Path("/Users/yassinezahrouni/coding/test/SCM Magazines/SupplyChainMagazine_links.json")
output_file = input_file_path.parent / "supplychainmagazinearticles.json"

async def load_magazine_links():
    """Load magazine links from the JSON file and handle varying key names."""
    with open(input_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Possible key names
    name_keys = ["magazine name", "name", "magazine"]
    link_keys = ["link", "url", "homepage"]

    magazines = []
    
    for mag in data:
        mag_name = next((mag[key] for key in name_keys if key in mag), "Unknown Magazine")
        mag_link = next((mag[key] for key in link_keys if key in mag), None)
        
        if mag_link:
            magazines.append((mag_name, mag_link))

    return magazines


async def scrape_articles_from_homepage(magazine_name, homepage_url, page):
    """Extract article URLs from a magazine homepage."""
    await page.goto(homepage_url, wait_until="domcontentloaded")
    
    article_links = await page.query_selector_all("a[href]")  # General anchor tags
    extracted_links = set()

    for link in article_links:
        href = await link.get_attribute("href")
        if href and href.startswith("http") and homepage_url in href:
            extracted_links.add(href)

    return list(extracted_links)

async def scrape_article_details(magazine_name, article_url, page):
    """Extract article details from a given URL."""
    try:
        await page.goto(article_url, wait_until="domcontentloaded")

        title = await page.title()  # Get the title of the page
        summary = await page.query_selector_eval("meta[name='description']", "el => el.content") if await page.query_selector("meta[name='description']") else "No Summary"
        publication_date = await page.query_selector_eval("time", "el => el.innerText") if await page.query_selector("time") else "No Date"

        return {
            "magazine": magazine_name,
            "title": title,
            "url": article_url,
            "summary": summary,
            "publication_date": publication_date
        }
    except Exception as e:
        print(f"Failed to scrape article {article_url}: {e}")
        return None

async def main():
    """Run the scraper using Playwright."""
    scraped_articles = []
    
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)  # Use Mozilla Firefox
        context = await browser.new_context()
        page = await context.new_page()

        # Load magazine URLs from JSON
        magazines = await load_magazine_links()

        for magazine_name, homepage_url in magazines:
            print(f"Scraping homepage: {homepage_url}")
            try:
                article_urls = await scrape_articles_from_homepage(magazine_name, homepage_url, page)
                
                for article_url in article_urls:
                    article_data = await scrape_article_details(magazine_name, article_url, page)
                    if article_data:
                        scraped_articles.append(article_data)

            except Exception as e:
                print(f"Failed to scrape {magazine_name}: {e}")

        await browser.close()

    # Save scraped data
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(scraped_articles, f, ensure_ascii=False, indent=4)

    print(f"Scraped {len(scraped_articles)} articles. Data saved to {output_file}")

# Run the scraper
asyncio.run(main())
