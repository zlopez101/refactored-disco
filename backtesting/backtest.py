import os
from datetime import datetime
import pandas as pd
import numpy as np
import backtrader as bt
import matplotlib.pyplot as plt
import alpaca_trade_api as tradeapi
from btutils import credentialing, business_day


url, key, secret = credentialing()
api = tradeapi.REST(key, secret, url)
start, end = business_day()


def get_data(symbol):
    df = api.polygon.historic_agg_v2(
        symbol,
        1,
        "minute",
        _from=pd.Timestamp(start).isoformat(),
        to=pd.Timestamp(end).isoformat(),
    ).df
    df = df[np.logical_and(df.index >= start, df.index <= end)]
    return df


data = get_data("TSLA")
print(data)


class Macd(bt.Strategy):
    """
    params = dict(first_fast=12, first_slow=26, second_fast=40, second_slow=60)
    """

    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=30,  # period for the slow moving average
    )

    def __init__(self):
        """
        self.macd1 = bt.ind.MACD(
            period_me1=self.p.first_fast, period_me2=self.p.first_slow
        )
        self.macd2 = bt.ind.MACD(
            period_me1=self.p.first_fast, period_me2=self.p.first_slow
        )

        self.crossover = bt.ind.CrossOver(sma1, sma2)
        """

        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal

    def next(self):
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.buy()  # enter long
        elif self.crossover < 0:  # in the market & cross to the downside
            self.close()  # close long position


"""
    def next(self):
        if not self.position:
            if self.macd1 > 0 and self.macd2 > 0:
                self.buy()"""


if __name__ == "__main__":
    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(100000)
    print(f"Starting portfolio value: {cerebro.broker.getvalue()}")
    data = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data)
    cerebro.addstrategy(Macd)
    cerebro.run()
    print(f"Starting portfolio value: {cerebro.broker.getvalue()}")
    cerebro.plot()

