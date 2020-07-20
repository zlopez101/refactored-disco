import backtrader as bt


class Zach(bt.Strategy):

    params = dict(
        ma_fast=None,  # period for the fast moving average
        ma_slow=None,  # period for the slow moving average
        rsi_period=None,
        rsi_high=None,
        rsi_low=None,
        macd_filter=None,
    )

    def __init__(self):

        # if moving averages are defined
        if self.p.ma_fast and self.p.ma_slow:
            sma1 = bt.ind.SMA(period=self.p.ma_fast)  # fast moving average
            sma2 = bt.ind.SMA(period=self.p.ma_slow)  # slow moving average
            self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal
        else:
            self.crossover = True

        # if rsi parameters are defined
        if self.p.rsi_period:
            self.rsi = bt.ind.RSI_SMA(period=self.p.rsi_period)
        else:
            self.rsi = True
            self.p.rsi_high = 200

        # if macd parameter are defined
        if self.p.macd_filter:
            self.macd = bt.ind.MACD(
                period_me1=self.p.macd_filter[0],
                period_me2=self.p.macd_filter[1],
                period_signal=self.p.macd_filter[2],
            )
        else:
            self.macd = True

    def next(self):

        #
        if not self.position:  # not in the market
            if (
                self.crossover > 0 and self.rsi < self.p.rsi_high
            ):  # if fast crosses slow to the upside

                self.buy()  # enter long
        elif self.crossover < 0:  # in the market & cross to the downside
            self.close()  # close long position

        #

