import requests
from geopy.geocoders import GoogleV3
import country_converter as coco

# Replace with your Google Geocoding API key
API_KEY = "AIzaSyDxz5uhfKwQBAAyeafBw8-aZdyGvxd-Mxk"  # Replace with your API key

# Mapping of continents to regions
CONTINENT_TO_REGION_MAPPING = {
    "Europe": "EMEA",
    "Asia": "APAC",
    "North America": "NA",
    "South America": "SA",
    "Africa": "EMEA",
    "Oceania": "APAC"
}


def get_location_hierarchy(address):
    """
    Get the location hierarchy from an address using Google Geocoding API.
    :param address: Address string to geocode.
    :return: Dictionary containing the hierarchy of the location.
    """
    geolocator = GoogleV3(api_key=API_KEY)
    try:
        location = geolocator.geocode(address)
        if location:
            # Extract address components
            hierarchy = {
                "street": None,
                "house_number": None,
                "neighborhood": None,
                "part_of_city": None,
                "city": None,
                "part_of_state": None,
                "state": None,
                "country": None,
                "continent": None,
                "continent_region": None,
                "world_region": None
            }

            for component in location.raw.get("address_components", []):
                types = component.get("types", [])
                if "street_number" in types:
                    hierarchy["house_number"] = component.get("long_name")
                if "route" in types:
                    hierarchy["street"] = component.get("long_name")
                if "neighborhood" in types:
                    hierarchy["neighborhood"] = component.get("long_name")
                if "sublocality" in types or "sublocality_level_1" in types:
                    hierarchy["part_of_city"] = component.get("long_name")
                if "locality" in types:
                    hierarchy["city"] = component.get("long_name")
                if "administrative_area_level_2" in types:
                    hierarchy["part_of_state"] = component.get("long_name")
                if "administrative_area_level_1" in types:
                    hierarchy["state"] = component.get("long_name")
                if "country" in types:
                    hierarchy["country"] = component.get("long_name")

            # Determine continent and region
            country = hierarchy["country"]
            hierarchy["continent"] = coco.convert(names=country, to='continent')
            hierarchy["continent_region"] = coco.convert(names=country, to="UNregion")
            if hierarchy["continent"] in CONTINENT_TO_REGION_MAPPING:
                    hierarchy["world_region"] = CONTINENT_TO_REGION_MAPPING[hierarchy["continent"]]


            return hierarchy
    except Exception as e:
        print(f"Error retrieving location hierarchy for address '{address}': {e}")
    return None

# Example usage
addresses = ["Grasmeierstr. 25, 80805 München"]  # List of addresses to analyze
hierarchies = []  # List of location hierarchies

for address in addresses:
    hierarchy = get_location_hierarchy(address)
    hierarchies.append(hierarchy)

print(hierarchies)
