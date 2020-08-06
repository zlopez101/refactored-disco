import os
from tqdm import tqdm
from datetime import datetime
import alpaca_trade_api as tradeapi
from db_utils import *
from db_classes import Stock
import time


def make_database(start):
    symbols = get_assets()
    for symbol in tqdm(symbols):
        time.sleep(3)
        sym = Stock(symbol)
        os.makedirs(sym.industry, exist_ok=True)
        # os.chdir(os.path.join(os.getcwd(), sym.industry))
        _, data = lots_of_data(start, sym.ticker)
        data.to_csv(f"{sym.industry}/{sym.ticker}.csv")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-year", type=int, default=2015)
    parser.add_argument("-month", type=int, default=1)
    parser.add_argument("-day", type=int, default=1)
    date = vars(parser.parse_args())
    make_database(datetime(data["year"], date["month"], date["day"]))
