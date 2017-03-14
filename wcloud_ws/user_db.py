# -*- coding: utf8 -*-
#!/usr/bin/env python

import pymongo
import logging
import sha
import ecode
import config
import mongoUtil
import time
import datetime
import re
import org
import user_ldap
import random


client = mongoUtil.getClient()
db = client[config.get('mongo_db')]
users = db[config.get('mongo_user_table')]



def init_db():
    users.drop()
    users.create_index([('uid',pymongo.ASCENDING)], unique=True)


def create(uid,pw,status,username,email,title,oudn):
    try:
        users.create_index([('uid',pymongo.ASCENDING)], unique=True)
        users.create_index([('key',pymongo.ASCENDING)], unique=False)
        # +++20150803 建立oudn的查询索引
        users.create_index([('oudn',pymongo.ASCENDING)], unique=False)
        # +++20150805 建立创建时间索引，为后边分页排序用
        users.create_index([('create_time',pymongo.ASCENDING)], unique=False)
        if users.find_one({'uid':uid,'verified':0}, {'uid':1}):
            u = users.update({'uid':uid}, {'$set':{'pw':pw}})
            return True
        else:
            key = get_key(18)
            create_time=int(time.time()*1000)
            if users.insert({'key':key,'uid':uid,'pw':pw,'status':status,'username':username,'email':email,
                           'title':title,'oudn':oudn,'create_time':create_time,'devs':[],'verified':0,'pw_exp':1}):
                return True
    except pymongo.errors.DuplicateKeyError:
        raise ecode.USER_EXIST
    except:
        logging.exception('create user failed. uid:%s', uid)
    raise ecode.DB_OP


def online_op(key):
    """
    用户登录时与时间相关的操作
    :param key: 登录用户的主键
    :return:
    """
    if len(key)<=0:
        raise ecode.DATA_LEN_ERROR
    try:
        #进入到这个函数应该已经找到用户了,构造用户在线时间
        online_time_stamp = str(int(time.time()))   #获取登录时的秒时间戳
        localtime = time.localtime()
        date_of_today = datetime.datetime(localtime[0],localtime[1],localtime[2])
        date_stamp = time.mktime(date_of_today.timetuple())
        result = users.find_one({"key":key})
        if result:
            if not result.has_key("online"):
                users.update({"key":key},{"$set":{"last_update":online_time_stamp,"online":1,
                                          "outline":0,"onlinetime":date_stamp}})
            else:
                users.update({"key":key},{"$set":{"last_update":online_time_stamp}})
    except Exception as e:
        logging.exception('create user failed. key:%s', key)


def get_onlinetime( key ):
    try:
        r = users.find_one({'key':key}, {'_id':0,'onlinetime':1})
        if not r:
            t = time.localtime()
            tt = datetime.datetime(t[0],t[1],t[2])
            ttt = time.mktime(tt.timetuple())
            users.update({'key':key},{'$set':{'online':1,'outline':0,'onlinetime':ttt }})
            return ttt
        return r['onlinetime']
    except:
        logging.exception('get_onlinetime failed. key:%s', key)
    raise ecode.DB_OP


def get_onlinetimes( key ):
    try:
        r = users.find_one({'key':key}, {'_id':0,'onlinetime':1})
        if not r:
            t = time.localtime()
            tt = datetime.datetime(t[0],t[1],t[2])
            ttt = time.mktime(tt.timetuple())
            users.update({'key':key},{'$set':{'online':0,'outline':0,'onlinetime':ttt }})
            return ttt
        return r['onlinetime']
    except:
        logging.exception('get_onlinetime failed. key:%s', key)
    raise ecode.DB_OP


def get_onlinestate( key ):
    try:
        r = users.find_one({'key':key}, {'_id':0,'online':1,'outline':1})
        if not r:
            t = time.localtime()
            tt = datetime.datetime(t[0],t[1],t[2])
            ttt = time.mktime(tt.timetuple())
            users.update({'key':key},{'$set':{'online':0,'outline':0,'onlinetime':ttt }})
        return r
    except:
        logging.exception('get_onlinestate failed. key:%s', key)
        raise ecode.DB_OP
    return {}


# +++20151231获取用户的使用时间情况
def get_use_state(key):
    try:
        r = users.find_one({'key':key}, {'_id':0,'online':1,'outline':1})
        return r
    except:
        logging.exception('get_onlinestate failed. key:%s', key)
        raise ecode.DB_OP
    return {}


