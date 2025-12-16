import sys
import os
import pandas as pd
import xml.etree.ElementTree as ET


#Reading raw data (CSV)-IP_DATA_ALL.csv
#Cleaning the data: Before converting to XML, the code cleans the column names by removing or replacing characters that are not allowed in XML tags, such as:
#spaces " ",dots ".",colons ":"
#Converting data into XML format: The df2xml() function converts the DataFrame into an XML structure:
#Saving XML to a file
#Reading XML back into a DataFrame:The xml2df() function reads the XML file and reconstructs it into a DataFrame.
#Remove Duplicate Records:drop_duplicates()

#
# -------------------------------------------------------
# Convert DataFrame → XML
# -------------------------------------------------------
def df2xml(data):
    header = data.columns
    root = ET.Element('root')

    for row in range(data.shape[0]):
        entry = ET.SubElement(root, 'entry')

        for col in header:
            child = ET.SubElement(entry, col)
            val = data.at[row, col]

            child.text = 'n/a' if pd.isna(val) else str(val)

    return ET.tostring(root, encoding='utf-8')


# -------------------------------------------------------
# Convert XML → DataFrame
# -------------------------------------------------------
def xml2df(xml_data):
    root = ET.XML(xml_data)
    all_records = []

    for child in root:
        record = {}
        for subchild in child:
            record[subchild.tag] = subchild.text
        all_records.append(record)

    return pd.DataFrame(all_records)


# -------------------------------------------------------
# Main Program
# -------------------------------------------------------
InputFileName = 'IP_DATA_ALL.csv'
OutputFileName = 'Retrieve_Online_Visitor.xml'

# Base folder
if sys.platform == 'linux':
    Base = os.path.expanduser('~') + '/VKHCG'
else:
    Base = 'C:/Users/JYOTI RAHATE/Downloads/DataScience'

print('Working Base :', Base, ' using ', sys.platform)

# Input file
sFileName = Base + '/Inputfile/' + InputFileName
print('Loading :', sFileName)

# Read CSV
IP_DATA_ALL = pd.read_csv(sFileName, header=0, low_memory=False)

# -------------------------------
# FIX COLUMN NAMES FOR XML SAFETY
# -------------------------------
# Remove illegal XML characters
IP_DATA_ALL.columns = (
    IP_DATA_ALL.columns
    .str.replace(" ", "_", regex=False)
    .str.replace(".", "_", regex=False)
    .str.replace(":", "_", regex=False)
)

# Remove "Unnamed" auto-index columns if present
IP_DATA_ALL = IP_DATA_ALL.loc[:, ~IP_DATA_ALL.columns.str.contains("^Unnamed")]

# Output directory
sFileDir = Base + '/Outputfile'
if not os.path.exists(sFileDir):
    os.makedirs(sFileDir)

# Subset
visitordata = IP_DATA_ALL.head(10000)
print('Original Subset Data Frame')
print('Rows :', visitordata.shape[0])
print('Columns :', visitordata.shape[1])
print(visitordata)

# Export XML
print('Export XML')
sXML = df2xml(visitordata)

# Save XML file
sFileName = sFileDir + '/' + OutputFileName
with open(sFileName, 'wb') as file_out:
    file_out.write(sXML)

print('Store XML:', sFileName)

# Read XML
xml_data = open(sFileName, "r", encoding="utf-8").read()
unxmlrawdata = xml2df(xml_data)

print('Raw XML Data Frame')
print('Rows :', unxmlrawdata.shape[0])
print('Columns :', unxmlrawdata.shape[1])
print(unxmlrawdata)

# Deduplicate rows
unxmldata = unxmlrawdata.drop_duplicates(keep='first')

print('Deduplicated XML Data Frame')
print('Rows :', unxmldata.shape[0])
print('Columns :', unxmldata.shape[1])
print(unxmldata)
