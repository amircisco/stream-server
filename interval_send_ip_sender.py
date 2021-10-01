import time
import threading
import socket
from initConfig import initConfig
import traceback
from Encoding import encrypt_cisco
import config
import psutil
import os

class interval_send_ip_sender():

    def communicate(self):
        try:
            total,used,free=self.get_size_drive(str(os.getcwd())[0]+":/")
            total=total/1000000000
            used=used/1000000000
            free=free/1000000000
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip=self.conf.get_update_config('reciver_ip')
            port=int(self.conf.get_update_config('port_communicate'))
            address=(ip,port)
            s.connect(address)
            data="sender"+self.conf.get_update_config('communicate_spliter')+"every_time_send"+self.conf.get_update_config('communicate_spliter')+str(self.conf.get_update_config('key'))+self.conf.get_update_config('communicate_spliter')+str(total)+self.conf.get_update_config('communicate_spliter')+str(used)+self.conf.get_update_config('communicate_spliter')+str(free)
            data=data.encode('utf-8')
            data=self.encoding.encrypt(data)
            s.sendall(data)
            s.close()
        except:
            #traceback.print_exc()
            print("center system by ip {} is not running...".format(config.reciver_ip))

    def init_first(self):
        self.flg=False
        self.conf=initConfig()
        self.encoding=encrypt_cisco('qwe!@#rty$%^uio&*(oiuytrewq(*&^%$#@!')
        threading.Thread(target=self.bef_send).start()

    def bef_send(self):
        if self.flg==False:
            self.communicate()
            self.flg=True
        while True:
            time.sleep(60)
            self.communicate()


    def get_size_drive(self,drive):
        obj_Disk = psutil.disk_usage(drive)
        total=obj_Disk.total
        used=obj_Disk.used
        free=obj_Disk.free

        return total,used,free




