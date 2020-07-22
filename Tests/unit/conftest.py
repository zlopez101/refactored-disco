import pytest


@pytest.fixture(scope="module")
def api_setup():
    from MoneyPrinter.utils import credentialing
    import alpaca_trade_api as trade_api

    url, key, secret = credentialing(paper=True)
    api = trade_api.REST(key_id=key, secret_key=secret, base_url=url)
    return api


@pytest.fixture(scope="module")
def sample_symbols(api_setup):

    from numpy import random
    from MoneyPrinter.utils import get_tickers

    min_share = random.randint(1, 6)  # choose a random integer between 1 and 6
    max_share = random.randint(10, 15)  # choose a random integer between 10 and 15
    min_volume = random.normal(
        loc=1000000, scale=10000, size=1
    )  # choose a random value from a normal distribution center on 1 million with std of 10,000
    tickers = get_tickers(api_setup, min_share, max_share, min_volume, quick=True)
    return min_share, max_share, min_volume, tickers

@pytest.fixture(scope='module'):
def sample_data():
    """
    create 3 sample data flows of length 100. 
    """
    import pandas as pd
    from datetime import datetime
    now = datetime.now()
    idx = pd.date_range("2020-07-20 8:00", periods=100, freq="T")

    # create with 1 signal
    


    # create with 2 signals


    # create with no signals
