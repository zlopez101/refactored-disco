from utils import credentialing
import alpaca_trade_api as trade_api


url, key, secret = credentialing()

api = trade_api.REST(key_id=key, secret_key=secret, base_url=url)

api.submit_order(
    symbol="TSLA",
    qty=str(1),
    side="buy",
    type="market",
    time_in_force="day",
    order_class="bracket",
    take_profit=dict(limit_price="1530.00"),
    stop_loss=dict(stop_price="1520.00", limit_price="1520.00"),
)
