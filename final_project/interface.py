import serial

COMPORT='COM7'
ARDUINO = serial.Serial(COMPORT, 9600) 

def moveCar(fingerUp): 
    if fingerUp==[0,0,0,0,0]: 
        ARDUINO.write(b'F')
    elif fingerUp==[1,0,0,0,1]: 
        ARDUINO.write(b'L')
    elif fingerUp==[0,1,1,0,0]: 
        ARDUINO.write(b'R')
    elif fingerUp==[1,1,1,1,1]: 
        ARDUINO.write(b'B')
    else: 
        ARDUINO.write(b'S')