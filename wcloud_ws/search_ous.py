# -*- coding: utf8 -*-
__author__ = 'ZXC'
import ldap

def get_config():
    org_config = {}
    org_config['ldap_host']="111.204.189.34"
    org_config['ldap_port'] = 389
    org_config['ldap_base_dn']="dc=test,dc=com"
    org_config['ldap_user_dn']="cn=admin,dc=test,dc=com"
    org_config['ldap_pw'] = "111111"
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


if __name__ == '__main__':
    uldap = getLdap()
    result = uldap.search( "dc=test,dc=com", ldap.SCOPE_SUBTREE
                    , 'objectClass=%s'%("inetOrgPerson"), None)
    ous = []
    count = 0
    while result:
        count +=1
        rtype,rdata = uldap.result(result, 0)
        print(rdata)
        if not rdata:
            break
        ous.append(rdata[0])

    print len(ous)
    print "count:"+str(count)

    # tree = get_ou_tree(uldap,"dc=test,dc=com")
    #
    # print str(tree)

    del uldap


