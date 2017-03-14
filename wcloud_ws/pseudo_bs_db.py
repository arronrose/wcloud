__author__ = 'arron_rose'
# -*- coding:utf8 -*-
import pymongo
import logging
import time
import ecode
import json

import mongoUtil

client = mongoUtil.getClient()
db = client["wcloud_o"]
pbs = db["pseudo_bs"]


def init_db():
    pbs.drop()
    pbs.create_index([('uid',pymongo.ASCENDING)], unique=True)
# 管控端添加新的设备，(设备号，设备类型，所属部门)******
def addpbsinfo(uid,type,institute):
    try:
        # 新增设备默认设备的工作状态为离线0
        pbs.create_index([('uid',pymongo.ASCENDING)], unique=True)
        if(type=="pseudo_bs"):
            if pbs.find_one({'uid':uid}):
                pbs.update({'uid':uid},{'$set':{'type':type,'institute':institute}})
            elif pbs.insert({'uid':uid,
                             'type':type,
                             'status':"0",
                             'institute':institute,
                             'position':"",
                             'last_time':"",
                             'remark':"",
                             'infos':{
                                 'standard':"",
                                 'power':"",
                                 'radius':"",
                                 'whitelist':[]
                             }
                             }):
                return True
        elif(type=="safe_gate"):
            if pbs.find_one({'uid':uid}):
                pbs.update({'uid':uid},{'$set':{'type':type,'institute':institute}})
            elif pbs.insert({'uid':uid,
                             'type':type,
                             'status':"0",
                             'institute':institute,
                             'position':"",
                             'last_time':"",
                             'remark':"",
                             'infos':{}
                             }):
                return True
    except:
        logging.exception('web add new static pseudo_bs or safe_gate devices failed. uid:%s', uid)
        raise ecode.DB_OP
# 删除设备***
def del_pbs(uid):
    try:
        pbs.create_index([('uid',pymongo.ASCENDING)], unique=True)
        if pbs.find_one({'uid':uid}):
            pbs.remove({'uid':uid})
            if not pbs.find_one({'uid':uid}):
                return True
    except:
        logging.exception('del control devices failed. uid:%s', uid)
    raise ecode.DB_OP
#左侧树聚类显示***
def show_pbs():
    try:
        # 聚类函数distinct
        r=pbs.distinct("institute")
        strs = []
        for doc in r:
            strs.append(doc)
        return strs
    except:
        logging.exception('get pseudo_bs details to left-body failed.')
    raise ecode.DB_OP

# 中间列表聚类显示***
def show_list(inst):
    try:
        r=pbs.find({"institute":inst},{"_id":0,'remark':0,'infos':0})
        strs=[]
        for i in r:
            strs.append(i)
        return strs
    except:
        logging.exception('get pseudo_bs details to middle-body show failed.')
    raise ecode.DB_OP
# 右下角详细信息列表化展示***
def show_details(uid):
    try:
        r=pbs.find({'uid':uid},{'_id':0,'infos.whitelist':0})
        strs=[]
        for i in r:
            strs.append(i)
        return strs
    except:
        logging.exception('show pseudo_bs details failed')
# 右下角白名单管理展示白名单列表***
def show_whitelist(uid):
    try:
        r=pbs.find({'uid':uid},{'_id':0,'infos.whitelist':1})
        strs=[]
        for i in r:
            strs.append(i)
        return strs
    except:
        logging.exception('show whitelist failed')

