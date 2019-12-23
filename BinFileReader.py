import struct


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

    inFile, version, numCols = openPackedFileForReading('left_radial_PAL_Artline.bin')
    print("The file is version %d, with each row having %d columns." % (version, numCols))

    row = []
    while row is not None:
        row = readPackedRow(inFile, numCols)
        print(row[200])
        print(row[201])
        print(row[202])
        print(row[203])
        print(row[204])
        print(row[205])
        print(row[206])



    inFile.close()