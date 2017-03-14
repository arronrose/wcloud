# -*- coding: utf8 -*-

import web
import logging
import sha
import os

import ws_io
import ecode
import session_db
import org
import user_ldap
import user_db
import dev_db
import log_db
import cert_db
import config
import admin_db
# import trace
import time
import baseStation
#+++ 20150506
import strategy_db
import json
import re
#+++ 20150602
import xlrd
import commands
import shutil
#+++ 20150706
import contact_db
#+++ 20150716
import trace_db
#+++ 20150804
import captcha_web
# +++20151103
import log_web_db
# +++20151127 用于IP地址的转换
import urllib
import sys
from xml.dom.minidom import parseString
# +++20160122 统计在线人数数据表
import online_statistics_db
import traceback
#+++1117 four member
import master_db   #+++ 9.18
import SA_db   #+++ 9.18
import auditor_db   #+++ 9.18
import operation   #+++11.21
import global_db   #+++11.23
import xlwt   #+++11.23 导出到excel的模块（在服务器上预装此包）

def getLdap():
    org_config = org.get_config()
    uldap = user_ldap.create_ldap( ip = org_config['ldap_host']
                    , port = org_config['ldap_port']
                    , base_dn = org_config['ldap_base_dn']
                    , user_dn = org_config['ldap_user_dn']
                    , pw = org_config['ldap_pw']
                    , at_uid = org_config['ldap_at_uid']
                    , at_allow_use = org_config['ldap_at_allow_use']
                    , at_pnumber = org_config['ldap_at_pnumber']
                    , at_email = org_config['ldap_at_email']
                    , at_username = org_config['ldap_at_username']
                    , at_dn = org_config['ldap_at_dn']
                    , at_ou = org_config['ldap_at_ou']
                    , at_job = org_config['ldap_at_job'])
    return uldap

global ldap_base_dn
ldap_base_dn = "dc=test,dc=com"

class Login:
    #{{{
    def POST(self):
        """
        input:
            uid: user id
            pw: password
            session_id:web session_id
            captcha: encry_captcha
        output:
            rt: error code
            sid: session id
            is_config_ok: is this org acc config finish?
            loginType:loginVersion 。
        """
        rt = ecode.FAILED
        sid = ''
        is_config_ok = 1
        loginType='' 

        try:
            i = ws_io.ws_input(['uid','pw','session_id','captcha'])
            if not i:
                raise ecode.WS_INPUT
            logging.error("Login session_id:%s,captha:%s",i['session_id'],i['captcha'])
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 
            if i['session_id']!='':
                #+++ 20150804 校验验证码
                dbCaptcha=captcha_web.get_captcha(i['session_id'])
                logging.warn("captcha from db is : %s",dbCaptcha)
                if len(dbCaptcha)<=0:
                    raise ecode.CAPTHCA_IS_SENDED #验证码过期
                if i['captcha']!=dbCaptcha:
                    raise ecode.CAPTCHA_ERROR

            ###四员分立，统一登录###
            #管理员master
            # 20161116 入口从内存中读取
            if master_db.is_has_master(i['uid']):
                if not master_db.check_pw(i['uid'], sha.new(i['pw']).hexdigest()):
                    raise ecode.USER_AUTH
                else:
                    loginType='master'
            elif admin_db.is_has_admin(i['uid']):
                if not admin_db.check_pw(i['uid'],sha.new(i['pw']).hexdigest()):
                        raise ecode.USER_AUTH
                else:
                    loginType='admin'
            elif auditor_db.is_has_auditor(i['uid']):
                if not auditor_db.check_pw(i['uid'],sha.new(i['pw']).hexdigest()):
                        raise ecode.USER_AUTH
                else:
                    loginType='auditor'
            elif SA_db.is_has_SA(i['uid']):
                if not SA_db.check_pw(i['uid'], sha.new(i['pw']).hexdigest()):
                    raise ecode.USER_AUTH
                else:
                    loginType='sa'
            else:
                raise ecode.USER_NOT_EXIST

            # create session
            sid = session_db.user.create( i['uid'], loginType, web.ctx.ip)

            if not sid:
                raise ecode.SDB_OP
            org_config = org.get_config()
            if not org_config['ldap_host']:
                is_config_ok = 0

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('org admin login')
            error_info = str(traceback.format_exc()).replace("\n"," ")
            #日志记录

        # op_user=i['uid']
        # print op_user
        # print str(i)
        # ip_addr = get_ip_addr(web.ctx.ip)
        # if loginType=='master':
        #     op_type=operation.LOGIN_master.type
        #     # op_desc=operation.LOGIN_master.desc
        # elif loginType=='admin':
        #     op_type=operation.LOGIN_admin.type
        #     # op_desc=operation.LOGIN_admin.desc
        # elif loginType=='sa':
        #     op_type=operation.LOGIN_sa.type
        #     # op_desc=operation.LOGIN_sa.desc
        # elif loginType=='auditor':
        #     op_type=operation.LOGIN_auditor.type
        #     # op_desc=operation.LOGIN_auditor.desc
        # elif loginType=='':
        #     op_type=operation.LOGIN_failed.type
        #     # op_desc=operation.LOGIN_failed.desc
        # op_result=rt.desc
        # op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        # log_web_db.add_log(op_user,[],op_time ,op_type, ip_addr, op_result )
        # # ( admin, users, time, action, info,result)
        # # (i['admin'],[],timeStr,i['action'],ip_addr,i['result'])
        return ws_io.ws_output(dict(rt=rt.eid,sid=sid,is_config_ok=is_config_ok,loginType=loginType),error_info)
    #}}}

#+++ 20150804 设置验证码
class SetCaptcha:
    def POST(self):
        """
        input:
            session_id:web端产生的临时web session
            captcha:加密的验证码内容（sha1）
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['session_id','captcha'])
            logging.error("SetCaptcha session_id:%s,captha:%s",i['session_id'],i['captcha'])
            if not i:
                raise ecode.WS_INPUT
            
            if not captcha_web.add_captcha(i['session_id'], i['captcha']):
                raise ecode.DB_OP
            
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('set a captcha.')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

class Logout:
    #{{{
    def POST(self):
        """
        input:
            sid: 

        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            # +++20160112 将用户相关的选中状态清除
            admin = session_db.user.get_user(i['sid'],web.ctx.ip)
            oudn = admin_db.get_ou_by_uid(admin)
            user_db.set_ou_users_checked(oudn,0,admin)
            user_db.set_ou_users_checked(oudn,0,admin+"_contact")
            session_db.user.del_by_sid( i['sid'], web.ctx.ip)
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('Logout')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        #日志记录
        op_user=admin
        if admin_db.is_has_admin(admin):
            op_type="操作员登出"
            op_desc=operation.LOGOUT.desc
        elif master_db.is_has_master(admin):
            op_type="管理员登出"
            op_desc=operation.LOGOUT.desc
        elif auditor_db.is_has_auditor(admin):
            op_type="审计员登出"
            op_desc=operation.LOGOUT.desc
        elif SA_db.is_has_SA(admin):
            op_type="安全员登出"
            op_desc=operation.LOGOUT.desc
        # op_type=operation.LOGOUT.type
        # op_desc=operation.LOGOUT.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        # ip_addr = get_ip_addr(web.ctx.ip)
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}


class SetPW:
    #{{{
    def POST(self):
        """
        input:
            sid: 
            oldpw:
            newpw:
        output:
            rt: error code
        """
        rt = ecode.FAILED
        loginType=''

        try:
            i = ws_io.ws_input(['sid','oldpw','newpw'])
            if not i:
                raise ecode.WS_INPUT

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            if not config.check_pw_rule( i['newpw']) :
                raise ecode.PW_RULE

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            ###四员分立，统一改密码###
            # 20161117+++统一从数据库修改
            # 管理员master 新密码存入 sha.new(i['pw']).hexdigest()
            print master_db.get_pw_by_uid(user)
            print sha.new(i['oldpw']).hexdigest()
            if master_db.is_has_master(user):
                if master_db.get_pw_by_uid(user)!= sha.new(i['oldpw']).hexdigest():
                    raise ecode.OLD_PW_ERROR
                if not master_db.update_pw(user,sha.new(i['newpw']).hexdigest()):
                    raise ecode.DB_OP
                loginType='master'
            #操作员admin
            elif admin_db.is_has_admin(user):
                if admin_db.get_pw_by_uid(user)!= sha.new(i['oldpw']).hexdigest():
                    raise ecode.OLD_PW_ERROR
                if not admin_db.update_pw(user,sha.new(i['newpw']).hexdigest()):
                    raise ecode.DB_OP
                loginType='admin'
            #审计员auditor
            elif auditor_db.is_has_auditor(user):
                if auditor_db.get_pw_by_uid(user)!= sha.new(i['oldpw']).hexdigest():
                    raise ecode.OLD_PW_ERROR
                if not auditor_db.update_pw(user,sha.new(i['newpw']).hexdigest()):
                    raise ecode.DB_OP
                loginType='auditor'
            #安全员SA
            elif SA_db.is_has_SA(user):
                if SA_db.get_pw_by_uid(user)!= sha.new(i['oldpw']).hexdigest():
                    raise ecode.OLD_PW_ERROR
                if not SA_db.update_pw(user,sha.new(i['newpw']).hexdigest()):
                    raise ecode.DB_OP
                loginType='sa'
            #非以上用户
            else:
                raise ecode.NOT_PERMISSION
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('setpw')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        # 日志记录DDDDD
        op_user = session_db.user.get_user( i['sid'], web.ctx.ip)
        # if loginType=='admin':
        #     op_type = operation.SETPW_admin.type
        #     op_desc = operation.SETPW_admin.desc
        # elif loginType=='master':
        #     op_type = operation.SETPW_master.type
        #     op_desc = operation.SETPW_master.desc
        # elif loginType=='sa':
        #     op_type = operation.SETPW_sa.type
        #     op_desc = operation.SETPW_sa.desc
        # elif loginType=='auditor':
        #     op_type = operation.SETPW_auditor.type
        #     op_desc = operation.SETPW_auditor.desc
        op_type = operation.SETPW_master.type
        op_desc = operation.SETPW_master.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        print op_user
        print op_type
        print op_desc
        print op_result
        print op_time
        # log_web_db.add_log(op_user,[],op_time,op_type, op_desc, op_result )

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}



class OrgInfo:
    #{{{
    def POST(self):
        """
        input:
            sid: session id
            auth_mode:0
            org_name:''
            org_addr:''
            admin_pnumber:''
            admin_email:''
        output:
            rt: error code
        """
        rt = ecode.FAILED
        sid = ''

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if user != 'admin':
                raise ecode.NOT_PERMISSION

            kv_table = {}
            if i.has_key('auth_mode'):
                kv_table['auth_mode'] = int(i['auth_mode'])
            if i.has_key('org_name'):
                kv_table['org_name'] = i['org_name']
            if i.has_key('org_addr'):
                kv_table['org_addr'] = i['org_addr']
            if i.has_key('admin_pnumber'):
                kv_table['admin_pnumber'] = i['admin_pnumber']
            if i.has_key('admin_email'):
                kv_table['admin_email'] = i['admin_email']

            if not org.update_config(kv_table):
                raise ecode.DB_OP

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('set org info')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)


    def GET(self):
        """
        input:
            sid: session id
        output:
            rt: error code
            auth_mode:0
            org_name:''
            org_right:''
            admin_email:''
        """
        rt = ecode.FAILED
        auth_mode=0
        admin_name=''
        org_right=''
        #org_addr=''
        #admin_pnumber=''
        admin_email=''
        org_contact_ous=''

        try:
            # 遍历sid 判断请求参数是否错误
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            # 版本判断，是否是当前版本允许的操作
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 
            # 用户判断，是否登陆，从session_db中取出
            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            # 获得配置文件中的值给org_config
            org_config = org.get_config()
            if user != 'admin':
                # 判断权限
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
                else:
                    # 有权限的情况下
                    org_right,admin_email,org_contact_ous = admin_db.get_ou_and_email_by_uid(user)
                    auth_mode = org_config['auth_mode']
                    admin_name = user
                    if org_right=="admin":
                        org_right = ldap_base_dn
                    
            else:
                auth_mode = org_config['auth_mode']
                admin_name = org_config['org_name']
                org_right = ldap_base_dn
                admin_email = org_config['admin_email']
                # org_contact_ous = org.config['org_contact_ous']
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get org info')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,auth_mode=auth_mode
            ,org_right=org_right,admin_name=admin_name,
                                    admin_email=admin_email,org_contact_ous=org_contact_ous),error_info)
    #}}}


class LdapConfig:
    #{{{
    def POST(self):
        """
        input:
            sid: session id
            ldap_host: ''
            ldap_port:389
            ldap_base_dn:''
            ldap_user_dn:''
            ldap_pw:''
            ldap_at_uid:''
            ldap_at_allow_use:''
            ldap_at_pnumber:''
            ldap_at_email:''
        output:
            rt: error code
        """
        rt = ecode.FAILED
        sid = ''

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if user != 'admin':
                
                raise ecode.NOT_PERMISSION

            kv_table = {}
            if i.has_key('ldap_host'):
                kv_table['ldap_host'] = i['ldap_host']
            if i.has_key('ldap_port'):
                kv_table['ldap_port'] = int(i['ldap_port'])
            if i.has_key('ldap_base_dn'):
                kv_table['ldap_base_dn'] = i['ldap_base_dn']
            if i.has_key('ldap_user_dn'):
                kv_table['ldap_user_dn'] = i['ldap_user_dn']
            if i.has_key('ldap_pw'):
                kv_table['ldap_pw'] = i['ldap_pw']
            if i.has_key('ldap_at_uid'):
                kv_table['ldap_at_uid'] = i['ldap_at_uid']
            if i.has_key('ldap_at_allow_use'):
                kv_table['ldap_at_allow_use'] = i['ldap_at_allow_use']
            if i.has_key('ldap_at_pnumber'):
                kv_table['ldap_at_pnumber'] = i['ldap_at_pnumber']
            if i.has_key('ldap_at_email'):
                kv_table['ldap_at_email'] = i['ldap_at_email']

            if not org.update_config(kv_table):
                raise ecode.DB_OP

            # org_config = org.get_config()
            uldap = getLdap()

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('set org ldap config')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)


    def GET(self):
        """
        input:
            sid: session id
        output:
            rt: error code
            ldap_host: ''
            ldap_port:389
            ldap_base_dn:''
            ldap_user_dn:''
            ldap_pw:''
            ldap_at_uid:''
            ldap_at_allow_use:''
            ldap_at_pnumber:''
            ldap_at_email:''
        """
        rt = ecode.FAILED
        ldap_host =  ''
        ldap_port = 389
        ldap_base_dn = ''
        ldap_user_dn = ''
        ldap_pw = ''
        ldap_at_uid = ''
        ldap_at_allow_use = ''
        ldap_at_pnumber = ''
        ldap_at_email = ''

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            org_config = org.get_config()
#             if user != org_config['admin']:
#                 raise ecode.NOT_PERMISSION
#             if user != org_config['admin']:
#                 if not admin_db.is_has_admin(user):
#                     raise ecode.NOT_PERMISSION
                
            ldap_host = org_config['ldap_host']
            ldap_port = org_config['ldap_port']
            ldap_base_dn = org_config['ldap_base_dn']
            ldap_user_dn = org_config['ldap_user_dn']
            ldap_pw = org_config['ldap_pw']
            ldap_at_uid = org_config['ldap_at_uid']
            ldap_at_allow_use = org_config['ldap_at_allow_use']
            ldap_at_pnumber = org_config['ldap_at_pnumber']
            ldap_at_email = org_config['ldap_at_email']

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get org ldap config info')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid
            ,ldap_host = ldap_host
            ,ldap_port = ldap_port
            ,ldap_base_dn = ldap_base_dn
            ,ldap_user_dn = ldap_user_dn
            ,ldap_pw = ldap_pw
            ,ldap_at_uid = ldap_at_uid
            ,ldap_at_allow_use = ldap_at_allow_use
            ,ldap_at_pnumber = ldap_at_pnumber
            ,ldap_at_email = ldap_at_email),error_info)
    #}}}



