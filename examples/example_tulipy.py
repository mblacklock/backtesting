from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG

import matplotlib.pyplot as plt
import numpy as np
import tulipy as ti

class SmaCross(Strategy):
    n1 = 10
    n2 = 30

    def init(self):

        def tulip_pad(func, *args, **kwargs):
            outputs = func(*args, **kwargs)
            if not isinstance(outputs, tuple):
                outputs = (outputs,)
            expect_size = len(args[0])
            padded = [np.r_[np.repeat(np.nan, expect_size - o.size), o]
                      for o in outputs]
            return padded
        
        self.bbands1 = self.I(tulip_pad, ti.bbands, self.data.Close, self.n1, 2)[1]
        self.bbands2 = self.I(tulip_pad, ti.bbands, self.data.Close, self.n2, 2)[1]

    def next(self):
        price = self.data.Close[-1]
        
        if crossover(self.bbands1, self.bbands2):
            self.buy(sl = 0.9 * price)
        elif crossover(self.bbands2, self.bbands1):
            self.sell(sl = 1.1 * price)


bt = Backtest(GOOG, SmaCross, cash=10000, commission=.002)

output = bt.run()

bt.plot()
print(output)

# python -m idlelib.idle
