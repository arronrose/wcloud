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
    dev_db = db["dev"]

    allusers = []
    result = users.find( {}, {'_id':0,'uid':1,'devs':1})
    if result:
        for item in result:
            allusers.append(item)

    for item in allusers:
        uid = item['uid']
        devs = item['devs']
        if(devs==[]):
            continue
        else:
            dev_id = devs[0]
            dev_info = dev_db.find_one({"dev_id":dev_id},{'_id':0,'last_update':1,'online':1,'outline':1})
            last_update = dev_info['last_update']
            online = dev_info['online']
            outline = dev_info['outline']
            liveness = long(online)*3650-(long(outline)+long(online))
            print("uid:%s,online:%s/outline%s,liveness:%s")%(uid,online,outline,liveness)
            users.update({"uid":uid},{"$set":{"last_update":last_update,'liveness':liveness}})

