import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import os
import pyautogui


#############################
wCam, hCam = 640, 480
frameR = 100 # frame Reduction
smoothening = 7
##############################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

# Volume variables
previous_length = 0
previous_vol = 0
volume_muted = False


cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)

detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
#print(wScr, hScr)
while True:
    #1. Find hand landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    #2. Get the tip of the index and the middle fingers
    if len(lmList)!=0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        #print(x1, y1, x2, y2)

    #3. Check which finger are up
        fingers = detector.fingersUp()
        #print(fingers)
        cv2.rectangle(img, (frameR, frameR), (wCam-frameR, hCam-frameR), (255,0,255), 2)

    #4. Only index finger: Moving mode
        if fingers[1]==1 and fingers[2]==0:

            #5. Convert Coordinates
            x3 = np.interp(x1, (frameR,wCam-frameR), (0,wScr))
            y3 = np.interp(y1, (frameR,hCam-frameR), (0,hScr))

            #6. Smoothen Valuse
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            #7. Move mouse
            autopy.mouse.move(wScr-clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

    #Volume control

        if fingers[1] == 1 and fingers[2] == 1:
    # 15. Find distance between fingers
            length, img, lineInfo = detector.findDistance(4, 8, img)

    # 6. Volume Range 0 - 100
            vol = np.interp(length, [20, 200], [0, 100])
            

    # 7. Set volume
            if vol < previous_vol:
                for i in range(int(previous_vol - vol)):
                    pyautogui.press('volumedown')
                previous_vol = int(vol)
            elif vol > previous_vol:
                for i in range(int(vol - previous_vol)):
                    pyautogui.press('volumeup')
                previous_vol = int(vol)





            # if int(vol) != previous_vol:
            #     pyautogui.press(['volumedown', 'volumeup'][int(vol) > previous_vol])
            #     previous_vol = int(vol)


    
   
    #11. Frame rate
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0),3)
   
    #12. Display
    
    cv2.imshow("AI Virtual Mouse", img)
    if cv2.waitKey(1)  == 27:
        break
cap.release()
cv2.destroyAllWindows()  