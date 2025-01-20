import requests
from googletrans import Translator
from countryinfo import CountryInfo
from newspaper import Article
from geopy.geocoders import Nominatim, GoogleV3
import country_converter as coco

# Replace with your own API key and CX
API_KEY = "AIzaSyBhgM9ucPG5vSqo7eqSE6MXp0GmTLPs-MQ"  # Replace with your API key
CX = "9725ead1807594275"

news_api = "07b3587b547b47339f94c4a0890b6363"

def get_country_from_city(city_name):
    """
    Get the country name from a city name using GoogleV3 and country_converter.
    :param city_name: Name of the city.
    :return: Country name if found, else None.
    """
    geolocator = GoogleV3(api_key="AIzaSyDxz5uhfKwQBAAyeafBw8-aZdyGvxd-Mxk")
    try:
        location = geolocator.geocode(city_name)
        if location and location.address:
            # Extract the country name using geopy
            address_components = location.raw.get("address_components", [])
            for component in address_components:
                if "country" in component.get("types", []):
                    print(f"{city_name}, {component.get('long_name')}")
                    return component.get("long_name")

            # As a fallback, convert city name to country using coco
            return coco.convert(names=city_name, to="name_short")
    except Exception as e:
        print(f"Error retrieving country for city '{city_name}': {e}")
    return None

def get_translated_queries(location_list):
    """
    Get translated 'local news {country}' queries along with country and language codes.
    :param location_list: List of city or country names.
    :return: Dictionary with location name as key and a dictionary of translated query, country code, and language code as value.
    """
    translator = Translator()
    translated_queries = {}

    for location in location_list:
        try:
            # Identify country if location is a city
            country = get_country_from_city(location) or location

            # Get the primary language and country code
            country_info = CountryInfo(country).info()
            languages = country_info.get("languages", ["en"])
            target_language = languages[0]  # Use the first language, fallback to English if unavailable
            country_code = country_info.get("ISO", {}).get("alpha2", "US")  # Fallback to "US" if no country code

            # Translate 'local news {country}' into the primary language
            query = f"News {location} {country}"
            translated_query = translator.translate(query, dest=target_language).text

            # Store the result in the dictionary
            translated_queries[location] = {
                "query": translated_query,
                "country_code": country_code,
                "language_code": target_language
            }
        except Exception as e:
            print(f"Error for {location}: {e}")
            translated_queries[location] = {
                "query": f"News {location} {country}",
                "country_code": "US",  # Fallback to "US"
                "language_code": "en"  # Fallback to English
            }

    return translated_queries

def get_news_sources_with_google_api(location_name, query, country_code, language_code):
    """
    Fetch local news sources using Google Custom Search API with filters.
    :param location_name: Name of the location (city or country).
    :param query: Search query.
    :param country_code: Country code for geolocation.
    :param language_code: Language code for the search.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
        "num": 8,
        "tbm": "nws",
        "hl": language_code,
        "gl": country_code,
        "cr": f"country{country_code}",
        "lr": f"lang_{language_code}",
        "excludeTerms": "embassy organization IMF WHO UNESCO consulate org gov"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract title and link from the search results
        news_sources = []
        if "items" in data:
            for item in data["items"]:
                title = item.get("title")
                link = item.get("link")
                news_sources.append((title, link))

        return news_sources
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {location_name}: {e}")
        return []

# Example usage
location_list = ["Guadalajara", "Köln", "Rabat", "Tunis", "Orléans", "Roma"]
queries_in_local_language = get_translated_queries(location_list)

for location, data in queries_in_local_language.items():
    query = data["query"]
    country_code = data["country_code"]
    language_code = data["language_code"]

    sources = get_news_sources_with_google_api(location, query, country_code, language_code)
    if sources:
        print(f"Filtered news sources for {location} , {query} , {country_code} , {language_code}:")
        for name, link in sources:
            print(f"- {link}")
    else:
        print(f"No local news sources found for {location}.")
    print()