class LdapUsers:
    #{{{
    def GET(self):
        """
        input:
            sid: sesssion id
        output:
            rt: error code
            users:[{uid:'',email:'',pnumber:'',username:'','dn':'','ou':''},{}]
            nau_users:[{uid:'',email:'',pnumber:'',username:'','dn':'','ou':''},{}]
        """
        rt = ecode.FAILED
        users = []
        nau_users = []

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            org_config = org.get_config()
#             if user != org_config['admin']:
#                 raise ecode.NOT_PERMISSION
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
            

            uldap = getLdap()
            
            for u in uldap.get_all_users():
                uinfo =  u[1]
                if not uinfo.has_key(org_config['ldap_at_uid']):
                    continue
                uid = uinfo[org_config['ldap_at_uid']]
                if type(uid) is list:
                    uid = uid[0]

                if not uinfo.has_key(org_config['ldap_at_allow_use']):
                    continue
                allow_use = uinfo[org_config['ldap_at_allow_use']]
                if type(allow_use) is list:
                    allow_use = allow_use[0]

                email = ''
                if uinfo.has_key(org_config['ldap_at_email']):
                    email = uinfo[org_config['ldap_at_email']]
                    if type(email) is list:
                        email = email[0]

                pnumber = ''
                if uinfo.has_key(org_config['ldap_at_pnumber']):
                    pnumber = uinfo[org_config['ldap_at_pnumber']]
                    if type(pnumber) is list:
                        pnumber = pnumber[0]
                username = ''
                if uinfo.has_key(org_config['ldap_at_username']):
                    username = uinfo[org_config['ldap_at_username']]
                    if type(username) is list:
                        username = username[0]
                dn = str(u[0])
                #if uinfo.has_key(org_config['ldap_at_dn']):
                    #dn = uinfo[org_config['ldap_at_dn']]
                    #if type(dn) is list:
                        #dn = dn[0]

                if allow_use == 'Y':
                    users.append( {'uid':uid,'email':email, 'pnumber':pnumber, 'username':username, 'dn':dn} )
                else:
                    nau_users.append( {'uid':uid,'email':email, 'pnumber':pnumber, 'username':username, 'dn':dn} )

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get ldap users')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid, users=users,nau_users=nau_users),error_info)
    #}}}
    
    
class LdapOus:
    #{{{
    def GET(self):
        """
        input:
            sid: sesssion id
        output:
            rt: error code
            ous:['dn':'','ou':''},{}]
        """
        rt = ecode.FAILED
        ous = []

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if user != 'admin':
                raise ecode.NOT_PERMISSION

            uldap = getLdap()
            
            for ou in uldap.get_all_ous():
                ouinfo =  ou[1]
                dn = str(ou[0])
                ous.append( {'ou':ouinfo['ou'], 'dn':dn} )
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get ldap users')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid, ous=ous),error_info)
    #}}}

class LdapGetOuBySid:
    #{{{
    def GET(self):
        """
        input:
            sid: sesssion id
        output:
            rt: error code
            dn: oudn
            contacts: [...]
        """
        rt = ecode.FAILED
        org_config = org.get_config()
        oudn = ''
        contact_ous = []
        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
                else:
                    ou = admin_db.get_ou_by_uid(user)
                    contact_arr = admin_db.get_contact_ous_by_uid(user)
                    logging.warn("LdapGetOuBySid--ou:%s",ou)
                    if ou=="admin":
                        oudn = org_config['ldap_base_dn']
                        contact_ous = org_config['ldap_base_dn']
                    else:
                        oudn = ou
                        contact_ous = contact_arr
            else:
                oudn = org_config['ldap_base_dn']
                contact_ous = org_config['ldap_base_dn']

            rt = ecode.OK
            error_info = ""
            logging.warn("LdapGetOuBySid--oudn:%s",oudn)
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get oudn bu sid')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid, dn =oudn, contacts=contact_ous),error_info)

    #}}}
class LdapOneLevel:
    #{{{
    def GET(self):
        """
        input:
            sid: sesssion id
            oudn: oudn在前台点击群组时获得的群组dn(选填)
        output:
            rt: error code
            ou: oudn为了标志现在的用户
            ous:[{'dn':'','ou':''},{}]
            users:[{'dn':'',uid:'',email:'',pnumber:'',username:''},{}]授权的用户
        """
        rt = ecode.FAILED
        ous = []
        users = []

        # org_config = org.get_config()
        oudn = ''
        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # if user != org_config['admin']:
            #     if not admin_db.is_has_admin(user):
            #         raise ecode.NOT_PERMISSION
            if i.get('oudn')==None:
                oudn = admin_db.get_ou_by_uid(user)
            else:
                oudn = i['oudn']
            logging.warn("LdapOneLevel--Oudn:%s",oudn)
            uldap = getLdap()
            
            for onelevel in uldap.get_all_onelevel(oudn):
                info =  onelevel[1]
                dn = str(onelevel[0])
                if not info.has_key(at_uid):
                    if not info.has_key(at_ou):
                        continue
                    ou = info[at_ou]
                    if type(ou) is list:
                        ou = ou[0]
                    ous.append({'dn':dn,'ou':ou})
                else:
                    if not info.has_key(at_allow_use):
                        continue
                    allow_use = info[at_allow_use]
                    if type(allow_use) is list:
                        allow_use = allow_use[0]
                    #这个逻辑很重要，因为返回来的很有可能就是一个列表结构，只是表明上输出是字符
                    uid = info[at_uid]
                    if type(uid) is list:
                        uid = uid[0]
    
                    username = ''
                    if info.has_key(at_username):
                        username = info[at_username]
                        if type(username) is list:
                            username = username[0];
                                
                    pnumber = ''
                    if info.has_key(pnumber):
                        pnumber = info[at_pnumber]
                        if type(pnumber) is list:
                            pnumber = pnumber[0];
                            
                    if allow_use=='Y':
                        users.append( {'dn':dn, 'uid':uid,'username':username,'pnumber':pnumber} )
            rt = ecode.OK
            error_info=""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.exception('get ldap onelevel')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid, dn =oudn,ous=ous, users=users),error_info)
    #}}}

class LdapOneLevelUidHide:
    #{{{
    def GET(self):
        """
        input:
            sid: sesssion id
            oudn: oudn在前台点击群组时获得的群组dn(选填)
            contacts:通信群组(选填)
        output:
            rt: error code
            ou: oudn为了标志现在的用户
            ous:[{'dn':'','ou':''},{}]
            users:[{'dn':'',uid:'',email:'',pnumber:'',username:''},{}]授权的用户
        """
        rt = ecode.FAILED
        ous = []
        users = []

        # org_config = org.get_config()
        oudn = ''
        try:
            #请求参数判断
            i = ws_io.ws_input(['sid'])
            # i:<Storage {对应前端cookie里面的org_session_id ---  'sid': u'e38231c64b7bc40d20b180d0a6b515f76210c14e',
            #           对应前端的rootdn ---  'oudn': u'ou=\u6d77\u4fe1\u6d4b\u8bd5\u7fa4\u7ec4,dc=test,dc=com',
            #           对应前端的oudn ---  'contacts': u'ou=\u6d77\u4fe1\u6d4b\u8bd5\u7fa4\u7ec4,dc=test,dc=com'}>
            if not i:
                raise ecode.WS_INPUT
            # 版本控制
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP
            # 登陆判断
            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            # 权限判断
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
            # 请求参数即sid中判断管理权限，不存在时取uid为oudn
            if i.get('oudn')==None:
                oudn = admin_db.get_ou_by_uid(user)
            else:
                # 存在管理权限时，取管理权限oudn和通信权限contacts
                oudn = i['oudn']
                # oudn : ou=海信测试群组,dc=test,dc=com
                contacts = i['contacts']
                # contacts :ou=海信测试群组,dc=test,dc=com
            logging.warn("LdapOneLevel--Oudn:%s",contacts)
            # 逻辑判断后，生成ldap
            uldap = getLdap()
            # <user_ldap.UserLDAP instance at 0x349bcf8>
            # 通信权限里面取出内容
            for onelevel in uldap.get_all_onelevel(contacts):
                # info用户的具体信息即：{'telephoneNumber': ['13261539851'], 'cn': ['\xe9\xad\x91\xe9\xad\x85\xe9\xad\x8d\xe9\xad\x89'], 'objectClass': ['top', 'inetOrgPerson'], 'userPassword': ['12345678'], 'mobile': ['Y'], 'sn': ['\xe9\xad\x85\xe9\xad\x8d\xe9\xad\x89']}
                info =  onelevel[1]
                # dn转化为字符串形式的用户信息即： cn=魑魅魍魉,ou=通信三级群组,ou=通信二级群组,ou=通信权限测试群组,dc=test,dc=com
                dn = str(onelevel[0])
                # at_##为全局变量，即为在ldap中取出的##
                # 将uid，ou从列表转化为字符串，然后重新赋给ous，即最后的出的ous为字符串。
                # has_key判断字符串
                if not info.has_key(at_uid):
                    if not info.has_key(at_ou):
                        continue
                    ou = info[at_ou]
                    if type(ou) is list:
                        ou = ou[0]
                    ous.append({'dn':dn,'ou':ou})
                else:
                    # at_allow_use:mobile
                    if not info.has_key(at_allow_use):
                        continue


                    allow_use = info[at_allow_use]
                    # allow_use:['Y']---列表
                    if type(allow_use) is list:
                        allow_use = allow_use[0]
                    # allow_use:Y---字符串
                    #这个逻辑很重要，因为返回来的很有可能就是一个列表结构，只是表明上输出是字符


                    uid = info[at_uid]
                    if type(uid) is list:
                        uid = uid[0]

                    username = ''
                    if info.has_key(at_username):
                        username = info[at_username]
                        if type(username) is list:
                            username = username[0];

                    pnumber = ''
                    if info.has_key(pnumber):
                        pnumber = info[at_pnumber]
                        if type(pnumber) is list:
                            pnumber = pnumber[0];

                    key = user_db.get_user_key_by_uid(uid)
                    # print("-----key-------"+str(key))
                    # print "---------------"+oudn
                    # print "-----result----"+str(oudn in dn)
                    if oudn in dn :
                        users.append( {'dn':dn, 'uid':uid,'username':username,'pnumber':pnumber,'key':key} )
                        # print "#################"
                        # print users
                    else :
                        users.append( {'dn':dn, 'uid':"***********",'username':username,'pnumber':pnumber,'key':key} )
            rt = ecode.OK
            # print users
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED

            logging.error('get ldap onelevel'+e.message)
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid, oudn =oudn, contacts =contacts,ous=ous, users=users),error_info)
    #}}}
    
class StaticUserInfo:
    #{{{
    def GET(self):
        """
        input:
            sid: sesssion id
            oudn: oudn在前台点击群组时获得的群组dn
        output:
            rt: error code
            ous:[{'dn':'','ou':''},{}]
            users:[{'dn':'',uid:'',email:'',pnumber:'',username:''},{}]授权的用户
        """
        rt = ecode.FAILED
        all = {}
        
        try:
            s = ''.join([line.rstrip() for line in open('ocr.txt')]) 
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get ldap onelevel')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid, ous=ous, users=users),error_info)
    #}}}


class LdapTree:
    #{{{
    org_config = org.get_config()
    global ip
    ip = org_config['ldap_host']
    global port
    port= org_config['ldap_port']
    global base_dn
    base_dn = org_config['ldap_base_dn']

    global user_dn
    user_dn = org_config['ldap_user_dn']
    global pw
    pw = org_config['ldap_pw']
    global at_uid
    at_uid = org_config['ldap_at_uid']
    global at_allow_use
    at_allow_use = org_config['ldap_at_allow_use']
    global at_pnumber
    at_pnumber = org_config['ldap_at_pnumber']
    global at_email
    at_email = org_config['ldap_at_email']
    global at_username
    at_username = org_config['ldap_at_username']
    global at_dn
    at_dn = org_config['ldap_at_dn']
    global at_ou
    at_ou = org_config['ldap_at_ou']
    global at_job
    at_job = org_config['ldap_at_job']

    global uldap
    uldap = getLdap()
    def GET(self):
        """
        input:
            sid: sesssion id
        output:
            rt: error code
            ous:[{'dn':'','ou':''},{}]
            users:[{'dn':'',uid:'',email:'',pnumber:'',username:''},{}]授权的用户
        """
        rt = ecode.FAILED
        all = {}
        try:
            org_config = org.get_config()
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            """
                                    如果登陆用户不是高级管理员,判定是否为单位管理员，如果是，则只加载该单位的人员信息
            """
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
                else:
                    oudn = admin_db.get_ou_by_uid(user)
                    ou = admin_db.get_ou_friendly_name_by_uid(user)
                    all = LdapTree().get_all_sons(oudn,ou)
            else:
                all = LdapTree().get_all_sons(org_config['ldap_base_dn'],'admin')
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get ldap tree')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid, all=all),error_info)
 

    def get_all_sons(self,oudn,ouname):
        """get all users and ous on one level for the oudn"""
        #查找同一层级SCOPE_ONELEVEL
        #基于群组的dn查找,找到自己所有的子节点 
        #读取配置文件中的内容
        sons = uldap.get_all_onelevel(oudn)#找到基准节点的所有下一层级子节点
        ous=[]
        users=[]
        for son in sons:   
            info = son[1]
            dn = str(son[0])
            if not dn:
                continue
            else:
                if not info.has_key(at_uid):
                    if info.has_key(at_ou):
                        ou = info.get(at_ou)
                        if type(ou) is list:
                            ou = ou[0]
                        sons2 = LdapTree().get_all_sons(dn,ou);
                        if not sons2:
                            continue
                        else:
                            ous.append(sons2)
                else:
                    if not info.has_key(at_allow_use):
                        continue
                    allow_use = info[at_allow_use]
                    if type(allow_use) is list:
                        allow_use = allow_use[0]
                        #这个逻辑很重要，因为返回来的很有可能就是一个列表结构，只是表明上输出是字符
                    uid = info[at_uid]
                    if type(uid) is list:
                        uid = uid[0]
    
                    username = ''
                    if info.has_key(at_username):
                        username = info[at_username]
                        if type(username) is list:
                            username = username[0];
                                
                    pnumber = ''
                    if info.has_key(at_pnumber):
                        pnumber = info[at_pnumber]
                        if type(pnumber) is list:
                            pnumber = pnumber[0];
                            
                    email = ''
                    if info.has_key(at_email):
                        email = info[at_email]
                        if type(email) is list:
                            email = email[0];
                            
                    job = ''
                    if info.has_key(at_job):
                        job = info[at_job]
                        if type(job) is list:
                            job = job[0];
                            
                    if allow_use=='Y':
                        users.append( {'dn':dn, 'uid':uid,'username':username,'pnumber':pnumber,'job':job,'email':email})
                    
        return {'dn':oudn,'ou':ouname,'ous':ous,'users':users}
            
    #}}}

class LdapAll:
    #{{{
    def GET(self):
        '''
        input:
            sid:session id
                        这个其实也得考虑一下以后的扩展，将根节点信息写在配置文件中应该是没问题
        output:
            rt:error code
            all:{'dn':dn,'ou':ou,'ous':[],'users':[]}
        '''
        rt = ecode.FAILED
        all = {}
        ous = []
        users = []

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if user != 'admin':
                raise ecode.NOT_PERMISSION

            uldap = getLdap()
            
            for all in uldap.get_all():
                ouinfo =  ou[1]
                dn = str(ou[0])
                ous.append( {'ou':ouinfo['ou'], 'dn':dn} )
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get ldap users')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid, ous=ous),error_info)
        
    #}}}

#LDAP授权
class LdapUsersAllowUse:
    #{{{
    def POST(self):
        """
        input:
            sid: sesssion id
            uid0: uid1
            uid1: uid2
            ...
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION

            uldap = getLdap()

            uids = []
            for uid in i.keys():
                if len(uid) > 3 and uid[:3] == 'uid':
                    u = uldap.get_uid_by_username(i[uid])
                    if u:
                        uids.append(u)
            if not uldap.users_allow_use( uids ):
                raise ecode.MOD_LDAP_ERROR

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('LdapUsersAllowUse')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,username=i.keys(),uids=uids),error_info)
    #}}}

class UserInfo:
    #{{{
    def GET(self):
        """
        input:
            sid:
            uid:
        output:
            rt: error code
            devs:
        """
        rt = ecode.FAILED
        devs = []

        try:
            i = ws_io.ws_input(['sid','uid'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION

            devs = user_db.devs( i['uid'])

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get user list')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,devs=devs),error_info)
    #}}}
    
class CheckPwdAndDevs:
    #{{{
    def GET(self):
        """
        input:
            sid:
            uid:
            pwd:
        output:
            rt: error code
            devs:
        """
        rt = ecode.FAILED
        dev = ''

        try:
            i = ws_io.ws_input(['sid','uid','pwd'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
                
            #创建LDAP连接   
            uldap = getLdap()
            
            if user_db.is_has_user(i['uid']) and dev_db.is_has_user(i['uid']):    #如果用户已经注册过直接去数据库严重密码
                if user_db.check_pw(i['uid'],sha.new(i['pwd']).hexdigest()):
                    dev_id = dev_db.get_dev_id_by_curuser(i['uid'])
                    dev = dev_db.get_static_info(dev_id,'model_number')
                else:
                    raise ecode.USER_AUTH
            else:
                if uldap.get_user(i['uid']):     #如果用户在ldap中存在，说明用户未注册，否则用户不存在
                    raise ecode.USER_UN_VERIFIED
                else:
                    raise ecode.USER_NOT_EXIST

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get user list')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,dev=dev),error_info)
    #}}}


class UserLog:
    #{{{
    def GET(self):
        """
        input:
            sid:
            dev_id:
        output:
            rt: error code
            logs:[{},..]
        """
        rt = ecode.FAILED
        logs = []
        logtime={}

        try:
            i = ws_io.ws_input(['sid','dev_id'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

#            org_config = org.get_config()
#            if user != org_config['admin']:
#                raise ecode.NOT_PERMISSION

            uid=dev_db.get_cur_user(i['dev_id'])
            logs = log_db.get_logs(uid,i['dev_id'])
            
            #日志时间
            for log in logs:
                utime=int(log['t'])*0.001   #长整型转换为python可操作时间戳
                utimeArry=time.localtime(utime)
                logtime=time.strftime("%Y-%m-%d %H:%M:%S",utimeArry)
                log['t']=logtime

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get user log')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,logs=logs),error_info)
    #}}}


class LdapSync:
    #{{{
    def POST(self):
        """
        input:
            sid:
            admin_pw:
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            # org_config = org.get_config()
            if not i.has_key('admin_pw'):
                user = session_db.user.get_user( i['sid'], web.ctx.ip)
                if not user:
                    raise ecode.NOT_LOGIN

                if user != 'admin':
                    if not admin_db.is_has_admin(user):
                        raise ecode.NOT_PERMISSION
            else:
                if i['admin_pw'] != '184070c4026106318b0c920d873d0b6a6e428815':
                    raise ecode.NOT_PERMISSION

            org.sync_ldap_user()

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('sync_ldap_user')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}


