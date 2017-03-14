# -*- coding: utf8 -*-
#!/usr/bin/env python

#+++ 9.18 审计员数据库

import pymongo
import logging
import time
import ecode

import json
from bson import json_util
import mongoUtil


# import config
# db = client[config.get('mongo_db')]
# aus = db[config.get('mongo_auditor_table')]
client = mongoUtil.getClient()
db = client['wcloud_o']
aus = db['admin']


def init_db():
    aus.drop()
    aus.create_index([('uid',pymongo.ASCENDING)], unique=True)

def add_auditor(uid,pw,qx,email,phonenumber):
        
    try:
        aus.create_index([('uid',pymongo.ASCENDING)], unique=True)

        if aus.find_one({'uid':uid,'logo':"auditor"}):
            u = aus.update({'uid':uid,'logo':"auditor"}, {'$set':{'pw':pw,'qx':qx,'email':email,'phonenumber':phonenumber,'logo':"auditor"}})
            if u and u['n']:
                return True
        elif aus.insert({'uid':uid,'pw':pw,'qx':qx,'email':email,'phonenumber':phonenumber,'logo':"auditor"}):
            return True
    except pymongo.errors.DuplicateKeyError:
        raise ecode.USER_EXIST
    except:
        logging.exception('create auditor failed. uid:%s', uid)
    raise ecode.DB_OP

def get_auditor_list():
    
    try:
        r = aus.find({'logo':"auditor"},{'_id':0,'uid':1})
        if r:
            return r
    except:
        logging.exception('get_auditor_list failed')
    raise ecode.DB_OP

def is_has_auditor(uid):
    try:
        r = aus.find_one({'uid':uid,'logo':"auditor"}, {'uid':1})
        if r:
            return True
    except:
        logging.exception('is_has_auditor failed. uid:%s', uid)
        raise ecode.DB_OP
    return False

def check_pw( uid, pw ):
    try:
        r = aus.find_one({'uid':uid,'pw':pw,'logo':"auditor"}, {'pw':1})
        if r:
            return True
    except:
        logging.exception('check_pw auditor failed. uid:%s', uid)
        raise ecode.DB_OP
    return False
 
def get_qx_by_uid( uid):
    try:

        r = aus.find_one({'uid':uid,'logo':"auditor"}, {'qx':1})
        if r and r.has_key('qx'):
            return r['qx']
    except:
        logging.exception('get_qx_by_uid auditor failed. uid:%s', uid)
        raise ecode.DB_OP 
    return '' 
 
def get_pw_by_uid(uid):
    try:
        r = aus.find_one({'uid':uid,'logo':"auditor"}, {'pw':1})
        if r and r.has_key('pw'):
            return r['pw']
    except:
        logging.exception('get_pw_by_uid auditor failed. uid:%s', uid)
        raise ecode.DB_OP 
    return '' 

def update_pw(uid,pw):
    try:
        
        u = aus.update({'uid':uid,'logo':"auditor"}, {'$set':{'pw':pw}})
        if u and u['n']:
            return True
    except:
        logging.exception('get_pw_by_uid auditor failed. uid:%s', uid)
        raise ecode.DB_OP 
    return False     
        
def del_auditor(uid):
        
    try:
        aus.create_index([('uid',pymongo.ASCENDING)], unique=True)

        if aus.find_one({'uid':uid,'logo':"auditor"}):
            aus.remove({'uid':uid,'logo':"auditor"})
            if not aus.find_one({'uid':uid,'logo':"auditor"}):
                return True
    except:
        logging.exception('del auditor failed. uid:%s', uid)
    raise ecode.DB_OP
    
#展示所有的审计员（列表化显示）
def show_auditors():
    try:
        r = aus.find({'logo':"auditor"},{"_id":0,"pw":0})
        strs = []
        for doc in r:
            strs.append(doc)
        return strs
    except:
        logging.exception('get auditors failed.')
    raise ecode.DB_OP
