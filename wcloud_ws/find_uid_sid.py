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

def analysis():

    result = redis_conn.keys()
    for item in result:
        if item.find(":")>0:
            user_data = redis_conn.get(item)
            uid = user_data.split(":")[0]
            if uid=="18588837291":
                print user_data


if __name__=="__main__":
    analysis()



