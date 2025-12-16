import sys
import os
import pandas as pd
import sqlite3 as sq

# Determine Base directory based on platform
if sys.platform == 'linux':
    Base = os.path.expanduser('~') + '/VKHCG'
else:
     Base = 'C:/Users/JYOTI RAHATE/Downloads/DataScience'

print('Working Base:', Base, 'using', sys.platform)

Company = '01-Vermeulen'

# Data Warehouse directory
sDataWarehouseDir = Base + '/Inputfile'
if not os.path.exists(sDataWarehouseDir):
    os.makedirs(sDataWarehouseDir)

# Connect to databases
sDatabaseName_dw = sDataWarehouseDir + '/datawarehouse1.db'
conn1 = sq.connect(sDatabaseName_dw)

sDatabaseName_dm = sDataWarehouseDir + '/datamart1.db'
conn2 = sq.connect(sDatabaseName_dm)

# Load full Dim-BMI table from data warehouse
sTable = 'Dim-BMI'
print('Loading:', sDatabaseName_dw, 'Table:', sTable)

sSQL = "SELECT * FROM [Dim-BMI];"
PersonFrame0 = pd.read_sql_query(sSQL, conn1)

# Load filtered Dim-BMI table (Height > 1.5 and Indicator = 1)
sSQL = """
SELECT PersonID,
       Height,
       Weight,
       bmi,
       Indicator
FROM [Dim-BMI]
WHERE Height > 1.5 AND Indicator = 1
ORDER BY Height, Weight;
"""
PersonFrame1 = pd.read_sql_query(sSQL, conn1)

# Set index on PersonID
DimPerson = PersonFrame1
DimPersonIndex = DimPerson.set_index(['PersonID'], inplace=False)

# Store horizontal table in datamart
sTable = 'Dim-BMI-Horizontal'
print('Storing:', sDatabaseName_dm, 'Table:', sTable)
DimPersonIndex.to_sql(sTable, conn2, if_exists="replace")

# Load horizontal table from datamart
print('Loading:', sDatabaseName_dm, 'Table:', sTable)
sSQL = "SELECT * FROM [Dim-BMI-Horizontal];"
PersonFrame2 = pd.read_sql_query(sSQL, conn2)

# Print dataset info
print('Full Data Set (Rows):', PersonFrame0.shape[0])
print('Full Data Set (Columns):', PersonFrame0.shape[1])
print('Horizontal Data Set (Rows):', PersonFrame2.shape[0])
print('Horizontal Data Set (Columns):', PersonFrame2.shape[1])
