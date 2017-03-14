# -*- coding: utf8 -*-
#!/usr/bin/env python

import pymongo
import logging
import time
import ecode
import config
import datetime
import mongoUtil


client = mongoUtil.getClient()
db = client[config.get('mongo_db')]
devs = db[config.get('mongo_dev_table')]


def init_db():
    devs.drop()
    devs.create_index([('dev_id',pymongo.ASCENDING)], unique=True)


def add_dev( dev_id, user ):
    if len(dev_id) <= 0:
        raise ecode.DATA_LEN_ERROR

    try:
        devs.create_index([('dev_id',pymongo.ASCENDING)], unique=True)
        has_dev = devs.find_one({"dev_id":dev_id})
        if not has_dev:
            if devs.insert({'dev_id':dev_id, 'loc':{'lon':'0','lat':'0'}
            ,'cmd_sn':0, 'cmds':[],'strategy_sn':0,'strategys':[],'current':{},'cur_user':user}):
                return True
        else:
            devs.update({"dev_id":dev_id},{"$set":{"cur_user":user}})
            return True
    except:
        logging.error('add new dev failed. dev_id:%s', dev_id)
    raise ecode.DB_OP


def is_has_dev( dev_id ):
    try:
        r = devs.find_one({'dev_id':dev_id}, {'dev_id':1})
        if r:
            return True
    except:
        logging.error('is_has_dev failed. dev_id:%s', dev_id)
        raise ecode.DB_OP
    return False


def del_dev( dev_id):
    try:
        u = devs.remove({'dev_id':dev_id})
        return True
    except:
        logging.error('del_dev failed. dev_id:%s', dev_id)
    raise ecode.DB_OP


def new_cmd( dev_id, cmd):
    if len(cmd) <= 0:
        raise ecode.DATA_LEN_ERROR
    if len(cmd) > 256:
        raise ecode.DATA_LEN_ERROR

    try:
        r = devs.find_and_modify({'dev_id':dev_id},{'$inc':{'cmd_sn':1}}
                ,new=True,fields={'cmd_sn':1,'cmds':1})
        if len(r['cmds']) > 7:
            devs.update({'dev_id':dev_id}, {'$pop':{'cmds':-1}})

        u = devs.update({'dev_id':dev_id}, {'$push':{'cmds':
            {'id':r['cmd_sn'],'cmd':cmd}}})
        return True
    except:
        logging.error('new_cmd failed. dev_id:%s', dev_id)
        raise ecode.DB_OP
    return False

