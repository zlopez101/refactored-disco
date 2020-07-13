import os
import numpy as np
import pandas as pd
import alpaca_trade_api as trade_api
from datetime import datetime

conn = trade_api.StreamConn(
    base_url=os.environ.get("rALPACA_ENDPOINT"),
    key_id=os.environ.get("rALPACA_API_KEY"),
    secret_key=os.environ.get("rALPACA_API_SECRET"),
)


@conn.on(r"^trade_updates$")
async def on_account_updaes(conn, channel, data):
    print("account", account)
p'l
@conn.on(r"^AM$")
async def on_minute_bars(conn, channel, data):
    print("bars", bar)


conn.run(["trade_updates", "AM.*"])

