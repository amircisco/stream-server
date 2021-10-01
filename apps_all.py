import socket
import os
import threading
from get_all_camera import get_all_camera
try:
    import config
except:
    with open('config1.py','r') as file:
        data=file.read()
        file.close()
        with open('config.py','w+') as file1:
            file1.write(data)
            file1.close()
    import config
import base64
from Encoding import encrypt_cisco
import time
import datetime
import shutil
from distutils.dir_util import copy_tree
from darkflow.net.build import TFNet
import cv2
import numpy as np
import traceback
from interval_send_ip_sender import interval_send_ip_sender
import win32api
from initConfig import initConfig
from generate_key import GenerateKey
import psutil
from queue import Queue

class Server():
    def __init__(self):
        super(Server,self).__init__()
        self.conf=initConfig()
        self.ip=self.conf.get_update_config('sender_ip')
        self.port=int(self.conf.get_update_config('port_rec_video_frame'))
        self.ip_port=(self.ip,self.port)
        self.stop_listen=False
        self.stop=False
        self.w=config.def_width
        self.h=config.def_height
        self.buf_size=1024*58
        self.data_all=""
        self.list_detections=[]
        self.ip_port_tcp=(config.reciver_ip,config.port_rec_detect_frame)
        self.flg_detection=False
        self.index_for_detection=0
        self.stop_send_camera=False
        self.stop_send_camera_viewer=False
        self.check_detection_state=False
        self.is_runnin=False
        self.wich_3g=0
        self.gen=GenerateKey()
        self.wait_between_every_frame=float(self.conf.get_update_config('wait_between_every_frame'))
        self.qu_detect=Queue()
        self.flg_first_socket_send_detection=False


    def run(self):
        print("initialize tfnet...")
        self.init_tfnet()
        print("successfull tfnet")
        second=10
        print("search for ip in {} second".format(second))
        while second>0:
            print("start at {} second...".format(second))
            second-=1
            time.sleep(1)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.ip_port)
        self.socket.listen()
        print("Listen for socket in ip_port {}".format(self.ip_port))
        while self.stop==False:
            try:
                conn ,addr= self.socket.accept()
                data=conn.recv(1024)
                if(data.decode()=="abcdef"):
                    thread_run_camera= threading.Thread(target=self.run_camera,args=(conn,addr))
                    thread_run_camera.start()
                elif(data.decode().startswith("zxcvbn")):
                    self.wich_3g=data.decode().split('+')[1]
                    self.thread_send_camera= threading.Thread(target=self.send_camera,args=(conn,addr))
                    self.thread_send_camera.start()
                elif(data.decode().startswith("vxcvbn")):
                    arr_acept_user=self.conf.get_update_config('list_accept_users').split(',')
                    if addr[0] in arr_acept_user:
                        wich_3g=data.decode().split('+')[1]
                        self.thread_send_camera= threading.Thread(target=self.send_camera_viewr_only,args=(conn,addr,wich_3g))
                        self.thread_send_camera.start()
                    else:
                        sender_data='00'.encode('utf-8')
                        conn.sendall(sender_data)
                        conn.close()

                elif(data.decode().startswith("a@a@a@")):
                    threading.Thread(target=self.sync_info_config,args=(conn,addr)).start()
                elif(data.decode().startswith("b@b@b@")):
                    threading.Thread(target=self.update_info_config,args=(conn,addr)).start()
                elif(data.decode().startswith("c@c@c@")):
                    threading.Thread(target=self.sync_key_code,args=(conn,addr)).start()
                elif(data.decode().startswith("d@d@d@")):
                    threading.Thread(target=self.update_users_can_view,args=(conn,addr)).start()
                elif(data.decode().startswith("e@e@e@")):
                    threading.Thread(target=self.get_dir_and_soojeh_list,args=(conn,addr)).start()
                elif(data.decode().startswith("f@f@f@")):
                    threading.Thread(target=self.start_copy_paste,args=(conn,addr)).start()
            except:
                traceback.print_exc()


    def start_copy_paste(self,conn,addr):
        try:
            res='00'
            encoding=encrypt_cisco('qwe!@#rty$%^uio&*(oiuytrewq(*&^%$#@!')
            sender_data='88'.encode('utf-8')
            sender_data=encoding.encrypt(sender_data)
            conn.sendall(sender_data)
            while True:
                try:
                    data=conn.recv(5124)
                    data=encoding.decrypt(data)
                    new_data=data.decode('utf-8')
                    arr=new_data.split(self.conf.get_update_config('communicate_spliter'))
                    if len(arr)==3:
                        t=arr[0]
                        src=arr[1]
                        tmp=arr[1].split('/')
                        dst=arr[2]+arr[1].split('/')[len(tmp)-2]
                        if os.path.isdir(src):
                            total_bytes,total_kb,total_mb,total_gb=self.get_size_dir(src)
                            total_size_dst,used_size_dst,free_size_dst=self.get_size_drive(dst[0]+":/")
                            if free_size_dst>total_bytes:
                                #copy_tree(src,dst)
                                th_copy=threading.Thread(target=copy_tree,args=(src,dst))
                                th_copy.start()
                                tmp_data=str('11@'+str(total_bytes)).encode('utf-8')
                                tmp_data=encoding.encrypt(tmp_data)
                                conn.sendall(tmp_data)
                                while th_copy.is_alive():
                                    size_now=self.get_size_drive(dst[0]+":/")[1]
                                    tmp_data=str("23@"+str(size_now-used_size_dst)).encode('utf-8')
                                    tmp_data=encoding.encrypt(tmp_data)
                                    conn.sendall(tmp_data)
                                    time.sleep(1)
                                th_cut=threading.Thread
                                if t=="cut":
                                    #shutil.rmtree(src)
                                    th_cut=threading.Thread(target=shutil.rmtree,args=(src,))
                                    th_cut.start()
                                    while th_cut.is_alive():
                                        tmp_data="12".encode('utf-8')
                                        conn.sendall(encoding.encrypt(tmp_data))
                                        time.sleep(1)
                                res="88"
                            else:
                                res="77"
                except:
                    traceback.print_exc()
                sender_data=res.encode('utf-8')
                sender_data=encoding.encrypt(sender_data)
                conn.sendall(sender_data)
                break
            conn.close()
        except:
            traceback.print_exc()



    def get_dir_and_soojeh_list(self,conn,addr):
        try:
            list_soojeh=""
            if os.path.isdir('media'):
                if len(os.listdir('media'))>0:
                    list_soojeh=','.join(os.listdir('media'))
            list_drives=','.join(self.get_drive_list())
            ppath=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')
            if len(ppath)<1:
                ppath=os.getcwd().replace('\\','/')
            encoding=encrypt_cisco('qwe!@#rty$%^uio&*(oiuytrewq(*&^%$#@!')
            sender_data=ppath+self.conf.get_update_config('communicate_spliter')+list_soojeh+self.conf.get_update_config('communicate_spliter')+list_drives
            sender_data=sender_data.encode('utf-8')
            sender_data=encoding.encrypt(sender_data)
            conn.sendall(sender_data)
            conn.close()
        except:
            traceback.print_exc()


    def update_users_can_view(self,conn,addr):
        try:
            encoding=encrypt_cisco('qwe!@#rty$%^uio&*(oiuytrewq(*&^%$#@!')
            sender_data='88'.encode('utf-8')
            sender_data=encoding.encrypt(sender_data)
            conn.sendall(sender_data)
            while True:
                data=conn.recv(5124)
                data=encoding.decrypt(data)
                new_data=data.decode('utf-8')
                self.conf.set_new_val_data('list_accept_users',new_data)
                sender_data='88'.encode('utf-8')
                sender_data=encoding.encrypt(sender_data)
                conn.sendall(sender_data)
                break
            conn.close()
        except:
            traceback.print_exc()


    def sync_key_code(self,conn,addr):
        try:
            data=str(self.conf.get_update_config('key'))
            encoding=encrypt_cisco('qwe!@#rty$%^uio&*(oiuytrewq(*&^%$#@!')
            data=encoding.encrypt(data.encode('utf-8'))
            conn.sendall(data)
            conn.close()
        except:
            traceback.print_exc()

    def update_info_config(self,conn,addr):
        try:
            encoding=encrypt_cisco('qwe!@#rty$%^uio&*(oiuytrewq(*&^%$#@!')
            sender_data='88'.encode('utf-8')
            sender_data=encoding.encrypt(sender_data)
            conn.sendall(sender_data)
            while True:
                data=conn.recv(5124)
                data=encoding.decrypt(data)
                new_data=data.decode('utf-8')
                old_data=self.conf.get_data()
                data=new_data+'br=""'+old_data.split('br=""')[1]
                self.conf.write_data(data)
                sender_data='88'.encode('utf-8')
                sender_data=encoding.encrypt(sender_data)
                conn.sendall(sender_data)
                break
            conn.close()
            self.stop_and_reset_apps_all()
        except:
            traceback.print_exc()

    def stop_and_reset_apps_all(self):
        try:
            self.wait_between_every_frame=float(self.conf.get_update_config('wait_between_every_frame'))
            if self.is_runnin:
                self.is_runnin=False
                if self.stop_send_camera==False:
                    self.stop_send_camera=True
                if self.stop_send_camera_viewer==False:
                    self.stop_send_camera_viewer=True

                if self.check_detection_state==False:
                    self.check_detection_state=True
                    self.thread_detection.join()
                    self.thread_send_socket_detect.join()
                self.all_camera.start1_bool=False
                self.all_camera.th1.join()
                self.all_camera.start2_bool=False
                self.all_camera.th2.join()
                self.all_camera.start3_bool=False
                self.all_camera.th3.join()
                self.all_camera.start4_bool=False
                self.all_camera.th4.join()
                self.all_camera.stop=True
                self.all_camera.thmix.join()
                self.all_camera.stop_save_video=True
                self.all_camera.stop_video()
                self.is_runnin=True
                self.all_camera=get_all_camera()
                self.all_camera.run()
        except:
            traceback.print_exc()

    def sync_info_config(self,conn,addr):
        try:
            encoding=encrypt_cisco('qwe!@#rty$%^uio&*(oiuytrewq(*&^%$#@!')
            data=self.conf.get_data()
            data=data.encode('utf-8')
            data=encoding.encrypt(data)
            conn.sendall(data)
            conn.close()
        except:
            traceback.print_exc()


    def run_camera(self,conn,addr):
        try:
            if self.is_runnin==True:
                msg1="camera_is_running..."
                response="rtxz"

                print(msg1)
                response=response.encode(encoding='utf-8')
            elif self.is_runnin==False:
                self.is_runnin=True
                msg1="camera_started"
                print(msg1)
                response="bqyu"
                response=response.encode(encoding='utf-8')
                self.all_camera=get_all_camera()
                self.all_camera.run()

            timer=3
            print("wait for {} second until run camera...".format(timer))
            while timer>0:
                print(timer)
                timer-=1
                time.sleep(1)
            conn.sendall(response)
            conn.close()
        except:
            traceback.print_exc()


    def send_camera_viewr_only(self,conn,addr,wich_3g):
        try:
            self.stop_send_camera_viewer=False

            while self.stop_send_camera_viewer==False:

                if wich_3g=="0":
                    frame=self.all_camera.DATA
                elif wich_3g=="1":
                    frame=self.all_camera.DATA_3G_1
                elif wich_3g=="2":
                    frame=self.all_camera.DATA_3G_2

                try:
                    conn.sendall(frame)
                    time.sleep(self.wait_between_every_frame)
                except:
                    print("socket sending frames stoped...")
                    #traceback.print_exc()
                    conn.close()
                    self.stop_send_camera_viewer=True
        except:
            traceback.print_exc()




    def send_camera(self,conn,addr):
        try:
            threading.Thread(target=self.all_camera.check_for_wich_video,args=(self.wich_3g,)).start()
            self.check_detection_state=False
            self.stop_send_camera=False
            self.thread_detection=threading.Thread(target=self.detect_from_frame)
            self.thread_detection.start()
            self.thread_send_socket_detect=threading.Thread(target=self.socket_send_detection)
            self.thread_send_socket_detect.start()
            cc=int(self.conf.get_update_config('count_frame_detect'))-1
            while self.stop_send_camera==False:
                self.index_for_detection+=1
                if self.index_for_detection==cc:
                    self.index_for_detection=0
                    self.flg_detection=True

                if self.wich_3g=="0":
                    frame=self.all_camera.DATA
                elif self.wich_3g=="1":
                    frame=self.all_camera.DATA_3G_1
                elif self.wich_3g=="2":
                    frame=self.all_camera.DATA_3G_2

                try:
                    conn.sendall(frame)
                    time.sleep(self.wait_between_every_frame)
                except:
                    print("socket sending frames stoped...")
                    #traceback.print_exc()
                    conn.close()
                    self.stop_send_camera=True
                    self.check_detection_state=True
                    self.thread_detection.join()
                    self.thread_send_socket_detect.join()
        except:
            traceback.print_exc()


    def init_tfnet(self):
        options={
            'model':'cfg/tiny-yolo-voc-3c.cfg',
            'load':10000,
            'threshold':0.1,
        }
        self.tfnet=TFNet(options)


    def detect_from_frame(self):
        while self.check_detection_state==False:
            if self.flg_detection:
                encoding=encrypt_cisco(self.gen.get_uniq_key(int(self.conf.get_update_config('key'))))
                pading="aaaaa"
                if self.wich_3g=="0":
                    frame=self.all_camera.DATA_DETECT
                elif self.wich_3g=="1":
                    frame=self.all_camera.DATA_DETECT_3G_1
                elif self.wich_3g=="2":
                    frame=self.all_camera.DATA_DETECT_3G_2

                if type(frame)==np.ndarray:
                    results=self.tfnet.return_predict(frame)
                    for i in range(0,len(results)):
                        tl=(results[i]['topleft']['x'],results[i]['topleft']['y'])
                        br=(results[i]['bottomright']['x'],results[i]['bottomright']['y'])
                        label=results[i]['label']
                        try:
                            camera_number=self.detect_number_cam(tl)
                        except:
                            traceback.print_exc()
                            camera_number=None,None
                        if camera_number==None:
                            continue

                        try:
                            if(label=="plate_ir" ):
                                what="plate"
                                az_y=tl[1]-5
                                ta_y=br[1]+5
                                az_x=tl[0]-20
                                ta_x=br[0]+20
                                crop = frame[az_y:ta_y, az_x:ta_x]
                                crop= cv2.resize(crop,(0,0),fx=0.5,fy=0.5)
                                az_x,ta_x,az_y,ta_y=self.crop_img_for_sections(camera_number)
                                frame_org=frame[az_y:ta_y,az_x:ta_x]
                                frame_org=cv2.resize(frame_org,(config.def_width,config.def_height))
                                #self.socket_send_detection(camera_number,what,crop,frame_org)
                                frame_org=encoding.encrypt(frame_org)
                                frame_org=base64.b64encode(frame_org)
                                frame_org=frame_org.decode('utf-8')
                                crop=encoding.encrypt(crop)
                                crop=base64.b64encode(crop)
                                crop=crop.decode('utf-8')
                                str_frm=str(camera_number)+pading+str(what)+pading+crop+pading+frame_org
                                self.qu_detect.put(str_frm)
                            if(label=="face_ir"):
                                what="face"
                                az_x=tl[0]-35
                                ta_x=br[0]+35
                                crop = frame[tl[1]:br[1], az_x:ta_x]
                                crop= cv2.resize(crop,(0,0),fx=0.5,fy=0.5)
                                az_x,ta_x,az_y,ta_y=self.crop_img_for_sections(camera_number)
                                frame_org=frame[az_y:ta_y,az_x:ta_x]
                                frame_org=cv2.resize(frame_org,(config.def_width,config.def_height))
                                #self.socket_send_detection(camera_number,what,crop,frame_org)
                                frame_org=encoding.encrypt(frame_org)
                                frame_org=base64.b64encode(frame_org)
                                frame_org=frame_org.decode('utf-8')
                                crop=encoding.encrypt(crop)
                                crop=base64.b64encode(crop)
                                crop=crop.decode('utf-8')
                                str_frm=str(camera_number)+pading+str(what)+pading+crop+pading+frame_org
                                self.qu_detect.put(str_frm)
                            if(label=="person_ir"):
                                what="person"
                                az_y=tl[1]-5
                                ta_y=br[1]+5
                                az_x=tl[0]-15
                                ta_x=br[0]+15
                                crop = frame[az_y:ta_y, az_x:ta_x]
                                crop= cv2.resize(crop,(0,0),fx=0.5,fy=0.5)
                                az_x,ta_x,az_y,ta_y=self.crop_img_for_sections(camera_number)
                                frame_org=frame[az_y:ta_y,az_x:ta_x]
                                frame_org=cv2.resize(frame_org,(config.def_width,config.def_height))
                                #self.socket_send_detection(camera_number,what,crop,frame_org)
                                frame_org=encoding.encrypt(frame_org)
                                frame_org=base64.b64encode(frame_org)
                                frame_org=frame_org.decode('utf-8')
                                crop=encoding.encrypt(crop)
                                crop=base64.b64encode(crop)
                                crop=crop.decode('utf-8')
                                str_frm=str(camera_number)+pading+str(what)+pading+crop+pading+frame_org
                                self.qu_detect.put(str_frm)
                                self.flg_detection=False
                        except:
                            self.flg_detection=False
                            continue
                    else:
                        time.sleep(0.1)


    def socket_send_detection(self):
        encoding=encrypt_cisco(self.gen.get_uniq_key(int(self.conf.get_update_config('key'))))
        pading="aaaaa"
        while self.check_detection_state==False:
            if self.flg_first_socket_send_detection==False:
                try:
                    self.socket_tcp=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket_tcp.connect(self.ip_port_tcp)
                    self.socket_tcp.sendall('36'.encode('utf-8'))
                except:
                    traceback.print_exc()

                self.flg_first_socket_send_detection=True

            if self.qu_detect.qsize()>0:
                try:
                    arr=self.qu_detect.get().split(pading)
                    ret,crp=self.dec_quality(arr[2],False)
                    if ret:
                        crp=encoding.encrypt(crp)
                        crp=base64.b64encode(crp)
                        crp=crp.decode('utf-8')

                        ret,org=self.dec_quality(arr[3],False)
                        if ret:
                            org=encoding.encrypt(org)
                            org=base64.b64encode(org)
                            org=org.decode('utf-8')
                            data=arr[0]+pading+arr[1]+pading+crp+pading+org
                            try:
                                self.socket_tcp.sendall(data.encode('utf-8'))
                                #self.socket_tcp.close()
                            except:
                                #self.socket_tcp.close()
                                #self.check_detection_state=True
                                #print("tcp socket detection closed...")
                                traceback.print_exc()
                                self.flg_first_socket_send_detection=False
                                continue
                except:
                    traceback.print_exc()
            else:
                time.sleep(.5)

    def crop_img_for_sections(self,t):
        ret=""
        w=config.def_width_detect
        h=config.def_height_detect
        if t == "1":
            az_x=0
            ta_x=int(w)
            az_y=0
            ta_y=int(h)
            ret= az_x,ta_x,az_y,ta_y
        elif t== "2":
            az_x=int(w)
            ta_x=int(w*2)
            az_y=0
            ta_y=int(h)
            ret= az_x,ta_x,az_y,ta_y
        elif t== "3":
            az_x=0
            ta_x=int(w)
            az_y=int(h)
            ta_y=int(h*2)
            ret= az_x,ta_x,az_y,ta_y
        elif t== "4":
            az_x=int(w)
            ta_x=int(w*2)
            az_y=int(h)
            ta_y=int(h*2)
            ret= az_x,ta_x,az_y,ta_y

        return ret
    def detect_number_cam(self,tl):
        ret=0
        x=int(config.def_width_detect)
        y=int(config.def_height_detect)
        tl0=int(tl[0])
        tl1=int(tl[1])
        if tl0<x:
            if tl1<y:
                ret="1"
            elif tl1>y:
                ret="3"
        elif tl0>x:
            if tl1<y:
                ret="2"
            elif tl1>y:
                ret="4"
        return ret


    def get_drive_list(self):

        drives=win32api.GetLogicalDriveStrings()
        drives=drives.split('\000')[:-1]

        for x in range(0,len(drives)):
            try:
                drives[x]=drives[x]+'@'+win32api.GetVolumeInformation(drives[x])[0]
            except:
                drives[x]=drives[x]+"@"

        return drives

    def dec_quality(self,frame,dec):
        try:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), config.udp_qu]
            if dec:
                ret,frame=cv2.imencode('.jpg', frame,encode_param)
            elif dec==False:
                ret,frame=cv2.imencode('.jpg', frame)
            frm=frame.tobytes()
            rett=True
        except:
            print("error durring dec quality")
            traceback.print_exc()
            rett=False
            frm=None

        return rett,frm

    def get_size_drive(self,drive):
        obj_Disk = psutil.disk_usage(drive)
        total=obj_Disk.total
        used=obj_Disk.used
        free=obj_Disk.free

        return total,used,free

    def get_size_dir(self,root):
        size = 0
        for path, dirs, files in os.walk(root):
            for f in files:
                size +=  os.path.getsize( os.path.join( path, f ) )

        return size,size/1000,size/1000000,size/1000000000

if __name__=="__main__":
    connect_first=interval_send_ip_sender()
    connect_first.init_first()
    server=Server()
    server.run()