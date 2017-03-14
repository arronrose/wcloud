# -*- coding: utf8 -*-
__author__ = 'GCY'

from pymongo import MongoClient
import re


# 使用方法
"""
脚本已经拷贝到/home/wcloud/opt/org/wcloud_ws/lib/python2.7/site-packages/wcloud_ws目录下，
1）在/home/wcloud/opt/org/wcloud_ws/bin 目录下执行. activate激活虚拟环境
2）在虚拟环境下执行python statistics.py脚本即可输出结果
"""
# 返回格式
""" {
    active_count:激活设备数
    sum_online_days：总活跃（上线）天数
    sum_use_days:总使用天数
    average_online_days：平均上线天数
    average_use_days：平均使用天数
 }"""


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
    user_db = db["user"]
    dev_db = db['dev']
    # 将测试群组中的用户剔除
    result = user_db.find({"oudn":{"$nin":[re.compile(u'/*ou=中科院信工所,dc=test,dc=com'),
                                           re.compile(u'/*ou=测试群组,dc=test,dc=com'),
                                           re.compile(u'/*ou=新岸线测试,dc=test,dc=com'),
                                           re.compile(u'/*ou=测试第一级群组,dc=test,dc=com'),
                                           re.compile(u'/*ou=联通运维服务团队,dc=test,dc=com')]}})
    active_count = 0
    sum_online_days = 0
    sum_out_line_days = 0
    err_count = 0
    for item in result:
        if item['devs']!=[]:
            active_count+=1
            dev_id = item['devs'][0]
            dev_onlinestate = dev_db.find_one({"dev_id":dev_id},{"online":1,"outline":1})
            if dev_onlinestate!="" and dev_onlinestate!=None:
                sum_online_days+=int(dev_onlinestate['online'])
                sum_out_line_days+=int(dev_onlinestate['outline'])
            else:
                err_count+=1
                print str(item['uid'])+":"+str(item['uid'])+":"+dev_id
        else:
            continue
    average_online_days = str(float(sum_online_days)/active_count)
    average_use_days = str(float(sum_out_line_days+sum_out_line_days)/active_count)
    print "激活设备数量:"+str(active_count)
    print "err设备数量:"+str(err_count)
    print "总活跃天数:"+str(sum_online_days)
    print "平均活跃天数:"+str(float(sum_online_days)/active_count)
    print "总使用天数:"+str(sum_out_line_days+sum_out_line_days)
    print "平均使用天数:"+str(float(sum_out_line_days+sum_out_line_days)/active_count)

    return dict(active_count=active_count,sum_online_days=sum_online_days,
                sum_use_days=sum_out_line_days+sum_out_line_days,
                average_online_days=average_online_days,
                average_use_days=average_use_days)


if __name__=="__main__":
    data_statistics()




