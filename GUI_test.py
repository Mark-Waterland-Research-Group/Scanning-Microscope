import PySimpleGUI as sg
import pickle
import csv
import math
import numpy as np

elements = sorted(vars(sg))
for x in elements:
    if 'SYMBOL' in x:
        print('-'*100)
        print(x)

symbols = [x for x in elements if 'SYMBOL' in x]
# print(elements)
# pause()

deja = 'DejaVu Sans Mono'

def pause(text = '...'):
    input(text)

class UI():

    codeKeys = {'IMAGEMODE':'image mode', 'RAMANMODE':'raman mode'}
    startPos = None
    finishPos = None
    scanRes = 1
    scanLen = None
    acquisitionTime = 1
    light = False
    lightLevel = 255

    def __init__(self):
        try:
            with open("microscope.config", "r") as file:
                config = csv.reader(file, delimiter = ' ')
                config = {row[0]:row[1] for row in config}
        except:
            config = {
            'microMode':'RAMANMODE',
            'scanType':'linescan'
            }
            print('Config file not found - creating a new one...')
            while True:
                self.microMode = input('Please enter current microscope configuration: "image" or "raman": ')
                if self.microMode == 'raman':
                    config['microMode'] = 'RAMANMODE'
                    break
                if self.microMode == 'image':
                    config['microMode'] = 'IMAGEMODE'
                    break
                else:
                    print('"{}" not recognised.'.format(self.microMode))

            configList = [[key, value] for (key, value) in config.items()]
            with open("microscope.config", "w", newline = '') as file:
                writer = csv.writer(file, delimiter=' ')
                for item in configList:
                    writer.writerow(item)
                # pickle.dump(config, file)

        # self.config = config['config']
        self.scanType = config['scanType']
        self.microMode = config['microMode']
        try:
            self.currentPos = config['currentPos']
        except KeyError:
            print('Could not find current positon - startnig at (0, 0)')
            self.currentPos = (0,0)


        self.commandDict = {'print':self.print_response}

        theme_dict = {'BACKGROUND': '#2B475D',
                        'TEXT': '#FFFFFF',
                        'INPUT': '#F2EFE8',
                        'TEXT_INPUT': '#000000',
                        'SCROLL': '#F2EFE8',
                        'BUTTON': ('#000000', '#C2D4D8'),
                        'PROGRESS': ('#FFFFFF', '#C7D5E0'),
                        'BORDER': 1,'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0}


        # FONTS: constantina 'DejaVu Sans Mono'
        # sg.theme_add_new('Dashboard', theme_dict)     # if using 4.20.0.1+
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
                    [sg.Radio('Linescan', 'scanType', enable_events=True, key = 'LINESCAN', default = (False if self.scanType == 'map' else True)), sg.Radio('Map', group_id='scanType', enable_events=True, key='MAP', default = (True if self.scanType == 'map' else False)), sg.Radio('Image mode', group_id='microMode', enable_events=True, key='IMAGEMODE', default = (True if self.microMode == 'IMAGEMODE' else False)), sg.Radio('Raman mode', group_id='microMode', enable_events=True, key='RAMANMODE', default = (True if self.microMode == 'RAMANMODE' else False))],
                    [sg.T('Alread in {} - are you sure you want to ovewrite?'.format(self.microMode), visible = False, key = 'MODE_CHECK')],
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
                    [sg.T('Current Pos\n{}, {}  xy'.format(*self.currentPos), font=(deja,10), size = (12,2), text_color = 'white', background_color='green', justification='centre')]]

                    # , [sg.T('{}, {}'.format(*self.currentPos), font = (deja, 10), expand_x=False, size = (10, 1), key = 'SCANRESVAL', relief = 'flat', text_color = 'white', background_color='green', border_width = 1, justification = 'centre')]]

        block_mid = [[sg.T('Array size: \n{}'.format(self.scanLen if self.scanLen else 'N/A'), size = (19,2), background_color = 'red', font = (deja, 10), justification = 'centre', key='SCANLEN')],[sg.T('Est. runtime: \nN/A', font = (deja, 10), size = (19,2), justification = 'centre', background_color='red', key='RUNTIME')],[sg.T('Scan Not Ready', font = (deja, 10), size = (19,2), justification = 'centre', background_color='red', key='NOTREADY')], [sg.Button('Scan Ready\n START', font = (deja, 10), size = (19,2), justification = 'centre', background_color='green', key='READY', visible = False)]]


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

        self.window = sg.Window('Dashboard PySimpleGUI-Style', layout, margins=(0,0), background_color=BORDER_COLOR, no_titlebar=False, grab_anywhere=True)




    def print_response(self, a = 'a', b = 'b', c = 'c'):
        print(a)
        print(b)
        print(c)

    def ramanMode(self):
        print('Switching to Raman mode')
        print('Switching complete - Ready for Raman')
        self.microMode = 'RAMANMODE'
        self.lightOff()

    def imageMode(self):
        print('Switching to Image mode')
        print('Switching complete - Ready for imaging')
        self.microMode = 'IMAGEMODE'
        self.lightOn()

    def switch_mode(self):
        if self.microMode == 'RAMANMODE':
            self.imageMode()
        elif self.microMode == 'IMAGEMODE':
            self.ramanMode()

    def overwrite_mode(self):
        if self.microMode == 'RAMANMODE':
            self.ramanMode()
        elif self.microMode == 'IMAGEMODE':
            self.imageMode()

    def lightOn(self, val = None):
        if not val:
            val = self.lightLevel
        self.window['LIGHT'].update(text='ON', button_color='white on green')
        print('Turning on light at {} power'.format(val))

    def lightOff(self):
        self.window['LIGHT'].update(text='OFF', button_color='white on grey')
        print('Light:0')

    def generate_2D_arrays(self):
        deltaX = self.finishPos[0]-self.startPos[0]
        deltaY = self.finishPos[1]-self.startPos[1]

        if deltaX > 0:
            xStep = self.scanRes
        if deltaX < 0:
            xStep = self.scanRes*-1

        if deltaY > 0:
            yStep = self.scanRes
        if deltaY < 0:
            yStep = self.scanRes*-1

        print(xStep)
        lenX = math.floor(abs(deltaX/xStep))
        lenY = math.floor(abs(deltaY/yStep))

        self.xScan = [self.startPos[0]+(xStep*index) for index in list(range(lenX+1))]
        self.yScan = [self.startPos[1]+(yStep*index) for index in list(range(lenY+1))]

        print('xScan:', self.xScan)
        print('yScan:', self.yScan)

        if len(self.xScan) == 0 or len(self.yScan)== 0:
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
        lineVector = (float(self.finishPos[0])-float(self.startPos[0]), float(self.finishPos[1])-float(self.startPos[1]))
        self.scanLen = math.sqrt((lineVector[0]**2)+(lineVector[1]**2))

        arrayLen = math.floor(self.scanLen/self.scanRes)

        xInt = (self.finishPos[0] - self.startPos[0])/(arrayLen-1)
        yInt = (self.finishPos[1] - self.startPos[1])/(arrayLen-1)
        lineScanX = [self.startPos[0]+(xInt*index) for index in list(range(arrayLen))]
        lineScanY = [self.startPos[1]+(yInt*index) for index in list(range(arrayLen))]

        self.lineScanList = [(lineScanX[idx], lineScanY[idx]) for idx in range(len(lineScanX))]
        print('Linescan: ',self.lineScanList)
        self.scanLen = len(self.lineScanList)


    def refresh_window(self):
        self.window['MODE_CHECK'].update(visible = False)
        self.window['CANCEL'].update(visible = False)
        self.window['OVERWRITE'].update(visible = False)

        # if self.microMode == 'RAMANMODE':
        #     self.window['RAMANMODE'].update(disabled = False)
        # elif self.microMode == 'IMAGEMODE':
        #     self.window['IMAGEMODE'].update(disabled = False)

        if self.event in ['STARTPOSIN','STARTPOSBUT','FINISHPOSIN','FINISHPOSBUT','SCANRESIN','MAP','LINESCAN','ACQIN']:
            if self.startPos and self.finishPos and self.scanRes:
                if self.scanType == 'linescan':

                    self.generate_linescan()
                    self.window['SCANLEN'].update('Array size: \n{}'.format(self.scanLen), background_color = 'green')


                if self.scanType == 'map':
                    self.generate_2D_arrays()


                if self.acquisitionTime:
                    self.runTime = self.scanLen*self.acquisitionTime
                    if self.runTime <= 60:
                        self.window['RUNTIME'].update('Est. runtime:\n{} seconds'.format(round(self.runTime,2)), background_color='green')
                    if 60 < self.runTime <= 3600:
                        self.window['RUNTIME'].update('Est. runtime:\n{} minutes'.format(round(self.runTime/60,2)), background_color='green')
                    if 3600 < self.runTime:
                        self.window['RUNTIME'].update('Est. runtime:\n{} hours'.format(round(self.runTime/3600,2)), background_color='green')

                else:
                    self.window['RUNTIME'].update('Est. runtime:\nN/A', background_color='red')

            # Does final check to make sure all variables are entered
            if self.acquisitionTime and self.scanLen:
                self.window['READY'].update(visible = True)
                self.window['NOTREADY'].update(visible = False)
            else:
                self.window['READY'].update(visible = False)
                self.window['NOTREADY'].update(visible = True)





    def event_radio(self):
        if self.event == self.microMode:
            self.window['MODE_CHECK'].update('Alread in {} - are you sure you want to ovewrite?'.format(self.microMode), visible = True)
            self.window['CANCEL'].update(visible = True)
            self.window['OVERWRITE'].update(visible = True)
        else:
            self.window['MODE_CHECK'].update(visible = False)
            self.window['CANCEL'].update(visible = False)
            self.window['OVERWRITE'].update(visible = False)

            self.switch_mode()

    def main_loop(self):

                    # pass
                # pass
        while True:             # Event Loop
            self.event, self.values = self.window.read()

            if self.event == 'LINESCAN':
                self.scanType = 'linescan'
            if self.event == 'MAP':
                self.scanType = 'map'

            if self.event == 'LIGHT': # adjusts lighting
                self.light = not self.light
                if self.light:
                    self.lightOn()
                else:
                    self.lightOff()

            if self.event == 'LIGHTSL':
                self.lightLevel = self.values['LIGHTSL']
                if self.light:
                    self.lightOn(self.lightLevel)
                # if self.light:

            if self.event == 'STARTPOSBUT':
                print('Setting start position as {}'.format(self.currentPos))
                self.startPos = self.currentPos
                self.window['STARTPOSVAL'].update(self.startPos)

            if self.event == 'STARTPOSIN':
                try:
                    pos = np.array(self.values['STARTPOSIN'].split(',')).astype(float)
                    self.startPos = (pos[0], pos[1])
                    self.window['STARTPOSVAL'].update(self.startPos)
                except Exception as e:
                    print(e)
                    self.startPos = None
                    self.window['RUNTIME'].update('Estimated runtime:\nN/A', background_color='red')
                    self.window['SCANLEN'].update('Array size: \nN/A', background_color = 'red')
            elif self.event == 'FINISHPOSIN':
                try:
                    pos = np.array(self.values['FINISHPOSIN'].split(',')).astype(float)
                    self.finishPos = (pos[0], pos[1])
                    self.window['FINISHPOSVAL'].update(self.finishPos)
                except Exception as e:
                    print(e)
                    self.finishPos = None
                    self.window['RUNTIME'].update('Estimated runtime:\nN/A', background_color='red')
                    self.window['SCANLEN'].update('Array size: \nN/A', background_color = 'red')

            if self.event == 'SCANRESIN':
                # self.scanRes = self.values['SCANRESIN']
                try:
                    self.scanRes = float(self.values['SCANRESIN'])
                    self.window['SCANRESVAL'].update('{} mu m'.format(self.scanRes))
                except:
                    pass

            if self.event == 'ACQIN':
                try:
                    self.acquisitionTime = float(self.values['ACQIN'])
                    self.window['ACQVAL'].update('{} second(s)'.format(self.acquisitionTime))
                except:
                    self.acquisitionTime = None
                    pass

            if self.event == sg.WIN_CLOSED or self.event == 'Exit':
                break
            print(self.event)
            print(self.values)
            if self.event == 'CANCEL':
                self.window['MODE_CHECK'].update(visible = False)
                self.window['CANCEL'].update(visible = False)
                self.window['OVERWRITE'].update(visible = False)
                continue

            if self.event == 'OVERWRITE': # Forces microscope mode change
                self.overwrite_mode()

            if self.event == 'IMAGEMODE' or self.event == 'RAMANMODE': # if microscope mode is selected
                self.event_radio()
                continue

            if self.event == 'STEPIN': # adjusts the motion step size (value)
                try:
                    stepSize = float(self.values['STEPIN'])
                    if 0.05 <= stepSize <= 5000:
                        self.window['STEP'].update(stepSize)
                except:
                    pass
                continue

            if self.event == 'STEPSL': # adjusts the motion step size (slider)
                stepSize = float(self.values['STEPSL'])
                self.window['STEP'].update(int(stepSize))
                self.window['STEPIN'].update(int(stepSize))
                continue

            if self.event == 'SUBMIT':
                com = self.values['COMIN']
                if com == '':
                    continue
                self.window['COM'].update('Enter commands')
                command, arg = parse_input(com)
                print(command)
                print(arg)

                try:
                    if not arg:
                        self.commandDict[command]()
                    else:
                        self.commandDict[command](*arg)
                    self.window['COMIN'].update('')
                except Exception as e:
                    print(e)
                    self.window['COM'].update('Command "{}" not recognised.\n{}'.format(com, e))



            self.refresh_window()


        class Motion():
            pass





