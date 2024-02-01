# import gpib_ctypes
import pyvisa
import time
import serial

# Open a connection to the instrument
rm = pyvisa.ResourceManager()
rm.list_resources()
instrument = rm.open_resource('COM12')  # Replace with the actual VISA address of your instrument
# s = serial.Serial(port='COM12', timeout=5000)

# breakpoint()
breakpoint()
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

# import serial
# import time

# # Replace 'COM3' with the correct port name on your computer.
# # The baudrate should be set to the value specified by your spectrometer's manual.
# ser = serial.Serial('COM12', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=1)
# ser.flushInput()
# ser.flushOutput()

# ser.write(' \r'.encode())
# initial = ser.read(ser.inWaiting())
# print('initial:', initial.decode())

# # Function to send commands to the spectrometer
# def send_command(command):
#     command = command + '\r'  # Add a carriage return to the end of the command
#     ser.write(command.encode())
#     time.sleep(0.01)  # Wait for the command to be sent
#     breakpoint()
#     response = ser.read(ser.inWaiting())  # Read the response
#     return response.decode()

# # Example command, replace with actual commands for your spectrometer
# while True:
#     command = input('Enter command:')
#     response = send_command('YOUR_COMMAND_HERE')
#     print(response)

# # Close the serial connection
# ser.close()
