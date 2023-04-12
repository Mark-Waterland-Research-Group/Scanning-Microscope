# Import the .NET class library
import clr
#LATEST 23-9-21
# Import python sys module
import sys

# Import os module
import os, glob, string

# Import System.IO for saving and opening files
from System.IO import *
from System.Threading import AutoResetEvent
# Import c compatible List and String
from System import String
from System.Collections.Generic import List
import math
# config file save
import json

# Add needed dll references
sys.path.append(os.environ['LIGHTFIELD_ROOT'])
sys.path.append(os.environ['LIGHTFIELD_ROOT']+"\\AddInViews")
clr.AddReference('PrincetonInstruments.LightFieldViewV5')
clr.AddReference('PrincetonInstruments.LightField.AutomationV5')
clr.AddReference('PrincetonInstruments.LightFieldAddInSupportServices')

# PI imports
from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import ExperimentSettings
from PrincetonInstruments.LightField.AddIns import DeviceType
from PrincetonInstruments.LightField.AddIns import SpectrometerSettings
from PrincetonInstruments.LightField.AddIns import CameraSettings



class ScanningMicroscope:

    def __init__(self):
        # self.scanList = scanList
        pass

    def experiment_completed(sender, event_args):
        print("...Acquisition Completed")
        acquireCompleted.Set()

    def InitializeFileParams():
        # Set the base file name
        experiment.SetValue(
            ExperimentSettings.FileNameGenerationBaseFileName,
            Path.GetFileName(filename))

        # Option to Increment, set to false will not increment
        experiment.SetValue(
            ExperimentSettings.FileNameGenerationAttachIncrement,
            False)

        # Option to add date
        experiment.SetValue(
            ExperimentSettings.FileNameGenerationAttachDate,
            False)

        # Option to add time
        experiment.SetValue(
            ExperimentSettings.FileNameGenerationAttachTime,
            False)


    def AcquireAndLock(name):
        print("Acquiring...", end="")
        # name += "add values for map locations here"
        # experiment.SetValue(ExperimentSettings.FileNameGenerationBaseFileName, name)
        experiment.Acquire()
        acquireCompleted.WaitOne()



# '''LightField Section'''
LF = input('Boot LightField?')
if LF != 'no':
    auto = Automation(True, List[String]())

    experiment = auto.LightFieldApplication.Experiment
    acquireCompleted = AutoResetEvent(False)
    experiment.Load("Automation")
    experiment.ExperimentCompleted += experiment_completed

comPort = 'COM9'
filename = "CVD1line1"
motorSpeed = 500
basetravelpersecond = 20
travelTime = 2

s, currentPos, commandDict, commandList = initializeGRBL(motorSpeed, comPort)