def set_onlinestate( key, onlinestate ):
    try:
        t = time.localtime()
        tt = datetime.datetime(t[0],t[1],t[2])
        ttt = time.mktime(tt.timetuple())
        u = users.update({'key':key},{'$set':{'online':onlinestate,'onlinetime':ttt }})
        return True
    except:
        logging.exception('set_onlinestate failed. key:%s', key)
    raise ecode.DB_OP


def set_outlinestate( key, onlinestate, outlinestate ):
    try:
        t = time.localtime()
        tt = datetime.datetime(t[0],t[1],t[2])
        ttt = time.mktime(tt.timetuple())
        u = users.update({'key':key},{'$set':{'online':onlinestate,'outline':outlinestate,'onlinetime':ttt }})
        return True
    except:
        logging.exception('set_outlinestate failed. key:%s', key)
    raise ecode.DB_OP


def set_outlinestate1( key, onlinestate, outlinestate ):
    try:
        # +++ 20150901 change time
        now = time.time()
        t = time.localtime(now-24*3600)
        tt = datetime.datetime(t[0],t[1],t[2])
        ttt = time.mktime(tt.timetuple())
        u = users.update({'key':key},{'$set':{'online':onlinestate,'outline':outlinestate,'onlinetime':ttt }})
        return True
    except:
        logging.exception('set_outlinestate failed. key:%s', key)
    raise ecode.DB_OP


def get_last_update( key ):
    try:
        r = users.find_one({'key':key}, {'last_update':1})
        if r.has_key("last_update"):
            return r['last_update']
        else:
            return ""
    except:
        logging.exception('get_last_update failed. key:%s', key)
    raise ecode.DB_OP


# +++20160217 加入生成随机数主键的函数
def get_key(len):
    """
    :param len:键的长度
    :return:生成的键
    """
    key = 0
    if len>0:
        start = int("1"+(len-1)*"0")
        end = int(len*"9")
        key = random.randint(start,end)
        # 只要存在key就重复生成，保证key的唯一性
        while is_has_key(key):
            key = random.randint(start,end)
    return str(key)


def is_has_key(key):
    """
    查找是否存在此键值
    :param key: 需要查找的键值
    :return:查找结果，存在True，不存在False
    """
    exist = False
    try:
        result = users.find_one({"key":key})
        if result:
            exist = True
    except Exception as e:
        logging.exception('is_has_key failed. key:%s', key)
        print e.message
    return exist


def share_user_info():
    org_config = org.get_config()
    uldap = user_ldap.create_ldap( ip = org_config['ldap_host']
                    , port = org_config['ldap_port']
                    , base_dn = org_config['ldap_base_dn']
                    , user_dn = org_config['ldap_user_dn']
                    , pw = org_config['ldap_pw']
                    , at_uid = org_config['ldap_at_uid']
                    , at_allow_use = org_config['ldap_at_allow_use']
                    , at_pnumber = org_config['ldap_at_pnumber']
                    , at_email = org_config['ldap_at_email']
                    , at_username = org_config['ldap_at_username']
                    , at_dn = org_config['ldap_at_dn']
                    , at_ou = org_config['ldap_at_ou']
                    , at_job = org_config['ldap_at_job'])

    allusers = uldap.get_all_users()
    logging.warn(str(allusers))

    for item in allusers:
        itemdn = item[0]
        oudn = itemdn[itemdn.find(',')+1:]
        itemcontent = item[1]
        phone = itemcontent['telephoneNumber']
        if is_has_user(phone[0]):
            continue
        else:
            email = ''
            if itemcontent.get("mail"):
                email = itemcontent.get("mail")[0]
            users.insert({'uid':phone[0],'status':0,'username':itemcontent['cn'][0],'email':email,'devs':[],'verified':0,'pw_exp':1,
                        'oudn':oudn,'create_time':int(time.time()*1000),"pw":sha.new("12345678")})

def is_has_user( uid ):
    try:
        r = users.find_one({'uid':uid}, {'uid':1})
        if r:
            return True
    except:
        logging.exception('is_has_user failed. uid:%s', uid)
        raise ecode.DB_OP
    return False


def check_is_has_user(map):
    try:
        r = users.find_one(map,{'uid':1})
        if r:
            return True
    except Exception as e:
        logging.error("check is_has_user failed, map is:%s",str(map))
        raise ecode.DB_OP
    return False

def del_user( uid ):
    try:
        u = users.remove({'uid':uid})
        return True
    except:
        logging.exception('del_user failed. uid:%s', uid)
    return False



