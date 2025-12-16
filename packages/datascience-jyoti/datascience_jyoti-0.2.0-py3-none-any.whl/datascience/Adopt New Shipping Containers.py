import sys
import os
import pandas as pd

# ---------------------------------------

# File Names
# ---------------------------------------
ContainerFileName = 'Retrieve_Container.csv'
BoxFileName = 'Retrieve_Box.csv'
ProductFileName = 'Retrieve_Product.csv'
Base = 'C:/Users/JYOTI RAHATE/Downloads/DataScience'

print('Working Base :', Base, ' using ', sys.platform)

# Directory Path
sFileDir = Base + '/Outputfile'
if not os.path.exists(sFileDir):
    os.makedirs(sFileDir)

# ----------------------------------------------------------
# 1. CREATE CONTAINER DATA
# ----------------------------------------------------------
containerLength = range(1, 21)
containerWidth = range(1, 10)
containerHeight = range(1, 6)
containerStep = 1

c = 0
ContainerFrame = pd.DataFrame()

for l in containerLength:
    for w in containerWidth:
        for h in containerHeight:

            containerVolume = (l / containerStep) * (w / containerStep) * (h / containerStep)
            c += 1

            ContainerLine = {
                'ShipType': 'Container',
                'UnitNumber': 'C' + format(c, "06d"),
                'Length': round(l, 4),
                'Width': round(w, 4),
                'Height': round(h, 4),
                'ContainerVolume': round(containerVolume, 6)
            }

            ContainerRow = pd.DataFrame([ContainerLine])
            ContainerFrame = pd.concat([ContainerFrame, ContainerRow], ignore_index=True)

ContainerFrame.index.name = 'IDNumber'

print('################')
print('## Container')
print('################')
print('Rows :', ContainerFrame.shape[0])
print('Columns :', ContainerFrame.shape[1])

sFileContainerName = sFileDir + '/' + ContainerFileName
ContainerFrame.to_csv(sFileContainerName, index=False)


# ----------------------------------------------------------
# 2. CREATE BOX DATA
# ----------------------------------------------------------
boxLength = range(1, 21)
boxWidth = range(1, 21)
boxHeight = range(1, 21)
packThick = range(0, 6)
boxStep = 10

b = 0
BoxFrame = pd.DataFrame()

for l in boxLength:
    for w in boxWidth:
        for h in boxHeight:
            for t in packThick:

                boxVolume = round((l / boxStep) * (w / boxStep) * (h / boxStep), 6)
                productVolume = round(((l - t) / boxStep) *
                                      ((w - t) / boxStep) *
                                      ((h - t) / boxStep), 6)

                if productVolume > 0:
                    b += 1

                    BoxLine = {
                        'ShipType': 'Box',
                        'UnitNumber': 'B' + format(b, "06d"),
                        'Length': round(l / 10, 6),
                        'Width': round(w / 10, 6),
                        'Height': round(h / 10, 6),
                        'Thickness': round(t / 5, 6),
                        'BoxVolume': round(boxVolume, 9),
                        'ProductVolume': round(productVolume, 9)
                    }

                    BoxRow = pd.DataFrame([BoxLine])
                    BoxFrame = pd.concat([BoxFrame, BoxRow], ignore_index=True)

BoxFrame.index.name = 'IDNumber'

print('################')
print('## Box')
print('################')
print('Rows :', BoxFrame.shape[0])
print('Columns :', BoxFrame.shape[1])

sFileBoxName = sFileDir + '/' + BoxFileName
BoxFrame.to_csv(sFileBoxName, index=False)


# ----------------------------------------------------------
# 3. CREATE PRODUCT DATA
# ----------------------------------------------------------
productLength = range(1, 21)
productWidth = range(1, 21)
productHeight = range(1, 21)
productStep = 10

p = 0
ProductFrame = pd.DataFrame()

for l in productLength:
    for w in productWidth:
        for h in productHeight:

            productVolume = round((l / productStep) *
                                  (w / productStep) *
                                  (h / productStep), 6)

            if productVolume > 0:
                p += 1

                ProductLine = {
                    'ShipType': 'Product',
                    'UnitNumber': 'P' + format(p, "06d"),
                    'Length': round(l / 10, 6),
                    'Width': round(w / 10, 6),
                    'Height': round(h / 10, 6),
                    'ProductVolume': round(productVolume, 9)
                }

                ProductRow = pd.DataFrame([ProductLine])
                ProductFrame = pd.concat([ProductFrame, ProductRow], ignore_index=True)

ProductFrame.index.name = 'IDNumber'

print('################')
print('## Product')
print('################')
print('Rows :', ProductFrame.shape[0])
print('Columns :', ProductFrame.shape[1])

sFileProductName = sFileDir + '/' + ProductFileName
ProductFrame.to_csv(sFileProductName, index=False)

print('### Done!! ##############')
#The program automatically creates 3 datasets—containers, boxes,
#and products—with all dimension combinations and volume calculations,
#and saves them as CSV files for logistics/packing analysis.
#The first part of the code generates all possible container sizes based on:
#Length: 1 to 20 units
#Width: 1 to 9 units
#Height: 1 to 5 units
#Step size: 1
#Box Data Creation
#The second part generates various box sizes:
#Length: 1 to 20
#Width: 1 to 20
#Height: 1 to 20
#Packing thickness: 0 to 5
#Step size = 10 (so actual size = dimension / 10)
#Two types of volumes are calculated:
#BoxVolume → total volume
#ProductVolume → usable space after thickness
#If this value is > 0, the box is valid and stored
#Each box gets a unique ID (B000001, B000002, …)
#Product Data Creation
#The third part generates product dimensions:
#Length: 1 to 20
#Width: 1 to 20
#Height: 1 to 20
#Step size = 10
#Volume = (L/10) × (W/10) × (H/10)
#Each product gets a unique ID (P000001, P000002, …)
