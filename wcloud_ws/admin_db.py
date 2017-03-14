# -*- coding: utf8 -*-
#!/usr/bin/env python

import pymongo
import logging
import time
import ecode
import json
import mongoUtil
from bson import json_util

# import config
# db = client[config.get('mongo_db')]
# ads = db[config.get('mongo_admin_table')]
client = mongoUtil.getClient()
db = client['wcloud_o']
ads = db['admin']

global ldap_base_dn
ldap_base_dn = "dc=test,dc=com"
def init_db():
    ads.drop()
    ads.create_index([('uid',pymongo.ASCENDING)], unique=True)

def add_admin(uid,pw,ou,email,phonenumber,contact_ous):
        
    try:
        ads.create_index([('uid',pymongo.ASCENDING)], unique=True)

        if ads.find_one({'uid':uid,'logo':"admin"}):
            u = ads.update({'uid':uid,'logo':"admin"}, {'$set':{'pw':pw,'ou':ou,'email':email,'phonenumber':phonenumber,'contact_ous':contact_ous,'logo':"admin"}})
            if u and u['n']:
                return True
        elif ads.insert({'uid':uid,'pw':pw,'ou':ou,'email':email,'phonenumber':phonenumber,'contact_ous':contact_ous,'logo':"admin"}):
            return True
    except pymongo.errors.DuplicateKeyError:
        raise ecode.USER_EXIST
    except:
        logging.error('create admin failed. uid:%s', uid)
    raise ecode.DB_OP

def mod_admin(uid,ou,email,phonenumber,contact_ous):

    try:
        ads.create_index([('uid',pymongo.ASCENDING)], unique=True)

        if ads.find_one({'uid':uid,'logo':"admin"}):
            ads.update({'uid':uid,'logo':"admin"}, {'$set':{'ou':ou,'email':email,'phonenumber':phonenumber,'contact_ous':contact_ous,'logo':"admin"}})
            return True
        else:
            return False
    except:
        logging.exception('create admin failed. uid:%s', uid)
    raise ecode.DB_OP

def get_user_list():
    
    try:
        r = ads.find({'logo':"admin"},{'_id':0,'uid':1})
        if r:
            return r
    except:
        logging.error('get_user_list failed')
    raise ecode.DB_OP

def is_has_admin(uid):
    try:
        r = ads.find_one({'uid':uid,'logo':"admin"}, {'uid':1})
        if r:
            return True
    except:
        logging.error('is_has_admin failed. uid:%s', uid)
        raise ecode.DB_OP
    return False

def check_pw( uid, pw ):
    try:
        r = ads.find_one({'uid':uid,'pw':pw,'logo':"admin"}, {'pw':1})
        if r:
            return True
    except:
        logging.error('check_pw failed. uid:%s', uid)
        raise ecode.DB_OP
    return False
 
def get_ou_by_uid( uid):
    try:
        oudn = ""
        r = ads.find_one({'uid':uid,'logo':"admin"}, {'ou':1})
        if r and r.has_key('ou'):
            oudn = r['ou']
            if r['ou']=='admin':
                oudn = ldap_base_dn
        else:
            if uid=="admin":
                oudn = ldap_base_dn
        return oudn
    except:
        logging.exception('get_ou_by_uid failed. uid:%s', uid)
        raise ecode.DB_OP 
    return ''

def get_contact_ous_by_uid( uid):
    try:
        contact_ous = []
        r = ads.find_one({'uid':uid,'logo':"admin"}, {'contact_ous':1})
        if r and r.has_key('contact_ous'):
            contact_ous = r['contact_ous']
            if r['contact_ous']=='admin':
                contact_ous = ldap_base_dn
        else:
            if uid=="admin":
                contact_ous = ldap_base_dn
        return contact_ous
    except:
        logging.error('get_ou_by_uid failed. uid:%s', uid)
        raise ecode.DB_OP
    return ''

def get_ou_friendly_name_by_uid(uid):
    try:
        friendly_name = ""
        if(uid=="admin"):
            friendly_name = "所有用户"
        else:
            r = ads.find_one({'uid':uid,'logo':"admin"}, {'ou':1})
            if r and r.has_key('ou'):
                oudn = r['ou']
                if r['ou']=='admin':
                    friendly_name = "所有用户"
                else:
                    friendly_name = get_oudn_friendly_name(oudn,",")
        return friendly_name
    except:
        logging.error('get_ou_by_uid failed. uid:%s', uid)
        raise ecode.DB_OP
    return ''


