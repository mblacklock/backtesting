import datetime
import talib as ta
import pandas as pd

from backtesting import Backtest
from backtesting import Strategy
from backtesting.lib import crossover, plot_heatmaps, resample_apply, barssince
from backtesting.test import GOOG

factor = 1_000_000

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
                
        elif crossover(self.daily_rsi, self.lower_bound) and not self.position:
            stop = price - 30
            oneR = abs(price - stop)
            size =  round(1 / oneR * factor)
            self.buy(size=size,sl=stop)

bt = Backtest(GOOG, RsiOscillator, cash=100 * factor, commission=0)

stats = bt.run()
bt.plot(factor=factor)

stats['Equity Final [$]'] /= factor
stats['Equity Peak [$]'] /= factor
stats['Best Trade [R]'] /= factor
stats['Worst Trade [R]'] /= factor
stats['Expectancy (mean R)'] /= factor
trades = stats['_trades'].drop('ReturnPct', axis=1)
trades.Size /= factor
trades.PnL /= factor
print(stats)
print(trades.to_string())
