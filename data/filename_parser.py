import os
import csv

files = os.listdir(path='.\BTCUSDT')
split = [file.split('_') for file in files]

join = ['_'.join([s[1], s[2]]) for s in split]
renamed_files = [j + '.csv' for j in join]

old_filenames = [os.path.join('.\BTCUSDT', file) for file in files]
new_filenames = [os.path.join('.\BTCUSDT', file) for file in renamed_files]

for i in range(len(files)):
    os.rename(old_filenames[i], new_filenames[i])
