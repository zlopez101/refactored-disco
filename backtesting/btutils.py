import os
from datetime import datetime
from pytz import timezone
import backtrader as bt
import alpaca_trade_api as tradeapi

import pandas as pd
from numpy import logical_and, argmin


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
    returns business hours for July 8th, 2020. This date was picked randomly (coded on 7/16/2020)
    """
    nyc = timezone("America/New_York")
    start = datetime(2020, 7, 8, 8, 00).astimezone(nyc)
    end = datetime(2020, 7, 8, 15, 30).astimezone(nyc)
    return start, end


def get_data(symbol):
    """
    get the 1 minute aggregate data for trading on 7/8
    """
    url, key, secret = credentialing()
    api = tradeapi.REST(key, secret, url)
    start, end = business_day()
    df = api.polygon.historic_agg_v2(
        symbol,
        1,
        "minute",
        _from=pd.Timestamp(start).isoformat(),
        to=pd.Timestamp(end).isoformat(),
    ).df
    df = df[logical_and(df.index >= start, df.index <= end)]
    return df


def get_best_parameters(lst):
    """
    The list will have be made of tuples of the result. The parameters specifed will be the first values and ending portfolio value of the simulation is last value.
    """
    best = argmin([sim[-1] for sim in lst])
    return best


def _run(*args, **kwargs):
    pass