def is_verified( uid ):
    try:
        r = users.find_one({'uid':uid,'verified':1}, {'uid':1})
        if r:
            return True
    except:
        logging.exception('is_verified failed. uid:%s', uid)
        raise ecode.DB_OP
    return False



def verified( uid ):
    try:
        u = users.update({'uid':uid}, {'$set':{'verified':1}})
        return True
    except:
        logging.exception('verified failed. uid:%s', uid)
    raise ecode.DB_OP


def is_pw_exp( uid ):
    try:
        r = users.find_one({'uid':uid,'pw_exp':1}, {'pw_exp':1})
        if r:
            return True
    except:
        logging.exception('is_pw_exp failed. uid:%s', uid)
        raise ecode.DB_OP
    return False



def pw_exp( uid, is_pw_exp ):
    try:
        if is_pw_exp:
            exp = 1 
        else:
            exp = 0
        u = users.update( {'uid':uid}, {'$set':{'pw_exp':exp}})
        return True
    except:
        logging.exception('pw_exp failed. uid:%s', uid)
    raise ecode.DB_OP



def check_pw( uid, pw ):
    try:
        if config.check_debug_acc(uid) and pw == sha.new(config.DEBUG_PW).hexdigest():
            return True

        r = users.find_one({'uid':uid,'pw':pw}, {'pw':1})
        if r:
            return True
    except:
        logging.exception('check_pw failed. uid:%s', uid)
        raise ecode.DB_OP
    return False


def set_pw( uid, pw ):

    try:
        u = users.update( {'uid':uid}, {'$set':{'pw':pw}})
        return True
    except:
        logging.exception('set_pw failed. uid:%s', uid)
    raise ecode.DB_OP


def user_list():
    allusers = []
    try:
        r = users.find( {}, {'_id':0,'uid':1})
        if r:
            for item in r:
                if item.has_key("uid"):
                    allusers.append(item['uid'])
                else:
                    continue
            return allusers
    except:
        logging.exception('get_user_list failed. uid:%s')
    raise ecode.DB_OP


def key_list():
    allusers = []
    try:
        r = users.find( {}, {'_id':0,'key':1,'uid':1})
        if r:
            for item in r:
                if item.has_key("key"):
                    allusers.append(item)
                else:
                    continue
            return allusers
    except:
        logging.exception('get_key_list failed.')
    raise ecode.DB_OP


def add_dev( uid, dev_id):
    if len(dev_id) <= 0:
        raise ecode.DATA_LEN_ERROR

    try:
        r = users.find_one( {'uid':uid}, {'devs':1})
        if len(r['devs']) >= 16:
            raise ecode.TOO_MANY_DEVS

        u = users.update( {'uid':uid}, {'$addToSet':{'devs':dev_id}})
        return True
    except:
        logging.exception('update_dev failed. uid:%s', uid)
    raise ecode.DB_OP



def del_dev( uid, dev_id):
    try:
        u = users.update( {'uid':uid}, {'$pull':{'devs':dev_id}})
        return True
    except:
        logging.exception('del_dev failed. uid:%s', uid)
    raise ecode.DB_OP



def is_my_dev( uid, dev_id):
    try:
        r = users.find_one( {'uid':uid, 'devs':dev_id}
                , {'uid':1} )
        if r:
            return True
    except:
        logging.exception('is_my_dev failed. uid:%s', uid)
        raise ecode.DB_OP
    return False



def devs( uid ):
    try:
        r = users.find_one( {'uid':uid}, {'devs':1} )
        if r:
            return r['devs']
    except:
        logging.exception('is_my_dev failed. uid:%s', uid)
        raise ecode.DB_OP
    return [] 

def add_contact( uid, contacts):
    try:
        r = users.find_one({'uid':uid})
        if r.has_key("contacts") :
            #+++改20150820如果有则向contacts中追加，可以直接追加集合,但是要加入each符号 改1105查重后添加
            old_contacts = list(r['contacts'])
            for item in contacts:
                new_uid = item['uid']
                new_flag = item['flag']
                has_uid = False
                for old_item in old_contacts:
                    old_uid = old_item['uid']
                    if(new_uid==old_uid):
                        has_uid=True
                        if(old_item.has_key('flag')):
                            old_flag = old_item['flag']
                            if(int(old_flag)+int(new_flag)>=1):
                                old_item['flag']=1
                            else:
                                old_item['flag']=0
                        else:
                            old_item['flag']=new_flag
                        break
                    else:
                        continue
                if(has_uid==False):
                    old_contacts.append(item)
            users.update({'uid':uid},{'$set':{'contacts':old_contacts}})
            return True
        else:
            # +++如果没有的话需要insert进去
            users.update({'uid':uid},{"$set":{'contacts':contacts}})
            return True
    except:
        logging.exception('add_contact failed. uid:%s', uid)
    raise ecode.DB_OP

