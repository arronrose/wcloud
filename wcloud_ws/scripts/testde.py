__author__ = 'ZXC'


import logging
import base64
from ctypes import *
import ctypes
#+++ 20150504
from pyDes import *

def decrypt_des(dev_id,crypt_data):

    print("------------------decrypt_des dev_id:"+dev_id)

    key=dev_id[-8:].encode("utf-8");
    des_mid=des(key,CBC,"\0\0\0\0\0\0\0\0",pad=None,padmode=PAD_PKCS5)
    if des_mid:
        logging.error("init is ok!")
    crypt_b64=base64.b64decode(crypt_data)
    outData=des_mid.decrypt(crypt_b64)
    logging.error("------------------decrypt_des outData:"+outData)
    return outData

if __name__ == '__main__':
    crypt_data = "U5lERa/5KY//VpSN4my0+e/OMUmKmedL"
    dev_id = "002101540934779"
    # dev_id = "867425020010527"

    print decrypt_des(dev_id,crypt_data)


