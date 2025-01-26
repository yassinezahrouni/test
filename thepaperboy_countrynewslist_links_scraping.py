import json
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def extract_newspaper_data(page_content, region):
    """
    Extracts newspaper links, names, and additional data from the page content.
    Args:
        page_content (str): The HTML content of the page.
        region (str): The region (country or state) name.
    Returns:
        list: A list of dictionaries with newspaper details.
    """
    print(f"Extracting data for region: {region}")
    soup = BeautifulSoup(page_content, "html.parser")
    newspapers = []

    # Find all rows with bgcolor="#ffffff" or "#efefef"
    rows = soup.find_all("tr", {"bgcolor": ["#ffffff", "#efefef"]})
    print(f"Found {len(rows)} rows with newspaper data for {region}")

    for idx, row in enumerate(rows):
        try:
            # Extract name and link
            name_tag = row.find("td", align="left").find("a", href=True)
            if not name_tag:
                print(f"Row {idx + 1}: No name or link found, skipping.")
                continue

            name = name_tag.text.strip()
            link = name_tag["href"]
            paperboy_page = f"https://www.thepaperboy.com{link}"

            newspaper_data = {
                "region": region,
                "name": name,
                "paperboy_page": paperboy_page
            }
            newspapers.append(newspaper_data)
            print(f"Row {idx + 1}: Found newspaper - Name: {name}, Link: {paperboy_page}")
        except Exception as e:
            print(f"Row {idx + 1}: Error processing row - {e}")

    print(f"Extracted {len(newspapers)} newspapers for {region}")
    return newspapers


def scrape_newspapers_links(input_file, output_file):
    """
    Scrapes newspaper links from the list of country/state pages and saves them to a JSON file.
    Args:
        input_file (str): Path to the JSON file with the list of country/state links.
        output_file (str): Path to the output JSON file to save the newspaper details.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        country_state_links = json.load(f)

    print(f"Loaded {len(country_state_links)} country/state links from {input_file}")
    all_newspapers = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15"
        )

        for idx, entry in enumerate(country_state_links):
            region_name = entry["name"]
            url = entry["url"]
            print(f"\n[{idx + 1}/{len(country_state_links)}] Scraping: {region_name} - {url}")

            page = context.new_page()
            try:
                page.goto(url, timeout=60000)  # Wait up to 60 seconds to load the page
                print(f"Page loaded successfully for {region_name}")

                page_content = page.content()
                newspapers = extract_newspaper_data(page_content, region_name)
                all_newspapers.extend(newspapers)

                print(f"Total newspapers so far: {len(all_newspapers)}")
            except Exception as e:
                print(f"Error scraping {region_name} ({url}): {e}")
            finally:
                page.close()

            # Save intermediate results after processing each region
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(all_newspapers, f, indent=4)
                print(f"Intermediate results saved to {output_file}")
            except Exception as e:
                print(f"Error saving intermediate results: {e}")

            time.sleep(2)  # Prevent rapid requests

        browser.close()

    print(f"Scraping complete. Total newspapers extracted: {len(all_newspapers)}")
    print(f"Results saved to {output_file}")


# Example Usage
if __name__ == "__main__":
    input_file = "thepaperboy_countrynewslist_links.json"  # Input file with country/state links
    output_file = "newspaper_links.json"  # Output file for extracted newspaper details
    scrape_newspapers_links(input_file, output_file)
