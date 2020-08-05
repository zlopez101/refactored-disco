import alpaca_trade_api as trade_api
import sqlite3
from db_utils import *
from db_classes import Stock


conn = sqlite3.connect("stock_data.db")
c = conn.cursor()

c.execute(
    # """CREATE TABLE stocks (
    # ticker text,
    # industry text,
    # industry_sic integer
    # events integer
    # best_percent_gain real
    # file text
    # )"""
)


conn.commit()
conn.close()