# 伪基站上传信息时才调用******
def add_pseudo_bs(uid,status,position,last_time,standard,power,radius,whitelist):
    """
    uid: 设备id
    status: 设备状态
    type: 设备类型伪基站
    institute: 设备所属单位
    position: 设备位置
    last_time: 设备最近开机时间
    remark: 设备备注
    infos: 设备信息
    {
           standard: 基站制式
           power: 基站发射功率
           radius: 基站工作半径
           whitelist: 基站白名单
    }
    """
    try:
        pbs.create_index([('uid',pymongo.ASCENDING)], unique=True)
        if pbs.find_one({'uid':uid}):
            pbs.update({'uid':uid},{'$set':  {
                                                'status':status,

                                                'position':position,
                                                'last_time':last_time,

                                                 'infos':{
                                                             'standard':standard,
                                                             'power':power,
                                                             'radius':radius,
                                                             'whitelist':whitelist
                                                         }
                                                 }})
            return True
    except pymongo.errors.DuplicateKeyError:
        raise ecode.USER_EXIST
    except:
        logging.exception('pseudo_bs add new static infos failed. uid:%s', uid)
    raise ecode.DB_OP

# 修改基站状态******
def updatastatus(uid,state):
    try:
        if pbs.find_one({'uid':uid}):
            pbs.update({'uid':uid},{'$set':{'status':state}})
            return True
        else:
            return False
    except:
        logging.exception('modify pseudo_bs status failed. uid:%s', uid)
        raise ecode.DB_OP
# 修改基站作用半径******
def updataradius(uid,radius):
    try:
        if pbs.find_one({'uid':uid}):
            pbs.update({'uid':uid},{'$set':{'infos.radius':radius}})
        else:
            return False
    except:
        logging.exception('modify pseudo_bs radius failed. uid:%s', uid)
        raise ecode.DB_OP
# 修改基站功率******
def updatapower(uid,power):
    try:
        if pbs.find_one({'uid':uid}):
            pbs.update({'uid':uid},{'$set':{'infos.power':power}})
        else:
            return False
    except:
        logging.exception('modify pseudo_bs power failed. uid:%s', uid)
        raise ecode.DB_OP
# 修改白名单******
def updatawhitelist(uid,change,number):
    try:
        if change=="1":
            if not pbs.find_one({'uid':uid}):
                # 加each保证唯一插入
                # pbs.update({"uid" : uid}, {"$addToSet" : {"infos.whitelist" : {"$each" : number}}})
                pbs.update({"uid" : uid}, {"$addToSet" : {"infos.whitelist":number}})
            else:
                return False
        if change=="-1":
            if pbs.find_one({'uid':uid}):
                pbs.update({'uid':uid},{"$pull":{'infos.whitelist':number}})
            else:
                return False
    except:
        logging.exception('modify pseudo_bs whitelist failed. uid:%s', uid)
        raise ecode.DB_OP


# {'uid':"1234566",'type':"pseudo_bs",'status':"1",'institute':"中科院",'standard':"GSM",'power':"50",'radius':"100",'position':"111 333",'last_time':"2016年12月13日 19:00:00",'remark':"模拟的第一个数据",'whitelist':["1234","5678"]}
# 检测门上传信息时才调用***
def add_safe_gate(uid,status,last_time,position):
    """
    uid: 设备id
    status: 设备状态
    type: 设备类型检测门
    institute: 设备所属单位
    position: 设备位置
    last_time: 设备最近开机时间
    remark: 设备备注
    infos: 设备信息
    {
           #type检测门，这一项为空#
    }
    """
    try:
        pbs.create_index([('uid',pymongo.ASCENDING)], unique=True)
        if pbs.find_one({'uid':uid}):
            pbs.update({'uid':uid},{'$set':  {
                                                'status':status,
                                                'last_time':last_time,
                                                'position':position,
                                                 }})
            return True
    except pymongo.errors.DuplicateKeyError:
        raise ecode.USER_EXIST
    except:
        logging.exception('safe_gate add new static infos failed. uid:%s', uid)
    raise ecode.DB_OP

def shutdown(uid):
    try:
         pbs.create_index([('uid',pymongo.ASCENDING)], unique=True)
         if pbs.find_one({'uid':uid}):
             pbs.update({'uid':uid},{'$set':{ 'status':"0"}})
             return True
    except pymongo.errors.DuplicateKeyError:
         raise ecode.USER_EXIST
    except:
         logging.exception('shutdown failed. uid:%s', uid)
    raise ecode.DB_OP