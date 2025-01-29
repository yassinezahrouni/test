import json
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def extract_newspaper_data(page_content, region, is_usa_state=False):
    """
    Extracts newspaper links, names, and additional data from the page content.
    Args:
        page_content (str): The HTML content of the page.
        region (str): The region (country or state) name.
        is_usa_state (bool): Whether the region is a US state (adjusts element mapping).
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

            # Extract additional elements based on whether it's a US state or country list
            additional_elements = row.find_all("td")[1:]  # Skip the first column (name/link)
            if is_usa_state:
                city = additional_elements[0].get_text(strip=True) if len(additional_elements) > 0 else None
                language = additional_elements[1].get_text(strip=True) if len(additional_elements) > 1 else None
                newspaper_data = {
                    "region": region,
                    "name": name,
                    "paperboy_page": paperboy_page,
                    "city": city,
                    "language": language,
                }
            else:
                city = additional_elements[0].get_text(strip=True) if len(additional_elements) > 0 else None
                state = additional_elements[1].get_text(strip=True) if len(additional_elements) > 1 else None
                language = additional_elements[2].get_text(strip=True) if len(additional_elements) > 2 else None
                newspaper_data = {
                    "region": region,
                    "name": name,
                    "paperboy_page": paperboy_page,
                    "city": city,
                    "state": state,
                    "language": language,
                }

            newspapers.append(newspaper_data)
            print(f"Row {idx + 1}: Found newspaper - {newspaper_data}")
        except Exception as e:
            print(f"Row {idx + 1}: Error processing row - {e}")

    print(f"Extracted {len(newspapers)} newspapers for {region}")
    return newspapers


def scrape_newspapers_links(input_file, output_file, is_usa_state=False):
    """
    Scrapes newspaper links from the list of country/state pages and saves them to a JSON file.
    Args:
        input_file (str): Path to the JSON file with the list of country/state links.
        output_file (str): Path to the output JSON file to save the newspaper details.
        is_usa_state (bool): Whether the input file is for US state-level newspapers.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        country_state_links = json.load(f)

    print(f"Loaded {len(country_state_links)} country/state links from {input_file}")
    all_newspapers = []

    for idx, entry in enumerate(country_state_links):
        region_name = entry["name"]
        url = entry["url"]
        print(f"\n[{idx + 1}/{len(country_state_links)}] Scraping: {region_name} - {url}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = context.new_page()
            try:
                page.goto(url, timeout=60000)  # Wait up to 60 seconds for the page to load
                page.wait_for_selector("tr[bgcolor]", timeout=10000)  # Wait for newspaper rows to appear
                print(f"Page loaded successfully for {region_name}")

                page_content = page.content()
                newspapers = extract_newspaper_data(page_content, region_name, is_usa_state)

                # Debugging: Log HTML if no rows are found
                if not newspapers:
                    with open(f"debug_{region_name}.html", "w", encoding="utf-8") as debug_file:
                        debug_file.write(page_content)
                    print(f"Saved debug HTML for {region_name} to debug_{region_name}.html")

                all_newspapers.extend(newspapers)
                print(f"Total newspapers so far: {len(all_newspapers)}")

            except Exception as e:
                print(f"Error scraping {region_name} ({url}): {e}")
            finally:
                page.close()
                context.close()
                browser.close()

            # Save intermediate results after each region
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_newspapers, f, indent=4)
            print(f"Intermediate results saved to {output_file}")

        time.sleep(2)  # Avoid rapid requests

    print(f"Scraping complete. Total newspapers extracted: {len(all_newspapers)}")
    print(f"Results saved to {output_file}")


# Example Usage
if __name__ == "__main__":
    # For country-level lists (3 elements: city, state, language)
    scrape_newspapers_links(
        input_file="thepaperboy_countrynewslist_links.json",
        output_file="newspaper_links_country.json",
        is_usa_state=False
    )

    # For US state-level lists (2 elements: city, language)
    scrape_newspapers_links(
        input_file="thepaperboy_usastatesnewslist_links.json",
        output_file="newspaper_links_us_states.json",
        is_usa_state=True
    )
