# -*- coding: utf8 -*-
__author__ = 'GCY'

from pymongo import MongoClient
import re
import json

def change_app_info(dev_id,app_info):
    # 获取数据库连接
    # mongo_host = "repset/192.168.1.15/192.168.1.16"
    mongo_host = "192.168.1.15"
    # mongo_host = "127.0.0.1"
    mongo_port = 27017
    client = MongoClient(mongo_host,mongo_port)
    db = client["wcloud_o"]
    dev_db = db['dev']
    user_db = db['user']
    dev_db.update({"dev_id":dev_id},{"$set":{"app_info":app_info}})
    # user_db.update({"uid":uid},{"$addToSet":{"apps":}})  同时需要向用户应用表加入应用的id信息


if __name__ == '__main__':
    app_info = [
        {"app_id":"com.singuloid.secphone",
         "app_name":u"系统应用",
         "version_name":"secphone 1.0",
         "version_code":12,
         "icon":"jjj",
         "last_update_time":"1478604360306"},
        {"app_id":"com.tencent.mm",
         "app_name":u"微信",
         "version_name":"6.3.28",
         "version_code":20,
         "icon":"jjj",
         "last_update_time":"1478604360278"},
        {"app_id":"com.syberos.browser",
         "app_name":u"UC浏览器",
         "icon":"browserICON",
         "last_update_time":"1478604370278",
         "version_code":1,
         "version_name":"1.0"},
        {
            "app_id":"com.baidu.BaiduMap",
            "app_name":u"百度地图",
            "icon":"browserICON",
            "last_update_time":"1478804370278",
            "version_code":15,
            "version_name":"5.0.8"
        },
        {
            "app_id":"com.ss.android.article.news",
            "app_name":u"今日头条",
            "icon":"browserICON",
            "last_update_time":"1478804370278",
            "version_code":23,
            "version_name":"2.6.0"
        },
        {
            "app_id":"com.eg.android.AlipayGphone",
            "app_name":u"支付宝",
            "icon":"browserICON",
            "last_update_time":"1478804370278",
            "version_code":34,
            "version_name":"3.8.0"
        },
    ]
    app_str = json.dumps(app_info)
    change_app_info("862521033324560",app_str)