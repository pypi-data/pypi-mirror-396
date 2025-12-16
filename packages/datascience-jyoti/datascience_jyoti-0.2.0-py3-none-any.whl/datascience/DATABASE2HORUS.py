# Utility Start Database to HORUS =================================
# Standard Tools
#=============================================================
import pandas as pd
import sqlite3 as sq
conn = sq.connect("C:/Users/JYOTI RAHATE/Downloads/DataScience/Inputfile/utility.db")
sSQL='select * FROM Country_Code;'
InputData=pd.read_sql_query(sSQL, conn)
ProcessData=InputData
ProcessData.drop('ISO-2-CODE', axis=1,inplace=True)
ProcessData.drop('ISO-3-Code', axis=1,inplace=True)
ProcessData.rename(columns={'Country': 'CountryName'}, inplace=True)
ProcessData.rename(columns={'ISO-M49': 'CountryNumber'}, inplace=True)
ProcessData.set_index('CountryNumber', inplace=True)
ProcessData.sort_values('CountryName', axis=0, ascending=False, inplace=True)
print('Process Data Values =================================')
print(ProcessData)
print('=====================================================')
OutputData=ProcessData
sOutputFileName='C:/Users/JYOTI RAHATE/Downloads/DataScience/Outputfile/dbToCsvHORUS.csv'
OutputData.to_csv(sOutputFileName, index = False)
print('Database to HORUS - Done')

