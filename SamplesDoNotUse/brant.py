import os
import asyncio
import alpaca_trade_api as tradeapi
import requests
import time
from ta.trend import MACD
from ta.momentum import rsi
import numpy as np
from datetime import datetime, timedelta
from pytz import timezone

# Replace these with your API connection info from the dashboard
base_url = "https://paper-api.alpaca.markets"
api_key_id = os.environ.get("ALPACA_API_KEY")
api_secret = os.environ.get("ALPACA_API_SECRET")

api = tradeapi.REST(base_url=base_url, key_id=api_key_id, secret_key=api_secret)

session = requests.session()

# We only consider stocks with per-share prices inside this range
min_share_price = 1.0
max_share_price = 10
# Minimum previous-day dollar volume for a stock we might consider
min_last_dv = 1000000
# Stop limit to default to
default_stop = 0.95
# How much of our portfolio to allocate to any one position
risk = 0.10


def get_1000m_history_data(symbols):
    """
    returns a dictionary with the ticker as the key and the last 1000 minutes as the history

    :param Symbols: a list of symbols
    """
    print("Getting historical data...")
    minute_history = {}
    c = 0
    _from = datetime.today() - timedelta(days=4)
    _to = datetime.now()
    for symbol in symbols:
        minute_history[symbol] = api.polygon.historic_agg_v2(
            symbol,
            1,
            "minute",
            _from=_from.strftime("%Y-%m-%d"),
            to=_to.strftime("%Y-%m-%d"),
            limit=1000,
        ).df
        c += 1
        print("{}/{}".format(c, len(symbols)))
    print("Success.")
    return minute_history


def get_tickers():
    """
    get all tickers that meet the criteria of min_share_price, max_share_price, min_last_dv, todaysChangePerc
    """
    print("Getting current ticker data...")
    # tickers = api.polygon.all_tickers()

    assets = api.list_assets(status="active", asset_class="us_equity")
    symbols = [
        asset.symbol
        for asset in assets
        if asset.tradable
        and asset.exchange == "NYSE"
        and asset.status == "active"
        and asset.shortable
    ]
    dct = {}
    for symbol in symbols:
        try:
            data = api.polygon.daily_open_close(symbol, "2020-07-13")
            if (
                data.close >= min_share_price
                and data.close <= max_share_price
                and data.volume * data.close > min_last_dv
            ):
                dct[symbol] = api.polygon.daily_open_close(symbol, "2020-07-13")
        except requests.exceptions.HTTPError:
            print(f"Symbol {symbol} gave an error, excluding from universe.")
    # print(f"Including {len(data.keys())} stocks for trading today.")
    return dct


def find_stop(current_value, minute_history, now):
    """
    returns the stop value for the 
    """
    # get the lowest low every 5 minutes for the last 100 transactions prices resampled to 5 minutes
    series = minute_history["low"][-100:].dropna().resample("5min").min()
    # confirm that these are the prices for today, and not reaching back to yesterday
    series = series[now.floor("1D") :]
    # get the differences in prices
    diff = np.diff(series.values)
    # get the indexes of troughes (when prices stop decreasing, start increasing )
    low_index = np.where((diff[:-1] <= 0) & (diff[1:] > 0))[0] + 1
    # if there are any
    if len(low_index) > 0:
        # return the price at the last trough minues 1 cent?
        return series[low_index[-1]] - 0.01
    return current_value * default_stop


