__author__ = 'ZXC'
# -*- coding: utf8 -*-

from pymongo import MongoClient
import redis
import pymongo
import time
import datetime

# mongo_host = "repset/192.168.1.15/192.168.1.16"
mongo_host = "192.168.1.15"
mongo_port = 27017
client = MongoClient(mongo_host,mongo_port)
db = client["wcloud_o"]
users = db["user"]
devs = db["dev"]

redis_conn = redis.Redis(host="192.168.1.15",port=6379, db=2)

def getMongoClient(host,port):
    replset=host.split("/")
    reptype=replset[0]
    master=replset[1]
    slave=replset[2]
    mport=str(port)
    mongoUrl="mongodb://"+master+":"+mport+","+slave+":"+mport+"/?replicaSet="+reptype
    client = MongoClient(mongoUrl,w=0)
    # client = MongoClient(host, port,w=0)
    return client

def get_user_list(users):
    users.find( {}, {'_id':0,'uid':1,'devs':1})

def is_has_user( uid ):
    try:
        r = users.find_one({'uid':uid}, {'uid':1})
        if r:
            return True
    except:
        print('is_has_user failed. uid:%s', uid)
    return False

def add_dev( dev_id, user):
    if len(dev_id) <= 0:
        raise
    try:
        devs.create_index([('dev_id',pymongo.ASCENDING)], unique=True)
        if devs.find_one({"dev_id":dev_id})==None:
            if devs.insert({'dev_id':dev_id, 'loc':{'lon':'0','lat':'0'}
                ,'cmd_sn':0, 'cmds':[],'strategy_sn':0,'strategys':[],'current':{},'cur_user':user}):
                return True
    except:
        print('add new dev failed. dev_id:%s', dev_id)
    return False

def get_on_out_line(time_diff):
    #     传入的是活跃度的分母
    online = int(float(6.4/38)*time_diff)
    out_line = time_diff-online
    return dict(online=online,outline=out_line)


def get_array():
    array = []
    file = open("ous.txt")
    ous = file.readline()
    while ous:
        array.append(ous[0:-2].replace('"',""))
        ous = file.readline()
    return array


def analysis(target_oudn,time_diff):
    result = redis_conn.keys()
    count = 0

    # 获取在线离线时间
    online_tuple = get_on_out_line(time_diff)
    online = online_tuple['online']
    outline = online_tuple['outline']

    for item in result:
        if item.find(":")>0:
            user_data = redis_conn.get(item)
            uid = user_data.split(":")[0]
            dev_id = user_data.split(":")[1]
            # 获取uid和dev_id成功，分别添加设备和生成设备信息
            if(len(uid)==11):
                if(is_has_user(uid)==True):
                    user = users.find_one({"uid":uid})
                    binded_dev = user['devs']
                    if(user['oudn'].find(target_oudn)>=0):

                        if(binded_dev==[] and dev_id!=""):
                            print user['uid']+":"+user['username']+":"+user['oudn']+\
                              ":redis_dev:"+dev_id+":bind_dev"+str(binded_dev)
                            count += 1
                            # 恢复数据
                            users.update({"uid":uid},{"$addToSet":{"devs":dev_id}})
                            add_dev(dev_id,uid)
                            print "完成修复"

    print "用户%s人"%(str(count))

if __name__=="__main__":
    # recover_ou = "ou=省档案局,dc=test,dc=com"
    ou_array = get_array()
    for item in ou_array:
        print "群组为:"+str(item[0:-1])
        analysis(unicode(item[0:-1].decode("utf-8")),1)



