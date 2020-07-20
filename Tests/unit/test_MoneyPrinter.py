import pytest

# import numpy as np
from MoneyPrinter.utils import get_tiingo_eod, create_dict, business_day


def test_master_dictionary_creation(sample_symbols):
    """
    test that the dictionary is set up properly
    """
    _, _, _, tickers = sample_symbols
    master_dct = create_dict(tickers)


def test_get_tickers(sample_symbols):
    """ 
    get_tickers should screen stocks for previous day values
    values will be picked at random, then checked for previous business day
    """
    min_share, max_share, min_volume, tickers = sample_symbols
    results = get_tiingo_eod(tickers)
    for key, value in results.items():
        assert (
            value["close"] > min_share
        ), f"{key} did not meet the criteria for a close higher than ${min_share}."
        assert (
            value["close"] < max_share
        ), f"{key} did not meet the criteria for a close lower that ${max_share}"
        assert (
            value["volume"] > min_volume
        ), f"{key} did not meet the criteria volume traded of {min_volume} shares."


def test_cancel_orders(api_setup):
    pass


def test_add_data_to_master_dct(sample_symbols):
    pass
    # import pandas as pd
    # from numpy import random.choice as choice
    # start, _ = business_day()
    #     _, _, _, tickers = sample_symbols
    # master_dct = create_dict(tickers)
    # idx = pd.date_range(start, periods=1, freq="T")
    # ticker = choice(tickers)
    # master_dct[ticker].loc


def test_buy_logic():
    pass
