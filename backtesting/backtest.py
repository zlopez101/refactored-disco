import backtrader as bt
import matplotlib.pyplot as plt
from btutils import get_data, get_best_parameters

from strategies import ZachSMA
import argparse


def run(dct):
    results = []
    data = get_data(dct["Symbol"])
    btready_data = bt.feeds.PandasData(dataname=data)
    dct.pop("Symbol")
    iterators = dct.keys()
    # print(len(iterators))
    # for i in range(len(iterators):

    for i in range(dct["ma_fast"][0], dct["ma_fast"][1] + 1):
        for j in range(dct["ma_slow"][0], dct["ma_slow"][1] + 1):
            cerebro = bt.Cerebro()
            cerebro.broker.set_cash(100000)
            cerebro.adddata(btready_data)
            cerebro.addstrategy(ZachSMA, pfast=i, pslow=j)
            cerebro.run()
            end = cerebro.broker.getvalue()
            results.append((i, j, end))
    best_parameters = results[get_best_parameters(results)][:-1]
    best_parameters = zip(iterators, best_parameters)
    print(*best_parameters)


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Welcome to the Backtrading Integration.")
    parser.add_argument(
        "Symbol",
        type=str,
        help="Choose a single symbol or a random one will be selected",
    )
    ma = parser.add_argument_group("Smooth Moving Average parameters ")
    rsi = parser.add_argument_group("RSI parameters ")
    so = parser.add_argument_group("Stochastic Oscillator parameters")

    ma.add_argument(
        "-ma_slow",
        nargs=2,
        type=int,
        default=[26, 40],
        help="input two periods seperated by only 1 space",
    )
    ma.add_argument(
        "-ma_fast",
        nargs=2,
        type=int,
        default=[8, 20],
        help="input two periods seperated by only 1 space",
    )

    args = parser.parse_args()
    run(vars(args))

