import sqlite3 as sq
import pandas as pd
import os

# -------------------------------------------------------
# Base path and database
# -------------------------------------------------------
Base = 'C:/Users/JYOTI RAHATE/Downloads/DataScience'
sDatabaseName = Base + '/Inputfile/vermeulen.db'

# Make sure the directory exists
os.makedirs(os.path.dirname(sDatabaseName), exist_ok=True)

# -------------------------------------------------------
# Load CSV file
# -------------------------------------------------------
sFileName = Base + '/Inputfile/Retrieve_IP_DATA.csv'
print('Loading CSV file:', sFileName)

IP_DATA_ALL_FIX = pd.read_csv(sFileName, header=0, low_memory=False)
IP_DATA_ALL_FIX.index.names = ['RowIDCSV']

# -------------------------------------------------------
# Store CSV data into SQLite table
# -------------------------------------------------------
sTable = 'IP_DATA_ALL'
print('Storing to database:', sDatabaseName, ' Table:', sTable)

# Connect to SQLite database (will create a new DB if it doesn't exist)
conn = sq.connect(sDatabaseName)

# Store the DataFrame into SQLite (replace if table exists)
IP_DATA_ALL_FIX.to_sql(sTable, conn, if_exists="replace", index=False)

# -------------------------------------------------------
# Verify by reading back from the SQLite table
# -------------------------------------------------------
print('Loading from database:', sDatabaseName, ' Table:', sTable)
TestData = pd.read_sql_query(f"SELECT * FROM {sTable};", conn)

# Display data values
print('## Data Values')
print(TestData.head())

# Display data profile
print('## Data Profile')
print('Rows :', TestData.shape[0])
print('Columns :', TestData.shape[1])

print('### Done!! ###############')

# Close the database connection
conn.close()


