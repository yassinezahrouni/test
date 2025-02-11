import re
import json
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_weather_warnings():
    with sync_playwright() as p:
        # Launch the browser in headless mode.
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the WMO severe weather warnings page.
        page.goto("https://severeweather.wmo.int/list.html")

        # -----------------------------------------
        # Step 1: Select "All" from the dropdown menu.
        try:
            page.wait_for_selector("select[name='list_container_length']", timeout=10000)
            # Select the option with value "-1" (which represents "All").
            page.select_option("select[name='list_container_length']", value="-1")
            print("Dropdown selection set to 'All' entries.")
        except Exception as e:
            print("Error selecting 'All' from dropdown:", e)

        # Allow time for the table to refresh after selecting "All".
        page.wait_for_timeout(5000)

        # -----------------------------------------
        # Step 2: Click on the "show all nodes" button if present.
        try:
            page.wait_for_selector("button:has-text('nodes')", timeout=10000)
            page.click("button:has-text('nodes')")
            print("Clicked on 'show all nodes' button.")
        except Exception as e:
            print("Could not find or click the 'show all nodes' button. Proceeding with the current list.", e)

        # Wait a few seconds to ensure that all entries are loaded.
        page.wait_for_timeout(5000)

        # -----------------------------------------
        # Step 3: Scrape all weather warning rows.
        rows = page.query_selector_all("tr.odd, tr.even")
        warnings = []

        for row in rows:
            try:
                tds = row.query_selector_all("td")
                # Ensure the row contains at least 6 columns.
                if len(tds) < 6:
                    continue

                # --- TIME EXTRACTION ---
                # Extract the event time from the onclick attribute of the event link.
                event_a = row.query_selector("a.eventname.forNormal")
                extracted_time = ""
                if event_a:
                    onclick_attr = event_a.get_attribute("onclick")
                    # Example: getDetail('capURL','us-noaa-nws-en-marine/2025/02/11/12/19/00-c5c27d67709ae413dc153f87bd942b6c.xml','093');
                    match = re.search(r"getDetail\([^,]+,\s*'([^']+)'", onclick_attr)
                    if match:
                        url_part = match.group(1)
                        parts = url_part.split('/')
                        if len(parts) >= 6:
                            date_from_click = f"{parts[1]}.{parts[2]}.{parts[3]}"
                            time_from_click = f"{parts[4]}:{parts[5]}"
                            extracted_time = f"{date_from_click} {time_from_click}"
                else:
                    extracted_time = ""

                # --- EVENT NAME ---
                event_name = event_a.inner_text().strip() if event_a else ""

                # --- ISSUED TIME ---
                issued_time = tds[1].inner_text().strip()

                # --- SEVERITY, URGENCY, CERTAINTY ---
                # Instead of relying on splitlines() from inner_text (which sometimes doesn't work as expected),
                # we get the inner HTML, replace <br> tags with newline characters,
                # remove any remaining HTML tags, and then split into lines.
                detail_html = tds[2].inner_html()
                # Replace <br> or <br/> (with or without extra spaces) with newline.
                detail_text = re.sub(r"<br\s*/?>", "\n", detail_html, flags=re.IGNORECASE)
                # Remove any other HTML tags.
                detail_text = re.sub(r"<.*?>", "", detail_text)
                detail_text = detail_text.strip()

                severity = urgency = certainty = ""
                for line in detail_text.split("\n"):
                    line = line.strip()
                    if line.lower().startswith("s:"):
                        severity = line.split(":", 1)[1].strip()
                    elif line.lower().startswith("u:"):
                        urgency = line.split(":", 1)[1].strip()
                    elif line.lower().startswith("c:"):
                        certainty = line.split(":", 1)[1].strip()

                # --- COUNTRY ---
                country = tds[3].inner_text().strip()

                # --- LOCATION DESCRIPTION ---
                location_description = ""
                loc_span = tds[4].query_selector("span.ad.forNormal")
                if loc_span:
                    location_description = loc_span.inner_text().strip()

                # --- REGION ---
                region = tds[5].inner_text().strip().replace('\n', ' ')

                # Build the warning record.
                warning = {
                    "time": extracted_time,
                    "event_name": event_name,
                    "issued_time": issued_time,
                    "severity": severity,
                    "urgency": urgency,
                    "certainty": certainty,
                    "country": country,
                    "location_description": location_description,
                    "region": region
                }
                warnings.append(warning)
            except Exception as ex:
                print("Error processing a row:", ex)

        # -----------------------------------------
        # Step 4: Save the results to a JSON file.
        directory = "WeatherData/WMO warnings"
        os.makedirs(directory, exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{directory}/weatherwarning_{date_str}_SourceWMO.json"
        with open(filename, "w", encoding="utf-8") as outfile:
            json.dump(warnings, outfile, ensure_ascii=False, indent=4)

        print(f"Scraped {len(warnings)} warnings. Data saved to {filename}")
        browser.close()

if __name__ == "__main__":
    scrape_weather_warnings()