# +++20151105 改，直接从数据库中获取联系人的详细信息
def get_contacts_by_uid(uid):
    try:
        r = users.find_one( {'uid':uid}, {'contacts':1} )
        uids = []
        if r and r.has_key('contacts'):
            uids =  r['contacts']
        contacts = []
        if uids!=[]:
            for item in uids:
                user = users.find_one({"uid":item['uid']},{"_id":0,"username":1,"email":1,'title':1,"oudn":1,"uid":1})
                if user!=None:
                    #生成标志位信息
                    flag=0
                    if item.has_key("flag"):
                        flag = item['flag']
                    #生成单位信息
                    oudn = user['oudn']
                    department = ''
                    fenjie = oudn.split(",");
                    for son in fenjie:
                        if son.find('ou')>=0:
                            department+=son[3:]+','
                        else:
                            continue
                    department = department[0:len(department)-1]

                    one = {'name':user['username'],'email':user['email'],'job':user['title'],'department':department,'pnumber':user['uid'],'flag':flag}
                    contacts.append(one)
                else:
                    continue
        logging.warn("uid:%s,contacts length:%d",uid,len(contacts))
        return contacts
    except:
        logging.exception('get_contacts_by_uid failed. uid:%s', uid)
    raise ecode.DB_OP

def get_contacs_count(uid):
    contacts_count = 0
    try:
        r = users.find_one( {'uid':uid}, {'contacts':1} )
        uids = []
        if r and r.has_key('contacts'):
            uids =  r['contacts']
        contacts_count = len(uids)
        return contacts_count
    except:
        logging.exception('get_contacs_count failed. uid:%s', uid)
    raise ecode.DB_OP

def del_contact(uid):
    try:
        u = users.update( {'uid':uid}, {'$set':{'contacts':[]}})
        return True
    except:
        logging.exception('del_contact failed. uid:%s', uid)
    raise ecode.DB_OP

def add_app( uid, app_name):
    try:
        u = users.update( {'uid':uid}, {'$addToSet':{'apps':app_name}})
        return True
    except:
        logging.exception('add_app failed. uid:%s', uid)
    raise ecode.DB_OP

def add_app_buffer( uid, app_ids):
    try:
        logging.error("add_app_buffer:%s",str(app_ids))
        for app_id in app_ids:
#             logging.error("add_app_buffer uid %s ,appid:%s",uid,app_id)
            users.update({'uid':uid}, {'$addToSet':{'apps_buffer':app_id}})
        return True
    except:
        logging.exception('add_app failed. uid:%s', uid)
    raise ecode.DB_OP

def get_app_buffer(uid):
    try:
        r = users.find_one( {'uid':uid}, {'apps_buffer':1} )
        if r and r.has_key('apps_buffer'):
            return r['apps_buffer']
        else:
            return None
    except:
        logging.exception('get_apps_buffer_by_uid failed. uid:%s', uid)
    raise ecode.DB_OP

def del_app_buffer( uid):
    try:
        u = users.update( {'uid':uid}, {'$set':{'apps_buffer':[]}})
        return True
    except:
        logging.exception('del_contact failed. uid:%s', uid)
    raise ecode.DB_OP



def get_apps( uid ):
    try:
        r = users.find_one( {'uid':uid}, {'apps':1} )
        if r and r.has_key('apps'):
            return r['apps']
    except:
        logging.exception('get_apps failed. uid:%s', uid)
        raise ecode.DB_OP
    return [] 


def add_web_app( uid, app_name):
    try:
        u = users.update( {'uid':uid}, {'$addToSet':{'web_apps':app_name}})
        return True
    except:
        logging.exception('add_app failed. uid:%s', uid)
    raise ecode.DB_OP


def get_web_apps( uid ):
    try:
        r = users.find_one( {'uid':uid}, {'web_apps':1} )
        if r and r.has_key('web_apps'):
            return r['web_apps']
    except:
        logging.exception('get_web_apps failed. uid:%s', uid)
        raise ecode.DB_OP
    return [] 

    #}}}

