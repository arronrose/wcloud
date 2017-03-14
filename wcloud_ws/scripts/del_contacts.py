__author__ = 'ZXC'
# -*- coding: utf8 -*-

from pymongo import MongoClient
import re

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
    # mongo_host = "repset/192.168.1.15/192.168.1.16"
    mongo_host = "192.168.1.15"
    mongo_port = 27017
    client = MongoClient(mongo_host,mongo_port)
    db = client["wcloud_o"]
    users = db["user"]

    result = users.find({"oudn":{"$in":[re.compile(u'/*ou=四室,ou=中科院信工所,dc=test,dc=com')]}})
    count = 0
    if result:
        for item in result:
            users.update({"uid":item['uid']},{"$set":{"contacts":[]}})
            count+=1
    print "总共删除联系人"+str(count)


