# -*- coding: utf8 -*-
#!/usr/bin/env python

import pymongo
import logging
import time
import datetime
import ecode
import config
import json
import re
import mongoUtil
from bson import json_util


client = mongoUtil.getClient()

db = client[config.get('mongo_db')]
strategys = db[config.get('mongo_strategy_table')]


def init_db():
    strategys.drop()
    strategys.create_index([('strategy_id',pymongo.ASCENDING)], unique=True)


def new_strategy( strategy,users,userdesc):
    if dict != type(strategy):
        raise ecode.DATA_TYPE_ERROR
    if len(strategy) <= 0:
        raise ecode.DATA_LEN_ERROR
    logging.error(strategy)
    logging.error(len(strategy))
#    if len(strategy) > 14:
#        raise ecode.DATA_LEN_ERROR
    strategy_id = strategy['strategy_id']
    start = strategy['start']
    end = strategy['end']
    lon = strategy['lon']
    lat = strategy['lat']
    desc = strategy['desc']
    radius = strategy['radius']
    wifi = strategy['wifi']
    bluetooth = strategy['bluetooth']
    camera = strategy['camera']
    tape = strategy['tape']
    gps = strategy['gps']
    mobiledata = strategy['mobiledata']
    usb_connect = strategy['usb_connect']
    usb_debug = strategy['usb_debug']
    baseStationID = strategy['baseStationID']
    force = strategy['force'] #+++20150630 for forceControl
    types=strategy['types']
    auth = strategy['auth']
    
    if len(strategy_id) <= 0:
        raise ecode.DATA_LEN_ERROR
    try:
        strategys.create_index([('strategy_id',pymongo.ASCENDING)], unique=True)
        if strategys.insert({'types':types,'strategy_id':strategy_id, 'force':force,'start':start,'end':end,
                             'lon':lon, 'lat':lat,'radius':radius,'desc':desc,'wifi':wifi,'bluetooth':bluetooth,
                             'camera':camera,'tape':tape,'gps':gps,'mobiledata':mobiledata,'usb_connect':usb_connect,
                             'usb_debug':usb_debug,'users':users,'userdesc':userdesc,'baseStationId':baseStationID,'auth':auth}):
            return True  #+++20150630 change for forceControl
    except:
        logging.error('add new strategy failed. strategy_id:%s', strategy_id)
    raise ecode.DB_OP


def get_strategy_by_id(strategy_id):
    try:
        r = strategys.find_one({'strategy_id':strategy_id},{"_id" : 0})
        strategy = r
        return strategy
    except:
        logging.error('get_strategy_by_id failed. strategy_id:%s', strategy_id)
    raise ecode.DB_OP

def get_strategy_by_id1( strategy_id):
    try:
        r = strategys.find_one({'strategy_id':strategy_id},{"_id" : 0,'users':0,'userdesc':0,'types':0})
        strategy = r
        return strategy
    except:
        logging.error('get_strategy_by_id failed. strategy_id:%s', strategy_id)
    raise ecode.DB_OP

def get_strategys():
    try:
        r = strategys.find({"types":''},{"_id" : 0}).sort("strategy_id",pymongo.DESCENDING)
        strs = []
        for doc in r:
            #+++ 20150506 for pre stra
            if len(doc['types'])>0:
                continue
            strs.append(doc)
        return strs
    except:
        logging.error('get_strategts failed.')
    raise ecode.DB_OP

def get_strategys_by_admin(ou):
    try:
        #str = MongoRegex("/".ou.".*/i")  利用正则表达式来完成模糊查找
        str = re.compile(r'.*'+ou+'.*')
#         str = re.compile(r''+ou+'.*')
        # +++20151023 将原来的模糊匹配用户描述名称改为匹配用户数组中的
        r = strategys.find({"users.name":{'$regex':str},"types":''},{"_id" : 0}).sort("end",pymongo.DESCENDING)
        strs = []
        for doc in r:
            #+++ 20150506 for pre stra
            if len(doc['types'])>0:
                continue
            strs.append(doc)
        return strs
    except:
        logging.error('get_strategts failed.')
    raise ecode.DB_OP

#客户端调用的get_strategys()
def get_strategys_to_user(ids):
    try:
        user_strategys = []
        for id in ids: 
#             logging.error(id)
            strategy_id = str(id['strategy_id'])
            r = strategys.find_one({'strategy_id':strategy_id},{"_id" : 0,'users':0,'userdesc':0,'types':0})
#         strategy = r
            if r:
                stra = r
                user_strategys.append(stra)
        return user_strategys
    except:
        logging.error('get_strategts_to_user failed.')
    raise ecode.DB_OP

def get_strategys_of_user_by_admin(ids):
    try:
        user_strategys = []
        logging.error("ids is :%s",ids)
        for id in ids:
            strategy_id = str(id['strategy_id'])
            r = strategys.find_one({'strategy_id':strategy_id},{"_id" : 0,'users':0,'userdesc':0})
            if r:
                stra = r
                stra['is_read']=str(id['is_read'])
                #+++ 20150615
                end_time=stra['end']
                end=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M'))
                now_time=time.time()
                if int(now_time)-int(end)<0:
                    user_strategys.append(stra)
        return user_strategys
    except:
        logging.error('get_strategts_to_user failed.')
    raise ecode.DB_OP
        
