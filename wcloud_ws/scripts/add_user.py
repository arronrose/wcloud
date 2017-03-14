__author__ = 'ZXC'
# -*- coding: utf8 -*-

import pymongo
import random
import time
import logging
from pymongo import MongoClient
import sha

mongo_host = "192.168.1.15"
# mongo_host = "127.0.0.1"
mongo_port = 27017
client = MongoClient(mongo_host,mongo_port)
db = client["wcloud_o"]
users = db['user']

def create(uid,pw,status,username,email,title,oudn):
    try:
        if users.find_one({'uid':uid,'verified':0}, {'uid':1}):
            u = users.update({'uid':uid}, {'$set':{'pw':pw}})
            return True
        else:
            key = get_key(18)
            create_time=int(time.time()*1000)
            if users.insert({'key':key,'uid':uid,'pw':pw,'status':status,'username':username,'email':email,
                           'title':title,'oudn':oudn,'create_time':create_time,'devs':[],'verified':0,'pw_exp':1}):
                return True
    except pymongo.errors.DuplicateKeyError:
        raise
    except:
        logging.error('create user failed. uid:%s', uid)
    raise

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
    return str(key)

def is_has_key(key):
    """
    查找是否存在此键值
    :param key: 需要查找的键值
    :return:查找结果，存在True，不存在False
    """
    exist = False
    try:
        result = users.find_one({"key":key})
        if result:
            exist = True
    except Exception as e:
        logging.error('is_has_key failed. key:%s', key)
        logging.error(e.message)
    return exist

if __name__ == '__main__':
    create("85200000019", sha.new('12345678').hexdigest(), 0, "47632",
                           " ", u"工程师", u"ou=香港测试群,ou=中科院信工所,dc=test,dc=com")
    create("85200000011", sha.new('12345678').hexdigest(), 0, "37559",
                           " ", u"工程师", u"ou=香港测试群,ou=中科院信工所,dc=test,dc=com")