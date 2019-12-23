import os
import pickle


PICKLE_FILE = 'SensorData.pickle'


def main():
    # load & show all stored objects
    for item in read_from_pickle(PICKLE_FILE):
        print(item)


def read_from_pickle(path):
    with open(path, 'rb') as file:
        try:
            while True:
                yield pickle.load(file)
        except EOFError:
            pass


if __name__ == '__main__':
    main()