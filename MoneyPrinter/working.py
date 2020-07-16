from utils import credentialing
import alpaca_trade_api as trade_api


def create_order(symbol):
    url, key, secret = credentialing()
    api = trade_api.REST(key_id=key, secret_key=secret, base_url=url)
    order = api.submit_order(
        symbol=symbol,
        qty=str(1),
        side="buy",
        type="market",
        time_in_force="day",
        # order_class="bracket",
        # take_profit=dict(limit_price="1510.00"),
        # stop_loss=dict(stop_price="1506.00", limit_price="1506.00"),
    )
    return order

