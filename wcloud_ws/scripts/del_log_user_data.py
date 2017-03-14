__author__ = 'GCY'
# -*- coding: utf8 -*-

from pymongo import MongoClient
import re

mongo_host = "192.168.1.15"
mongo_port = 27017
client = MongoClient(mongo_host,mongo_port)
db = client["wcloud_o"]
log_web = db["log_web"]
dev = db['dev']

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


# 根据群组添加用户活跃值
def del_log_user_data():
    result = log_web.find({"time":{"$gt":"2016-01-20"},"action":"send contacts"})
    count = 0
    if result:
        for item in result:
            users = item['users']
            if(users[0].has_key("pw")):
                new_user_list = []
                for user in users:
                    new_user = {"uid":user['uid'],"username":user['username'],"oudn":user["oudn"]}
                    new_user_list.append(new_user)
                log_web.update({"time":item['time'],"action":item['action']},{"$set":{"users":new_user_list}})

                count+=1
    print "总共有联系人："+str(count)


if __name__=="__main__":
    # mongo_host = "repset/192.168.1.15/192.168.1.16"
    # 注意输入oudn的时候前面加u，将字符串变为unicode编码，否则python2.7默认是ASCII编码，中文会乱码
    # add_ou_liveness(u'ou=广州市,dc=test,dc=com',2)

    del_log_user_data()
