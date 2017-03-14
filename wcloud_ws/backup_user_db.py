# -*- coding: utf8 -*-
#!/usr/bin/env python

import pymongo
import logging
import sha
import ecode
import config
import mongoUtil


client = mongoUtil.getClient()

db = client[config.get('mongo_db')]
backup_users = db[config.get('mongo_backup_user_table')]
backup_sms = db[config.get('mongo_backup_sms_table')]
backup_contact = db[config.get('mongo_backup_contact_table')]


def init_db():
    backup_users.drop()
    backup_users.create_index([('uid',pymongo.ASCENDING)], unique=True)

#for register
def create(uid,passwd,dev_id):
    try:
        backup_users.create_index([('uid',pymongo.ASCENDING)], unique=True)

        if backup_users.insert({'uid':uid,'passwd':passwd, 'dev_id':dev_id}):
            return True
    except pymongo.errors.DuplicateKeyError:
        raise ecode.USER_EXIST
    except:
        logging.error('create backup user failed. uid:%s', uid)
    raise ecode.DB_OP

#for login
def check_pw(uid,passwd):
    try:
        r = backup_users.find_one({'uid':uid,'passwd':passwd}, {'passwd':1})
        if r:
            return True
    except:
        logging.error('check_pw failed. uid:%s', uid)
        raise ecode.DB_OP
    return False

def is_has_user(uid):
    try:
        r = backup_users.find_one({'uid':uid}, {'uid':1})
        if r:
            return True
    except:
        logging.error('is_has_user failed. uid:%s', uid)
        raise ecode.DB_OP
    return False

def set_dev(uid,dev_id):
    try:
        u = backup_users.update({'uid':uid}, {'$set':{'dev_id':dev_id}})
        return True
    except:
        logging.error('set_dev failed. uid:%s', uid)
    return False

def get_dev(uid):
    try:
        u = backup_users.find_one({'uid':uid}, {'_id':0,'dev_id':1})
        if u and u.has_key('dev_id'):
            if len(u['dev_id'])==0:
                return False
            else:
                return True
    except:
        logging.error('get_dev failed. uid:%s', uid)
    raise ecode.DB_OP

#for change passwd
def set_pw(uid,passwd):
    try:
        u = backup_users.update({'uid':uid}, {'$set':{'passwd':passwd}})
        return True
    except:
        logging.error('set_pw failed. uid:%s', uid)
    raise ecode.DB_OP

def save_sms(uid,content):
    try:
        logging.error("开始存储短信")
        _id = content[1]
        logging.error("_id:"+str(_id))
        type = content[2]
        read = content[3]
        address = content[4]
        body = content[5]
        date = content[6]
        backup_sms.insert({"uid":uid,"obj_id":_id,
                           "type":type,"read":read,"address":address,
                           "body":body,"date":date})
        return True
    except:
        logging.error('save_sms failed. uid:%s', uid)
    raise ecode.DB_OP

def get_smss(uid):
    smss = []
    try:
        print "开始获取数据库中短信"
        result = backup_sms.find({"uid":uid})
        for item in result:
            smss.append(item)
        return smss
    except:
        logging.error('get_smss failed. uid:%s', uid)
    raise ecode.DB_OP

def get_sms_by_date(uid,date):
    try:
        result = backup_sms.find_one({"uid":uid,"date":date})
        return result
    except:
        logging.error('get_smss failed. uid:%s', uid)
    raise ecode.DB_OP

def save_contact(uid,content):
    try:
        FN = content["FN"]
        N = content["N"]
        TEL = content["TEL"]
        VERSION = content["VERSION"]
        backup_contact.insert({"uid":uid,"FN":FN,"N":N,"TEL":TEL,
                           "VERSION":VERSION})
        return
    except:
        logging.error('save_contact failed. uid:%s', uid)
    raise ecode.DB_OP

def get_contacts(uid):
    contacts = []
    try:
        result = backup_contact.find({"uid":uid})
        for item in result:
            if item:
                item_dict = dict(N=item['N'],FN=item['FN'],TEL=item['TEL'],VERSION=item['VERSION'])
                contacts.append(item_dict)
            else:
                continue
        return contacts
    except:
        logging.error('get_contacts failed. uid:%s', uid)
    raise ecode.DB_OP

def del_sms(uid):
    try:
        backup_sms.remove({"uid":uid})
        return True
    except:
        logging.error('get_contacts failed. uid:%s', uid)
    raise ecode.DB_OP

def del_contact(uid):
    try:
        backup_contact.remove({"uid":uid})
        return True
    except:
        logging.error('get_contacts failed. uid:%s', uid)
    raise ecode.DB_OP