def new_cmd_and_rs( dev_id, cmd,flog,res):
    if len(cmd) <= 0:
        raise ecode.DATA_LEN_ERROR
    if len(cmd) > 256:
        raise ecode.DATA_LEN_ERROR

    try:
        r = devs.find_and_modify({'dev_id':dev_id},{'$inc':{'cmd_sn':1}}
                ,new=True,fields={'cmd_sn':1,'cmds':1})
        if len(r['cmds']) > 2:
            devs.update({'dev_id':dev_id}, {'$pop':{'cmds':-1}})

        u = devs.update({'dev_id':dev_id}, {'$push':{'cmds':
            {'id':r['cmd_sn'],'cmd':cmd}}})
        s = devs.update({'dev_id':dev_id}, {'$set':{flog:res}})
        return True
    except:
        logging.error('new_cmd failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def get_cmds( dev_id):
    try:
        r = devs.find_one({'dev_id':dev_id}, {'cmds':1})
        return r['cmds']
    except:
        logging.error('get_cmds failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def complete_cmd( dev_id, cmd_id ):
    logging.error("cmd_id"+str(cmd_id))
    try:
        u = devs.update({'dev_id':dev_id}
                , {'$pull':{'cmds':{'id':int(cmd_id)}}})
        return True
    except:
        logging.error('complete_cmd failed. dev_id:%s', dev_id)
    raise ecode.DB_OP


def add_strategy(dev_id,strategy_id):  
    try:
        u = devs.update({'dev_id':dev_id}, {'$push':{'strategys':{'strategy_id':strategy_id,'is_read':"false"}}})
        return True
    except:
        logging.error('add_strategy failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def strategy_is_read(dev_id,strategy_id):
    try:
        stra = devs.find_one({'dev_id':dev_id},{'strategys':1})
       
        for s in stra['strategys']:
           if s['strategy_id']== strategy_id:
               s['is_read']="true"
               break
        u = devs.update({'dev_id':dev_id},{'$set':{"strategys":stra['strategys']}})
        return True
    except:
        logging.error('strategy_is_read failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def strategy_is_not_read(dev_id,strategy_id):
    try:
       stra = devs.find_one({'dev_id':dev_id},{'strategys':1})
       
       for s in stra['strategys']:
           if s['strategy_id']== strategy_id:
               s['is_read']="false"
               break
       u = devs.update({'dev_id':dev_id},{'$set':{"strategys":stra['strategys']}})
       return True
    except:
        logging.error('strategy_is_not_read failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def strategy_need_del(dev_id,strategy_id):
    try:
       stra = devs.find_one({'dev_id':dev_id},{'strategys':1})
       if stra:
           for s in stra['strategys']:
               if s['strategy_id']== strategy_id:
                   s['is_read']="delete"
                   break
           u = devs.update({'dev_id':dev_id},{'$set':{"strategys":stra['strategys']}})
           return True
       else:
           return False
    except:
        logging.error('strategy_need_delete failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def is_has_strategy_id(dev_id,strategy_id):
    try:
       stra = devs.find_one({'dev_id':dev_id},{'strategys':1})
       flog=0
       for s in stra['strategys']:
           if s['strategy_id']== strategy_id:
               flog=1
               break
       if flog == 1:
           return True
       else: 
           return False         
    except:
        logging.error('is_has_strategy_id failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def get_strategy_ids(cur_user):
    try:
        r = devs.find_one({'cur_user':cur_user})
        if not r:
            return 'no'
        if r.has_key("strategys"):
            return r["strategys"]
        else:
            return []
    except:
        logging.error('get_strategy_ids failed. cur_user:%s', cur_user)
    raise ecode.DB_OP
        
def complete_strategy( dev_id, strategy_id ):
    try:
        u = devs.update({'dev_id':dev_id}
                , {'$pull':{'strategys':{'strategy_id':strategy_id}}})
        return True
    except:
        logging.error('complete_strategy failed. dev_id:%s', dev_id)
    raise ecode.DB_OP
def set_loc( dev_id, lon, lat):
    if len(lon) <= 0 or len(lat) <= 0:
        raise ecode.DATA_LEN_ERROR

    try:
        t = str(int(time.time()))

        u = devs.update({'dev_id':dev_id}
                , {'$set':{'loc':{'lon':lon,'lat':lat}
                    , 'last_update':t }})
        return True
    except:
        logging.error('set_loc failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

# +++20151207 refresh dev_last_update
def set_dev_last_update(dev_id,time):
    try:
        devs.update({'dev_id':dev_id}
                , {'$set':{'last_update':time }})
        return True
    except:
        logging.error('set_user_dev_last_update failed. dev_id:%s', dev_id)
        raise ecode.DB_OP


def get_loc( dev_id ):
    try:
        r = devs.find_one({'dev_id':dev_id}, {'loc':1})
        return r['loc']
    except:
        logging.error('get_loc failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def get_onlinetime( dev_id ):
    try:
        r = devs.find_one({'dev_id':dev_id}, {'_id':0,'onlinetime':1})
        if not r:
            t = time.localtime()
            tt = datetime.datetime(t[0],t[1],t[2])
            ttt = time.mktime(tt.timetuple())
            devs.update({'dev_id':dev_id},{'$set':{'online':1,'outline':0,'onlinetime':ttt }})
            return ttt
        return r['onlinetime']
    except:
        logging.error('get_onlinetime failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def get_onlinetimes( dev_id ):
    try:
        r = devs.find_one({'dev_id':dev_id}, {'_id':0,'onlinetime':1})
        if not r:
            t = time.localtime()
            tt = datetime.datetime(t[0],t[1],t[2])
            ttt = time.mktime(tt.timetuple())
            devs.update({'dev_id':dev_id},{'$set':{'online':0,'outline':0,'onlinetime':ttt }})
            return ttt
        return r['onlinetime']
    except:
        logging.error('get_onlinetime failed. dev_id:%s', dev_id)
    raise ecode.DB_OP


def get_onlinestate( dev_id ):
    try:
        r = devs.find_one({'dev_id':dev_id}, {'_id':0,'online':1,'outline':1})
        if not r:
            t = time.localtime()
            tt = datetime.datetime(t[0],t[1],t[2])
            ttt = time.mktime(tt.timetuple())
            devs.update({'dev_id':dev_id},{'$set':{'online':0,'outline':0,'onlinetime':ttt }})            
        return r
    except:
        logging.error('get_onlinestate failed. dev_id:%s', dev_id)
        raise ecode.DB_OP
    return {}

# +++20151231获取用户的使用时间情况
def get_use_state(dev_id):
    try:
        r = devs.find_one({'dev_id':dev_id}, {'_id':0,'online':1,'outline':1})
        return r
    except:
        logging.error('get_onlinestate failed. dev_id:%s', dev_id)
        raise ecode.DB_OP
    return {}

def set_onlinestate( dev_id, onlinestate ):
    try:
        t = time.localtime()
        tt = datetime.datetime(t[0],t[1],t[2])
        ttt = time.mktime(tt.timetuple())
        u = devs.update({'dev_id':dev_id},{'$set':{'online':onlinestate,'onlinetime':ttt }})
        return True
    except:
        logging.error('set_onlinestate failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def set_outlinestate( dev_id, onlinestate, outlinestate ):
    try:
        t = time.localtime()
        tt = datetime.datetime(t[0],t[1],t[2])
        ttt = time.mktime(tt.timetuple())
        u = devs.update({'dev_id':dev_id},{'$set':{'online':onlinestate,'outline':outlinestate,'onlinetime':ttt }})
        return True
    except:
        logging.error('set_outlinestate failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def set_outlinestate1( dev_id, onlinestate, outlinestate ):
    try:
        # +++ 20150901 change time
        now = time.time()
        t = time.localtime(now-24*3600)
        tt = datetime.datetime(t[0],t[1],t[2])
        ttt = time.mktime(tt.timetuple())
        u = devs.update({'dev_id':dev_id},{'$set':{'online':onlinestate,'outline':outlinestate,'onlinetime':ttt }})
        return True
    except:
        logging.error('set_outlinestate failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def set_rs( dev_id, info,rs):

    try:
        if (info == "wifi"):
            u = devs.update( {'dev_id':dev_id}, {'$set':{'wifi' :rs}})
        if (info == "bluetooth"):
            u = devs.update( {'dev_id':dev_id}, {'$set':{'bluetooth' :rs}})
        if (info == "camera"):
            u = devs.update( {'dev_id':dev_id}, {'$set':{'camera' :rs}})
        if (info == "tape"):
            u = devs.update( {'dev_id':dev_id}, {'$set':{'tape' :rs}})
        if (info == "gps"):
            u = devs.update( {'dev_id':dev_id}, {'$set':{'gps' :rs}})
        if (info == "mobiledata"):
            u = devs.update( {'dev_id':dev_id}, {'$set':{'mobiledata' :rs}})
        if (info == "usb_connect"):
            u = devs.update( {'dev_id':dev_id}, {'$set':{'usb_connect' :rs}})
        if (info == "usb_debug"):
            u = devs.update( {'dev_id':dev_id}, {'$set':{'usb_debug' :rs}})
        return True
    except:
        logging.error('set_rt failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def set_all_rs( dev_id,rs):

    try:
        u = devs.update( {'dev_id':dev_id}, {'$set':{'camera' :rs,'bluetooth':rs,'wifi':rs,'tape':rs,'gps':rs,'mobiledata':rs,'usb_connect':rs,'usb_debug':rs}})
        return True
    except:
        logging.error('set_all_rt failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def get_rs( dev_id, info):

    try:
        
        if (info == "wifi"):
            r = devs.find_one( {'dev_id':dev_id}, {'wifi' :1})
            return r['wifi']
        if (info == "bluetooth"):
            r = devs.find_one( {'dev_id':dev_id}, {'bluetooth' :1})
            return r['bluetooth']
        if (info == "camera"):
            r = devs.find_one( {'dev_id':dev_id}, {'camera' :1})
            return r['camera']
        if (info == "tape"):
            r = devs.find_one( {'dev_id':dev_id}, {'tape' :1})
            return r['tape']
        if (info == "gps"):
            r = devs.find_one( {'dev_id':dev_id}, {'gps' :1})
            return r['gps']
        if (info == "mobiledata"):
            r = devs.find_one( {'dev_id':dev_id}, {'mobiledata' :1})
            return r['mobiledata']
        if (info == "usb_connect"):
            r = devs.find_one( {'dev_id':dev_id}, {'usb_connect' :1})
            return r['usb_connect']
        if (info == "usb_debug"):
            r = devs.find_one( {'dev_id':dev_id}, {'usb_debug' :1})
            return r['usb_debug']
    except:
        logging.error('get_rt failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def get_last_update( dev_id ):
    try:
        r = devs.find_one({'dev_id':dev_id}, {'last_update':1})
        return r['last_update']
    except:
        logging.error('get_last_update failed. dev_id:%s', dev_id)
    raise ecode.DB_OP


def get_static_info( dev_id, k ):
    try:
        r = devs.find_one({'dev_id':dev_id}, {'static_info':1})
        if r.has_key('static_info') and r['static_info'].has_key(k):
            return r['static_info'][k]
        else:
            return ''
    except:
        logging.error('get_static_info failed. dev_id:%s', dev_id)
    raise ecode.DB_OP


def set_static_info( dev_id, k, v ):
    # 20160818值可以为空
    # if len(k) <= 0 or len(v) <= 0:
    #     raise ecode.DATA_LEN_ERROR
    if len(k) <= 0:
        raise ecode.DATA_LEN_ERROR
    if len(k) > 32:
        raise ecode.DATA_LEN_ERROR
    if len(v) > 128:
        raise ecode.DATA_LEN_ERROR

    try:
        t = str(int(time.time()))
        u = devs.update({'dev_id':dev_id}
                , {'$set':{'static_info.%s'%(k):v,'last_update':t}})
        return True
    except:
        logging.error('set_static_info failed. dev_id:%s', dev_id)
    raise ecode.DB_OP


def get_app_info( dev_id ):
    try:
        r = devs.find_one({'dev_id':dev_id}, {'app_info':1})
        if r.has_key('app_info'):
            return r['app_info']
        else:
            return ''
    except:
        logging.error('get_app_info failed. dev_id:%s', dev_id)
    raise ecode.DB_OP


def set_app_info( dev_id, apps ):
    if len(apps) <= 0:
        raise ecode.DATA_LEN_ERROR

    try:
        u = devs.update({'dev_id':dev_id}
                , {'$set':{'app_info':apps}})
        return True
    except:
        logging.error('set_app_info failed. dev_id:%s', dev_id)
    raise ecode.DB_OP




def get_web_app_info( dev_id ):
    try:
        r = devs.find_one({'dev_id':dev_id}, {'web_app_info':1})
        if r.has_key('web_app_info'):
            return r['web_app_info']
        else:
            return ''
    except:
        logging.error('get_web_app_info failed. dev_id:%s', dev_id)
    raise ecode.DB_OP


def set_web_app_info( dev_id, apps ):
    if len(apps) <= 0:
        raise ecode.DATA_LEN_ERROR

    try:
        u = devs.update({'dev_id':dev_id}
                , {'$set':{'web_app_info':apps}})
        return True
    except:
        logging.error('set_web_app_info failed. dev_id:%s', dev_id)
    raise ecode.DB_OP


def get_cur_user( dev_id ):
    try:
        r = devs.find_one({'dev_id':dev_id}, {'cur_user':1})
        if r :
            return r['cur_user']
        return ''
    except:
        logging.error('get_cur_user failed. dev_id:%s', dev_id)
    raise ecode.DB_OP

def get_dev_id_by_curuser(curuser):
    try:
        r = devs.find_one({'cur_user':curuser},{'dev_id':1})
        if not r:
            return None
        return r['dev_id']
    except:
        logging.error('get dev_id by cur_user failed. cur_user:%s',curuser)
    raise ecode.DB_OP

#+++ 20150612
def remove_cmd(dev_id):
    try:
        u = devs.update({'dev_id':dev_id},{'$set':{'cmds':[]}})
        return True
    except:
        logging.error('remove_cmd failed. dev_id:%s', dev_id)
    raise ecode.DB_OP
#+++ 20150615
def remove_expire_strategy(cur_user,strategy_id):
    try:
        r = devs.find_one({'cur_user':cur_user})
        if not r:
            return True
        if r.has_key("strategys"):
            u = devs.update({'cur_user':cur_user}, {'$pull':{'strategys':{'strategy_id':strategy_id}}})
        return True
    except:
        logging.error('get_strategy_ids failed. cur_user:%s', cur_user)
    raise ecode.DB_OP
        
#+++ 20150612
def remove_strategy(cur_user):
    try:
        u = devs.update({'cur_user':cur_user},{'$set':{"strategys":[]}})
        return True
    except:
        logging.error('remove_strategy failed. cur_user:%s', cur_user)
        raise ecode.DB_OP
    return False

#+++ 20150619
def is_has_user(cur_user):
    try:
        r = devs.find_one({'cur_user':cur_user}, {'cur_user':1})
        if r:
            return True
    except:
        logging.error('is_has_user failed. cur_user:%s', cur_user)
        raise ecode.DB_OP
    return False

def update_strategy(dev_id,strategy_ids):  
    try:
        for strategy in strategy_ids:
            u = devs.update({'dev_id':dev_id}, {'$push':{'strategys':strategy}})
            return True
    except:
        logging.error('add_strategy failed. dev_id:%s', dev_id)
    raise ecode.DB_OP


def get_dev_by_id(dev_id):
    """
    +++20160223 根据dev_id获取设备信息
    :param dev_id:设备号
    :return:返回相应的设备信息
    """
    dev = None
    try:
        dev = devs.find_one({"dev_id":dev_id},{"_id":0,"dev_id":1,"cur_user":1})
        return dev
    except Exception as e:
        logging.error("get_dev_by_id failed. dev_id:%s",dev_id)
    raise ecode.DB_OP


def change_bind_uid(dev_id,pnumber):
    """
    +++20160223 修改设备的绑定关系
    :param dev_id:需要修改的设备
    :param pnumber: 需要绑定的号码
    :return:修改结果
    """
    try:
        devs.update({"dev_id":dev_id},{"$set":{"cur_user":pnumber}})
        return True
    except Exception as e:
        logging.error("dev_db.py change_bind_uid failed,dev_id:%s",dev_id)
    return False

