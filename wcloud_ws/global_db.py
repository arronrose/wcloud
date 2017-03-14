# -*- coding: utf8 -*-
#!/usr/bin/env python
#9.9+

import pymongo
import logging
import ecode
import config
import mongoUtil


client = mongoUtil.getClient()
db = client[config.get('mongo_db')]
globaldb = db[config.get('mongo_global_table')]


def init_db():
    globaldb.drop()

#存name-value键值对
def add_global(name,value):
    if len(name) <= 0:
        raise ecode.DATA_LEN_ERROR

    try:
        if globaldb.find_one({'name':name}):
            u=globaldb.update({'name':name},{'$set':{'value':value}})
            if u and u['n']:
                return True
        else:
            if globaldb.insert({'name':name,'value':value}):
                return True
    except:
        logging.exception('add new global items failed. name:%s，value:%s', name,value)
    raise ecode.DB_OP

def get_global(name):
    try:
        r = globaldb.find_one({'name':name}, {'value':1})
        if r:
            return r['value']
        else:
            return ''
    except:
        logging.exception('get_global failed. value:%s', r['value'])
    raise ecode.DB_OP

def del_global(name):   #global数据库 name 唯一。+9.11
    try:
        if globaldb.find_one({'name':name})!='':
            if globaldb.remove({'name':name}):
                return True
        else:
            return True
    except:
        logging.exception('del_global failed.')
    raise ecode.DB_OP

def del_by_value(value):   #global数据库 name 唯一。+9.11
    try:
        if globaldb.find_one({'value':value})!='':
            if globaldb.remove({'value':value}):
                return True
        else:
            return True
    except:
        logging.exception('del_by_value failed.')
    raise ecode.DB_OP
