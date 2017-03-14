# -*- coding: utf8 -*-
__author__ = 'GCY'

import random
from pymongo import MongoClient


if __name__ == '__main__':
    mongo_host = "192.168.1.15"
    mongo_port = 27017
    client = MongoClient(mongo_host,mongo_port)
    db = client["wcloud_o"]
    users = db["user"]
    devs = db['dev']

    user_list = users.find()
    for item in user_list:
        if(item['devs']!=[] and item.has_key('online')):
            user_online = int(item['online'])
            user_outline = int(item['outline'])
            dev_id = item['devs'][0]
            dev = devs.find_one({"dev_id":dev_id})
            if(dev and dev.has_key("online")):
                if(user_online==1 and user_outline==0):
                    online = int(dev['online'])
                    outline = int(dev['outline'])
                    users.update({"uid":item['uid']},{"$set":{"online":str(online+10),
                                                          "outline":str(outline+10)}})
                    print "完成用户"+str(item['uid'])+"的修改"
        else:
            print "用户"+str(item['uid'])+"未激活"

