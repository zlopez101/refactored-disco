import os
from datetime import datetime
from itertools import product

import numpy as np
import pandas as pd
from pytz import timezone
from ta.momentum import rsi
from ta.trend import macd_diff, sma_indicator


class BaseBackTester:
    def __init__(self, symbol, paper=True):
        self.symbol = symbol
        self._paper = paper
        self.get_data()

    def get_data(self):
        import alpaca_trade_api as tradeapi

        url, key, secret = self._credentialing()
        api = tradeapi.REST(key, secret, url)
        if self.symbol.lower() == "random":
            assets = api.list_assets()
            symbols = [
                asset.symbol
                for asset in assets
                if asset.tradable
                and asset.exchange == "NYSE"
                and asset.status == "active"
                and asset.shortable
            ]
            self.symbol = np.random.choice(symbols)
        nyc = timezone("America/New_York")
        start = datetime(2020, 7, 15, 9, 30).astimezone(nyc)
        end = datetime(2020, 7, 15, 16, 0).astimezone(nyc)
        df = api.polygon.historic_agg_v2(
            self.symbol,
            1,
            "minute",
            _from=pd.Timestamp(start).isoformat(),
            to=pd.Timestamp(end).isoformat(),
        ).df
        self.data = df[np.logical_and(df.index >= start, df.index <= end)]

    def _credentialing(self):
        if self._paper:
            url = "https://paper-api.alpaca.markets"
            key = os.environ.get("ALPACA_API_KEY")
            secret = os.environ.get("ALPACA_API_SECRET")
        else:
            url = "https://api.alpaca.markets"
            key = os.environ.get("rALPACA_API_KEY")
            secret = os.environ.get("rALPACA_API_SECRET")
        return url, key, secret

    def apply_rsi(self, time_period, on_data="close"):
        """
        calculate the RSI on specified data type. return df with columns added.

        Parameters:

        df : pandas dataframe of ohlcv data
        time_period : iterable of length 2, specifying the range to vary the window
        on_data : str of data to calculate macd indicator on

        """
        assert len(time_period) == 2, "time_period must have a start and and end"
        self._ensure_data_calculation_choice(on_data)
        self.rsi = pd.DataFrame(index=self.data.index)
        for period in range(time_period[0], time_period[1]):
            self.rsi["RSI_" + str(period) + "_period"] = rsi(
                self.data[on_data], n=period
            )

    def _ensure_data_calculation_choice(self, on_data):
        column_choices = ["close", "open", "low", "high", "volume"]
        if on_data.lower() not in column_choices:
            raise ValueError(
                f"Invalid Data Column Selection. {on_data} not in DataFrame."
            )

    def get_signals(self, rsi_check):
        """
        Calculate when a signal was received.

        FOR NOW:
        use only rsi + either (sma_cross, macd) 

        Parameters:

        df_rsi : pandas dataframe of RSI's
        df_signal : pandas dataframe of either sma crossover or macd
        rsi_check : iterable of len(2), The value of RSI to use as upper bound for traders
        """

        def func(x):
            """
            rolling window calculation to check if the signal line crossed zero
            """
            diff = x[-1] - x[0]
            # make sure the last value is bigger than the first
            if diff > 0:
                # make sure the first value is less than zero, last value greater than zero
                if x[0] < 0 and x[-1] > 0:
                    return True
                # difference not across zero
                else:
                    return False
            else:
                return False

        self.signals = pd.DataFrame(index=self.data.index)
        rsi_check = range(rsi_check[0], rsi_check[1])
        columns = product(self.rsi.columns, self.indicator.columns, rsi_check)
        for column in columns:
            # check if RSI is below certain number
            x = self.rsi[column[0]] < column[2]  # boolean mask
            # do a rolling sum (that would be negative if crossover from the bottom) and a zero check
            y = (
                self.indicator[column[1]].rolling(window=2).apply(func).fillna(0)
            )  # also a boolean mask
            name = f"RSI period: {column[0]}, RSI_screen_top: {column[2]} Signal period: {column[1]}"
            final = np.logical_and(x, y)
            self.signals[name] = np.logical_and(x, y)

    def analyze_signals(self, high, low, window):
        """
        for each column of signals, run the analysis and return the results as a dictionary of dictionarys
        The outer dictionary key will contain the parameters for generating the signals. The value of this dictionary
        will be another dictionary, where the key will be the time of the signal, and the value will be either 1, 0, -1
        for High hit, No hit, and Low hit. 
        """

        def create_window(signal, window):
            """
            creates a 15 minute window after a True in the signal, based on the index where the value is True
            The signal also has to be contained within the 15 minute mark (can't be at the end of the day)
            returns a dictionary with the key as a string of start_signal

            Parameters

            signal : Pandas series with bool True as the signal
            """
            dct = {}
            all_sigs = signal.iloc[:-window][signal == True]
            for time in all_sigs.index:
                dct[time] = np.nan
            return dct

        def analyze(dct, window, high, low):
            """
            analyze the original dataframe and see if first:
            -highs crossed threshold 
            -lows crossed threshold
            -timer ran out

            Parameters

            data: A dataframe containing the high and lowes
            dct: dictionary created by `create_window`. 
            high: float specifying the percentage increase threshold
            low: float specifying the percentage decrease threshold
            time: int specifying the length of the window in bars
            """
            h_perc = 1 + (high / 100)
            l_perc = 1 - (low / 100)

            base_targets = [self.data["close"][key] for key in list(dct.keys())]
            high_targets = [target * h_perc for target in base_targets]
            low_targets = [target * l_perc for target in base_targets]
            for key, high, low in zip(list(dct.keys()), high_targets, low_targets):
                # slice dataframe for range and check if the highs > high_targets, lows < low_targets
                # flag setup
                h_hit, l_hit = False, False
                count = 0
                generator = self.data.loc[key:].iterrows()

                while not (h_hit) and not (l_hit) and count < window:
                    index, row = next(generator)
                    if row.high >= high:
                        h_hit = True
                    if row.low <= low:
                        l_hit = True
                    count += 1

                if h_hit:
                    dct[key] = 1
                if l_hit:
                    dct[key] = -1
                else:
                    dct[key] = 0
            return dct

        results = []
        for column in self.signals.columns:

            results.append(
                (
                    column,
                    analyze(
                        create_window(self.signals[column], window), window, high, low,
                    ),
                )
            )

        self.results = results


