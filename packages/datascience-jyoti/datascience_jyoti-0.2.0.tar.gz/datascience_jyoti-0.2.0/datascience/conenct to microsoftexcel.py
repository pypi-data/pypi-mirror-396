import os
import pandas as pd
#pip install openpyxl
################################################################
Base = 'C:/Users/JYOTI RAHATE/Downloads/DataScience'
################################################################
sFileDir=Base + '/Outputfile' 
#if not os.path.exists(sFileDir):
#os.makedirs(sFileDir)
################################################################
CurrencyRawData = pd.read_excel('C:/Users/JYOTI RAHATE/Downloads/DataScience/Inputfile/Country_Currency.xlsx')
sColumns = ['Country or territory', 'Currency', 'ISO-4217']
CurrencyData = CurrencyRawData[sColumns]
CurrencyData.rename(columns={'Country or territory': 'Country', 'ISO-4217':
'CurrencyCode'}, inplace=True)
CurrencyData.dropna(subset=['Currency'],inplace=True)
CurrencyData['Country'] = CurrencyData['Country'].map(lambda x: x.strip())
CurrencyData['Currency'] = CurrencyData['Currency'].map(lambda x:
x.strip())
CurrencyData['CurrencyCode'] = CurrencyData['CurrencyCode'].map(lambda x:
x.strip())
print(CurrencyData)
print('~~~~~~ Data from Excel Sheet Retrived Successfully ~~~~~~~ ')
sFileName=sFileDir + '/Retrieve-Country-Currency.csv'
CurrencyData.to_csv(sFileName, index = False)
