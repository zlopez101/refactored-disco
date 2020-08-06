import os
from pytz import timezone
import pandas as pd
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
import time


def credentialing(paper=True):
    if paper:
        url = "https://paper-api.alpaca.markets"
        key = os.environ.get("ALPACA_API_KEY")
        secret = os.environ.get("ALPACA_API_SECRET")
    else:
        url = "https://api.alpaca.markets"
        key = os.environ.get("rALPACA_API_KEY")
        secret = os.environ.get("rALPACA_API_SECRET")
    return url, key, secret


def business_day():
    """
    returns business hours for July 15th, 2020. This date was picked randomly (re-coded on 7/20/2020)
    """
    nyc = timezone("America/New_York")
    start = datetime(2020, 1, 1, 0, 0).astimezone(nyc)
    end = datetime(2020, 7, 15, 23, 59).astimezone(nyc)
    return start, end


def get_data(symbol, start=None, end=None, normal=True):
    """
    get the 1 minute aggregate data for trading on 7/15
    """
    nyc = timezone("America/New_York")
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

    #     if normal:
    #         start, end = business_day()
    if normal:
        end = start + timedelta(days=40)
    df = api.polygon.historic_agg_v2(
        symbol,
        1,
        "minute",
        _from=pd.Timestamp(start).isoformat(),
        to=pd.Timestamp(end).isoformat(),
    ).df
    # df = df[np.logical_and(df.index >= start, df.index <= end)]
    return df, symbol


def lots_of_data(start, symbol):
    """
    takes about 3 minutes
    """
    nyc = timezone("America/New_York")
    data, symbol = get_data(symbol, start=start)
    now = datetime.now().astimezone(nyc)
    last = data.index[-1]
    while last < now - timedelta(hours=8):
        time.sleep(1)
        new_data, _ = get_data(symbol, last)
        last = data.index[-1]
        data = pd.concat([data, new_data])

    return symbol, data


def get_assets():
    url, key, secret = credentialing()
    api = tradeapi.REST(key, secret, url)
    assets = api.list_assets()
    symbols = [
        asset.symbol
        for asset in assets
        if asset.tradable
        and asset.exchange == "NYSE"
        and asset.status == "active"
        and asset.shortable
    ]
    return symbols

