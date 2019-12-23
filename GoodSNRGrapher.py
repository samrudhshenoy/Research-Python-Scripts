import struct
import matplotlib.pyplot as plt
import statistics


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
    x = 'Sensor_1.bin'
    inFile, version, numCols = openPackedFileForReading(x)

    print("File: " + x)

###############################################
    # Now read each row back in.
    row = []
    rowTemp = []
    x = []
    y = []
    SNRList = []

    limit = 1

    while row is not None and limit < 2:  #change limit < x to change the number of waves
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
            QA = row[30]
        except TypeError:
            QA = 0

        try:
            SNR = row[5]
        except TypeError:
            SNR = 0

        if abs(QA) - 1 <= 0 and SNR >= 10:

            print("QA: " + str(QA), ", SNR:" + str(SNR))

            try:
                SNRList.extend([row[5]])
            except TypeError:
                x = 0

            rows, cols = (3, 512)
            waveform = [[0] * cols] * rows
            x = 0
            temp = [0] * 512
            while x < 512:
                temp[x] = x + 1
                x += 1

            x = 0
            waves = [0] * 512
            while x < 512:
                waves[x] = row[256 + x]
                x += 1

            x = 0
            indices = [0] * 512
            while x < 512:
                indices[x] = row[767 + x]
                x += 1

            waveform[0] = temp
            waveform[1] = waves
            waveform[2] = indices

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

            x = 250
            while x < 265:
                if indices[x] == 1:
                    i = 0
                    x = 1/waves[x]
                    while i < 512:
                        waves[i] *= x
                        i += 1
                    break
                x += 1


            x = []
            y = []
            # x axis values
            x.extend(waveform[0])
            # corresponding y axis values
            y.extend(waveform[1])

            # plotting the points
            plt.plot(x, y)

            x = 0
            while x < 512:
                if indices[x] == -1 or indices[x] == 1:
                    plt.scatter(x + 1, waves[x], color='#FF0000')
                x += 1

            limit += 1


    # naming the x axis
    plt.xlabel('Time')
    # naming the y axis
    plt.ylabel('Cardiac Output')

    # giving a title to my graph
    if SNRList is not None:
        median = statistics.median(SNRList)
        plt.title("Cardiac Output v. Time")
    else:
        plt.title('Waveform')

    # function to show the plot
    plt.show()


    inFile.close()