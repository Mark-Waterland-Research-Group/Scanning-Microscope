import os
import time
import shutil

def grab_files(exportDir, fileDir, seriesName, waitDelay = 0.01, copy = True):
    files = []
    print('checking')

    files = [file for file in os.listdir(exportDir) if '{}'.format(seriesName) in file]
    csvFiles = [file for file in files if file.endswith('.csv')]
    dirList = [file for file in os.listdir(fileDir) if '{}'.format(seriesName) in file]
    time.sleep(waitDelay)

    for file in files:
        try:
            if file in dirList:
                # print('{} already in dir. Skipping.'.format(file))
                pass
            else:
                move_files(file, exportDir, fileDir, copy = copy)
                if file.endswith('.csv'):
                    print(file)

        except Exception as e:
            if len(csvFiles) > 1:
                continue
            print("permission error")
            print(e)
            time.sleep(waitDelay)
            waitDelay += 1
            return waitDelay

    # time.sleep(5)
    return waitDelay

def make_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def move_files(file, dirInitial, dirFinal, copy = None, filename = None):
    make_dir(dirFinal)
    if not filename:
        filename = file
    if copy == True:
        shutil.copyfile('{}/{}'.format(dirInitial, file), '{}/{}'.format(dirFinal, filename))
    else:
        shutil.move('{}/{}'.format(dirInitial, file),'{}/{}'.format(dirFinal, filename)) #

#p140
seriesName = "MEM1_MEA_f1_l2"
# seriesName = "qly3"
exportDir = r"C:\Users\sjbrooke\Documents\tempData"
fileDir = r"H:\PhD\Raman\2021\6-27-21 Resonance tuning"+"\{}".format(seriesName)
waitDelay = 0.01

make_dir(fileDir)
while True:
    waitDelay = grab_files(exportDir, fileDir, seriesName, waitDelay = waitDelay, copy = False)
    time.sleep(1)
