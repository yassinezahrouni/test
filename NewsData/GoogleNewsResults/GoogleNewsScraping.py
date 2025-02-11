import os
import json
import datetime
import requests
from newspaper import Article
from geopy.geocoders import GoogleV3
import country_converter as coco

# ---------------------------
# Geocoder Code (Geocoder/geocoder_test.py)
# ---------------------------
API_KEY_GEOCODER = "AIzaSyDxz5uhfKwQBAAyeafBw8-aZdyGvxd-Mxk"  # Your Google Geocoding API key

def get_location_hierarchy(address):
    """
    Get the location hierarchy from an address using Google Geocoding API.
    Returns a dictionary containing various address components.
    """
    geolocator = GoogleV3(api_key=API_KEY_GEOCODER)
    try:
        location = geolocator.geocode(address)
        if location:
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
            # Determine continent and region (though we will ignore region later)
            country_name = hierarchy["country"]
            hierarchy["continent"] = coco.convert(names=country_name, to='continent')
            hierarchy["continent_region"] = coco.convert(names=country_name, to="UNregion")
            hierarchy["world_region"] = None  # Ignored in this integration
            return hierarchy
    except Exception as e:
        print(f"Error retrieving location hierarchy for address '{address}': {e}")
    return None

# ---------------------------
# Google News Scraper Code
# ---------------------------
# Replace with your own API key and Custom Search Engine ID (CX) for news searches
API_KEY_NEWS = "AIzaSyBhgM9ucPG5vSqo7eqSE6MXp0GmTLPs-MQ"  # Your API key
CX = "9725ead1807594275"  # Your Custom Search Engine ID

def get_news_articles(query, country_code, language_code, max_results=100):
    """
    Fetches news articles from Google Custom Search API (Google News) for a given query,
    restricted to the last 30 days.
    Returns a list of dictionaries, each containing:
      - headline
      - article_text
      - link
      - published_date (if available)
    """
    all_articles = []
    start = 1

    while start < max_results:
        params = {
            "key": API_KEY_NEWS,
            "cx": CX,
            "q": query,
            "num": 10,             # Maximum results per request is 10.
            "start": start,
            "tbm": "nws",          # Restrict search to Google News.
            "hl": language_code,
            "gl": country_code,
            "cr": f"country{country_code}",
            "lr": f"lang_{language_code}",
            "dateRestrict": "d30", # Limit results to the last 30 days.
            "sort": "date"         # Sort by date (latest first).
        }
        
        url = "https://www.googleapis.com/customsearch/v1"
        response = requests.get(url, params=params)
        try:
            response.raise_for_status()
        except Exception as e:
            print(f"Error fetching results: {e}")
            break
        
        data = response.json()
        items = data.get("items", [])
        if not items:
            break
        
        for item in items:
            headline = item.get("title", "").strip()
            link = item.get("link", "").strip()

            original_article_text = ""
            published_date = ""

            try:
                article = Article(link)
                article.download()
                article.parse()
                original_article_text = article.text or ""
                if article.publish_date:
                    published_date = article.publish_date.strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(f"Error extracting article text from {link}: {e}")
            
            article_info = {
                "headline": headline,
                "article_text": original_article_text,
                "link": link,
                "published_date": published_date
            }
            all_articles.append(article_info)
        
        start += 10

    return all_articles

def save_to_json(data, output_file):
    """
    Saves the provided data to a JSON file.
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {output_file}")

def scrape_news_for_levels(address, language_code="de"):
    """
    Uses the geocoder to get the location hierarchy for the given address and then,
    for each level among 'part_of_city', 'city', 'part_of_state', 'state', and 'country'
    (if not None), fetches news articles from Google News.
    The results for each level are saved in separate JSON files under NewsData/GoogleNewsResults.
    """
    hierarchy = get_location_hierarchy(address)
    if not hierarchy:
        print("Could not retrieve location hierarchy.")
        return
    
    # Define the levels we care about.
    levels_to_query = ['part_of_city', 'city', 'part_of_state', 'state', 'country']
    
    # Convert the full country name to an ISO2 country code.
    country_name = hierarchy.get("country")
    country_code = coco.convert(names=country_name, to="ISO2")
    if not country_code:
        country_code = "US"  # Fallback if conversion fails

    results = {}
    # For each level, if the value is not None, run a news search.
    for level in levels_to_query:
        value = hierarchy.get(level)
        if value:
            query = f"News {value}"
            print(f"Fetching news for {level}: {value} with query '{query}'")
            articles = get_news_articles(query, country_code, language_code, max_results=50)
            results[level] = articles
        else:
            results[level] = []
    
    # Save each level's results into a separate JSON file.
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    base_path = os.path.join("NewsData", "GoogleNewsResults")
    os.makedirs(base_path, exist_ok=True)
    for level, articles in results.items():
        output_file = os.path.join(base_path, f"news_{level}_{today_date}.json")
        save_to_json(articles, output_file)
    
    return results

# ---------------------------
# Example Usage
# ---------------------------
if __name__ == "__main__":
    # Example address (from your provided example, note that here we use a German address)
    address = "Grasmeierstr. 25, 80805 München"
    scrape_news_for_levels(address, language_code="de")
