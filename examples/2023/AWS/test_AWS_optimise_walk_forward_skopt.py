import datetime
import talib as ta
import pandas as pd
import matplotlib.pyplot as plt
import tqdm

from backtesting import Backtest
from backtesting import Strategy
from backtesting.lib import plot_heatmaps, resample_apply, crossover
from backtesting.test import GOOG

factor = 1_000_000
GOOG['Open'] /= factor
GOOG['High'] /= factor
GOOG['Low'] /= factor
GOOG['Close'] /= factor

size = 4

class RsiOscillator(Strategy):
 

    upper_bound = 70
    lower_bound = 30
    rsi_window = 14

    # Do as much initial computation as possible
    def init(self):
        self.rsi = self.I(ta.RSI, self.data.Close, self.rsi_window)

    # Step through bars one by one
    # Note that multiple buys are a thing here
    def next(self):
        price = self.data.Close[-1]
        if crossover(self.rsi, self.upper_bound):
            self.position.close()
        elif crossover(self.lower_bound, self.rsi):
            stop = price - 0.1*price
            oneR = abs(price - stop)
            take_profit = price + (1.2 * oneR)
            self.buy(size=size-1,sl=stop,tag=[oneR,size,"initial"])
            self.buy(size=1,sl=stop,tp=take_profit,tag=[oneR,size,"portion"])

##bt = Backtest(GOOG, RsiOscillator, cash=100, commission=.002)
##stats, heatmap, optimize_result  = bt.optimize(
##    upper_bound = [50, 100],
##    lower_bound = [20, 50],
##    rsi_window = [5, 30],
##    maximize = "SQN",
##    method = "skopt",
##    constraint = lambda param: param.upper_bound > param.lower_bound,
##    max_tries = 500,
##    random_state=0,
##    return_heatmap=True,
##    return_optimization=True
##    )
##
##print(stats)
##bt.plot(resample=False)

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
            upper_bound = [50, 100],
            lower_bound = [20, 50],
            rsi_window = [5, 30],
            maximize = "SQN",
            method = "skopt",
            constraint = lambda param: param.upper_bound > param.lower_bound,
            max_tries = 50,
            random_state=0,
            #return_heatmap=True,
            #return_optimization=True
            )
        
        lower_bound = stats_training._strategy.lower_bound
        upper_bound = stats_training._strategy.upper_bound

        bt_validation = Backtest(validation_data, strategy, cash=cash, commission=commission)
        stats_validation = bt_validation.run(
                                lower_bound = lower_bound,
                                upper_bound = upper_bound,
                                )
        stats_master.append(stats_validation)

    return stats_master

lookback_bars = 365
validation_bars = 182
warmup_bars = 30

stats = walk_forward(
    RsiOscillator,
    GOOG,
    lookback_bars=lookback_bars,
    validation_bars=validation_bars,
    warmup_bars=warmup_bars)

def plot_stats(data_full, stats):
    equity_curve = stats._equity_curve
    aligned_data = data_full.reindex(equity_curve.index)
    
    bt = Backtest(aligned_data, RsiOscillator, cash=100, commission=0.002)
    bt.plot(resample=False, results = stats, filename='finished_runs/trades', open_browser=False)

plot_stats(GOOG, stats[2])

def plot_full_equity_curve(
    data,
    stats_list,
    warmup_bars,
    lookback_bars):
    
    equity_curves = [x["_equity_curve"].iloc[warmup_bars:] for x in stats_list]
    
    combined = pd.Series(dtype="float64")
    for curve in equity_curves:
        if len(combined) == 0:
            combined = curve["Equity"]/100
            #check
        else:
            combined = pd.concat([combined, (curve["Equity"]/100)*combined.iloc[-1]]) 
                                             
    aligned_price_data = data[data.index <= combined.index[-1]].iloc[lookback_bars + warmup_bars:]
    
    fig, ax1 = plt.subplots()
    ax1.plot(combined.index, combined, color="orange")
    ax2 = ax1.twinx()
    ax2.plot(aligned_price_data.index, aligned_price_data.Close*factor)
    
    plt.savefig('finished_runs/equity_curve.png')

plot_full_equity_curve(GOOG, stats, warmup_bars, lookback_bars)

def plot_period_graph(
    data,
    lookback_bars,
    validation_bars):
    
    ranges = list(range(lookback_bars + warmup_bars, len(data) - validation_bars, validation_bars))
    
    fig, ax = plt.subplots()
    fig.set_figwidth(12)
    
    for i in range(len(ranges)):
        
        training_data = data.iloc[ranges[i]-lookback_bars:ranges[i]]
        validation_data = data.iloc[ranges[i]:ranges[i]+validation_bars]
        
        plt.fill_between(training_data.index,
                        [len(ranges) - i - 0.5]*len(training_data.index),
                        [len(ranges) - i + 0.5]*len(training_data.index),
                         color = "blue"
                        )
        
        plt.fill_between(validation_data.index,
                        [len(ranges) - i - 0.5]*len(validation_data.index),
                        [len(ranges) - i + 0.5]*len(validation_data.index),
                         color = "orange"
                        )
    
    plt.savefig('finished_runs/periods.png')

plot_period_graph(GOOG,lookback_bars,validation_bars)
