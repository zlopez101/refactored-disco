import os
from datetime import datetime

import alpaca_trade_api
import numpy as np
import pandas as pd


class BaseTrader:
    def __init__(self):

        # set up connections to Alpaca
        self.base_url = "https://paper-api.alpaca.markets"
        self.api_key = os.environ.get("ALPACA_API_KEY")
        self.api_secret = os.environ.get("ALPACA_API_SECRET")
        self.api = alpaca_trade_api.REST(self.api_key, self.api_secret, self.base_url)

        # define starting conditions
        account_info = self.api.get_account()
        self.equity = float(account_info.equity)
        self.margin_multiplier = float(account_info.multiplier)
        self.universe = {}

    def create_universe(self, min_price=1, max_price=10, min_dollar_vol=100000):
        """
        create the universe of stocks the trader is allowed to manipulate
        """
        assets = self.api.list_assets(status="active", asset_class="us_equity")
        tickers = [
            ticker.ticker
            for ticker in assets
            if (
                ticker.lastTrade["p"] >= min_s_price
                and ticker.lastTrade["p"] <= max_price
                and ticker.prevDay["v"] * ticker.lastTrade["p"] > min_dollar_vol
            )
        ]
        for tick in ticker:
            self.universe[tick] = {}


class Cross(BaseTrader):
    def _init__(self, fast, slow):
        super().__init__()
        self.fast_ma = int(fast)
        self.slow_ma = int(slow)


m = MacdCross(2, 20)
print(m.equity)
