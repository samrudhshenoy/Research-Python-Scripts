import struct
import matplotlib.pyplot as plt


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

    print("Now reading.")

    # Now, reopen the file for reading. This command will open the file
    # and return the file, the version, and the number of columns per row.
    inFile, version, numCols = openPackedFileForReading('Sensor_1.bin')

    print("The file is version %d, with each row having %d columns." % (version, numCols))

###############################################
    # Now read each row back in.
    row = []
    rowTemp = []
    x = []
    y = []
    while row is not None:
        # readPackedRow will return None at the end of the file

        row = readPackedRow(inFile, numCols)
        # print("Read back: ", row)

        if row is not None:
            rowTemp = row

        try:
            sensorSeq = row[35]
        except TypeError:
            sensorSeq = 0

        try:
            SNR = row[5]
        except TypeError:
            SNR = 0

        # x axis values
        x.extend([sensorSeq])
        # corresponding y axis values
        y.extend([SNR])

################################################
    print("Number of Rows: ", rowTemp[0])
    # plotting the points
    plt.scatter(x, y)

    # naming the x axis
    plt.xlabel('Sequence Number')
    # naming the y axis
    plt.ylabel('SNR')

    # giving a title to my graph
    plt.title('SNR vs Sequence Number')

    # function to show the plot
    plt.show()
################################################

    #     pickle_out = open("test.pickle", "wb")
    #     pickle.dump(row, pickle_out)
    #
    # pickle_out.close()
    inFile.close()