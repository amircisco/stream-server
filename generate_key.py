import random
import sqlite3
import datetime
from Encoding import encrypt_cisco
import base64

class GenerateKey():
    def __init__(self):
        self.data = {}
        self.arr_adad = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.arr_horof_k = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
                            's', 't', 'u', 'w', 'x', 'y', 'z']
        self.arr_horof_b = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                            'S', 'T', 'W', 'X', 'Y', 'Z']
        self.arr_char = ['!', '@', '#', '$', '%', '^', '&', '*', '+']
        self.encoding=encrypt_cisco('qwe!@#rty$%^uio&*(oiuytrewq(*&^%$#@!')

        self.conn = sqlite3.connect('backup.db')
        self.c = self.conn.cursor()

        self.c.execute("SELECT * FROM tbl_auth")
        self.result=self.c.fetchall()

    def get_random(self):
        list_random = list()
        index1 = random.randrange(0, len(self.arr_adad) - 1)
        list_random.append(self.arr_adad[index1])
        index2 = random.randrange(0, len(self.arr_adad) - 1)
        list_random.append(self.arr_adad[index2])

        index1 = random.randrange(0, len(self.arr_horof_k) - 1)
        list_random.append(self.arr_horof_k[index1])
        index2 = random.randrange(0, len(self.arr_horof_k) - 1)
        list_random.append(self.arr_horof_k[index2])

        index1 = random.randrange(0, len(self.arr_horof_b) - 1)
        list_random.append(self.arr_horof_b[index1])
        index2 = random.randrange(0, len(self.arr_horof_b) - 1)
        list_random.append(self.arr_horof_b[index2])

        index1 = random.randrange(0, len(self.arr_char) - 1)
        list_random.append(self.arr_char[index1])
        index2 = random.randrange(0, len(self.arr_char) - 1)
        list_random.append(self.arr_char[index2])

        list_adad = [0, 1, 2, 3, 4, 5, 6, 7]
        list_tartip = list()
        while len(list_adad) > 0:
            index = random.randrange(0, 8)
            if index in list_adad and not index in list_tartip:
                list_tartip.append(index)
                list_adad.remove(index)

        str_data = ""
        for item in list_tartip:
            value = list_random[item]
            str_data += str(value)

        return str_data

    def get_key(self):
        key = ""
        for i in range(0, 4):
            key += self.get_random()

        return key

    def start(self, count):
        for i in range(0, count):
            self.data[i] = self.get_key()

        for i in range(0,len(self.data)):
            if i<152:
                continue
            item=self.data.get(i)
            item=self.encoding.encrypt(item.encode('utf-8'))
            a = i
            a=self.encoding.encrypt(str(a).encode('utf-8'))

            self.c.execute('''INSERT INTO tbl_auth(key_code,key_data) VALUES (?,?)''',(a,item) )

        self.conn.commit()


    def get_uniq_key(self, key):
        key_data=0
        index=int(key)-152
        key_code=self.encoding.decrypt(self.result[index][1])
        key_code=key_code.decode('utf-8')
        if int(key_code)==int(key):
            key_data=self.encoding.decrypt(self.result[index][2])
            key_data=key_data.decode('utf-8')
        return key_data

if __name__ == "__main__":
    gen = GenerateKey()
    #gen.start(200000)
    #print(gen.get_uniq_key(1522))
