from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG

import matplotlib.pyplot as plt
import numpy as np

class SmaCross(Strategy):
    n1 = 10
    n2 = 30

    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        price = self.data.Close[-1]
        
        if crossover(self.sma1, self.sma2):
            self.buy(sl = 0.9 * price)
        elif crossover(self.sma2, self.sma1):
            self.sell(sl = 1.1 * price)


bt = Backtest(GOOG, SmaCross, cash=10000, commission=.002)

output = bt.run()

#bt.plot()
print(output)

# python -m idlelib.idle

# plots
