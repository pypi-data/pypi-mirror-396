import sys
import os
import pandas as pd

# Input file path
sFileName = 'C:/Users/JYOTI RAHATE/Downloads/DataScience/Inputfile/IP_DATA_ALL.csv'
print('Loading :', sFileName)

# Read CSV file
IP_DATA_ALL = pd.read_csv(sFileName, header=0, low_memory=False, encoding="latin-1")

# Output directory
sFileDir = 'C:/Users/JYOTI RAHATE/Downloads/DataScience/Outputfile'
if not os.path.exists(sFileDir):
    os.makedirs(sFileDir)

# Display dataset information
print('Rows:', IP_DATA_ALL.shape[0])
print('Columns:', IP_DATA_ALL.shape[1])

print('### Raw Data Set ###')
for col in IP_DATA_ALL.columns:
    print(col, type(col))

# Fix column names: remove spaces and replace with dots
print('### Fixed Data Set ###')
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
sFileName2 = os.path.join(sFileDir, 'Retrieve_IP_DATA_ALL.csv')
IP_DATA_ALL_with_ID.to_csv(sFileName2, index=True, encoding="latin-1")

print('### Done!! ###')
