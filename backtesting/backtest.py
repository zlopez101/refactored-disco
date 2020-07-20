import backtrader as bt
import matplotlib.pyplot as plt
from btutils import get_data, get_best_parameters, get_ranges
from itertools import product
from strategies import Zach
from tqdm import tqdm
import argparse
import logging

logging.basicConfig(
    filename="BackTesting.log",
    level=logging.INFO,
    format="%(levelname)s:%(asctime)s:%(message)s",
)


def run(dct):
    results = []
    data = get_data(dct["Symbol"])
    btready_data = bt.feeds.PandasData(dataname=data)
    symbol = dct.pop("Symbol")
    iterators = list(dct.keys())
    ls = get_ranges(dct, [])
    output_list = list(product(*ls))
    for values in tqdm(output_list):
        cerebro = bt.Cerebro()
        cerebro.broker.set_cash(100000)
        cerebro.adddata(btready_data)
        cerebro.addstrategy(
            Zach,
            ma_slow=values[0],
            ma_fast=values[1],
            rsi_period=values[2],
            rsi_high=values[3],
            rsi_low=values[4],
            macd_filter=values[5],
        )
        cerebro.run()
        end = cerebro.broker.getvalue()
        results.append((values, end))

    best_parameters = results[get_best_parameters(results)][:-1]
    best_parameters = zip(iterators, *best_parameters)
    logging.info(
        f"{list(best_parameters)} for {symbol} data with a length of {len(data)}."
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Welcome to the Backtrading Integration.")
    parser.add_argument(
        "Symbol",
        type=str,
        help="Choose a single symbol or a random one will be selected",
    )
    ma = parser.add_argument_group("Smooth Moving Average parameters ")
    rsi = parser.add_argument_group("RSI parameters ")
    macd = parser.add_argument_group("MACD parameters")

    ma.add_argument(
        "-ma_slow",
        nargs=2,
        type=int,
        help="input two periods seperated by only 1 space. Final Value not inclusive",
        default=(0, 1),
    )
    ma.add_argument(
        "-ma_fast",
        nargs=2,
        type=int,
        help="input two periods seperated by only 1 space. Final Value not inclusive",
        default=(0, 1),
    )
    rsi.add_argument(
        "-RSI_period", type=int, nargs=2, help="RSI period range", default=(0, 1)
    )
    rsi.add_argument(
        "-RSI_high", type=int, nargs=2, help="RSI High filter range", default=(0, 1),
    )
    rsi.add_argument(
        "-RSI_low", type=int, nargs=2, help="RSI low filter range", default=(0, 1)
    )

    macd.add_argument("-MACD_filter", type=int, nargs=2, help="", default=(0, 1))
    args = parser.parse_args()
    logging.info(vars(args))
    run(vars(args))

