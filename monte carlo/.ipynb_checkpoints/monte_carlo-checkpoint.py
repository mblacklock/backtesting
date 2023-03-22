import pandas as pd

df = pd.read_csv('finished_runs/WF_Live_trades.txt', delimiter='\t')

print(df['PnL'])
