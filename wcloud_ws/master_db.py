# -*- coding: utf8 -*-
#!/usr/bin/env python

#+++ 9.18 管理员数据库

import pymongo
import logging
import time
import ecode

import json
import mongoUtil
from bson import json_util


# import config
# db = client[config.get('mongo_db')]
# ads = db[config.get('mongo_admin_table')]
client = mongoUtil.getClient()
db = client['wcloud_o']
ads = db['admin']


def init_db():
    ads.drop()
    ads.create_index([('uid',pymongo.ASCENDING)], unique=True)

def add_master(uid,pw,qx,email,phonenumber):
        
    try:
        ads.create_index([('uid',pymongo.ASCENDING)], unique=True)

        if ads.find_one({'uid':uid,'logo':"master"}):
            u = ads.update({'uid':uid,'logo':"master"}, {'$set':{'pw':pw,'qx':qx,'email':email,'phonenumber':phonenumber,'logo':"master"}})
            if u and u['n']:
                return True
        elif ads.insert({'uid':uid,'pw':pw,'qx':qx,'email':email,'phonenumber':phonenumber,'logo':"master"}):
            return True
    except pymongo.errors.DuplicateKeyError:
        raise ecode.USER_EXIST
    except:
        logging.exception('create master failed. uid:%s', uid)
    raise ecode.DB_OP

def get_master_list():
    
    try:
        r = ads.find({'logo':"master"},{'_id':0,'uid':1})
        if r:
            return r
    except:
        logging.exception('get_master_list failed')
    raise ecode.DB_OP

def is_has_master(uid):
    try:
        r = ads.find_one({'uid':uid,'logo':"master"}, {'uid':1})
        if r:
            return True
    except:
        logging.exception('is_has_master failed. uid:%s', uid)
        raise ecode.DB_OP
    return False

def check_pw( uid, pw ):
    try:
        r = ads.find_one({'uid':uid,'pw':pw,'logo':"master"}, {'pw':1})
        if r:
            return True
    except:
        logging.exception('check_pw master failed. uid:%s', uid)
        raise ecode.DB_OP
    return False
 
def get_qx_by_uid( uid):
    try:

        r = ads.find_one({'uid':uid,'logo':"master"}, {'qx':1})
        if r and r.has_key('qx'):
            return r['qx']
    except:
        logging.exception('get_qx_by_uid master failed. uid:%s', uid)
        raise ecode.DB_OP 
    return '' 
 
def get_pw_by_uid(uid):
    try:
        r = ads.find_one({'uid':uid,'logo':"master"}, {'pw':1})
        if r and r.has_key('pw'):
            return r['pw']
            # return r
    except:
        logging.exception('get_pw_by_uid master failed. uid:%s', uid)
        raise ecode.DB_OP 
    return '' 

def update_pw(uid,pw):
    try:
        
        u = ads.update({'uid':uid,'logo':"master"}, {'$set':{'pw':pw}})

        # if u and u['n']:
        return True
    except:
        logging.exception('get_pw_by_uid master failed. uid:%s', uid)
        raise ecode.DB_OP 
    return False     
        
def del_master(uid):
        
    try:
        ads.create_index([('uid',pymongo.ASCENDING)], unique=True)

        if ads.find_one({'uid':uid,'logo':"master"}):
            ads.remove({'uid':uid,'logo':"master"})
            if not ads.find_one({'uid':uid,'logo':"master"}):
                return True
    except:
        logging.exception('del master failed. uid:%s', uid)
    raise ecode.DB_OP
    
#展示所有的管理员（列表化显示）
def show_masters():
    try:
        r = ads.find({'logo':"master"},{"_id":0,"pw":0})
        strs = []
        for doc in r:
            strs.append(doc)
        return strs
    except:
        logging.exception('get masters failed.')
    raise ecode.DB_OP
