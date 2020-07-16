import os
from datetime import datetime
from pytz import timezone
from backtrader.feed import DataBase


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
    nyc = timezone("America/New_York")
    today = datetime.today().astimezone(nyc)
    start = datetime(today.year, today.month, today.day, 8, 00).astimezone(nyc)
    end = datetime(today.year, today.month, today.day, 15, 30).astimezone(nyc)
    return start, end


class PandasData(DataBase):

    params = (
        ("datetime", None),
        ("open", -1),
        ("high", -1),
        ("low", -1),
        ("volume", -1),
        ("close", -1),
        ("openinterest", None),
    )
