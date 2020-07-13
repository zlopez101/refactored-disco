import os
from datetime import datetime
import pandas as pd
import backtrader as bt
import matplotlib.pyplot as plt
import alpaca_trade_api as tradeapi
from MoneyPrinter.utils import credentialing

url, key, secret = credentialing()
api = tradeapi.REST(key, secret, url)

tsla = api.get_barset(
    "TSLA", "day", start=datetime(2017, 1, 1), end=datetime(2020, 1, 1)
).df
tsla.columns = tsla.columns.levels[1]


class SmaCross(bt.Strategy):

    params = dict(fast=5, slow=30)

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.fast)
        sma2 = bt.ind.SMA(period=self.p.slow)

        self.crossover = bt.ind.CrossOver(sma1, sma2)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        elif self.crossover < 0:
            self.close()


cerebro = bt.Cerebro()
data = bt.feeds.PandasData(dataname=tsla)
cerebro.adddata(data)
cerebro.addstrategy(SmaCross)
cerebro.run()
cerebro.plot()

