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
sDatabaseName_dw = sDataWarehouseDir + '/datawarehouse1.db'  # Input database
conn1 = sq.connect(sDatabaseName_dw)

sDatabaseName_dm = sDataWarehouseDir + '/datamart2.db'      # Output database
conn2 = sq.connect(sDatabaseName_dm)

# Load full Dim-BMI table
sTable = 'Dim-BMI'
print('Loading:', sDatabaseName_dw, 'Table:', sTable)

sSQL = "SELECT * FROM [Dim-BMI];"
PersonFrame0 = pd.read_sql_query(sSQL, conn1)

# Print first 10 rows of original data
print("\nOriginal Dim-BMI Data (first 10 rows):")
#print(PersonFrame0.head(5))

# Load filtered Dim-BMI table with CASE for Name
sSQL = """
SELECT 
    Height,
    Weight,
    Indicator,
    CASE Indicator
        WHEN 1 THEN 'Pip'
        WHEN 2 THEN 'Norman'
        WHEN 3 THEN 'Grant'
        ELSE 'Sam'
    END AS Name
FROM [Dim-BMI]
WHERE Indicator > 2
ORDER BY Height, Weight;
"""
PersonFrame1 = pd.read_sql_query(sSQL, conn1)

# Set index on Indicator
DimPerson = PersonFrame1
DimPersonIndex = DimPerson.set_index(['Indicator'], inplace=False)

# Store in datamart database
sTable = 'Dim-BMISecure'
print('Storing:', sDatabaseName_dm, 'Table:', sTable)
DimPersonIndex.to_sql(sTable, conn2, if_exists="replace")

# Load back and check
print('Loading back stored table...')
sSQL = "SELECT * FROM [Dim-BMISecure];"
PersonFrame2 = pd.read_sql_query(sSQL, conn2)

# Print first 10 rows of stored table
print("\nFiltered/Stored Dim-BMISecure Data (first 10 rows):")
print(PersonFrame2.head(5))

print('\nOriginal Data Set Rows:', PersonFrame0.shape[0])
print('Original Data Set Columns:', PersonFrame0.shape[1])
print('Filtered/Stored Data Set Rows:', PersonFrame2.shape[0])
print('Filtered/Stored Data Set Columns:', PersonFrame2.shape[1])

# Close connections
conn1.close()
conn2.close()
