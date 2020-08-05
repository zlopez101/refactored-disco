from bokeh.plotting import figure, output_file, show
import alpaca_trade_api as trade_api

# from bokeh.layouts import column
from bokeh.models import ColumnDataSource
import pandas as pd
from btutils import credentialing
from pd_bt import *
from datetime import datetime

url, key, secret = credentialing()
api = trade_api.REST(key_id=key, secret_key=secret, base_url=url)

start = datetime(2020, 1, 7)
end = datetime(2020, 1, 8)


df = api.polygon.historic_agg_v2(
    "MSFT",
    1,
    "minute",
    _from=pd.Timestamp(start).isoformat(),
    to=pd.Timestamp(end).isoformat(),
).df

# data, symbol = get_data("PVG")

# my_macd = apply_macd(data, (8, 9), (24, 25), (9, 10))
# my_rsi = apply_rsi(data, (14, 15))
# signals = get_signals(my_rsi, my_macd, (60, 62))

# df = pd.concat([data, my_macd, my_rsi, signals], axis=1)
source = ColumnDataSource(df)

p = figure(
    plot_width=800,
    plot_height=300,
    title="MSFT",
    x_axis_type="datetime",
    y_axis_label="Price",
)
p.line(x="timestamp", y="close", source=source, color="blue")
# p.circle(
#     x=df.index[
#         df["RSI period: RSI_Period_14, RSI_screen_top: 60 Signal period: MACD: 8_24_9"]
#     ],
#     y=df["close"][
#         df["RSI period: RSI_Period_14, RSI_screen_top: 60 Signal period: MACD: 8_24_9"]
#     ],
#     color="green",
#     size=10,
# )
# s = figure(
#     plot_width=800,
#     plot_height=200,
#     x_range=p.x_range,
#     x_axis_type="datetime",
#     y_axis_label="MACD",
# )
# s.line(x="timestamp", y="MACD: 8_24_9", source=source, color="red")
# t = figure(
#     plot_width=800,
#     plot_height=200,
#     x_range=p.x_range,
#     x_axis_type="datetime",
#     y_axis_label="MACD",
# )
# t.line(x="timestamp", y="RSI_Period_14", source=source)
show(p)

