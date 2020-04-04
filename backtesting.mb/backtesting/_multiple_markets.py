import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

## Multiple Markets Stats ##
def compute_stats(output):

    def _drawdown_duration_peaks(dd, index):
            # XXX: possible to vectorize any of this?
            durations = [np.nan] * len(dd)
            peaks = [np.nan] * len(dd)
            i = 0
            for j in range(1, len(dd)):
                if dd[j] == 0:
                    if dd[j - 1] != 0:
                        durations[j - 1] = index[j] - index[i]
                        peaks[j - 1] = dd[i:j].max()
                    i = j
            return pd.Series(durations), pd.Series(peaks)

    indy_r_multiples = [s._trade_data['R multiple'].dropna()for s in output]
    r_multiples = pd.concat(indy_r_multiples).sort_index()
    drawdown = np.maximum.accumulate(np.cumsum(r_multiples)) - np.cumsum(r_multiples)
    dd_dur, dd_peaks = _drawdown_duration_peaks(drawdown.dropna().values, drawdown.index)

    o = pd.Series()
    o.loc['Start'] = min([s.loc['Start'] for s in output])
    o.loc['End'] = max([s.loc['End'] for s in output])
    o.loc['Duration'] = o.loc['End'] - o.loc['Start']
    o.loc['# Trades'] = n_trades = r_multiples.count()
    o.loc['Win Rate [%]'] = win_rate = np.nan if not n_trades else (r_multiples > 0).sum() / n_trades * 100  # noqa: E5
    o.loc['Max. Trade Duration'] = max([s.loc['Max. Trade Duration'] for s in output])
    o.loc['Avg. Trade Duration'] = np.sum([s.loc['Avg. Trade Duration'] * s.loc['# Trades'] for s in output]) / n_trades
    o.loc['-'] = '----------'

    market_sytem_r = [s.loc['System R multiple'] for s in output]
    o.loc['Positive R markets [%]'] = sum(r > 0 for r in market_sytem_r) / len(output) * 100
    o.loc['Max Market R'] = max(market_sytem_r)
    o.loc['Min Market R'] = min(market_sytem_r)
    o.loc['Avg. Market R'] = np.mean(market_sytem_r)
    o.loc['Stdev Market R'] = np.std(market_sytem_r)
    o.loc['--'] = '----------'

    o.loc['System R multiple'] =  sum([s.loc['System R multiple'] for s in output])
    o.loc['R of longs'] =  sum([s.loc['R of longs'] for s in output])
    o.loc['R of shorts'] =  sum([s.loc['R of shorts'] for s in output])
    o.loc['R min'] =  min(r_multiples)
    o.loc['R max'] =  max(r_multiples)
    o.loc['R stdev'] =  np.std(r_multiples)
    o.loc['Mean R win'] =  r_multiples.agg(lambda x: x[x>0].mean())
    o.loc['Mean R loss'] =  r_multiples.agg(lambda x: x[x<0].mean())
    o.loc['Expectancy'] =  np.mean(r_multiples)
    o.loc['Expectunity'] =  np.mean(r_multiples) * n_trades / float((o.loc['End'] - o.loc['Start']).days / 365)
    o.loc['SQN'] =  np.mean(r_multiples) / np.std(r_multiples) * np.sqrt(n_trades)
    o.loc['SQN 100'] =  np.mean(r_multiples) / np.std(r_multiples) * 10
    o.loc['SQN /year'] =  np.mean(r_multiples) / np.std(r_multiples) * np.sqrt(n_trades / float((o.loc['End'] - o.loc['Start']).days / 365))
    o.loc['---'] = '----------'
    
    o.loc['Max. Drawdown R'] = max_dd = - drawdown.max()
    o.loc['Avg. Drawdown R'] = - dd_peaks.mean()
    o.loc['Max. Drawdown Duration'] = dd_dur.max()
    o.loc['Avg. Drawdown Duration'] = dd_dur.mean()
    o.loc['----'] = '----------'
    
    return o

