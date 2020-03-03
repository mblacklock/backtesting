from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
import os

data_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'data'))
filename= os.path.join(data_path, 'test.csv')

DATA = pd.read_csv(filename, index_col='Time', parse_dates=True)

class SmaCross(Strategy):
    n1 = 5
    n2 = 7
    stop = 0.05

    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        price = self.data.Close[-1]
        
        if crossover(self.sma1, self.sma2):
            self.buy(sl = (1 - self.stop) * price)
        elif crossover(self.sma2, self.sma1):
            self.sell(sl = (1 + self.stop) * price)


bt = Backtest(DATA, SmaCross, cash=10000, commission=.00075)

output = bt.run()

bt.plot()
print(output)

#ent = output._trade_data[['Entry Price', 'Stop Loss']].dropna()
#print(ent['Stop Loss'] / ent['Entry Price'])

# python -m idlelib.idle
# https://github.com/kernc/backtesting.py
#https://tulipindicators.org/