def get_app_info( uid ):
    try:
        r = users.find_one( {'uid':uid}, {'web_apps':1} )
        if r and r.has_key('web_apps'):
            return r['web_apps']
    except:
        logging.exception('get_web_apps failed. uid:%s', uid)
        raise ecode.DB_OP
    return [] 

    #}}}
#+++20150403 from zte, for login,for monitor?
def add_email( uid, email):
    if len(email) <= 0:
        raise ecode.DATA_LEN_ERROR
    try:
        u = users.update( {'uid':uid}, {'$addToSet':{'email':email}})
        return True
    except:
        logging.exception('add email to userdb failed. uid:%s', uid)
    raise ecode.DB_OP

#+++ 20150619 for pre strategy 20150710 改
def add_strategy(uid,strategy_id):  
    try:
#         r = users.find({"uid":uid,"strategys":{"$elemMatch":{"strategy_id":strategy_id}}})
#         if r:
#             logging.warn("math strategy true, add strategy failed.")
#             return True
        u = users.update({'uid':uid}, {'$push':{'strategys':{'strategy_id':strategy_id,'is_read':"false"}}})           
        return True
    except:
        logging.exception('add_strategy failed. uid:%s', uid)
    raise ecode.DB_OP

#+++ 20150619 for strategy id
def get_strategy_ids(uid):
    try:
        r = users.find_one({'uid':uid})
        if not r:
            return 'no'
        if r.has_key("strategys"):
            return r["strategys"]
        else:
            return []
    except:
        logging.exception('get_strategy_ids failed. uid:%s', uid)
    raise ecode.DB_OP

def get_remain_strategy(uid,del_list):
    try:
        r=users.find_one({'uid':uid},{'_id':0,'strategys':1})
        if r:
            users.update({'uid':uid},{'$unset':{'strategys':1}})
            ids=r['strategys']
            if len(del_list)!=0:
                rm_ids=[]
                for son_id in ids:
                    for del_id in del_list:
                        if son_id["strategy_id"]==del_id:
                            rm_ids.append(son_id)
                if len(rm_ids)!=0:
                    ids=list(set(ids).difference(rm_ids))
            return ids
    except:
        logging.exception('complete_strategy failed. uid:%s', uid)
        raise ecode.DB_OP
    return []

def strategy_is_read(uid,strategy_id):
    try:
        stra = users.find_one({'uid':uid},{'strategys':1})
        for s in stra['strategys']:
            if s['strategy_id']== strategy_id:
                s['is_read']="true"
                break
        u = users.update({'uid':uid},{'$set':{"strategys":stra['strategys']}}) 
        return True             
    except:
        logging.exception('strategy_is_read failed. uid:%s',uid)
    raise ecode.DB_OP

#+++ 20150707 for 未激活用户的删除策略
def remove_expire_strategy(uid,strategy_id):
    try:
        r = users.find_one({'uid':uid})
        if not r:
            return True
        if r.has_key("strategys"):
            u = users.update({'uid':uid}, {'$pull':{'strategys':{'strategy_id':strategy_id}}})
        return True 
    except:
        logging.exception('remove_expire_strategy failed. uid:%s', uid)
    raise ecode.DB_OP

#+++ 20150710 for 判读是否存在该策略id
def is_has_strategy_id(uid,strategy_id):
    try:
        stra = users.find_one({'uid':uid},{'_id':0,'strategys':1})
        if not stra:
            return False
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
        logging.exception('is_has_strategy_id failed. uid:%s', uid)
    raise ecode.DB_OP


#+++ 20150728 用户选中标志位置位
def user_checked(uid,operation,admin):
    try:
        # if users.find_one({'uid':uid}):
        if operation==1:
            u = users.update({'uid':uid}, {'$set':{admin+'_checked':operation}})
        else:
            u = users.update({'uid':uid}, {'$unset':{admin+'_checked':operation}})
        return True
    except Exception as e:
        logging.exception('user_checked failed. uid:%s', uid)
        raise ecode.DB_OP
    return False

def user_checked_uid_hid(key,operation,admin):
    try:
        # if users.find_one({'uid':uid}):
        if operation==1:
            u = users.update({'key':key}, {'$set':{admin+'_checked':operation}})
        else:
            u = users.update({'key':key}, {'$unset':{admin+'_checked':operation}})
        return True
    except Exception as e:
        logging.exception('user_checked failed. key:%s', key)
        raise ecode.DB_OP
    return False

