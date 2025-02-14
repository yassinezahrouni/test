import requests
import csv
import re
from bs4 import BeautifulSoup

# Google Maps Directions API key
API_KEY = "AIzaSyDxz5uhfKwQBAAyeafBw8-aZdyGvxd-Mxk"  # Replace with your actual API key

# Ground segment data
ground_segments = [
    {"Segment_From": "China, Shang Hai Shi, Pu Dong Xin Qu, Lujiazui, Dongfang Rd, 8号, Liangfeng Mansion, 19G 邮政编码: 200082", "Segment_To": "Port of Shanghai, China"},
    {"Segment_From": "121 Woodlands Ave 5, Singapore", "Segment_To": "Port of Singapore"},
    {"Segment_From": "Adnan Kahveci, Alemdağ Cd. No:3, 34520 Beylikdüzü/İstanbul, Türkiye", "Segment_To": "Port of Ambarlı, Turkey"},
    {"Segment_From": "12357 Riata Trace Pkwy, Suite A-130, Austin, TX 78727, USA", "Segment_To": "Port of Houston, USA"},
    {"Segment_From": "One Analog Way, Wilmington, MA 01887, USA", "Segment_To": "Port of Boston, USA"},
    {"Segment_From": "Rohrdamm 85, 13629 Berlin, Germany", "Segment_To": "Port of Hamburg, Germany"},
    {"Segment_From": "Sanand-Viramgam Highway village Iyava, Tal, Sanand, Gujarat 382170, India", "Segment_To": "Port of Mundra, India"},
    {"Segment_From": "R. Adelino Cardana, 293 - Centro, Barueri - SP, 06401-147, Brazil", "Segment_To": "Port of Santos, Brazil"},
    {"Segment_From": "25 Nishinaka, Kowata, Uji-shi, Kyoto 611-8585, JAPAN", "Segment_To": "Port of Osaka, Japan"},
    {"Segment_From": "333, Noksansaneopjung-ro, Gangseo-gu, Busan, Republic of Korea", "Segment_To": "Port of Busan, South Korea"},
    {"Segment_From": "174, Okgye2gongdan-ro (Gupo-dong), Gumi-si, Gyeongsangbuk-do, Republic of Korea", "Segment_To": "Port of Busan, South Korea"},
    {"Segment_From": "Telco Road, Pimpri, Near KSB Chowk, Pimpri Chinchwad, Maharashtra, 411018, India", "Segment_To": "Jawaharlal Nehru Port, India"},
    {"Segment_From": "Post box No.981, Nandambakkam, Chennai, India", "Segment_To": "Port of Chennai, India"},
    {"Segment_From": "Block K, Unit 3, Monavalley Business Park, Monavalley, Ireland", "Segment_To": "Port of Cork, Ireland"},
    {"Segment_From": "Carrer del Cotó, 1, 9, 08830 Sant Boi de Llobregat, Barcelona, Spain", "Segment_To": "Port of Barcelona, Spain"},
    {"Segment_From": "Via Camillo Olivetti, 2, 20864 Agrate Brianza MB, Italy", "Segment_To": "Port of Genoa, Italy"},
    {"Segment_From": "Via Rivalta, 30, 10095 Grugliasco TO, Italy", "Segment_To": "Port of Genoa, Italy"},
    {"Segment_From": "738 Av. Roumanille, 06410 Biot, France", "Segment_To": "Port of Nice, France"},
    {"Segment_From": "Sma House Home Park Industrial Estate, Kings Langley WD4 8LZ, United Kingdom", "Segment_To": "Port of London, UK"},
    {"Segment_From": "1900-5140 Yonge St, North York, ON M2N 6L7, Canada", "Segment_To": "Port of Toronto, Canada"},
    {"Segment_From": "Walentego Roździeńskiego 12, 41-303 Dąbrowa Górnicza, Poland", "Segment_To": "Port of Gdańsk, Poland"},
    {"Segment_From": "Route Jedidi Sidi Hammed, BP 80 8032, Hammamet, Tunisia", "Segment_To": "Port of Tunis, Tunisia"},
    {"Segment_From": "Rod. Armando de Sales Oliveira, km 4,7 - Distrito Industrial, Sertãozinho - SP, 14175-300, Brazil", "Segment_To": "Port of Santos, Brazil"},
    {"Segment_From": "107 Carnarvon St, Silverwater, Australia", "Segment_To": "Port Botany, Sydney"},
    {"Segment_From": "Bd des Müriers, 101 P3013, Bouskoura 20180, Morocco", "Segment_To": "Port of Casablanca, Morocco"},
    {"Segment_From": "Port of Hamburg, Germany", "Segment_To": "Krauss-Maffei-Straße 2, 80997 Munich, Germany"}
]

def get_route_description(origin, destination):
    """Fetch the route description, distance, and time using Google Maps Directions API."""
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "driving",
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            leg = data["routes"][0]["legs"][0]
            steps = [BeautifulSoup(step["html_instructions"], "html.parser").get_text() for step in leg["steps"]]
            route_description = " - ".join(steps)
            distance = leg["distance"]["text"]
            duration = leg["duration"]["text"]
            return route_description, distance, duration
    return "No route found", "N/A", "N/A"

# Collect results
results = []
route_from_hamburg = get_route_description("Port of Hamburg, Germany", "Krauss-Maffei-Straße 2, 80997 Munich, Germany")

for segment in ground_segments:
    if segment["Segment_From"] == "Port of Hamburg, Germany" and segment["Segment_To"] == "Krauss-Maffei-Straße 2, 80997 Munich, Germany":
        route_description, distance, duration = route_from_hamburg
    else:
        route_description, distance, duration = get_route_description(segment["Segment_From"], segment["Segment_To"])
    
    results.append({
        "Segment_From": segment["Segment_From"],
        "Segment_To": segment["Segment_To"],
        "Route_Description": route_description,
        "Distance": distance,
        "Duration": duration
    })

# Write to CSV
with open("ground_segments_with_details_v1.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["Segment_From", "Segment_To", "Route_Description", "Distance", "Duration"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print("CSV file 'ground_segments_with_details_v1.csv' has been created.")
