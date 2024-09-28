#!/usr/bin/env python3.12

import pandas as pd
import numpy as np
from scraper import getDatFromSymbol
import datetime

import matplotlib.pyplot as plt

MARGIN = 1 # 1 percent

def getAvg(dat, period=200):

	nums = dat["Close"]
	nums = nums[0:period]

	return nums.sum() / period

def isKeeper(stock_dat, strategy):
	match strategy:
		case "DMA Proximity":
			avg_val = getAvg(stock_dat)
			current_val = stock_dat.iloc[0,3]

			margin = avg_val * MARGIN / 100
			lower = avg_val - margin
			upper = avg_val + margin

			if (current_val >= lower and current_val <= upper):
				return True
			return False

		case "Golden Cross":
			avg_val = getAvg(stock_dat)
			avg_val50 = getAvg(stock_dat, 50)
			current_val = stock_dat.iloc[0,4]

			if (current_val <= avg_val and avg_val50 >= avg_val):
				return True
			return False

		case "Linear Regression":
			stock_dat = stock_dat[::-1]
			dat_arr = np.array(stock_dat["Close"])

			num_entries = np.size(dat_arr, 0)

			lin_x = np.linspace(0, num_entries-1, num_entries)
			p = np.polyfit(lin_x, dat_arr, 1)
			lin_y = p[0]*lin_x + p[1]

			delta = lin_y - dat_arr
			sigma = np.std(delta)

			target = lin_y[-1] - sigma
			margin = target * MARGIN / 100
			current_val = dat_arr[-1]
			
			lower = target - margin
			upper = target + margin

			if (current_val >= lower and current_val <= upper and p[0] > 0):
				"""
				plt.plot(lin_x, dat_arr)
				plt.plot(lin_x, lin_y)
				plt.plot(lin_x, (lin_y-sigma))
				plt.plot(lin_x, (lin_y+sigma))
				plt.show()
				"""
				return p[0]
			return None

		case _:
			return False

# script start
stock_list = pd.read_csv("stocklist/stocks.csv")

# run through list
keepers_dma = []
keepers_lg = []
failures = []
for _, row in stock_list.iterrows():
	symbol = row['Symbol']
	print("Checking...", symbol)

	market = "none" if pd.isna(row['Market']) else row['Market']

	try:
		dat = getDatFromSymbol(symbol, market=market, span=1, offset=1)
		dat = dat[(dat.Close != "-")]
		dat = dat.apply(pd.to_numeric)
	except:
		print("Failed getting data for:", symbol)
		failures.append(symbol)

	try:
		if isKeeper(dat, strategy="DMA Proximity"):
			keepers_dma.append(row)
			
		m = isKeeper(dat, strategy="Linear Regression")
		if m is not None:
			row.append(round(m, 2))
			keepers_lg.append(row)
	except:
		print("Failed evaluating:", symbol)
		failures.append(symbol)

# configure output
output = pd.DataFrame(keepers)
timestamp = datetime.datetime.now().isoformat()

print("Failures: ", failures)

output.to_csv("output/picks_"+timestamp+".csv")