class LdapSyncConfig:
    #{{{
    def POST(self):
        """
        input:
            sid: session id
            ldap_sync_cycle: 
        output:
            rt: error code
        """
        rt = ecode.FAILED
        sid = ''

        try:
            i = ws_io.ws_input(['sid','ldap_sync_cycle'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION

            kv_table = {}
            kv_table['ldap_sync_cycle'] = i['ldap_sync_cycle']

            if not org.update_config(kv_table):
                raise ecode.DB_OP

            #os.system('wcloud_ldap_sync_server.py stop "%s"'%(org_config('ldap_sync_pidfile')))
            #if i['ldap_sync_cycle'] > 0:
            #    if 0 != os.system('wcloud_ldap_sync_server.py start "%s"'%(config.get('org_config'))):
            #        raise ecode.START_LDAP_SYNC_SERV

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('set org ldap config')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)


    def GET(self):
        """
        input:
            sid: session id
        output:
            rt: error code
            ldap_sync_cycle: ''
        """
        rt = ecode.FAILED
        ldap_sync_cycle = 0

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            org_config = org.get_config()
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION

            ldap_sync_cycle = org_config['ldap_sync_cycle']

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get org ldap config info')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,ldap_sync_cycle= ldap_sync_cycle),error_info)
    #}}}
class LdapAddUser:
    #{{{
    def POST(self):
        '''
        input:
            sid: session id
            dn:  the oudn of adduser
            pw:  the init pw of user
            email: email
            mobile: Y/N  at_allow_use
            username:
            pnumber: telephone
            title: at_job
        output:
            rt: error code
        '''
        rt = ecode.FAILED
        
        try:
                
            i = ws_io.ws_input(['sid','dn','pw','email','mobile','username','pnumber','title'])
            if not i:
                raise ecode.WS_INPUT

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION

            uldap = getLdap()

            if uldap.is_has_pnumber(i['pnumber']):
                raise ecode.USER_EXIST
#             userdn = i['dn']+','+ org_config['ldap_base_dn']
            userdn = 'cn=%s,%s'%(str(i['username']),str(i['dn']))
            u = uldap.add_user(userdn,i['pw'],i['email'],i['mobile'],i['pnumber'],i['username'],i['title'])
            if not u:
                raise ecode.WRITE_LDAP_FAIL
            #+++20150728 for 预置策略和联系人，先建立user_db
            oudn=str(i['dn'])
            user_db.create(i['pnumber'], sha.new('12345678').hexdigest(), 0, str(i['username']),
                           i['email'], i['title'], oudn)
           
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('Ldap add user failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        #日志记录
        op_user=user
        op_type=operation.ACC_adduser.type
        op_desc=operation.ACC_adduser.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
            
    #}}}

class ShareUserInfo:
    def GET(self):
        user_db.share_user_info()


#+++20150331 +++20160223 修改
class LdapModUser:
    def POST(self):
        '''
        input:
            sid: session id
            key: primary key of user_db
            dn:  the oudn of moduser
            email: email
            mobile: Y/N  at_allow_use
            username:
            pnumber: telephone
            dev_id:dev_id
            title: at_job
        output:
            rt: error code
        '''
        rt = ecode.FAILED
        
        try:

            i = ws_io.ws_input(['sid','key','dn','email','mobile','username','pnumber','dev_id','title'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            admin = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not admin:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if admin !='admin':
                if not admin_db.is_has_admin(admin):
                    raise ecode.NOT_PERMISSION

            uldap = getLdap()

            user = user_db.get_user_info_by_key(i['key'])
            target_user = user_db.get_user_info_by_uid(i['pnumber'])

            if(len(user['devs'])>0):
                former_user_dev_id = user['devs'][0]
            else:
                former_user_dev_id = ""
            target_dev_id = i['dev_id']
            #更新用户信息（先删后增）
            #删除ldap中原用户

            # 设备的绑定关系管理逻辑
            if user['uid']==i['pnumber'] and former_user_dev_id!=target_dev_id:
                change_devs(i['pnumber'],former_user_dev_id,target_dev_id,i)
            elif user['uid']!=i['pnumber'] and former_user_dev_id==target_dev_id:
                change_uids(user['uid'],i['pnumber'],former_user_dev_id,i)
            elif user['uid']==i['pnumber'] and former_user_dev_id==target_dev_id:
                user_db.update_userinfo(i['key'],i['pnumber'],i['username'],i['dn'],i['email'],i['title'])
            else:
                change_uids(user['uid'],i['pnumber'],former_user_dev_id,i)
                change_devs(i['pnumber'],former_user_dev_id,target_dev_id,i)

            if user:
                pnumber = user['uid']
                rdata = uldap.get_user(pnumber)   #根据号码获取用户的
                logging.error("len is : %s.rdata is : %s",len(rdata),rdata)
                if len(rdata)!=0:
                    u = uldap.delete_user(rdata[0])
                    if not u:
                        raise ecode.DEL_LDAP_FAIL
                else:
                    raise ecode.USER_NOT_EXIST
                #新增新的用户
                userdn = 'cn=%s,%s'%(str(i['username']),str(i['dn']))
                pw='12345678'
                u = uldap.add_user(userdn,pw,i['email'],i['mobile'],i['pnumber'],i['username'],i['title'])
                if not u:
                    raise ecode.WRITE_LDAP_FAIL
                # ++++20150902 用户数据存在数据库中，现在分页显示也是从数据库中读取的数据，所以更改用户信息的时候也要修改数据库里的
                if(target_user): #如果目标用户存在直接互换,互换的时候需要删除重复索引
                    target_userdn = 'cn=%s,%s'%(str(target_user['username']),str(target_user['oudn']))
                    # 其中的修改项必须加str变为标准编码
                    uldap.modify_user(target_userdn,dict(telephoneNumber=[str(target_user['uid'])]),dict(telephoneNumber=[str(user['uid'])]))

                logging.warn("修改了用户信息，uid:%s",i['pnumber'])
            else:
                raise ecode.DB_OP
           
            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('Ldap mod user failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")


def change_uids(src,target,dev_id,i):
    """
    电话号码改变，设备不变,修改设备绑定号码，修改用户设备
    :param src: 原来的uid
    :param target: 目标uid
    :param dev_id: 原来uid绑定的dev_id
    :return:
    """
    try:
        src_user = user_db.get_user_info_by_uid(src)
        target_user = user_db.get_user_info_by_uid(target)
        target_user_devs = user_db.devs(target)
        if target_user:
            user_db.update_userinfo(target_user['key'],src,target_user['username'],target_user['oudn'],
                                            target_user['email'],target_user['title'])
        oudn = str(i['dn'])
        user_db.update_userinfo(i['key'],i['pnumber'],i['username'],oudn,i['email'],i['title'])
        # 修改用户绑定的设备
        if(dev_id==""):
            devs = []
        else:
            devs = [dev_id,]
        logging.error(src_user['key']+":"+str(devs))
        # 修改设备的当前用户
        if(dev_id!=""):
            dev_db.change_bind_uid(dev_id,target)
        if(target_user_devs!=[]):
            target_dev_id = target_user_devs[0]
            dev_db.change_bind_uid(target_dev_id,src)
    except Exception as e:
        logging.error(e.message)


def change_devs(uid,src,target,i):
    """
    电话号码不变，设备改变
    :param uid: 电话号码
    :param src: 原来的设备号
    :param target: 目标设备号
    :return:
    """
    try:
        user = user_db.get_user_info_by_uid(uid)
        target_uid = dev_db.get_cur_user(target)


        oudn = str(i['dn'])
        user_db.update_userinfo(i['key'],i['pnumber'],i['username'],oudn,i['email'],i['title'])

        if(target_uid==""):#设备未被占用
            if(target==""):
                user_db.change_bind_dev(user['key'],[])
            else:
                user_db.change_bind_dev(user['key'],[target,])
                dev_db.change_bind_uid(target,user['uid'])
            dev_db.change_bind_uid(src,"")
        else:
            target_user = user_db.get_user_info_by_uid(target_uid)
            user_db.change_bind_dev(user['key'],[target,])
            dev_db.change_bind_uid(target,uid)
            if(src==""):
                target_user_dev = []
            else:
                target_user_dev = [src,]
                dev_db.change_bind_uid(src,target_uid)
            user_db.change_bind_dev(target_user['key'],target_user_dev)
    except Exception as e:
        logging.error(e.message)


class CheckUserName:
    #{{{
    def GET(self):
        """
        input:
            sid:admin sid
            key:user key
            username: target username
            oudn:user target oudn
        output:
            rt: error ecode
        """
        rt = ecode.FAILED

        try:

            i = ws_io.ws_input(['sid','key','username','oudn'])
            if not i:
                raise ecode.WS_INPUT
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            admin = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not admin:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if admin != 'admin':
                if not admin_db.is_has_admin(admin):
                    raise ecode.NOT_PERMISSION

            user = user_db.get_user_info_by_key(i['key'])
            if not user: #用户不存在
                raise ecode.USER_NOT_EXIST
            else:
                former_username = user['username']
                former_oudn = user['oudn']
                target_username = i['username']
                target_oudn = i['oudn']
                if former_oudn==target_oudn and former_username==target_username: #用户姓名和群组都没有变，可以修改
                    rt = ecode.OK
                else:#其余的情况需要查看同名
                    if user_db.check_is_has_user({"username":i['username'],"oudn":i["oudn"]}):
                        rt = ecode.FAILED
                    else:
                        rt = ecode.OK

            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            error_info = str(traceback.format_exc()).replace("\n"," ")
        #日志记录
        op_user=session_db.user.get_user( i['sid'], web.ctx.ip)
        op_type=operation.CHANGE_user.type
        op_desc=operation.CHANGE_user.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}


class LdapDelUser:
    #{{{
    def POST(self):
        """
        input:
            sid:
            uids: [] 
        output:
            rt: error ecode
        """
        rt = ecode.FAILED
        
        try:
                
            i = ws_io.ws_input(['sid','uids'])
            if not i:
                raise ecode.WS_INPUT
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            
            # org_config = org.get_config()
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION

            uldap = getLdap()

            uids=[]
            #+++ 20150706 20151016加入选择全部的判断逻辑
            if(i.has_key("need_del_users")):
                need_del_users = json.loads(i['need_del_users'])
                select_uids = user_db.get_selected_uids(user)
                uids = [val for val in select_uids if val not in need_del_users]
            else:
                uids=json.loads(i['uids'])
            for uid in uids:
                if not uldap.get_user(uid):
                    logging.error('LDAP raise ecode.USER_NOT_EXIST')
            
                #+++ 20150706
                stra_ids=dev_db.get_strategy_ids(uid)
                if stra_ids=='no':
                    stra_ids=user_db.get_strategy_ids(uid)
                logging.warn("###stra_ids is : %s",stra_ids)
                if len(stra_ids)!=0 and stra_ids!='no':
                    for stra in stra_ids:
                        stra_id=stra["strategy_id"]
                        if strategy_db.is_has_strategy(stra_id):
                            strategy_db.del_user_of_users(stra_id, uid)
            
                if user_db.is_has_user(uid):
                    user_db.del_user(uid)
                    #+++ 20150706
                    contact_db.remove_contact(uid)
                    
                dev_id = dev_db.get_dev_id_by_curuser(uid)
                if dev_id != None:
                    dev_db.del_dev(dev_id)

                    # +++20150805 删除用户时清除用户轨迹信息
                    trace_db.del_trace_of_user(uid)
                    # +++20150831 删除用户时清除用户的工作日志
                    log_db.del_logs(uid,dev_id)
                    #+++ 20150909 将用户对应的sid信息删除
                    session_db.user.del_by_user(uid,dev_id)
             
                rdata = uldap.get_user(uid)
                if rdata:
                    u = uldap.delete_user(rdata[0])
                    if not u:
                        logging.error("raise ecode.DEL_LDAP_FAIL")
                        continue

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.exception('Ldap delete user failed'+ rdata[0])
            error_info = str(traceback.format_exc()).replace("\n"," ")
        #日志记录
        op_user=user
        op_type=operation.DEL_user.type
        op_desc=operation.DEL_user.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )

        return ws_io.ws_output(dict(rt=rt.eid,dn=rdata[0]),error_info)
    #}}}
    
class OrgLogo:
    #{{{
    def POST(self):
        """
        input:
            sid: session id
            logo_base64: img raw date base64 code
            img_type: [jpeg|png]
        output:
            rt: error code
        """
        rt = ecode.FAILED
        sid = ''

        try:
            i = ws_io.ws_input(['sid','img_type','logo_base64'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if user != 'admin':
                raise ecode.NOT_PERMISSION

            if not org.set_logo( i['logo_base64'], i['img_type']):
                raise ecode.SAVE_ORG_LOGO

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('set org ldap config')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)


    def GET(self):
        """
        input:
            sid: session id
        output:
            rt: error code
            logo_base64:
            img_type: 
        """
        rt = ecode.FAILED
        logo_base64 = ''
        img_type = ''

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION

            logo_base64, img_type = org.get_logo()

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get org ldap config info')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,logo_base64=logo_base64,img_type=img_type),error_info)
    #}}}


class AddAdmin:
    #{{{
    def POST(self):
        """
        input:
            sid:
            uid: user id
            loginType:logintype
            phonenumber:phonenumber
            email:
            pw: password
            ou: the range of uid's right
            contact_ous:admin contact ous
        output:
            rt: error code
        """
        rt = ecode.FAILED
       
        try:
            i = ws_io.ws_input(['uid','pw','sid','ou','loginType','phonenumber','email','contact_ous'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 
            
            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

#             org_config = org.get_config()
#             if user != org_config['admin']:
#                 raise ecode.NOT_PERMISSION
            
            if not admin_db.add_admin(i['uid'], sha.new(i['pw']).hexdigest(),i['ou'],i['email'],i['phonenumber'],json.loads(i['contact_ous'])):
                raise ecode.USER_EXIST
            rt = ecode.OK
            error_info=""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('org add admin')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        # 日志记录
        op_user=user
        op_type=operation.ADD_admin.type
        op_desc=operation.ADD_admin.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )
        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}


class ModAdmin:
    #{{{
    def POST(self):
        """
        修改操作员信息
        input:
            sid:
            uid: user id
            loginType:logintype
            phonenumber:phonenumber
            email:
            ou: the range of uid's right
            contact_ous:admin contact ous
        output:
            rt: error code
        """
        rt = ecode.FAILED
        
        try:
            i = ws_io.ws_input(['uid','sid','ou','loginType','phonenumber','email','contact_ous'])
            if not i:
                raise ecode.WS_INPUT

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

#             org_config = org.get_config()
#             if user != org_config['admin']:
#                 raise ecode.NOT_PERMISSION

            if not admin_db.mod_admin(i['uid'],i['ou'],i['email'],i['phonenumber'],json.loads(i['contact_ous'])):
                raise ecode.USER_EXIST
            rt = ecode.OK
            error_info=""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('org add admin')
            error_info = str(traceback.format_exc()).replace("\n"," ")
         # 日志记录
        op_user=user
        op_type=operation.CHANGE_admin.type
        op_desc=operation.CHANGE_admin.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

    #}}}
class DelAdmin:
    #{{{
    def POST(self):
        """
        input:
            sid:
            loginType:
            uid:user to delete
        output:
            rt: error ecode
        """
        rt = ecode.FAILED

        try:

            i = ws_io.ws_input(['sid','uid','loginType'])
            if not i:
                raise ecode.WS_INPUT

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if i['loginType'] !='master':
                raise ecode.NOT_PERMISSION

            if not admin_db.is_has_admin(i['uid']):
                raise ecode.USER_NOT_EXIST

            if not admin_db.del_admin(i['uid']):
                raise ecode.DB_OP

            rt = ecode.OK
            error_info=""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('delete admin failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        #日志记录
        op_user=user
        op_type=operation.DEL_admin.type
        op_desc=operation.DEL_admin.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )

        return ws_io.ws_output(dict(rt=rt.eid),error_info)


class AddUser:
    #{{{
    def POST(self):
        """
        input:
            sid:
            uid: user id
            pw: password
            email: email uid
            pnumber: telephone
            title:
            mobile: yes/no
            
            
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['uid','pw','sid','ou'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 
            
            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if user != 'admin':
                raise ecode.NOT_PERMISSION
            
            admin_db.add_admin(i['uid'], sha.new(i['pw']).hexdigest(),i['ou'])
            
            
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('org add admin')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    
    #}}}
    
 #轨迹信息存储和读取
class TraceLocInfo:
    #{{{
    #web端调用
    def GET(self):
        """
        input；
            sid:
            start:
            end:
            uid:
        output:
            rt:
            locinfo:{key:value,key:value}
        """
        
        rt = ecode.FAILED
        locinfo={}
        
        try:
            i = ws_io.ws_input(['uid','sid','start','end'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 
            
            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
            #将时间字符串转化为时间戳
            if str(i['start'])!='':
                starttime = time.mktime(time.strptime(str(i['start']), '%Y-%m-%d %H:%M'))
            else:
                starttime = ''
            if str(i['end'])!='':
                endtime = time.mktime(time.strptime(str(i['end']), '%Y-%m-%d %H:%M'))
            else:
                endtime = ''
            locinfo = trace_db.get(i['uid'],starttime,endtime)
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('TraceLocInfo get failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,locinfo=locinfo),error_info)

    #客户端调用
    def POST(self):
        """
        input:
            sid:
            key:
            value:
        output:
            rt:
        """
        rt=ecode.FAILED
        try:
            i = ws_io.ws_input(['sid','key','value'])
            if not i:
                raise ecode.WS_INPUT
            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            trace_db.set(user,i['key'],i['value'])
            rt=ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('TraceLocInfo post failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        
        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}

class SendCertification:
    #{{{
    #供加密模块调用
    def POST(self):
        """
        input:
            uid: 客户端采用dev_id向加密模块请求证书数据
            bid: business id
            encCertification:证书数据
            signCertification:签名证书
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['uid','bid','encCertification','signCertification'])
            if not i:
                raise ecode.WS_INPUT
            
            if not cert_db.add_cert(i['uid'],i['bid'],i['encCertification'],i['signCertification']):
                raise ecode.DB_OP
            logging.error("证书数据是：%s",i['signCertification'])
            
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('send certification')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}                       
            
class GetAllBaseStation:
    #web端调用
    def GET(self):
        """
        input；
            sid: session id
            baseSec: org name
        output:
            rt: error code
            baseStationInfo: {baseStationID1: baseStation1,baseStationID2: baseStation2,...}
        """
        
        rt = ecode.FAILED
        baseStationInfo={}
        
        try:
            i = ws_io.ws_input(['sid','baseSec'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 
            
            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            #baseSec编码转换
            baseSec=i['baseSec'].encode('utf-8')
            temps=baseStation.get(baseSec)

            for temp in temps:
                baseStationInfo[temp[0]]=temp[1]
            
            if baseStationInfo == {}:
                logging.error('get baseStationInfo failed')
        
            rt = ecode.OK
            error_info = ""
            
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('baseStationInfo get failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        
        return ws_io.ws_output(dict(rt=rt.eid,baseStationInfo=baseStationInfo),error_info)

#+++ 20150506 
#获取策略快照列表
class GetAllPreStra:
    #web端调用
    def GET(self):
        """
        input；
            sid: session id
            types: fastStra
        output:
            rt: error code
            preStraList: [desc1,desc2,...]
        """
        
        rt = ecode.FAILED
        preStraList=[]
        
        try:
            i = ws_io.ws_input(['sid','types'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 
            
            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            preStra=strategy_db.get_pre_stra_list(i['types'])
            preStraList=json.dumps(preStra)
            
            rt = ecode.OK
            error_info = ""
            
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('preStraList get failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        
        return ws_io.ws_output(dict(rt=rt.eid,preStraList=preStraList),error_info)

#获取预置策略
class GetStrategyByDesc:
    def GET(self):
        """
        input:
          sid:
          strategy_id:
        output:
          rt:error code
          strategy:{...}
        """
        rt = ecode.FAILED
        strategy = {}
        try:
            i = ws_io.ws_input(['sid','desc'])
            if not i:
                raise ecode.WS_INPUT
            
            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            
            # org_config = org.get_config()
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
                         
            desc = i['desc']
            strategy=strategy_db.get_strategy_by_desc(desc)
            
            if admin_db.is_has_admin(user):
                ou = admin_db.get_ou_friendly_name_by_uid(user)
                temp=[]
                rg = re.compile(r'.*'+ou+'.*')
                for us in strategy['users']:
                    if rg.match(us['name']):
                        temp.append(us)
                strategy['users'] = temp
           
            rt = ecode.OK
            error_info = ""
            
            
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get strategy by desc')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,strategy=strategy),error_info)

#设置预置策略
class SendPreStrategy:
    #{{{
    def POST(self):
        """
        input
             id:strategy id
             sid
                                开始时间 start
                                结束时间 end
                                作用经度 longitude 
                               作用维度 latitude
                                作用半径 radius
                                策略作用基站 baseStationID
                               范围描述  desc
                                摄像头 camera
                                蓝牙 bluetooth
             Wifi wifi
                                录音 tape
             gps gps
                                移动数据  mobiledata
            USB连接  usb_connect
            USB调试  usb_debug
                              作用人 users:{}
                             作用人描述userdesc:
        output
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','id','types','users','userdesc','start','end','lon','lat','desc','radius','baseStationID','camera','bluetooth','wifi','tape','gps','mobiledata','usb_connect','usb_debug'])
            if not i:
                raise ecode.WS_INPUT
            strategy = {}
            
            if str(i['start'])!='':
                strategy['start'] = str(i['start'])
                start = time.mktime(time.strptime(str(i['start']), '%Y-%m-%d %H:%M'))
            else:
                start = time.time()
                strategy['start'] = time.strftime('%Y-%m-%d %H:%M',time.localtime(start))#获取当前时间
            #如果前台传来时的时间是空的，那么开始时间取为当前时间，否则取为前台所选时间
            if str(i['end'])!='':
                strategy['end'] = str(i['end'])
            else:
                end = start+30*24*3600
                strategy['end'] = time.strftime('%Y-%m-%d %H:%M',time.localtime(end))
            """
            1、开始空，结束空 -----开始当前，结束当前加30天
            2、开始空，结束非空----开始当前，结束用传来的（已经默认前台传来的结束数据比当前时间晚）
            3、开始非空，结束空----开始用传来的，结束传来的加30天
            4、开始非空，结束非空--都用传来的
            """ 
            if str(i['lon'])=='':
                strategy['lon'] = '116.220686'
            else:
                strategy['lon']=str(i['lon'])
            if str(i['lat'])=='':
                strategy['lat'] = '39.979471'
            else:
                strategy['lat']=str(i['lat'])
            if str(i['radius'])=='':
                strategy['radius']='100'
            else:
                strategy['radius']=str(i['radius'])
            strategy['baseStationID']=i['baseStationID']
            strategy['desc'] = i['desc']
            strategy['camera'] = str(i['camera'])
            strategy['bluetooth'] = str(i['bluetooth'])
            strategy['wifi'] = str(i['wifi'])
            strategy['tape'] = str(i['tape'])
            strategy['gps'] = str(i['gps'])
            strategy['mobiledata'] = str(i['mobiledata'])
            strategy['usb_connect'] = str(i['usb_connect'])
            strategy['usb_debug'] = str(i['usb_debug'])
            strategy['strategy_id']=i['id']
            strategy['types']=i['types']
            strategy['force']=i['force']
            users=json.loads(i['users'])
            userdesc=json.loads(i['userdesc'])
            
            
            user = session_db.user.get_user( i['sid'], str(web.ctx.ip))
            if not user:
                raise ecode.NOT_LOGIN
            
            # org_config = org.get_config()
            
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
                else:
                    ouAuth = admin_db.get_ou_by_uid(user)
                    strategy['auth'] = ouAuth
            else:
                # +++20151023 在策略中加入一个字段来记录下发此策略的权限
                strategy['auth'] = "admin"
            #将策略ID写进dev-db中
            #将策略写入数据库strategy_db
            strategy_db.new_strategy(strategy,users,userdesc)

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            strategy_db.del_strategy(i['id'])
            logging.error('send strategy')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

#+++ 20150507
#删除预置策略
class DelPreStra:
    #web端调用
    def GET(self):
        """
        input；
            sid: session id
            desc: desc
        output:
            rt: error code
        """
        
        rt = ecode.FAILED
        
        try:
            i = ws_io.ws_input(['sid','desc'])
            if not i:
                raise ecode.WS_INPUT
            
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP 
            
            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            strategy_db.del_pre_stra(i['desc'])
            
            rt = ecode.OK
            error_info = ""
            
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('del pre strategy failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

#+++ 20150601
#用户信息批量导入excel->ldap
class UpldapByexcel:
    #web调用
    def POST(self):
        """
        input:
            excel_path:
        output:
            rt: error code
            row: error row
        """
        rt = ecode.FAILED
        error_info = ""

        try:
            i = ws_io.ws_input(['excel_path'])
            logging.error('path=%s',i)
            if not i:
                raise ecode.WS_INPUT
            ep = i['excel_path']
            logging.error("path=%s",ep)  
            
            #copy first
            aa=time.time()
            ab=int(aa)
            ac=str(ab)
            excelfile = "%s.xls"%(ac)

            # copy excel file to web download dir.
            dest_file=os.path.join( config.get('app_download_dir'),'exceltoldap',excelfile)   #直接复制到远程文件夹中
            
            #just for hisense
#             shutil.copy2(ep, dest_file)
            
            #远程传输到数据服务器
            back_host=config.get('redis_host')   #都存在数据库服务器，同redis地址
            #rt_c=commands.getstatusoutput( 'scp %s %s:%s'%(ep,back_host,dest_file))
            #logging.error('add: scp %s %s:%s!%s',ep,back_host,dest_file,rt_c)
            #if rt_c[0]!=0:
                #raise ecode.DB_OP
                      
            xlsfile=xlrd.open_workbook(ep)
            try:
                mysheet=xlsfile.sheet_by_name("Sheet1")
            except:
                logging.error("no sheet in %s named Sheet1")
                return
            logging.error("%d rows, %dcols"%(mysheet.nrows,mysheet.ncols))
            a=''
            a=mysheet.cell(0,10).value
            logging.error('a=%s',a)
            org_config = org.get_config()
            uldap = getLdap()
            for row in range(1,mysheet.nrows):
                userinfo={}
                if mysheet.cell(row,0).value != '':
                    userinfo['username']=(mysheet.cell(row,0).value).replace(' ','')
                    userinfo['email']=(mysheet.cell(row,1).value).replace(' ','')
                    userinfo['pnumber']=(str(int(mysheet.cell(row,2).value))).replace(' ','')
                    if mysheet.cell(row,3).value == '' or mysheet.cell(row,3).value == a:
                        if mysheet.cell(row,4).value == '' or mysheet.cell(row,4).value == a:
                            userinfo['title']='无'
                        else:
                            userinfo['title']=(mysheet.cell(row,4).value).replace(' ','')
                    else:
                        if mysheet.cell(row,4).value == '' or mysheet.cell(row,4).value == a:
                            userinfo['title']=(mysheet.cell(row,3).value).replace(' ','')
                        else:
                            userinfo['title']=(mysheet.cell(row,3).value).replace(' ','')+'/'+(mysheet.cell(row,4).value).replace(' ','')
                    userinfo['pw']='12345678'
                    userinfo['mobile']='Y'
                    if mysheet.cell(row,7).value == '':
                        if mysheet.cell(row,6).value == '':
                            userinfo['userdn']='ou='+(mysheet.cell(row,5).value).replace(' ','')
                        else:
                            userinfo['userdn']='ou='+(mysheet.cell(row,6).value).replace(' ','')+',ou='+(mysheet.cell(row,5).value).replace(' ','')
                    else:
                        userinfo['userdn']='ou='+(mysheet.cell(row,7).value).replace(' ','')+',ou='+(mysheet.cell(row,6).value).replace(' ','')+',ou='+(mysheet.cell(row,5).value).replace(' ','')

                    if uldap.is_has_pnumber(userinfo['pnumber']):
                        if user_db.is_has_user(userinfo['pnumber']):
                            logging.error('ecode.USER_EXIST')
                            continue
                        else:
                            oudn=str(userinfo['userdn'])+","+org_config['ldap_base_dn']
                            user_db.create(userinfo['pnumber'], sha.new(userinfo['pw']).hexdigest(), 0, str(userinfo['username']),
                                           userinfo['email'], userinfo['title'], oudn)
                    userdn = 'cn=%s,%s,'%(str(userinfo['username']),str(userinfo['userdn']))+org_config['ldap_base_dn']
                    u = uldap.add_user(userdn,userinfo['pw'],userinfo['email'],userinfo['mobile'],userinfo['pnumber'],userinfo['username'],userinfo['title'])
                    if not u:
                        rt = ecode.WRITE_LDAP_FAIL
                        error_info = "add user error"
                        logging.error('出错了，row=%s',str(row+1))
                        return ws_io.ws_output(dict(rt=rt.eid,row=row+1))
                    logging.error('写入结果u=%s',u)
                    #+++20150706 for 预置策略和联系人，先建立user_db
                    oudn=str(userinfo['userdn'])+","+org_config['ldap_base_dn']
                    user_db.create(userinfo['pnumber'], sha.new(userinfo['pw']).hexdigest(), 0, str(userinfo['username']),
                                   userinfo['email'], userinfo['title'], oudn)

            for key in userinfo.keys():
                logging.error('key=%s, value=%s' %(key,userinfo[key]))
            rt = ecode.OK
            commands.getstatusoutput( 'rm -f %s'%(ep))   #删除临时文件
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('Ldap add user failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

#++++0722 for user export
class GetAllUsers:
    def GET(self):
        users = []
        rt = ecode.FAILED
        try:
            uldap = getLdap()
            ldap_users = uldap.get_all_users()
            logging.debug("ldap_users"+str(len(ldap_users)))
            for item in ldap_users:
                dn = item[0]
                phone = item[1]['telephoneNumber'][0]
                name = item[1]['cn'][0]
                # title = item[1]['title'][0]
                if item[1].get('mail')!=None:
                    mail = item[1]['mail'][0]
                else:
                    mail = ""

                if user_db.is_has_user(phone):
                    department = getDepartmentOfUser(dn)
                    dev_id = user_db.devs(phone)
                    if len(dev_id)>0:
                       IMEI=dev_id[0]
                    else:
                        IMEI=""
                else:
                    IMEI=""
                users.append({'name':name,'mail':mail,'phone':phone,'title':'干部','department':department,'IMEI':IMEI})
                logging.error("users-len:"+str(len(users)))
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('Get all users failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,users=users),error_info)

def getDepartmentOfUser(dn):
    department = ''
    if dn=='':
        return department
    else:
        items = dn.split(',')
        for item in items:
            if item[0:2]=='ou':
                department = department + item[3:] + '/'
        lenth = len(department)
        department = department[0:lenth-1]
        return department

# ++++20150728 for get one page users
class ChangeSelectedUsers:
    def POST(self):
        """
        input:
            sid
            type:add/del
            users:用户或群组主键
            node:节点类型
            size:页面大小
        output:
            rt: error code
            selected_count:选中用户的总数
            users:[] for first page
        """
        rt = ecode.FAILED
        user_list = []
        selected_count = 0
        try:
            i = ws_io.ws_input(['sid','type','users',"node","size"])
            if not i:
                #20160923临时注释
                raise ecode.WS_INPUT
            sid = i['sid']
            user = session_db.user.get_user( sid, web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            #加入一步sid验证
            type = i['type']
            users = i['users']
            nodeType = i['node']
            size = i['size']
            logging.warn("change type %s,change node %s",type,users)
            #获取此次用户操作类型
            operation = -1
            if type=="add" or type=="contact add":
                operation = 1
            elif type=="del" or type=="contact del":
                operation = 0
            else:
                raise ecode.FAILED
            # 如果是contact节点，用户数据库中存储用户名称修改
            if type.find("contact")>=0:
                user = user + "_contact"

            #  获取节点相关用户数据
            if nodeType=="user":
                #将用户写入到缓存表，或者将用户表中的选中标志位置1
                user_db.user_checked(users,operation,user)
                #获取当前页数据返回
            elif nodeType=="ou":
                time1 = time.time()
                logging.warn("开始写的时间点"+str(time1))
                user_db.set_ou_users_checked(users,operation,user)
                time2 = time.time()
                logging.warn("写完的时间点"+str(time2)+"      同时开始获取被选中的用户数")
            #获取当前被选中的用户总数

            selected_count = user_db.get_selected_count(user)
            time3 = time.time()
            logging.warn("选择完用户数的时间点，同时开始获取第一页"+str(time3))
            #每次获取第一页数据返回，需要前台配合修改
            user_list = user_db.get_selected_page_users('1',size,"",user,[])
            time4 = time.time()
            logging.warn("获取完第一页的时间点"+str(time4))
            rt = ecode.OK
            error_info=""
        except Exception as e:
            logging.error('Change selected users failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,users=user_list,selected_count=selected_count),error_info)

class ChangeSelectedUsersUidHide:
    def POST(self):
        """
        input:
            sid
            type:add/del
            users:用户或群组主键
            rootdn:管理群组
            node:节点类型
            size:页面大小
        output:
            rt: error code
            selected_count:选中用户的总数
            users:[] for first page
        """
        rt = ecode.FAILED
        user_list = []
        selected_count = 0
        try:
            i = ws_io.ws_input(['sid','type','users','rootdn',"node","size"])
            if not i:
                raise ecode.WS_INPUT
            sid = i['sid']
            user = session_db.user.get_user( sid, web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            #加入一步sid验证
            type = i['type']
            users = i['users']
            rootdn = i['rootdn']
            nodeType = i['node']
            size = i['size']
            logging.warn("change type %s,change node %s",type,users)
            #获取此次用户操作类型
            operation = -1
            if type=="add" or type=="contact add":
                operation = 1
            elif type=="del" or type=="contact del":
                operation = 0
            else:
                raise ecode.FAILED
            # 如果是contact节点，用户数据库中存储用户名称修改
            if type.find("contact")>=0:
                user = user + "_contact"

            #  获取节点相关用户数据
            if nodeType=="user":
                #将用户写入到缓存表，或者将用户表中的选中标志位置1
                user_db.user_checked_uid_hid(users,operation,user)
                #获取当前页数据返回
            elif nodeType=="ou":
                time1 = time.time()
                logging.warn("开始写的时间点"+str(time1))
                user_db.set_ou_users_checked(users,operation,user)
                time2 = time.time()
                logging.warn("写完的时间点"+str(time2)+"      同时开始获取被选中的用户数")
            #获取当前被选中的用户总数

            selected_count = user_db.get_selected_count(user)
            time3 = time.time()
            logging.warn("选择完用户数的时间点，同时开始获取第一页"+str(time3))
            #每次获取第一页数据返回，需要前台配合修改
            # if rootdn in users :
            #     user_list = user_db.get_selected_page_users('1',size,"",user,[])
            # else :
            user_list = user_db.get_selected_page_users_uid_hide('1',size,"",user,[],rootdn)
            time4 = time.time()
            logging.warn("获取完第一页的时间点"+str(time4))
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            logging.error('Change selected users failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,users=user_list,selected_count=selected_count),error_info)

# ++++20150728 for change selected user not return users
class ChangeSelectedNode:
    def POST(self):
        """
        input:
            sid
            type:add/del
            users:用户或群组主键
            node:节点类型
        output:
            rt: error code
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['sid','type','users',"node"])
            if not i:
                raise ecode.WS_INPUT
            sid = i['sid']
            user = session_db.user.get_user( sid, web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            #加入一步sid验证
            type = i['type']
            users = i['users']
            nodeType = i['node']
            logging.warn("change type %s,change node %s",type,users)
            #获取此次用户操作类型
            operation = -1
            if type=="add":
                operation = 1
            elif type=="del":
                operation = 0
            else:
                raise ecode.FAILED

            #  获取节点相关用户数据
            if nodeType=="user":
                #将用户写入到缓存表，或者将用户表中的选中标志位置1
                user_db.user_checked(users,operation,user)
                #获取当前页数据返回
            elif nodeType=="ou":
                user_db.set_ou_users_checked(users,operation,user)
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            logging.error('Change selected users failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)

#+++20151027 for recover strategy users
class RecoverStraUsers:
    def GET(self):
        """
            input:
                sid:sid
                strategy_id:
            output:
                rt:
                users:策略中受管控的用户，格式{ous:[{oudn,ouname:,ous,users}],users:[]}
        """
        users = []
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(["sid","strategy_id"])
            if not i:
                raise ecode.WS_INPUT
            sid = i['sid']
            user = session_db.user.get_user( sid, web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # 这个策略肯定是这个管理员管控范围内的，从这个管理员的oudn进行根节点的匹配
            strategy_id = i['strategy_id']
            strategy = strategy_db.get_strategy_by_id(strategy_id)
            ous = strategy['users']
            for item in ous:
                oudn = item['name']#先要获取所有的群组，然后将受管控的群组用户信息获取到

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            logging.error('get one page users failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,users=users),error_info)


# ++++20150728 for get one page users
class GetOnePageUsers:
    def GET(self):
        """
        input:
            sid:
            page:num/next/last
            size:
            [last_user]:参考用户,此项可选，用于整合跳到某一页的情况
            sort_keys:[{name:,order:}]  就是排序键的一个集合，如果为空则是默认的情况，有值的话取值并按相应的顺序排序
        output:
            rt:
            users:[{}]
        """
        users = []
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(["sid","page","size"])
            if not i:
                raise ecode.WS_INPUT
            sid = i['sid']
            user = session_db.user.get_user( sid, web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            page = i['page']
            size = i['size']
            last_user = ""
            if i.has_key('last_user'):
                last_user = i['last_user']
            if i.has_key('sort_keys'):
                sort_keys = json.loads(i['sort_keys'])
            else:
                sort_keys = []

            if i.has_key('contact'):
                user = user+"_contact"

            # 根据前台是否有参考用户,当前无参考用户的方法使用skip实现，效率不太好，待优化
            users = user_db.get_selected_page_users(page,size,last_user,user,sort_keys)
            rt = ecode.OK
            error_info=""
        except Exception as e:
            logging.error('get one page users failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,users=users),error_info)

class GetOnePageUsersUidHide:
    def GET(self):
        """
        input:
            sid:
            page:num/next/last
            size:
            [last_user]:参考用户,此项可选，用于整合跳到某一页的情况
            sort_keys:[{name:,order:}]  就是排序键的一个集合，如果为空则是默认的情况，有值的话取值并按相应的顺序排序
        output:
            rt:
            users:[{}]
        """
        users = []
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(["sid","page","size"])
            if not i:
                raise ecode.WS_INPUT
            sid = i['sid']
            user = session_db.user.get_user( sid, web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            rootdn = admin_db.get_one_page_users_uid_hide(user)
            page = i['page']
            size = i['size']
            last_user = ""
            if i.has_key('last_user'):
                last_user = i['last_user']
            if i.has_key('sort_keys'):
                sort_keys = json.loads(i['sort_keys'])
            else:
                sort_keys = []

            if i.has_key('contact'):
                user = user+"_contact"

            # 根据前台是否有参考用户,当前无参考用户的方法使用skip实现，效率不太好，待优化
            users = user_db.get_selected_page_users_uid_hide(page,size,last_user,user,sort_keys,rootdn)
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            logging.error('get one page users failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,users=users),error_info)

# +++20150828 for check admin existence
class IsHasAdmin:
    def POST(self):
        """
        input:
            sid:
            adminID:
        output:
            rt:
            result
        """
        rt = ecode.FAILED
        result = 0
        try:
            i = ws_io.ws_input(['sid','adminID'])
            if not i:
                raise ecode.WS_INPUT

            sid = i['sid']
            user = session_db.user.get_user( sid, web.ctx.ip)
            # org_config = org.get_config()
            if not user:
                raise ecode.NOT_LOGIN

            adminID = i['adminID']
            if adminID=='admin' or admin_db.is_has_admin(adminID):
                result = 1
                logging.warn("admin exist")
            else:
                logging.warn("admin not exist,please go on")

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            logging.error('check adminID existence failed, adminID %s',adminID)
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,result=result),error_info)
# +++ 20150828 check admin old psw
class CheckOldPsw:
    def GET(self):
        """
        input:
            sid:
            psw:
        output:
            rt:
            result;
        """
        rt = ecode.FAILED
        result = 0
        try:
            i = ws_io.ws_input(['sid','psw'])
            if not i:
                raise ecode.WS_INPUT
            sid = i['sid']
            user = session_db.user.get_user(sid,web.ctx.ip)
            # org_config = org.get_config()
            if not user:
                raise ecode.NOT_LOGIN
            psw = i['psw']
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
                else:
                    if admin_db.check_pw(user,sha.new(psw).hexdigest()):
                        result = 1
            else:
                if admin_db.check_pw(user,sha.new(psw).hexdigest()):
                    result = 1
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            logging.error('check old psw failed,user is %s',user)
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,result=result),error_info)

class CheckIsHasUser:
    def GET(self):
        """
        input:
            sid:sid
            uid:pnumber
        output:
            rt:
            result:1 userexist,0 user not exist
        """
        rt = ecode.FAILED
        result = 0
        try:
            i = ws_io.ws_input(['sid','uid'])
            if not i:
                raise ecode.WS_INPUT
            sid = i['sid']
            user = session_db.user.get_user(sid,web.ctx.ip)
            # org_config = org.get_config()
            if user!='admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
            uid = i['uid']
            if user_db.is_has_user(uid):
                logging.warn("该号码已被注册")
                result = 1
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            logging.error("check is has user failed,uid is %s",uid)
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,result=result),error_info)


# +++20160726 查看是否存在用户号码
class CheckUidExist:
    def GET(self):
        """
        input:
            uid
        output:
            rt:1表示用户存在，0表示用户不存在
        """
        rt = ecode.OK
        try:
            i = ws_io.ws_input(['uid'])
            if not i:
                raise ecode.WS_INPUT
            uid = i['uid']
            if user_db.is_has_user(uid):
                logging.warn("该号码已被注册")
                rt = ecode.FAILED
            error_info = ""
        except Exception as e:
            logging.error("check is has user failed,uid is %s",uid)
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)

# +++20160724 查看是否存在重名用户
class CheckIsHasUsername:
    def GET(self):
        """
        input:
            sid:管理员的sid
            oudn:给用户选定的用户群组
            username:用户的姓名
        output:
            rt:0代表存在同名用户，默认不存在
        """
        rt = ecode.FAILED
        result = 0
        try:
            i = ws_io.ws_input(['sid','oudn','username'])
            if not i:
                raise ecode.WS_INPUT

            sid = i['sid']
            admin = session_db.user.get_user(sid,web.ctx.ip)
            # org_config = org.get_config()
            if admin!='admin':
                if not admin_db.is_has_admin(admin):
                    raise ecode.NOT_PERMISSION
            oudn = i['oudn']
            username = i['username']
            uldap = getLdap()
            result = uldap.oudn_has_username(username,oudn)
            if result:
                rt = ecode.OK
            error_info = ""
        except Exception as e:
            logging.error(e.message)
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)


# +++20160219 根据uid获取用户信息
class GetUserByUid:
    def GET(self):
        """
        input:
            sid:sid
            uid:pnumber
        output:
            rt:
            user:{}
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['sid','uid'])
            if not i:
                raise ecode.WS_INPUT
            sid = i['sid']
            admin = session_db.user.get_user(sid,web.ctx.ip)
            # org_config = org.get_config()
            if admin!='admin':
                if not admin_db.is_has_admin(admin):
                    raise ecode.NOT_PERMISSION
            uid = i['uid']
            user = user_db.get_user_info_by_uid(uid)
            print str(user)
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            logging.error("check is has user failed,uid is %s",uid)
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,user=user),error_info)

# +++20160222 根据dev_id获取设备信息
class GetDevById:
    def GET(self):
        """
        input:
            sid
            dev_id
        output:
            rt:
            dev:{}
        """
        rt = ecode.FAILED
        dev = None
        try:
            i = ws_io.ws_input(['sid','dev_id'])
            if not i:
                raise ecode.WS_INPUT
            sid = i['sid']
            admin = session_db.user.get_user(sid,web.ctx.ip)
            # org_config = org.get_config()
            if admin!='admin':
                if not admin_db.is_has_admin(admin):
                    raise ecode.NOT_PERMISSION
            dev_id = i['dev_id']
            dev = dev_db.get_dev_by_id(dev_id)
            print str(dev)
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            logging.error("get dev by id failed,dev_id is %s",i['dev_id'])
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,dev=dev),error_info)

# +++20151110 加入获取用户日志的总数
class GetUserLogCount:
    def GET(self):
        """
        input:
            sid
            admin：检查的管理员
            action: 获取的日志类型，如果日志类型为all，则获取所有类型的日志
            start_time:查询开始时间
            end_time:查询结束时间
        output:
            rt:
            logs_count:
        """
        rt = ecode.FAILED
        logs_count = 0
        try:
            i = ws_io.ws_input(['sid','admin','action','start_time','end_time'])
            if not i:
                raise ecode.WS_INPUT
            sid = i['sid']
            user = session_db.user.get_user(sid,web.ctx.ip)
            # org_config = org.get_config()
            if user!='admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_LOGIN
            # +++20151109 加入检验管理员权限的逻辑,admin可以查看所有管理员的操作，其他管理员可以查看同级管理员的操作
            admin = i['admin']
            if(admin==""):
                if(user=="admin" or admin_db.get_ou_by_uid(user)==ldap_base_dn):
                    logs_count = log_web_db.get_log_count("all",i['action'],i['start_time'],i['end_time'])
                else:
                    logs_count = log_web_db.get_log_count(user,i['action'],i['start_time'],i['end_time'])
            else:
                if(user=="admin" or admin_db.get_ou_by_uid(user)==ldap_base_dn):
                     logs_count = log_web_db.get_log_count(admin,i['action'],i['start_time'],i['end_time'])
                else:
                    if(admin_db.get_ou_by_uid(user)!=admin_db.get_ou_by_uid(admin)):
                        raise ecode.NOT_PERMISSION
                    else:
                        logs_count = log_web_db.get_log_count(admin,i['action'],i['start_time'],i['end_time'])
            rt=ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error("get admin send contacts log count failed,admin is %s",user)
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,logs_count=logs_count),error_info)

class GetWebLogs:
    def GET(self):
        """
        input:
            sid
            admin：检查的管理员
            action:获取的action类型
            start_time:查询开始时间
            end_time:查询结束时间
            size:每页的数量
            page_index:
        output:
            rt
            [{"uid":,管理员
            "time":,操作时间
            "users":所有用户
                {
                    "uid":,用户的uid
                    "result":用户取没取通讯录
                },
            contacts:,result接口执行结果
            }]
        """
        rt = ecode.FAILED
        logs = []
        try:
            i = ws_io.ws_input(['sid','admin','action','start_time','end_time','size','page_index'])
            if not i:
                raise ecode.WS_INPUT
            sid = i['sid']
            user = session_db.user.get_user(sid,web.ctx.ip)
            # org_config = org.get_config()
            if user!='admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_LOGIN
            # +++20151109 加入检验管理员权限的逻辑,admin可以查看所有管理员的操作，其他管理员可以查看同级管理员的操作
            page_index = i['page_index']
            if(len(page_index)<=0):
                raise ecode.DATA_LEN_ERROR
            admin = i['admin']
            if(admin==""):
                if(user=="admin" or admin_db.get_ou_by_uid(user)==ldap_base_dn):
                    logs = log_web_db.get_logs("all",i['action'],i['start_time'],i['end_time'],int(i['size']),int(page_index))
                else:
                    logs = log_web_db.get_logs(user,i['action'],i['start_time'],i['end_time'],int(i['size']),int(page_index))
            else:
                if(user=="admin" or admin_db.get_ou_by_uid(user)==ldap_base_dn):
                    logs = log_web_db.get_logs(admin,i['action'],i['start_time'],i['end_time'],int(i['size']),int(page_index))
                else:
                    if(admin_db.get_ou_by_uid(user)!=admin_db.get_ou_by_uid(admin)):
                        raise ecode.NOT_PERMISSION
                    else:
                        logs = log_web_db.get_logs(admin,i['action'],i['start_time'],i['end_time'],int(i['size']),int(page_index))
            # +++20151127 按照以上查询条件获取日志之后，根据日志的类型处理日志内容
            for item in logs:
                action = item['action']
                if action=="send contacts":
                    operate_contacts_log(item)
                elif action=="amdinlogin":
                    operate_login_log(item)
            rt=ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error(e.message)
            logging.error("get admin send contacts log failed,admin is %s",user)
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,logs=logs),error_info)

# +++20151127 加入专门处理login内容的函数，返回格式化的登录信息
def operate_login_log(item):
    return item
# +++20151127 加入一个专门处理contacts内容的函数，返回格式化的联系人日志信息
def operate_contacts_log(item):
    users = item['users']
    log_info = item['info']
    for send_user in users:
        if(send_user):
            send_user_id = send_user['uid']
            count = user_db.get_contacs_count(send_user_id)
            if(count==0):
                send_user['result']=0
            else:
                send_user['result']=1
        else:
            continue
    count = get_contact_log_info_count(log_info)
    base_dn = item['info']['oudn']
    muti_son = 0
    if base_dn==ldap_base_dn:
        second_ous = item['info']['ous']
        muti_son = len(second_ous)
        if muti_son==1:
            base_dn = second_ous[0]['oudn']
    item['info'] = {}
    item['info'] = {'oudn':base_dn,'count':count,"muti_son":muti_son}

global ou_count
def get_contact_log_info_count(log_info):
    ous = log_info['ous']
    users = log_info['users']
    count = 0
    count = count+len(users)
    if(len(ous)>0):
        for item in ous:
            count=count+get_contact_log_info_count(item)
    return count

class GetLogContacts:
    def GET(self):
        """
        input:
            sid:
            amdin:
            time:
            action:
            oudn:现在正在查找的oudn,这个需要验证一下是否为当前管理员权限下的群组
        output:
            rt:
            {
                oudn:
                users:[]
                ous:[只包含名称，不包含群组下的内容]
            }获取这一级节点下的所有群组名称和用户
        """
        log_contacts = {}
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(["sid","admin","time","action","oudn"])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user(i['sid'],web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            log_info = log_web_db.get_log_info(i['admin'],i['time'],i['action'])
            log_contacts = get_log_contacts(log_info,i['oudn'])
            user_count = get_contact_log_info_count(log_contacts)
            log_contacts['count'] = user_count
            son_ous = log_contacts['ous']
            for item in son_ous:
                item_count = get_contact_log_info_count(item)
                item['ous'] = []
                item['users'] = []
                item['count'] = item_count
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error("get log contacts failed")
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,log_contacts=log_contacts),error_info)


def get_log_contacts(log_info,target_oudn):
    if log_info==None:
        return None
    else:
        oudn = log_info['oudn']
        if oudn==target_oudn:
            return log_info
        else:
            son_log_infos = log_info['ous']
            for son_log_info in son_log_infos:
                son_log_info_contacts = get_log_contacts(son_log_info,target_oudn)
                if son_log_info_contacts!=None:
                    return son_log_info_contacts
                else:
                    continue

# +++20151118 分级加载下发日志作用用户，这个可迁移，以后的日志模块也可以用
class GetLogControlUsers:
    def GET(self):
        """
        input:能够唯一定位到一条日志信息
            sid:
            admin:
            time:
            action:
            oudn:根据这个oudn获取当前的树
        output:
            rt:
            result:{
                oudn:
                ous:[{oudn:count:}]
                users:[{username: uid}]
                count:
            }

        """
        rt = ecode.FAILED
        result = {}
        try:
            i = ws_io.ws_input(["sid","admin","time","action"])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user(i['sid'],web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            if not i.has_key("oudn"):
                i['oudn'] = admin_db.get_ou_by_uid(user)
            log = log_web_db.get_log(i['admin'],i['time'],i['action'])
            if log!=None:
                users = log['users']
                format_users = getFormatUsers(users)
                result['ous'] = []
                result['users'] = []
                result['oudn'] = i['oudn']
                ounames = []
                for group in format_users:
                    if(group['oudn']==i['oudn']):
                        for group_item in group['users']:
                            result['users'].append(group_item)
                    elif(group['oudn'].find(i['oudn'])>=0):
                        if(len(group['oudn'].split(","))==(len(i['oudn'].split(","))+1)):
                            group['count'] = get_ou_user_count(group['oudn'],format_users)
                            result['ous'].append(group)
                            if group['oudn'] not in ounames:
                                ounames.append(group['oudn'])
                        elif(len(group['oudn'].split(","))>(len(i['oudn'].split(","))+1)):
                            un_leaf_group_name = ",".join(group['oudn'].split(",")[-(len(i['oudn'].split(","))+1):])
                            if un_leaf_group_name not in ounames:
                                un_leaf_group = {'oudn':un_leaf_group_name,'count':get_ou_user_count(un_leaf_group_name,format_users)}
                                result['ous'].append(un_leaf_group)
                                ounames.append(un_leaf_group_name)

                result['users'] = sort_users_by_status(result['users'])
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error("get log control user failed")
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,result=result),error_info)

def get_ou_user_count(oudn,format_users):
    count = 0
    for group in format_users:
        if group['oudn'].find(oudn)>=0:
            count+= len(group['users'])
    return count

def sort_users_by_status(users):
    ok_users = []
    need_fetch_users = []
    for item in users:
        uid = item['uid']
        count = user_db.get_contacs_count(uid)
        if(count==0):
            item['result'] = 0
            ok_users.append(item)
        else:
            item['result'] = 1
            need_fetch_users.append(item)
    return ok_users+need_fetch_users

#+++20150801 获取格式化的选择用户
def getFormatUsers(selected_users):
    if len(selected_users)==0:
        return []
    groups = []
    i=0
    while i<len(selected_users):
        group = {"oudn":'','users':[]}
        group['oudn'] = selected_users[i]['oudn']
        j=i
        while j<len(selected_users):
            if(selected_users[j]['oudn']==selected_users[i]['oudn']):
                group['users'].append({'username':selected_users[j]['username'],'uid':selected_users[j]['uid']})
            else:
                i=j
                groups.append(group)
                break
            if j==len(selected_users)-1:
                i=j+1
                groups.append(group)
            j =j+1
    groups.sort(lambda x,y:cmp(len(x['oudn'].split(",")),len(y['oudn'].split(","))))
    return groups

# +++20151125 登录后上传IP，做IP地址的地区验证，检测异常登录
class UploadIP:
    def GET(self):
        """
        input:
            admin
            ip
        output:
            rt:
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['admin','action','time','result'])
            if not i:
                raise ecode.WS_INPUT
            timeStr = time.strftime('%Y-%m-%d %H:%M:%S')
            ip_addr = get_ip_addr(web.ctx.ip)
            if i['result']=='0':
                op = "正确"
            else :
                op = "登陆失败"
            log_web_db.add_log(i['admin'],[],timeStr,i['action'],ip_addr,op)

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error("get log control user failed")
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,jsonp=False),error_info)

# +++20151127 ip与物理地址映射
def get_ip_addr(ip):
    try:
        reload(sys)
        sys.setdefaultencoding('utf8')
        ip_addr = ip_service2(ip)
        return ip+': ('+str(ip_addr)+')'
    except Exception as e:
        print e.message
    return ip+":(未能成功获取地址)"

def ip_service1(ip):
    try:
        page = urllib.urlopen("http://www.webxml.com.cn/WebServices/IpAddressSearchWebService.asmx/getCountryCityByIp?theIpAddress="+ip)
        lines = page.readlines()
        page.close()
        document = ""
        for line in lines :
            document = document + unicode(line).encode("utf8")
        dom =parseString(document)
        strings = dom.getElementsByTagName("string")
        ip_addr = strings[1].childNodes[0].data
        return ip_addr
    except Exception as e:
        raise Exception("ip service failed")


def ip_service2(ip):
    try:
        page = urllib.urlopen("http://ip.taobao.com/service/getIpInfo.php?ip="+ip)
        result = page.read()
        page.close()
        dict_r = eval(result)
        return (dict_r['data']['city']+" "+dict_r['data']['isp']).decode('raw_unicode_escape')
    except Exception as e:
        raise Exception("ip service failed")


class GetOuBaseInfo:
    def GET(self):
        """
        input:
            sid:管理员的sid
        output:
            ou_name:从选中的用户中获得的群组名称
            user_num:群组中用户数量
            live_dev_num:激活设备数量
            live_user_num:在线用户数量
            sum_use_days:总使用天数
            avg_use_days:平均使用天数
            sum_live_days:总活跃天数
            avg_live_days:平均活跃天数
            avg_live_percentage:平均活跃度
            uses_live_beyond_per:活跃度大于（目前是50%）多少的人
        """
        rt = ecode.FAILED
        ou_name = ""
        user_num = 0
        live_dev_num = 0
        live_user_num = 0
        sum_use_days = 0
        avg_use_days = 0.0
        sum_live_days = 0
        avg_live_days = 0.0
        avg_live_percentage = 0.0
        uses_live_beyond_per = 0
        beyond_per = 0.5
        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            user = session_db.user.get_user(i['sid'],web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # if len(i['oudn'])>0:
                # users = user_db.get_ou_users(i['oudn'])
            users = user_db.get_selected_users(user)
            ou_name = get_ou_name(users)
            user_num = len(users)
            if(user_num>0):
                sum_use_days = 0
                sum_live_days = 0
                sum_liveness = 0.0
                #关于用户的统计信息
                for item in users:
                    #获取群组用户设备激活的情况
                    devs = item['devs']
                    if devs!=[]:
                        live_dev_num+=1
                        onlinestate = user_db.get_use_state(item['key'])
                        if((int(onlinestate['online'])+int(onlinestate['outline']))==0):
                            per_liveness = 0.0
                        else:
                            per_liveness = float(onlinestate['online'])/(float(onlinestate['online'])+float(onlinestate['outline']))
                        sum_liveness += per_liveness
                        if per_liveness>beyond_per:
                            logging.error("per_liveness:"+str(per_liveness))
                            uses_live_beyond_per+=1
                        sum_use_days+=int(onlinestate['online'])+int(onlinestate['outline'])
                        sum_live_days+=int(onlinestate['online'])
                    if int(item['status'])==2:
                        live_user_num+=1
                if(live_dev_num>0):
                    avg_use_days = float(sum_use_days)/float(live_dev_num)
                    avg_live_days = float(sum_live_days)/float(live_dev_num)
                    avg_live_percentage = float(sum_liveness)/float(live_dev_num)
                #关于群组策略的统计信息
                # strategys = strategy_db.get_strategys()
                # for strategy in strategys:
                #     # 由于策略描述可能不全，只能扒原始数据进行对比
                #     # 匹配条件1、策略未过期（当前策略+1，历史策略+1）、过期（历史策略+1）2、含有该群组
                #     if strategy_db.is_contorl_ou(strategy['strategy_id'],i['oudn']):
                #         strategy_status = strategy_db.strategy_status(strategy['strategy_id'])
                #         if strategy_status==0:
                #             cur_stras+=1
                #         elif strategy_status>=0:
                #             history_stras+=1
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error("get ou base info failed")
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,ou_name=ou_name,user_num=user_num,live_dev_num=live_dev_num,
                                    live_user_num=live_user_num,avg_use_days=avg_use_days,
                                    avg_live_days=avg_live_days,avg_live_percentage=avg_live_percentage,
                                    uses_live_beyond_per=uses_live_beyond_per,sum_use_days=sum_use_days,
                                    sum_live_days=sum_live_days),error_info)


def get_ou_name(users):
    """
    根据选中的用户获取统计的群组名称
    :param users:选中的用户
    :return:ou_name
    """
    ou_name = ""
    if(len(users)>0):
        ou_list = []
        min_len = len(users[0]['oudn'].split(","))
        for item in users:
            if(item['oudn'] not in ou_list):
                if(len(item['oudn'].split(",")))<min_len:
                    min_len = len(item['oudn'].split(","))   #获取最小群组长度
                ou_list.append(item['oudn'])

        start = -3
        while (abs(start)<=min_len) and len(find_step_ou_count(start,ou_list))==1:
            start-=1
        final_oudn = ""
        stop = start  #记录停止的层次
        start += 1    #回到上一层
        while start<0:
            final_oudn = final_oudn + "," + ou_list[0].split(",")[start]
            start+=1

        final_oudn = final_oudn[1:len(final_oudn)]
        # next_level_ous = find_step_ou_count(stop,ou_list)

        friendly_name = get_oudn_friendly_name(final_oudn)

    return friendly_name


def get_oudn_friendly_name(oudn):
    ou_name = ""
    if len(oudn)>0:
        if(oudn == "dc=test,dc=com"):
            ou_name = u"多个群组"
        else:
            ou_name = oudn.split(",")[0].split("=")[1]
    return ou_name


def find_step_ou_count(step,ou_list):
    oudn_item_list = []
    start = step  #将根节点的两个item舍去
    for oudn in ou_list:
        oudn_item = oudn.split(",")[start]
        if(oudn_item not in oudn_item_list):
            oudn_item_list.append(oudn_item)
    return oudn_item_list




# +++20160106获取群组活跃度统计信息
class GetLivenessData:
    def GET(self):
        """
        input:
            sid:
            analysis_rule:统计规则，目前规则只有在线天数
        output:
            活跃度占比对应的人数
            {
                rt:
                data:[
                    {
                        percentage:20，40,60,80，100  #0-20%，20%-40%，40%-60%，60%-80%，80%-100%
                        num:
                    }
                ],
                verfied_count:激活设备数量
            }
        """
        rt = ecode.FAILED
        percentage_list = []
        verfied_count = 0
        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT

            admin = session_db.user.get_user(i['sid'],web.ctx.ip)
            if not admin:
                raise ecode.NOT_LOGIN

            # if i['oudn']!="":
                # ou_users = user_db.get_ou_users(i['oudn'])
            ou_users = user_db.get_selected_users(admin)
            liveness_under_20 = 0
            liveness_under_40 = 0
            liveness_under_60 = 0
            liveness_under_80 = 0
            liveness_under_100 = 0
            for item in ou_users:
                devs = item['devs']
                if devs==[]:
                    # 剔除未激活用户
                    continue
                else:
                    verfied_count+=1
                    liveness_state = user_db.get_use_state(item['key'])
                    online = int(liveness_state['online'])
                    outline = int(liveness_state['outline'])
                    if(int(online)>=int(i['analysis_rule'])):
                        if online+outline!=0:
                            liveness_percentage = float(online)/float((online+outline))
                        else:
                            liveness_percentage = 0.0
                        if liveness_percentage>0 and liveness_percentage<=0.2:
                            liveness_under_20+=1
                        elif liveness_percentage>0.2 and liveness_percentage<=0.4:
                            liveness_under_40+=1
                        elif liveness_percentage>0.4 and liveness_percentage<=0.6:
                            liveness_under_60+=1
                        elif liveness_percentage>0.6 and liveness_percentage<=0.8:
                            liveness_under_80+=1
                        elif liveness_percentage>0.8 and liveness_percentage<=1.0:
                            liveness_under_100+=1
            percentage_list = [{"percentage":20,"num":liveness_under_20},
                                   {"percentage":40,"num":liveness_under_40},
                                   {"percentage":60,"num":liveness_under_60},
                                   {"percentage":80,"num":liveness_under_80},
                                   {"percentage":100,"num":liveness_under_100}]
            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error(e.message)
            logging.error('get liveness data failed,admin:%s',admin)
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,data=percentage_list,verfied_count=verfied_count),error_info)

# +++20160119获取群组用户在线情况
class GetUserOnlineData:
    """
    input:
        sid:管理员sid
        target:统计的时间范围
    output:
        rt:
        online_data:
    """
    def GET(self):
        rt = ecode.FAILED
        results = []
        try:
            i = ws_io.ws_input(['sid','target'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user(i['sid'],web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            # 获取现在被选中的所有用户
            users = user_db.get_selected_users(user)
            uid_list = []
            for item in users:
                uid_list.append(item['uid'])
            target = i['target']
            results = online_statistics_db.get_online_time_users(target)
            # 前两步将选中的统计目标用户和在线用户统计了一下，将每天的用户和统计用户作交集，即可得最后的结果
            for result in results:
                online_uid_list = result['online_users']
                final_uid_list = [val for val in online_uid_list if val in uid_list]
                result['online_user_length'] = len(final_uid_list)
                result['online_users'] = []
            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get user online data failed,admin:',user)
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,online_data=results),error_info)


# #+++20150625 for all users liveness
# class TestIsOnline:
#     def GET(self):
#         """
#         input:
#             interval:n(s)
#         output:
#             rt: error code
#         """
#         rt = ecode.FAILED
# 
#         try:
#             i = ws_io.ws_input(['interval'])
#             if not i:
#                 raise ecode.WS_INPUT
#             interval=int(i['interval'])
#             
#             user_dev_list=user_db.get_all_user_and_dev()
#             for user in user_dev_list:
#                 uid=user["uid"]
#                 dev_id=user["dev_id"]
#                 liveness=user_db.get_liveness(uid)
#                 sid=session_db.user.get_sid(uid,dev_id)
#                 #总的在线离线
#                 total=liveness['total']
#                 total_on=int(total.split(",")[0])
#                 total_off=int(total.split(",")[1])
#                 #一周的在线离线
#                 week=liveness['week']
#                 week_on=int(week.split(",")[0])
#                 week_off=int(week.split(",")[1])
#                 #一天的在线离线
#                 day=liveness['day']
#                 day_on=int(day.split(",")[0])
#                 day_off=int(day.split(",")[1])
#                 #判断是否足够一周或一天
#                 if week_on+week_off>=604800:
#                     week_on=0
#                     week_off=0
#                 if day_on+day_off>=86400:
#                     day_on=0
#                     day_off=0
#                 #判断在线状态
#                 if config.is_sid_on_push_server(sid):
#                     #该用户在线
#                     total_on=str(total_on+interval)
#                     week_on=str(week_on+interval)
#                     day_on=str(day_on+interval)
#                 else:
#                     #该用户离线
#                     total_off=str(total_off+interval)
#                     week_off=str(week_off+interval)
#                     day_off=str(day_off+interval)
#                 #统计时间
#                 liveness['total']=total_on+','+total_off
#                 liveness['week']=week_on+','+week_off
#                 liveness['day']=day_on+','+day_off
#                 #更新数据库
#                 user_db.update_liveness(uid, liveness)
#             
#             rt = ecode.OK
#               error_info=""
#         except Exception as e:
#             rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
#             logging.error('Test Is Online')
#               error_info = str(traceback.format_exc()).replace("\n"," ")
# 
#         return ws_io.ws_output(dict(rt=rt.eid),error_info)

class SearchFirstPageUsers:
    def GET(self):
        """
        input:
            sid:
            xialakuang:
            guanjianzi:
            size:页面大小
            [last_user]:参考用户,此项可选，用于整合跳到某一页的情况
            sort_keys:[{name:,order:}]  就是排序键的一个集合，如果为空则是默认的情况，有值的话取值并按相应的顺序排序
        output:
            rt: error code
            selected_count:选中用户的总数
            users:[] for first page
        """
        rt = ecode.FAILED
        user_list = []
        selected_count = 0
        try:
            i = ws_io.ws_input(['sid','xialakuang','guanjianzi',"size"])
            if not i:
                raise ecode.WS_INPUT
            sid = i['sid']
            user = session_db.user.get_user( sid, web.ctx.ip)
            #加入一步sid验证
            if not user:
                raise ecode.NOT_LOGIN
            size = i['size']
            last_user = ""
            if i.has_key('last_user'):
                last_user = i['last_user']
            if i.has_key('sort_keys'):
                sort_keys = json.loads(i['sort_keys'])
            else:
                sort_keys = []

            selected_count = user_db.get_selected_countqj(user,i['xialakuang'],i['guanjianzi'])
            #每次获取第一页数据返回，需要前台配合修改
            user_list = user_db.get_all_users_info(user,i['xialakuang'],i['guanjianzi'],'1',size,"",[])
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            logging.error('Change selected users failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,users=user_list,selected_count=selected_count),error_info)

class SearchAllUsers:
    def GET(self):
        """
        input:
            sid:
            xialakuang:
            guanjianzi:
            page:num/next/last
            size:
            [last_user]:参考用户,此项可选，用于整合跳到某一页的情况
            sort_keys:[{name:,order:}]  就是排序键的一个集合，如果为空则是默认的情况，有值的话取值并按相应的顺序排序
        output:
            rt: error code
            users:[]
        """
        rt = ecode.FAILED
        users = []

        try:
            i = ws_io.ws_input(['sid','xialakuang','guanjianzi',"page","size"])
            if not i:
                raise ecode.WS_INPUT

            sid = i['sid']
            admin = session_db.user.get_user( sid, web.ctx.ip)
            #加入一步sid验证
            if not admin:
                raise ecode.NOT_LOGIN
            page = i['page']
            size = i['size']
            last_user = ""
            if i.has_key('last_user'):
                last_user = i['last_user']
            if i.has_key('sort_keys'):
                sort_keys = json.loads(i['sort_keys'])
            else:
                sort_keys = []

            users = user_db.get_all_users_info(admin,i['xialakuang'],i['guanjianzi'],page,size,"",[])
            rt = ecode.OK
            error_info=""
        except Exception as e:
            logging.error_info('Search All Users failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,users=users),error_info)

#+++/************/+++#

class AddMaster:
    #{{{
    def POST(self):
        """
        input:
            sid:
            loginType:
            uid: user id
            pw: password
            ou: the range of uid's right
            email:email
            phonenumber:phonenumber
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['uid','pw','sid','ou','email','phonenumber','loginType'])
            if not i:
                raise ecode.WS_INPUT

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            # if i['loginType'] != org_config['su_master']:
            #     raise ecode.NOT_PERMISSION
            if i['loginType'] != 'master':
                raise ecode.NOT_PERMISSION

            if not master_db.is_has_master(i['uid']):
                master_db.add_master(i['uid'], sha.new(i['pw']).hexdigest(),i['ou'],i['email'],i['phonenumber'])
            else:
                raise ecode.USER_EXIST
            error_info=""
            rt = ecode.OK
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('org add master')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        op_user=user
        op_type=operation.ADD_master.type
        op_desc=operation.ADD_master.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )
        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}
class DelMaster:
    #{{{
    def POST(self):
        """
        input:
            sid:
            loginType:
            uid:user to delete
        output:
            rt: error ecode
        """
        rt = ecode.FAILED

        try:

            i = ws_io.ws_input(['sid','uid','loginType'])
            if not i:
                raise ecode.WS_INPUT

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            # if user != org_config['su_master']:
            #     raise ecode.NOT_PERMISSION

            if i['loginType'] != 'master':
                raise ecode.NOT_PERMISSION

            if not master_db.is_has_master(i['uid']):
                raise ecode.USER_NOT_EXIST

            if not master_db.del_master(i['uid']):
                raise ecode.DB_OP
            error_info=""
            rt = ecode.OK
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('delete master failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        #日志记录
        op_user=user
        op_type=operation.DEL_master.type
        op_desc=operation.DEL_master.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}


class AddAuditor:
    #{{{
    def POST(self):
        """
        input:
            sid:
            loginType:
            uid: user id
            pw: password
            ou: the range of uid's right
            email:email
            phonenumber:phonenumber
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['uid','pw','sid','ou','email','phonenumber','loginType'])
            if not i:
                raise ecode.WS_INPUT

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            # if i['loginType'] != org_config['su_auditor']:
            #     raise ecode.NOT_PERMISSION
            if i['loginType'] != 'auditor':
                raise ecode.NOT_PERMISSION

            if not auditor_db.is_has_auditor(i['uid']):
                auditor_db.add_auditor(i['uid'], sha.new(i['pw']).hexdigest(),i['ou'],i['email'],i['phonenumber'])
            else:
                raise ecode.USER_EXIST
            error_info=""
            rt = ecode.OK
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('org add auditor')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        # 日志记录
        op_user=user
        op_type=operation.ADD_auditor.type
        op_desc=operation.ADD_auditor.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )
        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}

class DelAuditor:
    #{{{
    def POST(self):
        """
        input:
            sid:
            loginType:
            uid:user to delete
        output:
            rt: error ecode
        """
        rt = ecode.FAILED

        try:

            i = ws_io.ws_input(['sid','uid','loginType'])
            if not i:
                raise ecode.WS_INPUT

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            # if user != org_config['su_auditor']:
            #     raise ecode.NOT_PERMISSION

            if i['loginType'] != 'auditor':
                raise ecode.NOT_PERMISSION

            if not auditor_db.is_has_auditor(i['uid']):
                raise ecode.USER_NOT_EXIST

            if not auditor_db.del_auditor(i['uid']):
                raise ecode.DB_OP
            error_info=""
            rt = ecode.OK
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('delete auditor failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        #日志记录
        op_user=user
        op_type=operation.DEL_auditor.type
        op_desc=operation.DEL_auditor.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}

class AddSA:
    #{{{
    def POST(self):
        """
        input:
            sid:
            loginType:
            uid: user id
            pw: password
            ou: the range of uid's right
            email:email
            phonenumber:phonenumber
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['uid','pw','sid','ou','email','phonenumber','loginType'])
            if not i:
                raise ecode.WS_INPUT

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if i['loginType'] != 'sa':
                raise ecode.NOT_PERMISSION
            if not SA_db.is_has_SA(i['uid']):
                SA_db.add_SA(i['uid'], sha.new(i['pw']).hexdigest(),i['ou'],i['email'],i['phonenumber'])
            else:
                raise ecode.USER_EXIST
            error_info=""
            rt = ecode.OK
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('org add SA')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        # 日志记录
        op_user=user
        op_type=operation.ADD_sa.type
        op_desc=operation.ADD_sa.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )
        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}

class DelSA:
    #{{{
    def POST(self):
        """
        input:
            sid:
            loginType:
            uid:user to delete
        output:
            rt: error ecode
        """
        rt = ecode.FAILED

        try:

            i = ws_io.ws_input(['sid','uid','loginType'])
            if not i:
                raise ecode.WS_INPUT

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            # if user != org_config['su_SA']:
            #     raise ecode.NOT_PERMISSION

            if not SA_db.is_has_SA(i['uid']):
                raise ecode.USER_NOT_EXIST

            if not SA_db.del_SA(i['uid']):
                raise ecode.DB_OP
            error_info=""
            rt = ecode.OK
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('delete sa failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        #日志记录
        op_user=user
        op_type=operation.DEL_sa.type
        op_desc=operation.DEL_sa.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}

class MasterTree:   #获得所有的管理员(侧边列表)
    def GET(self):
        """
        input:
            sid:
            loginType:
        output:
            rt: error code
            all: [{uid,email,phonenumber,qx},{},...]
        """
        rt = ecode.FAILED
        all = []

        try:
            i = ws_io.ws_input(['sid','loginType'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            logging.error("用户是:%s",user)
            if not user:
                raise ecode.NOT_LOGIN

            if i['loginType']!='master':
                raise ecode.NOT_PERMISSION

            #get master
            all = master_db.show_masters()
            logging.error("all is : %s",all)
            rt = ecode.OK
            error_info=""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get master')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,all=all),error_info)

class adminTree:   #获得所有的操作员(侧边列表)
    def GET(self):
        """
        input:
            sid:
            loginType:
        output:
            rt: error code
            all: [{uid,email,phonenumber,ou},{},...]
        """
        rt = ecode.FAILED
        all = []

        try:
            i = ws_io.ws_input(['sid','loginType'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            logging.error("用户是:%s",user)
            if not user:
                raise ecode.NOT_LOGIN

            if i['loginType']!='master':
                raise ecode.NOT_PERMISSION

            #get master
            all = admin_db.show_admins()
            logging.error("all is : %s",all)
            rt = ecode.OK
            error_info=""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get admin')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,all=all),error_info)

class SaTree:   #获得所有的安全员(侧边列表)
    def GET(self):
        """
        input:
            sid:
            loginType:
        output:
            rt: error code
            all: [{uid,email,phonenumber,ou},{},...]
        """
        rt = ecode.FAILED
        all = []

        try:
            i = ws_io.ws_input(['sid','loginType'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            logging.error("用户是:%s",user)
            if not user:
                raise ecode.NOT_LOGIN

            if i['loginType']!='sa':
                raise ecode.NOT_PERMISSION

            #get sa
            all = SA_db.show_SAs()
            logging.error("all is : %s",all)
            rt = ecode.OK
            error_info=""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get sa')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,all=all),error_info)

class AuditorTree:   #获得所有的审计员(侧边列表)
    def GET(self):
        """
        input:
            sid:
            loginType:
        output:
            rt: error code
            all: [{uid,email,phonenumber,ou},{},...]
        """
        rt = ecode.FAILED
        all = []

        try:
            i = ws_io.ws_input(['sid','loginType'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            logging.error("用户是:%s",user)
            if not user:
                raise ecode.NOT_LOGIN

            if i['loginType']!='auditor':
                raise ecode.NOT_PERMISSION

            #get auditor
            all = auditor_db.show_auditors()
            logging.error("all is : %s",all)
            rt = ecode.OK
            error_info=""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get auditor')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,all=all),error_info)

#服务器端日志，封装供前端调用，以记录前端的动作（login）
class LogWeb:
    #{{{
    def POST(self):
        """
        input:
            sid:   for user
            user:  可为空(与sid至少一个不为空)   for login
            op_type:   操作类型
            op_desc:   操作描述
            op_result:   操作结果
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','user','op_type','op_desc','op_result'])
            if not i:
                raise ecode.WS_INPUT

            if i['user']!='':
                user=i['user']
            elif i['sid']!='':
                user=session_db.user.get_user( i['sid'], web.ctx.ip)
            else:
                raise ecode.FAILED

            op_type=i['op_type']
            op_desc=i['op_desc']
            op_result=i['op_result']
            op_time=time.strftime('%Y-%m-%d %H:%M:%S')
            re_num=log_web_db.add_log(user,[],op_time ,op_type, op_desc, op_result )
            #re_num，用来内存预警和删除的。9.9+
            error_info=""
            rt = ecode.OK
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('log_web:%d',re_num)
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,re_num=re_num),error_info)
    #}}}