#+++ 20150728 选择指定群组用户列表
def get_ou_users(oudn):
    ou_users = []
    try:
        regex = re.compile('.*'+oudn)
        r = users.find( {"oudn":regex}, {'_id':0,'uid':1})
        if r:
            for item in r:
                ou_users.append(item['uid'])
        return ou_users
    except:
        logging.exception('get_ou_users failed. oudn:%s',oudn)
        raise ecode.DB_OP

def set_ou_users_checked(oudn,operation,admin):
    time1 = time.time()
    print("进入set_ou_users_checked时间点"+str(time1))
    try:
        regex = re.compile('.*'+oudn)
        r = users.find( {"oudn":regex}, {'_id':0,'uid':1})
        if r:
            for item in r:
                if operation==1:
                    users.update({'uid':item['uid']}, {'$set':{admin+'_checked':operation}})
                else:
                    users.update({'uid':item['uid']}, {'$unset':{admin+'_checked':operation}})
            time2 = time.time()
            print("结束set_ou_users_checked时间点"+str(time2))
        return True
    except:
        logging.exception('set_pw failed. oudn:%s',oudn)
        raise ecode.DB_OP
    return False

#+++ 20150728 获取的被选中的用户数
def get_selected_count(admin):
    selected_count = 0
    try:
        r = users.find({admin+"_checked":1}).count()
        if r:
            selected_count = r
            return selected_count
        else:
            return 0
    except Exception as e:
        logging.exception('get_selected_count failed.')
        raise ecode.DB_OP

def get_selected_countqj(admin,xialakuang,guanjianzi):
    selected_count = 0
    try:
        r = users.find({admin+"_checked":1,xialakuang:{'$regex':guanjianzi}}).count()
        if r:
            selected_count = r
            return selected_count
    except Exception as e:
        logging.exception('get_selected_countqj failed.')
        raise ecode.DB_OP

#+++ 20150731 获取符合以前格式的选定用户
def get_selected_users(admin):
    selected_users = []
    try:
        r = users.find({admin+"_checked":1},{"_id":0}).sort("oudn")
        if r:
            for item in r:
                selected_users.append(item)
            return selected_users
    except Exception as e:
        logging.exception("get_selected_users failed!!")
        raise ecode.DB_OP

def get_selected_users_simple(admin):
    selected_users = []
    try:
        r = users.find({admin+"_checked":1},{"_id":0,"uid":1,"username":1,"oudn":1}).sort("oudn")
        if r:
            for item in r:
                selected_users.append(item)
            return selected_users
    except Exception as e:
        logging.exception("get_selected_users failed!!")
        raise ecode.DB_OP

#+++ 20150803 获取选定用户的uid
def get_selected_uids(admin):
    selected_users = []
    try:
        r = users.find({admin+"_checked":1},{"_id":0,"uid":1,'oudn':1}).sort("oudn")
        if r:
            for item in r:
                if item.has_key("uid"):
                    selected_users.append(item['uid'])
            return selected_users
    except Exception as e:
        logging.exception("get_selected_users failed!!")
        raise ecode.DB_OP

#+++ 20150728 20150831改，多字段排序
def get_selected_page_users(page,size,last_user,admin,sort_keys):
    page_users = []
    sort_tuple = []
    if len(sort_keys)==0:
        sort_tuple = [('create_time',pymongo.ASCENDING)]
    else:
        sort_tuple = generate_sort_tuple(sort_keys)
    if page=='next':
        r = users.find({admin+'_checked':1},{'_id':0,'key':1,'uid':1,'status':1,'username':1,'email':1,'title':1,
                                                                      'oudn':1,'devs':1}).sort(sort_tuple).limit(int(size))
    elif page=='last':
        r = users.find({admin+'_checked':1},{'_id':0,'key':1,'uid':1,'status':1,'username':1,'email':1,'title':1,
                                                                      'oudn':1,'devs':1}).sort(sort_tuple).limit(int(size))
    else:
        logging.warn('get_selected_page_users:返回page页的size条数据，skip待优化！')
        past_users=(int(page)-1)*int(size)
        r = users.find({admin+'_checked':1},{'_id':0,'key':1,'uid':1,'status':1,'username':1,'email':1,'title':1,
                                      'oudn':1,'devs':1}).sort(sort_tuple).skip(past_users).limit(int(size))
    if r:
        for item in r:
            page_users.append(item)
        return page_users

