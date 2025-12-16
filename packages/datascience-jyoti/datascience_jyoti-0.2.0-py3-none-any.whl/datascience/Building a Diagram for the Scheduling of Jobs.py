import sys
import os
import pandas as pd

# Input and output file names
InputFileName = 'IP_DATA_CORE.csv'
OutputFileName = 'Retrieve_Router_Location.csv'

# Input file path
sFileName = 'C:/Users/JYOTI RAHATE/Downloads/DataScience/Inputfile/' + InputFileName
print('Loading:', sFileName)

# Load CSV with selected columns
IP_DATA_ALL = pd.read_csv(
    sFileName,
    header=0,
    low_memory=False,
    usecols=['Country', 'Place Name', 'Latitude', 'Longitude'],
    encoding="latin-1"
)

# Rename column for convenience
IP_DATA_ALL.rename(columns={'Place Name': 'Place_Name'}, inplace=True)

# Output directory
sFileDir = 'C:/Users/JYOTI RAHATE/Downloads/DataScience/Outputfile'
if not os.path.exists(sFileDir):
    os.makedirs(sFileDir)

# Remove duplicate rows
ROUTERLOC = IP_DATA_ALL.drop_duplicates(keep='first')
print('Rows:', ROUTERLOC.shape[0])
print('Columns:', ROUTERLOC.shape[1])

# Output file path
sFileName2 = os.path.join(sFileDir, OutputFileName)
ROUTERLOC.to_csv(sFileName2, index=False, encoding="latin-1")

print('### Done!! ############################################')
