"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import json

# Base URLs and folder setup
base_url = "https://www.thepaperboy.com/"
us_states_base_url = "https://www.thepaperboy.com/united-states/newspapers/country.cfm"
folder_path = "./NewsData/News_sources"

# Ensure the folder exists
os.makedirs(folder_path, exist_ok=True)

# Function to fetch all country links from the main page
def fetch_country_links():
    response = requests.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        country_links = []
        for link in soup.find_all("a", href=True, class_="mediumlink"):  # Filter links with "mediumlink" class
            country_name = link.text.split(" (")[0].strip()  # Extract the country name
            relative_url = link["href"]
            full_url = urljoin(base_url, relative_url)  # Construct full URL
            country_links.append({"country": country_name, "url": full_url})
        return country_links
    else:
        print(f"Failed to fetch the main page. Status code: {response.status_code}")
        return []
    

fetch_country_links()


# Function to fetch the list of U.S. states
def fetch_us_states():
    response = requests.get(us_states_base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        states = []
        for link in soup.find_all("a", href=True, class_="gray"):  # State links have the "gray" class
            state_name = link.text.strip()
            relative_url = link["href"]
            state_url = urljoin(base_url, relative_url)
            states.append({"state": state_name, "state_url": state_url})
        return states
    else:
        print(f"Failed to fetch U.S. states page. Status code: {response.status_code}")
        return []

# Function to fetch the list of newspapers for a given country or state
def fetch_newspapers(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        newspapers = []
        for row in soup.find_all("tr", bgcolor="#efefef"):  # Each newspaper is in a table row with this bgcolor
            link = row.find("a", href=True)
            if link and "PaperID" in link['href']:  # Look for links with "PaperID" in href
                newspaper_name = link.text.strip()
                relative_url = link['href']
                newspaper_page_url = urljoin(base_url, relative_url)  # Construct the newspaper page URL
                newspapers.append({"name": newspaper_name, "page_url": newspaper_page_url})
        return newspapers
    else:
        print(f"Failed to fetch newspapers page: {url}. Status code: {response.status_code}")
        return []

# Function to fetch the real website link from a newspaper page
def fetch_real_website(newspaper_page_url):
    response = requests.get(newspaper_page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        external_link = soup.find("a", href=True, style=True)  # Look for external link with a style attribute
        if external_link:
            return external_link['href']
    return None

# Main function to fetch newspapers for all countries and U.S. states
def fetch_newspapers_for_all():
    all_data = {}

    # Step 1: Fetch all country links from the main page
    country_links = fetch_country_links()

    for country in country_links:
        print(f"Processing country: {country['country']}")

        if country['country'].lower() == "united states":
            # Step 2: Handle U.S. states as special cases
            states = fetch_us_states()
            for state in states:
                print(f"Processing state: {state['state']}")
                newspapers = fetch_newspapers(state['state_url'])
                for newspaper in newspapers:
                    print(f"Fetching website for newspaper: {newspaper['name']}")
                    real_website = fetch_real_website(newspaper['page_url'])
                    newspaper['real_website'] = real_website
                all_data[state['state']] = newspapers
        else:
            # Step 3: Process other countries
            newspapers = fetch_newspapers(country['url'])
            for newspaper in newspapers:
                print(f"Fetching website for newspaper: {newspaper['name']}")
                real_website = fetch_real_website(newspaper['page_url'])
                newspaper['real_website'] = real_website
            all_data[country['country']] = newspapers

    # Save the results to a JSON file in the specified folder
    file_path = os.path.join(folder_path, "newspapers.json")
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(all_data, file, indent=4)
    print(f"Data saved to {file_path}")

# Run the script
if __name__ == "__main__":
    fetch_newspapers_for_all()
"""


from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

# Base URL
base_url = "https://www.thepaperboy.com/"

# Function to fetch the list of countries and their links
def fetch_country_links():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(base_url, headers=headers)  # Add headers to mimic a browser
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        country_links = []
        for link in soup.find_all("a", href=True, class_="mediumlink"):  # Filter links with "mediumlink" class
            country_name = link.text.split(" (")[0].strip()  # Extract the country name
            relative_url = link["href"]  # Get the relative URL
            full_url = urljoin(base_url, relative_url)  # Convert to absolute URL
            country_links.append({"country": country_name, "url": full_url})
        return country_links
    else:
        print(f"Failed to fetch the main page. Status code: {response.status_code}")
        return []

# Example usage
if __name__ == "__main__":
    country_links = fetch_country_links()
    for country in country_links:
        print(f"Country: {country['country']}, URL: {country['url']}")