##### Plotting ######
import matplotlib.ticker as mtick

def plot(output, files):

    mkt_name = ['_'.join(file.split('_')[1:3]) for file in files]

    market_r_multiples = [s._trade_data['R multiple'].dropna()for s in output]
    r_multiples_unsorted = pd.concat(market_r_multiples)
    r_multiples = r_multiples_unsorted.sort_index()
    r_multiples_separate = pd.concat(market_r_multiples, axis=1).sort_index()
    r_multiples_separate.columns = mkt_name
    sum_equity = pd.concat([s._trade_data['Equity'] - 10000 for s in output], axis=1).fillna(method='ffill').sum(axis=1)
    eq_pc = 100 * (sum_equity + 10000) / 10000
    
    trade_r_multiples = pd.concat([s._trade_r_multiples for s in output], axis=1)

    n_trades_active = trade_r_multiples.fillna(0).astype(bool).sum(axis=1)
    pc_markets_active = 100 * n_trades_active / len(mkt_name)

    mae = trade_r_multiples.min().rename('MAE')
    mfe = trade_r_multiples.max().rename('MFE')
    mae[mae > 0] = 0
    mfe[mfe < 0] = 0

    excursions = pd.concat([r_multiples_unsorted.reset_index(drop=True), mae.reset_index(drop=True), mfe.reset_index(drop=True)], axis=1)
    excursions.index = r_multiples_unsorted.index
    
    mae_pos = excursions[excursions['R multiple'] > 0].abs()
    mae_neg = excursions[excursions['R multiple'] < 0].abs()

    mfe_pos = excursions[excursions['R multiple'] > 0].abs()
    mfe_neg = excursions[excursions['R multiple'] < 0].abs()
    
    
    fig, ax = plt.subplots(6, sharex=True)
    fig.tight_layout()
    [a.set_ylabel('R') for a in ax]
    ax[0].set_ylabel('Equity')
    ax[0].yaxis.set_major_formatter(mtick.PercentFormatter())
    ax[0].set_title('Equity')
    ax[1].set_title('R multiple distribution')
    ax[2].set_title('Cumulative R multiple distribution (EOT)')
    ax[3].set_title('Market cumulative R multiple distribution (EOT)')
    ax[4].set_title('R multiple distributions within trades')
    ax[5].set_title('Percentage of markets active')
    ax[5].set_ylabel('Active Markets')
    #ax[5].yaxis.set_major_formatter(mtick.PercentFormatter()) # when pc_markets_active
    eq_pc.plot(ax=ax[0])
    r_multiples.plot(ax=ax[1], marker='o', linestyle='None')
    r_multiples.cumsum().plot(ax=ax[2], marker='o')
    r_multiples_separate.cumsum().interpolate(method='linear').plot(ax=ax[3], marker='o')
    trade_r_multiples.plot(ax=ax[4], marker='o', legend=False)
    n_trades_active.plot(ax=ax[5])

    fig2, ax2 = plt.subplots(2)
    fig2.tight_layout()
    ax2[0].set_title('MAE')
    ax2[1].set_title('MFE')
    line0 = mlines.Line2D([0, max(mae.abs())], [0, max(mae.abs())], c='k', ls='--')
    line1 = mlines.Line2D([0, max(mfe)], [0, max(mfe)], c='k', ls='--')
    ax2[0].add_line(line0)
    ax2[1].add_line(line1)
    mae_pos.plot.scatter(ax=ax2[0], x='MAE', y='R multiple', c='g')
    mae_neg.plot.scatter(ax=ax2[0], x='MAE', y='R multiple', c='r')
    mfe_pos.plot.scatter(ax=ax2[1], x='MFE', y='R multiple', c='g')
    mfe_neg.plot.scatter(ax=ax2[1], x='MFE', y='R multiple', c='r')
    
    return plt.show()