class GetAuditLogs:   #+++11.21
    def GET(self):
        """
        input:
            sid:
            loginType:
        output:
            rt: error code
            auditlogs: [...]
        """
        rt = ecode.FAILED
        auditlogs = []

        try:
            i = ws_io.ws_input(['sid','loginType'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            # if i['loginType'] != org_config['su_auditor']:
            #     raise ecode.NOT_PERMISSION
            if i['loginType']!='auditor':
                raise ecode.NOT_PERMISSION

            auditlogs=log_web_db.get_audit_logs()
            log_space_state=global_db.get_global('log_warning')
            rt = ecode.OK
            error_info=""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get auditlogs')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,auditlogs=auditlogs,log_space_state=log_space_state),error_info)

class SearchLogs:   #+++11.22 日志检索功能
    def GET(self):
        """
        input:
            sid:
            loginType:
            start:检索日志开始的时间
            end:检索日志结束的时间
            operator:检索日志操作者
            log_number:检索日志数目
        output:
            rt: error code
            se_logs: [...]
        """
        rt = ecode.FAILED
        se_logs = []

        try:
            i = ws_io.ws_input(['sid','loginType','start','end','operator','log_number'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)

            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            # if i['loginType'] != org_config['su_auditor']:
            #     raise ecode.NOT_PERMISSION
            if i['loginType']!='auditor':
                raise ecode.NOT_PERMISSION

            #检索日志
            # if i['log_number']=='':
            #     i['log_number']=50   #default
            # if str(i['start'])!='':
            #     start = time.mktime(time.strptime(str(i['start']), '%Y-%m-%d %H:%M'))
            #     start=int(start)
            # if str(i['end'])!='':
            #     end = time.mktime(time.strptime(str(i['end']), '%Y-%m-%d %H:%M'))
            #     end=int(end)
            start=str(i['start'])
            end=str(i['end'])
            logging.error('start time and end time : %s,%s',start,end)
            # print i['operator']
            # print start
            # print end
            # print int(i['log_number'])
            se_logs=log_web_db.search_logs(str(i['operator']), start, end, int(i['log_number']))
            rt = ecode.OK
            error_info=""
            print "########################################"
            print se_logs
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get searchlogs')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,se_logs=se_logs),error_info)

class AuditlogCheck:
    #{{{
    def GET(self):
        """
        input:
            sazh:
            sapw:
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sazh','sapw'])
            if not i:
                raise ecode.WS_INPUT

            # org_config = org.get_config()
            # if org_config['su_SA'] == i['sazh']:
            #     if org_config['su_SA_pw'] != sha.new(i['sapw']).hexdigest():
            #         raise ecode.USER_AUTH
            if SA_db.is_has_SA(i['sazh']):
                if not SA_db.check_pw(i['sazh'], sha.new(i['sapw']).hexdigest()):
                    raise ecode.USER_AUTH
            rt = ecode.OK
            error_info=""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('check a auditlog qx.')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)

class ExportLog:   #+++11.23 日志导出功能
    def GET(self):
        """
        input:
            sid:
            loginType:
        output:
            rt: error code
        """
        rt = ecode.FAILED
        exportcontent=[]
        exportflag={}

        try:
            i = ws_io.ws_input(['sid','loginType'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            # if i['loginType'] != org_config['su_auditor']:
            #     raise ecode.NOT_PERMISSION
            if i['loginType']!='auditor':
                raise ecode.NOT_PERMISSION

            #查找global，确定要导出的日志内容 exportcontent
            exportflag=global_db.get_global('auditlogexport')
            if exportflag=='':
                exportcontent=log_web_db.get_audit_logs()
            else:
                user=exportflag['user']
                start=exportflag['start']
                end=exportflag['end']
                log_number=exportflag['log_number']
                exportcontent=log_web_db.search_logs(user, start, end, log_number)
            #现在根据exportcontent来导出excel
            #创建一个新工作簿
            auditlog=xlwt.Workbook(encoding='utf-8',style_compression=0)
            #添加一个sheet，命名为log
            sheet=auditlog.add_sheet('log',cell_overwrite_ok=True)
            #写入excel（中文需要编码）
            sheet.write(0,0,unicode('序号','utf-8'))
            sheet.write(0,1,unicode('操作时间','utf-8'))
            sheet.write(0,2,unicode('操作者','utf-8'))
            sheet.write(0,3,unicode('操作类型','utf-8'))
            sheet.write(0,4,unicode('操作描述','utf-8'))
            sheet.write(0,5,unicode('操作结果','utf-8'))
            xuhao=1   #写入的序号
            for item in exportcontent:
                # timeStamp=int(item['time'])*0.001
                # timeArray = time.localtime(timeStamp)
                # op_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)   #转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
                sheet.write(xuhao,0,xuhao)
                sheet.write(xuhao,1,item['time'])
                sheet.write(xuhao,2,item['uid'])
                sheet.write(xuhao,3,item['action'])
                sheet.write(xuhao,4,str(item['info']))
                sheet.write(xuhao,5,item['result'])
                xuhao=xuhao+1
            auditlog.save('/home/wcloud/opt/org/download/audit_log.xls')

            rt = ecode.OK
            error_info=""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('export auditlogs')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

class GetSpaceState:   #+++11.23
    def GET(self):
        """
        input:
            sid:
            loginType:
        output:
            rt: error code
            currentspace:
            currentlimit:
        """
        rt = ecode.FAILED
        currentspace=0
        currentlimit=200

        try:
            i = ws_io.ws_input(['sid','loginType'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            # if i['loginType'] != org_config['su_auditor']:
            #     raise ecode.NOT_PERMISSION
            if i['loginType']!='auditor':
                raise ecode.NOT_PERMISSION
            current_space=global_db.get_global('log_number')
            current_limit=global_db.get_global('currentlimit')
            if current_limit=='':
                current_limit=0
            currentspace=current_space*0.13   #一条记录0.13kb
            currentlimit=current_limit*0.13

            rt = ecode.OK
            error_info=""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get spacestate')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,currentspace=currentspace,currentlimit=currentlimit),error_info)

class SetLogSpace:   #+++11.23
    def GET(self):
        """
        input:
            sid:
            loginType:
            log_space_set:
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','loginType','log_space_set'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            # org_config = org.get_config()
            # if i['loginType'] != org_config['su_auditor']:
            #     raise ecode.NOT_PERMISSION
            if i['loginType']!='auditor':
                raise ecode.NOT_PERMISSION
            log_space_set=int(float(i['log_space_set'])/0.13)
            global_db.add_global('currentlimit', log_space_set)

            rt = ecode.OK
            error_info=""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('set log_space_set')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)

class AutoSearchBySid:
    #{{{
    def GET(self):
        """
        input:
            sid: sesssion id
        output:
            rt: error code
            users_name:[{}]
        """
        rt = ecode.FAILED
        oudn = ''
        contact_ous = []
        users_name = []

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT

            sid = i['sid']
            admin = session_db.user.get_user(sid,web.ctx.ip)
            org_config = org.get_config()

            if admin!=org_config['admin']:
                if not admin_db.is_has_admin(admin):
                    raise ecode.NOT_PERMISSION
                else:
                    ou = admin_db.get_ou_by_uid(admin)
                    contact_arr = admin_db.get_contact_ous_by_uid(admin)
                    if ou=="admin":
                        oudn = org_config['ldap_base_dn']
                        contact_ous = org_config['ldap_base_dn']
                    else:
                        oudn = ou
                        contact_ous = contact_arr
                users_name = user_db.get_auto_search_con_users(contact_ous)

            else:
                users_name = user_db.get_auto_search_all_users()
            error_info=""
            rt = ecode.OK
            logging.warn("AutoSearchBySid--sid:%s",sid)
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('auto search by sid')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,users=users_name),error_info)
    #}}}

