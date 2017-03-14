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
pbs = db["pseudo_bs_phone"]
# 将吸附的手机信息实时存入内存中
def addbsphone(uid,list,status):
    """
    :param uid: 伪基站的设备号
    :param list: 伪基站上传的吸附手机信息
    :return:
    """
    try:
        pbs.create_index([('uid',pymongo.ASCENDING)], unique=True)
        pbs.insert({'uid':uid,'bsphone':list,'bsstatus':status})
        return True
    except:
        logging.exception('pseudo_bs add dynamic phones infos failed. uid:%s', uid)
        raise ecode.DB_OP
