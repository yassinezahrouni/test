import csv
import json
import re
from playwright.sync_api import sync_playwright

##########################
# Part 1: Scraping Function
##########################
def slugify_port(port, country):
    """
    Converts a port name and country into a slug.
    
    - If the port starts with "port of ", remove that prefix.
    - If the port ends with " port", remove that suffix.
    - Then, replace spaces with hyphens.
    
    Additionally, for the country:
      - Map common abbreviations (e.g. "usa" -> "united-states", "uk" -> "united-kingdom").
      - Remove any digits.
      
    For example:
      "Port of Hamburg Port", "Germany"  -> "port-of-hamburg,germany"
      "Shanghai Port", "China"            -> "port-of-shanghai,china"
      "Singapore Port", "Singapore099253" -> "port-of-singapore,singapore"
    """
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
    # Exception for Genoa: if the slug contains "genoa-genova" or equals "genova", set to "genoa"
    elif port_slug == "genoa":
        port_slug = "genoa-genova"   
    
    # Process country: remove digits, lowercase and replace spaces with hyphens.
    country = re.sub(r'\d+', '', country).strip().lower()
    # Map common abbreviations:
    mapping = {
        "usa": "united-states",
        "us": "united-states",
        "uk": "united-kingdom"
    }
    if country in mapping:
        country = mapping[country]
    else:
        country = country.replace(" ", "-")
    
    return f"port-of-{port_slug},{country}"

def scrape_ocean_route(source_port, source_country, dest_port, dest_country):
    """
    Uses Playwright to scrape the water-route elements from ports.com.
    The URL is built using the slugified port names.
    
    For example, for a journey from "Shanghai Port", "China" to "Hamburg Port", "Germany",
    the URL becomes:
      http://ports.com/sea-route/port-of-hamburg,germany/port-of-shanghai,china/
      
    It extracts and returns a list of water-route names from <p> elements with the 
    class "text-route water-route".
    """
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

##########################
# Part 2: Data Generation
##########################

# CSV header (we now use a single "segment_via" column instead of segment_via1..6)
header = [
    "Itinerary_ID", "Sequence_Number", "Route_Code",
    "segment_FromLocation", "segment_FromAddress",
    "segment_ToLocation", "segment_ToAddress",
    "segment_via",
    "Shipping_Method", "Scheduled_Start_Time", "Scheduled_End_Time",
    "Part_Name", "Quantity", "Unit_Price", "Line_Total",
    "GoogleRouteDescription", "GoogleRouteMainWays"
]

# Define supplier data for 5 regions with real-sounding details.
supplier_data = {
    "China": {
        "supplier": "Foxconn Shanghai Plant",
        "plant_address": "No. 200 Xiuyan Rd, Pudong, Shanghai, China",
        "local_port": "Shanghai Port",
        "port_address": "Port Rd, Shanghai, China",
        "ocean_via": ["South China Sea", "Indian Ocean", "Suez Canal"]
    },
    "Singapore": {
        "supplier": "Seagate Singapore HQ",
        "plant_address": "10 Fusion Drive, Singapore 138577",
        "local_port": "Singapore Port",
        "port_address": "80 Maritime Sq, Singapore 099253",
        "ocean_via": ["Strait of Malacca", "Indian Ocean", "Suez Canal"]
    },
    "Turkey": {
        "supplier": "Arçelik Istanbul Plant",
        "plant_address": "No. 25 Industrial Zone, Istanbul, Turkey",
        "local_port": "Istanbul Port",
        "port_address": "Haydarpaşa, Istanbul, Turkey",
        "ocean_via": ["Aegean Sea", "Mediterranean Sea", "Suez Canal"]
    },
    "Australia": {
        "supplier": "RØDE Microphones HQ",
        "plant_address": "200 Industrial Ave, Sydney, NSW, Australia",
        "local_port": "Sydney Port",
        "port_address": "Sydney Harbour, Sydney, NSW, Australia",
        "ocean_via": ["Tasman Sea", "Indian Ocean", "Suez Canal"]
    },
    "Morocco": {
        "supplier": "STMicroelectronics Bouskoura",
        "plant_address": "50 Factory Rd, Casablanca, Morocco",
        "local_port": "Casablanca Port",
        "port_address": "Casablanca Port, Casablanca, Morocco",
        "ocean_via": ["Atlantic Ocean", "English Channel", "North Sea"]
    }
}

