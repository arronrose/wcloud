# -*- coding: utf8 -*-
#!/usr/bin/env python

import hashlib
import sha
import random
import redis
import logging
import config


rdb = None
def get_db():
    global rdb
    if not rdb:
        rdb= redis.Redis(host=config.get('redis_host'),port=config.get('redis_port'),db=config.get('redis_captcha_db'))
        logging.error("redis host ,port and db is : %s,%s,%s",config.get('redis_host'),config.get('redis_port'),config.get('redis_captcha_db'))
    return rdb


def add_captcha( uid, captcha ):
    if len(uid) <= 0 or len(captcha) <= 0:
        return False
    try:
        get_db().set( uid, captcha)
        get_db().expire(uid,60)
        logging.warn('add captcha succeed. uid:%s,captcha:%s',uid,captcha)
    except Exception,ex:
        logging.error('add captcha failed. uid:%s,captcha:%s',uid,captcha)
        return False
    return True


def get_captcha( uid ):
    captcha = ''
    try:
        captcha = get_db().get(uid)
        logging.error("redis_captcha："+str(captcha))
        if not captcha:
            captcha = ''
    except Exception,ex:
        logging.error('get captcha failed. uid:%s', uid)
    return captcha


# def get_then_del_captcha(uid):
#     captcha = ''
#     try:
#         captcha = get_db().get(uid)
#         if not captcha:
#             captcha = ''
#         else:
#             get_db().delete( uid )
#     except Exception,ex:
#         logging.error('get captcha failed. cid:%s', uid)
#     return captcha


def del_captcha( uid ):
    try:
        get_db().delete(uid)
    except Exception,ex:
        logging.error('del captcha failed. uid:%s', uid)


