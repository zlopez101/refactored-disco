import os
import numpy as np
import requests
import pandas as pd
from ta.trend import macd
import alpaca_trade_api as trade_api
from datetime import datetime
from utils import credentialing, business_day, targets, create_dict


class AlpacaStreamer:
    def __init__(self, paper=True):
        url, key, secret = credentialing(paper=paper)

        self.url = url
        self.key = key
        self.secret = secret
        self.api = trade_api.REST(
            key_id=self.key, secret_key=self.secret, base_url=self.url
        )
        self.conn = trade_api.StreamConn(
            key_id=self.key,
            secret_key=self.secret,
            base_url=self.url,
            data_stream="polygon",
        )
        start, end = business_day()
        self.trading_start = start
        self.trading_end = end
        self.open_orders = {}
        self.positions = {}
        self.partial_fills = {}
        self.stop_prices = {}
        self.target_prices = {}
        self.connect_retries = 0

    def define_universe(self, min_price=1, max_price=10, min_dv=100000, quick=False):
        assets = self.api.list_assets(status="active", asset_class="us_equity")
        symbols = [
            asset.symbol
            for asset in assets
            if asset.tradable
            and asset.exchange == "NYSE"
            and asset.status == "active"
            and asset.shortable
        ]
        dct = {}
        if quick:
            symbols = symbols[:10]
        for symbol in symbols:
            try:
                data = self.api.polygon.daily_open_close(symbol, "2020-07-13")
                if (
                    data.close >= min_price
                    and data.close <= max_price
                    and data.volume * data.close > min_dv
                ):
                    dct[symbol] = data
            except requests.exceptions.HTTPError:
                print(f"Symbol {symbol} gave an error, excluding from universe.")
        self.symbols = list(dct.keys())
        print(f"collected {len(self.symbols)} symbols.")
        self.channels = [f"AM.{symbol}" for symbol in self.symbols]
        self.channels.append("trade_updates")

    # def create_data_aggregator(
    #     self, symbols, data_to_capture=["open", "high", "low", "close", "volume"]
    # ):
    #     """
    #     Creates that table that holds the minute aggregation data for the day
    #     """
    #     self.master_dct = {}
    #     for symbol in symbols:
    #         idx = pd.date_range(self.trading_start, self.trading_end, freq="T")
    #         df = pd.DataFrame(columns=data_to_capture, index=idx)
    #         self.master_dct[symbol] = df

    def buy_criteria(self, indicator, **kwargs):
        # if the macd is positive
        if indicator[-1] > 0:
            return True
        else:
            return False

    def buy(self, symbol, amount, limit_price):
        return self.api.submit_order(
            symbol,
            amount,
            side="buy",
            type="limit",
            time_in_force="day",
            limit_price=str(limit_price),
        )

    def sell(self, symbol, amount, limit_price):
        return self.api.submit_order(
            symbol,
            amount,
            side="side",
            type="limit",
            time_in_force="day",
            limit_price=str(limit_price),
        )

    def data_collection(self, data):
        now = datetime.strptime(
            datetime.now().strftime("%y-%m-%d %H:%M"), "%y-%m-%d %H:%M"
        )
        self.master_dct[data.symbol].loc[now] = {
            "open": data.open,
            "high": data.high,
            "low": data.low,
            "close": data.close,
            "volume": data.volume,
        }
        return now, data.symbol

    def run(self):
        if not self.symbols:
            return "Must define the universe first."

        self.master_dct = create_dict(self.symbols)

        @self.conn.on(r"^trade_updates$")
        async def handle_trade_update(conn, channel, data):
            symbol = data.order["symbol"]
            last_order = self.open_orders.get(symbol)
            if last_order is not None:
                event = data.event
                if event == "partial_fill":
                    qty = int(data.order["filled_qty"])
                    if data.order["side"] == "sell":
                        qty = qty * -1
                    self.positions[symbol] = self.positions.get(
                        symbol, 0
                    ) - self.partial_fills.get(symbol, 0)
                    self.partial_fills[symbol] = qty
                    self.positions[symbol] += qty
                    self.open_orders[symbol] = data.order
                    print(f"partial fill of {symbol}")
                elif event == "fill":
                    qty = int(data.order["filled_qty"])
                    if data.order["side"] == "sell":
                        qty = qty * -1
                    self.positions[symbol] = self.positions.get(
                        symbol, 0
                    ) - self.partial_fills.get(symbol, 0)
                    self.partial_fills[symbol] = 0
                    self.positions[symbol] += qty
                    self.open_orders[symbol] = None
                    print(f"fill of {symbol}")
                elif event == "canceled" or event == "rejected":
                    self.partial_fills[symbol] = 0
                    self.open_orders[symbol] = None
                    print(f"{symbol} cancelled or rejected.")

        @self.conn.on(r"^AM$")
        async def on_minute_bars(conn, channel, data):
            now, symbol = self.data_collection(data)
            closes = self.master_dct[symbol].close[:now]
            hist = macd(closes)
            if self.buy_criteria(hist):
                print(
                    "Submitting buy for {} shares of {} at {}".format(
                        1, data.symbol, data.close
                    )
                )
                try:
                    buy = self.buy(symbol, 1)
                    self.open_orders[symbol] = buy
                    self.target_prices[symbol], self.stop_prices[symbol] = targets(
                        data.close
                    )
                    print(f"bought 1 share of {symbol}")
                except Exception as e:
                    print(e)
                    print(f"buy order for {symbol} not processed...")

            position = self.positions.get(symbol, False)
            if position:
                if (
                    data.close <= self.stop_prices[symbol]
                    or data.close >= self.target_prices[symbol]
                ):
                    print(
                        f"Submitting sell order for {position} shares of {data.symbol} at {data.close}"
                    )
                    try:
                        sell = self.sell(symbol, position, data.close)
                        self.open_orders[symbol] = sell
                    except Exception as e:
                        print(e)

        def run_ws(conn, channels):
            try:
                conn.run(channels)
            except Exception as e:
                print(e)
                if self.connect_retries < 100:
                    run_ws(conn, channels)
                else:
                    print("connection timed out more than 100 times")

        run_ws(self.conn, self.channels)