# Additional suppliers (ensuring diversity; each supplier appears at most twice)
additional_suppliers = [
    {"origin": "USA", "supplier": "Texas Instruments USA", "plant_address": "12500 TI Blvd, Dallas, TX, USA",
     "local_port": "Port of Houston", "port_address": "100 Main St, Houston, TX, USA", "ocean_via": ["Gulf of Mexico", "Atlantic Ocean", "English Channel"]},
    {"origin": "USA", "supplier": "Analog Devices USA", "plant_address": "1 Analog Way, Norwood, MA, USA",
     "local_port": "Port of Boston", "port_address": "50 Seaport Blvd, Boston, MA, USA", "ocean_via": ["Atlantic Ocean", "English Channel", "North Sea"]},
    {"origin": "Germany", "supplier": "Siemens AG", "plant_address": "Werner-von-Siemens-Strasse 1, Munich, Germany",
     "local_port": "Port of Hamburg", "port_address": "Hamburg Port, Hamburg, Germany", "ocean_via": ["North Sea", "Atlantic Ocean", "North Sea"]},
    {"origin": "Germany", "supplier": "Bosch Rexroth", "plant_address": "Rexrothallee 1, Lohr am Main, Germany",
     "local_port": "Port of Bremen", "port_address": "Bremen Harbor, Bremen, Germany", "ocean_via": ["North Sea", "Atlantic Ocean", "North Sea"]},
    {"origin": "Japan", "supplier": "Mitsubishi Electric", "plant_address": "3-3, Marunouchi 2-chome, Tokyo, Japan",
     "local_port": "Tokyo Port", "port_address": "Tokyo Bay, Tokyo, Japan", "ocean_via": ["South China Sea", "Indian Ocean", "Suez Canal"]},
    {"origin": "Japan", "supplier": "Panasonic Corporation", "plant_address": "1006 Oaza Kadoma, Kadoma, Osaka, Japan",
     "local_port": "Osaka Port", "port_address": "Osaka Harbor, Osaka, Japan", "ocean_via": ["South China Sea", "Indian Ocean", "Suez Canal"]},
    {"origin": "South Korea", "supplier": "Samsung Electro-Mechanics", "plant_address": "129 Samsung-ro, Suwon, Gyeonggi-do, South Korea",
     "local_port": "Busan Port", "port_address": "Busan Harbor, Busan, South Korea", "ocean_via": ["Korea Strait", "Indian Ocean", "Suez Canal"]},
    {"origin": "South Korea", "supplier": "LG Innotek", "plant_address": "LG Twin Towers, Yeouido-dong, Seoul, South Korea",
     "local_port": "Incheon Port", "port_address": "Incheon Harbor, Incheon, South Korea", "ocean_via": ["Yellow Sea", "Indian Ocean", "Suez Canal"]},
    {"origin": "India", "supplier": "Tata Motors Components", "plant_address": "44 Ganesh Shankar Vidyarthi Marg, Mumbai, India",
     "local_port": "Mumbai Port", "port_address": "Mumbai Port, Mumbai, India", "ocean_via": ["Arabian Sea", "Suez Canal", "Mediterranean Sea"]},
    {"origin": "India", "supplier": "Bharat Electronics Ltd.", "plant_address": "Dholera SEZ, Gujarat, India",
     "local_port": "Kandla Port", "port_address": "Kandla Port, Kutch, India", "ocean_via": ["Arabian Sea", "Suez Canal", "Mediterranean Sea"]},
    {"origin": "France", "supplier": "Thales Group", "plant_address": "Tour Carpe Diem, 31 Place des Corolles, La Défense, France",
     "local_port": "Le Havre Port", "port_address": "Le Havre Port, Le Havre, France", "ocean_via": ["English Channel", "North Sea", ""]},
    {"origin": "France", "supplier": "Schneider Electric France", "plant_address": "35 Rue Joseph Monier, Rueil-Malmaison, France",
     "local_port": "Marseille Port", "port_address": "Port of Marseille, Marseille, France", "ocean_via": ["Mediterranean Sea", "Atlantic Ocean", "North Sea"]},
    {"origin": "Italy", "supplier": "STMicroelectronics Italy", "plant_address": "Via Bassi, 10, Milan, Italy",
     "local_port": "Genoa Port", "port_address": "Genoa Port, Genoa, Italy", "ocean_via": ["Mediterranean Sea", "Atlantic Ocean", "North Sea"]},
    {"origin": "Italy", "supplier": "Comau S.p.A.", "plant_address": "Via Ferraris, 13, Turin, Italy",
     "local_port": "Trieste Port", "port_address": "Trieste Port, Trieste, Italy", "ocean_via": ["Adriatic Sea", "Atlantic Ocean", "North Sea"]},
    {"origin": "UK", "supplier": "ARM Holdings", "plant_address": "70 Cambridge Science Park, Milton, UK",
     "local_port": "Port of Felixstowe", "port_address": "Felixstowe Docks, Felixstowe, UK", "ocean_via": ["North Sea", "English Channel", "North Sea"]},
    {"origin": "UK", "supplier": "Imagination Technologies", "plant_address": "Rothamsted House, Harpenden, UK",
     "local_port": "Port of London", "port_address": "London Docks, London, UK", "ocean_via": ["North Sea", "English Channel", "North Sea"]},
    {"origin": "Canada", "supplier": "Celestica Inc.", "plant_address": "1000 Dalhousie St, Toronto, ON, Canada",
     "local_port": "Port of Vancouver", "port_address": "Vancouver Docks, Vancouver, BC, Canada", "ocean_via": ["Pacific Ocean", "Panama Canal", "Atlantic Ocean"]},
    {"origin": "Canada", "supplier": "Magna International", "plant_address": "7770 Yonge St, Aurora, ON, Canada",
     "local_port": "Port of Montreal", "port_address": "Montreal Harbor, Montreal, QC, Canada", "ocean_via": ["Atlantic Ocean", "English Channel", "North Sea"]},
    {"origin": "Brazil", "supplier": "Embraer Components", "plant_address": "Av. Brigadeiro Faria Lima, São Paulo, Brazil",
     "local_port": "Port of Santos", "port_address": "Santos Port, Santos, Brazil", "ocean_via": ["Atlantic Ocean", "English Channel", "North Sea"]},
    {"origin": "Brazil", "supplier": "WEG Brasil", "plant_address": "Rua dos Timbiras, Belo Horizonte, Brazil",
     "local_port": "Port of Rio de Janeiro", "port_address": "Rio de Janeiro Docks, Rio de Janeiro, Brazil", "ocean_via": ["Atlantic Ocean", "English Channel", "North Sea"]}
]