def mod_strategy( strategy, users, userdesc ):
    strategy_id = strategy['strategy_id']
    try:
        u = strategys.update({'strategy_id':strategy_id}
                , {'$set':{'start':strategy['start'],'end':strategy['end']
                ,'force':strategy['force']
                ,'lon':strategy['lon']
                ,'lat':strategy['lat']
                ,'desc':strategy['desc']
                ,'radius':strategy['radius']
                ,'wifi':strategy['wifi']
                ,'bluetooth':strategy['bluetooth']
                ,'camera':strategy['camera']
                ,'tape':strategy['tape']
                ,'gps':strategy['gps']
                ,'mobiledata':strategy['mobiledata']
                ,'usb_connect':strategy['usb_connect']
                ,'usb_debug':strategy['usb_debug']
                ,'users':users
                ,'userdesc':userdesc
                ,'baseStationId':strategy['baseStationID']}})
        return True
    except:
        logging.error('mod_strategy failed. strategy_id:%s', strategy_id)
        raise ecode.DB_OP
    return False

def mod_users_of_strategy(strategy_id,users,userdesc):
    try:
        u = strategys.update({'strategy_id':strategy_id}
                , {'$set':{'users':users,'userdesc':userdesc}})
        return True
    except:
        logging.error('mod_users_of_strategy failed. strategy_id:%s', strategy_id)
        raise ecode.DB_OP
    return False

def del_strategy( strategy_id):
    try:
        r=strategys.find_one({'strategy_id':strategy_id})
        if not r:
            return True
        u = strategys.remove({'strategy_id':strategy_id})
        return True
    except:
        logging.error('del_strategy failed. strategy_id:%s', strategy_id)
    raise ecode.DB_OP

#+++ 20150506
def get_pre_stra_list(types):
    try:
        r = strategys.find({"types":types},{"_id" : 0,"desc":1})
        strs = []
        for doc in r:
            strs.append(doc)
        return strs
    except:
        logging.error('get_strategts failed.')
    raise ecode.DB_OP

def get_strategy_by_desc(desc):
    try:
        r = strategys.find_one({'desc':desc},{"_id" : 0})
        return r
    except:
        logging.error('get_strategy_by_desc failed. desc:%s', desc)
    raise ecode.DB_OP

#+++ 20150507
def del_pre_stra(desc):
    try:
        r = strategys.remove({"desc":desc,"types":"preStra"})
        return True
    except:
        logging.error('get_strategts failed.')
    raise ecode.DB_OP

#+++ 20150512 for 清除策略
def is_has_strategy(strategy_id):
    try:
        r = strategys.find_one({'strategy_id':strategy_id}, {'strategy_id':1})
        if r:
            return True
    except:
        logging.error('is_has_dev failed. dev_id:%s', strategy_id)
        raise ecode.DB_OP
    return False

#+++ 20150617 for 下发策略反馈
def mod_users_un_send(strategy_id,users):
    try:
        r = strategys.find_one({'strategy_id':strategy_id},{"_id" : 0,'users':1})
        if not r:
            return True
        newusers=r["users"]
        for del_son in users:
            for son in newusers:
                if del_son["name"]==son["name"]:
                    del_list=del_son["users"]
                    for s in del_list:
                        son["users"].remove(s)
                    if son["users"]==[]:
                        ss={"name":son["name"],"users":son["users"]}
                        newusers.remove(ss)
        if newusers!=[]:
            strategys.update({'strategy_id':strategy_id},{'$set':{'users':newusers}})
        else:
            strategys.remove({'strategy_id':strategy_id})
            return True
    except:
        logging.error('mod_users_of_strategy failed. strategy_id:%s', strategy_id)
        raise ecode.DB_OP
    return False

#+++ 20150618 for 策略删除反馈
def mod_users_un_del(strategy_id,users):
    try:
        u = strategys.update({'strategy_id':strategy_id},{'$set':{'users':users}})
        return True
    except:
        logging.error('mod_users_un_del failed. strategy_id:%s', strategy_id)
        raise ecode.DB_OP
    return False

#+++ 20150629 for 一键清除策略
def del_user_of_users(strategy_id,uid):
    try:
        r = strategys.find_one({'strategy_id':strategy_id},{"_id" : 0,'users':1})
        if not r:
            return True
        newusers=r["users"]
        for son in newusers:
            sonusers=son["users"]
            for gson in sonusers:
                if gson["uid"]==uid:
                    son["users"].remove(gson)
            logging.warn("del users is :%s",newusers)
            if len(son['users'])==0:
                newusers.remove(son)
                
        if newusers!=[]:
            u=strategys.update({'strategy_id':strategy_id},{'$set':{'users':newusers}})
        else:
            u=strategys.remove({'strategy_id':strategy_id})
            return True
    except:
        logging.error('del_user_of_users failed. strategy_id:%s', strategy_id)
        raise ecode.DB_OP
    return False

#+++20160104判断策略是否作用在改群组上
def is_contorl_ou(strategy_id,oudn):
    try:
        u = strategys.find_one({'strategy_id':strategy_id})
        if(u!=""):
            users = u['users']
            for ou in users:
                if ou['name'].find(oudn)>=0:
                    return True
        return False
    except:
        logging.error('is_contorl_ou failed. strategy_id:%s,oudn:%s', strategy_id,oudn)
        raise ecode.DB_OP

#+++20160104 判断策略状态 -1 未执行 0正在执行中 1 已经过期
def strategy_status(strategy_id):
    try:
        u = strategys.find_one({'strategy_id':strategy_id})
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        if(u!=""):
            start_time = u['start']
            end_time = u['end']
            if start_time>now_time:
                return -1
            elif start_time<=now_time and now_time<=end_time:
                return 0
            else:
                return 1
        else:
            raise ecode.FAILED
    except:
        logging.error('strategy_status failed. strategy_id:%s', strategy_id)
        raise ecode.DB_OP