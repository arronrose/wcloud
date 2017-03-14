# -*- coding: utf8 -*-
#!/usr/bin/env python

import pymongo
import logging
import time
import ecode
import config
import mongoUtil

client = mongoUtil.getClient()

db = client[config.get('mongo_db')]
table = db[config.get('mongo_trace_table')]


def init_db():
    table.drop()
    table.create_index([('uid',pymongo.ASCENDING)], unique=True)

def set(uid,time,loc):
    try:
        trace=[]
        item={'time':time,'loc':loc}
        trace.append(item)
        #先判断数据若无效(-0.1,-0.1)，则直接返回
        lat=loc.split(':')[0]
        if str(lat)<str(0):
            return True
        # table.create_index([('uid',pymongo.ASCENDING)], unique=True)
        r = table.find_one({'uid':uid},{'_id':0,'trace':1})
        if r:
            tempitems=r['trace']
            #需要判断，每个用户只取150个点，替换掉最早的点
            if len(tempitems)>150:
                table.update({"uid":uid},{'$pop':{"trace":-1}})
            if not table.update({'uid':uid},{'$push':{'trace':item}}):
                return False
        else:
            if not table.insert({'uid':uid,'trace':trace}):
                return False
    except:
        logging.error('set trace failed')
    return True

def get(uid,time1='',time2=''):
    """get trace key value."""
    """ 传入的时间为时间戳"""
    items=[]
    try:
        r = table.find_one({'uid':uid},{'_id':0,'trace':1})
        if not r:
            return items
        #得到的格式：[{},{},...]
        tempitems=r['trace']
        #返回值格式：[(),(),...]
        if time1=='' and time2=='': #如果时间都为空，则是获取全部的键值对
            for item in tempitems:
                items.append((item['time'],item['loc']))
        elif time1==''and time2!='':   #如果起始时间为空，则获取截止日期之前的所有值
            for item in tempitems:
                if str(item['time'])<str(time2):
                    items.append((item['time'],item['loc']))
        elif time1!='' and time2=='':
            for item in tempitems:
                if str(item['time'])>str(time1):
                    items.append((item['time'],item['loc']))
        else:
            for item in tempitems:
                if str(item['time'])>str(time1) and str(item['time'])<str(time2):
                    items.append((item['time'],item['loc']))
    except:
        logging.error('read trace_db failed')
    return items      

def get_last_option(uid):
    """get uid last key value."""
    item=[]
    try:
        r=table.find_one({'uid':uid},{'_id':0,'trace':1})
        if r and len(r['trace'])>0:
            tempitems=r['trace']
            items=tempitems[len(tempitems)-1]
            item=[items['time'],items['loc']]
    except:
        logging.error('get last_option failed')
    return item


# +++20150805 删除用户时清除用户轨迹信息
def del_trace_of_user(uid):
    try:
        u = table.remove({'uid':uid})
        if u and u['n']:
            return True
        else:
            logging.warn('del_trace failed: uid:%s', uid)
    except:
        logging.error('del_trace failed. uid:%s', uid)
    return False