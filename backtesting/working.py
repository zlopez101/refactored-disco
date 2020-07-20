import backtrader as bt
from btutils import get_data
import matplotlib.pyplot as plt
from strategies import Zach

data = get_data("TSLA")
btready_data = bt.feeds.PandasData(dataname=data)

cerebro = bt.Cerebro()
cerebro.broker.set_cash(100000)
cerebro.adddata(btready_data)
cerebro.addstrategy(Zach, ma_fast=10, ma_slow=39, rsi_period=9, rsi_high=62)
cerebro.run()
print(cerebro.broker.getvalue())
cerebro.plot()


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