class AutoSearchAdmBySid:
    #{{{
    def GET(self):
        """
        input:
            sid: sesssion id
        output:
            rt: error code
            users_name:[{}]
        """
        rt = ecode.FAILED
        oudn = ''
        users_name = []

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT

            sid = i['sid']
            admin = session_db.user.get_user(sid,web.ctx.ip)
            org_config = org.get_config()

            if admin!='admin':
                if not admin_db.is_has_admin(admin):
                    raise ecode.NOT_PERMISSION
                else:
                    ou = admin_db.get_ou_by_uid(admin)
                    if ou=="admin":
                        oudn = org_config['ldap_base_dn']
                    else:
                        oudn = ou
                users_name = user_db.get_auto_search_adm_users(oudn)

            else:
                users_name = user_db.get_auto_search_all_users()
            error_info=""
            rt = ecode.OK
            logging.warn("AutoSearchBySid--sid:%s",sid)
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('auto search by sid')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,users=users_name),error_info)
    #}}}

class AutoSelectedBySid:
    #{{{
    def GET(self):
        """
        input:
            sid: sesssion id
            username: username
        output:
            rt: error code
            dn:操作员的管理权限
            contacts：操作员的通信权限
            users:[{}]
            count：找到的用户个数
        """
        rt = ecode.FAILED
        oudn = ''
        contact_ous = []
        #user_oudn= ''
        #user_key= ''
        #user_uid= ''
        item_user=[]
        items_user=[]
        user_search_count=0
        try:
            i = ws_io.ws_input(['sid','username'])
            if not i:
                raise ecode.WS_INPUT

            sid = i['sid']
            admin = session_db.user.get_user(sid,web.ctx.ip)
            org_config = org.get_config()

            if admin!=org_config['admin']:
                if not admin_db.is_has_admin(admin):
                    raise ecode.NOT_PERMISSION
                else:
                    ou = admin_db.get_ou_by_uid(admin)
                    contact_arr = admin_db.get_contact_ous_by_uid(admin)
                    if ou=="admin":
                        oudn = org_config['ldap_base_dn']
                        contact_ous = org_config['ldap_base_dn']
                    else:
                        oudn = ou
                        contact_ous = contact_arr

                users = user_db.get_auto_selected_users(admin,i['username'])
                #user_uid = user["uid"]
                #user_key = user["key"]
                #user_oudn = user["oudn"]
                for item in users:
                    for con in contact_ous:
                        if con in item["oudn"]:
                            item_user=[('user_id',item["uid"]),('user_key',item["key"]),('user_oudn',item["oudn"])]
                            item_user=dict(item_user)
                            items_user=items_user+[item_user]
                            user_search_count=user_search_count+1

            else:
                oudn = admin_db.get_ou_by_uid(admin)
                contact_ous = org_config['ldap_base_dn']
                users = user_db.get_auto_selected_users(admin,i['username'])

                #user_uid = user["uid"]
                #user_key = user["key"]
                #user_oudn = user["oudn"]
                for item in users:
                    item_user=[('user_id',item["uid"]),('user_key',item["key"]),('user_oudn',item["oudn"])]
                    item_user=dict(item_user)
                    items_user=items_user+[item_user]
                    user_search_count=user_search_count+1

            rt = ecode.OK
            error_info=""
            logging.warn("AutoSelectedBySid--sid:%s",sid)
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('auto selected by sid')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,dn=oudn,contacts=contact_ous,user=items_user,count=user_search_count),error_info)
    #}}}

