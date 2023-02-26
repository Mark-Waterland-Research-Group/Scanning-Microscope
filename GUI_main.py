import PySimpleGUI as sg
import numpy as np
import os
import json

import tkinter as tk
from tkinter import ttk

def pause(text = '---'):
    input(text)

class TK_GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Example GUI")

        # Define ttk style for the GUI
        s = ttk.Style()
        s.theme_use('winnative')
        print(s.theme_names())

        # Create a frame for the main window
        main_frame = ttk.Frame(self.master, padding="30 20 30 20")
        main_frame.grid(column=0, row=0, sticky="nsew")

        # Create a drop-down menu
        options = ["Option 1", "Option 2", "Option 3", 'This is custom']
        self.option_var = tk.StringVar()
        self.option_var.set(options[0])
        option_menu = ttk.OptionMenu(main_frame, self.option_var, *options)
        option_menu.grid(column=0, row=1, padx=10, pady=10, sticky="w")

        # Create a text input box
        self.text_var = tk.StringVar()
        text_entry = ttk.Entry(main_frame, textvariable=self.text_var)
        text_entry.grid(column=0, row=0, padx=10, pady=10, sticky="we")
        text_entry.focus()

        # Create a button
        button = ttk.Button(main_frame, text="Click me", command=self.button_callback)
        button.grid(column=2, row=0, padx=10, pady=10, sticky="e")

        # Create a tabbed notebook with extra options
        notebook = ttk.Notebook(main_frame)
        notebook.grid(column=0, row=2, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Create the first tab
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Tab 1")
        ttk.Label(tab1, text="This is the first tab").grid(column=0, row=0)

        # Create the second tab
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Tab 2")
        ttk.Label(tab2, text="This is the second tab").grid(column=0, row=0)

    def button_callback(self):
        # Callback function for the button
        print("Option:", self.option_var.get())
        print("Text input:", self.text_var.get())

# class MicroscopeConfig:
#
#     attributeList = [
#         'microscope_mode',
#         'light_level',
#         'light_on',
#         'current_position',
#         'linescanConfig',
#         'mapConfig'
#         ]
#
#     def __init__(self, config):
#         # print(config.__dict__)
#         self.__dict__ = config.instrumentConfig
#         print(config.instrumentConfig)
#         print(self.__dict__)



class Linescan:

    attributeList = [
        'scan_res',
        'scan_len',
        'acquisition_time',
        'x_scan',
        'y_scan',
        'start_pos',
        'finish_pos'
        ]

    def __init__(self, configDict):
        self.__dict__ = {key:value for (key, value) in configDict.items() if key in Linescan.attributeList}
    pass

class Map:
    pass

class JustMove:
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
        # if self.hasConfig: # check config exists
        #     print('Config file found, returning...')
        #     return
        self.__dict__ = {'scriptDir': self.scriptDir, 'hasConfig': True}

        microscope_mode = self.query_mode()


        self.instrument = {
            'microscope_mode': microscope_mode,
            'light_level': 255,
            'light_on': False,
            'current_position': [0, 0],
            # 'scan_type': 'linescan'
        }

        self.scan = {
            'scan_type': 'linescan',
            'scan_res': 1,
            'scan_len': None,
            'acquisition_time': 1,
            'x_scan': [],
            'y_scan': [],
            'start_pos': None,
            'finish_pos': None
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



    def __init__(self):
        self.config = MetaFile()
        # print(self.config.__dict__)
        # self.microscope = MicroscopeConfig(self.config)
        print(self.config.instrument)
        pause()

        # print(self.microscope.__dict__)

        self.scan_type = self.instrument.scan_type
        self.microscope_mode = self.microscope.microscope_mode
        self.current_position = self.microscope.current_position
        self.light_level = self.microscope.light_level
        self.light_on = self.microscope.light_on
        # self.current_

        self.linescan = Linescan(self.config.linescanConfig)
        print(self.linescan.__dict__)
        # pause()

        # self.scan_type = self.microscope.scan_type
        # print(self.microscope.__dict__)

        # print(self.scan_type)

        self.window = self.__construct_UI()

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

        block_mid = [[sg.T('Array size: \n{}'.format(self.scanLen if self.scanLen else 'N/A'), size = (19,2), background_color = 'red', font = (SimGUI.deja, 10), justification = 'centre', key='SCANLEN')],[sg.T('Est. runtime: \nN/A', font = (SimGUI.deja, 10), size = (19,2), justification = 'centre', background_color='red', key='RUNTIME')],[sg.T('Scan Not Ready', font = (SimGUI.deja, 10), size = (19,2), background_color='red', key='NOTREADY')], [sg.Button('Scan Ready\n START', font = (SimGUI.deja, 10), size = (19,2), key='READY', visible = False)]]


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

        return self.window


    def print_response(self, a = 'a', b = 'b', c = 'c'):
        # dummy function for printing the response of inputs
        print(a)
        print(b)
        print(c)

        # self.__pull_config()

    # def __pull_config(self):
        # takes the config items and puts relevant information into attributes
        # for key, item in self.config.__dict__.items():
        #     if key in MicroscopeConfig.attributeList:
        #         self.__dict__[key] = item


if __name__ == "__main__":
    win = SimGUI()
    # mf = MetaFile()
    # mf._save_config(makeNew = True)
    # print(mf.__dict__)
    # win.config._save_config(makeNew = True)

    print(win.config.__dict__)
    # print(win.__dict__)

    # root = tk.Tk()
    # app = TK_GUI(root)
    # root.mainloop()
