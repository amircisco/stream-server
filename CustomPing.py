import os
import time
import threading


class Ping:
    def __init__(self):
        self.i=0
        self.do=True

    def start(self,host):
        th=threading.Thread(target=self.timer)
        th.start()
        os.system('ping '+host)
        self.do=False
        th.join()
        if self.i<=7:
            ret=True
        else:
            ret=False

        return ret

    def timer(self):
        while self.do:
            self.i+=1
            time.sleep(1)


