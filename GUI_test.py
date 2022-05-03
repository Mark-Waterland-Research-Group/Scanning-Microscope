import PySimpleGUI as sg
import pickle

"""
    Dashboard using blocks of information.

    Copyright 2020 PySimpleGUI.org
"""


theme_dict = {'BACKGROUND': '#2B475D',
                'TEXT': '#FFFFFF',
                'INPUT': '#F2EFE8',
                'TEXT_INPUT': '#000000',
                'SCROLL': '#F2EFE8',
                'BUTTON': ('#000000', '#C2D4D8'),
                'PROGRESS': ('#FFFFFF', '#C7D5E0'),
                'BORDER': 1,'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0}

# sg.theme_add_new('Dashboard', theme_dict)     # if using 4.20.0.1+
sg.LOOK_AND_FEEL_TABLE['Dashboard'] = theme_dict
sg.theme('Dashboard')

BORDER_COLOR = '#C7D5E0'
DARK_HEADER_COLOR = '#1B2838'
BPAD_TOP = ((20,20), (20, 10))
BPAD_LEFT = ((20,10), (0, 10))
BPAD_LEFT_INSIDE = (0, 10)
BPAD_RIGHT = ((10,20), (10, 20))
stepSize = 10

top_banner = [[sg.Text('Here we put title', font='Any 20', background_color = DARK_HEADER_COLOR)]]


block_1 = [[sg.T('Enter commands', font='Any 12', key = '-COM-')],
            [sg.Input(key = '-COMIN-'), sg.Button('<Enter>', bind_return_key = True, enable_events=True, key = '-SUBMIT-')]]


block_2 = [[sg.Text('Controls', font='Any 12')],
            [sg.Radio('Linescan', 'scan_type', enable_events=True, key = '-LINESCAN-'), sg.Radio('Map', group_id='scan_type', enable_events=True, key='-MAP-')],
            [sg.Button()],
            [sg.Image(data=sg.DEFAULT_BASE64_ICON)]  ]

block_3 = [[sg.Text('Motion control', font='Any 12')],
            [sg.Button(size = (4,2), key='-UL-', enable_events=True), sg.Button('^', size = (4,2)), sg.Button(size = (4,2))],
            [sg.Button('<', size = (4,2)), sg.Button(size = (4,2)), sg.Button('>', size = (4,2))],
            [sg.Button(size = (4,2)), sg.Button(size = (4,2)), sg.Button(size = (4,2))],
            [sg.T('Step size (micron)', font = 'Any 12')],
            [sg.In(size = (4,1), key='-STEPIN-', enable_events=True), sg.T(stepSize, key='-STEP-')],           [sg.Slider(range = (1, 1000), size=(15,15), key='-STEPSL-', default_value=10, resolution=1,enable_events=True,orientation='h')]]


layout = [[sg.Column(top_banner, size=(960, 60), pad=(0,0), background_color=DARK_HEADER_COLOR)],
          [sg.Column([[sg.Column(block_1, size=(450,80), pad=BPAD_LEFT_INSIDE)],
                      [sg.Column(block_2, size=(450,300),  pad=BPAD_LEFT_INSIDE)]], pad=BPAD_LEFT, background_color=BORDER_COLOR),
           sg.Column(block_3, size=(200, 300), pad=BPAD_RIGHT)]]

class UI():

    def __init__(self):
        try:
            with open("microscope.config", "rb") as file:
                config = pickle.load(file)
            print(config)
        except:
            config = {'config':'raman',
                        'scan_type':'linescan'
                        }
            print('Config file not found - creating a new one...')
            with open("microscope.config", "wb") as file:
                pickle.dump(config, file)
        self.config = config['config']
        self.scan_type = config['scan_type']

        self.commandDict = {'print':print_response}

        self.window = sg.Window('Dashboard PySimpleGUI-Style', layout, margins=(0,0), background_color=BORDER_COLOR, no_titlebar=True, grab_anywhere=True)


    def print_response(self, a = 'a', b = 'b', c = 'c'):
        print(a)
        print(b)
        print(c)

    def main_loop(self):
        while True:             # Event Loop
            self.event, self.values = self.window.read()
            if self.event == sg.WIN_CLOSED or self.event == 'Exit':
                break
            print(self.event)
            print(self.values)
            if self.event == '-STEPIN-':
            # stepSize = values['-STEPSIZE-']
                try:
                    stepSize = float(self.values['-STEPIN-'])
                    if 0.05 <= stepSize <= 5000:
                        self.window['-STEP-'].update(stepSize)
                except:
                    pass
            if self.event == '-STEPSL-':
                stepSize = float(self.values['-STEPSL-'])
                self.window['-STEP-'].update(int(stepSize))
                self.window['-STEPIN-'].update(int(stepSize))

            if self.event == '-SUBMIT-':
                com = values['-COMIN-']
                self.window['-COM-'].update('Enter commands')
                command, arg = parse_input(com)

                try:
                    if not arg:
                        self.commandDict[command]()
                    else:
                        self.commandDict[command](*arg)
                    self.window['-COMIN-'].update('')
                except Exception as e:
                    print(e)
                    self.window['-COM-'].update('Command "{}" not recognised.\n{}'.format(com, e))

        class Motion():
            pass





# window = sg.Window('Dashboard PySimpleGUI-Style', layout, margins=(0,0), background_color=BORDER_COLOR, no_titlebar=True, grab_anywhere=True)

# def update_window():

# def print_response(a = 'a', b = 'b', c = 'c'):
#     print(a)
#     print(b)
#     print(c)

def parse_input(input):
    try: # searches for spaces in command
        command = input[:input.index(' ')]
    except:
        return input, None # if no spaces, returns input as command
    try: # grabs string after the space
        arg = com[com.index(' ')+1:]
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
#     if event == '-STEPIN-':
#     # stepSize = values['-STEPSIZE-']
#         try:
#             stepSize = float(values['-STEPIN-'])
#             if 0.05 <= stepSize <= 5000:
#                 window['-STEP-'].update(stepSize)
#         except:
#             pass
#     if event == '-STEPSL-':
#         stepSize = float(values['-STEPSL-'])
#         window['-STEP-'].update(int(stepSize))
#         window['-STEPIN-'].update(int(stepSize))
#
#     if event == '-SUBMIT-':
#         com = values['-COMIN-']
#         window['-COM-'].update('Enter commands')
#         command, arg = parse_input(com)
#
#         try:
#             if not arg:
#                 commandDict[command]()
#             else:
#                 commandDict[command](*arg)
#             window['-COMIN-'].update('')
#         except Exception as e:
#             print(e)
#             window['-COM-'].update('Command "{}" not recognised.\n{}'.format(com, e))



interface = UI()



interface.window.close()
