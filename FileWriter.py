import struct
import pickle
import numpy as np

fileName = 'Sensor_1.bin'

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

    pickle_out = open("SensorData.pickle", "wb")

    print("Now Reading.")

    # Now, reopen the file for reading. This command will open the file
    # and return the file, the version, and the number of columns per row.
    inFile, version, numCols = openPackedFileForReading(fileName)
    e = 0
    row = []
    while row is not None:
        row = readPackedRow(inFile, numCols)
        e += 1
    inFile.close()

    inFile, version, numCols = openPackedFileForReading(fileName)

    print("The file is version %d, with each row having %d columns." % (version, numCols))

###############################################
    # Now read each row back in.
    row = []
    finalResult = np.zeros(shape=(e - 1, 528))
    z = 0
    while row is not None:
        result = []

        row = readPackedRow(inFile, numCols)

        if row is None:
            break

        result.extend([row[1]])  # DBP
        result.extend([row[2]])  # SBP
        result.extend([row[3]])  # MAP
        result.extend([row[8]])  # HR(sensor)
        result.extend([row[36]])  # Timestamp
        result.extend([row[35]])  # SensorSeq
        result.extend([0])
        result.extend([0])
        result.extend([row[5]])  # SNR
        result.extend([row[6]])  # Correlation
        result.extend([row[9]])  # Quality Flag
        result.extend([0])
        result.extend([0])
        result.extend([0])
        result.extend([row[30]])  # QA Score
        result.extend([0])

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

        result.extend(waves)
        waveform = np.array(result)
        a = 0
        for i in waveform:
            finalResult[z, a] = i
            a += 1

        z += 1

    pickle.dump(finalResult, pickle_out)

################################################

    pickle_out.close()
    inFile.close()
    print("Done Writing.")
