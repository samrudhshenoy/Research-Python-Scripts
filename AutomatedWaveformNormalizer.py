import struct
import os.path

''' MODIFY THESE VARS TO FIT THE READ AND WRITE FOLDERS'''
read_path = ''
write_path = ''


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

    z = 1
    for root, dirs, files in os.walk(read_path):
        for file in files:
            if file.endswith(".bin"):
                fileName = os.path.join(root, file)

                # Now, reopen the file for reading. This command will open the file
                # and return the file, the version, and the number of columns per row.
                inFile, version, numCols = openPackedFileForReading(fileName)


                name_of_new_file = fileName + '_normalized'
                completeName = os.path.join(write_path, name_of_new_file + ".bin")
                file = openPackedFileForWriting(completeName, 1, 1280)

                row = []
                while row is not None:
                    row = readPackedRow(inFile, numCols)
                    if row is not None:
                        rowTemp = list(row)

                        # Gathers all waveform data
                        x = 0
                        waves = [0] * 512
                        while x < 512:
                            waves[x] = row[256 + x]
                            x += 1

                        # Gathers all peak/trough indices
                        x = 0
                        indices = [0] * 512
                        while x < 512:
                            indices[x] = row[767 + x]
                            x += 1

                        # Vertically repositions the waveform
                        x = 240
                        while x < 250:
                            if indices[x] == -1:
                                i = 0
                                x = waves[x]
                                while i < 512:
                                    waves[i] -= x
                                    i += 1
                                break
                            x += 1

                        # Scales the waveform
                        x = 250
                        while x < 265:
                            if indices[x] == 1:
                                i = 0
                                x = 1 / waves[x]
                                while i < 512:
                                    waves[i] *= x
                                    i += 1
                                break
                            x += 1

                        # Inserts the normalized waveform values
                        c = 0
                        while c < 512:
                            rowTemp[256 + c] = waves[c]

                        # Writes the entire new row
                        writePackedRow(file, numCols, rowTemp)

                inFile.close()
                file.close()
                z += 1

    print("Done Writing.")
