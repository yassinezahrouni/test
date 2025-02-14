import pandas as pd
import re
from playwright.sync_api import sync_playwright

# Function to slugify port and country
def slugify_port(port, country):
    port = port.strip().lower()
    if port.startswith("port of "):
        port = port[len("port of "):].strip()
    if port.endswith(" port"):
        port = port[:-len(" port")].strip()
    port_slug = port.replace(" ", "-")
    
    # Special exceptions
    if port_slug == "busan":
        port_slug = "busan-pusan"
    elif port_slug == "incheon":
        port_slug = "incheon-inchon"
    elif port_slug.startswith("vancouver"):
        port_slug = "metro-vancouver"
    elif port_slug == "genoa":
        port_slug = "genoa-genova"
    
    country = re.sub(r'\d+', '', country).strip().lower()
    mapping = {"usa": "united-states", "us": "united-states", "uk": "united-kingdom"}
    if country in mapping:
        country = mapping[country]
    else:
        country = country.replace(" ", "-")
    
    return f"port-of-{port_slug},{country}"

# Function to scrape water route descriptions
def scrape_ocean_route(source_port, source_country, dest_port, dest_country):
    dest_slug = slugify_port(dest_port, dest_country)
    source_slug = slugify_port(source_port, source_country)
    url = f"http://ports.com/sea-route/{source_slug}/{dest_slug}/"
    print(f"Constructed URL: {url}")
    
    water_routes = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_selector("#text-route", timeout=10000)
            elements = page.query_selector_all("p.text-route.water-route")
            for el in elements:
                a_el = el.query_selector("a")
                if a_el:
                    text = a_el.inner_text().strip()
                    if text:
                        water_routes.append(text)
            browser.close()
    except Exception as e:
        print(f"Scraping error for {url}: {e}")
    return water_routes

# Load ocean segment data
ocean_segments = [
    {"Segment_From": "Port of Shanghai, China", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Singapore, Singapore", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Ambarlı, Turkey", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Houston, USA", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Boston, USA", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Hamburg, Germany", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Mundra, India", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Santos, Brazil", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Osaka, Japan", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Busan, South Korea", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Busan, South Korea", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Jawaharlal Nehru Port, India", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Chennai, India", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Cork, Ireland", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Barcelona, Spain", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Genoa, Italy", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Genoa, Italy", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Nice, France", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of London, UK", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Toronto, Canada", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Gdańsk, Poland", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Tunis, Tunisia", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Santos, Brazil", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port Botany, Sydney", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Port of Casablanca, Morocco", "Segment_To": "Port of Hamburg, Germany"}
]

# Create a DataFrame to store the results
results = []

# Scrape water route for each ocean segment
for segment in ocean_segments:
    source_port, source_country = segment['Segment_From'].rsplit(", ", 1)
    dest_port, dest_country = segment['Segment_To'].rsplit(", ", 1)
    water_routes = scrape_ocean_route(source_port, source_country, dest_port, dest_country)
    results.append({
        "Segment_From": segment['Segment_From'],
        "Segment_To": segment['Segment_To'],
        "Water Route Description": "; ".join(water_routes) if water_routes else "No route found"
    })

# Convert results to DataFrame and save as CSV
results_df = pd.DataFrame(results)
results_df.to_csv("ocean_routes_with_descriptions.csv", index=False)
print("CSV file 'ocean_routes_with_descriptions.csv' created.")
