import sys
import os
import pandas as pd
from math import radians, cos, sin, asin, sqrt

# Function to calculate haversine distance
def haversine(lon1, lat1, lon2, lat2, stype):
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    
    # Determine the radius of Earth based on the unit type
    r = 6371 if stype == 'km' else 3956
    
    # Calculate and return the distance
    return round(c * r, 3)

# File paths
sFileName = 'C:/Users/JYOTI RAHATE/Downloads/DataScience/Inputfile/IP_DATA_CORE.csv'
sFileDir = 'C:/Users/JYOTI RAHATE/Downloads/DataScience/Outputfile'

# Check if output directory exists; create if not
if not os.path.exists(sFileDir):
    os.makedirs(sFileDir)

# Load the CSV file
print('Loading:', sFileName)
IP_DATA_ALL = pd.read_csv(
    sFileName, 
    header=0, 
    low_memory=False,
    usecols=['Country', 'Place Name', 'Latitude', 'Longitude'],
    encoding="latin-1"
)

# Process the data
IP_DATA = IP_DATA_ALL.drop_duplicates()
IP_DATA.rename(columns={'Place Name': 'Place_Name'}, inplace=True)

# Prepare data for cross join
IP_DATA1 = IP_DATA.copy()
IP_DATA1.insert(0, 'K', 1)
IP_DATA2 = IP_DATA1.copy()

# Cross-join to calculate pairwise distances
IP_CROSS = pd.merge(left=IP_DATA2, right=IP_DATA1, on='K')
IP_CROSS.drop('K', axis=1, inplace=True)

# Rename columns for clarity
IP_CROSS.rename(columns={
    'Longitude_x': 'Longitude_from', 
    'Longitude_y': 'Longitude_to',
    'Latitude_x': 'Latitude_from', 
    'Latitude_y': 'Latitude_to', 
    'Place_Name_x': 'Place_Name_from', 
    'Place_Name_y': 'Place_Name_to', 
    'Country_x': 'Country_from', 
    'Country_y': 'Country_to'
}, inplace=True)

# Calculate distances in kilometers and miles
IP_CROSS['DistanceBetweenKilometers'] = IP_CROSS.apply(
    lambda row: haversine(
        row['Longitude_from'],
        row['Latitude_from'],
        row['Longitude_to'],
        row['Latitude_to'],
        'km'
    ), axis=1
)

IP_CROSS['DistanceBetweenMiles'] = IP_CROSS.apply(
    lambda row: haversine(
        row['Longitude_from'],
        row['Latitude_from'],
        row['Longitude_to'],
        row['Latitude_to'],
        'miles'
    ), axis=1
)

# Save the result to a CSV file
print('Saving results...')
sFileName2 = os.path.join(sFileDir, 'Retrieve_IP_RoutingvermmulaPLC.csv')
IP_CROSS.to_csv(sFileName2, index=False, encoding="latin-1")

print('### Done!! ############################################')
