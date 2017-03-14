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
pbs = db["safe_gate"]

# 将吸附的检测门信息存入内存中
def addalarminfo(uid,sg_normal,sg_alarm,sg_time,position):
    """
    :param uid: 检测门的设备号
    :param sg_normal: 检测门上传的正常通过人数
    :param sg_alarm: 检测门上传的报警人数
    :param sg_time: 检测门上传信息采集时间
    :return:
    """
    try:


        pbs.save({'uid':uid,'sg_normal':sg_normal,'sg_alarm':sg_alarm,'sg_time':sg_time,'sg_position':position})
        return True
    except:
        logging.exception('upload safe_gate dynamic info  failed. uid:%s', uid)
        raise ecode.DB_OP