class AutoSelectedAdmBySid:
    #{{{
    def GET(self):
        """
        input:
            sid: sesssion id
            username: username
        output:
            rt: error code
            users:[{}]
        """
        rt = ecode.FAILED
        oudn = ''
        contact_ous = []
        user_oudn= ''
        item_user=[]
        items_user=[]
        user_search_count=0
        try:
            i = ws_io.ws_input(['sid','username'])
            if not i:
                raise ecode.WS_INPUT

            sid = i['sid']
            admin = session_db.user.get_user(sid,web.ctx.ip)
            org_config = org.get_config()

            if admin!=org_config['admin']:
                if not admin_db.is_has_admin(admin):
                    raise ecode.NOT_PERMISSION
                else:
                    ou = admin_db.get_ou_by_uid(admin)
                    contact_arr = admin_db.get_contact_ous_by_uid(admin)
                    if ou=="admin":
                        oudn = org_config['ldap_base_dn']
                        contact_ous = org_config['ldap_base_dn']
                    else:
                        oudn = ou
                        contact_ous = contact_arr

                users = user_db.get_auto_selected_adm_users(admin,i['username'])
                #user_uid = user["uid"]
                #user_key = user["key"]
                #user_oudn = user["oudn"]
                for item in users:
                    if oudn in item["oudn"]:
                        item_user=[('user_id',item["uid"]),('user_key',item["key"]),('user_oudn',item["oudn"])]
                        item_user=dict(item_user)
                        items_user=items_user+[item_user]
                        user_search_count=user_search_count+1



            else:
                oudn = admin_db.get_ou_by_uid(admin)
                users = user_db.get_auto_selected_adm_users(admin,i['username'])
                #user_uid = user["uid"]
                #user_key = user["key"]
                #user_oudn = user["oudn"]
                for item in users:
                    item_user=[('user_id',item['uid']),('user_key',item['key']),('user_oudn',item['oudn'])]
                    item_user=dict(item_user)
                    items_user=items_user+[item_user]
                    user_search_count=user_search_count+1
            error_info=""
            rt = ecode.OK
            logging.warn("AutoSelectedBySid--sid:%s",sid)
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('auto selected by sid failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,dn=oudn,contacts=contact_ous,user=items_user,count=user_search_count),error_info)
    #}}}
import pseudo_bs_db
# 新增设备***
class AddControl:
    def POST(self):
        """
        input:
        type
        uid
        institute
        output:
        rt
        """
        rt=ecode.FAILED
        try:
            i = ws_io.ws_input(['type','uid','institute'])
            ty=i['type']
            uid=i['uid']
            institute=i['institute']
            if not i:
                raise ecode.WS_INPUT
            if not pseudo_bs_db.addpbsinfo(uid,ty,institute):
                return ecode.DB_OP
            error_info=""
            rt = ecode.OK
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get pseudo_bs_single_info failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)
# 删除设备***
class DelControlUser:
    def POST(self):
        rt=ecode.FAILED
        try:
            i = ws_io.ws_input(['uid'])
            uid=i['uid']
            if not i:
                raise ecode.WS_INPUT
            if not pseudo_bs_db.del_pbs(uid):
                raise ecode.DB_OP
            error_info=""
            rt = ecode.OK
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('del pseudo_bs failed ')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)
# 左侧目录聚类树***
class ControlTree:
    def GET(self):
        """
        input:
        sid
        output:
        all
        """
        rt=ecode.FAILED
        all=[]
        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT
            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            logging.error("用户是:%s",user)
            if not user:
                raise ecode.NOT_LOGIN
            all=pseudo_bs_db.show_pbs()
            error_info=""
            rt = ecode.OK

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get pseudo_bs failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,all=all),error_info)
# 中间列表信息***
class ControlTreeList:
    def GET(self):
        """
        input:
        sid
        institute
        output:
        all
        """
        rt=ecode.FAILED
        try:
            i = ws_io.ws_input(['institute'])
            if not i:
                raise ecode.WS_INPUT

            all=pseudo_bs_db.show_list(i['institute'])
            error_info=""
            rt = ecode.OK

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get pseudo_bs failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,all=all),error_info)
# 右下角设备详细信息***
class ControlTreeInfo:
    def GET(self):
        """
        input:
        sid
        uid
        output:
        all
        """
        rt=ecode.FAILED

        all=[]
        try:
            i = ws_io.ws_input(['uid'])
            uid=i['uid']
            if not i:
                raise ecode.WS_INPUT
            all=pseudo_bs_db.show_details(uid)
            print all
            error_info=""
            rt = ecode.OK
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get pseudo_bs_single_info failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,all=all),error_info)
# 右下角设备白名单***
class ControlWhitelistInfo:
    def GET(self):
        """
        input:
        sid
        uid
        output:
        all
        """
        rt=ecode.FAILED
        all=[]
        try:
            i = ws_io.ws_input(['uid'])
            uid=i['uid']
            if not i:
                raise ecode.WS_INPUT
            all=pseudo_bs_db.show_whitelist(uid)
            error_info=""
            rt = ecode.OK
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get pseudo_bs_single_info failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,all=all),error_info)
import MySQLdb
class CityWifiInfos1:
    def GET(self):
        """
        input:
        beijing
        output:
        all
        """
        allsafe=[]
        alldanger=[]
        rt=ecode.FAILED
        try:
            i = ws_io.ws_input(['city'])
            cityname=i['city']
            # 北京
            # **************************************************************************************************
            # conn=MySQLdb.connect(host='111.204.189.58',user='root',passwd='1234',db='mobile',port=3306)
            conn=MySQLdb.connect(host='122.13.138.146',user='root',passwd='1234',db='mobile1',port=3306)
            cur=conn.cursor()

            if cityname=="beijing":
                cur.execute("select * from beijing_all")
                for i in cur.fetchall():
                    allsafe.append(i)
                cur.execute("select * from beijing_danger")
                for i in cur.fetchall():
                    alldanger.append(i)
            if cityname=="qingdao":
                cur.execute("select * from qingdao_all")
                for i in cur.fetchall():
                    allsafe.append(i)
                cur.execute("select * from qingdao_danger")
                for i in cur.fetchall():
                    alldanger.append(i)
            if cityname=="guangzhou":
                cur.execute("select * from guangzhou_all")
                for i in cur.fetchall():
                    allsafe.append(i)
                cur.execute("select * from guangzhou_danger")
                for i in cur.fetchall():
                    alldanger.append(i)
            cur.close()
            conn.close()
            # **************************************************************************************************
            error_info=""
            rt = ecode.OK
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get  beijing wifi infos failed ')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,all_all=allsafe,all_danger=alldanger),error_info)