# window = sg.Window('Dashboard PySimpleGUI-Style', layout, margins=(0,0), background_color=BORDER_COLOR, no_titlebar=True, grab_anywhere=True)

# def update_window():

# def print_response(a = 'a', b = 'b', c = 'c'):
#     print(a)
#     print(b)
#     print(c)

# def parse_motion(input):


def parse_input(input):
    try: # searches for spaces in command
        command = input[:input.index(' ')]
    except:
        return input, None # if no spaces, returns input as command
    try: # grabs string after the space
        arg = input[input.index(' ')+1:]
        if len(arg) == 0:
            return command, None
    except:
        return command, None # if nothing after space, returns string before the space
    try: # splits arguments by comma
        arg = arg.split(',')
        return command, arg
    except:
        return command, arg



# while True:             # Event Loop
#     event, values = window.read()
#     if event == sg.WIN_CLOSED or event == 'Exit':
#         break
#     print(event)
#     print(values)
#     if event == 'STEPIN':
#     # stepSize = values['-STEPSIZE-']
#         try:
#             stepSize = float(values['STEPIN'])
#             if 0.05 <= stepSize <= 5000:
#                 window['STEP'].update(stepSize)
#         except:
#             pass
#     if event == 'STEPSL':
#         stepSize = float(values['STEPSL'])
#         window['STEP'].update(int(stepSize))
#         window['STEPIN'].update(int(stepSize))
#
#     if event == 'SUBMIT':
#         com = values['COMIN']
#         window['COM'].update('Enter commands')
#         command, arg = parse_input(com)
#
#         try:
#             if not arg:
#                 commandDict[command]()
#             else:
#                 commandDict[command](*arg)
#             window['COMIN'].update('')
#         except Exception as e:
#             print(e)
#             window['COM'].update('Command "{}" not recognised.\n{}'.format(com, e))



interface = UI()
interface.main_loop()

# NEXT: Do motion controls and config updating on the fly.
# then add gcode and mapping

interface.window.close()
