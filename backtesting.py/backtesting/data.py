"""Data and utilities for testing."""
import pandas as pd
import os
cwd = os.getcwd()
if 'home' in cwd:
    path = '/home/mblacklock/backtesting/'
else:
    path = 'D:/Documents/Backtesting/'


def _read_file(filename):
    from os.path import dirname, join
    
    
    data = pd.read_csv(path + filename,
                       usecols = [0,1,2,3,4,5],
                       names = ["Date","Open","High","Low","Close","Volume"])
    
    data["Date"] = pd.to_datetime(data["Date"], unit = "ms")
    data.set_index("Date", inplace=True)

    # Resample data to required bar size
    data = data.resample('1H').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    })

    # Interpolate to fill in NaN values
    data = data.interpolate()

    factor = 1_000_000
    data['Open'] /= factor
    data['High'] /= factor
    data['Low'] /= factor
    data['Close'] /= factor
    
    return data

BTCUSDT = _read_file('data/data_1min/BTCUSDT-1m-2017-08-2023-01.csv')