def run(tickers, market_open_dt, market_close_dt):
    # Establish streaming connection
    conn = tradeapi.StreamConn(
        base_url=base_url,
        key_id=api_key_id,
        secret_key=api_secret,
        data_stream="polygon",
    )

    # Update initial state with information from tickers

    volume_today = {}
    prev_closes = {}
    for ticker in tickers.keys():
        prev_closes[ticker] = tickers[ticker].close
        volume_today[ticker] = 0

    symbols = tickers.keys()
    print("Tracking {} symbols.".format(len(symbols)))
    minute_history = get_1000m_history_data(symbols)

    portfolio_value = float(api.get_account().portfolio_value)
    print(f"Starting with {portfolio_value} in the bank.")

    open_orders = {}
    positions = {}

    # Cancel any existing open orders on watched symbols
    existing_orders = api.list_orders(limit=500)
    for order in existing_orders:
        if order.symbol in symbols:
            api.cancel_order(order.id)

    stop_prices = {}
    # needed for previous buying positions
    latest_cost_basis = {}

    # Track any positions bought during previous executions
    existing_positions = api.list_positions()
    for position in existing_positions:
        if position.symbol in symbols:
            positions[position.symbol] = float(position.qty)
            # Recalculate cost basis and stop price
            latest_cost_basis[position.symbol] = float(position.cost_basis)
            stop_prices[position.symbol] = float(position.cost_basis) * default_stop

    # Keep track of what we're buying/selling
    target_prices = {}
    partial_fills = {}

    # Use trade updates to keep track of our portfolio
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

    # Replace aggregated 1s bars with incoming 1m bars
    @conn.on(r"^AM$")
    async def handle_minute_bar(conn, channel, data):
        print("got some data")
        ts = data.start
        ts -= timedelta(microseconds=ts.microsecond)
        minute_history[data.symbol].loc[ts] = [
            data.open,
            data.high,
            data.low,
            data.close,
            data.volume,
        ]
        volume_today[data.symbol] += data.volume

        # Next, check for existing orders for the stock
        existing_order = open_orders.get(symbol)
        if existing_order is not None:
            # Make sure the order's not too old
            submission_ts = existing_order.submitted_at.astimezone(
                timezone("America/New_York")
            )
            order_lifetime = ts - submission_ts
            if order_lifetime.seconds // 60 > 1:
                # Cancel it so we can try again for a fill
                api.cancel_order(existing_order.id)
            return

        # Now we check to see if it might be time to buy or sell
        since_market_open = ts - market_open_dt
        until_market_close = market_close_dt - ts
        if (
            since_market_open.seconds // 60 > 15
            and since_market_open.seconds // 60 < 60
        ):
            # Check for buy signals

            # See if we've already bought in first
            position = positions.get(symbol, 0)
            if position > 0:
                return

            # See how high the price went during the first 15 minutes
            lbound = market_open_dt
            ubound = lbound + timedelta(minutes=15)
            high_15m = 0
            try:
                high_15m = minute_history[symbol][lbound:ubound]["high"].max()
            except Exception as e:
                # Because we're aggregating on the fly, sometimes the datetime
                # index can get messy until it's healed by the minute bars
                return

            # Get the change since yesterday's market close
            daily_pct_change = (data.close - prev_closes[symbol]) / prev_closes[symbol]
            if (
                daily_pct_change > 0.02
                and data.close > high_15m
                and volume_today[symbol] > 3000
            ):
                # check for a positive, increasing MACD
                hist = MACD(
                    minute_history[symbol]["close"].dropna(), n_fast=12, n_slow=26
                )
                if hist[-1] < 0 or not (hist[-3] < hist[-2] < hist[-1]):
                    return
                hist = MACD(
                    minute_history[symbol]["close"].dropna(), n_fast=40, n_slow=60
                )
                if hist[-1] < 0 or np.diff(hist)[-1] < 0:
                    return

                # # personal
                # r = rsi(minute_history[symbol]["close"].dropna())
                # if r[-1] > 50:
                #     return

                # Stock has passed all checks; figure out how much to buy
                stop_price = data.close * 0.99
                stop_prices[symbol] = stop_price
                target_prices[symbol] = data.close * 1.02
                shares_to_buy = portfolio_value * risk // (data.close - stop_price)
                if shares_to_buy == 0:
                    shares_to_buy = 1
                shares_to_buy -= positions.get(symbol, 0)
                if shares_to_buy <= 0:
                    return

                print(
                    "Submitting buy for {} shares of {} at {}".format(
                        shares_to_buy, symbol, data.close
                    )
                )
                try:
                    o = api.submit_order(
                        symbol=symbol,
                        qty=str(shares_to_buy),
                        side="buy",
                        type="limit",
                        time_in_force="day",
                        limit_price=str(data.close),
                    )
                    open_orders[symbol] = o
                    latest_cost_basis[symbol] = data.close
                except Exception as e:
                    print(e)
                return
        if (
            since_market_open.seconds // 60 >= 24
            and until_market_close.seconds // 60 > 15
        ):
            # Check for liquidation signals

            # We can't liquidate if there's no position
            position = positions.get(symbol, 0)
            if position == 0:
                return

            # Sell for a loss if it's fallen below our stop price
            # Sell for a loss if it's below our cost basis and MACD < 0
            # Sell for a profit if it's above our target price
            hist = MACD(minute_history[symbol]["close"].dropna(), n_fast=13, n_slow=21)
            if (
                data.close <= stop_prices[symbol]
                or data.close >= target_prices[symbol]  # and hist[-1] <= 0)
                # or (data.close <= latest_cost_basis[symbol] and hist[-1] <= 0)
            ):
                print(
                    "Submitting sell for {} shares of {} at {}".format(
                        position, symbol, data.close
                    )
                )
                try:
                    o = api.submit_order(
                        symbol=symbol,
                        qty=str(position),
                        side="sell",
                        type="limit",
                        time_in_force="day",
                        limit_price=str(data.close),
                    )
                    open_orders[symbol] = o
                    latest_cost_basis[symbol] = data.close
                except Exception as e:
                    print(e)
            return
        elif until_market_close.seconds // 60 <= 15:
            # Liquidate remaining positions on watched symbols at market
            try:
                position = api.get_position(symbol)
            except Exception as e:
                # Exception here indicates that we have no position
                return
            print("Trading over, liquidating remaining position in {}".format(symbol))
            api.submit_order(
                symbol=symbol,
                qty=position.qty,
                side="sell",
                type="market",
                time_in_force="day",
            )
            symbols.remove(symbol)
            if len(symbols) <= 0:
                conn.close()
            conn.deregister(["AM.{}".format(symbol)])

        print("still listening...")

    channels = ["trade_updates"]
    for symbol in symbols:
        symbol_channels = ["AM.{}".format(symbol)]
        channels += symbol_channels
    print("Watching {} symbols.".format(len(symbols)))
    run_ws(conn, channels)


# Handle failed websocket connections by reconnecting
def run_ws(conn, channels):
    try:
        conn.run(channels)
    except Exception as e:
        print(e)
        if e == asyncio.exceptions.CancelledError:
            run_ws(conn, channels)
        conn.close()
        run_ws(conn, channels)


if __name__ == "__main__":
    # Get when the market opens or opened today
    nyc = timezone("America/New_York")
    today = datetime.today().astimezone(nyc)
    today_str = datetime.today().astimezone(nyc).strftime("%Y-%m-%d")
    calendar = api.get_calendar(start=today_str, end=today_str)[0]
    market_open = today.replace(
        hour=calendar.open.hour, minute=calendar.open.minute, second=0
    )
    market_open = market_open.astimezone(nyc)
    market_close = today.replace(
        hour=calendar.close.hour, minute=calendar.close.minute, second=0
    )
    market_close = market_close.astimezone(nyc)

    # Wait until just before we might want to trade
    current_dt = datetime.today().astimezone(nyc)
    since_market_open = current_dt - market_open
    """
    while since_market_open.seconds // 60 <= 14:
        time.sleep(1)
        since_market_open = current_dt - market_open
    """
    run(get_tickers(), market_open, market_close)
