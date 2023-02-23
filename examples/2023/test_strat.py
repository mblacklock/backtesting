import datetime
import pandas_ta as ta
import pandas as pd
import numpy as np

from backtesting import Backtest, Strategy
from backtesting.lib import resample_apply

data = pd.read_csv("data\BTCUSDT-1m-2023-01.csv",
                   usecols = [0,1,2,3,4],
                   names = ["Date","Open","High","Low","Close"])
data["Date"] = pd.to_datetime(data["Date"], unit = "ms")
data.set_index("Date", inplace=True)
#data = data.iloc[0:20000]

factor = 1_000_000
data['Open'] /= factor
data['High'] /= factor
data['Low'] /= factor
data['Close'] /= factor

def indicator(data):
    # % increase in stock over 7 periods
    return data.pct_change(periods = 7) * 100

class MomentumStrategy(Strategy):

    small_threshold = 0
    large_threshold = 3

    # Do as much initial computation as possible
    def init(self):
        
        self.short_pct_change = resample_apply(
            '15min', indicator, self.data.Close.s)
        self.long_pct_change = resample_apply(
            '1h', indicator, self.data.Close.s)

    # MB - Any dollar amounts must be divided by factor
    def next(self):
        change_short = self.short_pct_change[-1]
        change_long = self.long_pct_change[-1]
        price = self.data.Close[-1]

        if self.position:
            if self.position.is_long and change_short < self.small_threshold:
                self.position.close()
            elif self.position.is_short and change_short > -self.small_threshold:
                self.position.close()

        else:
            if change_short > self.large_threshold and change_long > self.large_threshold:
                stop = price - (change_short / 100) * price
                oneR = abs(price - stop)
                self.buy(size=1, sl=stop, tag=oneR)

            elif change_short < -self.large_threshold and change_long < -self.large_threshold:
                stop = price - (change_long / 100) * price
                oneR = abs(price - stop)
                self.sell(size=1, sl=stop, tag=oneR)

'''
bt = Backtest(data, MomentumStrategy, cash=100, commission=0.002/factor)

stats = bt.optimize(
    small_threshold = list(np.arange(0,1,0.1)),
    large_threshold = list(np.arange(1,3,0.2)),
    maximize = "Equity Final [$]"
    )
bt.plot(resample=False)

trades = stats['_trades'].drop('ReturnPct', axis=1)
trades.EntryPrice = round(trades.EntryPrice * factor,2)
trades.ExitPrice = round(trades.ExitPrice * factor,2)
trades.PnL = round(trades.PnL,2)
trades.StopLoss = round(trades.StopLoss * factor,2)
trades.oneR = round(trades.oneR * factor,2)

print(stats)
print(trades.to_string())
'''
def walk_forward(
    strategy,
    data_full,
    warmup_bars,
    lookback_bars,
    validation_bars,
    cash = 100,
    commission = 0.002/factor
    ):

    stats_master = []

    for i in range(lookback_bars + warmup_bars, len(data_full) - validation_bars, validation_bars):
        
        training_data = data_full.iloc[i-lookback_bars-warmup_bars:i]
        validation_data = data_full.iloc[i-warmup_bars:i+validation_bars]

        bt_training = Backtest(training_data, strategy, cash=cash, commission=commission)
        stats_training = bt_training.optimize(
            small_threshold = list(np.arange(0,1,0.1)),
            large_threshold = list(np.arange(1,3,0.2)),
            maximize = "Equity Final [$]"
            )
        
        small_threshold = stats_training._strategy.small_threshold
        large_threshold = stats_training._strategy.large_threshold

        bt_validation = Backtest(validation_data, strategy, cash=cash, commission=commission)
        stats_validation = bt_validation.run(
                                small_threshold = small_threshold,
                                large_threshold = large_threshold,
                                )
        stats_master.append(stats_validation)

    return stats_master

lookback_bars = 14*1440
validation_bars = 2*1440
warmup_bars = 16*60

stats = walk_forward(
    MomentumStrategy,
    data,
    lookback_bars=lookback_bars,
    validation_bars=validation_bars,
    warmup_bars=warmup_bars)
print(stats)

