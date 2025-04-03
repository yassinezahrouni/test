from serpapi import GoogleSearch

params = {
  "engine": "google_news",
  "q": "LG Innotek",
  "gl": "us",
  "hl": "en",
  "topic_token": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB",
  "api_key": "secret_api_key"
}

search = GoogleSearch(params)
results = search.get_dict()
news_results = results["news_results"]
print(results)