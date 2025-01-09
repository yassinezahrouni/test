"""from requests_html import HTMLSession 

session = HTMLSession()

url = "https://www.google.com/search?q=actualit%C3%A9s+tunisie"

r = session.get(url)

r.html.render()

articles = r.html.find('article')

for item in articles:
    newsitem = item.find('cite', first=True)
    #title = newsitem.text
    #link = newsitem.absolute_links
    print(newsitem)

#print(articles)


# Google Search URL
search_url = "https://www.google.com/search?q=actualit%C3%A9s+tunisie&num=20"
response = session.get(search_url)
response.html.render(timeout=20)  # Render JavaScript content
print(response)"""

import requests
from bs4 import BeautifulSoup 
import datetime

def gettitle(x):
    url = f'https://scrapethissite.com/pages/forms/?page_num={x}'
    r = requests.get(url)
    sp = BeautifulSoup(r.text, 'html.parser')
    print(sp.title.text)
    return

def gettitle_session(x):
    url = f'https://scrapethissite.com/pages/forms/?page_num={x}'
    r = s.get(url)
    sp = BeautifulSoup(r.text, 'html.parser')
    #sp.find_all('div')
    print("html: ", sp.prettify())
    print(sp.title.text)
    return 

# no session   0:00:15.545124
# with session 0:00:06.448914

if __name__ == '__main__':
    s = requests.Session()
    start = datetime.datetime.now()
    for x in range (1,2) :
        gettitle_session(x)
    finish = datetime.datetime.now() - start
    print(finish)