import pandas as pd
import xml.etree.ElementTree as ET

def xml2df(xml_data):
    root = ET.XML(xml_data) 
    all_records = []
    for i, child in enumerate(root):
        record = {}
        for subchild in child:
            record[subchild.tag] = subchild.text
        all_records.append(record)
    return pd.DataFrame(all_records)

sInputFileName='C:/Users/JYOTI RAHATE/Downloads/DataScience/Inputfile/Country_Code.xml'
InputData = open(sInputFileName).read()

print('Input Data Values ===================================')
print(InputData)
print('=====================================================')
ProcessDataXML=InputData
ProcessData=xml2df(ProcessDataXML)

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
sOutputFileName='C:/Users/JYOTI RAHATE/Downloads/DataScience/Outputfile/XMLtoCSVHORUS.csv'
OutputData.to_csv(sOutputFileName, index = False)
