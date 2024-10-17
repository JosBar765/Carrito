import cv2 
from cvzone.HandTrackingModule import HandDetector 
import serial

COMPORT='COM7' # This comport can change eventually
ARDUINO = serial.Serial(COMPORT, 9600) # Baud rate always 9600
DETECTOR=HandDetector(detectionCon=0.8,maxHands=1) 
CAMERA=1 # Cameras are stored in a vector
VIDEO=cv2.VideoCapture(CAMERA)

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
    if fingerUp==[0,0,0,0,0]: 
        return "Adelante" 
    elif fingerUp==[1,0,0,0,1]: 
        return "Izquierda" 
    elif fingerUp==[0,1,1,0,0]: 
        return "Derecha" 
    elif fingerUp==[1,1,1,1,1]: 
        return "Atras" 
    else: 
        return "Parar"

def printDebugMessages(landmarkList):
    print(f"Dedos de la mano: {fingersUp(landmarkList)}") 
    print(f"Está volteada: {'Sí' if isHandFlipped(landmarkList) else 'No'}") 
    print(f"Acción carrito: {steeringIndication(fingersUp(landmarkList))}")
    print("-----------------------------------------------------------------------------------")

if __name__ == "__main__": 
    while True: 
        ret,frame=VIDEO.read() 
        hands,img=DETECTOR.findHands(frame, draw=True) 

        if hands: 
            landmarkList=hands[0]
            fingerUp=fingersUp(landmarkList) 

            cv2.putText(frame,f'Direccion: {steeringIndication(fingerUp)}',(10,450),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(255,255,255),1,cv2.LINE_AA) 

            moveCar(fingerUp) 

            printDebugMessages(landmarkList)

        cv2.imshow("VIDEO",frame) 
        key=cv2.waitKey(1) 
        if key==27: # Key 27 ASCII ('Esc') 
            break 

    VIDEO.release() 
    cv2.destroyAllWindows()