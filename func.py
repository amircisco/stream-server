import os
class helper():

    @staticmethod
    def check_ip(ip):
        ret=False
        response = os.system("ping " + ip)
        if response == 0:
            ret=True

        return ret