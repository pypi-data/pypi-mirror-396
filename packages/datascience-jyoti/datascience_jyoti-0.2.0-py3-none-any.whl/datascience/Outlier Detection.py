import pandas as pd

# File paths
InputFileName = 'IP_DATA_CORE.csv'
OutputFileName = 'Retrieve_Router_Location.csv'
Base = 'C:/Users/JYOTI RAHATE/Downloads/DataScience'

print('Working Base:', Base)

# Full input file path
sFileName = Base + '/Inputfile/' + InputFileName
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

# Filter for London
LondonData = IP_DATA_ALL.loc[IP_DATA_ALL['Place_Name'] == 'London']
AllData = LondonData[['Country', 'Place_Name', 'Latitude']]
print('All Data:')
print(AllData)

# Compute mean and standard deviation by Country and Place_Name
MeanData = AllData.groupby(['Country', 'Place_Name'])['Latitude'].mean()
StdData = AllData.groupby(['Country', 'Place_Name'])['Latitude'].std()

# Detect outliers
print('Outliers:')

# Compute bounds
UpperBound = MeanData + StdData
LowerBound = MeanData - StdData

# Higher than upper bound
print('Higher than Upper Bound:')
OutliersHigher = AllData.join(UpperBound, on=['Country', 'Place_Name'], rsuffix='_mean')
OutliersHigher = OutliersHigher[OutliersHigher.Latitude > OutliersHigher.Latitude_mean]
print(OutliersHigher)

# Lower than lower bound
print('Lower than Lower Bound:')
OutliersLower = AllData.join(LowerBound, on=['Country', 'Place_Name'], rsuffix='_mean')
OutliersLower = OutliersLower[OutliersLower.Latitude < OutliersLower.Latitude_mean]
print(OutliersLower)

# Not outliers
print('Not Outliers:')
OutliersNot = AllData[
    (AllData.Latitude >= AllData.join(LowerBound, on=['Country','Place_Name'], rsuffix='_mean').Latitude_mean) &
    (AllData.Latitude <= AllData.join(UpperBound, on=['Country','Place_Name'], rsuffix='_mean').Latitude_mean)
]
print(OutliersNot)
