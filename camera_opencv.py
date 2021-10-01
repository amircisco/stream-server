import cv2
from base_camera import BaseCamera
import config
from Encoding import encrypt_cisco
import base64
import json
import time

class Camera(BaseCamera):
    video_source = 0
    width=config.def_width
    height=config.def_height
    stop=False
    @staticmethod
    def init_sourc(id):
        if(int(id)==1):
            Camera.video_source=config.sourc1
        elif(int(id)==2):
            Camera.video_source=config.sourc2
        elif(int(id)==3):
            Camera.video_source=config.sourc3
        elif(int(id)==4):
            Camera.video_source=config.sourc4

    @staticmethod
    def set_video_source(source):
        Camera.video_source=source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH,Camera.width)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT,Camera.height)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            if(Camera.stop==True):
                break
            _, img = camera.read()
            shape=Camera.width,Camera.height
            img=cv2.resize(img,shape)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), config.qu]
            ret,sender=cv2.imencode('.jpg', img,encode_param)
            sender=sender.tobytes()
            yield sender



