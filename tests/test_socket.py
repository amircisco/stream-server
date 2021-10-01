import socket
import time

i=0
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
address=('192.168.2.3',26251)
s.connect(address)
while True:
    i+=1
    if i%3==0:
        s.sendall(str(i).encode('utf-8'))
        print("send")
    else:
        print("wait")
    time.sleep(1)

