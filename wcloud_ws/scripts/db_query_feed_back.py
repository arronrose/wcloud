# -*- coding: utf8 -*-
__author__ = 'GCY'

from pymongo import MongoClient

mongo_host = "192.168.1.15"
mongo_port = 27017
client = MongoClient(mongo_host,mongo_port)
db = client["wcloud_o"]
users = db["user"]

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


if __name__ == '__main__':
    uid = users.find_one({"uid":"13261539852"})
    key = users.find_one({"key":"12345678jjjjjjjj"})

    print("uid:"+str(uid))
    print("key:"+str(key))
