# import gpib_ctypes
import pyvisa
import time
# import serial

# Open a connection to the instrument
rm = pyvisa.ResourceManager()
rm.list_resources()
instrument = rm.open_resource('GPIB0::1::INSTR')  # Replace with the actual VISA address of your instrument
# instrument = rm.open_resource('COM6')  # Replace with the actual VISA address of your instrument
# s = serial.Serial(port='GPIB0::1::INSTR', timeout=5000)


def connect(instrument):
    instrument.write('WHERE AM I')
    time.sleep(0.0001)
    state = instrument.read()
    print(state)
    # breakpoint()
    return state


state = connect(instrument)
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



'''
# breakpoint()
# iniz= input('To begin initialization, enter "A", else continue')

# if iniz == 'A':
#     instrument.write('A')
#     time.sleep(10)
#     response = instrument.read()
#     print(response)
# else:
#     pass    
# breakpoint()

# breakpoint()

# Send the ASCII character to the instrument
# ascii_character = 'H0'  # Replace 'A' with the ASCII character you want to send
# instrument.write(ascii_character)
# response = instrument.read()
# print("Response:", response)

while True:
    try:
        # loop continuously here for com input
        com = input('Enter command - c to continue:\n')
        if com == 'c':
            break
        instrument.write(com)
        if com == 'A':
            count = 100
            while count > 0:
                print('Initialising: Sleeping for {} seconds'.format(count))
                time.sleep(1)
                count -= 1
        response = instrument.read()
        print('RES:', response)
    except Exception as e:
        print(e) 

count = 0
for x in range(10):
    instrument.write('F0,{}'.format(5000))
    response = instrument.read()
    print('moving to {}'.format(x*5000))
    # while response == 'b':
    # while True:
    #     # response = instrument.write('E')
    #     time.sleep(0.5)
    #     count+=1
    #     if count > 50:
    #         break
    time.sleep(0.5)
    # count += 1
        # print('waiting')
        
        # response = instrument.read()
        # if count > 50:
        #     print('timed out')
        #     break

    

    
    

while True:
    try:
        com = input('Enter command:\n')
        instrument.write(com)
        response = instrument.read()
        print('RES:', response)
    except Exception as e:
        print(e) 
        

breakpoint()
# Read the response from the instrument

try:
    response = instrument.read()
    print("Response:", response)
except pyvisa .VisaIOError as e:
    if e.error_code == pyvisa.constants.VI_ERROR_TMO:
        print("Timeout expired. Instrument did not respond.")
    else:
        print("An error occurred:", e)


# Close the instrument connection
instrument.close()


#k0,0,100 = move slit 100 steps relative
#j0,0<CR> = read slit pos
#i0,0,0<CR> = set slit position (0)