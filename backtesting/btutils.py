import os
from datetime import datetime
from pytz import timezone
from backtrader.feed import DataBase
import alpaca_trade_api as tradeapi
import pandas as pd
from numpy import logical_and


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


# class PandasData(DataBase):

#     params = (
#         ("datetime", None),
#         ("open", -1),
#         ("high", -1),
#         ("low", -1),
#         ("volume", -1),
#         ("close", -1),
#         ("openinterest", None),
#     )


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
