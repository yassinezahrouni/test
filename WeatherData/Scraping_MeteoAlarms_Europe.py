import feedparser
import json
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime

def extract_warning_info(item):
    """
    Given a feed item, extract:
      - location (from the <title> tag)
      - warning_description (the text following "English(en-GB):" in the description's HTML)
      - from_date and until_date (if available, extracted from date strings in the description)
      - pubDate and link
    """
    location = item.get("title", "").strip()
    pubDate = item.get("pubDate", "").strip()
    link = item.get("link", "").strip()
    description_html = item.get("description", "")
    
    # Parse the description (which is HTML wrapped in CDATA)
    soup = BeautifulSoup(description_html, "html.parser")
    
    # Initialize variables
    warning_desc = ""
    from_date = ""
    until_date = ""
    
    # Look for the <td> that contains "English(en-GB):"
    for td in soup.find_all("td"):
        td_text = td.get_text(separator=" ", strip=True)
        if "English(en-GB):" in td_text:
            # Remove the prefix and trim the result
            warning_desc = td_text.split("English(en-GB):", 1)[1].strip()
            break

    # Extract date strings using a regex pattern for ISO-like timestamps.
    # The description usually contains two dates: one after "From:" and one after "Until:"
    description_text = soup.get_text(" ", strip=True)
    dates = re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}", description_text)
    if len(dates) >= 2:
        from_date = dates[0]
        until_date = dates[1]

    return {
        "location": location,
        "warning_description": warning_desc,
        "from": from_date,
        "until": until_date,
        "pubDate": pubDate,
        "link": link
    }

def process_feed(rss_url, country):
    """
    Parse the RSS feed at rss_url and extract warning info from each item.
    Attach the country (from the input feed JSON) to each warning.
    """
    warnings = []
    parsed_feed = feedparser.parse(rss_url)
    for item in parsed_feed.entries:
        info = extract_warning_info(item)
        info["country"] = country
        warnings.append(info)
    return warnings

def main():
    # Input file (inside WeatherData folder)
    input_file = os.path.join("WeatherData", "RSSfeed_WeatherAlerts_europeanCountries.json")
    with open(input_file, "r", encoding="utf-8") as f:
        feeds = json.load(f)
    
    all_warnings = []
    for feed in feeds:
        country = feed.get("country", "Unknown")
        rss_url = feed.get("rss_feed")
        if not rss_url:
            continue
        print(f"Processing feed for {country}: {rss_url}")
        warnings = process_feed(rss_url, country)
        # Filter out warnings with an empty description
        warnings = [w for w in warnings if w.get("warning_description", "").strip() != ""]
        all_warnings.extend(warnings)
    
        ## Assume all_warnings is already defined from your code
    output_dir = "All_sources_Links"
    os.makedirs(output_dir, exist_ok=True)
    today = datetime.now()
    formatted_date = today.strftime("%Y%m%d")  # format to avoid invalid filename characters
    output_file = os.path.join(output_dir, f"consolidated_data_from_RSS_links_files_{formatted_date}.json")

    # Read existing consolidated data if available.
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            consolidated_data = json.load(f)
    else:
        consolidated_data = {}

    # Optionally, you can record the date separately if needed.
    today_date = datetime.today().strftime('%Y-%m-%d')
    # For this example, we simply store the warnings under the key "weather_warning_europe".
    consolidated_data["Europe_region_weather_alerts"] = all_warnings

    # Write the updated consolidated data back to the file.
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(consolidated_data, f, ensure_ascii=False, indent=4)

    print(f"Extracted {len(all_warnings)} warnings to {output_file}")

if __name__ == "__main__":
    main()
