import requests as rq
import bs4 as bs
import html5lib
from io import StringIO
from datetime import datetime

import pandas as pd
import numpy as np

def getDatFromSymbol(symbol, market=None, span=3, offset=0):
	comb_symbol = symbol if market == None else f"{symbol}.{market}"
	yr2unix = lambda yr: int(yr * 365.25 * 24 * 60 * 60)
	pages = []
	total = 3 * span

	for i in range(total):
		end_time = int(datetime.timestamp(datetime.now()) - yr2unix(offset + i/3))
		start_time = end_time - yr2unix(1/3)

		url = f"https://ca.finance.yahoo.com/quote/{comb_symbol}/history/?period1={start_time}&period2={end_time}&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
		headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}

		print(f"Fetching page {i+1} of {total}...")
		r = rq.get(url=url, headers=headers)
		soup = bs.BeautifulSoup(r.content, "html5lib")
		table = (pd.read_html(StringIO(str(soup.table)))[0])[:-1]

		pages.append(table)

	df = pd.concat(pages)
	df.rename(columns={"Close*": "Close"}, inplace=True)
	df.drop(columns=["Adj Close**", "Volume"], inplace=True)

	df.drop_duplicates(subset=['Date'], inplace=True)
	df.set_index("Date", inplace=True)

	return df
