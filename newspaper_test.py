import os
from datetime import datetime
from newspaper import build, Article
import newspaper
"""
def save_headlines_to_file(url):
    # Define the relative folder path
    folder_path = "./NewsData/NewsData_withDate"
    
    # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)
    
    # Generate a filename with the current date
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(folder_path, f"headlines_{date_str}.txt")

    try:
        # Build the newspaper source
        paper = build(url, memoize_articles=False)
        
        print(f"Found {len(paper.articles)} articles on {url}")
        
        # Open the file to write headlines
        with open(file_path, "w", encoding="utf-8") as file:
            for article in paper.articles:
                try:
                    article.download()
                    article.parse()
                    # Write the headline to the file
                    file.write(article.title + "\n")
                except Exception as e:
                    print(f"Error processing article {article.url}: {e}")
        
        print(f"Headlines saved to {file_path}")
    except Exception as e:
        print(f"Error building newspaper for {url}: {e}")

# Example usage
save_headlines_to_file("https://www.tunisienumerique.com")
"""

TN_paper = newspaper.build('https://www.tunisienumerique.com', memoize_articles=False)
print(TN_paper.size())

#for article in TN_paper.articles:
 #   print(article.url)

first_article = newspaper.Article("https://www.tunisienumerique.com/france-jean-marie-le-pen-est-mort/")
first_article.download()
first_article.parse()
print(first_article.text)



"""
import os
from datetime import datetime
from newspaper import build, Article
from googletrans import Translator
from concurrent.futures import ThreadPoolExecutor

def fetch_and_translate_article(article, translator):
    
    #Fetch and translate an article's headline, content, and publication date.
    #:param article: Newspaper article object.
    #:param translator: Google Translator object.
    #:return: Dictionary with headline, translated content, and date.
    
    try:
        article.download()
        article.parse()
        
        # Extract data
        headline = article.title
        content = article.text
        pub_date = article.publish_date

        # Translate full content
        content_translated = translator.translate(content, dest="en").text if content else "N/A"
        
        return {
            "headline": headline,
            "content_translated": content_translated,
            "pub_date": pub_date.strftime("%Y-%m-%d %H:%M:%S") if pub_date else "Unknown"
        }
    except Exception as e:
        print(f"Error processing article: {e}")
        return None

def save_articles_to_file(articles, folder_path, file_prefix="articles"):
    
    #Save article data to a file in the specified folder.
    #:param articles: List of dictionaries containing article data.
    #:param folder_path: Path to the folder where the file should be saved.
    #:param file_prefix: Prefix for the filename.
    
    os.makedirs(folder_path, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(folder_path, f"{file_prefix}_{date_str}.txt")
    
    with open(file_path, "w", encoding="utf-8") as file:
        for article in articles:
            if article:
                file.write(f"Headline: {article['headline']}\n")
                file.write(f"Publication Date: {article['pub_date']}\n")
                file.write(f"Content (Translated):\n{article['content_translated']}\n")
                file.write("\n" + "-"*80 + "\n")
    print(f"Articles saved to {file_path}")

def scrape_and_translate_website(url, max_articles=None):
    
    #Scrape and translate articles from a website.
    #:param url: Website URL to scrape.
    #:param max_articles: Limit the number of articles to process.
    
    folder_path = "./NewsData/NewsData_withDate"
    translator = Translator()

    try:
        # Build the newspaper source
        paper = build(url, memoize_articles=False)
        articles = paper.articles[:max_articles] if max_articles else paper.articles

        print(f"Found {len(articles)} articles on {url}")
        
        # Use multithreading for faster article processing
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda article: fetch_and_translate_article(article, translator), articles))
        
        # Save results to file
        save_articles_to_file([res for res in results if res], folder_path)
    except Exception as e:
        print(f"Error scraping website {url}: {e}")

# Example usage
scrape_and_translate_website("https://www.tunisienumerique.com", max_articles=50)

"""