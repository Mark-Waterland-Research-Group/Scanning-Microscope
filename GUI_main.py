import PySimpleGUI as sg
import numpy as np
import os
import json
import math

import tkinter as tk
from tkinter import ttk

def pause(text = '---'):
    input(text)
    

class Linescan:

    def __init__(self, config):
        self.__dict__ = {key: value for (key, value) in config.items()}
        pass
        

class MetaFile:

    def __init__(self):
        self.scriptDir = os.path.realpath(os.path.dirname(__file__))
        if 'microscope_config.json' in os.listdir(self.scriptDir):
            self.hasConfig = True
            self.__load_config_file()
        else:
            self.hasConfig = False

            self.__generate_config()
            self.__write_config_file()

    def query_mode(self):
        while True:
            mode = input('Please enter current microscope configuration: "image" or "raman"\n')
            if mode != 'image' and mode != 'raman':
                print('"{}" not recognised, please enter "image" or "raman"'.format(mode))
                continue
            return mode
            # break

    def __generate_config(self):
        self.__dict__ = {'scriptDir': self.scriptDir, 'hasConfig': True}
        microscope_mode = self.query_mode()

        self.instrument = {
            'microscope_mode': microscope_mode,
            'light_level': 255,
            'light_on': False,
            'current_position': [0, 0],
            'home_position' : [0, 0]
            # 'scan_type': 'linescan'
        }

        self.scan = {
            'scan_type': 'linescan',
            'scan_res': 1,
            'scan_len': 0,
            'acquisition_time': 1,
            'x_scan': [],
            'y_scan': [],
            'start_pos': None,
            'finish_pos': None,
            'linescanList': []
        }

        self.hasConfig = True

    def __write_config_file(self):
        filePath = os.path.join(self.scriptDir, 'microscope_config.json')

        with open(filePath, 'w') as jsonFile:
            json.dump(self.__dict__, jsonFile)
        print('Saved config')

    def __load_config_file(self):
        filePath = os.path.join(self.scriptDir, 'microscope_config.json')

        with open(filePath, 'r') as jsonFile:
            self.__dict__ = json.load(jsonFile)
        print('Loaded config')

    def _save_config(self, makeNew = False):
        if makeNew:
            self.__generate_config()
        self.__write_config_file()

