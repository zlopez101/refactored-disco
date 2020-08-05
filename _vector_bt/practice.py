import vectorbt as vbt
import numpy as np
import yfinance as yf

# Fetch daily price of Bitcoin
price = yf.Ticker("BTC-USD").history(period="max")["Close"]

# Compute moving averages for all combinations of fast and slow windows
fast_ma, slow_ma = vbt.MA.from_combs(
    price, np.arange(2, 101), 2, names=["fast", "slow"], hide_params=["ewm"]
)

# Generate crossover signals for each combination
entries = fast_ma.ma_above(slow_ma, crossed=True)
exits = fast_ma.ma_below(slow_ma, crossed=True)

# Model performance
portfolio = vbt.Portfolio.from_signals(price, entries, exits, fees=0.001, freq="1D")

# Get total return, reshape to symmetric matrix, and plot the whole thing
portfolio.total_return.vbt.heatmap(
    x_level="fast_window",
    y_level="slow_window",
    symmetric=True,
    trace_kwargs=dict(colorbar=dict(title="Total return", tickformat="%")),
)
