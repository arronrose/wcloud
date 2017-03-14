__author__ = 'arron_rose_gjw'
# -*- coding: utf8 -*-
import pymongo
import mongoUtil
if __name__=="__main__":
    # mongo_host = "repset/192.168.1.15/192.168.1.16"
    # mongo_host = "192.168.1.200"
    # mongo_port = 27017
    # client = MongoClient(mongo_host,mongo_port)
    client = mongoUtil.getClient()
    db = client["wcloud_o"]
    ads = db["admin"]
    # ads.update({'uid':"admin"}, {'$set':{'logo':"admin"}})
    # ads.insert({'uid':"admin",'pw':"184070c4026106318b0c920d873d0b6a6e428815",'logo':"admin"})
    # ads.insert({'uid':"master",'pw':"184070c4026106318b0c920d873d0b6a6e428815",'logo':"master"})
    # ads.insert({'uid':"auditor",'pw':"184070c4026106318b0c920d873d0b6a6e428815",'logo':"auditor"})
    # ads.insert({'uid':"SA",'pw':"184070c4026106318b0c920d873d0b6a6e428815",'logo':"sa"})
    ads.update({'uid':"SA"},{'$set':{'logo':"sa"}})
    print "添加初始四员成功！"