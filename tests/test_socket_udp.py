import socket
import datetime
import threading
import time

def handle(addr,conn):
    while True:
        data=conn.recv(1024)
        #data=data.decode('utf-8')
        print("time is {} and data is {}".format(datetime.datetime.now(),data))

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
address=('192.168.2.3',26251)
s.bind(address)
s.listen()
while True:
    conn,addr=s.accept()
    data=conn.recv(1024)
    print(data)
    threading.Thread(target=handle,args=(addr,conn)).start()
