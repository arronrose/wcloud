# -*- coding: utf8 -*-
#!/usr/bin/env python
__author__ = 'GCY'

import pymongo
import logging
import time
import ecode
import config
import global_db   #+++11.23
import mongoUtil

client = mongoUtil.getClient()

db = client[config.get('mongo_db')]
table = db[config.get('mongo_log_web_auditor')]

def init_db():
    table.drop()

# +++20151103
def add_log( admin, users, time, action, info,result):
    if len(admin) <= 0 or len(time) <= 0 or len(action) <= 0:
        raise ecode.DATA_LEN_ERROR
    try:
        if table.insert({'uid':admin, 'users':users, 'time':time,
                         'action':action, 'info':info,'result':result}):
            return True
    except:
        logging.error('add log_web:%s %s', admin, action)
    raise ecode.DB_OP
# +++ 20151118根据条件唯一定位一条日志返回
def get_log(admin,time,action):
    if len(admin) <= 0 or len(time) <= 0 or len(action) <= 0:
        raise ecode.DATA_LEN_ERROR
    try:
        log = table.find_one({"uid":admin,"time":time,"action":action},{"_id":0,"users":1})
        return log
    except:
        logging.error('get log_web failed:%s %s %s', admin,time,action)
    raise ecode.DB_OP

def get_logs( uid, action,start_time, end_time,page_size,page_index):
    logging.error("start get log")
    if(page_index<=0):
        raise ecode.DATA_LEN_ERROR
    if(len(action)<=0):
        raise ecode.DATA_LEN_ERROR
    select_tuple = {}
    if(uid!=""):
        if(uid!="all"):
            select_tuple['uid'] = uid
    if(action!=""):
        if(action!="all"):
            select_tuple['action'] = action
    if(start_time!="" or end_time!=""):
        select_tuple['time'] = {}
        if(start_time!=""):
            select_tuple['time']['$gt'] = start_time
        if(end_time!=""):
            select_tuple['time']['$lt'] = end_time
    logging.error(select_tuple)
    logs = []
    try:
        skip_count = (page_index-1)*page_size
        r = table.find( select_tuple, {'_id':0,'uid':1,'action':1,'time':1,'users':1,'info':1,'result':1}).skip(skip_count).limit(page_size)
        for item in r.sort([('time',-1)]):
            logs.append(item)

        return logs

    except:
        logging.error('get log failed. %s %s', uid,action)
    raise ecode.DB_OP

def get_log_count(uid, action,start_time, end_time):
    logging.error("start get log count")
    if(len(action)<=0):
        raise ecode.DATA_LEN_ERROR
    select_tuple = {}
    if(uid!=""):
        if(uid!="all"):
            select_tuple['uid'] = uid
    if(action!=""):
        if(action!="all"):
            select_tuple['action'] = action
    if(start_time!="" or end_time!=""):
        select_tuple['time'] = {}
        if(start_time!=""):
            select_tuple['time']['$gt'] = start_time
        if(end_time!=""):
            select_tuple['time']['$lt'] = end_time
    try:
        log_count = table.find(select_tuple).count()
        logging.error("log_count:"+str(log_count))
        return log_count
    except:
        logging.error('get log count failed. %s %s', uid,action)
    raise ecode.DB_OP

def get_log_info(uid,time,action):
    try:
        log = table.find_one({"uid":uid,"time":time,"action":action})
        if log:
            info = log['info']
            return info
        else:
            return None
    except:
        logging.error("get log contacts failed admin:%s,action:%s,time:%s",uid,action,time)
    return None


#添加一条web的审计日志，op_time为时间戳
# def add_log_web(user,op_type,op_desc,op_result,op_time):
#     if len(user) <= 0 or len(op_type) <= 0 or len(op_desc) <= 0 or len(op_result) <= 0:
#         raise ecode.DATA_LEN_ERROR
#
#     try:
#         items=global_db.get_global('log_number')   #每次都置零，需要有东西存储这个数值！！！没有考虑到并发的情况
#         if items=='':
#             items=0;
#         b=global_db.get_global('currentlimit')   #阈值
#         if b=='':
#             b=200
#         a=b-100  #告警
#         if items<=a:
#             table.insert({'user':user,'op_type':op_type,'op_desc':op_desc,'op_result':op_result, 'op_time':op_time})
#             items=items+1
#         elif items>a and items<=b:
#             table.insert({'user':user,'op_type':op_type,'op_desc':op_desc,'op_result':op_result, 'op_time':op_time})
#             items=items+1
#         else:
#             table.find().sort([('op_time',1)])
#             del_id=table.find_one()['_id']
#             table.remove(del_id)
#             table.insert({'user':user,'op_type':op_type,'op_desc':op_desc,'op_result':op_result, 'op_time':op_time})
#         # +++20160901 先弃用存入告警相关的逻辑
#         # global_db.add_global('log_number',items)
#         # #9.9+（return的数值用于返回前台的告警）
#         # if items<=a:
#         #     global_db.add_global('log_warning', 'ok')
#         #     return 111
#         # elif items>a and items<=b:
#         #     global_db.add_global('log_warning', 'need_del')
#         #     return 222
#         # else:
#         #     global_db.add_global('log_warning', 'del')
#         #     return 333
#
#     except:
#         logging.exception('add log web:%s', user)
#     raise ecode.DB_OP


#由user获取web的审计日志（后期实现按关键字查询）
def search_logs(user,start,end,log_number):
    logs = []
    exportflag={}
    try:

        if len(user)<= 0:
            r = table.find({'time':{'$gte':start,'$lte':end}},{'_id':0}).sort([('time',1)]).limit(log_number)
        else:
            r = table.find({'uid':user,'time':{'$gte':start,'$lte':end}},{'_id':0}).sort([('time',1)]).limit(log_number)
        #op_time为时间戳
        for item in r:
            logs.append(item)
        #导出日志时的标志位，这时应置相应的数组，即导出检索的日志

        exportflag['user']=user
        exportflag['start']=start
        exportflag['end']=end
        exportflag['log_number']=log_number
        global_db.add_global('auditlogexport',exportflag)
        return logs
    except:
        logging.exception('get searchlogs failed. %s',user)
        raise ecode.DB_OP

#获取前100条日审计日志
def get_audit_logs():
    audit_logs = []
    try:
        # ({'uid':admin, 'users':users, 'time':time,'action':action, 'info':info,'result':result})
        r = table.find({},{'_id':0,'uid':1,'action':1,'info':1,'result':1,'time':1,'users':1})
        if not r:
            logging.exception('get log failed. %s',audit_logs)
            raise ecode.DB_OP
        #op_time为时间戳
        for item in r.sort([('time',-1)]).limit(100):
            #将时间戳转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
            audit_logs.append(item)
        #导出日志时的标志位，这时应置空，即导出所有日志（未检索）
        # global_db.add_global('auditlogexport','')
        return audit_logs
    except:
        logging.exception('get log failed. %s',audit_logs)
        raise ecode.DB_OP

