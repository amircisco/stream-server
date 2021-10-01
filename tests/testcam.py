import psutil
import time
from multiprocessing import Process
import cv2
from Encoding import encrypt_cisco
import base64
import numpy as np


encoding=encrypt_cisco('amirjahani69')
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
def dec_quality(frame):
    ret,frame=cv2.imencode('.jpg', frame,encode_param)
    return frame.tobytes()

def code_data(frame):
    frame=encoding.encrypt(frame)
    json_frm=base64.b64encode(frame)

    return json_frm

i=0
while True:
    i+=1
    name="test/b{}.jpg".format(i)
    with open(name,'rb') as file:
        data=file.read()
        file.close()
    enc_frm=base64.b64decode(data)
    frame=encoding.decrypt(enc_frm)
    nparr=np.fromstring(frame, dtype='int8')
    crp=cv2.imdecode(nparr,cv2.IMREAD_COLOR)
    cv2.imshow("a",crp)
    cv2.waitKey(10)
"""cap=cv2.VideoCapture(0)

i=0
while True:
    i+=1
    ret,frame=cap.read()
    frame=cv2.resize(frame,(480,320))
    frame=dec_quality(frame)
    frame=code_data(frame)
    with open('test/b{}.jpg'.format(i),'wb') as file:
        file.write(frame)
        file.close()"""
