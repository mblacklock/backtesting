from backtesting import Backtest, Strategy

from backtesting.lib import SQN

from backtesting.test import GOOG, SMA

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tulipy as ti
import csv
import os

data_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'data'))
filename= os.path.join(data_path, 'BTCUSDT_8h.csv')
BTC = pd.read_csv(filename, index_col='Time', parse_dates=True)[['Close']]
BTC.rename(columns = {'Close':'BTC'}, inplace = True)

filename= os.path.join(data_path, 'ETHUSDT_8h.csv')
DATA = pd.read_csv(filename, index_col='Time', parse_dates=True)

DATA = pd.merge(DATA, BTC, on='Time', how='left')

########## Market SQN ##############
# Strong Bull   1.47 <= x          #
# Bull          0.7  <= x <  1.47  #
# Neutral       0.0  <= x <  0.7   #
# Bear         -0.7  <= x <  0.0   #
# Strong Bull           x < -0.07  #
####################################

class Swing_Trend_01(Strategy):
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

        self.rsi_flag = 0

        self.atr = self.I(tulip_pad, ti.atr, self.data.High, self.data.Low, self.data.Close, 10)
        self.rsi = self.I(tulip_pad, ti.rsi, self.data.Close, 10)
        self.market_sqn = self.I(SQN, self.data.BTC, 75)
        self.price_sqn = self.I(SQN, self.data.Close, 75)

    def next(self):
        
        price = self.data.Close[-1]
        
        relative_strength = self.price_sqn / self.market_sqn

        ## Exits ##
        if self.position:

            ## 25% trailing stop ##
            ath_trade = max(self.data.Close[self.position.open_i:])
            if price <= 0.75 * ath_trade:
                self.position.close()
                self.rsi_flag = 0

            ## 2 times ATR move against the previous day ##
            if self.data.Close[-2] - price >= 2 * self.atr:
                self.position.close()
                self.rsi_flag = 0

        ## Setups ##
        elif self.market_sqn >= 0.7 and self.price_sqn >= 0.7: # and relative_strength > 1.:   
            if self.rsi < 40:
                self.rsi_flag = 1

        ## Entry & Stop ##
            if self.rsi_flag == 1 and price == max(self.data.Close[-10:]):
                self.buy(sl = 0.98 * min(self.data.Close[-10:]))


bt = Backtest(DATA, Swing_Trend_01, cash=10000, commission=.00075)

output = bt.run()

bt.plot()
print(output)

# python -m idlelib.idle
