"""
import pandas as pd
import json
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import re
from deep_translator import GoogleTranslator

def clean_search_term(term):
    term = re.sub(r'[^a-zA-Z0-9 ]', ' ', term)  # Remove special characters
    return term.replace(" ", "+")  # Replace spaces with +

def scrape_google_news(search_term, language, region, searched_terms):
    if search_term in searched_terms:
        print(f"Skipping duplicate search term: {search_term}")
        return []
    
    search_term = clean_search_term(search_term)
    url = f'https://www.google.com/search?q={search_term}&tbm=nws&hl={language}&gl={region}&tbs=qdr:w&ucbcb=1'
    articles = []
    searched_terms.add(search_term)  # Mark this term as searched

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/91.0.4472.124 Safari/537.36")
        )
        page = context.new_page()
        try:
            print(f"Searching for: {search_term}")
            page.goto(url, timeout=60000)
            time.sleep(2)  # Wait for the page to load completely
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            results = soup.select('div.SoAPf')
            num_results = 0

            for result in results:
                headline_element = result.select_one('div.n0jPhd.ynAwRc.MBeuO.nDgy9d')
                source_element = result.select_one('div.MgUUmf.NUnG9d span')
                snippet_element = result.select_one('div.GI74Re.nDgy9d')
                date_element = result.select_one('div.OSrXXb.rbYSKb.LfVVr span')
                link_element = result.find_parent('a')
                
                headline = translate_to_english(headline_element.text) if headline_element else 'N/A'
                link = link_element['href'] if link_element else 'N/A'
                source = translate_to_english(source_element.text) if source_element else 'N/A'
                snippet = translate_to_english(snippet_element.text) if snippet_element else 'N/A'
                date_published = date_element.text if date_element else 'N/A'

                print(f"Headline found: {headline}")
                num_results += 1

                articles.append({
                    'search_term': search_term,
                    'headline': headline,
                    'link': link,
                    'source': source,
                    'snippet': snippet,
                    'date_published': date_published
                })

            print(f"✅ {num_results} articles found for search term: {search_term}\n")
        except Exception as e:
            print(f"An error occurred while processing '{search_term}': {e}")
        finally:
            browser.close()

    return sorted(articles, key=lambda x: x['date_published'], reverse=True)  # Sort by most recent

def translate_to_english(text):
    if text:
        try:
            return GoogleTranslator(source='auto', target='en').translate(text)
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    return ""

def main():
    searched_terms = set()
    country_language_region = {
        'DE': ('de', 'DE'),  # Germany
        'US': ('en', 'US'),  # United States
        'TN': ('fr', 'TN')
    }

    test_cases = [
        ("Foxconn", 'en', 'US'),  # One supplier
        ("A8 Deutschland", 'de', 'DE'),  # One road with a country
        ("A1 Tunisie", 'fr', 'TN'),  # One road with nan as country
        ("Foxconn", 'en', 'US'),  # Duplicate to check
        ("A8 Deutschland", 'de', 'DE')  # Duplicate to check
    ]

    all_articles = {}
    for search_term, language, region in test_cases:
        articles = scrape_google_news(search_term, language, region, searched_terms)
        all_articles[search_term] = articles
    
    # Save results in JSON format
    with open('test_scraped_news_r.json', 'w', encoding='utf-8') as json_file:
        json.dump(all_articles, json_file, indent=4, ensure_ascii=False)
    
    print("✅ Test execution complete. JSON file saved successfully.")

if __name__ == "__main__":
    main()




"""
import pandas as pd
import json
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import re
from deep_translator import GoogleTranslator
from langdetect import detect

python_special_characters = [
    "+", "-", "*", "/", "//", "%", "**","==", "!=", ">", "<", ">=", "<=",
    "=", "+=", "-=", "*=", "/=", "//=", "%=", "**=", "&=", "|=", "^=", ">>=", "<<=",
    "&", "|", "^", "~", "<<", ">>","(", ")", "[", "]", "{", "}", ":", ",", ".", ";", "@",
      "->", "...","'", "\"", "'''", "\"\"\"", "\\", "#", "\0", "_", "*", "**", "$", "!", "?", "`",":="]

def clean_search_term(term):
    for char in python_special_characters:
        term = term.replace(char, " ")  # Replace each special character with a space
    term = re.sub(r'\s+', '+', term.strip())  # Replace multiple spaces with a single +
    return term

def detect_and_translate(text, target_lang):
    if text:
        try:
            detected_lang = detect(text)
            if detected_lang == target_lang:
                return text  # Use as-is if already in the target language
            return GoogleTranslator(source='auto', target=target_lang).translate(text)
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    return ""

