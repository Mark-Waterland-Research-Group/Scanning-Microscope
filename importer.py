import os
import csv
import numpy as np

def pause():
    input('---')

scriptDir = os.path.dirname(__file__)
dataDir = os.path.join(scriptDir, 'data')

files = [file for file in os.listdir(dataDir) if file.endswith('.csv')]


class UVVisData:

    def __init__(self, data):
        print('Processing UV-vis data')
        self.data = data
        self.process_data()
        # breakpoint()
        pause()

    def process_data(self):
        print(self.data)

        
    
class IRData:

    def __init__(self, data):
        print('Processing IR data')
        self.data = data
        self.process_data()

    def process_data(self):
        print(self.data)
        # breakpoint()
        pause()

class RamanData:

    def __init__(self, data):
        print('Processing Raman data')
        self.data = data
        self.process_data()

    def process_data(self):
        print(self.data)
        # breakpoint()
        pause()

class CSVImporter:

    subclassList = {
        'IR': IRData,
        'Raman': RamanData,
        'UVVis': UVVisData,
    }

    def __init__(self, dataDir):
        self.dataDir = dataDir
        self.fileList = [file for file in os.listdir(dataDir) if file.endswith('.csv')]
        self.dataDict = {}
        self.typeDict = {}

        self.import_files()
    
    def import_files(self):
        
        for file in self.fileList:
            data = []
            with open(os.path.join(self.dataDir, file), 'r') as csvfile:
                # data = f.read()
                datareader = csv.reader(csvfile, delimiter=',')
                for row in datareader:
                    data.append(row)
                # print(f.read())

            dataType = self.test_file_type(data)
            self.typeDict[file] = dataType


    def test_file_type(self, data: list):

        if data[0][0] == 'Wavelength':
            return 'Raman'
    
        elif data[0][0] == 'Wavelength (nm)':
            return 'UVVis'
        
        else:
            try:
                data = np.array(data).astype(float)
                return 'IR'
            
            except ValueError:
                return 'unknown'
    
    def send_to_subclass(self):

        for file, dataType in self.typeDict.items():
            self.dataDict[file] = self.subclassList[dataType](file)
        
        return self.dataDict



importer = CSVImporter(dataDir)
dataSet = importer.send_to_subclass()



