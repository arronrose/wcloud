# -*- coding: utf8 -*-
#!/usr/bin/env python

import pymongo
import logging
import ecode
import config
import mongoUtil

client = mongoUtil.getClient()

db = client[config.get('mongo_db')]
recmd = db[config.get('mongo_recmd_table')]


def init_db():
    recmd.drop()
    recmd.create_index([('uid',pymongo.ASCENDING)], unique=True)

#add new re cmd record
def create(uid,devs,cmd,type):
    try:
        recmd.create_index([('uid',pymongo.ASCENDING)], unique=True)
        if recmd.insert({'uid':uid+cmd,'devs':devs,'type':type}):
            #remove "设备未激活"
            recmd.remove({"devs":[]}) #ensure adm is removed
            return True
    except pymongo.errors.DuplicateKeyError:
        raise ecode.USER_EXIST
    except:
        logging.error('create recmd failed. uid:%s', uid)
    raise ecode.DB_OP

#get_cmd and remove the dev_id from re_cmd list
def get_cmd_ok(dev_id):
    try:
        r = recmd.find({'type':'cmds'},{"_id":0})
        dev = dev_id.split(":")   #str to list
        for doc in r:
            doc["devs"]=list(set(doc["devs"]).difference(set(dev)))
            uid=doc["uid"]
            #+++ 改 20150709
            if len(doc['devs'])!=0:
                recmd.update({'uid':uid}, {'$set':{'devs':doc["devs"]}})
            else:
                recmd.remove({'uid':uid})
        return True
    except:
        logging.error('get_cmd_ok failed.')
    raise ecode.DB_OP

#get devs of admin
def get_devs(uid):
    try:
        r = recmd.find_one( {'uid':uid}, {'devs':1} )
        if r:
            return r['devs']
    except:
        logging.error('get_devs failed. uid:%s', uid)
        raise ecode.DB_OP
    return [] 

#complete reply
def complete_re_cmd(uid):
    try:
        r=recmd.find_one({'uid':uid})
        if not r:
            return True
        # +++20150910 取消执行指令时非安全模式不再读取反馈
        recmd.remove({'uid':uid})
        return True
    except:
        logging.error('del_user failed. uid:%s', uid)
    return False

#get_stra and remove the user from list
def get_stra_ok(user,type):
    try:
        r = recmd.find({'type':type},{"_id":0})
        for doc in r:
            uid=doc["uid"]
            users=doc["devs"]
            rm_son_list=[]
            for son in users:
                sonusers=son["users"]
                remove_list=[]
                for gson in sonusers:
                    if gson["uid"]==user:
                        remove_list.append(gson)
                for rem in remove_list:
                    son["users"].remove(rem)
                if len(son["users"])<=0:
                    rm_son_list.append(son)
            if len(rm_son_list)>0:
                for s in rm_son_list:
                    users.remove(s)
            logging.error("user:%s complete : %s operation",user,type)
            recmd.update({'uid':uid}, {'$set':{'devs':users}})
        return True
    except:
        logging.error('get_stra_ok failed.')
        raise ecode.DB_OP

#+++for modify complete
def modify_stra_ok(user,strategy_id,type):
    try:
        result = recmd.find_one({'type':type},{"_id":0})
        if not result:
            return
        else:
            result_stra_id = result['uid'].split(':')[1]
            if(strategy_id==result_stra_id):
                uid = result['uid']
                users = result['devs']
                for sonuser in users:
                    if sonuser['uid']==user:
                        users.remove(sonuser)
                logging.error("user:%s complete : %s operation",user,uid)
                recmd.update({'uid':uid}, {'$set':{'devs':users}})
    except:
        logging.error("modify_stra_ok failed.")
        raise ecode.DB_OP

# +++20150922 for modify new strategy ok
# user:完成操作的用户，amdin:完成此操作的管理员,info:此次信息的存储info
def modify_sms_stra_ok(user,admin,info):
    try:
        re_cmd_id = admin+info
        record = recmd.find_one({"uid":re_cmd_id})
        if record:
            devs = record['devs']
            for dev in devs:
                if dev['uid']==user:
                    devs.remove(user)
                    logging.error("user:%s complete : %s operation",user,info)
            if devs==[]:
                recmd.remove({"uid":re_cmd_id})
    except Exception as e:
        logging.error("modify_sms_stra_ok failed.")
        raise ecode.DB_OP

#+++ 20150714 for modify complete
def mod_stra_ok(user,type,info):
    try:
        result = recmd.find({'type':type},{"_id":0})
        if not result:
            return
        else:
            for re in result:
                re_stra_head=re['uid'].split(':')[0]
                mod_info=re_stra_head.split('_')[1]
                if mod_info!=info:
                    continue
                uid = re['uid']
                users = re['devs']
                for sonuser in users:
                    if sonuser['uid']==user:
                        users.remove(sonuser)
                logging.error("user:%s complete : %s operation",user,uid)
                # +++ 20150922 如果该组没有用户了，需要删除整个任务
                if users==[]:
                    recmd.remove({"uid":uid})
                else:
                    recmd.update({'uid':uid}, {'$set':{'devs':users}})
    except:
        logging.error("mod_stra_ok failed.")
        raise ecode.DB_OP