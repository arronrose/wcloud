# -*- coding: utf8 -*-
#!/usr/bin/env python

import pymongo
import logging
import time
import ecode
import config
import json
import user_db
import mongoUtil
from bson import json_util


client = mongoUtil.getClient()

db = client[config.get('mongo_db')]
contacts = db[config.get('mongo_contact_table')]


def init_db():
    contacts.drop()
    contacts.create_index([('uid',pymongo.ASCENDING)], unique=True)

def add_contact(uid,contact):
    if len(contact)<0:
        raise ecode.DATA_LEN_ERROR
    if list != type(contact):
        raise ecode.DATA_TYPE_ERROR
    if len(uid)<0:
        raise ecode.DATA_LEN_ERROR
    try:
        contacts.create_index([('uid',pymongo.ASCENDING)], unique=True)
        #是否含有uid项
        r = contacts.find_one({'uid':uid})
        if r :
            #+++改20150820如果有则向contacts中追加，可以直接追加集合,但是要加入each符号
            u = contacts.update({'uid':uid},{'$addToSet':{'contact':{"$each":contact}}})
            return True
        else:
            # +++如果没有的话需要insert进去
            if contacts.insert({'uid':uid,'contact':contact}):
                return True 
    except:
        logging.error('add_contact failed. uid:%s', uid)
    raise ecode.DB_OP 

def del_contact(uid,contact):
    if len(contact)<0:
        raise ecode.DATA_LEN_ERROR
    if list != type(contact):
        raise ecode.DATA_TYPE_ERROR
    if len(uid)<0:
         raise ecode.DATA_LEN_ERROR
    try:
        #是否含有uid项
        r = contacts.find_one({'uid':uid})
        if r :  #如果有则从contact中删除
            for item in contact:
                #if not contacts.find({'contact.uid':item[1]}):
                u = contacts.update({'uid':uid},{'$pull':{'contact':item}})
            return True
    except:
        logging.error('del_contact failed. uid:%s', uid)
    raise ecode.DB_OP 

def get_contacts_by_uid(uid):
    if len(uid)<0:
        raise ecode.DATA_LEN_ERROR
    try:
        #是否含有uid项
        r = contacts.find_one({'uid':uid})
        if r:
            #+++20150925 加入删除不存在的联系人逻辑
            contacts = r['contact']
            i = len(contacts)-1
            while i>=0:
                uid = contacts[i]["uid"]
                if not user_db.is_has_user(uid):
                    contacts.remove(contacts[i])
                else:
                    continue
            # +++20150925最后再把删除之后的结果存入数据库
            contacts.update({"uid":uid},{"$set":{"contact":contacts}})
            return contacts
        else:
            return []
    except:
        logging.error('get_contacts_by_uid failed. uid:%s', uid)
    raise ecode.DB_OP 

#+++ 20150706 for del user
def remove_contact(uid):
    try:
        r=contacts.find_one({'uid':uid})
        if not r:
            return True
        u = contacts.remove({'uid':uid})
        return True
    except:
        logging.error('remove_contact failed. uid:%s', uid)
    raise ecode.DB_OP
    