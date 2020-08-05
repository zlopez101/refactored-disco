import os
from pytz import timezone
from datetime import datetime


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
    today = datetime.today()
    start = datetime(today.year, today.month, (today.day - 1)).astimezone(nyc)
    end = datetime(today.year, today.month, (today.day - 1), 22, 59).astimezone(nyc)
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
    # df = df[np.logical_and(df.index >= start, df.index <= end)]
    return df, symbol
