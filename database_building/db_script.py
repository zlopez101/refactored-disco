import alpaca_trade_api as trade_api
import sqlite3
from db_utils import *
from db_classes import Stock


def create_database(sql_statement):
    conn = sqlite3.connect("stock_data.db")
    c = conn.cursor()
    c.execute(sql_statement)
    conn.commit()
    conn.close()


def delete_table(table):
    conn = sqlite3.connect("stock_data.db")
    c = conn.cursor()
    c.execute("DROP TABLE " + table)
    conn.commit()
    conn.close()


def insert_data(table):
    conn = sqlite3.connect("stock_data.db")
    c = conn.cursor()
    c.execute("DROP TABLE " + table)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database(
        """CREATE TABLE stocks (
    ticker text,
    industry text,
    industry_sic integer
    events integer
    best_percent_gain real
    file text
    )"""
    )

