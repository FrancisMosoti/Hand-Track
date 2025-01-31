import mediapipe as mp
import time
import cv2
import numpy as np
import HandTracking as htm
import math

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# ____________________________
wCam, hCam = 640, 480
# ----------------------------


cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.8)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volumeRange = volume.GetVolumeRange()

minVolume = volumeRange[0]
maxVolume = volumeRange[1]

varVolume = 0
varBar = 400
varPer = 0

while True:
    success, img = cap.read()

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 10, (255, 0, 120), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 120), cv2.FILLED)
        cv2.circle(img, (cx, cy), 15, (255, 0, 120), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 5)

        length = math.hypot(x2 - x1, y2 - y1)
        # print(length)

        # hand range 30-200
        # volume range -95 - 0

        varVolume = np.interp(length, [30, 170], [minVolume, maxVolume])
        varBar = np.interp(length, [30, 170], [400, 150])
        varPer = np.interp(length, [30, 170], [0, 100])
        print(int(length), varVolume)
        volume.SetMasterVolumeLevel(varVolume, None)

        if (length < 30):
            cv2.circle(img, (cx, cy), 15, (100, 200, 10), cv2.FILLED)

    cv2.rectangle(img,(50, 150), (85, 400), (255, 0, 0), 4)
    cv2.rectangle(img, (50, int(varBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(varPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 40), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 150), 3)

    cv2.imshow('Img', img)
    cv2.waitKey(1)
