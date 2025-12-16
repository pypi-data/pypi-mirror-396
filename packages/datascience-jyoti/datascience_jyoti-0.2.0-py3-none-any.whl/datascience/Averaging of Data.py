import pandas as pd

# File and base path
InputFileName = 'IP_DATA_CORE.csv'
OutputFileName = 'Retrieve_Router_Location.csv'
Base = 'C:/Users/JYOTI RAHATE/Downloads/DataScience'

print('Working Base :', Base)

# Full input file path
sFileName = Base + '/Inputfile/' + InputFileName
print('Loading :', sFileName)

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

# Select required columns
AllData = IP_DATA_ALL[['Country', 'Place_Name', 'Latitude']]
print("All Data:\n", AllData)

# Group by Country and Place_Name, compute mean Latitude
MeanData = AllData.groupby(['Country', 'Place_Name'])['Latitude'].mean()
print("Mean Latitude by Country and Place:\n", MeanData)

# Optional: save to CSV
sOutputFile = Base + '/Outputfile/' + OutputFileName
MeanData.to_csv(sOutputFile)
print('Saved processed data to:', sOutputFile)
