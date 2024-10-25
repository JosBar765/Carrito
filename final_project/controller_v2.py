import cv2 
import serial
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
from cvzone.HandTrackingModule import HandDetector

def isPortOpen(port):
    try:
        arduino = serial.Serial(port, 9600)
        arduino.close()  # COMPORT test
        return True
    except serial.SerialException:
        return False

def camerasAvailable():
    return cv2.VideoCapture(0).isOpened()

def isHandFlipped(handLandmarkList): 
    # Consider 'flipped' as the back of the hand 
    orientationByDefinition=handLandmarkList['type'] 
    pinkyKnuckle_x=handLandmarkList['lmList'][17][0] 
    wrist_x=handLandmarkList['lmList'][0][0] 
    if orientationByDefinition=='Right': 
        orientationByPositioning='Right' if pinkyKnuckle_x<wrist_x else 'Left' 
    else: 
        orientationByPositioning='Left' if pinkyKnuckle_x>wrist_x else 'Right' 
    return orientationByDefinition!=orientationByPositioning 

def fingersUp(landmarkList): 
    fingerUp=DETECTOR.fingersUp(landmarkList) 
    if isHandFlipped(landmarkList): 
        fingerUp[0] = 1 if fingerUp[0]==0 else 0 
    return fingerUp 

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

def steeringIndication(fingerUp): 
    if fingerUp == [0, 0, 0, 0, 0]:
        return "Adelante", "icons/adelante.jpg"
    elif fingerUp == [1, 0, 0, 0, 1]:
        return "Izquierda", "icons/izquierda.jpg"
    elif fingerUp == [0, 1, 1, 0, 0]:
        return "Derecha", "icons/derecha.jpg"
    elif fingerUp == [1, 1, 1, 1, 1]:
        return "Atras", "icons/atras.jpg"
    else:
        return "Parar", "icons/parar.png"

def printDebugMessages(landmarkList):
    print(f"Dedos de la mano: {fingersUp(landmarkList)}") 
    print(f"Está volteada: {'Sí' if isHandFlipped(landmarkList) else 'No'}") 
    print(f"Acción carrito: {steeringIndication(fingersUp(landmarkList))}")
    print("-----------------------------------------------------------------------------------")

def clearConsole():
    subprocess.run("cls", shell=True)

if __name__ == "__main__":
    COMPORT='COM7' # This comport can change eventually
    
    if not isPortOpen(COMPORT):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error de Puerto", f"El puerto {COMPORT} no está disponible.")
        sys.exit()

    if not camerasAvailable():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error de Cámara", f"El dispositivo no cuenta con una cámara.")
        sys.exit()
    
    ARDUINO = serial.Serial(COMPORT, 9600)
    DETECTOR=HandDetector(detectionCon=0.8,maxHands=1) 
    VIDEO=cv2.VideoCapture(1) if cv2.VideoCapture(1).isOpened() else cv2.VideoCapture(0)
    
    clearConsole()

    while True: 
        ret,frame=VIDEO.read() 
        hands,img=DETECTOR.findHands(frame, draw=True) 

        if hands: 
            landmarkList=hands[0]
            fingerUp=fingersUp(landmarkList) 
            direction, icon_path = steeringIndication(fingerUp)

            cv2.putText(frame, f'Direccion: {direction}', (10, 450), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_AA)
            icon=cv2.imread(icon_path)
            icon_dimensional=100
            icon = cv2.resize(icon, (icon_dimensional, icon_dimensional))
            icon_position=[10, 300] # [vertical_value, horizontal_value]
            frame[icon_position[0]:icon_position[0]+icon_dimensional, icon_position[1]:icon_position[1]+icon_dimensional] = icon

            moveCar(fingerUp) 
            
            printDebugMessages(landmarkList)

        cv2.imshow("VIDEO",frame)
        key=cv2.waitKey(1) 
        if key==27: # Key 27 ASCII ('Esc') 
            ARDUINO.write(b'X') # Turn off all the leds
            break 

    VIDEO.release() 
    cv2.destroyAllWindows()
    clearConsole()