def get_selected_page_users_uid_hide(page,size,last_user,admin,sort_keys,rootdn):
    page_users = []
    sort_tuple = []
    if len(sort_keys)==0:
        sort_tuple = [('create_time',pymongo.ASCENDING)]
    else:
        sort_tuple = generate_sort_tuple(sort_keys)
    if page=='next':
        r = users.find({admin+'_checked':1},{'_id':0,'key':1,'uid':1,'status':1,'username':1,'email':1,'title':1,
                                                                      'oudn':1,'devs':1}).sort(sort_tuple).limit(int(size))
    elif page=='last':
        r = users.find({admin+'_checked':1},{'_id':0,'key':1,'uid':1,'status':1,'username':1,'email':1,'title':1,
                                                                      'oudn':1,'devs':1}).sort(sort_tuple).limit(int(size))
    else:
        logging.warn('get_selected_page_users:返回page页的size条数据，skip待优化！')
        past_users=(int(page)-1)*int(size)
        r = users.find({admin+'_checked':1},{'_id':0,'key':1,'uid':1,'status':1,'username':1,'email':1,'title':1,
                                      'oudn':1,'devs':1}).sort(sort_tuple).skip(past_users).limit(int(size))
    if r:
        for item in r:
            if rootdn in item["oudn"] :
                page_users.append(item)
            else :
                item["uid"] = "***********"
                page_users.append(item)
        return page_users

def generate_sort_tuple(sort_keys):
    if sort_keys == []:
        return []
    else:
        sort_str = []
        for item in sort_keys:
            name = item['name']
            order = item['order']
            orderstr = 0
            if name=="status":
                if(int(order)==1):
                    orderstr = pymongo.DESCENDING
                elif(int(order) ==-1):
                    orderstr = pymongo.ASCENDING
            else:
                if(int(order)==1):
                    orderstr = pymongo.ASCENDING
                elif(int(order) ==-1):
                    orderstr = pymongo.DESCENDING
            sort_str.append((str(name),orderstr))
        print("sort keys"+str(sort_str))
        return sort_str

# +++20150901 加入在user_db中加入活跃度的函数
def set_liveness(uid,liveness):
    try:
        if users.find({"uid":uid}):
            users.update({"uid":uid},{"$set":{"liveness":liveness}})
            logging.error("user %s set liveness:%s succeed",uid,str(liveness))
            return True
    except Exception as e:
        logging.error("set liveness failed, uid:%s",uid)
    return False
# +++20150901 设置user_db中的last_update字段，共排序使用
def set_last_update(uid,last_update):
    try:
        if users.find({"uid":uid}):
            users.update({"uid":uid},{"$set":{"last_update":last_update}})
            return True
        else:
            logging.error("uid:%s not found",uid)
    except Exception as e:
        logging.error("user_db.py set_last_update failed,uid:%s",uid)
    return False

# +++20150902 配合前台修改用户信息
def update_userinfo(key,uid,username,oudn,email,title):
    try:
        param = {}
        fiuid = uid.replace(" ","")
        if(fiuid!=""):
            param['uid'] = fiuid
        fiusername = username.replace(" ","")
        if(fiusername!=""):
            param['username'] = fiusername
        fioudn = oudn.replace(" ","")
        if(fioudn!=""):
            param['oudn'] = fioudn

        # +++20151023 修改不能由空修改为非空的设定
        # fiemail = email.replace(" ","")
        # if(fiemail!=""):
        param['email'] = email

        # +++20151023 修改不能由空修改为非空的设定
        # fititle = title.replace(" ","")
        # if(fititle!=""):
        param['title'] = title
        r = users.find({"key":key})
        if r:
            users.update({"key":key},{"$set":param})
            return True
    except Exception as e:
        logging.error("update user info error,uid:%s",uid)
    return False


def change_bind_dev(key,devs):
    """
    +++20160224 修改用户绑定的设备
    :param key: 用户主键
    :param dev_id: 用户修改绑定设备
    :return: 改绑定操作结果
    """
    if len(key)<=0:
        raise ecode.DATA_LEN_ERROR
    try:
        users.update({"key":key},{"$set":{"devs":devs}})
    except Exception as e:
        logging.error("change bind dev failed, key:%s",key)


# +++ 20151008 修改用户设备的状态
def change_user_status(uid,status):
    try:
        if users.find({"uid":uid}):
            users.update({"uid":uid},{"$set":{"status":status}})
            return True
        else:
            logging.error("uid:%s not found",uid)
    except Exception as e:
        logging.error("user_db.py change_user_status failed,uid:%s",uid)
    return False


