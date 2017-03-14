# -*- coding: utf8 -*-
__author__ = 'GCY'

import ldap
from pymongo import MongoClient

mongo_host = "192.168.1.15"
mongo_port = 27017
client = MongoClient(mongo_host,mongo_port)
db = client["wcloud_o"]
users = db["user"]
dev = db['dev']

def get_config():
    org_config = {}
    org_config['ldap_host']="192.168.1.15"
    org_config['ldap_port'] = 389
    org_config['ldap_base_dn']="dc=test,dc=com"
    org_config['ldap_user_dn']="cn=admin,dc=test,dc=com"
    org_config['ldap_pw'] = "IIEiieabcde12345!@#$%"
    org_config['ldap_at_dn'] = "dn"
    org_config['ldap_at_ou'] = "ou"

    return org_config


def create_ldap(ip,port=389, user_dn='', pw=''):
    lobj = ldap.open(ip,port)
    if user_dn and pw:
        lobj.simple_bind_s(user_dn, pw)
    return lobj

def getLdap():
    org_config = get_config()
    uldap = create_ldap( ip = org_config['ldap_host']
                    , port = org_config['ldap_port']
                    , user_dn = org_config['ldap_user_dn']
                    , pw = org_config['ldap_pw'])
    return uldap

def get_ou_tree(uldap,base_dn):
        """获取LDAP服务器上的树架构,注意最后引用时用需要封装一下"""
        try:
            ous = []
            res_id = uldap.search( base_dn, ldap.SCOPE_ONELEVEL
                    , 'objectClass=%s'%("organizationalUnit"), None)
            while uldap:
                rtype,rdata = uldap.result(res_id,0)
                if not rdata:
                    break
                ou = {"oudn":rdata[0][0],"ous":[],"users":[]}
                ou["ous"] = get_ou_tree(uldap,rdata[0][0])
                ous.append(ou)
            return ous
        except Exception as e:
            print(e.message)


def get_ldap_user_info(user_data):
    uid = user_data[1]['telephoneNumber'][0]
    username = user_data[1]['cn'][0]
    return dict(uid=uid,username=username)


if __name__ == '__main__':
    uldap = getLdap()
    result = uldap.search( "dc=test,dc=com", ldap.SCOPE_SUBTREE
                    , 'objectClass=%s'%("inetOrgPerson"), None)
    ldap_users = []
    ldap_user_list = []
    count = 0
    while result:
        rtype,rdata = uldap.result(result, 0)
        if not rdata:
            break
        ldap_users.append(get_ldap_user_info(rdata[0]))
        ldap_user_list.append(rdata[0][1]['telephoneNumber'][0])

    print "ldap中用户的数量"+str(len(ldap_user_list))
    del uldap

    result = users.find()
    all_users = []
    not_in_ldap = []
    not_in_ldap_ous = []
    for item in result:
        all_users.append(item['uid'])
        if(item['uid'] not in ldap_user_list):
            not_in_ldap.append({"uid":item['uid'],"oudn":item['oudn'],"username":item['username']})
            if(item['oudn'] not in not_in_ldap_ous):
                not_in_ldap_ous.append(item['oudn'])

    print len(not_in_ldap)
    # print not_in_ldap

    ldap_not_in_mongo = [val for val in ldap_user_list if val not in all_users]

    print len(ldap_not_in_mongo)
    print ldap_not_in_mongo



    # tree = get_ou_tree(uldap,"dc=test,dc=com")
    #
    # print str(tree)





