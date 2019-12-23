import struct
import pandas as pd
import xlrd as x
import os.path

'''
YW14
YW13
'''

ext = 'YW13'
read_path = '/Volumes/PyrAmes Ext/Stanford_NICU_Aline_PeakCentered_Synced_Upsampled_125hz/Left-Radial-PAL_YW13/Sensor_4.bin'
write_path = '/Volumes/PyrAmes Ext/Stanford_NICU_Aline_PeakCentered_Synced_Upsampled_125hz_withDemographics/Left-Radial-PAL_YW13'


def openPackedFileForWriting(fileName, version, numCols):
    ''' This opens the file, and writes two ints into the header.
        The two ints are version number and the number of columns per row.
    '''

    f = open(fileName, 'wb')  # Change 'w' to 'a' if you want to append to existing files
    b = struct.pack("<2i", version, numCols)
    f.write(b)

    return f


def openPackedFileForReading(fileName):
    ''' This opens the file, and writes two ints into the header.

        The two ints are version number and the number of columns per row.
    '''
    f = open(fileName, 'rb')
    version = struct.unpack('<i', f.read(4))[0]
    numCols = struct.unpack('<i', f.read(4))[0]

    return f, version, numCols


def writePackedRow(file, numCols, row):
    ''' Write a row to the file. This ONLY WRITES FLOATS.
    '''
    bytes = struct.pack('<%df' % (numCols,), *row)
    file.write(bytes)


def readPackedRow(file, numCols):
    b = file.read(numCols * 4)

    if len(b) > 0:
        row = struct.unpack_from('<%df' % (numCols,), b)
    else:
        row = None

    return row


######################################################################

if __name__ == "__main__":

    fileName = read_path

    # Now, reopen the file for reading. This command will open the file
    # and return the file, the version, and the number of columns per row.
    inFile, version, numCols = openPackedFileForReading(fileName)

    # Opens spreadsheet for reading
    wb = x.open_workbook('summary.xlsx')

    # Reads spreadsheet
    content = pd.read_excel('summary.xlsx')

    sheet = None
    for s in wb.sheets():
        sheet = s
        rows = sheet.nrows
        cols = sheet.ncols
        break

    # Retrieves all values from a certain column
    values = content['PyrAmes ID'].values

    # Searches those values for the patient ID
    index = 1
    for i in values:
        if i == ext:
            print('Successfully matched ID')
            break
        index += 1

    gender = sheet.cell_value(index, 22)
    gen = 0.0
    if gender == "M":
        gen = 1.0
    elif gender == "F":
        gen = 2.0

    try:
        age = float(sheet.cell_value(index, 15))
    except ValueError:
        age = 0.0

    try:
        height = float(sheet.cell_value(index, 17))
    except ValueError:
        height = 0.0

    try:
        weightFirst = float(sheet.cell_value(index, 18))
    except ValueError:
        weightFirst = 0.0

    try:
        weightFirstAline = float(sheet.cell_value(index, 19))
    except ValueError:
        weightFirstAline = 0.0

    # try:
    #     weightLast = float(sheet.cell_value(index, 13))
    # except ValueError:
    #     weightLast = 0.0

    alineLoc = 0.0
    sensorLoc = 0.0

    aline = sheet.cell_value(index, 5)
    if "UAC" in aline:
        alineLoc = 1.0
    elif "Radial PAL" in aline:
        alineLoc = 3.0
    elif "Posterior Tibial PAL" in aline:
        alineLoc = 4.0
    elif "Radial Artery" in aline:
        alineLoc = 5.0
    elif "Femoral" in aline:
        alineLoc = 6.0
    elif "Ulnar" in aline:
        alineLoc = 7.0
    elif "Axillary" in aline:
        alineLoc = 8.0
    elif "PAL" in aline:
        alineLoc = 2.0

    if "/" in aline:
        aline = "Multiple_Aline_Locations"
    elif len(aline) < 2:
        aline = "No_Listed_Aline_Location"

    aline = aline.replace(" ", "_")

    '''
    [200] Gender 
    [201] Age (in days)
    [202] Height (cm)
    [203] Weight (kg) on first day 
    [204] Weight (kg) on first day of aline placement 
    [205] Weight (kg) on last day
    [206] Aline locations: 1, 2, 3, 4, 5, 6, 7, 8 for UAC, PAL, Radial PAL, Posterior Tibial PAL, Radial Artery, Femoral Artery, Ulnar Artery and Axillary Artery.
    [207] Sensor location: 1, 2, 3 ,4 for left wrist, right wrist, left foot, right foot 
    '''


    completeName = os.path.join(write_path, aline + "_" + "Sensor_4.bin")
    file = openPackedFileForWriting(completeName, 1, 1280)

    row = []
    while row is not None:
        print(fileName)
        row = readPackedRow(inFile, numCols)
        if row is not None:
            rowTemp = list(row)
            rowTemp[40] = gen
            rowTemp[41] = age
            rowTemp[42] = height
            rowTemp[43] = weightFirst
            rowTemp[44] = weightFirstAline
            rowTemp[45] = 0.0
            rowTemp[46] = alineLoc
            writePackedRow(file, numCols, rowTemp)

    inFile.close()
    file.close()

    print("Done Writing.")
