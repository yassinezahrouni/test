import requests
from urllib.parse import urlparse
import pandas as pd

# Your News API key
API_KEY = "AIzaSyBo03D2rKdBJRfUsL9GvyRcWzDoxIMfCdg"  # Replace with your API key
CX = "9725ead1807594275"

# Define the Excel file path
excel_file = "/Users/yassinezahrouni/coding/test/CountryIndexes/DB_SupplyChain_MA.xlsx"

# Get the data from the DB & Read the sheets for suppliers
suppliers_df = pd.read_excel(excel_file, sheet_name="Suppliers", engine="openpyxl")

# Existing domains to exclude
exclude_domains = ["x.com", "facebook.com", "instagram.com", "tiktok.com", "linkedin.com", "reddit.com", "pinterest.com", "wikipedia.org", "youtube.com"]

# Search configuration for supplier-related news
country_code = "US"   # United States
language_code = "en"   # English


def get_base_domain(url):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    if '.' in netloc:
        return netloc.split('.')[-2] + '.' + netloc.split('.')[-1]  # Get the main domain
    return netloc


def get_company_domains(company_name, api_key, cx):
    search_query = f"{company_name} official website"
    base_url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'q': search_query,
        'cx': cx,
        'key': api_key,
        'num': 10,
        'hl': language_code,  # Set language
        'gl': country_code  # Set region
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    domains = set()
    if 'items' in data:
        for item in data['items']:
            official_url = item.get('link')
            if official_url:
                domain = get_base_domain(official_url).lower()
                domains.add(domain)
    return list(domains)


def perform_search(query, cx, api_key, sort=None):
    base_url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'q': query,
        'cx': cx,
        'key': api_key,
        'num': 10,
        'hl': language_code,  # Set language
        'gl': country_code  # Set region
    }
    if sort:
        params['sort'] = sort
    response = requests.get(base_url, params=params)
    return response.json()


def display_results(results, supplier_name, sort_type):
    if 'items' in results:
        print(f'\nTop 10 news results for {supplier_name} sorted by {sort_type}:\n')
        for item in results['items']:
            title = item.get('title')
            link = item.get('link')
            snippet = item.get('snippet')
            print(f'Title: {title}\nLink: {link}\nSnippet: {snippet}\n')
    else:
        print(f'No results found for {supplier_name} ({sort_type} sorting).')

# Iterate through each supplier and perform the search
for supplier_name in suppliers_df['name']:
    company_domains = get_company_domains(supplier_name, API_KEY, CX)
    supplier_exclude_domains = exclude_domains + company_domains
    
    # Construct the exclusion query
    exclusion_query = ' '.join([f'-site:{domain}' for domain in supplier_exclude_domains])
    query = f'{supplier_name} {exclusion_query}'
    
    # Fetch results sorted by relevance
    relevance_results = perform_search(query, CX, API_KEY)
    
    # Fetch results sorted by date
    date_results = perform_search(query, CX, API_KEY, sort='date')
    
    # Display results
    display_results(relevance_results, supplier_name, 'relevance')
    display_results(date_results, supplier_name, 'date')
