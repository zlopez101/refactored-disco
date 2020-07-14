"""
Full credit goes Teddy Koker, this code was shamelessly copied from his github page. 
https://github.com/teddykoker
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import json

# request page
html = requests.get("https://www.ishares.com/us/products/239726/#tabsAll").content
soup = BeautifulSoup(html, "html.parser")

# find available dates
holdings = soup.find("div", {"id": "holdings"})
dates_div = holdings.find_all("div", "component-date-list")[1]
dates_div.find_all("option")
dates = [option.attrs["value"] for option in dates_div.find_all("option")]
print(len(dates))
# download constituents for each date
constituents = {}
for date in dates:
    resp = requests.get(
        f"https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/1467271812596.ajax?tab=all&fileType=json&asOfDate={date}"
    ).content[3:]
    tickers = json.loads(resp)
    tickers = [(arr[0], arr[1]) for arr in tickers["aaData"]]
    date = datetime.strptime(date, "%Y%m%d")
    constituents[date] = tickers

df = pd.DataFrame(constituents)
print(df.head())
