import os
from datetime import datetime
from newspaper import Source
import warnings
import pandas as pd

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="newspaper")

def process_articles(url, folder_path="./NewsData/NewsData_withDate"):

    #Process articles from a given newspaper URL, saving today's articles to a file.

    #Args:
     #   url (str): The URL of the newspaper.
      #  folder_path (str): The folder path to save the articles file.

    #Returns:
     #   None
    try:
        # Initialize the newspaper source
        paper = Source(url)
        paper.build()

        # Automatically identify the newspaper name using the 'brand' attribute
        newspaper_name = paper.brand

        # Store today's date for filtering and file naming
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")  # Format date as YYYY-MM-DD

        # Ensure the folder exists
        os.makedirs(folder_path, exist_ok=True)

        # Define the file name
        file_name = f"Articles_{today_str}.csv"
        file_path = os.path.join(folder_path, file_name)

        # List to store article data
        today_articles = []

        # Iterate through the articles
        for article in paper.articles:

            try:
                # Download and parse the article
                article.download()
                article.parse()

                # Get the publication date
                pub_date = article.publish_date
                if pub_date is not None and pub_date.date() == today:  # Check if the article is from today
                    today_articles.append({
                        "Newspaper": newspaper_name,
                        "Title": article.title,
                        "Category": article.source_url,  # Assuming category can be inferred from the URL
                        "Published Time": pub_date.strftime("%H:%M:%S"),  # Format time as HH:MM:SS
                        "URL": article.url
                    })
            except Exception as e:
                print(f"Error processing article: {e}")

        # Convert articles to a DataFrame and write or append to the file
        if today_articles:
            articles_df = pd.DataFrame(today_articles)

            if os.path.exists(file_path):
                # Append to the file
                articles_df.to_csv(file_path, mode='a', header=False, index=False)
                print(f"Appended {len(today_articles)} articles from {newspaper_name} to {file_path}")
            else:
                # Write a new file
                articles_df.to_csv(file_path, index=False)
                print(f"Created {file_path} with {len(today_articles)} articles.")
        else:
            print("No articles were published today.")

    except Exception as e:
        print(f"Error processing URL {url}: {e}")

# Example usage:
process_articles("https://www.tunisienumerique.com")