# class CityWifiInfos2:
#     def GET(self):
#         """
#         input:
#         qingdao
#         output:
#         all
#         """
#         rt=ecode.FAILED
#         allsafe=[]
#         alldanger=[]
#         try:
#             i = ws_io.ws_input(['city'])
#             cityname=i['city']
#             # 青岛
#             # **************************************************************************************************
#             # conn=MySQLdb.connect(host='111.204.189.58',user='root',passwd='1234',db='mobile',port=3306)
#             conn=MySQLdb.connect(host='122.13.138.146',user='root',passwd='1234',db='mobile1',port=3306)
#             cur=conn.cursor()
#
#             if cityname=="qingdao":
#                 cur.execute("select * from qingdao_all")
#                 for i in cur.fetchall():
#                     allsafe.append(i)
#                 cur.execute("select * from qingdao_danger")
#                 for i in cur.fetchall():
#                     alldanger.append(i)
#             cur.close()
#             conn.close()
#             # **************************************************************************************************
#             error_info=""
#             rt = ecode.OK
#         except Exception as e:
#             rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
#             logging.error('get  qingdao wifi infos failed ')
#             error_info = str(traceback.format_exc()).replace("\n"," ")
#         return ws_io.ws_output(dict(rt=rt.eid,all_all=allsafe,all_danger=alldanger),error_info)
# class CityWifiInfos3:
#     def GET(self):
#         """
#         input:
#         guangzhou
#         output:
#         all
#         """
#         rt=ecode.FAILED
#         allsafe=[]
#         alldanger=[]
#         try:
#             i = ws_io.ws_input(['city'])
#             cityname=i['city']
#             # 广州
#             # **************************************************************************************************
#             # conn=MySQLdb.connect(host='111.204.189.58',user='root',passwd='1234',db='mobile',port=3306)
#             conn=MySQLdb.connect(host='122.13.138.146',user='root',passwd='1234',db='mobile1',port=3306)
#             cur=conn.cursor()
#
#             if cityname=="guangzhou":
#                 cur.execute("select * from guangzhou_all")
#                 for i in cur.fetchall():
#                     allsafe.append(i)
#                 cur.execute("select * from guangzhou_danger")
#                 for i in cur.fetchall():
#                     alldanger.append(i)
#             cur.close()
#             conn.close()
#             # **************************************************************************************************
#             error_info=""
#             rt = ecode.OK
#         except Exception as e:
#             rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
#             logging.error('get  guangzhou wifi infos failed ')
#             error_info = str(traceback.format_exc()).replace("\n"," ")
#         return ws_io.ws_output(dict(rt=rt.eid,all_all=allsafe,all_danger=alldanger),error_info)

