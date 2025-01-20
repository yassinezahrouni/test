import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

# Define the Crawler Function
visited = set()

def crawl(url, base_url):
    if url not in visited:
        visited.add(url)
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    print(full_url)
                    time.sleep(1)  # Delay to avoid server overload
                    crawl(full_url, base_url)

# Starting URL
start_url = 'https://www.google.com/search?q=actualit%C3%A9s+tunisie'
crawl(start_url, start_url)
