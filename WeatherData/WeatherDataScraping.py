import os
import json
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Function to scrape weather news
def scrape_weather_news(city="Munich"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to False to see browser actions
        context = browser.new_context()
        page = context.new_page()
        
        url = 'https://www.wunderground.com/'
        page.goto(url)
        
        # Wait for the search box to be available
        page.wait_for_selector('input[name="query"]', timeout=10000)
        
        # Search for the city (Munich)
        search_box = page.locator('input[name="query"]')
        search_box.fill(city)
        search_box.press('Enter')

        time.sleep(5)  # Allow time for page to load

        # Get page content
        soup = BeautifulSoup(page.content(), 'html.parser')

        # Extract weather news
        weather_news = []
        news_section = soup.find('section', {'class': 'news'})

        if news_section:
            news_items = news_section.find_all('article')
            for news in news_items:
                title = news.find('h3').text.strip() if news.find('h3') else "No title"
                link = news.find('a')['href'] if news.find('a') else "No link"
                summary = news.find('p').text.strip() if news.find('p') else "No summary"
                
                weather_news.append({
                    "title": title,
                    "link": f"https://www.wunderground.com{link}",
                    "summary": summary
                })
        else:
            print(f"No news found for {city}.")

        browser.close()
        return weather_news

# Function to save data as JSON
def save_weather_data(city, data):
    folder_path = "WeatherData"
    os.makedirs(folder_path, exist_ok=True)  # Create the folder if it doesn't exist

    file_path = os.path.join(folder_path, f"{city.replace(' ', '_')}_weather_news.json")
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    
    print(f"Weather news for {city} saved in {file_path}")

# Scrape and save weather news for Munich
news_data = scrape_weather_news()
save_weather_data("Munich", news_data)

