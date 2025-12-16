import sys
import os
import pandas as pd
import gzip as gz

# Input / Output configuration
InputFileName = 'IP_DATA_ALL.csv'
OutputFileName = 'Retrieve_Online_Visitor'
CompanyIn = '01-Vermeulen'
CompanyOut = '02-Krennwallner'

# Base path configuration
Base = 'C:/Users/JYOTI RAHATE/Downloads/DataScience'
print('################################')
print('Working Base :', Base, ' using ', sys.platform)
print('################################')


# Input file path
sFileName = os.path.join(Base, 'Inputfile', InputFileName)
print('Loading :', sFileName)

# Load CSV
IP_DATA_ALL = pd.read_csv(
    sFileName,
    header=0,
    low_memory=False,
    usecols=['Country', 'Place.Name', 'Latitude', 'Longitude', 'First.IP.Number', 'Last.IP.Number']
)

# Rename columns to remove spaces
IP_DATA_ALL.rename(columns={
    'Place.Name': 'Place_Name',
    'First.IP.Number': 'First_IP_Number',
    'Last.IP.Number': 'Last_IP_Number'
}, inplace=True)

# Output directory
sFileDir = os.path.join(Base, 'Outputfile')
if not os.path.exists(sFileDir):
    os.makedirs(sFileDir)

# Remove duplicates
visitordata = IP_DATA_ALL.drop_duplicates()
visitordata10 = visitordata.head(10)

# Print basic info
print('Rows :', visitordata.shape[0])
print('Columns :', visitordata.shape[1])

# Export CSV
print('Export CSV')
sFileName2 = os.path.join(sFileDir, OutputFileName + '.csv')
visitordata.to_csv(sFileName2, index=False)
print('Store All:', sFileName2)

sFileName3 = os.path.join(sFileDir, OutputFileName + '_10.csv')
visitordata10.to_csv(sFileName3, index=False)
print('Store 10:', sFileName3)

# Export CSV with compression
for z in ['gzip', 'bz2', 'xz']:
    if z == 'gzip':
        sFileName4 = sFileName2 + '.gz'
    else:
        sFileName4 = sFileName2 + '.' + z
    visitordata.to_csv(sFileName4, index=False, compression=z)
    print('Store :', sFileName4)

# Export JSON
print('Export JSON')
for sOrient in ['split', 'records', 'index', 'columns', 'values', 'table']:
    sFileName2 = os.path.join(sFileDir, OutputFileName + '_' + sOrient + '.json')
    visitordata.to_json(sFileName2, orient=sOrient, force_ascii=True)
    print('Store All:', sFileName2)

    sFileName3 = os.path.join(sFileDir, OutputFileName + '_10_' + sOrient + '.json')
    visitordata10.to_json(sFileName3, orient=sOrient, force_ascii=True)
    print('Store 10:', sFileName3)

    # GZIP JSON
    sFileName4 = sFileName2 + '.gz'
    with open(sFileName2, 'rb') as file_in:
        with gz.open(sFileName4, 'wb') as file_out:
            file_out.writelines(file_in)
    print('Store GZIP All:', sFileName4)

    # UnGZIP JSON
    sFileName5 = os.path.join(sFileDir, OutputFileName + '_' + sOrient + '_UnGZip.json')
    with gz.open(sFileName4, 'rb') as file_in:
        with open(sFileName5, 'wb') as file_out:
            file_out.writelines(file_in)
    print('Store UnGZIP All:', sFileName5)

print('### Done!! ############################################')
