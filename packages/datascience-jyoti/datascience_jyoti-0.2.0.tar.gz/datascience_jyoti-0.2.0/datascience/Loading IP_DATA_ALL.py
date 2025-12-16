import sys
import os
import pandas as pd

# Base directory
Base = 'C:/Users/JYOTI RAHATE/Downloads/DataScience'

# Input file path
sFileName = Base + '/Inputfile/IP_DATA_ALL.csv'
print('Loading :', sFileName)

# Read CSV file
IP_DATA_ALL = pd.read_csv(sFileName, header=0, low_memory=False, encoding="latin-1")

# Output directory
sFileDir = Base + '/Outputfile'
if not os.path.exists(sFileDir):
    os.makedirs(sFileDir)

# Display dataset info
print('Rows:', IP_DATA_ALL.shape[0])
print('Columns:', IP_DATA_ALL.shape[1])

# Show raw column names
print('### Raw Data Set ##################')
for col in IP_DATA_ALL.columns:
    print(col, type(col))

# Fix column names: remove leading/trailing spaces and replace spaces with dots
print('### Fixed Data Set ###################################')
IP_DATA_ALL_FIX = IP_DATA_ALL.copy()
for i in range(len(IP_DATA_ALL_FIX.columns)):
    cNameOld = IP_DATA_ALL_FIX.columns[i] + ' '
    cNameNew = cNameOld.strip().replace(" ", ".")
    IP_DATA_ALL_FIX.columns.values[i] = cNameNew
    print(IP_DATA_ALL_FIX.columns[i], type(IP_DATA_ALL_FIX.columns[i]))

# Add RowID as index
print('Fixed Data Set with ID')
IP_DATA_ALL_with_ID = IP_DATA_ALL_FIX.copy()
IP_DATA_ALL_with_ID.index.names = ['RowID']

# Save cleaned data to CSV
sFileName2 = sFileDir + '/Retrieve_IP_DATA.csv'
IP_DATA_ALL_with_ID.to_csv(sFileName2, index=True, encoding="latin-1")

print('### Done!! ###')
