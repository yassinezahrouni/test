import os
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Base URL of the website
main_url = "https://www.allyoucanread.com/newspapers/"
folder_path = "./NewsData/News_sources"

# Ensure the folder exists
os.makedirs(folder_path, exist_ok=True)

# Function to extract country links
def get_country_links():
    response = requests.get(main_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        country_links = []
        for link in soup.find_all("a", class_="flex bg-white border-l-8 border-red-600 rounded-sm shadow hover:shadow-md transition-shadow"):
            h3 = link.find("h3", class_="font-oswald uppercase flex-auto my-auto text-sm w-auto text-sky-900")
            if h3:
                country = h3.text.strip()
                relative_url = link["href"]
                full_url = urljoin(main_url, relative_url)
                country_links.append({"country": country, "url": full_url})
        return country_links
    else:
        print(f"Failed to fetch the main page. Status code: {response.status_code}")
        return []

# Function to extract news sources from a country page
def get_news_sources(country_url):
    response = requests.get(country_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        news_sources = []
        for link in soup.find_all("a", href=True):
            h3 = link.find("h3", class_="font-oswald text-sky-900")
            if h3:
                name = h3.text.strip()
                href = link["href"]
                news_sources.append({"name": name, "url": href})
        return news_sources
    else:
        print(f"Failed to fetch the country page: {country_url}. Status code: {response.status_code}")
        return []

# Save data to a file in JSON format
def save_to_json(data, file_name):
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    print(f"Data saved to {file_path}")

# Main logic to combine everything
def main():
    # Get all country links
    country_links = get_country_links()

    # Save country links to a JSON file
    save_to_json(country_links, "country_links.json")

    all_news_sources = {}

    # Iterate through each country link and extract news sources
    for country in country_links:
        print(f"Fetching news sources for: {country['country']} ({country['url']})")
        news_sources = get_news_sources(country["url"])
        all_news_sources[country["country"]] = news_sources

    # Save news sources to a JSON file
    save_to_json(all_news_sources, "news_sources.json")

if __name__ == "__main__":
    main()
