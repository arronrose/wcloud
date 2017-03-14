# -*- coding: utf8 -*-
#!/usr/bin/env python

import pymongo
import logging
import sha
import ecode
import config
import mongoUtil
import time
import re

import org
import user_ldap


client = mongoUtil.getClient()
db = client[config.get('mongo_db')]
online_db = db[config.get('mongo_online_statistics_table')]

def init_db():
    online_db.drop()
    online_db.create_index([('time',pymongo.ASCENDING)], unique=True)

def create(time,week_no,online_users):
    try:
        online_db.create_index([('time',pymongo.ASCENDING)], unique=True)
        online_db.insert({"time":time,"week_no":week_no,
                          "online_users":online_users})
        return True
    except pymongo.errors.DuplicateKeyError:
        raise ecode.USER_EXIST
    except:
        logging.error('create user failed. time:%s', time)
    raise ecode.DB_OP

def is_has_time(time):
    try:
        r = online_db.find_one({'time':time}, {'time':1})
        if r:
            return True
    except:
        logging.error('is_has_time failed. time:%s', time)
        raise ecode.DB_OP
    return False

def time_is_has_user( time, uid ):
    try:
        r = online_db.find_one({'time':time,'users':uid}, {'time':1,'uid':uid})
        if r:
            return True
    except:
        logging.error('is_has_time failed. time:%s', time)
        raise ecode.DB_OP
    return False


# 向在线用户列表中添加用户
def add_user(time,uid):
    try:
        online_db.update( {'time':time}, {'$addToSet':{'online_users':uid}})
    except:
        logging.error('add_user failed. time:%s', time)
        raise ecode.DB_OP


def get_online_time_users(target):
    time_users = []
    try:
        result = online_db.find({'time':{"$regex":target}},{"_id":0})
        for item in result:
            time_users.append(item)
        return time_users
    except:
        logging.error("get_online_time_users failed,target:%s",target)
        raise ecode.DB_OP