# Combine original 5 and additional suppliers
all_suppliers = []
for key in ["China", "Singapore", "Turkey", "Australia", "Morocco"]:
    s = supplier_data[key].copy()
    s["origin"] = key
    all_suppliers.append(s)
all_suppliers.extend(additional_suppliers)

# Define 55 unique part names (completely different parts)
part_names = [
    "High-Precision Resistor", "Ultra-Low Power Microcontroller", "Advanced Capacitor Array", "Custom PCB Assembly", "Precision Servo Motor",
    "Robust Hydraulic Pump", "Eco-Friendly LED Module", "Smart Sensor Module", "Industrial Ethernet Switch", "Modular Power Supply Unit",
    "High-Speed Motor Controller", "Wireless Transceiver", "Digital Signal Processor Board", "Automated Conveyor Motor", "Thermal Imaging Sensor",
    "RFID Tracking Module", "Ultra-Durable Cable Assembly", "Optical Fiber Connector", "Heavy-Duty Pneumatic Cylinder", "Miniaturized GPS Module",
    "High-Efficiency Solar Panel Array", "Next-Gen Battery Pack", "Robust Industrial Valve", "Smart HVAC Controller", "Precision Robotic Actuator",
    "Multifunctional PLC Unit", "3D-Printed Gear Assembly", "High-Frequency Oscillator", "Ultra-Sonic Sensor Array", "Automotive ECU Module",
    "Advanced Brake Control System", "Dynamic Load Cell Sensor", "Multi-Port USB Hub", "Digital Temperature Controller", "Robust Industrial Relay",
    "Wireless Charging Pad", "High-Resolution Touchscreen Panel", "Intelligent Energy Meter", "Precision CNC Controller", "Smart Lighting Controller",
    "High-Power LED Driver", "Modular Data Acquisition System", "Industrial Pressure Sensor", "Dynamic Vibration Analyzer", "Robotic Gripper Assembly",
    "Smart Motor Driver", "Advanced Frequency Converter", "Multi-Axis Servo Drive", "Digital Signal Interface Board", "Compact Thermal Printer",
    "High-Speed Data Router", "Next-Generation IoT Gateway", "Industrial Safety Sensor", "Precision Optical Encoder", "Robust Wireless Router"
]

