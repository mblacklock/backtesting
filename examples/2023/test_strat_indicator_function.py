import datetime
import pandas_ta as ta
import pandas as pd

from backtesting import Backtest, Strategy
from backtesting.test import GOOG

factor = 1

def indicator(data):
    bbands = ta.bbands(close = data.Close.s, std = 1)
    return bbands.to_numpy().T[:3]

class BBStrategy(Strategy):

    # Do as much initial computation as possible
    def init(self):
        self.bbands = self.I(indicator, self.data)
        pass

    # Step through bars one by one
    # Note that multiple buys are a thing here
    def next(self):

        lower_band = self.bbands[0]
        upper_band = self.bbands[2]

        if self.position:
            if self.data.Close[-1] > upper_band[-1]:
                self.position.close()
        else:
            if self.data.Close[-1] < lower_band[-1]:
                self.buy()

bt = Backtest(GOOG, BBStrategy, cash=10_000 * factor, commission=0)

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
