import os
from datetime import datetime
from pytz import timezone
import backtrader as bt
import alpaca_trade_api as tradeapi

import pandas as pd
import numpy as np


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
    start = datetime(2020, 7, 15, 9, 30).astimezone(nyc)
    end = datetime(2020, 7, 15, 16, 0).astimezone(nyc)
    return start, end


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
    df = df[np.logical_and(df.index >= start, df.index <= end)]
    return df, symbol


def get_best_parameters(lst):
    """
    The list will have be made of tuples of the result. The parameters specifed will be the first values and ending portfolio value of the simulation is last value.
    """
    best = np.argmax([sim[-1] for sim in lst])
    return best


def get_ranges(dct, ls):
    """
    return ranges for specified keys. Values of keys are lists of len 2 of type [start,  stop]
    """
    keys = list(dct.keys())
    if len(keys) == 0:
        return ls
    else:
        rn = dct.pop(keys[0])
        ls.append(range(rn[0], rn[1]))
        return get_ranges(dct, ls)


def ensure_correct_data_calculation_choice(on_data):
    """
    helper function for checking the str value of on_data
    """
    column_choices = ["close", "open", "low", "high", "volume"]
    if on_data.lower() not in column_choices:
        raise ValueError(f"Invalid Data Column Selection. {on_data} not in DataFrame.")
