import datetime
import talib as ta
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from skopt.plots import plot_objective, plot_evaluations
import os

from backtesting import Backtest, Strategy
from backtesting.lib import crossover, plot_heatmaps

from backtesting.test import GOOG

factor = 1_000_000
GOOG['Open'] /= factor
GOOG['High'] /= factor
GOOG['Low'] /= factor
GOOG['Close'] /= factor

data = GOOG

size = 4

class Base_Strategy(Strategy):
 
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
        elif crossover(self.lower_bound, self.rsi) and not self.position:
            stop = price - 0.1*price
            oneR = abs(price - stop)
            take_profit = price + (1.2 * oneR)
            params = [self.lower_bound, self.upper_bound]
            self.buy(size=size-1,sl=stop,tag=[oneR,size,"initial",params])
            self.buy(size=1,sl=stop,tp=take_profit,tag=[oneR,size,"portion",params])

def walk_forward(
    strategy,
    data,
    lookback_bars,
    validation_bars,
    cash = 100,
    commission = 0.002/factor
    ):
    
    parameters_training_all = []
    trades_training_all = []
    stats_training_all = []
            
    for i in tqdm(range(lookback_bars, len(data) - validation_bars, validation_bars)):
        
        start = data.index[i-lookback_bars]
        end = data.index[i]
        
        class WF(strategy):

            start_date = start
            end_date = end

            def init(self):
                super().init()

            def next(self):
                # only call the strategy if in training period
                if self.start_date <= self.data.index[-1] < self.end_date:
                    super().next()

        bt_training = Backtest(data, WF, cash=100, commission=.002)
        stats_training, heatmap, optimize_result = bt_training.optimize(
            upper_bound = [50, 100],
            lower_bound = [20, 50],
            rsi_window = [10, 30],
            maximize = "SQN",
            method = "skopt",
            constraint = lambda param: param.upper_bound > param.lower_bound,
            max_tries = 50,
            random_state=0,
            return_heatmap=True,
            return_optimization=True
            )
        
        trades = stats_training['_trades'].drop('ReturnPct', axis=1)
        trades.Size /= size
        trades.EntryPrice = round(trades.EntryPrice * factor,2)
        trades.ExitPrice = round(trades.ExitPrice * factor,2)
        trades.PnL = round(trades.PnL,2)
        trades.OneR = round(trades.OneR * factor,2)
        
        if not os.path.exists('finished_runs/training'):
            os.mkdir('finished_runs/training')
        strategy_name = str(stats_training._strategy)
        start_str = start.strftime("%Y-%m-%d %H-%M")
        end_str = end.strftime("%Y-%m-%d %H-%M")
        # Export stats summary & trades plot
        with open('finished_runs/training/' + start_str + '_' + end_str + '_' + strategy_name +'_summary.txt', 'w') as f:
            f.write(str(stats_training))
##            
##        bt_training.plot(filename='finished_runs/training/' + start_str + '_' + end_str + '_' + strategy_name +'_trades_plot', open_browser=False)
        plot_heatmaps(heatmap, agg="mean", open_browser=False, filename='finished_runs/training/' + start_str + '_' + end_str + '_' + strategy_name +'_heatmaps_plot')
##        
        # Export trades
        with open(str('finished_runs/training/' + start_str + '_' + end_str + '_' + strategy_name +'_trades.txt'), 'w') as f:
            f.write(trades.to_string())

        # plot skopt
        _ = plot_objective(optimize_result, n_points=10)
        figure=_.flatten()[0].figure
        figure.set_size_inches(12,12)
        figure.savefig('finished_runs/training/' + start_str + '_' + end_str + '_' + strategy_name +'_plot_objective.png', dpi=300)

        _ = plot_evaluations(optimize_result, bins=10)
        figure=_.flatten()[0].figure
        figure.set_size_inches(12,12)
        figure.savefig('finished_runs/training/' + start_str + '_' + end_str + '_' + strategy_name +'_plot_evaluations.png', dpi=300)

        # return
        parameters_training_all.append([stats_training._strategy.lower_bound, stats_training._strategy.upper_bound, stats_training._strategy.rsi_window])
        trades_training_all.append(trades)    
        stats_training_all.append(stats_training)
        
    return parameters_training_all, trades_training_all, stats_training_all

