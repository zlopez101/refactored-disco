import numpy as np
import pandas as pd
from ta.trend import macd_diff, sma_indicator
from ta.momentum import rsi
import argparse
import datetime
from itertools import product

from btutils import get_data, ensure_correct_data_calculation_choice

df, symbol = get_data("random")


# apply transformations on data
def apply_macd(df, n_fast, n_slow, n_sign, on_data="close"):
    """
    calculate MACD on specified data type. return df with columns added

    Parameters:

    df : pandas dataframe of ohlcv data
    n_fast : iterable of length 2, specifying the range to vary the n_fast period of macd
    n_slow : iterable of length 2, specifying the range to vary the n_slow period of macd
    n_sign : iterable of length 2, specifying the range to vary the n_signal period of macd
    on_data : str of data to calculate macd indicator on

    """
    ensure_correct_data_calculation_choice(on_data)

    n_fast_range = range(n_fast[0], n_fast[1])
    n_slow_range = range(n_slow[0], n_slow[1])
    n_sign_range = range(n_sign[0], n_sign[1])

    complete = product(n_fast_range, n_slow_range, n_sign_range)
    df_new = pd.DataFrame(index=df.index)

    for combo in complete:
        # combo is a tuple of (n_fast, n_slow)
        df_new[
            "MACD: " + str(combo[0]) + "_" + str(combo[1]) + "_" + str(combo[2])
        ] = macd_diff(df[on_data], n_fast=combo[0], n_slow=combo[1], n_sign=combo[2])
    df_new.fillna(0, inplace=True)
    return df_new


def apply_rsi(df, time_period, on_data="close"):
    """
    calculate the RSI on specified data type. return df with columns added.

    Parameters:

    df : pandas dataframe of ohlcv data
    time_period : iterable of length 2, specifying the range to vary the window
    on_data : str of data to calculate macd indicator on

    """
    ensure_correct_data_calculation_choice(on_data)
    df_new = pd.DataFrame(index=df.index)
    for period in range(time_period[0], time_period[1]):
        df_new["RSI_Period_" + str(period)] = rsi(df[on_data], n=period, fillna=True)
    return df_new


def apply_sma_cross(df, n_fast, n_slow, on_data="close"):
    """
    calculate moving average crossover on specified data type. return df with columns added
    returns the distance between lines. reference point is the slower ma

    Parameters:

    df : pandas dataframe of ohlcv data
    n_fast : iterable of length 2, specifying the range to vary the n_fast period of moving average
    n_slow : iterable of length 2, specifying the range to vary the n_slow period of moving average
    on_data : str of data to calculate macd indicator on

    """
    ensure_correct_data_calculation_choice(on_data)

    n_fast_range = range(n_fast[0], n_fast[1])
    n_slow_range = range(n_slow[0], n_slow[1])

    complete = product(n_fast_range, n_slow_range)
    df_new = pd.DataFrame(index=df.index)
    for combo in complete:
        moving_average_distance = sma_indicator(df[on_data], combo[1]) - sma_indicator(
            df[on_data], combo[0]
        )
        df_new[str(combo[0]), str(combo[1])] = moving_average_distance.fillna(0)
    return df_new


def get_signals(df_rsi, df_signal, rsi_check):
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

    signals = pd.DataFrame(index=df_rsi.index)
    rsi_check = range(rsi_check[0], rsi_check[1])
    columns = product(df_rsi.columns, df_signal.columns, rsi_check)
    for column in columns:
        # check if RSI is below certain number
        x = df_rsi[column[0]] < column[2]  # boolean mask
        # do a rolling sum (that would be negative if crossover from the bottom) and a zero check
        y = (
            df_signal[column[1]].rolling(window=2).apply(func).fillna(0)
        )  # also a boolean mask
        name = f"RSI period: {column[0]}, RSI_screen_top: {column[2]} Signal period: {column[1]}"
        final = np.logical_and(x, y)
        signals[name] = np.logical_and(x, y)
    return signals


def analyze_signals(df, signals, window=30):
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

    def analyze(data, dct, window, high=2, low=1):
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

        base_targets = [data["close"][key] for key in list(dct.keys())]
        high_targets = [target * h_perc for target in base_targets]
        low_targets = [target * l_perc for target in base_targets]
        for key, high, low in zip(list(dct.keys()), high_targets, low_targets):
            # slice dataframe for range and check if the highs > high_targets, lows < low_targets
            # flag setup
            h_hit, l_hit = False, False
            count = 0
            generator = data.loc[key:].iterrows()

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

    dct = {}
    for column in signals.columns:

        dct[column] = analyze(df, create_window(signals[column], window), window)

    return dct


def main(df):
    """
    the main function
    """
    # rsi = apply_rsi(df, (16, 20))
    # macd = apply_macd(df, (8, 12), (26, 28), (9, 10))
    # signals = get_signals(rsi, macd, (62, 63))
    new = [(signal, df[signals[signal]]) for signal in signals.columns]
    new = [not_empty for not_empty in new if not not_empty[1].empty]
    return new


if __name__ == "__main__":
    data, symbol = get_data("PVG")
    my_macd = apply_macd(data, (8, 10), (24, 26), (9, 10))
    my_rsi = apply_rsi(data, (13, 15))
    signals = get_signals(my_rsi, my_macd, (60, 61))
    # dct = create_window(signals.iloc[:, 0])
    # dct = analyze(data, dct)
    dct = analyze_signals(data, signals, 30)
    print(dct)
