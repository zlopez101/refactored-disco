import logging
from utils import credentialing
import alpaca_trade_api as trade_api
import pandas as pd
from datetime import datetime, timedelta


def create_api():
    url, key, secret = credentialing()
    api = trade_api.REST(key_id=key, secret_key=secret, base_url=url)
    return api


api = create_api()
# logging.basicConfig(filename="example.log", level=logging.DEBUG)
# logging.debug("This message should go to the log file")
# logging.info("So should this")
# logging.warning("And this, too")
# api.submit_order(symbol="TSLA", qty=1, side="buy", type="market", time_in_force="gtc")
# current_time = api.get_clock().timestamp
# print(type(current_time))


# api.submit_order(
#     symbol="TSLA",
#     qty=1,
#     side="buy",
#     type="limit",
#     time_in_force="day",
#     limit_price=str(1000),
# )


def cancel_old_orders(api, orders, symbol, tz, order_expiration=2):
    """
    Cancels orders that exceed order_expiration in minutes
    : param api: Alpaca REST endpoint
    : dict orders: a dictionary with symbols for keys and orders for values
    : str symbol: a string with the symbol for the stock
    : int order_expiration: int for minutes to leave orders open 
    """
    current_time = pd.Timestamp(datetime.now().astimezone(tz))
    order_for_symbol = orders.get(symbol, None)
    if (
        (order_for_symbol.status == "held" or order_for_symbol.status == "new")
        and order_for_symbol.submitted_at + timedelta(minutes=order_expiration)
        > current_time
    ):
        try:
            api.cancel_order(order_for_symbol.id)
        except Exception as e:
            print(e)
