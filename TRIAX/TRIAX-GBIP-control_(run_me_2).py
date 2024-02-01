# import gpib_ctypes
import pyvisa
import time
# import serial

class TRIAX:


    def __init__(self, COM='GPIB0::1::INSTR'):

        self.command_dict = {
        'exit': self._move_exit_slit,
        'enterance': self._move_enterance_slit,
        'exit_side': self.__exit_side_port,
        'exit_front': self.__exit_front_port,
        'set_exit': self.__set_exit_slit_width,
        'set_enter': self.__set_enterance_slit_width
    }

        # Open a connection to the instrument   
        rm = pyvisa.ResourceManager()
        rm.list_resources()
        self.instrument = rm.open_resource(COM)
        self.establish_connection()
        self.enterance_slit_width = self.__get_enterance_slit_width
        self.exit_slit_width = self.__get_exit_slit_width

    def __set_exit_slit_width(self, new_width):
        new_width = float(new_width)
        if self.exit_slit_width == float(new_width):
            return
        else:
            self._send_command('k0,3,{}'.format(new_width))
            self.exit_slit_width = new_width
        print('Exit slit set to {}'.format(new_width))

    def __get_exit_slit_width(self):
        response = self._send_command('j0,3')
        try:
            self.exit_slit_width = float(response.lstrip('o'))
        except Exception as e:
            print('Exit width error:', e)

    def __get_enterance_slit_width(self):
        response = self._send_command('j0,1')
        try:
            self.exit_slit_width = float(response.lstrip('o'))
        except Exception as e:
            print('Enterance width error:', e)
    
    def __exit_side_port(self):
        self._send_command('e0')
    
    def __exit_front_port(self):
        self._send_command('f0')

    def _initialise_spectrometer(self):
        count = 100
        while count > 0:
            print('Initialising: Sleeping for {} seconds'.format(count))
            time.sleep(1)
            count -= 1
        response = self.instrument.read()
        print('RES:', response)

    def _send_command(self, command:str):
        try:
            self.instrument.write(command)
            time.sleep(0.0001)
            response = self.instrument.read()
            print('RES:{}'.format(response))
        except Exception as e:
            print('Caught error: {}'.format(e))

    def establish_connection(self):
        self.instrument.write('WHERE AM I')
        time.sleep(0.0001)
        state = self.instrument.read()
        print(state)
        if state != 'o':
            self.instrument.write('O2000')
            time.sleep(0.0001)
            state = self.instrument.read()
        # breakpoint()
        return state
    
    def _move_exit_slit(self, slit_width):


        self._send_command('k0,3,{}')
    
    def main(self):
        while True:
            try:
                # loop continuously here for com input
                com = input('Enter command - COM to send string:\n')
                if com == 'COM':
                    while True:
                        com = 'Enter string command:\n'
                        self.instrument.write(com)
                        time.sleep(0.0001)
                else:
                    command = com.split(' ')
                    if command[0] in self.command_dict.keys():

                
                        


            #         break
                    
            #     if com == 'A':
            #         count = 100
            #         while count > 0:
            #             print('Initialising: Sleeping for {} seconds'.format(count))
            #             time.sleep(1)
            #             count -= 1
            #     response = instrument.read()
            #     print('RES:', response)
            # except Exception as e:
            #     print(e) 



'''# looking for some kind of response like "b" or "o". Use command "O2000" to enter into command mode.
Initial grating is Blaze 500, 1200 g/mm
centre for 532 nm is roughly 241543
List of useful commands = {
"Initiate command mode": "02000",
"Initialise Spectrometer: "A",
"read motor position": "H0",
"read slit position: "j0,0",
"move slit relative: "k0,0,100"
"poll motors after move command sent - necessary because control is given to PC immediately after command is given, but new motor command cannot be issued until motor motion is stopped. Implement a check for this here. Note if the motors are not busy, a timeout is received... could be a delay/timing issue: "E",
"move exit mirror to front exit (out of path): "f0".
"move exit mirror to side exit (in path): "e0",
"entrance mirror to front enterance: "c0",
"entrance mirror to side enterance: "d0"

Note: increasing steps in spectrometer prodeces increasing wavelength 
343993 = 739.5 nm
+5000 = 747.5 nm
+5000 = 756.3 nm
+10000 = 777.5 nm (12861 cm-1)
+5000 = 368993 = 787.1 nm (12704 cm-1) 5000 ~= 157 cm-1,
Fluorescence spike on card is 802.9 nm

8000 steps across the window. ~250 cm-1
Notch filter: 791 nm - 774 nm edge: 787-794 (12706, 12594 ~= 111 cm-1) 
'''

# while True:
#     try:
#         # loop continuously here for com input
#         com = input('Enter command - c to continue:\n')
#         if com == 'c':
#             break
#         instrument.write(com)
#         if com == 'A':
#             count = 100
#             while count > 0:
#                 print('Initialising: Sleeping for {} seconds'.format(count))
#                 time.sleep(1)
#                 count -= 1
#         response = instrument.read()
#         print('RES:', response)
#     except Exception as e:
#         print(e) 