# +++20151103 根据uid获取用户信息
def get_user_info_by_uid(uid):
    try:
        user = users.find_one({"uid":uid},{"_id":0,"key":1,"uid":1,"username":1,
                                           "oudn":1,"title":1,"email":1,"devs":1,"online":1,"outline":1})
        return user
    except Exception as e:
        logging.error("user_db.py get_user_info_by_uid failed,uid:%s",uid)
    return None


# +++20160223 根据key获取用户信息
def get_user_info_by_key(key):
    try:
        user = users.find_one({"key":key},{"_id":0,"key":1,"uid":1,"username":1,"oudn":1,"devs":1})
        return user
    except Exception as e:
        logging.error("user_db.py get_user_info_by_key failed,key:%s",key)
    return None

def get_user_key_by_uid(uid):
    try:
        user = users.find_one({"uid":uid},{"_id":0,"key":1,"uid":1,"username":1,"oudn":1,"devs":1})
        return user['key']
    except Exception as e:
        logging.error("user_db.py get_user_info_by_key failed,uid:%s",uid)
    return None

def get_all_users_info(admin,xialakuang,guanjianzi,page,size,last_user,sort_keys):
    try:
        user = []
        sort_tuple = []
        if len(sort_keys)==0:
            sort_tuple = [('create_time',pymongo.ASCENDING)]
        else:
            sort_tuple = generate_sort_tuple(sort_keys)
        if page=='next':
            user_cur = users.find({admin+'_checked':1,xialakuang:{'$regex':guanjianzi}},{'_id':0,'key':1,'uid':1,'status':1,'username':1,'email':1,'title':1,
                                                                          'oudn':1,'devs':1}).sort(sort_tuple).limit(int(size))
        elif page=='last':
            user_cur = users.find({admin+'_checked':1,xialakuang:{'$regex':guanjianzi}},{'_id':0,'key':1,'uid':1,'status':1,'username':1,'email':1,'title':1,
                                                                          'oudn':1,'devs':1}).sort(sort_tuple).limit(int(size))
        else:
            logging.warn('get_selected_page_users:返回page页的size条数据，skip待优化！')
            past_users=(int(page)-1)*int(size)
            user_cur = users.find({admin+'_checked':1,xialakuang:{'$regex':guanjianzi}},{'_id':0,'key':1,'uid':1,'status':1,'username':1,'email':1,'title':1,
                                          'oudn':1,'devs':1}).sort(sort_tuple).skip(past_users).limit(int(size))
        for item in user_cur:
            user.append(item)
        return user
    except Exception as e:
        logging.error("user_db.py get_all_users_info failed,uid:%s",admin,xialakuang,guanjianzi,page,size,last_user,sort_keys)
    return None

def get_auto_search_all_users():
    search_users = []
    r = users.find({},{"_id":0,"username":1,"oudn":1}).sort("oudn")
    if r:
        for user_item in r:
            if user_item["username"] not in search_users:
                search_users.append(user_item["username"])
        return search_users

def get_auto_search_adm_users(oudn):
    search_users = []
    r = users.find({},{"_id":0,"username":1,"oudn":1}).sort("oudn")
    if r:
        for user_item in r:
            if oudn in user_item["oudn"]:
                if user_item["username"] not in search_users:
                    search_users.append(user_item["username"])
        return search_users

def get_auto_search_con_users(contact_ous):
    search_users = []
    r = users.find({},{"_id":0,"username":1,"oudn":1}).sort("oudn")
    if r:
        for user_item in r:
            for ou_item in contact_ous:
                if ou_item in user_item["oudn"]:
                    if user_item["username"] not in search_users:
                        search_users.append(user_item["username"])
        return search_users

def get_auto_selected_users(admin,username):
    r = users.find({"username":username},{"_id":0,"uid":1,"key":1,"oudn":1})
    u = users.find({admin+'_contact_checked':1},{"_id":0,"uid":1,admin+'_contact_checked':1})
    for item in u:
        users.update({"uid":item["uid"]},{'$unset':{admin+'_contact_checked':0}})
    return r

def get_auto_selected_adm_users(admin,username):
    r = users.find({"username":username},{"_id":0,"uid":1,"key":1,"oudn":1})
    u = users.find({admin+'_checked':1},{"_id":0,"uid":1,admin+'_checked':1})
    for item in u:
        users.update({"uid":item["uid"]},{'$unset':{admin+'_checked':0}})
        #如果不对做这个处理，每次新搜索的时候，上一次搜索的结果仍旧留在右侧栏

    return r
