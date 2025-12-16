import pandas as pd
sInputFileName='C:/Users/JYOTI RAHATE/Downloads/DataScience/Inputfile/Country_Code.csv'
InputData=pd.read_csv(sInputFileName,encoding="latin-1")
ProcessData=InputData
ProcessData.drop(['ISO-3-Code', 'ISO-2-CODE'], axis=1,inplace=True)
ProcessData.rename(columns={'ISO-M49': 'CountryNumber', 'Country': 'CountryName'},inplace=True)
ProcessData.set_index('CountryNumber', inplace=True)
ProcessData.sort_values('CountryName', axis=0, ascending=True, inplace=True)
print(ProcessData.head(10))
#Added bY jyoti
output_file = 'C:/Users/JYOTI RAHATE/Downloads/DataScience/Outputfile/CsvToCsvHORUS.csv'
ProcessData.to_csv(output_file, encoding='latin-1')

print("File saved to:", output_file)
