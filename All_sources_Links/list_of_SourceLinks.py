# News per country - file contains links to newspapers' websites for each country from which i have to scrape the articles
allyoucanread_links_path = "allyoucanread/allyoucanread_news_sources_websites.json"

# Business News for different industries - file contains RSS links to news for every industry from which i have to scrape the articles
Businesswire_links_path = 'Businesswire_NewsSources/businesswire_rss_links.json'
# scraping code to extract the articles from the RSS feeds using links from "Businesswire_links_path"
Businesswire__scraping_filepath = 'Businesswire_NewsSources/Businesswire_scraping_newsarticles_fromRSSlinks.py'

# Country indexes - file contains the indexes of each country (slavery index, bribery index, infrastructure index, ..)
Countryindexes_data_filepath = ''
Countryindexes__scraping_filepath = ''

# News per country - contains a lot of news with corresponding time and country of the news articles
gdelt_scraping_filepath = 'gdelt/GDELT_LatestDayData_download.py'

# Industry News - contains links of industry news websites from which i have to scrape the articles
IndustryOrgWebsites_links_path = 'News_based_on_IndustryOrgWebsites/links'

# News from Google News API - contains the code that will scrape the google news results when i query "news {supplier name}"
GoogleNewsAPI__scraping_filepath = 'News_GoogleNewsAPI_querying_suppliername/News_scraping_GoogleNewsAPI_suppliers.py'

# Newspaper general - contains names of news and data sources without links to the corresponding websites 
nexisuni_links_path = 'nexisuni/nexislexis_sourceslist_links.json'

# News per country - file contains links to newspapers' websites for each country from which i have to scrape the articles 
onlinenewspaper_links_path = 'onlinenewspaper/onlinenewspapers_scraped_newspapers.json'

# News per Region - contains newspapers' websites links for every region of the world from which i have to scrape the articles
Regions_top_newspapers_links_path = 'Regions_top_newssources/top_newssources.json'

# Supply chain magazines news - contains links to supply chain magazines websites from which i have to scrape the articles
SCM_magazines_links_path = 'SCM Magazines/SupplyChainMagazine_links.json'

# News per country - file contains links to newspapers' websites for each country from which i have to scrape the articles 
thepaperboy_links_path = 'thepaperboy/newspapers_websitelinks.json'

# News per country - file contains links to newspapers' websites for each country from which i have to scrape the articles 
w3newspapers_links_path = 'w3newspapers/w3newspapers_scraped_newspapers.json'

# Weather News - file contains RSS feed link to weather warnings for each country in Europe from which i have to scrape the warnings
WeatherWarningsEuropeanCountries_links_path = 'WeatherData/RSSfeed_WeatherAlerts_europeanCountries.json'
# Weather News - file contains RSS feed link to weather warnings for USA from which i have to scrape the warnings
WeatherWarningsUS_links_path = 'WeatherData/RSSfeed_WeatherAlerts_USarea.json'
# Weather News - file contains Scraping code to extract weather warnings for the global landscape
WeatherWarningsGlobal_scraping_filepath = 'WeatherData/WMO warnings/Warnings_scraping.py'

# Industry News - file contains scraping code to extract industry news articles from webwire website
Webwires_scraping_filepath = 'webwire/webwire_scraping_newsarticles_links.py'