__author__ = 'GCY'
# -*- coding: utf8 -*-

from pymongo import MongoClient

mongo_host = "192.168.1.15"
mongo_port = 27017
client = MongoClient(mongo_host,mongo_port)
db = client["wcloud_o"]
users = db["user"]
admin_db = db['admin']

def change_admin_ou():
    """
    修改数据库中管理员的权限标识
    :return:
    """
    try:
        result = admin_db.find()
        for admin in result:
            admin_id = admin['uid']
            print admin_id
            # admin_db.update({"uid":admin_id},{"$set":{"contact_ous":["dc=test,dc=com"]}})

            if admin_id=="admin":
                continue
            ou = admin['ou']
            if ou=='admin':
                continue

            new_ou = get_ou_oudn(ou)
            admin_db.update({"uid":admin_id},{"$set":{"ou":new_ou}})
            print "former:"+ou+"changed to:"+new_ou

    except Exception as e:
        print("connection error"+e.message)


def get_ou_oudn(ou):
    if(ou.find("dc")<0 and ou.find("ou")<0):
        oudn = "dc=test,dc=com"
        ous = ou.split(",")
        for item in ous:
            oudn="ou="+item+","+oudn
    else:
        oudn = ou
    return oudn

if __name__ == '__main__':
    change_admin_ou()

