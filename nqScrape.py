import urllib2
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import argparse

def scrapeIncomeData(ticker):
	url = "https://www.nasdaq.com/symbol/%s/financials?query=income-statement"%(ticker)

	page = urllib2.urlopen(url).read()
	soup = BeautifulSoup(page, "html5lib")

	#get table
	try:
		genTable = soup.find('div', class_="genTable").table
		tableBody = genTable.find('tbody')
	except:
		print "Error: No Financial Data Found"
		return None

	#get dates
	pEndings = genTable.find('thead')
	dates = pEndings.tr.find_all('th')
	datesTxt = [ele.text.encode('utf-8').strip() for ele in dates]
	datesTxt.remove('Trend')

	#get headers
	headNames = []
	headers = tableBody.find_all('th')
	headNames = [ele.text.encode('utf-8').strip() for ele in headers]
	headNames.remove('Operating Expenses')

	#get rows
	rows = tableBody.find_all('tr')
	data = []
	for row in rows:
		cols = row.find_all('td')
		cols = [ele.text.encode('utf-8').strip() for ele in cols]
		for ele in cols:
			if ele or ele != '':
				data.append(ele)

	#pair headers with row data
	myDict = {}
	x = 0 
	for i in range(0, len(headNames)):
		row = []
		for j in range(0, 4):
			#4 items in each row, also get rid of $ and ,
			inputD = data[j+x].translate(None, '$,')
			if(inputD[0] == '(' and inputD[-1] == ')'):
				inputD = inputD.translate(None, '()')
				inputD = '-' + inputD
			row.append(inputD)
		myDict[headNames[i]] = row
		x = x + 4

	last = datesTxt.pop(0)
	myDict[last] = datesTxt

	return myDict

def scrapeBalanceSheet(ticker):
	url = "https://www.nasdaq.com/symbol/%s/financials?query=balance-sheet"%(ticker)

	page = urllib2.urlopen(url).read()
	soup = BeautifulSoup(page, "html5lib")

	#get table
	try:
		genTable = soup.find('div', class_="genTable").table
		tableBody = genTable.find('tbody')
	except:
		print "Error: No Financial Data Found"
		return None

	#get dates
	pEndings = genTable.find('thead')
	dates = pEndings.tr.find_all('th')
	datesTxt = [ele.text.encode('utf-8').strip() for ele in dates]
	datesTxt.remove('Trend')

	#get headers
	headNames = []
	headers = tableBody.find_all('th')
	headNames = [ele.text.encode('utf-8').strip() for ele in headers]
	omits = ["Current Assets", "Long-Term Assets", "Current Liabilities", "Stock Holders Equity"]
	for item in omits:
		headNames.remove(item)

	#get rows
	rows = tableBody.find_all('tr')
	data = []
	for row in rows:
		cols = row.find_all('td')
		cols = [ele.text.encode('utf-8').strip() for ele in cols]
		for ele in cols:
			if ele or ele != '':
				data.append(ele)

	#pair headers with row data
	myDict = {}
	x = 0 
	for i in range(0, len(headNames)):
		row = []
		for j in range(0, 4):
			#4 items in each row, also get rid of $ and ,
			inputD = data[j+x].translate(None, '$,')
			if(inputD[0] == '(' and inputD[-1] == ')'):
				inputD = inputD.translate(None, '()')
				inputD = '-' + inputD
			row.append(inputD)
		myDict[headNames[i]] = row
		x = x + 4

	last = datesTxt.pop(0)
	myDict[last] = datesTxt

	return myDict

def convertToDF(dictArg):
	#Pop period end dates for indexes
	rows = dictArg.pop('Period Ending:')
	dti = pd.to_datetime(rows) 			# dti: datetime index
	#Make chronological dataframe
	pData = pd.DataFrame(data = dictArg, dtype = 'int64', index = dti)
	pData = pData[::-1]
	return pData

def main():
	#Get command line arg
	argparser = argparse.ArgumentParser()
  	argparser.add_argument('ticker',help = 'Company stock symbol')
  	args = argparser.parse_args()
  	ticker = args.ticker
	plt.close('all')
	print "Gathering income data for %s..."%ticker
	incomeData = scrapeIncomeData(ticker)
	balanceSheet = scrapeBalanceSheet(ticker)

	if incomeData and balanceSheet:
		print "Values in 000's of dollars"
		fig, (ax1, ax2) = plt.subplots(nrows = 1, ncols = 2, figsize = (14,7))
	elif incomeData or balanceSheet:
		print "Values in 000's of dollars"
		fig, ax1 = plt.subplots(nrows = 1, ncols = 1, figsize = (8,4))
	else:
		print "Perhaps NASDAQ does not have this companies financial data on their website."
	
	#Make dataframes
	if incomeData:
		pDataI = convertToDF(incomeData)
		iGraph = pDataI[['Gross Profit', 'Total Revenue']]
		
		iGraph.plot(kind = "line", ax = ax1)
		ax1.set_title("%s Income Data"%ticker.upper())
		ax1.set_xlabel('Period End Date')
		ax1.set_ylabel("Dollars(in 000's)")
		#print "\nIncome Data:\n", pDataI
		'''
		plt.figure(0)		
		plt.plot(data = pDataI, kind='line', table=True)
		plt.title("%s Income Data"%ticker.upper())
		'''

	if balanceSheet:
		if not incomeData:
			ax2 = ax1

		pDataB = convertToDF(balanceSheet)
		bGraph = pDataB[['Total Assets', 'Total Liabilities', 'Total Equity']]

		bGraph.plot(kind = "line", ax = ax2)
		ax2.set_title("%s Balance Sheet"%ticker.upper())
		ax2.set_xlabel('Period End Date')
		ax2.set_ylabel("Dollars (in 000's)")
		#print "\nBalance Sheet\n", pDataB
		'''
		plt.figure(1)
		plt.plot(data = pDataB, kind='line', table=True)
		plt.title("%s Balance Sheet"%ticker.upper())
		'''
	plt.show()
	print fig, ax1, ax2
	print "\nGood Metrics:\n", iGraph, '\n', bGraph

main()
