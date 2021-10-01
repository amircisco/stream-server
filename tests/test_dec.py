import threading
import time
import os
import random
from generate_key import GenerateKey
from Encoding import encrypt_cisco
import datetime
import base64
import config
import cv2

cap=cv2.VideoCapture(config.sourc2)
while True:
    ret,frame=cap.read()
    cv2.imshow("a",frame)
    cv2.waitKey(1)