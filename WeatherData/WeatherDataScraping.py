import datetime as dt 
import requests

BASE_URL = 'http://api.openweathermap.org/data/2.5/weather?'
API_KEY = '3bce3b17069693c955bf4431c09a1407'
city = 'Munich'
url = BASE_URL  + "appid=" + API_KEY + "&q=" + city 
response = requests.get(url).json()
print(response)
