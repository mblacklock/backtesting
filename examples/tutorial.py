import pandas as pd

def SMA(values, n):
    """
    Return SMA of 'values', at
    each step taking into account 'n' previous values.
    """
    return pd.Series(values).rolling(n).mean()

from backtesting.lib import SignalStrategy, TrailingStrategy
from backtesting.lib import crossover

class SmaCross(SignalStrategy, TrailingStrategy):
    
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 10
    n2 = 20
    stop = 4
    ATRrange = 100
    
    def init(self):
        # In init() and in next() it is important to call the
        # super method to properly initialize all the classes
        super().init()
        
        # Precompute two moving averages
        sma1 = self.I(SMA, self.data.Close, self.n1)
        sma2 = self.I(SMA, self.data.Close, self.n2)

        # Taking a first difference (`.diff()`) of a boolean
        # series results in +1, 0, and -1 values. In our signal,
        # as expected by SignalStrategy, +1 means buy,
        # -1 means sell, and 0 means to hold whatever current
        # position and wait. See the docs.
        signal = (pd.Series(sma1) > sma2).astype(int).diff().fillna(0)

        # Set the signal vector using the method provided
        # by SignalStrategy
        self.set_signal(signal)
        
        # Set trailing stop-loss to 4x ATR
        # using the method provided by TrailingStrategy
        self.set_atr_periods(self.ATRrange)
        self.set_trailing_sl(self.stop)
    
##    def next(self):
##        # If sma1 crosses above sma2, buy the asset
##        if crossover(self.sma1, self.sma2):
##            self.buy()
##
##        # Else, if smal crosses below sma2, sell it
##        elif crossover(self.sma2, self.sma1):
##            self.sell()

from backtesting import Backtest
from backtesting.test import GOOG

bt = Backtest(GOOG, SmaCross, commission=.002)
bt.run()

stats = bt.optimize(n1=range(5, 30, 5),
                    n2=range(10, 70, 5),
                    stop=range(1, 5, 1),
                    ATRrange=range(50, 150, 50),
                    maximize='Equity Final [$]',
                    constraint=lambda p: p.n1 < p.n2)
