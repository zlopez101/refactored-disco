import websocket, json
import asyncio
from datetime import datetime
import pandas as pd
from utils import credentialing, get_tickers, targets
import alpaca_trade_api as trade_api
from ta.trend import sma, macd


def run(min_share_price=1, max_share_price=10, min_dv=1000000, quick=False):
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
        print("added some data!")

        # if the macd is above one, make a purchase of 1 share
        closes = master_dct[data.symbol].close[:now]
        hist = macd(closes)
        order_history = {}
        if True:
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
                )
                open_orders[data.symbol] = buy
                target_prices[data.symbol], stop_prices[data.symbol] = targets(
                    data.close
                )
                print(f"bought 1 share of {data.symbol}")
            except Exception as e:
                print(e)
                print(f"buy order for {data.symbol} not processed...")

            position = positions.get(data.symbol, False)
            if position:
                if (
                    data.close <= stop_prices[data.symbol]
                    or data.close >= target_prices[data.symbol]
                ):
                    print(
                        f"Submitting sell order for 1 share of {data.symbol} at {data.close}"
                    )
                    try:
                        sell = api.submit_order(
                            symbol=symbol,
                            qty=str(position),
                            side="sell",
                            type="limit",
                            time_in_force="day",
                            limit_price=str(data.close),
                        )
                        open_orders[symbol] = sell
                    except Exception as e:
                        print(e)

    channels_to_listen = [f"AM.{symbol}" for symbol in symbols_to_watch]
    channels_to_listen.insert(0, "trade_updates")

    conn.run(channels_to_listen)

    # def run_ws(conn, channels):
    #     try:
    #         print(f"listening...")
    #         conn.run(channels)
    #     except Exception as e:
    #         print(e)
    #         if e == asyncio.exceptions.CancelledError:
    #             run_ws(conn, channels)
    #         run_ws(conn, channels)

    # run_ws(conn, channels_to_listen)


if __name__ == "__main__":
    run()
