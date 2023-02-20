import datetime
import talib as ta
import pandas as pd

from backtesting import Backtest
from backtesting import Strategy
from backtesting.lib import crossover, TrailingStrategy
from backtesting.test import GOOG

factor = 1

class RsiOscillator(TrailingStrategy):

    upper_bound = 70
    lower_bound = 30
    rsi_window = 14

    # Do as much initial computation as possible
    def init(self):
        super().init()
        super().set_trailing_sl(1)
        pass

    # Step through bars one by one
    # Note that multiple buys are a thing here
    def next(self):
        super().next()

        price = self.data.Close[-1]
                
        if self.position:
            pass                
        else:
            self.buy(size = 1, sl = price - 10, tp = price + 20)

bt = Backtest(GOOG, RsiOscillator, cash=10_000 * factor, commission=0)

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
#print(trades.to_string())
