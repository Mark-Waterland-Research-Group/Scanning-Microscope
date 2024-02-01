import pyvisa 
# rm = pyvisa.ResourceManager()
# rm.list_resources()
# # triax = rm.open_resource('ASRL3::INSTR')
# triax = rm.open_resource('COM6')

# breakpoint()
# triax.write(" ")
# print(triax.read())


import serial
import time

# Replace 'COM3' with the correct port name on your computer.
# The baudrate should be set to the value specified by your spectrometer's manual.
ser = serial.Serial('COM6', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=1)

# Function to send commands to the spectrometer
def send_command(command):
    ser.write(command.encode())
    time.sleep(0.1)  # Wait for the command to be sent
    response = ser.read(ser.inWaiting())  # Read the response
    return response.decode()

# Example command, replace with actual commands for your spectrometer
while True:
    command = input('Enter command:')
    response = send_command(command)
    print(response)
    read = ser.read()
    print(read)

# Close the serial connection
ser.close()
