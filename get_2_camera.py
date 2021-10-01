from distutils.command.config import config
import cv2
import numpy as np
import config
import threading,time
from Encoding import encrypt_cisco
import base64
import traceback
from generate_key import GenerateKey
from initConfig import initConfig
import CustomTime
import os
import datetime
import traceback
from kivy.clock import Clock

class get_2_camera():
    def __init__(self):
        self.w=config.def_width
        self.h=config.def_height
        self.w_detect=config.def_width_detect
        self.h_detect=config.def_height_detect
        self.DATA=b""
        self.DATA_3G_1=b""
        self.DATA_3G_2=b""
        self.conf=initConfig()
        self.gen=GenerateKey()
        key=self.conf.get_update_config('key')
        self.encoding=encrypt_cisco(self.gen.get_uniq_key(key))
        none_frame=cv2.imread(config.none_img)
        none_frame=cv2.resize(none_frame,(self.w,self.h))
        self.none_frame_detect=cv2.resize(none_frame,(self.w_detect,self.h_detect))
        self.none=none_frame
        self.frame1_code=none_frame
        self.frame2_code=none_frame
        self.frame3_code=none_frame
        self.frame4_code=none_frame

        self.frame1_org=none_frame
        self.frame2_org=none_frame
        self.frame3_org=none_frame
        self.frame4_org=none_frame

        self.frame1_detect=cv2.resize(none_frame,(self.w_detect,self.h_detect))
        self.frame2_detect=self.frame1_detect
        self.frame3_detect=self.frame1_detect
        self.frame4_detect=self.frame1_detect
        self.stop=False
        self.start1_bool=True
        self.start2_bool=True
        self.start3_bool=True
        self.start4_bool=True
        self.DATA_DETECT=b""
        self.DATA_DETECT_3G_1=b""
        self.DATA_DETECT_3G_2=b""
        self.count_black=25
        self.soojeh_name=self.conf.get_update_config('soojeh_name')
        if len(self.soojeh_name)<1:
            self.soojeh_name="Nasr"
            self.conf.set_new_val_data('soojeh_name','Nasr')
        self.do_video_save=str(config.do_save_video_in_sender)
        self.START_TIME_SAVE_VIDEO=datetime.datetime.now()
        self.LAST_TIME_SAVE_VIDEO=datetime.datetime.now()
        self.stop_save_video=True
        self.init_video_file_names()



    def init_video_file_names(self):
        w=int(self.conf.get_update_config('def_width'))
        h=int(self.conf.get_update_config('def_height'))
        pre_dir1="media/"+self.soojeh_name+"/cam1/"
        dir1=self.check_dir_video(pre_dir1)
        self.file_video_1=dir1+"/"+CustomTime.get_j_time()+".avi"
        self.out1 = cv2.VideoWriter(self.file_video_1,cv2.VideoWriter_fourcc('M','J','P','G'), 15, (w,h))

        pre_dir2="media/"+self.soojeh_name+"/cam2/"
        dir2=self.check_dir_video(pre_dir2)
        self.file_video_2=dir2+"/"+CustomTime.get_j_time()+".avi"
        self.out2 = cv2.VideoWriter(self.file_video_2,cv2.VideoWriter_fourcc('M','J','P','G'), 15, (w,h))

        pre_dir3="media/"+self.soojeh_name+"/cam3/"
        dir3=self.check_dir_video(pre_dir3)
        self.file_video_3=dir3+"/"+CustomTime.get_j_time()+".avi"
        self.out3 = cv2.VideoWriter(self.file_video_3,cv2.VideoWriter_fourcc('M','J','P','G'), 15, (w,h))

        pre_dir4="media/"+self.soojeh_name+"/cam4/"
        dir4=self.check_dir_video(pre_dir4)
        self.file_video_4=dir4+"/"+CustomTime.get_j_time()+".avi"
        self.out4 = cv2.VideoWriter(self.file_video_4,cv2.VideoWriter_fourcc('M','J','P','G'), 15, (w,h))

        self.stop_save_video=False

    def update_w_h(self,w,h,w_detect,h_detect):
        self.w=w
        self.h=h
        self.w_detect=w_detect
        self.h_detect=h_detect
        self.frame1_detect=b""
        self.frame2_detect=b""
        self.frame3_detect=b""
        self.frame4_detect=b""

        none_frame=cv2.imread(config.none_img)
        none_frame=cv2.resize(none_frame,(self.w,self.h))
        self.frame1_code=none_frame
        self.frame2_code=none_frame
        self.frame3_code=none_frame
        self.frame4_code=none_frame

    def run(self):
        print("init all camera after 5 second...")
        self.th1=threading.Thread(target=self.start1)
        self.th1.start()
        time.sleep(1)
        self.th2=threading.Thread(target=self.start2)
        self.th2.start()
        time.sleep(2)
        self.thmix=threading.Thread(target=self.mix_frame)
        self.thmix.start()

    def start1(self):
        cam=1
        repeat=0
        try:
            self.cap1=cv2.VideoCapture(self.conf.get_update_config('sourc1'))
            while self.start1_bool==True:
                self.check_for_reset_video()
                ret,frame1=self.cap1.read()
                if ret:
                    self.frame1_org=cv2.resize(frame1,(self.w,self.h))
                    if self.do_video_save=="1" and self.stop_save_video==False:
                        self.out1.write(self.frame1_org)
                        self.LAST_TIME_SAVE_VIDEO=datetime.datetime.now()
                    self.frame1_bytes=self.dec_quality(self.frame1_org)
                    self.frame1_code=self.code_data(self.frame1_bytes)
                    self.frame1_detect=cv2.resize(frame1,(self.w_detect,self.h_detect))
                    cv2.waitKey(1)
                else :
                    self.frame1_org=self.none
                    repeat+=1
                    time.sleep(1)
                    if repeat>self.count_black:
                        repeat=0
                        print("camera {} dont get frame".format(cam))
                        self.start1_bool=False


        except:
            traceback.print_exc()
            print("camera {} is not running...".format(cam))

    def start2(self):
        cam=2
        repeat=0
        try:
            self.cap2=cv2.VideoCapture(self.conf.get_update_config('sourc2'))
            while self.start2_bool==True:
                ret,frame2=self.cap2.read()
                if ret:
                    self.frame2_org=cv2.resize(frame2,(self.w,self.h))
                    if self.do_video_save=="1" and self.stop_save_video==False:
                        self.out2.write(self.frame2_org)
                    self.frame2_bytes=self.dec_quality(self.frame2_org)
                    self.frame2_code=self.code_data(self.frame2_bytes)
                    self.frame2_detect=cv2.resize(frame2,(self.w_detect,self.h_detect))
                    cv2.waitKey(1)
                else :
                    self.frame2_org=self.none
                    repeat+=1
                    time.sleep(1)
                    if repeat>self.count_black:
                        repeat=0
                        print("camera {} dont get frame".format(cam))
                        self.start2_bool=False


        except:
            traceback.print_exc()
            print("camera {} is not running...".format(cam))

    def mix_frame(self):
        try:
            while self.stop==False:
                tm0=np.concatenate((self.frame1_org,self.frame2_org),axis=1)
                tm1=np.concatenate((self.frame3_org,self.frame4_org),axis=1)
                frame=np.concatenate((tm0,tm1),axis=0)
                frame=self.dec_quality(frame)
                frame=self.code_data(frame)
                self.DATA=frame
                self.DATA_3G_1=frame
                self.DATA_3G_2=frame
                #g1=self.dec_quality(tm0)
                #g2=self.dec_quality(tm1)
                #self.DATA_3G_1=self.code_data(g1)
                #self.DATA_3G_2=self.code_data(g2)


                tmp0=np.concatenate((self.frame1_detect,self.frame2_detect),axis=1)
                tmp1=np.concatenate((self.frame3_detect,self.frame4_detect),axis=1)
                _frame=np.concatenate((tmp0,tmp1),axis=0)
                self.DATA_DETECT=_frame
                self.DATA_DETECT_3G_1=_frame
                self.DATA_DETECT_3G_2=_frame
                #tmp=np.concatenate((self.none_frame_detect,self.none_frame_detect),axis=1)
                #self.DATA_DETECT_3G_1=np.concatenate((tmp0,tmp),axis=0)
                #self.DATA_DETECT_3G_2=np.concatenate((tmp,tmp1),axis=0)
        except:
            traceback.print_exc()


    def stop_video(self):
        try:
            self.stop_save_video=True
            self.out1.release()
            self.out2.release()
            #self.out3.release()
            #self.out4.release()
        except:
            traceback.print_exc()

    def check_for_reset_video(self):
        diff=(self.LAST_TIME_SAVE_VIDEO-self.START_TIME_SAVE_VIDEO).total_seconds()
        if diff > 3600:
            try:
                self.stop_video()
                self.START_TIME_SAVE_VIDEO=self.LAST_TIME_SAVE_VIDEO
                self.init_video_file_names()
            except:
                traceback.print_exc()


    def check_dir_video(self,pre_dir):
        year=CustomTime.get_j_year()
        month=CustomTime.get_j_month()
        day=CustomTime.get_j_day()
        dir=pre_dir+"video/"+year+"/"+month+"/"+day
        os.makedirs(dir,exist_ok=True)
        return dir

    def dec_quality(self,frame):
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), int(self.conf.get_update_config('qu'))]
        ret,frame=cv2.imencode('.jpg', frame,encode_param)
        return frame.tobytes()

    def code_data(self,frame):
        frame=self.encoding.encrypt(frame)
        json_frm=base64.b64encode(frame)
        data=json_frm.decode('utf-8')
        data=config.start_spl+data+config.end_spl
        data=data.encode(encoding='utf-8')

        return data