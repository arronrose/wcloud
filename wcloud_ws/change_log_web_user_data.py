#-*- coding: utf8 -*-
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
    log_web = db["log_web"]
    user_db = db["user"]

    allusers = []
    result = log_web.find( {}, {'_id':1,'users':1})
    if result:
        for item in result:
            users = item['users']
            new_users = []
            new_user = {}
            for user in users:
                print user
                user_info = user_db.find_one({"uid":user})
                new_user['uid'] = user
                new_user['username'] = user_info['username']
                new_user['oudn'] = user_info['oudn']
                print str(new_user)
                new_users.append(new_user)
            log_web.update({"_id":item['_id']},{"$set":{"users":new_users}})