class SimGUI:

    codeKeys = {'IMAGEMODE':'image mode', 'RAMANMODE':'raman mode'}
    deja = 'DejaVu Sans Mono'

    def __init__(self, configObject):
        self.microscopeFunctionDict = {
            'SUBMIT': self.parse_input,
            'LINESCAN': self.set_linescan_mode,
            'MAP': self.set_map_mode,
            'IMAGEMODE': self.imageMode,
            'RAMANMODE': self.ramanMode,
            'LIGHT': self.toggle_light,
            'LIGHTSL': self.lightOn,
            'STARTPOSBUT': self.set_start_pos,
            'STARTPOSIN': self.input_start_pos,
            'FINISHPOSBUT': self.set_finish_pos,
            'FINISHPOSIN': self.input_finish_pos,
            'SCANRESIN': self.set_scan_res,
            'ACQIN': self.set_acquisition_time,
            'SYMBOL_LEFT_ARROWHEAD': self.move_stage_left,
            'SYMBOL_RIGHT_ARROWHEAD': self.move_stage_right,
            'SYMBOL_UP_ARROWHEAD': self.move_stage_up,
            'SYMBOL_DOWN_ARROWHEAD': self.move_stage_down,
            'STEPIN': self.set_step_size,
            'STEPSL': self.set_step_size_slider,
            'SETHOME': self.set_home_position,
            'GOHOME': self.move_to_home_position,
            'CANCEL': self.cancel_overwrite,
            'OVERWRITE': self.confirm_overwrite,
            'READY': self.run_scan,
            'SCANRES': self.do_nothing,
            'ACQUISITIONTIME': self.do_nothing
            # SCANRES: 
            # ACQUISITIONTIME: 
            
        }

        # Status flags
        self.startPos = False
        self.finishPos = False
        self.time = True
        self.scanRes = True

        # actual scan length
        self.scanLen = Config.scan['scan_len']
        self.config = configObject

        instrumentConfig = self.config.instrument
        scanConfig = self.config.scan

        for key, item in instrumentConfig.items():
            self.__dict__[key] = item
        for key, item in scanConfig.items():
            self.__dict__[key] = item


        # self.linescan = Linescan(self.config.scan)


        self.window = self.__construct_UI()


    '''
    --------------------------------
    Microscope functions
    --------------------------------
    '''
    def do_nothing(self):
        pass
    def run_scan(self):

        pass
    def move_to_position(self, position):
        print('NOCOM: Moving to position {}'.format(position))
    def set_home_position(self):
        Config.instrument['home_position'] = Config.instrument['current_position']
    def move_to_home_position(self):
        self.move_to_position(Config.instrument['home_position'])
    def move_stage_left(self):
        print('NOCOM: Moving stage x+{}'.format(self.stepSize))
    def move_stage_right(self):
        print('NOCOM: Moving stage +-{}'.format(self.stepSize))
    def move_stage_up(self):
        print('NOCOM: Moving stage y-{}'.format(self.stepSize))
    def move_stage_down(self):
        print('NOCOM: Moving stage y+{}'.format(self.stepSize))

    def set_step_size(self):
        '''Sets the motion step size from the step size input textbox'''
        stepSize = self.values['STEPIN'].strip(' ')
        try:
            stepSize = float(stepSize)
            if stepSize < 0.05:
                print("Step size is too small (though I'm flattered you think the stage can do it)\nPlease enter a step size between 0.05 and 5000 microns")
                return
            if stepSize > 5000:
                print("Step size is too big!\nPlease enter a step size between 0.05 and 5000 microns")
            else:
                self.window['STEP'].update(stepSize)
                self.window['STEPSL'].update(stepSize)
                self.stepSize = stepSize
        except:
            pass

    def set_step_size_slider(self):
        '''Sets the step size read from the slider'''
        stepSize = int(self.values['STEPSL'])
        self.window['STEP'].update(int(stepSize))
        self.window['STEPIN'].update(int(stepSize))
    
    def cancel_overwrite(self):
        '''Cancels the override warning box and returns to normal use'''
        self.window['MODE_CHECK'].update(visible = False)
        self.window['CANCEL'].update(visible = False)
        self.window['OVERWRITE'].update(visible = False)
        print('Aborting mode change, staying in {}'.format(Config.instrument['microscope_mode']))

    def confirm_overwrite(self):
        '''Checks the microcope mode and changes it to the opposide type. This will be redundnat if I can put some sensors in to detect mode configuration.'''
        print('Overwriting current mode...')
        if Config.instrument['microscope_mode'] == 'IMAGEMODE':
            Config.instrument['microscope_mode'] = 'RAMANMODE'
            self.imageMode()
        else:
            Config.instrument['microscope_mode'] = 'IMAGEMODE'
            self.ramanMode()

        self.window['MODE_CHECK'].update(visible = False)
        self.window['CANCEL'].update(visible = False)
        self.window['OVERWRITE'].update(visible = False)

    def set_scan_res(self):
        '''Sets the scan resolution from the scan resolution input textbox'''
        scanRes = self.values['SCANRESIN'].strip(' ')
        try:
            scanRes = float(scanRes)
        except:
            self.scanRes = False # flag for identifying changes later
            return
        
        if scanRes != 0:
            self.scanRes = True # flag for identifying changes later
            self.scan_change = True # flag for identifying changes later
        self.window['SCANRESVAL'].update('{} um'.format(scanRes))
        Config.scan['scan_res'] = scanRes

    def set_acquisition_time(self):
        '''Sets the acquisition time per scan point from the acquisition time input textbox'''
        aqTime = self.values['ACQIN'].strip(' ')
        try:
            aqTime = float(aqTime)
        except:
            # Config.scan['acquisition_time'] = None
            self.time = False # flag for identifying changes later
            return
        
        if aqTime == 0:
            self.time = False
            return
        
        self.time = True # flag for identifying changes later
        self.window['ACQVAL'].update('{} second(s)'.format(aqTime))
        Config.scan['acquisition_time'] = aqTime

    def set_start_pos(self):
        '''Sets the start position as the current position'''
        currentPos = Config.instrument['current_position']
        if currentPos == Config.scan['start_pos']:
            return # returns if position is unchanged
        
        self.window['STARTPOSIN'].update(','.join([str(x) for x in currentPos]))
        self.window['STARTPOSVAL'].update(','.join([str(x) for x in currentPos]))

        Config.scan['start_pos'] = currentPos
        self.startPos = True # flag for identifying changes later
        self.scan_change = True # flag for identifying changes later
    
    def set_finish_pos(self):
        '''Sets the finish position as the current position'''
        currentPos = Config.instrument['current_position']
        if currentPos == Config.scan['finish_pos']:
            return # returns if position is unchanged
        
        self.window['FINISHPOSIN'].update(','.join([str(x) for x in currentPos]))
        self.window['FINISHPOSVAL'].update(','.join([str(x) for x in currentPos]))

        Config.scan['finish_pos'] = currentPos
        self.finishPos = True # flag for identifying changes later
        self.scan_change = True # flag for identifying changes later

    
    def input_start_pos(self):
        '''Parses the input text from the start position textbox'''
        pos = self.values['STARTPOSIN'].split(',')
        try:
            x = float(pos[0].strip(' '))
            y = float(pos[1].strip(' '))
        except Exception as e:
            print(e)
            self.startPos = False # flag for identifying changes later
            self.window['RUNTIME'].update('Estimated runtime:\nN/A', background_color='red')
            self.window['SCANLEN'].update('Array size: \nN/A', background_color = 'red')
            return
        startPos = (x, y)
        if startPos == Config.scan['start_pos']:
            return
        
        self.window['STARTPOSVAL'].update(','.join([str(x) for x in startPos]))
        Config.scan['start_pos'] = startPos

        self.startPos = True # flag for identifying changes later
        self.scan_change = True # flag for identifying changes later


    def input_finish_pos(self):
        '''Parses the input text from the finish position textbox'''
        pos = self.values['FINISHPOSIN'].split(',')
        try:
            x = float(pos[0].strip(' '))
            y = float(pos[1].strip(' '))
        except Exception as e:
            print(e)
            self.finishPos = False # flag for identifying changes later
            self.window['RUNTIME'].update('Estimated runtime:\nN/A', background_color='red')
            self.window['SCANLEN'].update('Array size: \nN/A', background_color = 'red')
            return
        finishPos = (x, y)
        if finishPos == Config.scan['start_pos']:
            return
        
        self.window['FINISHPOSVAL'].update(','.join([str(x) for x in finishPos]))
        Config.scan['finish_pos'] = finishPos

        self.finishPos = True # flag for identifying changes later
        self.scan_change = True # flag for identifying changes later

    def set_linescan_mode(self):
        '''Sets the scan mode to linescan'''
        Config.scan['scan_type'] = 'linescan'
        print('Scan mode: linescan')
        self.scan_change = True # flag for identifying changes later

    def set_map_mode(self):
       '''Sets the scan mode to map'''
       Config.scan['scan_type'] = 'map'
       print('Scan mode: map')
       self.scan_change = True # flag for identifying changes later
   
    def toggle_light(self):
        '''Toggles the illumination source'''
        # Config.instrument['light_on'] = not Config.instrument['light_on']
        # light = Config.instrument['light_level']
        if Config.instrument['light_on']:
            self.lightOff()
        else:
            self.lightOn()

    def lightOn(self, val = None):
        '''Turns the illumination light source on, or changes it to a different brightness level'''
        if not val:
            val = self.values['LIGHTSL']
        
        self.window['LIGHTSL'].update(value=val)
        Config.instrument['light_level'] = val
        self.window['LIGHT'].update(text='ON', button_color='white on green')
        Config.instrument['light_on'] = True
        print('Turning on light at {} power'.format(val))

    def lightOff(self):
        '''Turns the illumination light source off'''
        self.window['LIGHT'].update(text='OFF', button_color='white on grey')
        Config.instrument['light_on'] = False
        print('Light:0')

    
    def print_response(self, a = 'a', b = 'b', c = 'c'):
        '''dummy function for printing the response of inputs'''

        print(a)
        print(b)
        print(c)
    
    def warn_already_in_mode(self):
        self.window['MODE_CHECK'].update('Alread in {} - are you sure you want to ovewrite?'.format(Config.instrument['microscope_mode']), visible = True)
        self.window['CANCEL'].update(visible = True)
        self.window['OVERWRITE'].update(visible = True)

    def ramanMode(self):
        '''Switches the microscope into Raman Mode'''
        if self.event == Config.instrument['microscope_mode']:
            self.warn_already_in_mode()
            return
        print('NOCOM: Switching to Raman mode')
        Config.instrument['microscope_mode'] = 'RAMANMODE'
        self.lightOff()
        print('Switching complete - Ready for Raman')

    def imageMode(self):
        '''Switches the microcope into Image Mode'''
        if self.event == Config.instrument['microscope_mode']:
            self.warn_already_in_mode()
            return
        print('NOCOM: Switching to Image mode')
        print('Switching complete - Ready for imaging')
        Config.instrument['microscope_mode'] = 'IMAGEMODE'
        self.lightOn()

    def switch_mode(self):
        '''Changes to the opposide microscope mode. Possibly redundant.'''
        if self.microMode == 'RAMANMODE':
            self.imageMode()
        elif self.microMode == 'IMAGEMODE':
            self.ramanMode()

    def overwrite_mode(self):
        if Config.instrument['microscope_mode'] == 'RAMANMODE':
            Config.instrument['microcsope_mode'] = 'IMAGEMODE'
            self.window['IMAGEMODE'].update(default=True)
            self.ramanMode()
        elif Config.instrument['microscope_mode']  == 'IMAGEMODE':
            Config.instrument['microcsope_mode'] = 'RAMANMODE'
            self.window['IMAGEMODE'].update(default=True)
            self.imageMode()
        
        # returns window to normal status
        self.window['MODE_CHECK'].update(visible = False)
        self.window['CANCEL'].update(visible = False)
        self.window['OVERWRITE'].update(visible = False)

    '''
    --------------------------------
    UI functions
    --------------------------------
    '''

    def __construct_UI(self):

        theme_dict = {'BACKGROUND': '#2B475D',
                        'TEXT': '#FFFFFF',
                        'INPUT': '#F2EFE8',
                        'TEXT_INPUT': '#000000',
                        'SCROLL': '#F2EFE8',
                        'BUTTON': ('#000000', '#C2D4D8'),
                        'PROGRESS': ('#FFFFFF', '#C7D5E0'),
                        'BORDER': 1,'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0}

        sg.LOOK_AND_FEEL_TABLE['Dashboard'] = theme_dict
        sg.theme('Dashboard')

        BORDER_COLOR = '#C7D5E0'
        DARK_HEADER_COLOR = '#1B2838'
        BPAD_TOP = ((20,20), (20, 10))
        BPAD_LEFT = ((20,10), (0, 10))
        BPAD_LEFT_INSIDE = (0, 10)
        BPAD_LEFT_MID = (5, 0)
        BPAD_RIGHT = ((10,20), (10, 20))
        BPAD_RIGHT_INSIDE = (0, 5)
        stepSize = 10

        top_banner = [[sg.Text('Here we put title', font='Any 20', background_color = DARK_HEADER_COLOR)]]


        block_cmd = [[sg.T('Enter commands', font='Any 12', key = 'COM')],
                    [sg.Input(key = 'COMIN'), sg.Button('<Enter>', bind_return_key = True, enable_events=True, key = 'SUBMIT')]]


        block_control = [[sg.Text('Controls', font='Any 12')],
                    [sg.Radio('Linescan', 'scanType', enable_events=True, key = 'LINESCAN', default = (False if self.scan_type == 'map' else True)), sg.Radio('Map', group_id='scanType', enable_events=True, key='MAP', default = (True if self.scan_type == 'map' else False)), sg.Radio('Image mode', group_id='microMode', enable_events=True, key='IMAGEMODE', default = (True if self.microscope_mode == 'image' else False)), sg.Radio('Raman mode', group_id='microMode', enable_events=True, key='RAMANMODE', default = (True if self.microscope_mode == 'raman' else False))],
                    [sg.T('Alread in {} mode - are you sure you want to ovewrite?'.format(self.microscope_mode), visible = False, key = 'MODE_CHECK')],
                    [sg.Button('Cancel', visible = False, key = 'CANCEL'), sg.Button('OVERWRITE', visible = False, key = 'OVERWRITE')]]

        block_left = [[sg.T('Illumination'), sg.Button('OFF', size = (3,1), button_color   ='white on grey', key='LIGHT', border_width=0), sg.Slider(range = (0, 255), disable_number_display = True, size=(15,15), key='LIGHTSL', default_value=255, resolution=1,enable_events=True,orientation='h')],
                    [sg.Button('Set Start Position', size = (10,2), key = "STARTPOSBUT", enable_events=True, visible = True), sg.In('', size = (6,2), key = 'STARTPOSIN', enable_events=True), sg.T('', expand_x=False, size = (13, 1), key = 'STARTPOSVAL', relief = 'flat', text_color = 'white', background_color='black', border_width = 1, justification = 'right')],
                    [sg.Button('Set Finish Position', size = (10,2), key = "FINISHPOSBUT", enable_events=True, visible = True), sg.In('', size = (6,2), key = 'FINISHPOSIN', enable_events=True), sg.T('', expand_x=False, size = (13, 1), key = 'FINISHPOSVAL', relief = 'flat', text_color = 'white', background_color='black', border_width = 1, justification = 'right')],
                    [sg.Button('Resolution', size = (10,1), key = "SCANRES", visible = True), sg.In('1', size = (6,2), key = 'SCANRESIN', enable_events=True), sg.T('1 micron', expand_x=False, size = (13, 1), key = 'SCANRESVAL', relief = 'flat', text_color = 'white', background_color='black', border_width = 1, justification = 'right')],
                    [sg.Button('Acquisition time', size = (10,2), key = "ACQUISITIONTIME", visible = True), sg.In('1', size = (6,2), key = 'ACQIN', enable_events=True), sg.T('1 second(s)', expand_x=False, size = (13, 1), key = 'ACQVAL', relief = 'flat', text_color = 'white', background_color='black', border_width = 1, justification = 'right')]]

        block_right = [[sg.Text('Motion control', font='Any 12')],
                    [sg.Button(size = (4,2), key='-UL-', enable_events=True), sg.Button(sg.SYMBOL_UP_ARROWHEAD, size = (4,2)), sg.Button(size = (4,2))],
                    [sg.Button(sg.SYMBOL_LEFT_ARROWHEAD, size = (4,2)), sg.Button(size = (4,2)), sg.Button(sg.SYMBOL_RIGHT_ARROWHEAD, size = (4,2))],
                    [sg.Button(size = (4,2)), sg.Button(sg.SYMBOL_DOWN_ARROWHEAD, size = (4,2)), sg.Button(size = (4,2))],
                    [sg.T('Step size (micron)', font = 'Any 12')],
                    [sg.In(size = (4,1), key='STEPIN', enable_events=True), sg.T(stepSize, key='STEP')],           [sg.Slider(range = (1, 1000), size=(15,15), key='STEPSL', default_value=10, resolution=1,enable_events=True,orientation='h')]]

        block_home = [[sg.Button('Set Home', key='SETHOME'), sg.Button('Go Home', key='GOHOME')],
                    [sg.T('Current Pos\n{}, {}  xy'.format(*self.current_position), font=(SimGUI.deja,10), size = (12,2), text_color = 'white', background_color='green', justification='centre')]]

                    # , [sg.T('{}, {}'.format(*self.current_position), font = (SimGUI.deja, 10), expand_x=False, size = (10, 1), key = 'SCANRESVAL', relief = 'flat', text_color = 'white', background_color='green', border_width = 1, justification = 'centre')]]

        block_mid = [[sg.T('Array size: \n{}'.format(Config.scan['scan_len'] if Config.scan['scan_len'] else 'N/A'), size = (19,2), background_color = 'red', font = (SimGUI.deja, 10), justification = 'centre', key='SCANLEN')],[sg.T('Est. runtime: \nN/A', font = (SimGUI.deja, 10), size = (19,2), justification = 'centre', background_color='red', key='RUNTIME')],[sg.T('Scan Not Ready', font = (SimGUI.deja, 10), size = (19,2), background_color='red', key='NOTREADY')], [sg.Button('Scan Ready\n START', font = (SimGUI.deja, 10), size = (19,2), key='READY', visible = False)]]


        layout = [
                [sg.Column(top_banner, size=(960, 60), pad=(0,0), background_color=DARK_HEADER_COLOR)],
                  [sg.Column([
                    [sg.Column(block_cmd, size=(450,80),  pad=BPAD_LEFT_INSIDE)],
                    [sg.Column(block_control, size=(450,120), pad=BPAD_LEFT_INSIDE)],
                    [sg.Column(block_left, size=(275,220), pad = BPAD_LEFT_INSIDE),
                    sg.Column(block_mid, size = (170,220), pad = BPAD_LEFT_MID)]
                        ], pad=(BPAD_LEFT), background_color=BORDER_COLOR),
                   sg.Column([
                    [sg.Column(block_right, size=(200, 300), pad=BPAD_RIGHT_INSIDE)],
                    [sg.Column(block_home, size = (200,80), pad=BPAD_RIGHT_INSIDE)]], pad=BPAD_RIGHT, background_color=BORDER_COLOR)]]

        self.window = sg.Window('Dashboard PySimpleGUI-Style', layout, margins=(0,0), background_color=BORDER_COLOR, no_titlebar=False, grab_anywhere=False)

        return self.window

    def generate_map(self):
        startPos = Config.scan['start_pos']
        finishPos = Config.scan['finish_pos']
        scanRes = Config.scan['scan_res']

        deltaX = finishPos[0]-startPos[0]
        deltaY = finishPos[1]-startPos[1]

        if deltaX > 0:
            xStep = scanRes
        if deltaX < 0:
            xStep = scanRes*-1

        if deltaY > 0:
            yStep = scanRes
        if deltaY < 0:
            yStep = scanRes*-1

        print(xStep)
        lenX = math.floor(abs(deltaX/xStep))
        lenY = math.floor(abs(deltaY/yStep))

        xScan = [startPos[0]+(xStep*index) for index in list(range(lenX+1))]
        yScan = [startPos[1]+(yStep*index) for index in list(range(lenY+1))]

        print('xScan:', self.xScan)
        print('yScan:', self.yScan)

        if len(xScan) == 0 or len(yScan)== 0:
            print('resolution error - please enter appropriate resolution for image size')

        self.posDict = {}
        self.mapList = []
        for j in self.yScan:
            for i in self.xScan:
                pos = (i, j)
                self.mapList.append(pos)
                self.posDict['{},{}'.format(i,j)] = (pos)
        #
        self.scanLen = len(self.posDict)
        # return xScan, yScan

    def generate_linescan(self):
        '''Generates a linescan which strictly maintains scan resolution by rescaling the line to the nearest length/resolution interger.'''
        startPos = Config.scan['start_pos']
        finishPos = Config.scan['finish_pos']
        scanResolution = Config.scan['scan_res']
        lineVector = (float(finishPos[0])-float(startPos[0]), float(finishPos[1])-float(startPos[1]))
        self.scanLen = math.sqrt((lineVector[0]**2)+(lineVector[1]**2))

        if self.scanLen == 0 or scanResolution == 0:
            return

        clean_array_len = round(self.scanLen/scanResolution) # used for rescaling the scan dimensions
        scale_ratio = (clean_array_len*scanResolution)/self.scanLen
        arrayLen = clean_array_len+1 # used for building the linescan list
        if arrayLen == 1:
            return

        xInt = ((finishPos[0] - startPos[0])*scale_ratio)/(arrayLen-1)
        yInt = ((finishPos[1] - startPos[1])*scale_ratio)/(arrayLen-1)
        lineScanX = [round(startPos[0]+(xInt*index), 2) for index in list(range(arrayLen))]
        lineScanY = [round(startPos[1]+(yInt*index), 2) for index in list(range(arrayLen))]

        linescanList = [(lineScanX[idx], lineScanY[idx]) for idx in range(len(lineScanX))]
        Config.scan['linescan_list'] = linescanList
        print('Linescan: ', linescanList)
        self.scanLen = len(linescanList)
        Config.scan['scan_len'] = self.scanLen
        
    def update_status(self):
        '''Updates all of the visual cues every time a change is made'''
        if self.startPos and self.finishPos and self.scanRes:
            self.window['SCANLEN'].update('Array size: \n{}'.format(Config.scan['scan_len']), background_color = 'green')
        else:
            self.window['SCANLEN'].update('Array size: \nN/A', background_color = 'red')
            self.window['RUNTIME'].update('Est. runtime:\nN/A', background_color='red')
            self.window['READY'].update(visible = False)
            self.window['NOTREADY'].update(visible = True)

        # edge case - if scan res is entered as 0
        if Config.scan['scan_res'] == 0:
            self.window['SCANLEN'].update('Array size: \nN/A', background_color = 'red')
            self.window['RUNTIME'].update('Est. runtime:\nN/A', background_color='red')
            self.window['READY'].update(visible = False)
            self.window['NOTREADY'].update(visible = True)
            self.scanRes = False
        # edge case: if acquisition time is set as 0
        if Config.scan['acquisition_time'] == 0:
            self.window['RUNTIME'].update('Est. runtime:\nN/A', background_color='red')
            self.window['READY'].update(visible = False)
            self.window['NOTREADY'].update(visible = True)
            self.time = False
        
        # edge case: if scan len is 0:
        if self.scanLen == 0:
            self.window['SCANLEN'].update('Array size: \nN/A', background_color = 'red')
            self.window['RUNTIME'].update('Est. runtime:\nN/A', background_color='red')
            self.window['READY'].update(visible = False)
            self.window['NOTREADY'].update(visible = True)
        # Final check if all ready
        if self.startPos and self.finishPos and self.time and self.scanRes:
            if self.scanLen != 0:
                self.window['READY'].update(visible = True)
                self.window['NOTREADY'].update(visible = False)
    
    def update_scan(self):
        '''Updates the linescan and maps when an appropriate change is made'''
        if Config.scan['scan_type'] == 'linescan':
            self.generate_linescan()
        if Config.scan['scan_type'] == 'map':
            self.generate_map()
      
    def update_scan_time(self):
        '''Updates the predicted scan time when a change is made'''
        self.runTime = Config.scan['scan_len']*Config.scan['acquisition_time']

        if self.runTime <= 60:
            self.window['RUNTIME'].update('Est. runtime:\n{} seconds'.format(round(self.runTime,2)), background_color='green')
        if 60 < self.runTime <= 3600:
            self.window['RUNTIME'].update('Est. runtime:\n{} minutes'.format(round(self.runTime/60,2)), background_color='green')
        if 3600 < self.runTime:
            self.window['RUNTIME'].update('Est. runtime:\n{} hours'.format(round(self.runTime/3600,2)), background_color='green')

    def refresh_window(self):
        '''Refreshes the window after an event. Calls each update function as appropriate'''

        if self.startPos and self.finishPos and self.scanRes:
            self.update_scan()
        if self.startPos and self.finishPos and self.scanRes and self.time:
            self.update_scan_time()

        self.update_status()
        return


    def parse_input(self):
        inp = self.values['COMIN']
        try: # searches for spaces in command
            command = inp[:inp.index(' ')]
        except:
            return inp, None # if no spaces, returns inp as command
        try: # grabs string after the space
            arg = inp[inp.index(' ')+1:]
            if len(arg) == 0:
                return command, None
        except:
            return command, None # if nothing after space, returns string before the space
        try: # splits arguments by comma
            arg = arg.split(',')
            return command, arg
        except:
            return command, arg


    def main_loop(self):
        '''Main event loop'''
        while True:             # Event Loop
            self.event, self.values = self.window.read()
            print('event:', self.event, 'values:', self.values)
            try:
                self.microscopeFunctionDict[self.event]()
            except KeyError:
                print('No function found for {}'.format(self.event))
            # self.do_function()
            self.refresh_window()

if __name__ == "__main__":
    Config = MetaFile()
    Win = SimGUI(Config)

    print(Config.__dict__)
    Win.main_loop()
    '''
    # NEED TO GO THROUGH AND CHANGE ALL THE VARIABLES IN MAINLOOP
    '''
    # print(win.__dict__)

    # root = tk.Tk()
    # app = TK_GUI(root)
    # root.mainloop()
