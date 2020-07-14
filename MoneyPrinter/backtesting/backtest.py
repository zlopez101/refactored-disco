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


class Macd(bt.Strategy):

    params = dict(first_fast=12, first_slow=26, second_fast=40, second_slow=60)

    def __init__(self):
        self.macd1 = bt.ind.MACD(
            me1_period=self.p.first_fast, me2_period=self.p.first_slow
        )
        self.macd2 = bt.ind.MACD(
            me1_period=self.p.first_fast, me2_period=self.p.first_slow
        )

        # self.crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add()

    def next(self):
        if not self.position:
            if self.macd1 > 0 and self.macd2 > 0:
                self.buy()
        elif self.position:
            if 
        elif self.crossover < 0:
            self.close()

if __name__=='__main__':
    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(100000)
    print(f"Starting portfolio value: {cerebro.broker.getvalue()}")
    data = bt.feeds.PandasData(dataname=tsla)
    cerebro.adddata(data)
    cerebro.addstrategy(Macd)
    cerebro.run()
    print(f"Starting portfolio value: {cerebro.broker.getvalue()}")
    cerebro.plot()

