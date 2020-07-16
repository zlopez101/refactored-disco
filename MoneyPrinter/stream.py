import websocket, json
import asyncio
import argparse
from datetime import datetime
import pandas as pd
from utils import credentialing, get_tickers, targets
import alpaca_trade_api as trade_api
from ta.trend import sma, macd


def run(min_share_price, max_share_price, min_dv, n_fast, n_slow, quick, n_retries):
    tries = 0
    url, key, secret = credentialing()
    conn = trade_api.StreamConn(
        base_url=url, key_id=key, secret_key=secret, data_stream="polygon"
    )
    api = trade_api.REST(base_url=url, key_id=key, secret_key=secret)

    def create_dict(symbols):
        """
        creates a master dictionary with each symbol pointing to a dataframe of data collected from the stream. 
        """
        dct = {}

        def create_dataframe():
            """
            Helper function to create a dataframe that is the value for each SYMBOL key in the dictionary
            """
            column_names = ["open", "high", "low", "close", "volume"]

            def get_trading_start():
                """
                Helper function gets the start of the trading day
                """
                today = datetime.today().date()
                start = datetime(today.year, today.month, today.day, hour=8, minute=30)
                return start

            idx = pd.date_range(get_trading_start(), periods=900, freq="T")
            df = pd.DataFrame(columns=column_names, index=idx)
            return df

        for symbol in symbols:
            dct[symbol] = create_dataframe()

        return dct

    symbols_to_watch = get_tickers(
        api, min_share_price, max_share_price, min_dv, quick=quick
    )
    master_dct = create_dict(symbols_to_watch)

    open_orders = {}
    partial_fills = {}
    positions = {}
    stop_prices = {}
    target_prices = {}

    @conn.on(r"^trade_updates$")
    async def handle_trade_update(conn, channel, data):
        symbol = data.order["symbol"]
        last_order = open_orders.get(symbol)
        if last_order is not None:
            event = data.event
            if event == "partial_fill":
                qty = int(data.order["filled_qty"])
                if data.order["side"] == "sell":
                    qty = qty * -1
                positions[symbol] = positions.get(symbol, 0) - partial_fills.get(
                    symbol, 0
                )
                partial_fills[symbol] = qty
                positions[symbol] += qty
                open_orders[symbol] = data.order
                print(f"partial fill of {symbol}")
            elif event == "fill":
                qty = int(data.order["filled_qty"])
                if data.order["side"] == "sell":
                    qty = qty * -1
                positions[symbol] = positions.get(symbol, 0) - partial_fills.get(
                    symbol, 0
                )
                partial_fills[symbol] = 0
                positions[symbol] += qty
                open_orders[symbol] = None
                print(f"fill of {symbol}")
            elif event == "canceled" or event == "rejected":
                partial_fills[symbol] = 0
                open_orders[symbol] = None
                print(f"{symbol} cancelled or rejected.")

    @conn.on(r"^AM$")
    async def on_minute_bars(conn, channel, data):
        now = datetime.strptime(
            datetime.now().strftime("%y-%m-%d %H:%M"), "%y-%m-%d %H:%M"
        )
        master_dct[data.symbol].loc[now] = {
            "open": data.open,
            "high": data.high,
            "low": data.low,
            "close": data.close,
            "volume": data.volume,
        }

        # if the macd is above one, make a purchase of 1 share
        closes = master_dct[data.symbol].close[:now]
        hist = macd(closes, n_fast=n_fast, n_slow=n_slow)
        order_history = {}
        # only buy if macd is positive and symbol not already bought
        if hist[-1] > 0 and not open_orders.get(symbol, None):
            print(
                "Submitting buy for {} shares of {} at {}".format(
                    1, data.symbol, data.close
                )
            )
            try:
                buy = api.submit_order(
                    symbol=data.symbol,
                    qty=1,
                    side="buy",
                    type="limit",
                    time_in_force="day",
                    limit_price=str(data.close),
                    order_class="bracket",
                    take_profit=dict(limit_price=f"{data.close * 1.02}"),
                    stop_loss=dict(
                        stop_price=f"{data.close * 0.99}",
                        limit_price=f"{data.close * 0.99}",
                    ),
                )
                open_orders[data.symbol] = buy
                print(f"Submitted order 1 share of {data.symbol}")
            except Exception as e:
                print(e)
                print(f"buy order for {data.symbol} not processed...")

            # position = positions.get(data.symbol, False)
            # if position:
            #     if (
            #         data.close <= stop_prices[data.symbol]
            #         or data.close >= target_prices[data.symbol]
            #     ):
            #         print(
            #             f"Submitting sell order for 1 share of {data.symbol} at {data.close}"
            #         )
            #         try:
            #             sell = api.submit_order(
            #                 symbol=symbol,
            #                 qty=str(position),
            #                 side="sell",
            #                 type="limit",
            #                 time_in_force="day",
            #                 limit_price=str(data.close),
            #             )
            #             open_orders[symbol] = sell
            #         except Exception as e:
            #             print(e)

    channels_to_listen = [f"AM.{symbol}" for symbol in symbols_to_watch]
    channels_to_listen.insert(0, "trade_updates")

    # conn.run(channels_to_listen)
    # sample change

    def run_ws(conn, channels):
        try:
            print(f"listening...")
            conn.run(channels)
        except Exception as e:
            print(e)
            tries += 1
            if tries <= n_retries:
                run_ws(conn, channels)
            print("ran out of retry options. better luck next time")

    run_ws(conn, channels_to_listen)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Stream Data from Alpaca and Trade based on Technical Indicators. Welcome to the new format!"
    )
    screening = parser.add_argument_group(title="Stock Screening Values")
    Moving_Average_Convergence_Divergence = parser.add_argument_group(
        title="MACD Values"
    )

    Moving_Average_Convergence_Divergence.add_argument(
        "-n_fast",
        type=int,
        help="fast period for the macd. Default 12 period",
        default=12,
    )
    Moving_Average_Convergence_Divergence.add_argument(
        "-n_slow",
        type=int,
        help="slow period for the macd. Default 26 period",
        default=26,
    )
    parser.add_argument(
        "-quick",
        type=bool,
        help="If you would like to quickly test functionality",
        default=False,
    )

    screening.add_argument(
        "-min_share_price",
        type=float,
        help="Minimum value of share price at yesterday's close. Default $1",
        default=1,
    )
    screening.add_argument(
        "-max_share_price",
        type=float,
        help="Maximum value of share price at yesterday's close. Default $10",
        default=10,
    )
    screening.add_argument(
        "-min_dv",
        type=float,
        help="Minimum  dollar volume of shares traded yesterday. Default $1,000,000",
        default=1000000,
    )
    parser.add_argument(
        "-n_retries",
        type=int,
        help="The number of times to try and reconnet. Default 100",
        default=100,
    )

    args = parser.parse_args()
    run(
        args.min_share_price,
        args.max_share_price,
        args.min_dv,
        args.n_fast,
        args.n_slow,
        args.quick,
        args.n_retries,
    )

