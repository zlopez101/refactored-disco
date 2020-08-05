import alpaca_trade_api as tradeapi
from db_utils import credentialing, business_day
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

endpoint_1, endpoint_2 = (
    "http://sec.gov/cgi-bin/browse-edgar?CIK=",
    "&Find=Search&owner=exclude&action=getcompany",
)


def get_data(symbol):
    """
    get the 1 minute aggregate data for trading on 7/15
    """
    url, key, secret = credentialing()
    api = tradeapi.REST(key, secret, url)
    if symbol.lower() == "random":
        assets = api.list_assets()
        symbols = [
            asset.symbol
            for asset in assets
            if asset.tradable
            and asset.exchange == "NYSE"
            and asset.status == "active"
            and asset.shortable
        ]
        symbol = np.random.choice(symbols)

    start, end = business_day()
    df = api.polygon.historic_agg_v2(
        symbol,
        1,
        "minute",
        _from=pd.Timestamp(start).isoformat(),
        to=pd.Timestamp(end).isoformat(),
    ).df
    # df = df[np.logical_and(df.index >= start, df.index <= end)]
    return df, symbol


def get_soup():
    _, symbol = get_data("random")
    print(symbol)

    r = requests.get(endpoint_1 + symbol + endpoint_2)

    soup = BeautifulSoup(r.text, features="html.parser")

    return symbol, soup
