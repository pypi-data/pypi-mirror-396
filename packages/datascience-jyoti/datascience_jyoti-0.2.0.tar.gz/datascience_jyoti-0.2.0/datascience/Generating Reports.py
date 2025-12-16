import sys
import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Disable chained assignment warnings
pd.options.mode.chained_assignment = None

# Set base directory
if sys.platform == 'linux':
    Base = os.path.expanduser('~') + '/VKHCG'
else:
    Base = 'C:/Users/JYOTI RAHATE/Downloads/DataScience'

# File paths
sInputFileName = 'Assess-Network-Routing-Customer.csv'
sOutputFileName1 = '/Outputfile/Report-Network-Routing-Customer.gml'
sOutputFileName2 = '/Outputfile/Report-Network-Routing-Customer.png'

Company = '01-Vermeulen'

sFileName = Base + '/Inputfile/'+ sInputFileName

# Read customer data (first 100 rows)
CustomerDataRaw = pd.read_csv(sFileName, header=0, low_memory=False, encoding="latin-1")
print(CustomerDataRaw.columns)
CustomerData = CustomerDataRaw.head(100)

# Create graph
G = nx.Graph()

# Add edges between customer countries
for i in range(CustomerData.shape[0]):
    for j in range(CustomerData.shape[0]):
        Node0 = CustomerData['Customer_Country_Name'][i]
        Node1 = CustomerData['Customer_Country_Name'][j]
        if Node0 != Node1:
            G.add_edge(Node0, Node1)

# Add edges from country -> place -> coordinates
for i in range(CustomerData.shape[0]):
    Node0 = CustomerData['Customer_Country_Name'][i]
    Node1 = CustomerData['Customer_Place_Name'][i] + '(' + CustomerData['Customer_Country_Name'][i] + ')'
    Node2 = '(' + "{:.9f}".format(CustomerData['Customer_Latitude'][i]) + ')(' + \
            "{:.9f}".format(CustomerData['Customer_Longitude'][i]) + ')'
    
    if Node0 != Node1:
        G.add_edge(Node0, Node1)
    if Node1 != Node2:
        G.add_edge(Node1, Node2)

# Write graph to GML file
sFileName = Base + sOutputFileName1
nx.write_gml(G, sFileName)

# Draw and save the graph as PNG
sFileName = Base + sOutputFileName2
plt.figure(figsize=(25, 25))
pos = nx.spectral_layout(G, dim=2)

nx.draw_networkx_nodes(G, pos, node_color='k', node_size=10, alpha=0.8)
nx.draw_networkx_edges(G, pos, edge_color='r', arrows=False, style='dashed')
nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif', font_color='b')

plt.axis('off')
plt.savefig(sFileName, dpi=600)
plt.show()
