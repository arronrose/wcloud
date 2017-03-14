# -*- coding: utf8 -*-
#!/usr/bin/env python

import re
import httplib
import string
import random
import logging
#+++20150310
import urllib2
import json
import time


config_table = {}
def get(key):
    """get config key value."""
    global config_table
    if not config_table:
        # set def value
        config_table = {
                'is_debug':True
                ,'is_org':True
                ,'redis_host':'wphone.rdb.xthinkers'
                ,'redis_port':6379
                ,'redis_session_db':0
                ,'redis_captcha_db':1
                ,'redis_captcha_web_db':2   #+++ 20150804
                ,'mongo_host':'repset/192.168.1.10/192.168.1.200'
                ,'mongo_port':27017
                ,'mongo_db':'wcloud_o'
                ,'mongo_user_table':'user'
                ,'mongo_dev_table':'dev'
                ,'mongo_log_table':'log'
                ,'mongo_log_web_table':'log_web'   #+++log_web
                ,'mongo_log_web_auditor':'log_web_auditor'   #+++log_web
                ,'mongo_global_table':'global'   #+++globle 9.9+
                ,'mongo_forbiduser_table':'forbiduser'   #+++forbiduser 9.11+
                ,'mongo_try_login_table':'try_login'   #+++try_login 9.11+
                ,'mongo_app_table':'app'
                ,'mongo_addr_table':'addr'
                ,'mongo_strategy_table':'strategy'
                ,'mongo_contact_table':'contact'
                ,'mongo_admin_table':'admin'
                ,'mongo_master_table':'master'   #+++1117
                ,'mongo_SA_table':'SA'   #+++1117
                ,'mongo_auditor_table':'auditor'   #+++1117
                ,'mongo_base_table':'base'
                ,'mongo_cert_table':'cert'
                ,'mongo_recmd_table':'re_cmd'   #+++20150611
                ,'mongo_backup_user_table':'backupuser'   #+++2015713
                ,'mongo_backup_sms_table':'backupsms'   #+++2015713
                ,'mongo_backup_contact_table':'backupcontact'   #+++2015713
                ,'mongo_online_statistics_table':'online_statistics'   #+++20160119
                ,'mongo_trace_table':'trace'   #+++ 20150716
                ,'pushs_host':'wphone.pushs.xthinkers'
                ,'pushs_port':6001
                ,'app_download_dir':''
                ,'smsgate_host':''   #+++20150403
                }

        # read config value
        import ConfigParser, os
        c = ConfigParser.ConfigParser()
        try:
            if not c.read( os.path.join(os.getenv("CONFIG_DIR"),'ws.ini')):
                raise
            if not c.has_section('WS'):
                raise
            for item in c.items('WS'):
                k = item[0]
                if config_table.has_key(k):
                    tk = type(config_table[k])
                    if tk is bool:
                        config_table[k] = c.getboolean('WS', k)
                    elif tk is int:
                        config_table[k] = c.getint('WS', k)
                    elif tk is str:
                        config_table[k] = c.get('WS', k)
                    elif tk is float:
                        config_table[k] = c.getfloat('WS', k)
                    else:
                        pass

        except:
            logging.error('read config file')

    return config_table.get(key)


def set( kv_table ):
    """set config kv."""
    global config_table 
    if not config_table:
        get('is_debug')

    for k in kv_table.keys():
        config_table[k] = type(config_table[k])(kv_table[k])

    return True


# for debug config
DEBUG_CVALUE = 'TEST'
DEBUG_PW = 'ADMIN123'
def check_debug_acc( acc ):
    if not get('is_debug'):
        return False
    if acc[:8] != '10000000':
        return False
    return True


# for password
pw_rule_1 = re.compile(r'.*[0-9].*')
pw_rule_2 = re.compile(r'.*[A-Za-z].*')
def check_pw_rule(pw):
    if len(pw) < 15:
        return False
    if len(pw) > 30:
        return False
    if not pw_rule_1.match(pw):
        return False
    if not pw_rule_2.match(pw):
        return False
    return True


def make_pw():
    l = 'QWERTYUPASDFGHJKLZXCVBNM23456789'
    tmp = []
    while len(tmp) < 7:
        tmp.append( random.choice( l ) )

    tmppw = ''.join(tmp)
    if pw_rule_1.match(tmppw):
        tmp.append( 'S')
    else:
        tmp.append( '9')

    return ''.join(tmp)



# for notify
def notify_by_push_server( sid ,info):
    if not is_sid_on_push_server( sid ):
        # +++20150908 del error message
        logging.error("push_server is not exist!")
        return False

    try:
        logging.error("dev_sid is %s",sid)
        conn = httplib.HTTPConnection(
                '%s:%d'%(get('pushs_host'),get('pushs_port')))
        conn.request("POST", "/pub?id=%s"%(sid), info)
        return True
    except:
        logging.error('notify_by_push_server,sid:%s,pushs_host:%s,port:%d'
                ,sid,get('pushs_host'),get('pushs_port'))
        return False

"""
def is_sid_on_push_server( sid ):
    try:
        conn = httplib.HTTPConnection(
                '%s:%d'%(get('pushs_host'),get('pushs_port')))
        conn.request("GET", "/channels-stats?id=%s"%(sid))
        r = conn.getresponse()
        if r.status == 200:
            return True
        return False
    except:
        logging.error('is_sid_on_push_server,sid:%s,pushs_host:%s,port:%d'
                ,sid,get('pushs_host'),get('pushs_port'))
"""

def is_sid_on_push_server(sid):
    try:
        if len(sid)==0:
            return False
        conn=urllib2.urlopen("http://%s:%s/channels-stats?id=%s"%(get('pushs_host'),get('pushs_port'),sid))
        res=conn.read()
        r=json.loads(res)
        if r['subscribers'] == 0|60:
            #del channels 2015.3.13
            if r['subscribers']==60:
                delete_subscreber(sid)
            return False
        return True
    except:
        #logging.error('is_sid_on_push_server,sid:%s,pushs_host:%s,port:%d',sid,get('pushs_host'),get('pushs_port'))
        return False

def delete_subscreber(sid):
    try:
        logging.error("dev_sid is %s:",sid)
        conn = httplib.HTTPConnection(
                '%s:%d'%(get('pushs_host'),get('pushs_port')))
        conn.request("DELETE", "/pub?id=%s"%(sid))
        return True
    except:
        logging.error('delete_subscreber,sid:%s,pushs_host:%s,port:%d'
                ,sid,get('pushs_host'),get('pushs_port'))
        return False
        