# Final common ground segment: Hamburg Port -> Allach Warehouse
final_ground = {
    "segment_FromLocation": "Hamburg Port",
    "segment_FromAddress": "Hamburg Port, Hamburg, Germany",
    "segment_ToLocation": "Allach Warehouse",
    "segment_ToAddress": "Krauss-Maffei-Straße 2, 80997 Munich, Germany",
    "Shipping_Method": "Ground",
    "Scheduled_Start_Time": "2024-10-07T07:00:00Z",
    "Scheduled_End_Time": "2024-10-07T11:00:00Z",
    "GoogleRouteDescription": json.dumps({
        "steps": [
            {"instruction": "Merge onto A1 toward Bremen/Hannover", "distance": "11.2 km", "duration": "7 mins"},
            {"instruction": "Continue onto A7", "distance": "123 km", "duration": "1 hr 16 mins"},
            {"instruction": "At interchange 68-Kreuz Magdeburg, follow A14 toward Leipzig/Dresden", "distance": "107 km", "duration": "1 hr 3 mins"},
            {"instruction": "Take A9 toward München/Erfurt", "distance": "256 km", "duration": "2 hr 32 mins"},
            {"instruction": "Merge onto A92 toward Deggendorf/Eching-Ost", "distance": "12.7 km", "duration": "8 mins"},
            {"instruction": "Take A99, then exit onto Dachauer Str.", "distance": "4.9 km", "duration": "6 mins"}
        ]
    }),
    "GoogleRouteMainWays": json.dumps(["A1", "A7", "A14", "A9", "A92", "A99"])
}

# Functions to generate segments
def get_ground_segment_supplier(supplier):
    return {
        "segment_FromLocation": supplier["supplier"],
        "segment_FromAddress": supplier["plant_address"],
        "segment_ToLocation": supplier["local_port"],
        "segment_ToAddress": supplier["port_address"],
        "segment_via": "",  # For ground segments, leave blank.
        "Shipping_Method": "Ground",
        "Scheduled_Start_Time": "2024-10-01T05:00:00Z",
        "Scheduled_End_Time": "2024-10-01T09:00:00Z",
        "GoogleRouteDescription": json.dumps({
            "steps": [
                {"instruction": "Depart from plant via main industrial road", "distance": "1.5 km", "duration": "4 mins"},
                {"instruction": "Turn onto local highway", "distance": "2.0 km", "duration": "5 mins"},
                {"instruction": "Arrive at local port", "distance": "1.0 km", "duration": "3 mins"}
            ]
        }),
        "GoogleRouteMainWays": json.dumps(["Local Highway"])
    }

def get_ocean_segment(supplier):
    # First, try to scrape the ocean route from the website.
    # Use supplier's local port as source, destination is Hamburg Port.
    # We'll assume the country for Hamburg is "Germany" and for the supplier's port we extract from port_address.
    # For simplicity, assume the country is the last word in port_address after a comma.
    src_country = supplier["port_address"].split(",")[-1].strip()
    dest_country = "Germany"
    scraped = scrape_ocean_route(supplier["local_port"], src_country, "Hamburg Port", dest_country)
    if scraped and len(scraped) > 0:
        segment_via = " - ".join(scraped)
    else:
        # If scraping fails, fall back to original fixed values.
        fallback = supplier["ocean_via"] + ["Mediterranean Sea", "English Channel", "North Sea"]
        segment_via = "-".join(fallback)
    return {
        "segment_FromLocation": supplier["local_port"],
        "segment_FromAddress": supplier["port_address"],
        "segment_ToLocation": "Hamburg Port",
        "segment_ToAddress": "Hamburg Port, Hamburg, Germany",
        "segment_via": segment_via,
        "Shipping_Method": "Ocean",
        "Scheduled_Start_Time": "2024-10-01T09:30:00Z",
        "Scheduled_End_Time": "2024-10-07T06:00:00Z",
        "GoogleRouteDescription": "N/A",
        "GoogleRouteMainWays": "N/A"
    }


# Build complete supplier list
all_suppliers = []
for key in ["China", "Singapore", "Turkey", "Australia", "Morocco"]:
    s = supplier_data[key].copy()
    s["origin"] = key
    all_suppliers.append(s)
