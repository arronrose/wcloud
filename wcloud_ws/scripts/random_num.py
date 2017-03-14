# -*- coding: utf8 -*-
__author__ = 'GCY'

import random
from pymongo import MongoClient

# +++20160217 加入生成随机数主键的函数
def get_key(len):
    """
    :param len:键的长度
    :return:生成的键
    """
    key = 0
    if len>0:
        start = int("1"+(len-1)*"0")
        end = int(len*"9")
        key = random.randint(start,end)
        # 只要存在key就重复生成，保证key的唯一性
        while is_has_key(key):
            key = random.randint(start,end)
    return key

def is_has_key(key):
    """
    查找是否存在此键值
    :param key: 需要查找的键值
    :return:查找结果，存在True，不存在False
    """
    exist = False
    try:
        key_list = [1000000000000000000,999999999999999999]
        result = key in key_list
        if result:
            exist = True
    except Exception as e:
        print e.message
    return exist

# print random_num

if __name__ == '__main__':
    mongo_host = "192.168.1.15"
    mongo_port = 27017
    client = MongoClient(mongo_host,mongo_port)
    db = client["wcloud_o"]
    users = db["user"]

    user_list = users.find()
    for item in user_list:
        key = get_key(18)
        print(str(key))
        users.update({"uid":item["uid"]},{"$set":{"key":str(key)}})