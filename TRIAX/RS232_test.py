import gpib_ctypes
import pyvisa
import time
import serial

# Open a connection to the instrument
rm = pyvisa.ResourceManager()
rm.list_resources()
instrument = rm.open_resource('COM6')  # Replace with the actual VISA address of your instrument
# s = serial.Serial(port='GPIB0::1::INSTR', timeout=5000)

# breakpoint()

# breakpoint()

# Send the ASCII character to the instrument
# ascii_character = 'H0'  # Replace 'A' with the ASCII character you want to send
# instrument.write(ascii_character)
# response = instrument.read()
# print("Response:", response)

while True:
    try:
        com = input('Enter command - c to continue:\n')
        if com == 'c':
            break
        instrument.write(com)
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