# -*- coding: utf8 -*-
__author__ = 'GCY'

from pymongo import MongoClient
import re


# 使用方法
"""
脚本已经拷贝到/home/wcloud/opt/org/wcloud_ws/lib/python2.7/site-packages/wcloud_ws目录下，
1）在/home/wcloud/opt/org/wcloud_ws/bin 目录下执行. activate激活虚拟环境
2）在虚拟环境下执行python get_online_data.py脚本即可输出结果
"""
# 返回格式


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

def data_statistics():
    # 获取数据库连接
    # mongo_host = "repset/192.168.1.15/192.168.1.16"
    mongo_host = "192.168.1.15"
    # mongo_host = "127.0.0.1"
    mongo_port = 27017
    client = MongoClient(mongo_host,mongo_port)
    db = client["wcloud_o"]
    online_db = db["online_statistics"]
    # 将测试群组中的用户剔除
    result = online_db.find()

    for item in result:
        print 'time:'+item['time']+',count:'+str(len(item['online_users']))


if __name__=="__main__":
    data_statistics()




