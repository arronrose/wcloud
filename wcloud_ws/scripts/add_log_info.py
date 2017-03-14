# -*- coding: utf8 -*-
__author__ = 'GCY'

from pymongo import MongoClient
import re
import json

def add_log( uid, dev_id, t, app, action, info):
    # 获取数据库连接
    # mongo_host = "repset/192.168.1.15/192.168.1.16"
    mongo_host = "192.168.1.15"
    # mongo_host = "127.0.0.1"
    mongo_port = 27017
    client = MongoClient(mongo_host,mongo_port)
    db = client["wcloud_o"]
    table = db['log']

    try:
        if table.insert({'uid':uid, 'dev_id':dev_id, 't':t, 'app':app
            ,'act':action, 'info':info}):
            return True
    except:
        print('add log:%s %s'%(uid, dev_id))


if __name__ == '__main__':

    add_log("13312175392","860482031439235","1478654303306","System","Start","SettingActivity")
    add_log("13312175392","860482031439235","1478655345306","Secphone","Login the app","SettingActivity")

    add_log("13312175392","862521033324560","1478656310306","System","Shutdown","SettingActivity")
    add_log("13312175392","862521033324560","1478657310306","System","Start","SettingActivity")

    # 应用安装
    add_log("13312175392","862521033324560","1478658320306","Secphone","PACKAGE_ADDED","com.android.settings install")
    add_log("13312175392","862521033324560","1478659320306","微信","PACKAGE_ADDED","com.tencent.mm install")
    add_log("13312175392","862521033324560","1478659430306","百度地图","PACKAGE_ADDED","com.baidu.BaiduMap install")
    add_log("13312175392","862521033324560","1478659530306","UC浏览器","PACKAGE_ADDED","com.UCMobile install")
    add_log("13312175392","862521033324560","1478659630306","今日头条","PACKAGE_ADDED","com.ss.android.article.news install")
    add_log("13312175392","862521033324560","1478659730306","支付宝","PACKAGE_ADDED","com.eg.android.AlipayGphone install")

    # 登录退出


    # 接打电话
    add_log("13312175392","862521033324560","1478660440306","Telephone","From 13261539852","Telephone")
    add_log("13312175392","862521033324560","1478661355306","Telephone","To 13302157697","Telephone")
    add_log("13312175392","862521033324560","1478672420306","Telephone","To 13312175392","Telephone")
    add_log("13312175392","862521033324560","1478672440306","Telephone","From 13312175392","Telephone")
    add_log("13312175392","862521033324560","1478673490306","Telephone","From 13302157697","Telephone")

    # 收发短信
    add_log("13312175392","862521033324560","1478684440306","Message","To 13302157697","Message")
    add_log("13312175392","862521033324560","1478684340306","Message","From 13261539852","Message")
    add_log("13312175392","862521033324560","1478684640306","Message","From 13312175392","Message")
    add_log("13312175392","862521033324560","1478685440306","Message","From 13302157697","Message")


    add_log("13312175392","862521033324560","1478696440306","Secphone","ADB Connection"," ")
    add_log("13312175392","862521033324560","1478697440306","Secphone","ADB Connection"," ")
    add_log("13312175392","862521033324560","1478698440306","Secphone","ADB Connection"," ")
    add_log("13312175392","862521033324560","1478701440306","Secphone","ADB Connection"," ")
    add_log("13312175392","862521033324560","1478702140306","Secphone","ADB Connection"," ")
    add_log("13312175392","862521033324560","1478703240306","Secphone","ADB Connection"," ")




    add_log("13312175392","862521033324560","1478703345306","Secphone","Logout the app","SettingActivity")
    add_log("13312175392","862521033324560","1478704703306","System","Shutdown","SettingActivity")


    # add_log("13302130162","860482031439235","1478959345306","Secphone","Logout the app","SettingActivity")