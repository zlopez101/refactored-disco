import requests
import json

r = requests.get("https://api.stocktwits.com/api/2/streams/trending.json")

print(type(r.json()))