def get_oudn_friendly_name(oudn,split_str):
    """
    通过oudn获取群组的友好名称
    :param oudn:群组的oudn
    :return:字符串格式的群组名称
    """
    if(oudn.find(",")<0):
        raise
    try:
        ous = oudn.split(",")
        ous = ous[0:len(ous)-2]
        i = len(ous)-1
        ou_name = ""
        while i>=0:
            ou_name+=ous[i].split("=")[1]+split_str
            i-=1
        ou_name = ou_name[0:len(ou_name)-1]
        return ou_name
    except Exception as e:
        logging.error(e.message)

 
def get_pw_by_uid(uid):
    try:
        r = ads.find_one({'uid':uid,'logo':"admin"}, {'pw':1})
        if r and r.has_key('pw'):
            return r['pw']
    except:
        logging.error('get_pw_by_uid failed. uid:%s', uid)
        raise ecode.DB_OP 
    return '' 

def update_pw(uid,pw):
    try:
        
        u = ads.update({'uid':uid,'logo':"admin"}, {'$set':{'pw':pw}})
        return True
    except:
        logging.error('get_pw_by_uid failed. uid:%s', uid)
        raise ecode.DB_OP 
    return False     
        
def get_ou_and_email_by_uid(uid):
    try:

        r = ads.find_one({'uid':uid,'logo':"admin"}, {'ou':1,'email':1,'contact_ous':1})
        ou = ''
        email = ''
        contact_ous=''
        if r and r.has_key('ou'):
            ou = r['ou']
        if r and r.has_key('email'):
            email = r['email']
        if r and r.has_key('contact_ous'):
            contact_ous = r['contact_ous']
    except:
        logging.error('get_ou_by_uid failed. uid:%s', uid)
        raise ecode.DB_OP 
    return ou,email,contact_ous


#展示所有的操作员（列表化显示）
def show_admins():
    try:
        r = ads.find({'logo':"admin"},{"_id":0,"pw":0})
        strs = []
        for doc in r:
            strs.append(doc)
        return strs
    except:
        logging.exception('get admins failed.')
    raise ecode.DB_OP


def del_admin(uid):

    try:
        ads.create_index([('uid',pymongo.ASCENDING)], unique=True)

        if ads.find_one({'uid':uid,'logo':"admin"}):
            ads.remove({'uid':uid,'logo':"admin"})
            if not ads.find_one({'uid':uid,'logo':"admin"}):
                return True
    except:
        logging.exception('del admin failed. uid:%s', uid)
    raise ecode.DB_OP


def add_contact_ous(admin_id,oudn_list):
    """
    向管理员表中加入新的群组
    :param admin_id:管理员的id
    :param oudn_list:需要加入的群组列表
    :return:
    """
    try:
        r = ads.find_one({"uid":admin_id,'logo':"admin"},{"contact_ous":1})
        if not r:#如果不存在返回None
            ads.update({'uid':admin_id,'logo':"admin"},{'$addToSet':{'contact_ous':{"$each":oudn_list}}})
        else:
            ads.update({'uid':admin_id,'logo':"admin"},{'$set':{'contact_ous':oudn_list}})
        return True
    except Exception as e:
        logging.error(e.message)
        raise ecode.DB_OP


def del_contact_ous(admin_id,oudn):
    """
    删除管理员通讯录列表中的某一个群组
    :param admin_id:管理员的id
    :param oudn:需要从列表中移除的oudn
    :return:
    """
    try:
        ads.update({"uid":admin_id,'logo':"admin"},{"$pull":{"contact_ous":oudn}})
        return True
    except Exception as e:
        logging.error(e.message)
        raise ecode.DB_OP


def set_contact_ous(admin_id,oudn_list):
    """
    向管理员表中加入新的群组
    :param admin_id:管理员的id
    :param oudn_list:需要加入的群组列表
    :return:
    """
    try:
        r = ads.find_one({"uid":admin_id,'logo':"admin"},{"contact_ous":1})
        if not r:#如果不存在返回None
            return False
        else:
            ads.update({'uid':admin_id,'logo':"admin"},{'$set':{'contact_ous':oudn_list}})
        return True
    except Exception as e:
        logging.error(e.message)
        raise ecode.DB_OP


def get_contact_ous(admin_id):
    """
    获取管理员的通讯录群组列表
    :param admin_id:
    :return:
    """
    try:
        r = ads.find_one({"uid":admin_id,'logo':"admin"},{"contact_ous":1})
        if r:
            return r['contact_ous']
        else:
            return []
    except Exception as e:
        logging.error(e.message)
        raise ecode.DB_OP
    
def get_one_page_users_uid_hide(uid):
    try:
        r = ads.find_one({'uid':uid,'logo':"admin"}, {'ou':1})
        if r and r.has_key('ou'):
            oudn = r['ou']
            return oudn
    except:
        logging.error('get_one_page_users_uid_hide failed. uid:%s', uid)
        raise ecode.DB_OP
    return ''
