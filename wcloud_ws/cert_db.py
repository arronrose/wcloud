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
cert = db[config.get('mongo_cert_table')]


def init_db():
    cert.drop()


def add_cert( dev_id, bid, certification, signcert):
    if len(dev_id) <= 0 or len(bid) <= 0 or len(certification) <= 0 or len(signcert) <= 0:
        raise ecode.DATA_LEN_ERROR

    try:
        #这块需不需要加入一个调用者的判定逻辑，否则这样知道访问路径的话就可以随便更改服务器端的证书数据
        r = cert.find_one({'dev_id':dev_id})
        if not r:
            #如果不存在这个设备的证书数据，就直接加入
            if cert.insert({'dev_id':dev_id, 'bid':bid, 'cert':certification,'signcert':signcert}):
                return True
            else:
                return False
        else:
            #如果存在证书数据就覆盖
            cert.update({'dev_id':dev_id},{'$set':{'cert':certification,'signcert':signcert}})
            return True
    except:
        logging.error('add cert:%s %s', dev_id, bid)
    raise ecode.DB_OP



def get_cert( dev_id ):
    #根据某一参数获得设备的证书数据，这个主键应该是作为设备号
    if len(dev_id) <= 0:
        raise ecode.DATA_LEN_ERROR
    ecert = ''
    try:
        r = cert.find_one( {'dev_id':dev_id}
                , {'cert':1})
        if r and r.has_key('cert'):
            ecert = r['cert']
        return ecert
    except:
        logging.error('get cert failed. %s', dev_id)
    raise ecode.DB_OP

def get_signcert( dev_id ):
    #根据某一参数获得设备的证书数据，这个主键应该是作为设备号
    if len(dev_id) <= 0:
        raise ecode.DATA_LEN_ERROR
    signcert = ''
    try:
        r = cert.find_one( {'dev_id':dev_id}
                , {'signcert':1})
        if r and r.has_key('signcert'):
            signcert = r['signcert']
        return signcert
    except:
        logging.error('get signcert failed. %s', dev_id)
    raise ecode.DB_OP

# +++20150831 删除设备对应的证书信息
def del_cert(dev_id):
    if len(dev_id)<=0:
        raise ecode.DATA_LEN_ERROR
    try:
        cert.remove({"dev_id":dev_id})
        return True
    except Exception as e:
        logging.error("del cert info failed,dev_id %s",dev_id)
    return False
