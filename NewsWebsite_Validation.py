"""
import requests
from bs4 import BeautifulSoup

url = 'https://airlines.einnews.com'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')  # Specify parser for BeautifulSoup

metas = soup.find_all('meta')

# Correctly iterate through the generator and print results
descriptions = [meta.attrs['content'] for meta in metas if 'name' in meta.attrs and meta.attrs['name'] == 'description']
print(descriptions)
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from googletrans import Translator

EXCLUDED_DOMAINS = ['gov', 'edu', 'org', 'youtube.com', 'vimeo.com']
NEWS_KEYWORDS = ["news", "journal", "gazette", "media", "radio", "broadcast", "fm", "tv", "television", "channel", 
                 "press", "report", "headline", "local", "regional", "community", "magazine", "events", "update"]

translator = Translator()

def get_news_source_type(keyword):
    """
    Determine the type of news source based on the keyword.
    :param keyword: The keyword found in the meta description or structured data.
    :return: The type of news source (e.g., News Website, Radio, TV).
    """
    if keyword in ["radio", "broadcast", "fm"]:
        return "Radio Website"
    elif keyword in ["tv", "television", "channel"]:
        return "Television Website"
    elif keyword in ["magazine", "gazette", "journal"]:
        return "Magazine Website"
    elif keyword in ["social media", "blog"]:
        return "Social Media or Blog"
    else:
        return "News Website"

def is_news_source(url):
    """
    Determine if a website is a pure news source and log meta description details.
    Translate the meta description to English before checking for keywords.
    Exclude university media and online video channels.
    :param url: URL of the website.
    :return: Tuple (is_news_source, meta_description, found_keyword, source_type)
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Check domain
        domain = urlparse(url).netloc
        if any(domain.endswith(f".{tld}") for tld in EXCLUDED_DOMAINS):
            return False, None, None, None

        # Check meta description
        meta_description = soup.find("meta", attrs={"name": "description"})
        meta_description_content = meta_description["content"] if meta_description else "None"

        # Translate meta description to English
        try:
            translated_description = translator.translate(meta_description_content, dest="en").text.lower()
        except Exception as e:
            print(f"Error translating meta description: {e}")
            translated_description = meta_description_content.lower()

        # Check for keywords in translated meta description
        for keyword in NEWS_KEYWORDS:
            if keyword in translated_description:
                source_type = get_news_source_type(keyword)
                return True, meta_description_content, keyword, source_type

        # Check structured data for NewsMediaOrganization or BroadcastService
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            if any(keyword in script.text for keyword in ["NewsMediaOrganization", "BroadcastService"]):
                return True, meta_description_content, "structured data", "News Website"

        # Fallback: Check domain for radio-related keywords
        if "radio" in domain or "fm" in domain:
            return True, meta_description_content, "domain keyword", "Radio Website"

    except Exception as e:
        print(f"Error processing {url}: {e}")
        return False, None, None, None

    return False, meta_description_content, None, None

# Example usage
urls = [
    "https://oem.com.mx/eloccidental/",
    "https://guadalajara.gob.mx/gdlWeb/#/detalle/2168/Inauguran-el-Polgono-Ramn-Corona-la-primera-Zona-de-Bajas-Emisiones-en-Mxico",
    "https://www.dshs-koeln.de/institut-fuer-paedagogik-und-philosophie/aktuelles/nachrichten-infos/",
    "https://www.mosaiquefm.net/ar/actualites/%D8%AA%D9%88%D9%86%D8%B3-%D9%88%D8%B7%D9%86%D9%8A%D8%A9/1",
    "https://www.nessma.tv/ar/actualites",
    "https://www.ifm.tn/ar/articles",
    "https://tn.linkedin.com",
    "https://www.skyscanner.fr",
    "https://www.governo.it",
    "https://www.office-tourisme-usa.com",
    "https://partir.ouest-france.fr",
    "https://www.univ-orleans.fr",
    "https://mapecology.ma",
    "https://www.bbk.bund.de",
    "https://www.udg.mx",
    "https://www.stadt-koeln.de",
    "https://www.mapnews.ma/ar/"
]

for url in urls:
    is_news, meta_desc, keyword, source_type = is_news_source(url)
    print(f"{url} is a news source: {is_news}")
    print(f"Meta description: {meta_desc}")
    if keyword:
        print(f"Found keyword: {keyword}")
        print(f"Source type: {source_type}")
    print("-")


