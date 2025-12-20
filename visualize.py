import csv
import numpy as np
import matplotlib.pyplot as plt
import datetime

fileName = './2025-12-19-AAPL-Apple.csv'

rowCount = 0
with open(fileName, 'r', newline='') as file:
    rowCount = sum(1 for _ in file) - 1

with open(fileName, 'r', newline='') as file:
    csvreader = csv.DictReader(file)
    
    dates = np.empty(rowCount, dtype='datetime64[D]')
    marketCaps = np.empty(rowCount, dtype=np.float64)
    
    for row in csvreader:
        index = csvreader.line_num - 2
        
        dates[index] = np.datetime64(row['date'])
        marketCaps[index] = np.float64(row['market_cap'])
        
# print(dates)
# print(marketCaps)

fig, ax = plt.subplots(layout='constrained')
ax.plot(dates, marketCaps)
plt.show()