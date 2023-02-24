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

class MicroscopeConfig:
    pass

class Linescan:
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

    def __generate_config(self):
        if self.hasConfig: # check config exists
            print('Config file found, returning...')
            return

        self.instrumentConfig = {
            'microscope_mode': None,
            'start_pos': 0,
            'finish_pos': 0,
            'light_level': 255,
            'light_on': False
        }

        self.linescanConfig = {
            'scan_res': 1,
            'scan_len': None,
            'acquisition_time': 1,
            'x_scan': [],
            'y_scan': []
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



class SimGUI:

    codeKeys = {'IMAGEMODE':'image mode', 'RAMANMODE':'raman mode'}
    startPos = None
    finishPos = None
    scanRes = 1
    scanLen = None
    acquisitionTime = 1
    light = False
    lightLevel = 255



if __name__ == "__main__":
    mf = MetaFile()
    print(mf.__dict__)
    # root = tk.Tk()
    # app = TK_GUI(root)
    # root.mainloop()
