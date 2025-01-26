import json
from playwright.sync_api import sync_playwright

def scrape_links():
    urls = [
        "https://onlinenewspapers.com/usstate/usatable.shtml",
        "https://onlinenewspapers.com/canada-province-newspapers.shtml",
        "https://onlinenewspapers.com/north-america-newspapers.shtml",
        "https://onlinenewspapers.com/africa-newspapers.shtml",
        "https://onlinenewspapers.com/asian-newspapers.shtml",
        "https://onlinenewspapers.com/south-america-newspapers.shtml",
        "https://onlinenewspapers.com/european-newspapers.shtml",
        "https://onlinenewspapers.com/oceania-newspapers.shtml",
    ]

    prefix = "https://onlinenewspapers.com"
    data = []

    def scrape_standard_list(page):
        items = page.locator("li > a.but")
        extracted = []
        for i in range(items.count()):
            href = items.nth(i).get_attribute("href")
            country = items.nth(i).inner_text()
            if href and country:
                extracted.append({"name": country, "link": prefix + href})
        return extracted

    def scrape_us_states(page):
        items = page.locator("table.usstateindex td a")
        extracted = []
        for i in range(items.count()):
            href = items.nth(i).get_attribute("href")
            state = items.nth(i).inner_text()
            if href and state:
                extracted.append({"name": state, "link": prefix + href})
        return extracted

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for url in urls:
            page = browser.new_page()
            page.goto(url)

            if "usstate/usatable.shtml" in url:
                data.extend(scrape_us_states(page))
            else:
                data.extend(scrape_standard_list(page))

        browser.close()

    # Save the data to a JSON file
    with open("onlinenewspapers_countries_links.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Scraped {len(data)} entries and saved to 'onlinenewspapers_countries_links.json'.")

if __name__ == "__main__":
    scrape_links()
