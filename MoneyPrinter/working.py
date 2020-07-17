import logging
from utils import credentialing
import alpaca_trade_api as trade_api

url, key, secret = credentialing()
api = trade_api.REST(key_id=key, secret_key=secret, base_url=url)

# logging.basicConfig(filename="example.log", level=logging.DEBUG)
# logging.debug("This message should go to the log file")
# logging.info("So should this")
# logging.warning("And this, too")
# api.submit_order(symbol="TSLA", qty=1, side="buy", type="market", time_in_force="gtc")
current_time = api.get_clock().timestamp
print(type(current_time))
