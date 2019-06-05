import urllib2
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from string import maketrans

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
	#print data, len(data)
	#print headNames, len(headNames)

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

def main():
	tick = "aapl"
	#plt.close('all')
	#print "Gathering income data for %s..."%tick
	incomeData = scrapeIncomeData(tick)
	#print "income data:", incomeData, len(incomeData.keys())
	balanceSheet = scrapeBalanceSheet(tick)
	#print "balance sheet:", balanceSheet, len(balanceSheet.keys())
	
	print "Values in 000's"

	#Pop period end dates for indexes
	rows = incomeData.pop('Period Ending:')
	dtii = pd.to_datetime(rows)

	#Make dataframes
	if incomeData:
		#Make chronological dataframe
		pDataI = pd.DataFrame(data = incomeData, dtype = 'int64', index = dtii)
		pDataI = pDataI[::-1]
		print pDataI

		plt.figure(1)		
		pDataI.plot(y = ["Gross Profit", "Total Revenue"],kind='line', table=True)
		plt.title("%s Income Data"%tick.upper())

	rows = balanceSheet.pop('Period Ending:')
	dtbi = pd.to_datetime(rows)

	if balanceSheet:
		#Make chronological dataframe
		pDataB = pd.DataFrame(data = balanceSheet, dtype = 'int64', index = dtbi)
		pDataB = pDataB[::-1]
		print pDataB

		plt.figure(2)
		pDataB.plot(y = ["Total Assets", "Total Liabilities", "Total Equity"],kind='line', table=True)
		plt.title("%s Balance Sheet"%tick.upper())
	plt.show()

main()
