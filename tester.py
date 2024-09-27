import subprocess
from io import StringIO

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import time
import datetime

picks = pd.read_csv("test_picks.csv")

def getDatFromSymbol(symbol, market="none"):
	# end_time = str(int(time.time())) for present
	start_time = str(1662329616) # sep 4, 2022
	end_time = str(1725488016) # sep 4, 2024

	if (market == "none"):
		command = "curl 'https://query1.finance.yahoo.com/v7/finance/download/"+symbol+"?period1="+start_time+"&period2="+end_time+"&interval=1d&events=history&includeAdjustedClose=true'"
	else:
		command = "curl 'https://query1.finance.yahoo.com/v7/finance/download/"+symbol+"."+market+"?period1="+start_time+"&period2="+end_time+"&interval=1d&events=history&includeAdjustedClose=true'"

	process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)
	bytes_dat = process.stdout

	data_str = bytes_dat.decode('utf-8')
	df = pd.read_csv(StringIO(data_str))

	return df[::-1]

holds = 0
rel_rois = [] # ROIs relative to XSP
for _, row in picks.iterrows():

	symbol = row['Symbol']
	print(symbol)
	market = "none" if pd.isna(row['Market']) else row['Market']

	stock_dat = getDatFromSymbol(symbol, market)
	stock_dat = stock_dat[::-1]
	dat_arr = np.array(stock_dat['Close'])

	num_entries = np.size(dat_arr, 0)
	halfway = num_entries // 2

	## graphing stuff
	lin_x = np.linspace(0, halfway-1, halfway)
	p = np.polyfit(lin_x, dat_arr[0:halfway], 1)
	lin_y = p[0]*lin_x + p[1]
	sigma = np.std(dat_arr[0:halfway] - lin_y)

	lin_x = np.linspace(0, num_entries-1, num_entries)
	lin_y = p[0]*lin_x + p[1]

	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)

	ax.plot(lin_x, lin_y)
	ax.plot(lin_x, dat_arr)
	ax.plot(lin_x, lin_y+sigma)
	ax.plot(lin_x, lin_y-sigma)

	# back to non graphing stuff
	start_price = dat_arr[halfway]

	day = halfway
	delta = 1
	while delta > 0:
		if day == lin_x[-1]:
			break
		delta = lin_y[day] - dat_arr[day]
		day += 1
	if day == lin_x[-1]:
		print("Hold on", symbol)
		holds += 1
		ylims = ax.get_ylim()
		ax.vlines(halfway, ylims[0], ylims[1])
		plt.show()
		continue

	end_price = dat_arr[day]
	pick_gain = (end_price - start_price) / start_price * 100

	xsp_dat = getDatFromSymbol("XSP", "TO")
	xsp_dat = xsp_dat[::-1]
	xsp_dat = np.array(xsp_dat['Close'])
	xsp_gain = (xsp_dat[day] - xsp_dat[halfway]) / xsp_dat[halfway] * 100

	print("Pick Gain:", str(pick_gain)+"%")
	print("XSP Gain:", str(xsp_gain)+"%")
	print("Sell day:", stock_dat.iloc[day, 0])

	rel_gain = pick_gain - xsp_gain
	rel_rois.append(rel_gain)

	ylims = ax.get_ylim()
	ax.vlines([halfway, day], ylims[0], ylims[1])
	plt.show()

avg_rel_roi = np.average(rel_rois)
print("Average Relative Gain:", avg_rel_roi)
print("Num didn't sell:", holds)


