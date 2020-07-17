import os
import requests
from datetime import datetime, timedelta
import pandas as pd
from pytz import timezone


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
    nyc = timezone("America/New_York")
    today = datetime.today().astimezone(nyc)
    start = datetime(today.year, today.month, today.day, 8, 00).astimezone(nyc)
    end = datetime(today.year, today.month, today.day, 15, 30).astimezone(nyc)
    return start, end


def get_tickers(api, min_share_price, max_share_price, min_dv, quick=False):
    """
    get all tickers that meet the criteria of min_share_price, max_share_price, min_last_dv, todaysChangePerc
    """
    print("Getting current ticker data...")
    # tickers = api.polygon.all_tickers()
    start, _ = business_day()
    yesterday = start - timedelta(days=1)
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
            data = api.polygon.daily_open_close(symbol, yesterday.strftime("%Y-%m-%d"))
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


def cancel_old_orders(api, orders, order_expiration=2):
    """
    Cancels orders that exceed order_expiration in minutes

    : param api: Alpaca REST endpoint
    : dict orders: a dictionary with symbols for keys and orders for values
    : int order_expiration: int for minutes to leave orders open 
    """
    current_time = api.get_clock().timestamp
    old_orders = [
        order.id
        for order in orders.values()
        if (order.status == "held" or order.status == "new")
        and order.submitted_at + timedelta(minutes=order_expiration) > current_time
    ]
    for order in old_orders:
        try:
            api.cancel_order(order)
        except Exception as e:
            print(e)
            print(f"Unable to cancel order id {order}")
