import socket
import time
import config
import threading
from Encoding import encrypt_cisco
from generate_key import GenerateKey
import random
import traceback
import os


class Remote():

    def run(self):
        try:
            self.repeat=0
            self.key_code=0
            self.key_code=""
            self.gen=GenerateKey()
            self.encoding=encrypt_cisco('qwe!@#rty$%^uio&*(oiuytrewq(*&^%$#@!')
            self.stop=False
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            address=(str(config.sender_ip),int(config.port_remote))
            self.socket.bind(address)
            self.socket.listen()
            print("Listen for socket in ip_port {}".format(address))
            while self.stop==False:
                conn ,addr= self.socket.accept()
                data=conn.recv(1024)
                if(data.decode('utf-8')=="qazxsw"):
                    threading.Thread(target=self.handle_connection,args=(conn,addr)).start()
        except:
            self.repeat+=1
            traceback.print_exc()
            self.stop=True
            self.socket.close()
            if self.repeat<20:
                sec=5
                while sec>0:
                    print("restart at {} seconds".format(sec))
                    time.sleep(1)
                    sec-=1
                self.run()

    def handle_connection(self,conn,addr):
        try:
            print("recive data for reset system...")
            self.key=random.randrange(2000,5000)
            self.key_code=self.gen.get_uniq_key(self.key)
            sender_data=str(self.key).encode('utf-8')
            sender_data=self.encoding.encrypt(sender_data)
            conn.sendall(sender_data)
            stop=False
            print("initialize code...")
            while stop==False:
                try:
                    print("recive decode command...")
                    encoding=encrypt_cisco(self.key_code)
                    data=conn.recv(5124)
                    data=encoding.decrypt(data)
                    new_data=data.decode('utf-8')
                    if new_data=="re@1234se78#$%90t":
                        print("reset do start")
                        stop=True
                        sender_data='88'.encode('utf-8')
                        conn.sendall(sender_data)
                        conn.close()
                        time.sleep(1)
                        self.reset_system()
                    else:
                        print("reset not true")
                        stop=True
                        sender_data='77'.encode('utf-8')
                        conn.sendall(sender_data)
                        conn.close()
                except:
                    stop=True

            conn.close()
        except:
            traceback.print_exc()


    def reset_system(self):
        os.system('shutdown -t 0 -r -f')
        pass

if __name__=="__main__":
    seconds=15
    print("start remote after {} seconds...".format(seconds))
    while seconds>0:
        print("wait for {} second".format(seconds))
        time.sleep(1)
        seconds-=1
    remote=Remote()
    remote.run()