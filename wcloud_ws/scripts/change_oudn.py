# -*- coding: utf8 -*-
__author__ = 'GCY'

from pymongo import MongoClient
import re

def change_oudn():
    # 获取数据库连接
    # mongo_host = "repset/192.168.1.15/192.168.1.16"
    mongo_host = "192.168.1.15"
    # mongo_host = "127.0.0.1"
    mongo_port = 27017
    client = MongoClient(mongo_host,mongo_port)
    db = client["wcloud_o"]
    user_db = db["user"]
    dev_db = db['dev']
    # 将测试群组中的用户剔除
    # result = user_db.find({"oudn":{"$in":[re.compile(u'/*ou=中科院信工所,dc=test,dc=co'),
    #                                        re.compile(u'/*ou=测试群组,dc=test,dc=co'),
    #                                        re.compile(u'/*ou=新岸线测试,dc=test,dc=co'),
    #                                        re.compile(u'/*ou=测试第一级群组,dc=test,dc=co'),
    #                                        re.compile(u'/*ou=联通运维服务团队,dc=test,dc=co')]}})
    # result = user_db.find({"oudn":'ou=新岸线测试,dc=test,dc=com'})
    result = user_db.find({"oudn":{"$in":[re.compile(u'/*ou=元心科技测试群,ou=中科院信工所,dc=test,dc=co')]}})

    count = 0
    for item in result:
        count+=1
        # print(item['uid'])
        oudn = item['oudn']
        user_db.update({"_id":item['_id']},{"$set":{"oudn":"ou=元心科技测试群,ou=中科院信工所,dc=test,dc=com"}})
        print count

if __name__ == '__main__':
    change_oudn()