"""import requests
from googletrans import Translator
from countryinfo import CountryInfo

# Replace with your own API key and CX
API_KEY = "AIzaSyDxz5uhfKwQBAAyeafBw8-aZdyGvxd-Mxk"  # Replace with your API key
CX = "3705271f6f1fe4196"

def get_translated_queries(country_list):
    
    #Get translated 'News {country}' queries for a list of countries.
    #:param country_list: List of country names.
    #:return: Dictionary mapping countries to their translated queries.
    
    translator = Translator()
    translated_queries = {}

    for country in country_list:
        try:
            # Get the primary language of the country
            languages = CountryInfo(country).info().get("languages", ["en"])
            target_language = languages[0]  # Use the first language, fallback to English if unavailable

            # Translate 'News {country}' into the primary language
            query = f"News {country}"
            translated_queries[country] = translator.translate(query, dest=target_language).text
        except Exception as e:
            print(f"Error for {country}: {e}")
            translated_queries[country] = f"News {country}"  # Fallback to English query

    return translated_queries

# Example usage
country_list = ["Mexico", "Germany", "Morocco", "Tunisia", "France", "Italy"]
queries_in_local_language = get_translated_queries(country_list)
print(queries_in_local_language) 


def get_translated_query(country_name, target_language):
    base_query = f"local news websites {country_name}"  # Base query in English
    try:
        # Translate the query into the target language
        translated_query = translator.translate(base_query, dest=target_language).text
        return translated_query
    except Exception as e:
        print(f"Error translating query for {country_name}: {e}")
        return base_query  # Fallback to the English query
    

def get_news_sources_with_google_api(country_name, query):
    url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,  # Use the local language query
        "num": 10  # Maximum results per page (up to 10)
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Extract title and link from the search results
        news_sources = []
        if "items" in data:
            for item in data["items"]:
                title = item.get("title")
                link = item.get("link")
                if title and link:
                    news_sources.append((title, link))
        
        return news_sources
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {country_name}: {e}")
        return []

# Loop through the dictionary and fetch results for each country
for country, query in queries_in_local_language.items():
    sources = get_news_sources_with_google_api(country, query)
    if sources:
        print(f"News sources for {country}:")
        for name, link in sources:
            print(f"- {name}: {link}")
    else:
        print(f"No news sources found for {country}.")
    print()"""


import requests
from googletrans import Translator
from countryinfo import CountryInfo

# Replace with your own API key and CX
API_KEY = "AIzaSyBhgM9ucPG5vSqo7eqSE6MXp0GmTLPs-MQ"  # Replace with your API key
CX = "9725ead1807594275"


def get_translated_queries(country_list):
    """
    Get translated 'local news {country}' queries along with country and language codes.
    :param country_list: List of country names.
    :return: Dictionary with country name as key and a dictionary of translated query, country code, and language code as value.
    """
    translator = Translator()
    translated_queries = {}

    for country in country_list:
        try:
            # Get the primary language and country code
            country_info = CountryInfo(country).info()
            languages = country_info.get("languages", ["en"])
            target_language = languages[0]  # Use the first language, fallback to English if unavailable
            country_code = country_info.get("ISO", {}).get("alpha2", "US")  # Fallback to "US" if no country code

            # Translate 'local news {country}' into the primary language
            query = f"News {country}"
            translated_query = translator.translate(query, dest=target_language).text

            # Store the result in the dictionary
            translated_queries[country] = {
                "query": translated_query,
                "country_code": country_code,
                "language_code": target_language
            }
        except Exception as e:
            print(f"Error for {country}: {e}")
            translated_queries[country] = {
                "query": f"News {country}",
                "country_code": "US",  # Fallback to "US"
                "language_code": "en"  # Fallback to English
            }

    return translated_queries


def get_news_sources_with_google_api(country_name, query, country_code, language_code):
    """
    Fetch local news sources using Google Custom Search API with filters.
    :param country_name: Name of the country.
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
                if title and link:
                    news_sources.append((title, link))
        
        # Filter out unwanted domains
        return news_sources
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {country_name}: {e}")
        return []


# Example usage
country_list = ["Mexico", "Germany", "Morocco", "Tunisia", "Singapore", "France", "Italy"]
queries_in_local_language = get_translated_queries(country_list)

for country, data in queries_in_local_language.items():
    query = data["query"]
    country_code = data["country_code"]
    language_code = data["language_code"]
    
    sources = get_news_sources_with_google_api(country, query, country_code, language_code)
    if sources:
        print(f"Filtered news sources for {country} , {query} , {country_code} , {language_code}:")
        for name, link in sources:
            print(f"- {name}: {link}")
    else:
        print(f"No local news sources found for {country}.")
    print()


from newsplease import NewsPlease
article = NewsPlease.from_url('https://www.nytimes.com/2017/02/23/us/politics/cpac-stephen-bannon-reince-priebus.html?hp')
print(article.title)