import requests
from urllib.parse import urlparse, urlunparse

# Replace with your own API key and CX
API_KEY = "AIzaSyBhgM9ucPG5vSqo7eqSE6MXp0GmTLPs-MQ"
CX = "9725ead1807594275"

def get_base_domain(url):
    """Extracts the base domain from a given URL."""
    parsed_url = urlparse(url)
    return parsed_url.netloc.replace("www.", "")  # Remove 'www.' for consistency

def google_search(query):
    """Performs a Google search using the Custom Search JSON API and returns the first result URL."""
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query
    }
    
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        results = response.json().get("items", [])
        if results:
            return results[0]["link"]  # Return first search result URL
    return None  # No results found

def check_page_validity_or_replace(url):
    """Checks if the searched website matches the first Google search result's base URL 
       and updates the URL while keeping the path."""
    
    parsed_url = urlparse(url)
    base_domain = get_base_domain(url)  # Extract base domain from input website
    
    # Perform a Google search for the website domain
    first_result_url = google_search(base_domain)
    if not first_result_url:
        return url  # If no result, return the original full URL
    
    first_result_domain = get_base_domain(first_result_url)  # Extract base domain from the first search result
    
    if base_domain == first_result_domain:
        return url  # Return original full URL if domains match
    else:
        # **Replace only the domain while keeping the original path**
        updated_url = urlunparse((
            parsed_url.scheme,  # Keep original scheme (http/https)
            first_result_domain,  # Replace with the corrected base domain
            parsed_url.path,  # Keep original path
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment
        ))
        return updated_url  # Return full updated URL with the corrected domain

# ✅ This allows the script to be used both directly and as an imported module
if __name__ == "__main__":
    website_input = input("Enter website URL to check: ")  # Only runs when executed directly
    updated_website = check_page_validity_or_replace(website_input)
    print("✅ Updated Website:", updated_website)