# all statistics
class CityWifiInfos:
    def GET(self):
        """
        input:
        "all"
        output:
        all
        """
        rt=ecode.FAILED
        alls={}
        all_dangerous=[]
        try:
            i = ws_io.ws_input(['city'])
            cityname=i['city']
            # **************************************************************************************************
            # conn=MySQLdb.connect(host='111.204.189.58',user='root',passwd='1234',db='mobile',port=3306)
            conn=MySQLdb.connect(host='122.13.138.146',user='root',passwd='1234',db='mobile1',port=3306)
            cur=conn.cursor()
            if cityname=="all":
                cur.execute("select count(*) from all_all")
                safe=cur.fetchone()[0]
                cur.execute("select count(*) from all_danger")
                danger=cur.fetchone()[0]


                cur.execute("select count(*) from beijing_all")
                safe1=cur.fetchone()[0]
                cur.execute("select count(*) from beijing_danger")
                danger1=cur.fetchone()[0]

                cur.execute("select count(*) from qingdao_all")
                safe2=cur.fetchone()[0]
                cur.execute("select count(*) from qingdao_danger")
                danger2=cur.fetchone()[0]

                cur.execute("select count(*) from guangzhou_all")
                safe3=cur.fetchone()[0]
                cur.execute("select count(*) from guangzhou_danger")
                danger3=cur.fetchone()[0]

                alls={
                    "all":[safe+danger,safe,danger],
                    "beijing":[safe1+danger1,safe1,danger1],
                    "qingdao":[safe2+danger2,safe2,danger2],
                    "guangzhou":[safe3+danger3,safe3,danger3]
                }
            cur.close()
            conn.close()

            conn=MySQLdb.connect(host='122.13.138.146',user='root',passwd='1234',db='mobile1',port=3306)
            cur=conn.cursor()
            cur.execute("select ssid,mac from all_danger")
            for i in cur.fetchall():
                all_dangerous.append(i)
            # **************************************************************************************************
            cur.close()
            conn.close()
            error_info=""
            rt = ecode.OK
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get all wifi infos failed ')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,all=alls,all_dangerous=all_dangerous),error_info)
