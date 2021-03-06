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

def add_dev( dev_id, user,online,outline ):
    if len(dev_id) <= 0:
        raise
    try:
        devs.create_index([('dev_id',pymongo.ASCENDING)], unique=True)
        t = str(int(time.time()))
        tt = time.localtime()
        ttt = datetime.datetime(tt[0],tt[1],tt[2])
        tttt = time.mktime(ttt.timetuple())
        if devs.insert({'dev_id':dev_id, 'loc':{'lon':'0','lat':'0'}
            ,'cmd_sn':0, 'cmds':[],'strategy_sn':0,'strategys':[],'current':{},
            'last_update':t,'cur_user':user,'online':online,'outline':outline,'onlinetime':tttt}):
            return True
    except:
        print('add new dev failed. dev_id:%s', dev_id)
    raise

def get_on_out_line(time_diff):
    #     传入的是活跃度的分母
    online = int(float(6.4/38)*time_diff)
    out_line = time_diff-online
    return dict(online=online,outline=out_line)

def analysis(recover_ou,time_diff):

    result = redis_conn.keys()
    exist = 0
    not_exist = 0

    # 获取在线离线时间
    online_tuple = get_on_out_line(time_diff)
    online = online_tuple['online']
    outline = online_tuple['outline']

    changed_dev_ids = []
    for item in result:
        print(item)
        if item.find(":")>0:
            user_data = redis_conn.get(item)
            uid = user_data.split(":")[0]
            dev_id = user_data.split(":")[1]
            # 获取uid和dev_id成功，分别添加设备和生成设备信息
            if(len(uid)==11):
                if(is_has_user(uid)==True):
                    oudn = users.find_one({"uid":uid})["oudn"]
                    print oudn
                    # 如果现在用户未绑定设备
                    # if binded_dev==[]:
                    #     user = users.find_one({"uid":uid})
                    #     user_name = user['username']
                    #     user_oudn = user['oudn']
                    #     if(user_oudn.encode("utf-8").find(recover_ou)>=0):
                    #         #recover_ou.append(user_oudn)
                    #         print "号码是:"+uid+",设备号:"+dev_id
                    #         users.update({"uid":uid},{"$addToSet":{"devs":dev_id}})
                    #         session_dev = devs.find_one({"dev_id":dev_id},{"cur_user":1})
                    #         if dev_id!="867425020040680":
                    #             add_dev(dev_id,uid,online,outline)
                    #         exist+=1
                    # # 如果现在用户已绑定设备
                    # else:
                    #     binded_dev_id = binded_dev[0]
                    #     if dev_id!=binded_dev_id:
                    #         changed_dev_ids.append(dict(uid=uid,session_dev_id=dev_id,db_dev_id=binded_dev_id))
                    # # users.update({"uid":uid},{"$push":{}})
                else:

                    not_exist+=1
            # print "uid:"+uid+","+str(is_has_user(uid))
            # print ("uid:%s,dev_id:%s"%(uid,dev_id))
    print "恢复用户%s人"%(str(exist))
    # print "设备发生改变的用户数量是：%s,数组是：%s"%(str(len(changed_dev_ids)),str(changed_dev_ids))
    # print str(len(recover_ou))

if __name__=="__main__":
    recover_ou = "ou=省人大常委会办公厅,dc=test,dc=com"
    # recover_ou = "ou=省档案局,dc=test,dc=com"
    time_diff = 7
    print "恢复的群组为："+recover_ou
    analysis(recover_ou,time_diff)



