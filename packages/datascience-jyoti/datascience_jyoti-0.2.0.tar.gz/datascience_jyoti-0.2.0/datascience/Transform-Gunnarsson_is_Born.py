import sys
import os
from datetime import datetime
from pytz import timezone
import pandas as pd
import sqlite3 as sq
import uuid

pd.options.mode.chained_assignment = None

# -----------------------------------------
# Base Path
# -----------------------------------------
if sys.platform == 'linux':
    Base = os.path.expanduser('~') + '/VKHCG'
else:
    Base = 'C:/Users/JYOTI RAHATE/Downloads/DataScience'

print('Working Base :', Base, ' using ', sys.platform)

# -----------------------------------------
# Company & Input Details
# -----------------------------------------
#Company = '01-Vermeulen'
#InputDir = '00-RawData'
#InputFileName = 'VehicleData.csv'

# -----------------------------------------
# SQLite Database Folders
# -----------------------------------------
# 1. Transform DB
sDataBaseDir = Base + '/Outputfile'
os.makedirs(sDataBaseDir, exist_ok=True)
sDatabaseName_Transform = sDataBaseDir + '/Vermeulen1.db'
conn1 = sq.connect(sDatabaseName_Transform)

# 2. Data Vault DB
sDataVaultDir = Base + '/Outputfile'
os.makedirs(sDataVaultDir, exist_ok=True)
sDatabaseName_DV = sDataVaultDir + '/datavault.db'
conn2 = sq.connect(sDatabaseName_DV)

# 3. Data Warehouse DB
sDataWarehouseDir = Base + '/Outputfile'
os.makedirs(sDataWarehouseDir, exist_ok=True)
sDatabaseName_DW = sDataWarehouseDir + '/datawarehouse.db'
conn3 = sq.connect(sDatabaseName_DW)

# -----------------------------------------
# Time Category
# -----------------------------------------
print('Time Category')
print('UTC Time')

BirthDateUTC = datetime(1960, 12, 20, 10, 15, 0)
BirthDateZoneUTC = BirthDateUTC.replace(tzinfo=timezone('UTC'))
BirthDateZoneStr = BirthDateZoneUTC.strftime("%Y-%m-%d %H:%M:%S")
BirthDateZoneUTCStr = BirthDateZoneUTC.strftime("%Y-%m-%d %H:%M:%S (%Z) (%z)")

print(BirthDateZoneUTCStr)

print('Birth Date in Reykjavik :')
BirthZone = 'Atlantic/Reykjavik'
BirthDate = BirthDateZoneUTC.astimezone(timezone(BirthZone))
BirthDateStr = BirthDate.strftime("%Y-%m-%d %H:%M:%S (%Z) (%z)")
BirthDateLocal = BirthDate.strftime("%Y-%m-%d %H:%M:%S")

print(BirthDateStr)

# -----------------------------------------
# Create Time Hub & Satellite Records
# -----------------------------------------
IDZoneNumber = str(uuid.uuid4())
sDateTimeKey = BirthDateZoneStr.replace(' ', '-').replace(':', '-')

TimeLine = [
    ('ZoneBaseKey', ['UTC']),
    ('IDNumber', [IDZoneNumber]),
    ('DateTimeKey', [sDateTimeKey]),
    ('UTCDateTimeValue', [BirthDateZoneUTC]),
    ('Zone', [BirthZone]),
    ('DateTimeValue', [BirthDateStr])
]

TimeFrame = pd.DataFrame.from_dict(dict(TimeLine))

# Hub: Time
TimeHub = TimeFrame[['IDNumber', 'ZoneBaseKey', 'DateTimeKey', 'DateTimeValue']]
TimeHubIndex = TimeHub.set_index(['IDNumber'], inplace=False)

sTable = 'Hub-Time-Gunnarsson'
print('Storing :', sDatabaseName_DV, '\n Table:', sTable)
TimeHubIndex.to_sql(sTable, conn2, if_exists="replace")

sTable = 'Dim-Time-Gunnarsson'
TimeHubIndex.to_sql(sTable, conn3, if_exists="replace")

# Satellite: Time Zone Details
TimeSatellite = TimeFrame[['IDNumber', 'DateTimeKey', 'Zone', 'DateTimeValue']]
TimeSatelliteIndex = TimeSatellite.set_index(['IDNumber'], inplace=False)

BirthZoneFix = BirthZone.replace(' ', '-').replace('/', '-')

sTable = 'Satellite-Time-' + BirthZoneFix + '-Gunnarsson'
print('Storing :', sDatabaseName_DV, '\n Table:', sTable)
TimeSatelliteIndex.to_sql(sTable, conn2, if_exists="replace")

sTable = 'Dim-Time-' + BirthZoneFix + '-Gunnarsson'
TimeSatelliteIndex.to_sql(sTable, conn3, if_exists="replace")

# -----------------------------------------
# Person Category
# -----------------------------------------
print('Person Category')

FirstName = 'Guðmundur'
LastName = 'Gunnarsson'

print('Name:', FirstName, LastName)
print('Birth Date:', BirthDateLocal)
print('Birth Zone:', BirthZone)
print('UTC Birth Date:', BirthDateZoneStr)

IDPersonNumber = str(uuid.uuid4())

PersonLine = [
    ('IDNumber', [IDPersonNumber]),
    ('FirstName', [FirstName]),
    ('LastName', [LastName]),
    ('Zone', ['UTC']),
    ('DateTimeValue', [BirthDateZoneStr])
]

PersonFrame = pd.DataFrame.from_dict(dict(PersonLine))
PersonHub = PersonFrame.set_index(['IDNumber'], inplace=False)

sTable = 'Hub-Person-Gunnarsson'
print('Storing :', sDatabaseName_DV, '\n Table:', sTable)
PersonHub.to_sql(sTable, conn2, if_exists="replace")

sTable = 'Dim-Person-Gunnarsson'
PersonHub.to_sql(sTable, conn3, if_exists="replace")

print("\n### DONE! ###################")