def scrape_google_news(search_term, language, region, searched_terms):
    if search_term in searched_terms:
        print(f"Skipping duplicate search term: {search_term}")
        return []
    
    search_term = clean_search_term(search_term)
    url = f'https://www.google.com/search?q={search_term}&tbm=nws&hl={language}&gl={region}&tbs=qdr:w&ucbcb=1'
    articles = []
    searched_terms.add(search_term)  # Mark this term as searched

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/91.0.4472.124 Safari/537.36")
        )
        page = context.new_page()
        try:
            print(f"Searching for: {search_term}")
            page.goto(url, timeout=60000)
            time.sleep(2)  # Wait for the page to load completely
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            results = soup.select('div.SoAPf')
            num_results = 0

            for result in results:
                headline_element = result.select_one('div.n0jPhd.ynAwRc.MBeuO.nDgy9d')
                source_element = result.select_one('div.MgUUmf.NUnG9d span')
                snippet_element = result.select_one('div.GI74Re.nDgy9d')
                date_element = result.select_one('div.OSrXXb.rbYSKb.LfVVr span')
                link_element = result.find_parent('a')
                
                headline = detect_and_translate(headline_element.text, 'en') if headline_element else 'N/A'
                link = link_element['href'] if link_element else 'N/A'
                source = detect_and_translate(source_element.text, 'en') if source_element else 'N/A'
                snippet = detect_and_translate(snippet_element.text, 'en') if snippet_element else 'N/A'
                date_published = date_element.text if date_element else 'N/A'

                print(f"Headline found: {headline}")
                num_results += 1

                articles.append({
                    'search_term': search_term,
                    'headline': headline,
                    'link': link,
                    'source': source,
                    'snippet': snippet,
                    'date_published': date_published
                })

            print(f"✅ {num_results} articles found for search term: {search_term}\n")
        except Exception as e:
            print(f"An error occurred while processing '{search_term}': {e}")
        finally:
            browser.close()

    return sorted(articles, key=lambda x: x['date_published'], reverse=True)  # Sort by most recent

def main():
    excel_file = "/Users/yassinezahrouni/coding/test/CountryIndexes/DB_SupplyChain_MA.xlsx"
    suppliers_df = pd.read_excel(excel_file, sheet_name="Suppliers", engine="openpyxl")
    segments_df = pd.read_excel(excel_file, sheet_name="ShipmentSegments", engine="openpyxl")

    country_language_region = {
        'CN': ('zh-CN', 'CN'),  # China
        'DE': ('de', 'DE'),  # Germany
        'KR': ('ko', 'KR'),  # South Korea
        'IN': ('en', 'IN'),  # India (Using English)
        'IE': ('en', 'IE'),  # Ireland
        'ES': ('es', 'ES'),  # Spain
        'IT': ('it', 'IT'),  # Italy
        'FR': ('fr', 'FR'),  # France
        'GB': ('en', 'GB'),  # United Kingdom
        'SG': ('en', 'SG'),  # Singapore
        'CA': ('en', 'CA'),  # Canada
        'PL': ('pl', 'PL'),  # Poland
        'TN': ('fr', 'TN'),  # Tunisia (Using French)
        'BR': ('pt', 'BR'),  # Brazil
        'AU': ('en', 'AU'),  # Australia
        'MA': ('fr', 'MA'),  # Morocco (Using French)
        'TR': ('tr', 'TR'),  # Turkey
        'US': ('en', 'US'),  # United States
        'JP': ('ja', 'JP'),  # Japan
    }

    searched_terms = set()
    all_articles = {}

    # Process suppliers
    for supplier_name in suppliers_df['name']:
        search_term = clean_search_term(supplier_name)
        language, region = 'en', 'US'  # Always use English and US region
        articles = scrape_google_news(search_term, language, region, searched_terms)
        all_articles[search_term] = articles

    # Process roads and ports
    for _, row in segments_df.iterrows():
        country_code = row['Country of roads']
        roads = row['Roads'].split(';')
        
        if pd.notna(country_code) and country_code in country_language_region:
            language, region = country_language_region[country_code]
            translated_country = detect_and_translate(country_code, language)
        else:
            language, region = 'en', 'US'
            translated_country = ''

        for road in roads:
            translated_road = detect_and_translate(road.strip(), language)
            search_term = clean_search_term(f"{translated_road}+{translated_country}").strip("+")
            articles = scrape_google_news(search_term, language, region, searched_terms)
            all_articles[search_term] = articles
    
    with open('news_roads_suppliers_ports.json', 'w', encoding='utf-8') as json_file:
        json.dump(all_articles, json_file, indent=4, ensure_ascii=False)
    
    print("✅ Execution complete. JSON file saved successfully.")

if __name__ == "__main__":
    main()