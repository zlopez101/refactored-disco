import os
import pandas as pd
from ta.momentum import rsi
import alpaca_trade_api as tradeapi
import requests
from datetime import datetime, timedelta
from utils import credentialing
import time
import websocket

base_url = os.environ.get("rALPACA_ENDPOINT")
api_key_id = os.environ.get("rALPACA_API_KEY")
api_secret = os.environ.get("rALPACA_API_SECRET")

api = tradeapi.REST(base_url=base_url, key_id=api_key_id, secret_key=api_secret)


def create_api():
    url, key, secret = credentialing()
    api = tradeapi.REST(key_id=key, base_url=url, secret_key=secret)
    return api


socket = "wss://data.alpaca.markets/stream"
app = websocket.WebSocketApp(socket)
