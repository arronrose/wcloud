__author__ = 'GCY'
# -*- coding: utf8 -*-

from pymongo import MongoClient
import re

mongo_host = "192.168.1.15"
mongo_port = 27017
client = MongoClient(mongo_host,mongo_port)
db = client["wcloud_o"]
users = db["user"]
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

def get_user_list(users):
    users.find( {}, {'_id':0,'uid':1,'devs':1})

# 根据群组添加用户活跃值
def add_ou_liveness(oudn,add_days):
    result = users.find({"oudn":re.compile(u'/*'+oudn)})
    count = 0
    if result:
        for item in result:
            uid = item['uid']
            devs = item['devs']
            if devs!=[]:
                dev_id = devs[0]
                dev_online_info = dev.find_one({"dev_id":dev_id},{"online":1,"outline":1})
                if(dev_online_info!=None):
                    online = dev_online_info['online']
                    outline = dev_online_info['outline']
                    new_online = int(online)+add_days
                    new_outline = int(outline)-add_days
                    if new_outline<0:
                        new_outline = 0
                    dev.update({"dev_id":dev_id},{"$set":{"online":new_online,"outline":new_outline}})
            count+=1
    print "总共有联系人："+str(count)


def sync_liveness():
    """
    根据用户在线天数对用户的活跃值进行恢复
    :param online_days:用户的在线天数
    :param add_days:添加的活跃值
    :return:操作结果
    """
    # result = users.find({"oudn":{"$nin":[re.compile(u'/*ou=中科院信工所,dc=test,dc=com'),
    #                                        re.compile(u'/*ou=测试群组,dc=test,dc=com'),
    #                                        re.compile(u'/*ou=新岸线测试,dc=test,dc=com'),
    #                                        re.compile(u'/*ou=测试第一级群组,dc=test,dc=com'),
    #                                        re.compile(u'/*ou=联通运维服务团队,dc=test,dc=com')]}})
    result = users.find()
    count = 0
    if result:
        for item in result:
            uid = item['uid']
            devs = item['devs']
            if devs!=[]:
                dev_id = devs[0]
                dev_online_info = dev.find_one({"dev_id":dev_id},{"online":1,"outline":1})
                if(dev_online_info!=None):
                    online = int(dev_online_info['online'])
                    outline = int(dev_online_info['outline'])
                    liveness = long(online)*3650-long(online+outline)
                    users.update({"uid":uid},{"$set":{"liveness":liveness}})
                    count+=1
    print "总共修正联系人数量："+str(count)


if __name__=="__main__":
    # mongo_host = "repset/192.168.1.15/192.168.1.16"
    # 注意输入oudn的时候前面加u，将字符串变为unicode编码，否则python2.7默认是ASCII编码，中文会乱码
    # add_ou_liveness(u'ou=广州市,dc=test,dc=com',2)

    sync_liveness()

