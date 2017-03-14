#-*- coding: utf8 -*-
__author__ = 'gcynewstart'
import urllib
import json

# 获取服务器用户数据
def getUserData(servicePath):
    stream=urllib.urlopen(servicePath+"/a/wp/org/get_all_users")
    rawData=stream.read()
    users = json.loads(rawData)["users"]
    print "获取json数据完成！"
    return users


# getUserData("http://111.204.189.34:6082")

