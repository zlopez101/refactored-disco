import websocket, json
from utils import credentialing
import alpaca_trade_api as trade_api

url, key, secret = credentialing()

conn = trade_api.StreamConn(
    base_url=url, key_id=key, secret_key=secret, data_stream="polygon"
)


@conn.on(r"^AM$")
async def on_minute_bars(conn, channel, bar):
    print("bars: ", bar)


conn.run(["AM.TSLA"])

"""
def on_open(ws):
    print("Opening...")
    _, key, secret = credentialing()
    auth_data = {
        "action": "authenticate",
        "data": {"key_id": key, "secret_key": secret},
    }
    ws.send(json.dumps(auth_data))

    listen_message = {"action": "listen", "data": {"streams": ["AM.TSLA"]}}

    ws.send(json.dumps(listen_message))


def on_message(ws, message):
    print("received a message")
    print(message)


socket = "wss://data.alpaca.markets/stream"
app = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message)
app.run_forever()
"""
