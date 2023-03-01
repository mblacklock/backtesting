import datetime
import talib as ta
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tqdm

from backtesting import Backtest
from backtesting import Strategy
from backtesting.lib import crossover, plot_heatmaps
from backtesting.test import GOOG

def optim_func(series):

    if series["# Trades"] < 10:
        return -1
    
    return series["Equity Final [$]"] / series["Exposure Time [%]"]

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

bt = Backtest(GOOG, RsiOscillator, cash=100, commission=.002)
stats, heatmap, optimize_result  = bt.optimize(
    upper_bound = [50, 100],
    lower_bound = [20, 50],
    rsi_window = [5, 30],
    maximize = "SQN",
    method = "skopt",
    constraint = lambda param: param.upper_bound > param.lower_bound,
    max_tries = 500,
    random_state=0,
    return_heatmap=True,
    return_optimization=True
    )

strategy_name = str(stats._strategy)

# Export stats summary
with open(str('finished_runs/'+strategy_name)+'_summary.txt', 'w') as f:
    f.write(str(stats))

bt.plot(filename='finished_runs/'+strategy_name+'_trades_plot', open_browser=False)

plot_heatmaps(heatmap, agg="mean", open_browser=False, filename="finished_runs/"+strategy_name+"_heatmaps_plot")

trades = stats['_trades'].drop('ReturnPct', axis=1)
trades.Size /= size
trades.EntryPrice = round(trades.EntryPrice * factor,2)
trades.ExitPrice = round(trades.ExitPrice * factor,2)
trades.PnL = round(trades.PnL,2)
trades.OneR = round(trades.OneR * factor,2)

# Export trades
with open(str('finished_runs/'+strategy_name)+'_trades.txt', 'w') as f:
    f.write(trades.to_string())

from skopt.plots import plot_objective, plot_evaluations

_ = plot_objective(optimize_result, n_points=10)
figure=_.flatten()[0].figure
figure.set_size_inches(12,12)
figure.savefig('finished_runs/'+strategy_name+'_plot_objective.png', dpi=300)
figure.set_size_inches(6,6)

_ = plot_evaluations(optimize_result, bins=10)
figure=_.flatten()[0].figure
figure.set_size_inches(12,12)
figure.savefig('finished_runs/'+strategy_name+'_plot_evaluations.png', dpi=300)
figure.set_size_inches(6,6)
