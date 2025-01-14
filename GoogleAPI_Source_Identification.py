import requests
from googletrans import Translator
from countryinfo import CountryInfo
from newspaper import Article
from geopy.geocoders import Nominatim

# Replace with your own API key and CX
API_KEY = "AIzaSyBhgM9ucPG5vSqo7eqSE6MXp0GmTLPs-MQ"  # Replace with your API key
CX = "9725ead1807594275"

# Define a set of keywords that indicate reliable news sources
NEWS_KEYWORDS = ["news", "noticias", "nouvelles", "nachrichten", "actualites", "journal", "gazette", "radio", "media"]

def get_country_from_city(city_name):
    """
    Get the country name from a city name using geopy.
    :param city_name: Name of the city.
    :return: Country name if found, else None.
    """
    geolocator = Nominatim(user_agent="geoapi")
    try:
        location = geolocator.geocode(city_name)
        if location and location.raw.get("address"):
            return location.raw["address"].get("country")
    except Exception as e:
        print(f"Error finding country for city {city_name}: {e}")
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
                "query": f"News {location}",
                "country_code": "US",  # Fallback to "US"
                "language_code": "en"  # Fallback to English
            }

    return translated_queries

def is_reliable_news_source(title, link):
    """
    Check if a given link leads to a reliable news source by fetching and analyzing the website content.
    :param title: Title of the news source.
    :param link: URL of the news source.
    :return: True if it is a reliable news source, otherwise False.
    """
    try:
        article = Article(link)
        article.download()
        article.parse()

        # Extract metadata
        meta_description = article.meta_description or ""
        meta_keywords = article.meta_keywords or []
        meta_description_lower = meta_description.lower()

        # Check for reliability based on keywords
        if any(keyword in meta_description_lower for keyword in NEWS_KEYWORDS):
            return True
        if any(keyword in meta_keywords for keyword in NEWS_KEYWORDS):
            return True

    except Exception as e:
        print(f"Error analyzing link {link}: {e}")

    return False

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
        "num": 10,
        "hl": language_code,
        "gl": country_code,
        "cr": f"country{country_code}",
        "lr": f"lang_{language_code}",
        "excludeTerms": "embassy organization IMF WHO UNESCO consulate"
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
                if title and link and is_reliable_news_source(title, link):
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
            print(f"- {name}: {link}")
    else:
        print(f"No local news sources found for {location}.")
    print()

