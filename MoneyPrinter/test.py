import os
import pandas as pd
from ta.momentum import rsi
import alpaca_trade_api as tradeapi
import requests
from datetime import datetime, timedelta
from utils import credentialing
import time

base_url = os.environ.get("rALPACA_ENDPOINT")
api_key_id = os.environ.get("rALPACA_API_KEY")
api_secret = os.environ.get("rALPACA_API_SECRET")

api = tradeapi.REST(base_url=base_url, key_id=api_key_id, secret_key=api_secret)


def get_tickers(api, min_share_price, max_share_price, min_last_dv):
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
    for symbol in symbols[:10]:
        try:
            data = api.polygon.daily_open_close(symbol, "2020-07-10")
            if (
                data.close >= min_share_price
                and data.close <= max_share_price
                and data.volume * data.close > min_last_dv
            ):
                dct[symbol] = api.polygon.daily_open_close(symbol, "2020-07-10")
        except requests.exceptions.HTTPError:
            print(f"Symbol {symbol} gave an error, excluding from universe.")
    print(f"Including {len(data.keys())} stocks for trading today.")
    return dct


def create_api():
    url, key, secret = credentialing()
    api = tradeapi.REST(key_id=key, base_url=url, secret_key=secret)
    return api

