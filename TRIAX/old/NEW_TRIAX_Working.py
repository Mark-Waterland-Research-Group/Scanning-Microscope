import pyvisa
import time

# # Open a connection to the instrument
# rm = pyvisa.ResourceManager()
# print(rm.list_resources())
# instrument = rm.open_resource('GPIB0::1::INSTR')  # Replace with the actual VISA address of your instrument

# Set termination characters if needed (consult your instrument's manual)
# instrument.write_termination = '\n'
# instrument.read_termination = '\n'

class TRIAX_GPIB:


    def __init__(self) -> None:
        self.command_dict = {
        'goto': self.move_grating_to_wavelength,
        'lambda': self.get_grating_wavelength
        }

        # Open a connection to the instrument
        self.rm = pyvisa.ResourceManager()
        print(self.rm.list_resources())
        self.instrument = self.rm.open_resource('GPIB0::1::INSTR')  # Replace with the actual VISA address of your instrument

    def send_command(self, command, delay = 0.00001):
        self.instrument.write(command)
        # time.sleep(delay)
        response = self.instrument.read()
        # print(response)
        return response


    def get_grating_wavelength(self):
        response = self.send_command('H0')
        print('Grating is at position {}'.format())

    def connect(self):
        try:
            # Send the command (with proper termination character)
            # self.instrument.clear()
            # self.instrument.write('222')
            self.instrument.write('WHERE AM I')
            # time.sleep(0.0001)
            
            # Read the response
            state = self.instrument.read()
            print("Instrument state:", state)
            
        except pyvisa.VisaIOError as e:
            print("Error communicating with the instrument:", e)
            state = None

        if state == '\x02' or state == 'B' or state != None or state == 'o':
            print("Successfully connected to BOOT mode (Type {}). Switching to intelligent mode".format(str(state)))
            self.instrument.write('O2000')
            time.sleep(0.0001)
            res = self.instrument.read()
            print('Response: {}'.format(res))
        else:
            print('ERROR: Failed to identify state: "{}", type: {}'.format(state, type(state)))


        return state

    def main_loop(self):
        while True:
            try:
                com = input('Enter command - c to continue:\n')
                if com == 'c':
                    break
                self.instrument.write(com)
                if com == 'A':
                    count = 60
                    while count > 0:
                        print('Initialising: Sleeping for {} seconds'.format(count))
                        time.sleep(1)
                        count -= 1
                response = self.instrument.read()
                print('RES:', response)
            except Exception as e:
                print(e) 

    def send_command(self):
        pass



# instrument.clear()
triax = TRIAX_GPIB()

state = triax.connect()
triax.main_loop()

print("State variable:", state)
