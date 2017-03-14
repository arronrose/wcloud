__author__ = 'GCY'
#-*- coding: utf8 -*-
# import ldap
# import ldap.modlist as modlist
import sys
from pymongo import MongoClient
import urllib
import urllib2
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

def get_config():
    org_config = {}
    org_config['ldap_host']="127.0.0.1"
    org_config['ldap_port'] = 389
    org_config['ldap_base_dn']="dc=test,dc=com"
    org_config['ldap_user_dn']="cn=admin,dc=test,dc=com"
    org_config['ldap_pw'] = "IIEiieabcde12345!@#$%"
    org_config['ldap_at_dn'] = "dn"
    org_config['ldap_at_ou'] = "ou"

    return org_config


# def create_ldap(ip,port=389, user_dn='', pw=''):
#     lobj = ldap.open(ip,port)
#     if user_dn and pw:
#         lobj.simple_bind_s(user_dn, pw)
#     return lobj

# def getLdap():
#     org_config = get_config()
#     uldap = create_ldap( ip = org_config['ldap_host']
#                     , port = org_config['ldap_port']
#                     , user_dn = org_config['ldap_user_dn']
#                     , pw = org_config['ldap_pw'])
#     return uldap

mongo_host = "127.0.0.1"
mongo_port = 27017
client = MongoClient(mongo_host,mongo_port)
db = client["wcloud_o"]
users = db["user"]

def get_user_list(oudn):
    oudn_user_list = []
    cursor = users.find({"oudn":oudn})
    for item in cursor:
        oudn_user_list.append(item)
    print("群组："+oudn+",用户数量："+str(len(oudn_user_list)))
    return oudn_user_list


def ldap_mod_user_requester(parameters):
    url="http://127.0.0.1:8082/a/wp/org/ldap_mod_user"                               #所要请求数据的url
    #                  #参数形式 ： “name" : "value",参数多余一个用,相隔
    data = urllib.urlencode(parameters)
    request=urllib2.Request(url,data)
    response=urllib2.urlopen(request)
    print "响应是:"+str(response.read())



if __name__ == '__main__':
    oudn_user_list = get_user_list("ou=管理员群,ou=青岛市应用示范群,dc=test,dc=com")

    for item in oudn_user_list:

        #构造请求的参数
        #'sid','key','dn','email','mobile','username','pnumber','dev_id','title'
        sid = "29e34be43f51a3da7c079bb214fdb6c8836238a9"
        key = item['key']
        dn = "ou=市委办公厅,ou=青岛市,dc=test,dc=com"
        email = item['email']
        mobile = "Y"
        username = item['username']
        pnumber = item['uid']
        devs = item['devs']
        if len(devs) >0:
            dev_id = devs[0]
        else:
            dev_id = ""
        title = item['title']

        param = {"sid":sid,"key":key,"dn":dn,"email":email,"mobile":mobile,"username":username,
                     "pnumber":pnumber,"dev_id":dev_id,"title":title}

        ldap_mod_user_requester(param)
            # users.update({"key":item['key']},{"$set":{"oudn":dn}})



