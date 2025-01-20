
import requests
from bs4 import BeautifulSoup

def get_news_sources_by_country_newspaperlist(countries):
    base_url = "https://newspaperlists.com/{country}"
    all_news_sources_newspaperlist = {}

    for country in countries:
        # Construct the country-specific URL
        url = base_url.format(country=country.lower())  # Ensure the country name is lowercase
        
        print(f"Fetching news sources for: {country}")
        
        # Send a GET request to fetch the webpage content
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Find the specific <div> with class "hps"
            hps_div = soup.find("div", class_="hps")
            
            # Ensure the <div class="hps"> exists
            if hps_div:
                # Find the nested <div class="li1"> inside <div class="hps">
                li1_div = hps_div.find("div", class_="li1")
                
                # Ensure the <div class="li1"> exists
                if li1_div:
                    # Find the <ul> inside <div class="li1">
                    ul_tag = li1_div.find("ul")
                    
                    # Ensure the <ul> exists
                    if ul_tag:
                        newspapers = []
                        # Iterate through <li> elements under the <ul>
                        for li in ul_tag.find_all("li"):
                            # Find the <a> tag within the <li>
                            link = li.find("a", href=True)
                            if link:
                                # Extract the name and URL
                                name = link.text.strip()
                                href = link['href']
                                newspapers.append({"name": name, "url": href})
                        
                        # Store the results for this country
                        all_news_sources_newspaperlist[country] = newspapers
                    else:
                        print(f"No <ul> found inside <div class='li1'> for {country}.")
                else:
                    print(f"No <div class='li1'> found inside <div class='hps'> for {country}.")
            else:
                print(f"No <div class='hps'> found for {country}.")
        else:
            print(f"Failed to fetch the webpage for {country}. Status code: {response.status_code}")
    
    return all_news_sources_newspaperlist


def get_news_sources_by_country_allyoucanread(countries):
    base_url = "https://www.allyoucanread.com/{country}-newspapers/"
    all_news_sources_allyoucanread = {}

    for country in countries:
        # Format the country name to construct the URL
        formatted_country = country.lower().replace(" ", "-")
        url = base_url.format(country=formatted_country)

        print(f"Fetching news sources for: {country} ({url})")

        # Send a GET request to fetch the webpage content
        response = requests.get(url)

        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

            # Find all <a> tags containing nested <h3> with the specific class
            newspapers = []
            for link in soup.find_all("a", href=True):  # Iterate through all <a> tags
                h3 = link.find("h3", class_="font-oswald text-sky-900")  # Look for nested <h3>
                if h3:
                    # Extract the name and URL
                    name = h3.text.strip()
                    href = link['href']
                    newspapers.append({"name": name, "url": href})
            
            # Add the newspapers list to the result dictionary
            all_news_sources_allyoucanread[country] = newspapers
        else:
            print(f"Failed to fetch the webpage for {country}. Status code: {response.status_code}")
    
    return all_news_sources_allyoucanread

# Example usage
countries = ["tunisia", "egypt", "morocco"]  # List of countries
news_sources_newspaperlist = get_news_sources_by_country_newspaperlist(countries)
news_sources_allyoucanread = get_news_sources_by_country_allyoucanread(countries)

news_sources = news_sources_newspaperlist.copy()  # Create a copy to avoid modifying the original
news_sources.update(news_sources_allyoucanread)


# Print the results
for country, sources in news_sources.items():
    print(f"\nNews sources for {country.capitalize()}:")
    for source in sources:
        print(f"Name: {source['name']}, URL: {source['url']}")


