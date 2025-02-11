import feedparser
import json
import os
import re
from bs4 import BeautifulSoup

def parse_summary(summary):
    """
    Given the summary text from a warning entry (which contains several sections 
    indicated by "* WHAT...", "* WHERE...", etc.), extract the sections as separate fields.
    Returns a dict with keys: what, where, when, impacts.
    """
    summary = summary.strip()
    parts = re.split(r"\*\s+", summary)
    result = {}
    for part in parts:
        part = part.strip()
        if not part:
            continue
        match = re.match(r"(\w+)\.\.\.(.*)", part, re.DOTALL)
        if match:
            label = match.group(1).strip().lower()  # e.g., what, where, when, impacts
            content = match.group(2).strip().replace("\n", " ")
            result[label] = content
    return result

def extract_warning(entry):
    """
    Extracts required fields from a CAP/ATOM warning entry.
    Returns a dict with the following keys:
      - link
      - updated
      - published
      - title
      - what, where, when, impacts (extracted from summary)
      - cap_event
      - cap_sent
      - cap_effective
      - eventbegin (from cap:onset)
      - eventend (from cap:expires)
      - cap_status
      - cap_msgType
      - cap_category
      - cap_urgency
      - cap_severity
      - cap_certainty
      - cap_areaDesc
      - cap_geocode
    """
    warning = {}
    warning["link"] = entry.get("link", "")
    warning["updated"] = entry.get("updated", "")
    warning["published"] = entry.get("published", "")
    warning["title"] = entry.get("title", "").strip()
    
    summary_raw = entry.get("summary", "")
    summary_fields = parse_summary(summary_raw) if summary_raw else {}
    warning["what"] = summary_fields.get("what", "")
    warning["where"] = summary_fields.get("where", "")
    warning["when"] = summary_fields.get("when", "")
    warning["impacts"] = summary_fields.get("impacts", "")
    
    warning["cap_event"] = entry.get("cap_event", "")
    warning["cap_sent"] = entry.get("cap_sent", "")
    warning["cap_effective"] = entry.get("cap_effective", "")
    # Rename cap:onset to eventbegin and add cap:expires as eventend
    warning["eventbegin"] = entry.get("cap_onset", "")
    warning["eventend"] = entry.get("cap_expires", "")
    warning["cap_status"] = entry.get("cap_status", "")
    warning["cap_msgType"] = entry.get("cap_msgtype", "") or entry.get("cap_msgType", "")
    warning["cap_category"] = entry.get("cap_category", "")
    warning["cap_urgency"] = entry.get("cap_urgency", "")
    warning["cap_severity"] = entry.get("cap_severity", "")
    warning["cap_certainty"] = entry.get("cap_certainty", "")
    warning["cap_areaDesc"] = entry.get("cap_areadesc", "") or entry.get("cap_areaDesc", "")
    warning["cap_geocode"] = entry.get("cap_geocode", "")
    
    return warning

def main():
    # Set the URL of the CAP/ATOM feed.
    feed_url = "https://api.weather.gov/alerts"
    
    # Parse the feed using feedparser.
    feed = feedparser.parse(feed_url)
    
    warnings_list = []
    for entry in feed.entries:
        warning = extract_warning(entry)
        # Only include warnings that have a non-empty title
        if warning.get("title", "").strip():
            warnings_list.append(warning)
    
    # Define output path
    output_dir = "WeatherData"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "WeatherAlerts.json")
    
    # Save the extracted warnings as JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(warnings_list, f, ensure_ascii=False, indent=4)
    
    print(f"Extracted {len(warnings_list)} warnings to {output_file}")

if __name__ == "__main__":
    main()
