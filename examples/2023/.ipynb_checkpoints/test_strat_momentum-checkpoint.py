import datetime
import pandas_ta as ta
import pandas as pd

from backtesting import Backtest, Strategy
from backtesting.test import GOOG

factor = 1_000_000

def indicator(data):
    # % increase in stock over 7 days
    return data.Close.s.pct_change(periods = 7) * 100

class MomentumStrategy(Strategy):

    # Do as much initial computation as possible
    def init(self):
        self.pct_change = self.I(indicator, self.data)

    # Step through bars one by one
    # Note that multiple buys are a thing here
    def next(self):
        change = self.pct_change[-1]
        price = self.data.Close[-1]

        if self.position:
            if change < 0:
                self.position.close()

        else:
            if change > 5 and self.pct_change[-2] > 5:
                stop = (1 - (change / 100)) * price
                oneR = abs(price - stop)
                size =  round(1 / oneR * factor)
                self.buy(size=size,sl=stop)

bt = Backtest(GOOG, MomentumStrategy, cash=100 * factor, commission=0)

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
