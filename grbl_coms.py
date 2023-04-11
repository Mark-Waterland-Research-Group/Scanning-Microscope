# GRBL commands
import serial
import serial.tools.list_ports
import time
import numpy as np
import matplotlib.pyplot as plt

def open_serial_port(baudrate=115200):
    # Scan for available COM ports
    ports = list(serial.tools.list_ports.comports())

    if len(ports) == 0:
        print("No COM ports found")
    else:
        for port in ports:
            try:
                port = ports[0].device
                ser = serial.Serial(port, timeout=1)
                print(f"Connected to {port}")
                return ser
            except Exception as e:
                print(e)
    
            




class GRBL_comms:

    def __init__(self):
        self.serial = open_serial_port()

    def send_gcode(self, code, delay = None):
        '''# REFACTOR'''
        if isinstance(code, str):
            print('Sending: ' + str(code))
            self.serial.write(str.encode(str(code)+'\n'))
            grbl_out = self.serial.readline() # Wait for grbl response with carriage return
            print(' : ' + str(grbl_out.strip()))
        elif isinstance(code, list):
            for item in code:
                print('Sending: ' + str(item))
                self.serial.write(str.encode(str(item)+'\n'))
                grbl_out = self.serial.readline() # Wait for grbl response with carriage return
                print(' : ' + str(grbl_out.strip()))
                if delay:
                    time.sleep(delay)
        else:
            print('Incorrect code format: please enter gcode as a string or list of strings.')


    def move_absolute(self, currentPos, newPos):
        # send_gcode('G90')
        if isinstance(newPos, tuple):
            xPos, yPos = newPos
            if currentPos[0] != xPos and currentPos[1] != yPos:
                self.send_gcode('G1 X'+str(xPos)+' Y'+str(yPos))
            # currentPos = update_pos(currentPos, pos)
            if currentPos[0] != xPos:
                # xPos = xPos.lstrip('xX')
                self.send_gcode('G1 X'+str(xPos))
                # currentPos = update_pos_x(currentPos, pos)
            if currentPos[1] != yPos:
                # yPos = xPos.lstrip('yY')
                self.send_gcode('G1 Y'+str(yPos))
                # currentPos = update_pos_y(currentPos, pos)
        if isinstance(newPos, str):
            if 'x' in newPos or 'X' in newPos:
                xPos = newPos.lstrip('xX')
                self.send_gcode('G1 X'+str(xPos))
                # currentPos = update_pos_x(currentPos, pos)
            if 'y' in pos or 'Y' in pos:
                yPos = newPos.lstrip('yY')
                self.send_gcode('G1 Y'+str(yPos))
                # currentPos = update_pos_y(currentPos, pos)
        return newPos

    def update_pos(self, currentPos, posData):
        if isinstance(posData, tuple):
            currentPos = (float(currentPos[0])+float(posData[0]), float(currentPos[1])+float(posData[1]))
        print("New position:", str(currentPos))
        # longAxis = max(abs(posData[0], abs(posData[1])))
        # travelTime = float(longAxis)*.08
        # if travelTime <= 1:
        #     travelTime = 1
        return currentPos

    def update_pos_x(currentPos, pos):
        currentPos = (float(currentPos[0])+float(pos), float(currentPos[1]))
        print("New position:", str(currentPos))
        return currentPos

    def update_pos_y(currentPos, pos):
        currentPos = (float(currentPos[0]), float(currentPos[1])+float(pos))
        print("New position:", str(currentPos))
        return currentPos

    def interpret_move(currentPos, command):
        if isinstance(command, tuple):
            newPos = update_pos(currentPos, command)
            return newPos
        xPos, yPos = False, False
        for x in ["x", "X"]:
            if x in command:
                xIndex = command.index(x)
                xPos = True
        for y in ["y", "Y"]:
            if y in command:
                yIndex = command.index(y)
                yPos = True

        if xPos == True and yPos == True:
            xPos = command[xIndex+1:yIndex]
            yPos = command[yIndex+1:]
            # print("new pos: ("+xPos+',', yPos+")")
            newPos = update_pos(currentPos, (xPos, yPos))
        if xPos == True and yPos == False:
            xPos = command[xIndex+1:]
            # print("new pos: X", xPos)
            newPos = update_pos_x(currentPos, xPos)
        if xPos == False and yPos == True:
            yPos = command[yIndex+1:]
            # print("new pos: Y", yPos)
            newPos = update_pos_y(currentPos, yPos)


        return newPos




    def runLinescan(self, lineScanList, acquisitionTime):
        for pos in lineScanList:
            currentPos = pos
            self.move_absolute(pos)
            time.sleep(acquisitionTime)
        print("Linescan complete")
        time.sleep(10)
        quit()

    '''Needs rewriting:
    1. move "s." to automation module/class'''


    def send_lightOn(self, power = 255):
        self.serial.write(str.encode('M106 P2 S{}\n'.format(power)))
        grbl_out = self.serial.readline() # Wait for grbl response with carriage return

    def z_focus(self):
        self.serial.write(str.encode('G91\n'))
        while True:
            zStep = input('Enter focus step in microns. Type "done" to break loop.\n')
            try:
                float(zStep)
                if -10 <= float(zStep) <= 10:
                    self.serial.write(str.encode('G1 Z{}\n'.format(zStep)))
                    grbl_out = self.serial.readline()
                else:
                    print('Illegal step size - enter number between -10 and 10')
            except:
                if zStep == 'done':
                    self.serial.write(str.encode('G90\n'))
                    break
                else:
                    print('Number not recognised - please enter a float.')

    def send_ramanMode(self):
        self.serial.write(str.encode('T0\n'))
        grbl_out = self.serial.readline() # Wait for grbl response with carriage return
        self.serial.write(str.encode('G1 E-125\n'))
        grbl_out = self.serial.readline() # Wait for grbl response with carriage return
        # adjustPower(power = 'max')

    def send_imageMode(self):

        self.serial.write(str.encode('T0\n'))
        grbl_out = self.serial.readline() # Wait for grbl response with carriage return
        self.serial.write(str.encode('G1 E125\n'))
        grbl_out = self.serial.readline() # Wait for grbl response with carriage return
        # adjustPower(power = 'min')


    def initializeGRBL(self, motorSpeed = 1000):
        self.serial.flushInput()  # Flush startup text in serial input
        # set motor speed
        self.serial.write(str.encode('G90 F{}'.format(motorSpeed)+'\n'))
        grbl_out = self.serial.readline() # Wait for grbl response with carriage return
        print('Moving in absolute coordinates : ' + str(grbl_out.strip()))

        self.serial.write(str.encode('G92 X0 Y0 Z0 E0\n')) # sets absolute coordinates for all axes to zero
        grbl_out = self.serial.readline()

if __name__ == '__main__':
    ser = open_serial_port()
    data = ser.write(b'hello')

    inn = ser.readline()
    breakpoint()