all_suppliers.extend(additional_suppliers)

rows = []
num_parts = 55
num_suppliers = len(all_suppliers)

for i in range(1, num_parts + 1):
    supplier = all_suppliers[(i - 1) % num_suppliers]
    part_name = part_names[i - 1]
    if supplier["origin"] in ["China", "Turkey", "Australia", "Morocco", "USA", "Japan", "India", "Brazil"]:
        quantity = 200
        unit_price = 2.50
        line_total = 500.00
    else:
        quantity = 50
        unit_price = 12.00
        line_total = 600.00

    base_id = 6000 + ((i - 1) * 3) + 1

    # Segment 1: Ground from supplier plant to local port
    seg1_data = get_ground_segment_supplier(supplier)
    seg1 = {
        "Itinerary_ID": base_id,
        "Sequence_Number": 1,
        "Route_Code": f"RT-{supplier['origin'][:2].upper()}-GND",
        "segment_FromLocation": seg1_data["segment_FromLocation"],
        "segment_FromAddress": seg1_data["segment_FromAddress"],
        "segment_ToLocation": seg1_data["segment_ToLocation"],
        "segment_ToAddress": seg1_data["segment_ToAddress"],
        "segment_via": seg1_data["segment_via"],
        "Shipping_Method": seg1_data["Shipping_Method"],
        "Scheduled_Start_Time": seg1_data["Scheduled_Start_Time"],
        "Scheduled_End_Time": seg1_data["Scheduled_End_Time"],
        "Part_Name": part_name,
        "Quantity": quantity,
        "Unit_Price": unit_price,
        "Line_Total": line_total,
        "GoogleRouteDescription": seg1_data["GoogleRouteDescription"],
        "GoogleRouteMainWays": seg1_data["GoogleRouteMainWays"]
    }
    
    # Segment 2: Ocean from local port to Hamburg Port
    seg2_data = get_ocean_segment(supplier)
    seg2 = {
        "Itinerary_ID": base_id + 1,
        "Sequence_Number": 2,
        "Route_Code": "RT-OCEAN",
        "segment_FromLocation": seg2_data["segment_FromLocation"],
        "segment_FromAddress": seg2_data["segment_FromAddress"],
        "segment_ToLocation": seg2_data["segment_ToLocation"],
        "segment_ToAddress": seg2_data["segment_ToAddress"],
        "segment_via": seg2_data["segment_via"],
        "Shipping_Method": seg2_data["Shipping_Method"],
        "Scheduled_Start_Time": seg2_data["Scheduled_Start_Time"],
        "Scheduled_End_Time": seg2_data["Scheduled_End_Time"],
        "Part_Name": part_name,
        "Quantity": quantity,
        "Unit_Price": unit_price,
        "Line_Total": line_total,
        "GoogleRouteDescription": seg2_data["GoogleRouteDescription"],
        "GoogleRouteMainWays": seg2_data["GoogleRouteMainWays"]
    }
    
    # Segment 3: Ground from Hamburg Port to Allach Warehouse (common for all parts)
    seg3 = {
        "Itinerary_ID": base_id + 2,
        "Sequence_Number": 3,
        "Route_Code": "RT-GND",
        "segment_FromLocation": final_ground["segment_FromLocation"],
        "segment_FromAddress": final_ground["segment_FromAddress"],
        "segment_ToLocation": final_ground["segment_ToLocation"],
        "segment_ToAddress": final_ground["segment_ToAddress"],
        "segment_via": "",  # For common ground segment, leave blank.
        "Shipping_Method": final_ground["Shipping_Method"],
        "Scheduled_Start_Time": final_ground["Scheduled_Start_Time"],
        "Scheduled_End_Time": final_ground["Scheduled_End_Time"],
        "Part_Name": part_name,
        "Quantity": quantity,
        "Unit_Price": unit_price,
        "Line_Total": line_total,
        "GoogleRouteDescription": final_ground["GoogleRouteDescription"],
        "GoogleRouteMainWays": final_ground["GoogleRouteMainWays"]
    }
    
    rows.extend([seg1, seg2, seg3])

# Write all rows to CSV
csv_filename = "expanded_shipment_overview.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=header)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

print(f"CSV file '{csv_filename}' has been created with {len(rows)} rows (55 parts, 165 segments).")
