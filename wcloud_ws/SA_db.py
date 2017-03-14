# -*- coding: utf8 -*-
#!/usr/bin/env python

#+++ 9.18 安全员数据库

import pymongo
import logging
import time
import ecode

import json
from bson import json_util
import mongoUtil


# import config
# db = client[config.get('mongo_db')]
# SAs = db[config.get('mongo_SA_table')]
client = mongoUtil.getClient()
db = client['wcloud_o']
SAs = db['admin']


def init_db():
    SAs.drop()
    SAs.create_index([('uid',pymongo.ASCENDING)], unique=True)

def add_SA(uid,pw,qx,email,phonenumber):
        
    try:
        SAs.create_index([('uid',pymongo.ASCENDING)], unique=True)

        if SAs.find_one({'uid':uid,'logo':"sa"}):
            u = SAs.update({'uid':uid,'logo':"sa"}, {'$set':{'pw':pw,'qx':qx,'email':email,'phonenumber':phonenumber,'logo':"sa"}})
            if u and u['n']:
                return True
        elif SAs.insert({'uid':uid,'pw':pw,'qx':qx,'email':email,'phonenumber':phonenumber,'logo':"sa"}):
            return True
    except pymongo.errors.DuplicateKeyError:
        raise ecode.USER_EXIST
    except:
        logging.exception('create SA failed. uid:%s', uid)
    raise ecode.DB_OP

def get_SA_list():
    
    try:
        r = SAs.find({'logo':"sa"},{'_id':0,'uid':1})
        if r:
            return r
    except:
        logging.exception('get_SA_list failed')
    raise ecode.DB_OP

def is_has_SA(uid):
    try:
        r = SAs.find_one({'uid':uid,'logo':"sa"}, {'uid':1})
        if r:
            return True
    except:
        logging.exception('is_has_SA failed. uid:%s', uid)
        raise ecode.DB_OP
    return False

def check_pw( uid, pw ):
    try:
        r = SAs.find_one({'uid':uid,'pw':pw,'logo':"sa"}, {'pw':1})
        if r:
            return True
    except:
        logging.exception('check_pw SA failed. uid:%s', uid)
        raise ecode.DB_OP
    return False
 
def get_qx_by_uid( uid):
    try:

        r = SAs.find_one({'uid':uid,'logo':"sa"}, {'qx':1})
        if r and r.has_key('qx'):
            return r['qx']
    except:
        logging.exception('get_qx_by_uid SA failed. uid:%s', uid)
        raise ecode.DB_OP 
    return '' 
 
def get_pw_by_uid(uid):
    try:
        r = SAs.find_one({'uid':uid,'logo':"sa"}, {'pw':1})
        if r and r.has_key('pw'):
            return r['pw']
    except:
        logging.exception('get_pw_by_uid SA failed. uid:%s', uid)
        raise ecode.DB_OP 
    return '' 

def update_pw(uid,pw):
    try:
        
        u = SAs.update({'uid':uid,'logo':"sa"}, {'$set':{'pw':pw}})
        if u and u['n']:
            return True
    except:
        logging.exception('get_pw_by_uid SA failed. uid:%s', uid)
        raise ecode.DB_OP 
    return False     
        
def del_SA(uid):
        
    try:
        SAs.create_index([('uid',pymongo.ASCENDING)], unique=True)

        if SAs.find_one({'uid':uid,'logo':"sa"}):
            SAs.remove({'uid':uid,'logo':"sa"})
            if not SAs.find_one({'uid':uid,'logo':"sa"}):
                return True
    except:
        logging.exception('del SA failed. uid:%s', uid)
    raise ecode.DB_OP

#展示所有的安全员（列表化显示）
def show_SAs():
    try:
        r = SAs.find({'logo':"sa"},{"_id":0,"pw":0})
        strs = []
        for doc in r:
            strs.append(doc)
        return strs
    except:
        logging.exception('get SAs failed.')
    raise ecode.DB_OP
