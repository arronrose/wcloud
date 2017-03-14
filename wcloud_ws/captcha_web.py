# -*- coding: utf8 -*-
#!/usr/bin/env python

import hashlib
import sha
import random
import redis
import logging
import config

#+++ 20150804 缓存验证码（web端）
rdb = None
def get_db():
    global rdb
    if not rdb:
        rdb= redis.Redis(host=config.get('redis_host'),port=config.get('redis_port'),db=config.get('redis_captcha_web_db'))
        logging.error("redis host ,port and db is : %s,%s,%s",config.get('redis_host'),config.get('redis_port'),config.get('redis_captcha_web_db'))
    return rdb

def add_captcha( session_id, captcha ):
    if len(session_id) <= 0 or len(captcha) <= 0:
        return False
    try:
        get_db().set( session_id, captcha)
        get_db().expire(session_id,60)
        logging.info("验证码存储成功，key : %s , value : %s",session_id,captcha)
    except Exception,ex:
        logging.error('add captcha web failed. session_id:%s,captcha:%s',session_id,captcha)
        return False
    return True

def get_captcha( session_id ):
    captcha = ''
    try:
        captcha = get_db().get(session_id)
        if not captcha:
            captcha = ''
    except Exception,ex:
        logging.error('get captcha web failed. session_id:%s', session_id)
    return captcha

def del_captcha( session_id ):
    try:
        get_db().delete(session_id)
    except Exception,ex:
        logging.error('del captcha failed. session_id:%s', session_id)
