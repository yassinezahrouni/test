import json
import os
import re
from playwright.sync_api import sync_playwright

def extract_region_from_title(title):
    """
    Given a title string such as "Top 100 Newspapers in North America",
    extract the substring after "in" (case-insensitive). If not found, return the full title.
    """
    match = re.search(r"(?i)\bin\s+(.*)", title)
    if match:
        return match.group(1).strip()
    else:
        return title.strip()

def scrape_newspapers_from_region(page, region_title):
    """
    From the currently loaded page, scrape the newspaper entries.
    Each entry is in a table row with a <td class="i"> containing the link.
    The link's <img> element has a src attribute of the form:
      "https://www.google.com/s2/favicons?domain=http://www.nytimes.com"
    We extract the domain parameter from the URL.
    """
    newspapers = []
    # Find all rows in the table (adjust selector if needed)
    rows = page.query_selector_all("tr")
    for row in rows:
        try:
            td = row.query_selector("td.i")
            if not td:
                continue
            # Get the <a> element inside the td
            a_elem = td.query_selector("a")
            if not a_elem:
                continue
            # Get the newspaper name – inner text of the link, stripped.
            # This should be something like "The New York Times" or "The Guardian"
            newspaper_name = a_elem.inner_text().strip()
            # Get the <img> element within the link
            img_elem = a_elem.query_selector("img")
            if not img_elem:
                continue
            img_src = img_elem.get_attribute("src")
            # Extract the domain parameter from the img src.
            # The src should look like: 
            # "https://www.google.com/s2/favicons?domain=http://www.nytimes.com"
            match = re.search(r"domain=([^&]+)", img_src)
            if match:
                newspaper_link = match.group(1).strip()
            else:
                newspaper_link = ""
            # Append the result (with region to be added later)
            newspapers.append({
                "newspaper": newspaper_name,
                "link": newspaper_link
            })
        except Exception as e:
            print("Error processing a row:", e)
    return newspapers

def main():
    # Load the JSON file with region links.
    input_file = "Regions_top_newssources/top_sources_links.json"
    if not os.path.exists(input_file):
        print(f"Input file '{input_file}' does not exist.")
        return

    with open(input_file, "r", encoding="utf-8") as infile:
        region_links = json.load(infile)

    all_newspapers = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Process each region entry from the JSON file.
        for entry in region_links:
            title = entry.get("title", "")
            url = entry.get("url", "")
            if not url:
                continue

            # Extract the region from the title (substring after "in")
            region = extract_region_from_title(title)
            print(f"Processing region: {region} from title: '{title}' - URL: {url}")

            # Navigate to the region URL
            try:
                page.goto(url)
                page.wait_for_load_state("networkidle")
            except Exception as e:
                print(f"Error loading URL {url}: {e}")
                continue

            # Scrape the newspapers on this page.
            newspapers = scrape_newspapers_from_region(page, title)
            # Add the region attribute to each newspaper record.
            for record in newspapers:
                record["region"] = region
            all_newspapers.extend(newspapers)

        browser.close()

    # Ensure output folder exists.
    output_dir = "Regions_top_newssources"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "top_newssources.json")
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(all_newspapers, outfile, ensure_ascii=False, indent=4)

    print(f"Scraped {len(all_newspapers)} newspaper records. Data saved to {output_file}")

if __name__ == "__main__":
    main()
