# import backtrader as bt
# from btutils import get_data
# import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# from strategies import Zach

# data = get_data("TSLA")
# btready_data = bt.feeds.PandasData(dataname=data)

# cerebro = bt.Cerebro()
# cerebro.broker.set_cash(100000)
# cerebro.addobserver(bt.observers.BuySell)
# cerebro.addwriter(bt.WriterFile, out="working.log")
# cerebro.adddata(btready_data)
# cerebro.addstrategy(Zach, ma_fast=10, ma_slow=39, rsi_period=9, rsi_high=62)
# cerebro.run()
# print(cerebro.broker.getvalue())


# def get_ranges(dct, ls):
#     keys = list(dct.keys())
#     if len(keys) == 0:
#         return ls
#     else:
#         ls.append(range(dct.pop(keys[0])))
#         return get_ranges(dct, ls)


# a = {"a": 100, "b": 200, "c": 300}
# b = []
# print(get_ranges(a, b))

df = pd.DataFrame(range(100), index=pd.date_range("1/1/2020", periods=100))
# rolling = df.rolling(window=2).sum()
# print(rolling)

for i in range(10):
    flag = False
    generator = df.iterrows()
    while not (flag):
        index, row = next(generator)
        print(index)
        flag = np.random.choice([False, False, False, True])
