import os
import time
import threading

class CheckPid(threading.Thread):
    def __init__(self,pid,instance):
        super(CheckPid,self).__init__()
        self.pid=pid
        self.instance=instance
    def run(self):
        while True:
            time.sleep(2)
            if(self.check()==False):
                self.instance.run_def_on_exit()
                break
            
            
    def check(self):
        try:
            os.kill(self.pid)
        except OSError:
            return False
        else:
            return True
        
        