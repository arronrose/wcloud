# -*- coding: utf8 -*-
__author__ = 'ZXC'

from pymongo import MongoClient

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



if __name__=="__main__":
    mongo_host = "repset/192.168.1.15/192.168.1.16"
    # mongo_host = "127.0.0.1"
    mongo_port = 27017
    client = getMongoClient(mongo_host,mongo_port)
    db = client["wcloud_o"]
    users = db["user"]

    allusers = []
    result = users.find( {"guochenyang_checked":1}, {'_id':0,'uid':1,'oudn':1,"username":1,'contacts':1})
    if result:
        for item in result:
            allusers.append(item)
    count = 0
    for item in allusers:
        uid = item['uid']
        users.update({"uid":uid},{"$set":{"contacts":[]}})
        count+=1

    print("用户总数"+str(count))

