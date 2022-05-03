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

# Princeton Instruments imports needed for lightfield control
from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import ExperimentSettings
from PrincetonInstruments.LightField.AddIns import DeviceType
from PrincetonInstruments.LightField.AddIns import SpectrometerSettings
from PrincetonInstruments.LightField.AddIns import CameraSettings

# GRBL and controller imports
import serial
import time
import numpy as np
import matplotlib.pyplot as plt

def pause(text = "Press Enter to continue..."):
    input(text)

class LightField():

    def experiment_completed(self, sender, event_args):
        print("...Acquisition Completed")
        acquireCompleted.Set()

    def InitializeFileParams(self):
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

class Microscope():

    def send_gcode(code, delay = None): # sends gcode commands as strings or list of strings
        if isinstance(code, str):
            print('Sending: ' + str(code))
            s.write(str.encode(str(code)+'\n'))
            grbl_out = s.readline() # Wait for grbl response with carriage return
            print(' : ' + str(grbl_out.strip()))
        elif isinstance(code, list):
            for item in code:
                print('Sending: ' + str(item))
                s.write(str.encode(str(item)+'\n'))
                grbl_out = s.readline() # Wait for grbl response with carriage return
                print(' : ' + str(grbl_out.strip()))
                if delay:
                    time.sleep(delay)
        else:
            print('Incorrect code format: please enter gcode as a string or list of strings.')
