import pandas as pd

raw_dat = pd.read_csv("etfs_can.csv", delimiter=",", header=None)

clean_dat = pd.DataFrame()

raw_syms = raw_dat[0]
clean_syms = []
markets = []

for sym in raw_syms:
	pieces = sym.split('-')
	market = "TO" if pieces[-1] == "T" else pieces[-1]
	markets.append(market)
	del pieces[-1]
	clean_syms.append('-'.join(pieces))

clean_dat['Symbol'] = clean_syms
clean_dat['Market'] = markets
clean_dat['Name'] = raw_dat[1]

clean_dat.to_csv("stocks.csv", mode="a", header=False, index=False)