class BackTestMacd(BaseBackTester):
    def __init__(self, symbol, macd_fast, macd_slow, macd_sig):
        super().__init__(symbol)
        assert len(macd_fast) == 2, "macd_fast must have a start and and end"
        assert len(macd_slow) == 2, "macd_slow must have a start and and end"
        assert len(macd_sig) == 2, "macd_sig must have a start and and end"
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_sig = macd_sig

    def apply_macd(self, on_data="close"):
        self._ensure_data_calculation_choice(on_data)

        n_fast_range = range(self.macd_fast[0], self.macd_fast[1])
        n_slow_range = range(self.macd_slow[0], self.macd_slow[1])
        n_sign_range = range(self.macd_sig[0], self.macd_sig[1])

        complete = product(n_fast_range, n_slow_range, n_sign_range)
        self.macd = pd.DataFrame(index=self.data.index)
        for combo in complete:
            self.macd[
                str(combo[0]) + "f_" + str(combo[1]) + "s_" + str(combo[2]) + "sig"
            ] = macd_diff(
                self.data[on_data], n_fast=combo[0], n_slow=combo[1], n_sign=combo[2]
            )
        self.macd.fillna(0, inplace=True)
        self.indicator = self.macd

    def run(self, rsi_values, window=30, on_data="close", high=2, low=1):

        assert len(rsi_values) == 4

        time_period_for_rsi = rsi_values[:2]
        rsi_upper_bound = rsi_values[2:]

        self.apply_macd(on_data=on_data)
        self.apply_rsi(time_period_for_rsi, on_data=on_data)
        self.get_signals(rsi_upper_bound)
        self.analyze_signals(high, low, window)
        return self.results


class BackTestSMA(BaseBackTester):
    pass


# testing
if __name__ == "__main__":
    macd_rsi = BackTestMacd("random", (5, 8), (26, 28), (9, 10))

    results = macd_rsi.run([9, 10, 60, 61])
    # print([setting for setting, result in results if result > 0])
    print(results[0])
