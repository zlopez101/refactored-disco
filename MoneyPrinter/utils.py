import os
import requests
from datetime import datetime
import pandas as pd


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


def create_dict(symbols):
    """
    creates a master dictionary with each symbol pointing to a dataframe of data collected from the stream. 
    """
    dct = {}

    def create_dataframe():
        """
        Helper function to create a dataframe that is the value for each SYMBOL key in the dictionary
        """
        column_names = ["open", "high", "low", "close", "volume"]

        def get_trading_start():
            """
            Helper function gets the start of the trading day
            """
            today = datetime.today().date()
            start = datetime(today.year, today.month, today.day, hour=8, minute=30)
            return start

        idx = pd.date_range(get_trading_start(), periods=900, freq="T")
        df = pd.DataFrame(columns=column_names, index=idx)
        return df

    for symbol in symbols:
        dct[symbol] = create_dataframe()

    return dct


def business_day():
    today = datetime.today()
    start = datetime(today.year, today.month, today.day, 8, 00)
    end = datetime(today.year, today.month, today.day, 3, 30)
    return start, end


def get_tickers(api, min_share_price, max_share_price, min_dv, quick=False):
    """
    get all tickers that meet the criteria of min_share_price, max_share_price, min_last_dv, todaysChangePerc
    """
    print("Getting current ticker data...")
    # tickers = api.polygon.all_tickers()

    assets = api.list_assets(status="active", asset_class="us_equity")
    symbols = [
        asset.symbol
        for asset in assets
        if asset.tradable
        and asset.exchange == "NYSE"
        and asset.status == "active"
        and asset.shortable
    ]
    dct = {}
    if quick:
        symbols = symbols[:10]
    for symbol in symbols:
        try:
            data = api.polygon.daily_open_close(symbol, "2020-07-13")
            if (
                data.close >= min_share_price
                and data.close <= max_share_price
                and data.volume * data.close > min_dv
            ):
                dct[symbol] = data
        except requests.exceptions.HTTPError:
            print(f"Symbol {symbol} gave an error, excluding from universe.")
    s = list(dct.keys())
    print(f"collected {len(s)} symbols.")
    return s


def targets(price, simple=True):
    """
    returns the take profit and the stop loss prices
    """
    if simple:
        return price * 1.02, price * 0.99
