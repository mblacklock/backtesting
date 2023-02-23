import datetime
import talib as ta
import pandas as pd

from backtesting import Backtest
from backtesting import Strategy
from backtesting.lib import crossover, plot_heatmaps, resample_apply, barssince
from backtesting.test import GOOG

factor = 1000

class RsiOscillator(Strategy):

    upper_bound = 70
    lower_bound = 30
    rsi_window = 14

    # Do as much initial computation as possible
    def init(self):
        self.daily_rsi = self.I(ta.RSI, self.data.Close, self.rsi_window)

    # Step through bars one by one
    # Note that multiple buys are a thing here
    def next(self):

        price = self.data.Close[-1]

        
        if crossover(self.daily_rsi, self.upper_bound):
                self.position.close()
                
        elif crossover(self.daily_rsi, self.lower_bound):
                self.buy()

bt = Backtest(GOOG, RsiOscillator, cash=1_000 * factor, commission=.002)

stats = bt.run()
bt.plot()

stats['Equity Final [$]'] /= factor
stats['Equity Peak [$]'] /= factor
print(stats)
trades = stats['_trades']
trades.Size /= factor
trades.PnL /= factor
print(trades.to_string())
