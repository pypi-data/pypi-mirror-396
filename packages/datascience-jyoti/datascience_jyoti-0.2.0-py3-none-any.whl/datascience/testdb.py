import sqlite3

# Replace with your DB path
db_path = "C:/Users/JYOTI RAHATE/Downloads/DataScience/Inputfile/datawarehouse1.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Preview data from a table
cursor.execute("SELECT * FROM [Dim-BMI] LIMIT 5;")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
