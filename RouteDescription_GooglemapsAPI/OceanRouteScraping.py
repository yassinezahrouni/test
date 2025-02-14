import re
from playwright.sync_api import sync_playwright
import csv

# List of port routes
data = [
    "Port of Shanghai, China",
    "Port of Singapore, Singapore",
    "Port of Ambarlı, Turkey",
    "Port of Houston, USA",
    "Port of Boston, USA",
    "Port of Hamburg, Germany",
    "Port of Mundra, India",
    "Port of Santos, Brazil",
    "Port of Osaka, Japan",
    "Port of Busan, South Korea",
    "Port of Busan, South Korea",
    "Jawaharlal Nehru Port, India",
    "Port of Chennai, India",
    "Port of Cork, Ireland",
    "Port of Barcelona, Spain",
    "Port of Genoa, Italy",
    "Port of Genoa, Italy",
    "Port of Nice, France",
    "Port of London, UK",
    "Port of Toronto, Canada",
    "Port of Gdańsk, Poland",
    "Port of Tunis, Tunisia",
    "Port of Santos, Brazil",
    "Port Botany, Sydney",
    "Port of Casablanca, Morocco"
]

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

# Function to scrape ocean routes from ports.com
def scrape_ocean_route(source_port, source_country, dest_port, dest_country):
    dest_slug = slugify_port(dest_port, dest_country)
    source_slug = slugify_port(source_port, source_country)
    url = f"http://ports.com/sea-route/{source_slug}/{dest_slug}/"
    water_routes = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_selector("#text-route", timeout=10000)
            elements = page.query_selector_all("p.text-route.water-route")
            for el in elements:
                text = el.text_content().strip()
                if text:
                    water_routes.append(text)
            browser.close()
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    return water_routes

# Create and write to a CSV file
with open("ocean_routes.csv", "w", newline="") as csvfile:
    fieldnames = ["Segment_From", "Segment_To", "Water Route Description"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    
    # Process each route and write to the CSV
    for nearest_port in data:
        try:
            port_name, country_name = nearest_port.rsplit(", ", 1)
            ocean_route = scrape_ocean_route(port_name, country_name, "Hamburg Port", "Germany")
            route_description = "; ".join(ocean_route) if ocean_route else "No route found"
            
            writer.writerow({
                "Segment_From": nearest_port,
                "Segment_To": "Port of Hamburg, Germany",
                "Water Route Description": route_description
            })
        except Exception as e:
            print(f"Failed to process {nearest_port}: {e}")

print("Processing completed! Results saved to ocean_routes.csv.")
