import serial
import serial.tools.list_ports
import time



def open_serial_port(baudrate=115200):
    # Scan for available COM ports
    ports = list(serial.tools.list_ports.comports())

    if len(ports) == 0:
        print("No COM ports found")
    else:
        for port in ports:
            try:
                port = ports[0].device
                ser = serial.Serial(port, baudrate=baudrate, timeout=1, bits=8, parity=None, stop=1)
                print(f"Connected to {port}")
                return ser
            except Exception as e:
                print(e)
    

# open the serial connection to the Raspberry Pi
# ser = serial.Serial('/dev/ttyUSB0', 115200)
# ser = open_serial_port()

# import serial
ports = list(serial.tools.list_ports.comports())
print(ports)
for port in ports:
    print(port.device)
    ser = serial.Serial(port.device, 115200, timeout=1)

# open the serial connection to the Raspberry Pi
time.sleep(1)
# ser.flush()

# send a command to the Raspberry Pi
command = b'some_command'

ser.write(str.encode('some_command'))
# response = ser.readline()
# print(response)
# response = ser.readline()
# wait for a response from the Raspberry Pi
# for _ in enumerate(range(10)):


# do something with the response

# close the serial connection
ser.close()