print('Training finished. Running out of sample.')
lookback_bars = int(len(data) / 5)
validation_bars = int(len(data) / 10)
parameters, trades_training, stats_training = walk_forward(
    Base_Strategy,
    data,
    lookback_bars=lookback_bars,
    validation_bars=validation_bars,
)
print('Finished.')

def walk_forward_live(
    strategy,
    data_full,
    lookback_bars,
    validation_bars,
    cash = 100,
    commission = 0.002/factor
    ):
    
            
    dates = [data_full.index[i+1] for i in range(lookback_bars, len(data_full) - validation_bars, validation_bars)]
    lower_bounds = [parameter[0] for parameter in parameters]
    upper_bounds = [parameter[1] for parameter in parameters]
    
    data_live = data_full.iloc[lookback_bars + 1 - parameters[0][2]:]
        
    class WF_Live(strategy):

        def init(self):
            rsi_windows = [parameter[2] for parameter in parameters]
            self.rsi0 =  self.I(ta.RSI, self.data.Close, rsi_windows[0])
            self.rsi1 =  self.I(ta.RSI, self.data.Close, rsi_windows[1])
            self.rsi2 =  self.I(ta.RSI, self.data.Close, rsi_windows[2])
            self.rsi3 =  self.I(ta.RSI, self.data.Close, rsi_windows[3])
            self.rsi4 =  self.I(ta.RSI, self.data.Close, rsi_windows[4])
            self.rsi5 =  self.I(ta.RSI, self.data.Close, rsi_windows[5])
            self.rsi6 =  self.I(ta.RSI, self.data.Close, rsi_windows[6])
            super().init()
            
        def next(self):
            
            if dates[0] <= self.data.index[-1]  < dates[1]:
                self.lower_bound = lower_bounds[0]
                self.upper_bound = upper_bounds[0]
                self.rsi = self.rsi0
            elif dates[1] <= self.data.index[-1]  < dates[2]:
                self.lower_bound = lower_bounds[1]
                self.upper_bound = upper_bounds[1]
                self.rsi = self.rsi1
            elif dates[2] <= self.data.index[-1]  < dates[3]:
                self.lower_bound = lower_bounds[2]
                self.upper_bound = upper_bounds[2]
                self.rsi = self.rsi2
            elif dates[3] <= self.data.index[-1]  < dates[4]:
                self.lower_bound = lower_bounds[3]
                self.upper_bound = upper_bounds[3]
                self.rsi = self.rsi3
            elif dates[4] <= self.data.index[-1]  < dates[5]:
                self.lower_bound = lower_bounds[4]
                self.upper_bound = upper_bounds[4]
                self.rsi = self.rsi4
            elif dates[5] <= self.data.index[-1]  < dates[6]:
                self.lower_bound = lower_bounds[5]
                self.upper_bound = upper_bounds[5]
                self.rsi = self.rsi5
            elif self.data.index[-1]  >= dates[6]:
                self.lower_bound = lower_bounds[6]
                self.upper_bound = upper_bounds[6]
                self.rsi = self.rsi6
            
            super().next()
            

    bt_live = Backtest(data_live, WF_Live, cash=100, commission=.002)
    stats_live = bt_live.run()

    trades = stats_live['_trades'].drop('ReturnPct', axis=1)
    trades.Size /= size
    trades.EntryPrice = round(trades.EntryPrice * factor,2)
    trades.ExitPrice = round(trades.ExitPrice * factor,2)
    trades.PnL = round(trades.PnL,2)
    trades.OneR = round(trades.OneR * factor,2)
    
    strategy_name = str(stats_live._strategy)
    bt_live.plot(filename='finished_runs/'+strategy_name+'_trades_plot', open_browser=False)
    with open(str('finished_runs/'+strategy_name)+'_summary.txt', 'w') as f:
        f.write(str(stats_live))
        
    # Export trades
    with open(str('finished_runs/'+strategy_name)+'_trades.txt', 'w') as f:
        f.write(trades.to_string())
        
    return trades, stats_live

trades, stats = walk_forward_live(
    Base_Strategy,
    data,
    lookback_bars=lookback_bars,
    validation_bars=validation_bars
)

def plot_period_graph(
    data,
    lookback_bars,
    validation_bars):
    
    ranges = list(range(lookback_bars, len(data) - validation_bars, validation_bars))
    
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

plot_period_graph(data,lookback_bars,validation_bars)
