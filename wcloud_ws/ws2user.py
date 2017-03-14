# -*- coding: utf8 -*-

import web
import logging
import sha
import json
import user_db
import dev_db
import log_db
import session_db
import strategy_db
import ws_io
import ecode
import send_sms
import captcha_mng
import user_ldap
import org
import config
import time
import string
import user_ldap
import contact_db
import admin_db
import base_db
# import trace
import re
import datetime
import math
import random   #+++20150402
import captcha_db   #+++20150403
import zlib   #+++20150428
import re_cmd_db   #+++20150611
#+++ 20150709
import baseStation
#+++ 20150716
import trace_db
#+++ 20150906
import threading
import jpype
from time import sleep
# +++20151103 存入管理员操作日志
import log_web_db
# +++20160119 在线统计表
import online_statistics_db
import op_user_online
import Logger
import json
import traceback
import operation
global ldap_base_dn
ldap_base_dn = "dc=test,dc=com"


class Reg:
    #{{{
    def POST(self):
        """
        input:
            uid: user id
            cid: captcha id
            cvalue: captcha value
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['uid','cid','cvalue'])
            if not i:
                raise ecode.WS_INPUT

            org_config = org.get_config()
            if config.get('is_org') and org_config['auth_mode'] == org.AUTH_LDAP:
                raise ecode.UAUTH_NOT_ALLOW_OP

            if config.check_debug_acc( i['uid']) and i['cvalue'] == config.DEBUG_CVALUE:
                pass
            else:
                if not captcha_mng.check_captcha(i['cid'], i['cvalue']):
                    raise ecode.CAPTCHA_ERROR

            if not send_sms.check_pnumber( i['uid']) :
                raise ecode.ERROR_PNUMBER

            if user_db.is_verified( i['uid']) :
                raise ecode.USER_EXIST

            tmppw = config.make_pw()
            user_db.create( i['uid'], sha.new(tmppw).hexdigest() )

#             send_sms.send_inital_pw( i['uid'], tmppw)

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('user reg.')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}

#+++20150403
class Captcha:
    def GET(self):
        """
        input:
            uid: user id
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['uid'])
            if not i:
                raise ecode.WS_INPUT
            user = user_db.get_user_info_by_uid(i["uid"])
            if not user:
                raise ecode.USER_NOT_EXIST
            #判断请求是否合法
            old_captcha=captcha_db.get_captcha(i['uid'])
            if old_captcha != '':
                raise ecode.CAPTHCA_IS_SENDED   #20160105如果当前存在验证码，非法请求
            #短信内容
            ran1=random.randint(100,999)
            ran2=random.randint(100,999)
            captcha=str(ran1)+str(ran2)
            logging.error(captcha)

            # ids=str(int(time.time()*1000))   #13位时间戳
            if not send_sms.send_sms_captcha(i['uid'], "verificationcode:"+captcha):
                raise ecode.SMS_TEMP_ERROR
            else:   #当发送验证码成功后，将信息存入redis数据库
                # captcha_str=ids+':'+captcha
                if not captcha_db.add_captcha(i['uid'], captcha):
                    raise ecode.CREATE_CAPTHCA_FAIL

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('user captcha.')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)


class Login:
    #{{{
    def POST(self):
        """
        input:
            uid: user id
            pw: password
            dev_id:
        output:
            rt: error code
            sid: session id
            need_mod_pw: need modify passwd
        """
        rt = ecode.FAILED
        sid = ''
        need_mod_pw = 0

        try:
            i = ws_io.ws_input(['uid','pw','dev_id'])
            if not i:
                raise ecode.WS_INPUT
            logging.error("这个函数的输入是"+str(i))
            # +++20150819 调整登陆逻辑
            #非web端个人版登录
            if i['dev_id']!='web':
                if not user_db.check_pw( i['uid'], sha.new(i['pw']).hexdigest()):   #验证密码
                    raise ecode.USER_AUTH
                else:   #密码验证通过，登陆成功
                    devs = user_db.devs(i['uid'])
                    if devs!=None and len(devs)>0:
                        user_dev_id = devs[0]
                        if user_dev_id!=i['dev_id']:
                            raise ecode.NOT_PERMISSION
                    else:
                        if dev_db.is_has_dev(i['dev_id']):
                            dev_cur_user = dev_db.get_cur_user(i['dev_id'])
                            if dev_cur_user!=None and dev_cur_user!='':
                                if dev_cur_user!=i['uid']:
                                    raise ecode.NOT_PERMISSION

                    user = user_db.get_user_info_by_uid(i['uid'])
                    user_db.verified( i['uid'])
                    user_db.pw_exp( i['uid'], False)

                    user_db.add_dev( i['uid'], i['dev_id'])
                    dev_db.add_dev( i['dev_id'], i['uid'])
                    #读取最后一次上传的地理位置坐标和时间，写入文件中
                    loc = dev_db.get_loc(i['dev_id'])
                    upt = user_db.get_last_update(user['key'])
                    value = loc['lon']+":"+loc['lat']+":offline"
                    trace_db.set(i['uid'],upt,value)
                    if user_db.is_pw_exp( i['uid']):
                        need_mod_pw = 1

                    # 用户上线之后的操作
                    user_db.online_op(user['key'])
                    # 修改用户的在线时间等属性
                    change_online_state(user['key'])
                    # 修改用户的活跃度
                    change_liveness(user)
                # create session
            sid = session_db.user.create( i['uid'], i['dev_id']
                        , web.ctx.ip)
            if not sid:
                raise ecode.SDB_OP

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error("user login")
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,sid=sid,need_mod_pw=need_mod_pw),error_info)
    #}}}


class LoginSms:
    def POST(self):
        """
        input:
            uid: user id
            pw: captcha
            dev_id:
        output:
            rt: error code
            sid: session id
            need_mod_pw: need modify passwd
        """
        rt = ecode.FAILED
        sid = ''
        need_mod_pw = 0

        try:
            org_config = org.get_config()
            if config.get('is_org') and org_config['auth_mode'] == org.AUTH_LDAP:
                uldap = user_ldap.create_ldap( ip = org_config['ldap_host']
                                                       , port = org_config['ldap_port']
                                                       , base_dn = org_config['ldap_base_dn']
                                                       , user_dn = org_config['ldap_user_dn']
                                                       , pw = org_config['ldap_pw']
                                                       , at_uid = org_config['ldap_at_uid']
                                                       , at_allow_use = org_config['ldap_at_allow_use']
                                                       , at_pnumber = org_config['ldap_at_pnumber']
                                                       , at_email = org_config['ldap_at_email'])

            i = ws_io.ws_input(['uid','pw','dev_id'])
            if not i:
                raise ecode.WS_INPUT
            #客户端登录

            cap=captcha_db.get_captcha(i['uid'])
            if cap != '':
                if cap!=i['pw']:   #captcha failed
                    raise ecode.CAPTHCA_ERROR
                else:   #captcha success
                    # #whether first time to login or not
                    # if not dev_db.is_has_user(i['uid']):
                    if not uldap.is_has_pnumber(i['uid']):
                        raise ecode.USER_UN_REGISTER
                    #user has been registered , now first time to login
                    #+++20160105 verify device
                    devs = user_db.devs(i['uid'])
                    if devs!=None and len(devs)>0:
                        user_dev_id = devs[0]
                        if user_dev_id!=i['dev_id']:
                            raise ecode.NOT_PERMISSION
                    else:
                        if dev_db.is_has_dev(i['dev_id']):
                            dev_cur_user = dev_db.get_cur_user(i['dev_id'])
                            if dev_cur_user!=None and dev_cur_user!='':
                                if dev_cur_user!=i['uid']:
                                    raise ecode.NOT_PERMISSION
                    user_db.verified( i['uid'])
                    user_db.pw_exp( i['uid'], False)

                    user_db.add_dev( i['uid'], i['dev_id'])
                    dev_db.add_dev( i['dev_id'], i['uid'])

                    user = user_db.get_user_info_by_uid(i['uid'])
                    # 用户上线之后的操作
                    user_db.online_op(user['key'])
                    post_online_status(user['uid'])
                    op_user_online.change_online_state(user['key'])
                    op_user_online.change_liveness(user)

                    #读取最后一次上传的地理位置坐标和时间，写入文件中
                    loc = dev_db.get_loc(i['dev_id'])
                    upt = user_db.get_last_update(user['key'])
                    value = loc['lon']+":"+loc['lat']+":offline"
                    trace_db.set(i['uid'],upt,value)
                    if user_db.is_pw_exp( i['uid']):
                        need_mod_pw = 1
                    # create session
                    sid = session_db.user.create( i['uid'], i['dev_id']
                                , web.ctx.ip)
                    logging.error("create sid")
                    if not sid:
                        raise ecode.SDB_OP

                    # +++20151029 加入登录时间置位逻辑
                    user_db.get_onlinetime(user['key'])
                    onlinestate1=user_db.get_onlinestate(user['key'])
                    liveness = long(onlinestate1['online'])*3650-(long(onlinestate1['online'])+long(onlinestate1['outline']))
                    user_db.set_liveness(i['uid'],liveness)
                    rt = ecode.OK
                    error_info = ""
            else:
                raise ecode.NEED_CAPTCHA #如果验证码不存在，则提示需要验证码

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('user login')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,sid=sid,need_mod_pw=need_mod_pw),error_info)

class ForgetPW:
    #{{{
    def POST(self):
        """
        input:
            uid:
            cid:
            cvalue:

        output:
            rt: error code
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['uid','cid','cvalue'])
            if not i:
                raise ecode.WS_INPUT

            org_config = org.get_config()
            if config.get('is_org') and org_config['auth_mode'] == org.AUTH_LDAP:
                raise ecode.UAUTH_NOT_ALLOW_OP

            if config.check_debug_acc( i['uid']) and i['cvalue'] == config.DEBUG_CVALUE:
                pass
            else:
                if not captcha_mng.check_captcha(i['cid'], i['cvalue']):
                    raise ecode.CAPTCHA_ERROR

            if not user_db.is_verified( i['uid']) :
                raise ecode.USER_NOT_EXIST

            tmppw = config.make_pw()
            user_db.set_pw( i['uid'], sha.new(tmppw).hexdigest() )
            user_db.pw_exp( i['uid'], True)
            send_sms.send_new_passwd( i['uid'], tmppw)

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('forgetpw')
            error_info = str(traceback.format_exc()).replace("\n"," ")

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

        try:
            i = ws_io.ws_input(['sid','oldpw','newpw'])
            if not i:
                raise ecode.WS_INPUT

            org_config = org.get_config()
            #if config.get('is_org') and org_config['auth_mode'] == org.AUTH_LDAP:
                #raise ecode.UAUTH_NOT_ALLOW_OP

            if not config.check_pw_rule( i['newpw']):
                raise ecode.PW_RULE

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if not user_db.check_pw( user
                    , sha.new(i['oldpw']).hexdigest()):
                raise ecode.OLD_PW_ERROR

            user_db.set_pw( user, sha.new(i['newpw']).hexdigest())

            if user_db.is_pw_exp( user):
                user_db.pw_exp( user, False)

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('setpw')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}


class SendCmd:
    #{{{
    def POST(self):
        """
        input:
            sid:
            devs:
            cmd:
        output:
            rt: error code
            offline_exist:0 不存在,1 存在 离线用户
        """
        rt = ecode.FAILED
        offline_exist = 0
        try:
            i = ws_io.ws_input(['cmd','devs','sid','uid'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            # +++20150909 将检查管理员权限前提
            if not admin_db.is_has_admin(user) and 'admin' != user:
                raise ecode.NOT_PERMISSION

            devs=json.loads(i['devs'])

            # +++20150909 将检查用户离线状态的遍历独立
            offline_exist = 0
            for dev_id in devs:
                uid = dev_db.get_cur_user(dev_id)
                if not user_db.is_my_dev(uid,dev_id):
                    logging.error("dev_id is not belonging to uid,uid : %s",uid)
                    continue
                dev_sid = session_db.user.get_sid(uid,dev_id)
                if not config.is_sid_on_push_server(dev_sid):
                    offline_exist = 1
                    break
                else:
                    continue

            #+++ 20150611   改 20150709 #对于推送通知，不需要反馈（手机没做）
            if i['cmd'][0:3]!='url':
                logging.error("开始存储命令")
                if not re_cmd_db.create(user,devs,i['cmd'],"cmds"):
                    raise ecode.USER_EXIST   #操作太频繁
            send_thread = threading.Thread(target=send_cmd_thread,args=(devs,i['cmd']))
            send_thread.start()
#                     #+++ 20150512 for 清除策略
#                     if i['cmd']=='qccl':
#                         cur_user=dev_db.get_cur_user(dev_id)
#                         stra_ids=dev_db.get_strategy_ids(cur_user)
#                         for stra in stra_ids:
#                             stra_id=stra["strategy_id"]
#                             if strategy_db.is_has_strategy(stra_id):
#                                 logging.warn("mod related strategy's users strategy_id : %s",stra_id)
#                                 if not strategy_db.del_user_of_users(stra_id, cur_user):
#                                     continue
#                         dev_db.remove_strategy(cur_user)  #+++20150629 删除dev_db

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('send cmd')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        # 日志记录
        op_user=session_db.user.get_user( i['sid'], web.ctx.ip)
        if str(i['cmd'][0:3])=="url":
            op_type=operation.HOME_pushinfo.type
            op_desc=operation.HOME_pushinfo.desc
        if str(i['cmd'])=="lockscreen":
            op_type=operation.HOME_lockphone.type
            op_desc=operation.HOME_lockphone.desc
        if str(i['cmd'])=="unlockscreen":
            op_type=operation.HOME_unlockphone.type
            op_desc=operation.HOME_unlockphone.desc
        if str(i['cmd'][0:13])=="chg_screen_pw":
            op_type=operation.HOME_lockpw.type
            op_desc=operation.HOME_lockpw.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,str(i['uid']),op_time ,op_type, op_desc, op_result )
        return ws_io.ws_output(dict(rt=rt.eid,offline_exist=offline_exist),error_info)
    #}}}

# +++20150909 检查到离线用户之后主线程返回，子线程继续处理在线用户的推送
def send_cmd_thread(devs,cmd):
    for dev_id in devs:
        uid = dev_db.get_cur_user(dev_id)
        if not user_db.is_my_dev( uid,dev_id):
            logging.error("dev_id is not of uid,dev_id:%s ,uid : %s",dev_id, uid)
            continue
        dev_db.new_cmd(dev_id,cmd)
        dev_sid = session_db.user.get_sid( uid,dev_id)
        if not config.notify_by_push_server(dev_sid,'cmd'):
            continue

# +++ 20150827 选择全部发送指令
class SendAllCmd:
    #{{{
    def POST(self):
        """
        input:
            sid:
            need_del_devs:["xxx","xxx"]
            cmd:
        output:
            rt: error code
            offline_exist:0不存在，1存在
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['sid','need_del_devs','cmd'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            # 检验管理员的权限
            if 'admin' != user:
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION

            need_del_devs = json.loads(i['need_del_devs'])
            selected_tree_users = user_db.get_selected_uids(user)
            selected_tree_devs = []
            for uid in selected_tree_users:
                selected_tree_devs += user_db.devs(uid)

            count = len(selected_tree_devs)-1
            while count>=0:
                item = selected_tree_devs[count]
                if item in need_del_devs:
                    selected_tree_devs.remove(item)
                count -= 1

            # +++20150910 加入提前检验离线用户逻辑
            offline_exist = 0
            for dev_id in selected_tree_devs:
                uid = dev_db.get_cur_user(dev_id)
                if not user_db.is_my_dev(uid,dev_id):
                    logging.error("dev_id is not belonging to uid,uid : %s",uid)
                    continue
                dev_sid = session_db.user.get_sid(uid,dev_id)
                if not config.is_sid_on_push_server(dev_sid):
                    offline_exist = 1
                    break
                else:
                    continue

            #+++ 20150611   改 20150709 #对于推送通知，不需要反馈（手机没做）
            if i['cmd'][0:3]!='url':
                logging.error("开始存储命令")
                if not re_cmd_db.create(user,selected_tree_devs,i['cmd'],"cmds"):
                    raise ecode.USER_EXIST   #操作太频繁
            send_thread = threading.Thread(target=send_cmd_thread,args=(selected_tree_devs,i['cmd']))
            send_thread.start()
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('send all cmd')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        # op_user=session_db.user.get_user( i['sid'], web.ctx.ip)
        # op_type=operation.HOME_pushinfo.type
        # op_desc=operation.HOME_pushinfo.desc
        # op_result=rt.desc
        # op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        # log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )

        return ws_io.ws_output(dict(rt=rt.eid,offline_exist=offline_exist),error_info)

    #}}}

class SendCmdAndRs:
    #{{{
    def POST(self):
        """
        input:
            sid:
            dev_id:
            cmd:
            flog:
            res:
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['cmd','dev_id','sid','res'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

#             if config.get('is_org') and org.get_config()['admin'] == user:
#                 user = dev_db.get_cur_user( i['dev_id'])
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            if admin_db.is_has_admin(user) or 'admin' == user:
                user = dev_db.get_cur_user( i['dev_id'])

            if not user_db.is_my_dev( user, i['dev_id']):
                raise ecode.NOT_PERMISSION

            dev_sid = session_db.user.get_sid( user, i['dev_id'])

            dev_db.new_cmd_and_rs( i['dev_id'], i['cmd'],i['flog'],i['res'])

            config.notify_by_push_server(dev_sid,'cmd')

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('send CmdAndRs')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}
# 设置设备管控命令标识位
class SetCmdRespons:
    #{{{
    def POST(self):
        """
        input:
            sid:
            info: wifi/bluetooth/camera/tape/gps/mobiledata/usb_connect/usb_debug
            results:  the respons
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['results','info','sid'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            user,dev_id = session_db.user.get_user_and_dev( i['sid']
                    , web.ctx.ip)
            if not user_db.is_my_dev( user, dev_id):
                raise ecode.NOT_PERMISSION

            dev_db.set_rs( dev_id,i['info'],i['results'])

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('set cmd respons')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}
class GetCmdRespons:
    #{{{
    def GET(self):
        """
        input:
            sid:
            dev_id:
            info: wifi/bluetooth/camera/tape/gps/mobiledata/usb_connect/usb_debug
        output:
            rt: error code
            rs:
        """
        rt = ecode.FAILED
        res = 0

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT

            if i.has_key('dev_id'):
                dev_id = i['dev_id']
                user = session_db.user.get_user( i['sid'], web.ctx.ip)
            else:
                user,dev_id = session_db.user.get_user_and_dev( i['sid']
                        , web.ctx.ip)

            if not user:
                raise ecode.NOT_LOGIN

#             if config.get('is_org') and org.get_config()['admin'] == user:
#                 user = dev_db.get_cur_user( i['dev_id'])
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            if admin_db.is_has_admin(user) or 'admin' == user:
                user = dev_db.get_cur_user( i['dev_id'])

            if not user_db.is_my_dev( user, dev_id):
                raise ecode.NOT_PERMISSION

            res = dev_db.get_rs( dev_id,i['info'])

            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get cmd respons')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,res=res),error_info)
    #}}}

class SetallRespons:
    #{{{
    def POST(self):
        """
        input:
            sid:
            dev_id:
            rs:  the respons
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['rs','dev_id','sid'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

#             if config.get('is_org') and org.get_config()['admin'] == user:
#                 user = dev_db.get_cur_user( i['dev_id'])
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            if admin_db.is_has_admin(user) or 'admin' == user:
                user = dev_db.get_cur_user( i['dev_id'])

            if not user_db.is_my_dev( user, i['dev_id']):
                raise ecode.NOT_PERMISSION

            dev_db.set_all_rs( i['dev_id'],i['rs'])

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('set cmd respons')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}

class GetCmds:
    #{{{
    def GET(self):
        """
        input:
            sid:
            dev_id:
        output:
            rt: error code
            cmds: {...}
        """
        rt = ecode.FAILED
        cmds = {}

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT

            if i.has_key('dev_id'):
                dev_id = i['dev_id']
                user = session_db.user.get_user( i['sid'], web.ctx.ip)
            else:
                user,dev_id = session_db.user.get_user_and_dev( i['sid']
                        , web.ctx.ip)

            if not user:
                raise ecode.NOT_LOGIN

            if config.get('is_org') and 'admin' == user:
                user = dev_db.get_cur_user( i['dev_id'])

            if not user_db.is_my_dev( user, dev_id):
                raise ecode.NOT_PERMISSION

            cmds = dev_db.get_cmds( dev_id )
            for cmd in cmds:
                dev_db.complete_cmd(dev_id,cmd['id'])
            #+++ 20150611 for reply send cmd
            re_cmd_db.get_cmd_ok(dev_id)
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get cmds')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,cmds=cmds),error_info)
    #}}}



class CompleteCmd:
    #{{{
    def POST(self):
        """
        input:
            sid:
            id:"cmd call id"
            results:
            info:
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','id','results','info'])
            if not i:
                raise ecode.WS_INPUT

            user,dev_id = session_db.user.get_user_and_dev( i['sid']
                    , web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if not user_db.is_my_dev( user, dev_id):
                raise ecode.NOT_PERMISSION

            dev_db.complete_cmd(dev_id, i['id'])

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('complete_cmd')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}

class GetStrategyById:
#{{{
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
            i = ws_io.ws_input(['sid','strategy_id'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)

            # org_config = org.get_config()
            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION

            strategy_id = i['strategy_id']
            strategy = strategy_db.get_strategy_by_id(strategy_id)
            # +++20150821策略内容瘦身，否则前台显示作用人群信息太慢
            getShortUsers(strategy)

            #如果是高级管理员，则加载所有作用人群
            if user == 'admin':
                strategy = strategy
            #如果是单位管理员，则只需加载该单位的作用人群
            elif admin_db.is_has_admin(user):
                oudn = admin_db.get_ou_by_uid(user)
                if oudn!=ldap_base_dn:
                    temp=[]
                    rg = re.compile(r'.*'+oudn+'.*')
                    for us in strategy['users']:
                        if rg.match(us['name']):
                            temp.append(us)
                    strategy['users'] = temp

            rt = ecode.OK
            error_info = ""


       except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get strategy by id')
            error_info = str(traceback.format_exc()).replace("\n"," ")
       op_user=session_db.user.get_user( i['sid'], web.ctx.ip)
       op_type=operation.STRATEGY_send.type
       op_desc=operation.STRATEGY_send.desc
       op_result=rt.desc
       op_time=time.strftime('%Y-%m-%d %H:%M:%S')
       log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )
       return ws_io.ws_output(dict(rt=rt.eid,strategy=strategy),error_info)

#}}}

class GetStrategyById1:
#{{{
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
            i = ws_io.ws_input(['sid','strategy_id'])
            if not i:
                raise ecode.WS_INPUT

            strategy_id = i['strategy_id']

            user,dev_id = session_db.user.get_user_and_dev( i['sid']
                    , web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
#             if not user_db.is_my_dev( user, dev_id):
#                 raise ecode.NOT_PERMISSION

            #过去所有的下发了的策略
            strategy = strategy_db.get_strategy_by_id1(strategy_id)
#            将策略ID标志位写为已读 true
            dev_db.strategy_is_read(dev_id,strategy_id)
            #+++ 20150616 for re_strategy
            re_cmd_db.get_stra_ok(user,'strategys')

            rt = ecode.OK
            error_info = ""

       except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get strategy by id')
            error_info = str(traceback.format_exc()).replace("\n"," ")

       return ws_io.ws_output(dict(rt=rt.eid,strategy=strategy),error_info)

#}}}

class GetStrategys:#
    #{{{
    def GET(self):
        """
        input:
            sid:
        output:
            rt: error code
            strategys: {...}
        """
        rt = ecode.FAILED
        strategys = {}

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN


            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
            # +++20151019 是数据库中的超级管理员时也加载所有策略
            oudn = admin_db.get_ou_by_uid(user)
            ou = admin_db.get_ou_friendly_name_by_uid(user)
            #如果是高级管理员，则加载所有的策略
            if user == 'admin' or oudn==ldap_base_dn:
                strategys = strategy_db.get_strategys()
                # +++20151024超级管理员
                for item in strategys:
                    if item['auth']=='admin' or item['auth']==ldap_base_dn:
                        item['isadmin'] = 1
                    else:
                        item['isadmin'] = 0
            #如果是单位管理员，则只需加载作用为其单位人群的策略
            elif admin_db.is_has_admin(user):
                strategys = strategy_db.get_strategys_by_admin(oudn)
                #将策略的作用人群描述修改为在当前可管理范围内
                none_stra=[]
                for strategy in strategys:
                    # +++20150805 对多余的用户进行清理，保证前面策略的加载速度
                    getShortUsers(strategy)
                    isadmin=0
                    if len(strategy['users'])>0:
                        temp=[]
#                         rg = re.compile(r'.*'+ou+'.*')
                        rg = re.compile(r'.*'+ou.split(",")[-1]+'.*')   #+++ 20150708
                        for ud in strategy['users']:
                            if rg.match(ud['name']):
                                temp.append(ud)
#                                 break
                        strategy['users'] = temp
                        if oudn == strategy['auth']:
                            isadmin=1
                    strategy['isadmin']=isadmin
                    if len(strategy['users'])==0:
                        none_stra.append(strategy)
                if len(none_stra)!=0:
                    for del_stra in none_stra:
                        strategys.remove(del_stra)
            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get strategys')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,strategys=strategys),error_info)
    #}}}

# +++20151023 加入从用户的权限生成oudn的过程
def generateOudn(qx):
    ous = qx.split(",")
    oudn = ""
    i = len(ous)-1
    while i>=0:
        oudn+="ou="+ous[i]+","
        i-=1
    org_config = org.get_config()
    oudn += org_config['ldap_base_dn']
    return oudn

def getShortUsers(strategy):
    ous = strategy['users']
    for ou in ous:
        users = ou['users']
        if len(users)>10:
            ou['users']=[]
            i=0
            while i<=10:
                ou['users'].append(users[i])
                i = i+1
        else:
            continue
    # return strategy


class GetUserStrategys:#
    #{{{
    def GET(self):
        """
        input:
            sid:
            uid:
        output:
            rt: error code
            strategys: {...}
        """
        rt = ecode.FAILED
        strategys = {}

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN



            #web端调用
            if user == 'admin' or admin_db.is_has_admin(user):
                ids = dev_db.get_strategy_ids(i['uid'])
                if ids=='no':
                    ids=user_db.get_strategy_ids(i['uid'])
                strategys = strategy_db.get_strategys_of_user_by_admin(ids)
                logging.error("************strategys is :%s",strategys)
            #客户端调用
            else:
                newids=[]
                ids = dev_db.get_strategy_ids(user)
                for stra_id in ids:
                    if(str(stra_id['is_read'])== "false"):
                        newids.append(stra_id)
                strategys = strategy_db.get_strategys_to_user(newids)

                #判定策略是否时间有效，如果无效则删除dev数据库中相应的id号
                dev_id = dev_db.get_dev_id_by_curuser(user)
                key = time.time()
                for stra in strategys:
                    et = time.mktime(time.strptime(str(stra['end']), '%Y-%m-%d %H:%M'))
                    if et < key: #如果策略结束时间比当前服务器时间早，则视为无效数据，需要删除dev_id中的ID号
                        dev_db.complete_strategy(dev_id,stra['strategy_id'])
                #将读取后的id对应标记位 is_read设置为true
                logging.error(user)
                logging.error(dev_id)
                logging.error(len(newids))
                for strid in newids:
                    dev_db.strategy_is_read(dev_id,strid['strategy_id'])
#                     logging.error(strid['strategy_id'])


            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get user strategys')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,strategys=strategys),error_info)
    #}}}

class GetUserNeedDelStrategys:#
    #{{{
    def GET(self):
        """
        input:
            sid:
            dev_id:
        output:
            rt: error code
            ids: [{"strategy_id": id}]
        """
        rt = ecode.FAILED
#         strategys = {}
        newids=[]
        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT

            user,dev_id = session_db.user.get_user_and_dev( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            ids = dev_db.get_strategy_ids(user)
            for stra_id in ids:
                if(str(stra_id['is_read'])== "delete"):
                    newids.append({"strategy_id":str(stra_id['strategy_id'])})
                    dev_db.complete_strategy(dev_id,str(stra_id['strategy_id']))
#             strategys = strategy_db.get_strategys_to_user(newids)

            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get user need delete strategys')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,ids=newids),error_info)
    #}}}

class CompleteStrategy:
    #{{{
    def POST(self):
        """
        input:
            sid:
            id:"strategy call id"
            results:
            info:
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','id','results','info'])
            if not i:
                raise ecode.WS_INPUT

            user,dev_id = session_db.user.get_user_and_dev( i['sid']
                    , web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if not user_db.is_my_dev( user, dev_id):
                raise ecode.NOT_PERMISSION

#             dev_db.complete_strategy(dev_id, i['id'])
            #给strategy_id写入已读标记
            dev_db.strategy_is_read(dev_id,i['id'])

            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('complete_strategy')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}

class DeleteUserStrategy:
    #{{{
    def POST(self):
        """
        input:
            sid:
            id:   "strategy call id"
        output:
            rt:  error code
        """

        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','id'])
            if not i:
                raise ecode.WS_INPUT

            user,dev_id = session_db.user.get_user_and_dev( i['sid']
                    , web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if not user_db.is_my_dev( user, dev_id):
                raise ecode.NOT_PERMISSION

            strategy_id = i['id']
            dev_db.complete_strategy(dev_id, strategy_id)
#             #+++ 20150703 for modify_stra_ok
#             re_cmd_db.modify_stra_ok(user,strategy_id,'modifyStrategys')
            #+++ 20150618 for 删除反馈,删除成功
            re_cmd_db.get_stra_ok(user,'delstrategys')
            #+++ 20150714 for 修改删除反馈
            re_cmd_db.mod_stra_ok(user,'modifyStrategys','DelStrategy')

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('delete_user_strategy')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        op_user=user
        op_type=operation.STRATEGY_del.type
        op_desc=operation.STRATEGY_del.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

    #}}}

class DeleteStrategy:
    #{{{
    def POST(self):
        """
        input:
            sid:
            ids: "strategy call id"
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','ids'])
            if not i:
                raise ecode.WS_INPUT
            #user是管理员
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            admin = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not admin:
                raise ecode.NOT_LOGIN


#             if user != org_config['admin']:
#                 raise ecode.NOT_PERMISSION
            if admin != 'admin':
                if not admin_db.is_has_admin(admin):
                    raise ecode.NOT_PERMISSION

            # +++ 20150916 查看当前要删除的策略作用人群中有无离线用户
            offline_exist = 0
            ids=json.loads(i['ids'])
            for str_id in ids:
                end_time=(strategy_db.get_strategy_by_id(str_id))['end']
                end=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M'))
                now_time=time.time()

                #+++20150917 如果策略已过期，直接执行下一个迭代，不计算离线人数
                if int(now_time)-int(end)>0:
                    strategy_db.del_strategy(str_id)
                    #+++ 20150925 加入删除ids中过期策略号的逻辑，如果不删除，后面的查找会报错
                    ids.remove(str_id)
                else:
                    strategy = strategy_db.get_strategy_by_id(str_id)
                    allous = strategy['users']
                    for ou in allous:
                        users = ou['users']
                        for user in users:
                            uid = user['uid']
                            devs = user_db.devs(uid)
                            if devs==[]:
                                continue
                            else:
                                dev_id = devs[0]
                                dev_sid = session_db.user.get_sid(uid,dev_id)
                                if config.is_sid_on_push_server(dev_sid):
                                    continue
                                else:
                                    offline_exist = 1
                                    break
            # +++20150916在加入推送线程之前先在数据库中写入re_cmd记录
            for iid in ids:
                #+++ 20150615 判断是否过期，过期则不必推送客户端消息
                users = (strategy_db.get_strategy_by_id(iid))['users']
                info='DelStrategy:'+str(iid)
                end_time=(strategy_db.get_strategy_by_id(iid))['end']
                end=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M'))
                now_time=time.time()

                #+++20150707 未激活用户
                if int(now_time)-int(end)>0:
                    strategy_db.del_strategy(iid)
                    for son in users:
                        sonusers = son['users']
                        for gson in sonusers:
                            if dev_db.is_has_user(gson['uid']):
                                dev_db.remove_expire_strategy(gson['uid'],iid)
                            else: #未激活
                                user_db.remove_expire_strategy(gson['uid'],iid)
                    users=[]
                    # +++ 20150917 如果策略已经过期，就从策略列表中直接删除，不用再放到线程里面
                    ids.remove(iid)
                else:
                    # +++为了统计需要推送的人数
                    need_fetch = 0
                    for son in users:
                        sonusers = son['users']
                        # +++20150823为了能够完全移除无设备用户
                        count = len(sonusers)-1
                        while count>=0:
                            gson = sonusers[count]
                            dev_id = dev_db.get_dev_id_by_curuser(gson['uid'])
                            if dev_id is None:
                                user_db.remove_expire_strategy(gson['uid'],iid)
                                sonusers.remove(gson)
                            else:
                                need_fetch+=1
                            count = count - 1
                    # +++ 20150823 判断需要添加到缓存表中的用户数量
                    if need_fetch>0:
                        #+++ 20150616 for re_stra
                        re_cmd_db.create(admin,users,info,"delstrategys")

            logging.warn("before:%s",str(ids))
            # +++ 20150916 加入开启删除策略线程
            delStrategyThread = threading.Thread(target=delStrategyFunc,args=(ids,))
            delStrategyThread.start()

            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('delete_strategy')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        op_user=admin
        op_type=operation.STRATEGY_del.type
        op_desc=operation.STRATEGY_del.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )

        return ws_io.ws_output(dict(rt=rt.eid,offline_exist=offline_exist),error_info)

    #}}}
# +++ 20150916 加入删除策略的线程函数
def delStrategyFunc(ids):
    for iid in ids:
        info='DelStrategy:'+str(iid)
        logging.warn("delStrategyFunc"+str(iid))
        users = (strategy_db.get_strategy_by_id(iid))['users']
        NotifyUsers(users,iid,info)


#如果策略作用于多个单位，修改策略时将原有策略中该管理员单位的作用人群全部删除，然后重新建立一条策略...
class ModifyUsersofStrategy:
    #{{{
    def POST(self):
        """
        input
            id: strategy_id
            sid:
        output
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','id'])
            if not i:
                raise ecode.WS_INPUT
            user = session_db.user.get_user( i['sid'], str(web.ctx.ip))
            if not user:
                raise ecode.NOT_LOGIN

            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION


            strategy = strategy_db.get_strategy_by_id(i['id'])
            ou = admin_db.get_ou_friendly_name_by_uid(user)
            rg = re.compile(r'.*'+ou+'.*')
            users = []
            delusers = []
            for us in strategy['users']:
                if not rg.match(us['name']):
                    users.append(us)
                else:
                    delusers.append(us)

            userdesc = []
            for ud in strategy['userdesc']:
                if not rg.match(ud['name']):
                    userdesc.append(ud)

            info='DelStrategy:'+str(i['id'])
            if not NotifyUsers(delusers,i['id'],info):
                raise ecode.PUSHSEVER_NOT_EXIST
            strategy_db.mod_users_of_strategy(i['id'],users,userdesc)

            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('Modify Users of Strategy ')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

    #}}}
class ModifyStrategy:
    #{{{
    def POST(self):
        """
        input
            id:strategyID
            sid
            强制管控 force
            开始时间 start
            结束时间 end
            作用经度 lon
            作用维度 lat
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
#         oldusers =[]
        try:
            i = ws_io.ws_input(['sid','id','force','users','userdesc','start','end','lon','lat','desc','radius','baseStationID','camera','bluetooth','wifi','tape','gps','mobiledata','usb_connect','usb_debug'])
            if not i:
                raise ecode.WS_INPUT
            strategy = {}
            """
            strategy={'end': '2014-03-12 08:00', 'wifi': 'wjy', 'lon': '12'
                      ,'bluetooth': 'bjy', 'start': '2014-03-11 08:00', 'camera': 'cfjy', 'radius': '10'
            ,'lat': '23'}
            """
            strategy['force'] = i['force']   #+++20150630加入强制管控标志位
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
            strategy['baseStationID']=i['baseStationID']

            user = session_db.user.get_user( i['sid'], str(web.ctx.ip))
            if not user:
                raise ecode.NOT_LOGIN


            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
            userdesc = json.loads(i['userdesc'])

            # +++改20150803修改用户的获取方式
            # users=json.loads(i['users'])
            selected_users = user_db.get_selected_users(user)
            users = getFormatUsers(selected_users)
            # +++20150916 加入离线检测逻辑 20151026改 对于不含有设备的用户跳过
            offline_exist = 0
            for item in selected_users:
                uid = item['uid']
                devs = user_db.devs(uid)
                if len(devs)>0:
                    dev_id = devs[0]
                    dev_sid = session_db.user.get_sid(uid,dev_id)
                    if config.is_sid_on_push_server(dev_sid):
                        continue
                    else:
                        offline_exist=1
                        break
                else:
                    continue
            # +++20150916 开启推送线程
            strategy_id = i['id']
            logging.warn("modify strategy offline_exist:%s",offline_exist)

            #+++ 20150714 修改策略梳理
            #1、获取修改前、后的用户,列表格式：[{'username':'','uid':''},...]
            newUsers=[]   #修改后
            for son in users:
                for gson in son['users']:
                    newUsers.append(gson)
            oldUsers = []  # 修改前
            strategy_id = strategy_id
            stra = strategy_db.get_strategy_by_id(strategy_id)
            for son in stra['users']:
                for gson in son['users']:
                    oldUsers.append(gson)
            # 2、获得待删除的用户和待修改（下发）的用户
            new_users = newUsers  # 待执行下发操作的用户
            del_users = []  # 待执行删除操作的用户
            for item in oldUsers:
                if item not in newUsers:
                    del_users.append(item)
            # 3、根据dev_id区分，找到未激活的用户，对user_db进行对应的操作
            del_list = []  # 确定是未激活用户后，需要从反馈列表中删除的用户id集合
            for son in new_users:  # 针对待下发用户中的未激活用户
                uid = son['uid']
                dev_id = dev_db.get_dev_id_by_curuser(uid)
                if dev_id is None:
                    # 未激活用户
                    if not user_db.is_has_strategy_id(uid, strategy_id):
                        user_db.add_strategy(uid, strategy_id)
                    del_list.append(son)
            for son in del_users:  # 针对待删除用户中的未激活用户
                uid = son['uid']
                dev_id = dev_db.get_dev_id_by_curuser(uid)
                if dev_id is None:
                    # 未激活用户
                    user_db.remove_expire_strategy(uid, strategy_id)
                    del_list.append(son)
            # 4、通过del_list将两种用户中的未激活用户清除掉
            for del_son in del_list:
                if del_son in del_users:
                    del_users.remove(del_son)
                if del_son in new_users:
                    new_users.remove(del_son)
            logging.warn("del_users and new_users without 未激活  is %s and %s", del_users, new_users)
            # 5、根据两种用户操作，修改策略后分别通知用户做相应的操作
            strategy_db.mod_strategy(strategy, users, userdesc)
            # 存入待删除的到反馈列表
            info_del = 'Mod_DelStrategy:' + str(strategy_id)
            re_cmd_db.create(user, del_users, info_del, "modifyStrategys")
            # 存入待下发的到反馈列表
            info_new = 'Mod_NewStrategy:' + str(strategy_id)
            re_cmd_db.create(user, new_users, info_new, "modifyStrategys")

            modify_stra_thread = threading.Thread(target=modify_stra_method,args=(strategy_id,new_users,del_users,user))
            modify_stra_thread.start()

#             #将策略写入数据库strategy_db
#             users=json.loads(i['users'])
#             userdesc = json.loads(i['userdesc'])
#             strategy_id = i['id']
#             #获取策略原有的作用人群
#             stra = strategy_db.get_strategy_by_id(strategy_id)
#             oldUsers=[]
#             for im in stra['users']:
#                 for item in im['users']:
#                     oldUsers.append(item)
#
#             #唤醒设备与pushsever之间的连接
#             #dev_sid = session_db.user.get_sid( user, i['dev_id'])
#             info='ModStrategy:'+str(strategy_id)
#             #config.notify_by_push_server(dev_sid,info)
#             # 修改策略内容
#             strategy_db.mod_strategy(strategy,users,userdesc)
#             #获取一个用户的合集
#             newUsers = []
#             for item in users:
#                 sonusers = item['users']
#                 for gson in sonusers:
#                     newUsers.append(gson)
#             userAll = newUsers

#             for item in oldusers:
#                 if item not in newUsers:
#                     userAll.append(item)

#             NotifyUsers(users,strategy_id,info,oldusers)
#             re_cmd_db.create(user,userAll,info,"modifyStrategys")

#             #+++ 20150710 for re_stra
#             re_cmd_db.create(user,users,info,"strategys")
#             re_cmd_db.create(user,userAll,info,"modifyStrategys")
#             #+++ 20150706 for pre_stra
#             for del_user in del_list:
#                 re_cmd_db.modify_stra_ok(del_user,strategy_id,'modifyStrategys')
#             NotifyUsers(users,strategy_id,info,oldusers)

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('modify strategy')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        op_user=session_db.user.get_user( i['sid'], web.ctx.ip)
        op_type=operation.STRATEGY_mod.type
        op_desc=operation.STRATEGY_mod.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )
        return ws_io.ws_output(dict(rt=rt.eid,offline_exist=offline_exist),error_info)
    #}}}


def modify_stra_method(strategy_id,new_users, del_users,admin):
    # 通知用户修改策略
    NotifyUsersMod(new_users, strategy_id, del_users,admin)


#+++ 20150714 推送修改策略消息机制
def NotifyUsersMod(new_users,strategy_id,del_users,admin):
    for son in new_users:
        #下发操作
        uid=son['uid']
        dev_id = dev_db.get_dev_id_by_curuser(uid)
        dev_sid = session_db.user.get_sid(uid,dev_id)
        if dev_db.is_has_strategy_id(dev_id,strategy_id):  #如果未改之前的策略未到期
            dev_db.strategy_is_not_read(dev_id,strategy_id)
        else: #如果未改之前的策略已到期
            dev_db.add_strategy(dev_id,strategy_id)
        info='ModStrategy:'+str(strategy_id)
        config.notify_by_push_server(dev_sid,info)
    for son in del_users:
        #删除操作
        uid=son['uid']
        dev_id = dev_db.get_dev_id_by_curuser(uid)
        dev_sid = session_db.user.get_sid(uid,dev_id)
        if(config.is_sid_on_push_server(dev_sid)):
            dev_db.remove_expire_strategy(uid,strategy_id)
            info='DelStrategy:'+str(strategy_id)
            config.notify_by_push_server(dev_sid,info)
            #+++20150922 删除推送成功就删除缓存表中的用户
            re_cmd_db.modify_sms_stra_ok(uid,admin,"Mod_DelStrategy:"+strategy_id)

#+++ 20150701 for check modify result
class CheckModifyResult:
    #{{{
    def GET(self):
        """
            input:
                sid:
                info: 'ModStrategy:'+strategy_id;
            output:
                rt: error code
                left_users: [...]
        """
        rt=ecode.FAILED
        left_users= []
        try:
            i = ws_io.ws_input(['sid','info'])
            if not i:
                raise ecode.WS_INPUT

            uid = session_db.user.get_user( i['sid'], web.ctx.ip)

            if not uid:
                raise ecode.NOT_LOGIN

            if (uid=='admin') or admin_db.is_has_admin(uid):
#                 info_head=i['info'].split(":")[0]+':'
                strategy_id =i['info'].split(":")[1]

                #+++ 改 20150714 改20150922
                left_users = getLeftUsers(uid,strategy_id)
            else:
                raise ecode.NOT_PERMISSION

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('check modify result failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,left_users=left_users),error_info)
    #}}}

class ModifyStrategyBySms:
    #{{{
    def POST(self):
        """
        input:
            sid:
            info:
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','info'])
            if not i:
                raise ecode.WS_INPUT
            #user是管理员
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN


            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION

            strategy_id = i['info'].split(":")[1]
            #+++ 改 20150714

            # +++20150906 加入多线程修改策略逻辑
            # sendThread = threading.Thread(target=ModStrategyBySmsToUsers,args=(strategy_id,user,i['sid']))
            # sendThread.start()
            ModStrategyBySmsToUsers(strategy_id,user,i['sid'])
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('modify_strategy by sms')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        op_user=user
        op_type=operation.STRATEGY_mod.type
        op_desc=operation.STRATEGY_mod.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )
        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}

class DelModifyStraUsers:
    def GET(self):
        """
        input:
            sid:
            info:
        output:
            rt: error code
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['sid','info'])
            if not i:
                raise ecode.WS_INPUT

            uid = session_db.user.get_user( i['sid'], web.ctx.ip)

            if not uid:
                raise ecode.NOT_LOGIN


            if (uid=='admin') or admin_db.is_has_admin(uid):
#                 users=re_cmd_db.get_devs(uid+i['info'])
#                 for son in users:
#                     cur_user=son["uid"]
#                     re_cmd_db.complete_re_cmd(uid+i['info'])
                #+++ 20150710 改   修改取消，则未修改的用户不管了（以后可添加取消短信修改的逻辑）
                re_cmd_db.complete_re_cmd(uid+i['info'])
            else:
                raise ecode.NOT_PERMISSION

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('del re strategy failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)


class CompleteModify:
    #{{{
    def POST(self):
        """
        :input:
            sid
            strategy_id
            type 用户完成的操作类型，可以是直接将推送的信息发送回来Modify:NewStrategy或者Modify:DelStrategy
        :output:
            rt
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','id','type'])
            if not i:
                raise ecode.WS_INPUT

            user,dev_id = session_db.user.get_user_and_dev( i['sid']
                    , web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if not user_db.is_my_dev( user, dev_id):
                raise ecode.NOT_PERMISSION

            type = i['type']
            strategy_id = i['strategy_id']

            if(type=='Modify:NewStrategy'):
                dev_db.strategy_is_read(dev_id,strategy_id)
                #+++ 20150616 for re_strategy
                re_cmd_db.modify_stra_ok(user,'modifyStrategys')
            elif(type=='Modify:DelStrategy'):
                dev_db.complete_strategy(dev_id, i['id'])
                #+++ 20150618 for 删除反馈,删除成功
                re_cmd_db.modify_stra_ok(user,'modifyStrategys')

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('delete_user_strategy')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)

    #}}}

# +++ 20150731 修改前台的加载逻辑之后修改，现在不用从前台获取用户，只需获取作用范围描述
class SendStrategy:
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
            offline_exist:0不存在，1存在 +++20150910 标识有无离线用户
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','id','force','users','userdesc','start','end','lon','lat','desc','radius',
                                'baseStationID','camera','bluetooth','wifi','tape','gps','mobiledata','usb_connect','usb_debug'])
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
            strategy['force'] = i['force']  #+++20150630 for force Control
            strategy['types']=''   #+++ 20150506 for pre stra

            userdesc=json.loads(i['userdesc'])

            user = session_db.user.get_user( i['sid'], str(web.ctx.ip))

            if not user:
                raise ecode.NOT_LOGIN

            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
                else:
                    ouAuth = admin_db.get_ou_by_uid(user)
                    strategy['auth'] = ouAuth
            else:
                # +++20151023 在策略中加入一个字段来记录下发此策略的权限
                strategy['auth'] = "admin"
            # +++20150821为了提升下发策略的效率
            ou_selected_users = user_db.get_selected_users(user)
            logging.warn("ou_selected_users：%s",str(ou_selected_users))

            # +++20150910 遍历查询是否存在离线用户
            offline_exist = 0
            for son in ou_selected_users:
                uid = son['uid']
                dev_id = dev_db.get_dev_id_by_curuser(uid)
                dev_sid = session_db.user.get_sid(uid, dev_id)
                if not config.is_sid_on_push_server(dev_sid):
                    offline_exist = 1
                    break
                else:
                    continue

            users=getFormatUsers(ou_selected_users)
            #将策略ID写进dev-db中
            #将策略写入数据库strategy_db
            strategy_db.new_strategy(strategy,users,userdesc)
            # +++20150823 为了完全删除无设备用户,计算需要加入到缓存数据库中的人数
            need_fetch = 0
            for son in users:
                sonusers = son['users']
                count = len(sonusers)-1
                while count>=0:
                    gson = sonusers[count]
                    uid = gson['uid']
                    dev_id = dev_db.get_dev_id_by_curuser(uid)
                    if dev_id is None:
                        if not user_db.is_has_strategy_id(uid, i['id']):
                            user_db.add_strategy(uid,i['id'])
                        sonusers.remove(gson)
                    else:
                        need_fetch = need_fetch + 1
                    count = count-1
            #+++ 20150616 for re_stra
            # +++20150823 判断加入缓存表的用户数量
            logging.warn( "need fetch is %s",str(need_fetch))
            info='NewStrategy:'+str(i['id'])
            if need_fetch>0:
                logging.error("进入发送线程")
                re_cmd_db.create(user,users,info,"strategys")
                send_thread = threading.Thread(target=sendStrategyThreadFunc,args=(users,i['id']))
                send_thread.start()
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            strategy_db.del_strategy(i['id'])
            logging.error('send strategy')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        op_user=user
        op_type=operation.STRATEGY_send.type
        op_desc=operation.STRATEGY_send.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )
        return ws_io.ws_output(dict(rt=rt.eid,offline_exist=offline_exist),error_info)
    #}}}

# +++20150910 开子线程向用户推送信息并存储数据库
def sendStrategyThreadFunc(users,strategy_id):
        info='NewStrategy:'+str(strategy_id)
        #+++ 20150706 for pre_stra
        # for del_user in del_list:
        #     re_cmd_db.get_stra_ok(del_user,'strategys')
        NotifyUsers(users,strategy_id,info)

#+++20150801 获取格式化的选择用户
def getFormatUsers(selected_users):
    if len(selected_users)==0:
        return []
    groups = []
    i=0
    while i<len(selected_users):
        group = {"name":'','users':[]}
        group['name'] = selected_users[i]['oudn']
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
    return groups

class SendContacts:
    #{{{
    def POST(self):
        """
        input
            sid
            uids 所有接受方
            users:[uid1,uid2,...]联系人
        output
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','uids','users','flag'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], str(web.ctx.ip))
            if not user:
                raise ecode.NOT_LOGIN
            #+++ 改 20150803
            # uids=json.loads(i['uids'])
            uids = user_db.get_selected_users_simple(user)
            # +++改 20150801 +++ 改20160111 从后台获取现在选中的通讯录联系人
            # user_tree=json.loads(i['users'])
            selected_contacts = user_db.get_selected_users(user+"_contact")
            users = []
            # +++20151019 在contacts字段存储的users中加入一个标志位，区别是否强制覆盖
            flag = i['flag']
            for item in selected_contacts:
                users.append({"uid":item['uid'],"flag":flag})
            # +++20150812 将写入数据库的逻辑和推送判断逻辑分离 +++20150929改，不再向contact表中存储联系人信息
            starttime = time.time()
            for user_item in uids:
                uid = user_item['uid']
                dev_id = dev_db.get_dev_id_by_curuser(uid)
                user_db.add_contact(uid,users)
                if dev_id!=None:
                    dev_sid = session_db.user.get_sid( uid, dev_id)
                    #通知在线的设备联系人列表有变化
                    config.notify_by_push_server(dev_sid,'contacts')
                else:
                    #在通知联系人列表有变化的同时要向用户数据库中写入刚刚发送的联系方式
		            continue
            endtime = time.time()
            span = endtime-starttime
            print "发送通讯录历时"+str(span)
            # +++ 20160729 将数据库的查重插入逻辑添加到子线程中

            # +++ 20151102 将下发联系人用户存入缓存表中，查看日志时显示联系人的接收情况
            send_time = time.strftime('%Y-%m-%d %H:%M:%S')
            # 获取用户树
            base_dn = admin_db.get_ou_by_uid(user)
            user_tree = get_user_tree(selected_contacts,base_dn)
            log_web_db.add_log(user,uids,send_time,"send contacts",user_tree,0)
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            log_web_db.add_log(user,uids,send_time,"send contacts",user_tree,1)
            logging.error('send contacts')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        #日志记录
        # op_user=session_db.user.get_user( i['sid'], web.ctx.ip)
        # op_type=operation.CONTACTS_send.type
        # op_desc=operation.CONTACTS_send.desc
        # op_result=rt.desc
        # op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        # log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )
        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}

# def thread_add_contacts(uids,contacts):

def get_user_tree(selected_contacts,base_dn):
    group_users = get_formated_contacts(selected_contacts)
    uldap = getLdap()
    user_son_ous = uldap.get_ou_tree(base_dn)
    user_tree = {"oudn":base_dn,"ous":user_son_ous,"users":[]}
    # 先生成群组的oudn列表，遍历时更易查看存在性
    ou_list = []
    for group in group_users:
        ou_list.append(group['name'])
    #遍历用户树，查找并添加群组
    fill_tree_node(group_users,ou_list,user_tree)
    return user_tree

def fill_tree_node(group_users,ou_list,user_tree):
    oudn = user_tree['oudn']
    user_count = 0
    if(len(ou_list)>0):
        if(oudn in ou_list):
            for item in group_users:
                if item['name']==oudn:
                    users = item['users']
            user_tree['users'] = users
            user_count+=len(users)
            ou_list.remove(oudn)
        ous = user_tree["ous"]
        counter = len(ous)-1
        while counter>=0:
            ou = ous[counter]
            ou_user_count = fill_tree_node(group_users,ou_list,ou)
            if ou_user_count==0:
                ous.remove(ou)
            else:
                user_count+=ou_user_count
            counter-=1
    return user_count

def get_contact_users(contact_tree):
    all_users = []
    ous = contact_tree['ous']
    users = contact_tree['users']
    if(len(users)>0):
        for item in users:
            all_users.append({'uid':item['uid']})
    if(len(ous)>0):
        for item_ou in ous:
            all_users+=get_contact_users(item_ou)
    return all_users

def get_formated_contacts(selected_contacts):
    if len(selected_contacts)==0:
        return []
    groups = []
    i=0
    while i<len(selected_contacts):
        group = {"name":'','users':[]}
        group['name'] = selected_contacts[i]['oudn']
        j=i
        while j<len(selected_contacts):
            if(selected_contacts[j]['oudn']==selected_contacts[i]['oudn']):
                group['users'].append({'name':selected_contacts[j]['username'],'uid':selected_contacts[j]['uid']})
            else:
                i=j
                groups.append(group)
                break
            if j==len(selected_contacts)-1:
                i=j+1
                groups.append(group)
            j =j+1
    return groups

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
class GetContacts:#
    #{{{
    def GET(self):
        """
        input:
            sid:
        output:
            rt: error code
            contacts: [{name姓名,email电子邮件,job职位,department部门,pnumber电话号码},...]
        """
        rt = ecode.FAILED
        contacts = []

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            logging.error("用户是:%s",user)
            if not user:
                raise ecode.NOT_LOGIN

            contacts = user_db.get_contacts_by_uid(user)
            logging.error("用户的联系人信息:%s",str(contacts))
            #+++20151109 如果取到的联系人信息不为空，则清空联系人缓存区中的联系人信息
            if(len(contacts)>0):
                user_db.del_contact(user)
            # contacts = getLdapContact(uids)
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get contacts')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,contacts=contacts),error_info)
    #}}}

class DelContacts:#
    #{{{
    def POST(self):
        """
        input:
            sid:
            uid:
            contacts:[uids]
        output:
            rt: error code
#             contacts: [{name姓名,email电子邮件,job职位,department部门}]
        """
        rt = ecode.FAILED
        contacts = {}

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            # +++20151103将添加contacts和获取contacts的逻辑修改，全在数据库中进行存取
            # uids = user_db.get_contacts_by_uid(user);
            # contacts = getLdapContact(uids)
            contacts = user_db.get_contacts_by_uid(user)
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get contacts')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,contacts=contacts),error_info)
    #}}}

def getLdapContact(uids):
    #{{{
    contacts = []
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
    pnumbers = []
    for item in uids:
        #uids是一个dic类  参数uid['uid']
        contact = uldap.get_user(item['uid'])
        logging.error("ldap user:%s",str(contact))
        info = contact[1]
        dn = str(contact[0])
        if not dn:
            continue
        else:
            logging.error("dn:%s",dn)
            department = ''
            fenjie = dn.split(",");
            logging.error("fenjie:%s",str(fenjie))
            for son in fenjie:
                logging.error("son:%s",son)
                if son.find('ou')>=0:
                    department+=son[3:]+','
                else:
                    continue
            department = department[0:len(department)-1]

            uid = info[org_config['ldap_at_uid']]
            if type(uid) is list:
                uid = uid[0]

            username = ''
            if info.has_key(org_config['ldap_at_username']):
                username = info[org_config['ldap_at_username']]
                if type(username) is list:
                    username = username[0];

            pnumber = ''
            if info.has_key(org_config['ldap_at_pnumber']):
                pnumber = info[org_config['ldap_at_pnumber']]
                if type(pnumber) is list:
                    pnumber = pnumber[0];

            email = ''
            if info.has_key(org_config['ldap_at_email']):
                email = info[org_config['ldap_at_email']]
                if type(email) is list:
                    email = email[0];

            job = ''
            if info.has_key(org_config['ldap_at_job']):
                job = info[org_config['ldap_at_job']]
                if type(job) is list:
                    job = job[0];

            flag = 0
            if item.has_key("flag"):
                flag = int(item['flag'])

            if(item['uid'] in pnumbers):
                for contact in contacts:
                    if contact['pnumber']==item['uid']:
                        contact['flag'] = 1
            else:
                #+++ 20151019改 加入强制覆盖标志位
                one = {'name':username,'email':email,'job':job,'department':department,'pnumber':pnumber,'flag':flag}
                contacts.append(one)
                pnumbers.append(item['uid'])


    return contacts
    #}}}

class Loc:
    #{{{
    def GET(self):
        """
        input:
            sid:
            dev_id:
        output:
            rt: error code
            lon:
            lat:
        """
        rt = ecode.FAILED
        lon = '0'
        lat = '0'
#         upt = '0'

        try:
            i = ws_io.ws_input(['sid','dev_id'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            dev_id = i['dev_id']

            if not user:
                raise ecode.NOT_LOGIN

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP
            #高级管理员可以定位单个设备的地理位置，单位管理则不可以
            #高级管理员
            if 'admin' == user:
                user = dev_db.get_cur_user( i['dev_id'])

                if not user_db.is_my_dev( user, dev_id):
                    raise ecode.NOT_PERMISSION

                loc = dev_db.get_loc( dev_id)
                lon = loc['lon']
                lat = loc['lat']
#                 upt = loc['upt']

            #单位管理员
            elif  admin_db.is_has_admin(user):
                user = dev_db.get_cur_user( i['dev_id'])

                if not user_db.is_my_dev( user, dev_id):
                    raise ecode.NOT_PERMISSION
                lon = " "
                lat = " "
#                 upt = " "
            else:
                raise ecode.NOT_PERMISSION

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('loc')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,lon=lon,lat=lat),error_info)

    def POST(self):
        """
        input:
            sid:
            lon:
            lat:
            baseStationID: 基站地址
            offlinetime:客户端掉线的时间戳    毫秒级
            currenttime: 客户端当前的时间戳   毫秒级
            accuracy: 精度
        output:
            rt: error code 处理的时间都是时间戳     秒级
        """
        rt = ecode.FAILED
        dev_id = ""
        try:
            i = ws_io.ws_input(['lon','lat','sid'])
            if not i:
                raise ecode.WS_INPUT

            user,dev_id = session_db.user.get_user_and_dev( i['sid']
                    , web.ctx.ip)

            if not user:
                raise ecode.NOT_LOGIN

            if not user_db.is_my_dev( user, dev_id):
                raise ecode.NOT_PERMISSION

            user_info = user_db.get_user_info_by_uid(user)
            #活跃度
            starttime = user_db.get_onlinetime(user_info['key'])
            t=time.localtime()
            tt=datetime.datetime(t[0],t[1],t[2])
            currenttime = time.mktime(tt.timetuple())
            if starttime:
                sttime = datetime.datetime.utcfromtimestamp(starttime)
                cutime = datetime.datetime.utcfromtimestamp(currenttime)
                timediff=(cutime-sttime).days
                if int(timediff)==1:
                    onlinestate=user_db.get_onlinestate(user_info['key'])
                    onlinest=str(int(onlinestate['online'])+1)
                    user_db.set_onlinestate(user_info['key'],onlinest)
                elif int(timediff)>1:
                    onlinestate=user_db.get_onlinestate(user_info['key'])
                    onlinest=str(int(onlinestate['online'])+1)
                    outlinest=str(int(onlinestate['outline'])+int(timediff)-1)
                    logging.error('get_onlinestate:onlinest=%s;outlinest=%s',onlinestate['online'],onlinestate['outline'])
                    user_db.set_outlinestate(user_info['key'],onlinest,outlinest)
                # +++ 20150901 user_db中加入活跃度和最后在线时间的时间戳用来排序
                onlinestate1=user_db.get_onlinestate(user_info['key'])
                liveness = long(onlinestate1['online'])*3650-(long(onlinestate1['online'])+long(onlinestate1['outline']))
                user_db.set_liveness(user,liveness)
            #基站信息统计（未利用）
            if i.has_key('baseStationId'):
                base_db.add_base(i['lon'],i['lat'],i['baseStationId'])
            #存位置，for 丢失溯源(手机上传就存)
            key = time.time()
            value = i['lon']+':'+i['lat']+':online'
            trace_db.set(user,int(key),value)
            # +++20150901 设置更新时间的过程在这个函数里面，设置位置信息的时候同时就设置了last_update
            dev_db.set_loc( dev_id, i['lon'], i['lat'])
            user_db.set_last_update(user,str(int(time.time())))
            # +++20160119将在线状态上传
            post_online_status(user,time.time())
            rt = ecode.OK
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('loc des')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output_des(dict(rt=rt.eid),dev_id,error_info)
#     def POST(self):
#         """
#         input:
#             sid:
#             lon:
#             lat:
#             baseStationID: 基站地址
#             offlinetime:客户端掉线的时间戳    毫秒级
#             currenttime: 客户端当前的时间戳   毫秒级
#             accuracy: 精度
#         output:
#             rt: error code
#         处理的时间都是时间戳     秒级
#         """
#         rt = ecode.FAILED
#         try:
#             i = ws_io.ws_input(['lon','lat','sid'])
#             if not i:
#                 raise ecode.WS_INPUT
#
#             user,dev_id = session_db.user.get_user_and_dev( i['sid']
#                     , web.ctx.ip)
#             if not user:
#                 raise ecode.NOT_LOGIN
#
#             if not user_db.is_my_dev( user, dev_id):
#                 raise ecode.NOT_PERMISSION
# #             如果坐标是小于零的数则表示定位失败  抛出异常，否则则正常存储
# #             if float(i['lon'])<=0 or float(i['lon'])<=0:
# #                 raise ecode.LOC_FAILED
# #             else:
# #            offset=服务器当前时间-客户端当前时间（key - i['onlinetime']）
#             if i.has_key('baseStationId'):
#                 base_db.add_base(i['lon'],i['lat'],i['baseStationId'])
#             item = trace_db.get_last_option(user)
#             last_time = 0.0
#             last_lon = 0.0
#             last_lat = 0.0
#             dis = 0.0
#             key = time.time()
#             if i['currenttime']!='':
#                 currenttime = int(i['currenttime'])/1000
#             else:
#                 currenttime = key
# #             if i.has_key('currenttime'):
# #                 currenttime = int(i['currenttime'])/1000
# #             else:
# #                 currenttime =
#             dev_db.set_loc( dev_id, i['lon'], i['lat'])
# #             value = i['lon']+':'+i['lat']+':yes:'+str(currenttime)+':'+str(int(key)-int(currenttime))
#             value = i['lon']+':'+i['lat']+':online'
#
#             offvalue = ''
# #                获取当前时间 %Y-%m-%d %H:%M
# #                获取当前时间的时间戳 毫秒数
# #                如果客户端没有长时间移动，则半个小时记录一次地理位置
# #                如果移动比较频繁，则是地理坐标超过500米则记录一次数据
#             logging.error(user)
#
#             if item : #获取section的最后一条记录的时间  有记录  ontime为客户端定位的时间
# #                 last_lon,last_lat,status,ontime,offset = item[1].split(':')
#                 last_lon,last_lat,status = item[1].split(':')
#                 logging.error("old:"+str(item[0])+":"+str(item[1]))
#                 last_time = item[0]
#                 if status == "no": #如果上一条记录状态为离线，直接记录该条最新定位信息
#                     trace_db.set(user,int(key),value)
#                 else:   #如果上一条记录状态为在线
#                     if i['offlinetime']!='':#如果掉线时间不为空，即客户端重新上线
#                         offlinetime = int(i['offlinetime'])/1000
#                         offvalue = last_lon+":"+last_lat+":offline"
#                         offset = key - currenttime  #时间差为服务器当前时间和客户端上传时间之间的差值
#                         trace_db.set(user,int(offlinetime+offset),offvalue)
#                         trace_db.set(user,int(key),value)
#                     else: #如果掉线时间为空，即客户端与上一次定位之间一直在线,记录当前最新定位信息
#                         dis = distance(i['lon'],i['lat'],last_lon,last_lat)
#                         if float(last_lon)<=0.0 or float(last_lat)<=0.0:  #如果上一条记录定位失败的，
#                             if float(i['lon'])>0 and float(i['lat'])>0:   #且 本次定位是成功的，则记录下该条信息
#                                 trace_db.set(user,int(key),value)
#                         else: #如果上一次记录定位是成功的，则按时间和距离的规则来判定
#                             if distance(i['lon'],i['lat'],last_lon,last_lat)>=500:
#                                 #如果两次记录的距离大于500米则记录
#                                 trace_db.set(user,int(key),value)
#                             elif (float(key)-float(last_time))>= 30*60: #如果距离上次记录大于30分钟，则记录:
#                                 trace_db.set(user,int(key),value)
#             else: #如果没有记录 记录下当前的时间及坐标即可
#                 trace_db.set(user,int(key),value)
#             logging.error("new:"+str(key)+":"+value)
#             logging.error("offline:"+i['offlinetime']+":"+offvalue)
# #                 logging.error(last_time)
# #                 logging.error(key)
# #                 logging.error(last_lon)
# #                 logging.error(last_lat)
#             logging.error("distance:"+str(dis))
#
#             rt = ecode.OK
#         except Exception as e:
#             rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
#             logging.error('loc')
#
#         return ws_io.ws_output(dict(rt=rt.eid))
    #}}}

class GetLocAndCuruser:
    #{{{
    def GET(self):
        """
        input:
            sid:
            dev_id:
        output:
            rt: error code
            lon:
            lat:
        """
        rt = ecode.FAILED
        lon = '0'
        lat = '0'
        curuser=""

        try:
            i = ws_io.ws_input(['sid','dev_id'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            dev_id = i['dev_id']

            if not user:
                raise ecode.NOT_LOGIN

#             if config.get('is_org') and org.get_config()['admin'] == user:
#                 user = dev_db.get_cur_user( i['dev_id'])
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            if admin_db.is_has_admin(user) or 'admin' == user:
                user = dev_db.get_cur_user( i['dev_id'])

            if not user_db.is_my_dev( user, dev_id):
                raise ecode.NOT_PERMISSION

            loc = dev_db.get_loc( dev_id)
            curuser = dev_db.get_cur_user(dev_id)
            lon = loc['lon']
            lat = loc['lat']

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('loc')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,lon=lon,lat=lat,curuser=curuser),error_info)

    #}}}


class GetDevs:
    #{{{
    def GET(self):
        """
        input:
            sid:

        output:
            rt: error code
            devs: {...}
        """
        rt = ecode.FAILED
        devs = []

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            for dev in user_db.devs( user ):
                devs.append({'dev_id':dev
                    ,'model_number':dev_db.get_static_info(dev,'model_number')})

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get devs')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,devs=devs),error_info)
    #}}}



class DelMe:
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

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            user_db.del_user( user )
            session_db.user.del_by_sid( i['sid'], web.ctx.ip)

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('del me')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}





class GetAccInfo:
    #{{{
    def GET(self):
        """
        input:
            sid:

        output:
            rt: error code
            uid:
        """
        rt = ecode.FAILED
        uid = ''

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT

            uid = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not uid:
                raise ecode.NOT_LOGIN

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('GetAccInfo')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,uid=uid),error_info)
    #}}}


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

            session_db.user.del_by_sid( i['sid'], web.ctx.ip)

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('Logout')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}



class GetOnlineStatus:
    #{{{
    def GET(self):
        """
        input:
            sid:
            dev_id:
        output:
            rt: error code
            status: 0 not login, 1 login but offline, 2 online
        """
        rt = ecode.FAILED
        status = 0
        dev_sid=''

        try:
            i = ws_io.ws_input(['sid','dev_id'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP
            if admin_db.is_has_admin(user) or 'admin' == user:
                user = dev_db.get_cur_user( i['dev_id'])

            if not user_db.is_my_dev( user, i['dev_id']):
                raise ecode.NOT_PERMISSION

            dev_sid = session_db.user.get_sid( user, i['dev_id'])
            if dev_sid:
                status = 1
                if config.is_sid_on_push_server( dev_sid):
                    status = 2

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('GetOnlineStatus')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid, status=status,dev_sid=dev_sid),error_info)
    #}}}


class GetDevInfo:
    #{{{
    def GET(self):
        """
        input:
            sid:
            dev_id:

        output:
            rt: error code
            last_update:
        """
        rt = ecode.FAILED
        last_update = ''

        try:
            i = ws_io.ws_input(['sid','dev_id'])
            if not i:
                raise ecode.WS_INPUT

            admin = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not admin:
                raise ecode.NOT_LOGIN

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            if admin_db.is_has_admin(admin) or 'admin' == admin:
                user = dev_db.get_cur_user( i['dev_id'])
                user_info = user_db.get_user_info_by_uid(user)

            if not user_db.is_my_dev( user, i['dev_id']):
                raise ecode.NOT_PERMISSION

            last_update = user_db.get_last_update( user_info['key'])

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('GetAccInfo')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,last_update=last_update),error_info)
    #}}}


class DevStaticInfo:
    #{{{
    keys = ('firmware_version',
            'model_number',
            'version_number',
            'imei',
            'imei_version',
            'sim_supplier',
            'sim_sn',
            'sim_state',
            'signal_strength',
            'network_providers',
            'network_type',
            'phone_type',
            'call_status',
            'wifi_bssid',
            'wifi_ip_addr',
            'wifi_mac_addr',
            'wifi_rssi',
            'wifi_ssid',
            'wifi_network_id',
            'wifi_request_status',
            'wifi_conn_speed',
            'bluetooth_is_on',
            'bluetooth_is_search',
            'bluetooth_name',
            'bluetooth_addr',
            'bluetooth_status',
            'bluetooth_pair_dev',
            'battery_status',
            'battery_power',
            'battery_voltage',
            'battery_temperature',
            'battery_technology',
            'battery_life',
            'data_activity_status',
            'data_conn_status',
            'call_volume',
            'system_volume',
            'ring_volume',
            'music_volume',
            'tip_sound_volume',
            'longitude',
            'latitude',
            'pos_corrention_time')

    def GET(self):
        """
        input:
            sid:
            dev_id:
            all:1
            key1:1
            key2:1
            ...

        output:
            rt: error code
            key1:value1
            key2:value2
            ...
        """
        rt = ecode.FAILED
        kv = {}

        try:
            i = ws_io.ws_input(['sid','dev_id'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            if admin_db.is_has_admin(user) or 'admin' == user:
                user = dev_db.get_cur_user( i['dev_id'])

            if not user_db.is_my_dev( user, i['dev_id']):
                raise ecode.NOT_PERMISSION

            if i.has_key('all'):
                for k in self.keys:
                    kv[k] = dev_db.get_static_info( i['dev_id'], k)
            else:
                for k in i:
                    if k not in self.keys:
                        continue
                    kv[k] = dev_db.get_static_info( i['dev_id'], k)

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('DevStaticInfo')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        kv['rt'] = rt.eid
        return ws_io.ws_output(kv,error_info)


    def POST(self):
        """
        input:
            sid:
            key1:value1
            key2:value2
            ...

        output:
            rt: error code
            count: update success count
        """
        rt = ecode.FAILED
        count = 0

        try:
            i = ws_io.ws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT

            user,dev_id = session_db.user.get_user_and_dev( i['sid']
                    , web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            for k in i:
                if k not in self.keys:
                    continue
                dev_db.set_static_info( dev_id, k, i[k])
                count = count + 1

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('DevStaticInfo')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,count=count),error_info)
    #}}}



class DevAppInfo:
    #{{{
    def GET(self):
        """
        input:
            sid:
            dev_id:
        output:
            rt: error code
            apps: json([{},{}...])
        """
        rt = ecode.FAILED
        apps = ''
        not_install_apps = []

        try:
            i = ws_io.ws_input(['sid','dev_id'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            if admin_db.is_has_admin(user) or 'admin' == user:
                user = dev_db.get_cur_user( i['dev_id'])

            if not user_db.is_my_dev( user, i['dev_id']):
                raise ecode.NOT_PERMISSION
            user = dev_db.get_cur_user(i['dev_id'])
            apps = dev_db.get_app_info( i['dev_id'])
            not_install_apps = user_db.get_apps( user )
            if apps:
                for a in json.loads(apps):
                    not_install_apps.remove(a['app_id'])

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('DevAppInfo')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,apps=apps
            ,not_install_apps=not_install_apps),error_info)


    def POST(self):
        """
        input:
            sid:
            apps: json([{},{}...])

        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','apps'])
            if not i:
                raise ecode.WS_INPUT

            user,dev_id = session_db.user.get_user_and_dev( i['sid']
                    , web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if i['apps']:
                for a in json.loads(i['apps']):
                    user_db.add_app( user, a['app_id'] )

            dev_db.set_app_info( dev_id, i['apps'])

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('DevAppInfo')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}



class DevWebAppInfo:
    #{{{
    def GET(self):
        """
        input:
            sid:
            dev_id:

        output:
            rt: error code
            apps: json([{},{}...])
            not_install_apps: []
        """
        rt = ecode.FAILED
        apps = ''
        not_install_apps = []

        try:
            i = ws_io.ws_input(['sid','dev_id'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

#             if config.get('is_org') and org.get_config()['admin'] == user:
#                 user = dev_db.get_cur_user( i['dev_id'])
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            if admin_db.is_has_admin(user) or 'admin' == user:
                user = dev_db.get_cur_user( i['dev_id'])

            if not user_db.is_my_dev( user, i['dev_id']):
                raise ecode.NOT_PERMISSION

            apps = dev_db.get_web_app_info( i['dev_id'])
            not_install_apps = user_db.get_web_apps( user )
            if apps:
                for a in json.loads(apps):
                    not_install_apps.remove(a['app_id'])

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('DevWebAppInfo')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,apps=apps
            ,not_install_apps=not_install_apps),error_info)


    def POST(self):
        """
        input:
            sid:
            apps: json([{},{}...])

        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','apps'])
            if not i:
                raise ecode.WS_INPUT

            user,dev_id = session_db.user.get_user_and_dev( i['sid']
                    , web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if i['apps']:
                for a in json.loads(i['apps']):
                    user_db.add_web_app( user, a['app_id'] )

            dev_db.set_web_app_info( dev_id, i['apps'])

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('DevWebAppInfo')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}


class Log:
    #{{{
    def POST(self):
        """
        input:
            sid:
            logs:json( [{t:"",app:"",act:"",info:""},{}..])
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['logs'])
            if not i:
                raise ecode.WS_INPUT

            user,dev_id = session_db.user.get_user_and_dev( i['sid']
                    , web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            for l in json.loads(i['logs']):
                log_db.add_log(user,dev_id,l['t'],l['app'],l['act'],l['info'])

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('log')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)
    #}}}
def NotifyUsers(users,strategy_id,info,oldusers=[]):
    for son in users:
        sonusers = son['users']
        for gson in sonusers:
            uid = gson['uid']
            dev_id = dev_db.get_dev_id_by_curuser(uid)
            if dev_id is None:
                continue
            else:
                dev_sid = session_db.user.get_sid( uid, dev_id)
                #+++改 2015630 new 和  del 都不管是否发送成功，直接发下去，等待手机来取得时候结算
                if((info.split(':'))[0]=='NewStrategy'):
                    dev_db.add_strategy(dev_id,strategy_id)
                    config.notify_by_push_server(dev_sid,info)
                elif((info.split(':'))[0]=='DelStrategy'):
                    dev_db.strategy_need_del(dev_id,strategy_id)
                    config.notify_by_push_server(dev_sid,info)
                elif((info.split(':'))[0]=='ModStrategy'):
                    #+++ 20150714 修改策略无所谓是否在oldusers中，均可执行下操作
                    if dev_db.is_has_strategy_id(dev_id,strategy_id):  #如果未改之前的策略未到期
                        dev_db.strategy_is_not_read(dev_id,strategy_id)
                    else: #如果未改之前的策略已到期
                        dev_db.add_strategy(dev_id,strategy_id)
                    config.notify_by_push_server(dev_sid,info)
                    oldusers.remove(gson)

#                     if gson in oldusers:
#                     #如果在oldusers中存在 则给相应的客户端发送修改策略,并从oldusers中删除
#                     #同时将dev中对应的策略标志位is_read 设置为false
#                     #特殊情况  如果策略到期被删除以后，dev_db中的该策略ID将会被删除，此时再修改该策略就需要在dev_db中新加一条
#                         if dev_db.is_has_strategy_id(dev_id,strategy_id):  #如果未改之前的策略未到期
#                             dev_db.strategy_is_not_read(dev_id,strategy_id)
#                         else: #如果未改之前的策略已到期
#                             dev_db.add_strategy(dev_id,strategy_id)
#                         if config.notify_by_push_server(dev_sid,info):
#                             #通知成功
#                             oldusers.remove(gson)
#                     else:
#                     #如果不在oldusers中，则说明其为新添加的用户，则发送新增策略，并在dev中写入策略编号
#                         if dev_db.is_has_strategy_id(dev_id,strategy_id):
#                             dev_db.strategy_is_not_read(dev_id,strategy_id)
#                         else:
#                             dev_db.add_strategy(dev_id,strategy_id)
#                             if not config.notify_by_push_server(dev_sid,info):
#                                 continue
    #遍历oldusers oldusers剩下的就是从原有用户列表中删除的,则提醒用户删除该条策略，并删除dev中的策略ID
    for ldu in oldusers:
        logging.error("ldu  is  %s",ldu)
        dev_id1 =dev_db.get_dev_id_by_curuser(ldu['uid'])
        if dev_id1:
            dev_sid1 = session_db.user.get_sid( ldu['uid'], dev_id1)

#         方案一：弊端服务器无法及时的判定客户端是否在线
            #如果不在线写标志位，让客户端上线后删除
#         if not config.is_sid_on_push_server(dev_sid1):
#             dev_db.strategy_need_del(dev_id1,strategy_id)
#         if config.is_sid_on_push_server(dev_sid1): #如果在线直接删除
#             dev_db.complete_strategy(dev_id1,strategy_id)
#         方案二：
#          服务器不判定客户端是否在线，都只是将标记位写上delete标识，等客户端下次上线以后去删除
            dev_db.strategy_need_del(dev_id1,strategy_id)
            if not config.notify_by_push_server(dev_sid1,'DelStrategy:'+strategy_id):
#             raise ecode.PUSHSEVER_NOT_EXIST
                continue
        else:
            continue
    return True

#计算两个经纬度之间的距离
def deg2rad(d):
    return float(d) * math.pi/ 180.0;
def distance(lon1,lat1,lon2,lat2): #经纬度
    radlat1=deg2rad(lat1)
    radlat2=deg2rad(lat2)
    a=radlat1-radlat2
    b=deg2rad(lon1)-deg2rad(lon2)
    s=2*math.asin(math.sqrt(math.pow(math.sin(a/2),2)+math.cos(radlat1)*math.cos(radlat2)*math.pow(math.sin(b/2),2)))
    earth_radius_meter = 6378137.0
#     s=round(s*earth_radius_meter,0)
    s = s*earth_radius_meter
    if s<0:
        return -s
    else:
        return s




class Test:
    #{{{
    def GET(self):
        """此方法是用于测试加解密的模块
        input:
            sid:
            cryptograph:
        output:
            rt: error code
            age: []
            name:{}
        """
        i = ws_io.cws_input(['sid','cryptograph'])
        rt = ecode.FAILED
        age = [1,2,3]
        name = {'a':'ddd','b':'nnnn'}


        return ws_io.cws_output(dict(rt=rt.eid,age=age
            ,name=name))
#}}}

# #+++20150206  ws2user.py
# class DevsInfo:
#     #{{{
#     def GET(self):
#         """
#         input:
#             sid:
#             uids:[uid1,uid2,...]
#         output:
#             rt: error code
#             devs_info:[{"dev_id":"dev1","status":"status1","last_update":"time1"},{},...]
#         """
#
#         rt = ecode.FAILED
#         last_update=''
#         dev=''
#         status=0   #status: 0 not login, 1 login but offline, 2 online
#         devs_info=[]   #多个设备信息
#
#         try:
#             i = ws_io.ws_input(['sid','uids'])
#             if not i:
#                 raise ecode.WS_INPUT
#
#             user = session_db.user.get_user( i['sid'], web.ctx.ip)
#             if not user:
#                 raise ecode.NOT_LOGIN
#
#             if not config.get('is_org'):
#                 raise ecode.NOT_ALLOW_OP
#
#             #判断用户权限
#             if not admin_db.is_has_admin(user) and org.get_config()['admin'] != user:
#                 raise ecode.NOT_PERMISSION
#
#             #查询状态并返回
#             uids=json.loads(i['uids'])
#             i=0
#             while(i<len(uids)):
#                 dev_info={}   #单个设备信息
#                 uid=uids[i]
#                 devs=user_db.devs(uid)
#                 if devs==[]:
#                     last_update=""
#                     status=0
#                     dev=""
#                 else:
#                     dev=devs[0]
#                     #最后更新时间
#                     last_update = dev_db.get_last_update(dev)
#                     #获取在线状态
#                     dev_sid=session_db.user.get_sid(uid, dev)
#                     if dev_sid:
#                         status=1
#                         if config.is_sid_on_push_server(dev_sid):
#                             status=2
#                 #打包返回
#                 dev_info["dev_id"]=dev
#                 dev_info["status"]=status
#                 dev_info["last_update"]=last_update
#                 devs_info.append(dev_info)
#                 i=i+1
#
#             rt = ecode.OK
#         except Exception as e:
#             rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
#             logging.error('DevsInfo')
#
#         return ws_io.ws_output(dict(rt=rt.eid,devs_info=devs_info))

#+++20150206  ws2user.py
class DevsInfo:
    #{{{
    def GET(self):
        """
        input:
            sid:
            uids:[uid1,uid2,...]
        output:
            rt: error code
            devs_info:[{"dev_id":"dev1","status":"status1","last_update":"time1","onlinestates":"onlinestate1"},{},...]
        """

        rt = ecode.FAILED
        last_update=''
        dev=''
        status=0   #status: 0 not login, 1 login but offline, 2 online
        devs_info=[]   #多个设备信息
        onlinestates="" #用户活跃度

        try:
            i = ws_io.ws_input(['sid','uids','type'])
            if not i:
                raise ecode.WS_INPUT

            admin = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not admin:
                raise ecode.NOT_LOGIN

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            #判断用户权限
            if not admin_db.is_has_admin(admin) and 'admin' != admin:
                raise ecode.NOT_PERMISSION

            #查询状态并返回
            uids=json.loads(i['uids'])
            op_type = i['type']
            i=0
            while(i<len(uids)):
                dev_info={}   #单个设备信息
                uid=uids[i]
                user = user_db.get_user_info_by_uid(uid)
                devs=user_db.devs(uid)
                status=0
                if devs==[]:
                    last_update=""
                    status=0
                    dev=""
                    onlinestates=""
                else:
                    dev=devs[0]
                    #最后更新时间
                    last_update = user_db.get_last_update(user['key'])
                    #获取在线状态
                    dev_sid=session_db.user.get_sid(uid, dev)
                    if dev_sid:
                        status=1
                        if config.is_sid_on_push_server(dev_sid):
                            status=2
                    # +++20151008在获取状态的同时，将状态存入数据库
                    user_db.change_user_status(uid,status)
                    onlinestates = generateLiveness(user)
                #打包返回
                dev_info["dev_id"]=dev
                dev_info["status"]=status
                dev_info["last_update"]=last_update
                dev_info["onlinestates"]=onlinestates
                devs_info.append(dev_info)
                i=i+1
            # +++20151008 加入获取状态并存入数据库的子线程
            if int(op_type)==0:
                logging.error("开始创建更新状态的线程")
                change_status_thread = threading.Thread(target=get_and_save_status_liveness,args=())
                change_status_thread.start()
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('DevsInfo')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,devs_info=devs_info),error_info)

# +++20151008 在get_devs_info的时候加入一个新的线程，获取设备当前的状态并存入数据库
def get_and_save_status_liveness():
    logging.error("开始更新用户设备的状态/活跃度并存入数据库")
    keys = user_db.key_list()
    for key_item in keys:
        uid = key_item['uid']
        key = key_item['key']
        devs=user_db.devs(uid)
        status=0
        if devs==[]:
            status=0
        else:
            dev=devs[0]
            r = user_db.get_onlinestate(key)
            onlinetime = user_db.get_onlinetimes(key)
            t = time.localtime()
            tt = datetime.datetime(t[0], t[1], t[2])
            currenttime = time.mktime(tt.timetuple())
            if onlinetime:
                ontime = datetime.datetime.utcfromtimestamp(onlinetime)
                cutime = datetime.datetime.utcfromtimestamp(currenttime)
                timediff = (cutime - ontime).days
                if int(timediff) > 1:
                    onlinest = str(r['online'])
                    outlinest = str(int(r['outline']) + int(timediff) - 1)
                    user_db.set_outlinestate1(key, onlinest, outlinest)
                    # +++20151112 在更新
                    onlinestate1=user_db.get_onlinestate(key)
                    liveness = long(onlinestate1['online'])*3650-(long(onlinestate1['online'])+long(onlinestate1['outline']))
                    user_db.set_liveness(uid,liveness)
            #获取在线状态
            dev_sid=session_db.user.get_sid(uid, dev)
            if dev_sid:
                status=1
                if config.is_sid_on_push_server(dev_sid):
                    status=2
            user_db.change_user_status(uid,status)
            #+++20151130获取上一次更新时间
            last_update = user_db.get_last_update(key)
            if last_update!="":
                user_db.set_last_update(uid,last_update)


# +++ 20150910 将获取活跃度的过程抽象成函数
def generateLiveness(user):
    key = user['key']
    uid = user['uid']
    r = user_db.get_onlinestate(key)
    onlinetime = user_db.get_onlinetimes(key)
    t = time.localtime()
    tt = datetime.datetime(t[0], t[1], t[2])
    currenttime = time.mktime(tt.timetuple())
    if onlinetime:
        ontime = datetime.datetime.utcfromtimestamp(onlinetime)
        cutime = datetime.datetime.utcfromtimestamp(currenttime)
        timediff = (cutime - ontime).days
        if int(timediff) > 1:
            onlinest = str(r['online'])
            outlinest = str(int(r['outline']) + int(timediff) - 1)
            user_db.set_outlinestate1(key, onlinest, outlinest)
            # +++20151112 在更新
            onlinestate1=user_db.get_onlinestate(key)
            liveness = long(onlinestate1['online'])*3650-(long(onlinestate1['online'])+long(onlinestate1['outline']))
            user_db.set_liveness(uid,liveness)

            rr = user_db.get_onlinestate(key)
            if len(rr) > 0:
                if int(rr['online']) + int(rr['outline']) != 0:
                    allstates = str(int(rr['online']) + int(rr['outline']))
                    onlinestates = str(rr['online']) + '/' + allstates
                else:
                    onlinestates = '0'
            else:
                onlinestates = '0'
        else:
            if len(r) > 0:
                if int(r['online']) + int(r['outline']) != 0:
                    allstates = str(int(r['online']) + int(r['outline']))
                    onlinestates = str(r['online']) + '/' + allstates
                else:
                    onlinestates = '0'
            else:
                onlinestates = '0'
    return onlinestates

class GetCmdsEncry:
    #{{{
    def GET(self):
        """
        input:
            sid:
        output:
            rt: error code
            cmds: {...}
        """
        rt = ecode.FAILED
        cmds = []
        dev_id=''

        try:
            i = ws_io.cws_input(['sid'])
            cmds = []
#             dev_id = '862769025344539'
            logging.error("decode output:%s",str(i))
            if not i:
                raise ecode.WS_INPUT

            if i.has_key('dev_id'):
                dev_id = i['dev_id']
                user = session_db.user.get_user( i['sid'], web.ctx.ip)
            else:
                user,dev_id = session_db.user.get_user_and_dev( i['sid']
                        , web.ctx.ip)

            if not user:
                raise ecode.NOT_LOGIN

            if not user_db.is_my_dev( user, dev_id):
                raise ecode.NOT_PERMISSION

            cmds = dev_db.get_cmds( dev_id )
            logging.error('cmds type: %s',type(cmds))
            for cmd in cmds:
                dev_db.complete_cmd(dev_id,cmd['id'])

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get cmds Encry')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.cws_output(dict(rt=rt.eid,cmds=cmds),dev_id,error_info)
    #}}}

class GetCmdsEncry1:
    #{{{
    def GET(self):
        """
        input:
            sid:
            cryptograph:
        output:
            rt: error code
            cmds: {...}
        """
        rt = ecode.FAILED
        cmds = []
        dev_id=''

        try:
            i = ws_io.cws_input(['sid'])
            cmds = [{  "cmd" : "url 11", "id" : 362 }]
            dev_id = '862769025344539'
            logging.error("decode output:%s",str(i))
#             if not i:
#                 raise ecode.WS_INPUT
#
#             if i.has_key('dev_id'):
#                 dev_id = i['dev_id']
#                 user = session_db.user.get_user( i['sid'], web.ctx.ip)
#             else:
#                 user,dev_id = session_db.user.get_user_and_dev( i['sid']
#                         , web.ctx.ip)
#
#             if not user:
#                 raise ecode.NOT_LOGIN
#
#             if not user_db.is_my_dev( user, dev_id):
#                 raise ecode.NOT_PERMISSION
#
#             cmds = dev_db.get_cmds( dev_id )
#             for cmd in cmds:
#                 dev_db.complete_cmd(dev_id,cmd['id'])


            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get cmds Encry')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt,cmds=cmds),error_info)
#         return ws_io.cws_output(dict(rt=rt,cmds=cmds),dev_id)
    #}}}

class GetStrategyById1Encry:
#{{{
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
            i = ws_io.cws_input(['sid','strategy_id'])   #从数据库读取数据
            if not i:
                raise ecode.WS_INPUT

            strategy_id = i['strategy_id']

            user,dev_id = session_db.user.get_user_and_dev( i['sid']
                    , web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
#             if not user_db.is_my_dev( user, dev_id):
#                 raise ecode.NOT_PERMISSION

            #通过strategy_id返回一条策略（strategy_db）
            strategy = strategy_db.get_strategy_by_id1(strategy_id)
#            将策略ID标志位写为已读 true(dev_db)
            dev_db.strategy_is_read(dev_id,strategy_id)

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get strategy by id')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.cws_output(dict(rt=rt.eid,strategy=strategy),dev_id,error_info)


#通过设备ID(dev_id)获取单个用户的策略信息(移动客户端only)
class GetUserStrategysEncry:#
    #{{{
    def GET(self):
        """
        input:
            sid:
            dev_id:
        output:
            rt: error code
            strategys: {...}
        """
        rt = ecode.FAILED
        strategys = {}

        try:
            i = ws_io.cws_input(['sid'])   #数据库读明文数据
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            #web端调用（弃）需要管理员来调用
            if user == 'admin' or admin_db.is_has_admin(user):
                user = dev_db.get_cur_user(i['dev_id'])
                ids = dev_db.get_strategy_ids(user)
                strategys = strategy_db.get_strategys_of_user_by_admin(ids)
            #客户端调用
            else:
                newids=[]
                ids = dev_db.get_strategy_ids(user)   #获取user的strategys id（dev_db）
                for stra_id in ids:
                    if(str(stra_id['is_read'])== "false"):   #得到未读取策略id数组
                        newids.append(stra_id)
                strategys = strategy_db.get_strategys_to_user(newids)   #获取未读策略（strategy_db）

                #判定策略是否时间有效，如果无效则删除dev数据库中相应的id号
                dev_id = dev_db.get_dev_id_by_curuser(user)
                key = time.time()
                for stra in strategys:
                    et = time.mktime(time.strptime(str(stra['end']), '%Y-%m-%d %H:%M'))
                    if et < key: #如果策略结束时间比当前服务器时间早，则视为无效数据，需要删除dev_id中的ID号
                        dev_db.complete_strategy(dev_id,stra['strategy_id'])

                #将读取后的id对应标记位 is_read设置为true
                logging.error(user)
                logging.error(dev_id)
                logging.error(len(newids))
                for strid in newids:   #把策略标志位设置为已读
                    dev_db.strategy_is_read(dev_id,strid['strategy_id'])
#                     logging.error(strid['strategy_id'])


            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get user strategys')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.cws_output(dict(rt=rt.eid,strategys=strategys),dev_id,error_info)
    #}}}


class GetContactsEncry:#
    #{{{
    def GET(self):
        """
        input:
            sid:
        output:
            rt: error code
            contacts: [{name姓名,email电子邮件,job职位,department部门,pnumber电话号码}]
        """
        rt = ecode.FAILED
        contacts = []

        try:
            i = ws_io.cws_input(['sid'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            logging.error("用户是:%s",user)
            if not user:
                raise ecode.NOT_LOGIN

            contacts = user_db.get_contacts_by_uid(user)   #从用户数据库中取得该用户的待下发联系人
            logging.error("用户的联系人信息:%s",str(contacts))
            #清空联系人缓存区中的联系人信息
            user_db.del_contact(user)
            # contacts = getLdapContact(uids)   #通过这些uid在ldap中取得详细联系人信息

            dev_id = dev_db.get_dev_id_by_curuser(user)
            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get contacts')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.cws_output(dict(rt=rt.eid,contacts=contacts),dev_id,error_info)
    #}}}

class SendStaticinfo:
    #{{{
    def POST(self):
        """
        input:
            sid:
            dev_id:
        output:
            rt: error code
        """
        rt = ecode.FAILED
        error_info = ""
        try:
            i = ws_io.ws_input(['dev_id','sid'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            if admin_db.is_has_admin(user) or 'admin' == user:
                user = dev_db.get_cur_user( i['dev_id'])

            if not user_db.is_my_dev( user, i['dev_id']):
                raise ecode.NOT_PERMISSION

            dev_sid = session_db.user.get_sid( user, i['dev_id'])

            if config.notify_by_push_server(dev_sid,'refresh staticinfo'):
                rt = ecode.OK
                error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('send Staticinfo')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)

#+++20150403
class SendStrategySms:
    def POST(self):
        """
        input:
            sid:session id
            id:strategy id
            start:开始时间
            end:结束时间
            longitude:作用经度
            latitude:作用维度
            radius:作用半径
            baseStationID:策略作用基站
            desc:范围描述
            camera:摄像头
            bluetooth:蓝牙
            Wifi:wifi
            tape:录音
            gps:gps
            mobiledata:移动数据
            usb_connect:USB连接
            usb_debug:USB调试
            users:{作用人}
            userdesc:作用人描述
        output
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','id','users','userdesc','start','end','lon','lat','desc','radius','baseStationID','camera','bluetooth','wifi','tape','gps','mobiledata','usb_connect','usb_debug'])
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
            strategy['baseStationID']='01'#i['baseStationID']   #+++20150430 基站信息不用短信发送
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
            strategy['force'] = i['force']  #+++20150709 for force Control
            strategy['types']=''   #+++ 20150506 for pre stra


            userdesc=json.loads(i['userdesc'])

            user = session_db.user.get_user( i['sid'], str(web.ctx.ip))
            if not user:
                raise ecode.NOT_LOGIN
            ou_selected_users = user_db.get_selected_users(user)
            users=getFormatUsers(ou_selected_users)


            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
                else:
                    ouAuth = admin_db.get_ou_by_uid(user)
                    logging.error("管理员权限"+ouAuth)
                    strategy['auth'] = ouAuth
            else:
                # +++20151023 在策略中加入一个字段来记录下发此策略的权限
                strategy['auth'] = "admin"
            #将策略写入数据库strategy_db,并且以加密短信形式下发
            strategy_db.new_strategy(strategy,users,userdesc)
            info='NewStrategy:'+str(i['id'])

            #+++ 20150710 根据dev_id区分是否为未登陆用户
            for son in users:
                sonusers = son['users']
                for gson in sonusers:
                    uid = gson['uid']
                    dev_id = dev_db.get_dev_id_by_curuser(uid)
                    logging.warn("uid is : %s, dev_id is : %s",uid,dev_id)
                    if dev_id is None:
                        if not user_db.is_has_strategy_id(uid, i['id']):
                            user_db.add_strategy(uid,i['id'])
            # +++20150906 改，加入多线程发送策略短信逻辑
            # sendThread = threading.Thread(target=SendStrategyBySmsToUsers,args=(users,i['id'],info))
            # sendThread.start()
            SendStrategyBySmsToUsers(users,i['id'],info)
            # if not SendStrategyBySmsToUsers(users,i['id'],info):
            #     strategy_db.del_strategy(i['id'])

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            strategy_db.del_strategy(i['id'])
            logging.error('send strategy sms')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

#send sms for strategy function
def SendStrategyBySmsToUsers(users,strategy_id,info,oldusers=[]):
    strategy_to_send = strategy_db.get_strategy_by_id1(strategy_id)   #sms minwen to send
    re=0
    for son in users:
        sonusers = son['users']
        for gson in sonusers:
            uid = gson['uid']
            dev_id = dev_db.get_dev_id_by_curuser(uid)
            if dev_id is None:
                continue
            else:
                strategy_str=json.dumps(strategy_to_send)
                logging.error('oringin strategy len and strategy is : %s,%s',len(strategy_str),strategy_str)
#                 strategy_zlib=zlib.compress(strategy_str)
#                 logging.error('strategy_zlib len and strategy_zlib is : %s,%s',len(strategy_zlib),strategy_zlib)
#                 encry_strategy=ws_io.encrypt_sec(strategy_zlib, dev_id)[0]   #get encry smsdata
                #encry_strategy=json.dumps(strategy_to_send,ensure_ascii=False,indent=2)   #only for test
                if((info.split(':'))[0]=='NewStrategy'):
                    dev_db.add_strategy(dev_id,strategy_id)
                    if not send_encrypt_sms(uid,'sty',strategy_str,dev_id):   #send encry strategy message
                        re=re+1
                    dev_db.strategy_is_read(dev_id, strategy_id)
#                 elif((info.split(':'))[0]=='ModStrategy'):
#                     if not send_encrypt_sms(uid,'sty',strategy_str,dev_id):   #send encry strategy message
#                         re=re+1
#                     if not dev_db.is_has_strategy_id(dev_id,strategy_id):
#                         dev_db.add_strategy(dev_id,strategy_id)
#                         dev_db.strategy_is_read(dev_id, strategy_id)
    if re!=0:
        # +++20150924这会导致有短信发送不成功就删除策略，不合理
        # strategy_db.del_strategy(strategy_id)
        return False
    return True

#+++20150403
def send_encrypt_sms(uid,types,sms,dev_id):
    sms_en=str(types+':'+sms)
#     if types=='sty':
#         sms_zlib=zlib.compress(sms_en)
#         logging.error('sms_zlib len and sms_zlib is : %s,%s',len(sms_zlib),sms_zlib)
#     else:
#         sms_zlib=sms_en
    logging.error("开始加密的时间"+str(time.time()))
    sms_zlib=sms_en
    encry_sms=ws_io.encrypt_des(sms_zlib, dev_id)   #get encry smsdata
    logging.error("结束加密的时间"+str(time.time()))
    result = send_sms.send_sms(uid,encry_sms)
    return result

#+++ 20150710 mod sms for strategy function 20150906 改
def ModStrategyBySmsToUsers(strategy_id,user,sid):
    info_head1="Mod_DelStrategy:"
    info1=info_head1+strategy_id
    info_head2="Mod_NewStrategy:"
    info2=info_head2+strategy_id

    #针对待删除策略用户和待下发的用户
    new_users=re_cmd_db.get_devs(user+info2)
    del_users=re_cmd_db.get_devs(user+info1)
    strategy_to_send = strategy_db.get_strategy_by_id1(strategy_id)   #sms minwen to send
    re=0
    for son in new_users:
        uid = son['uid']
        dev_id = dev_db.get_dev_id_by_curuser(uid)
        strategy_str=json.dumps(strategy_to_send)
        if not send_encrypt_sms(uid,'sty',strategy_str,dev_id):   #send encry strategy message
            re=re+1
            continue
        else:
            #+++ 20150922 如果短信发送成功，要删除其中的用户
            re_cmd_db.modify_sms_stra_ok(son,user,info2)
        if not dev_db.is_has_strategy_id(dev_id,strategy_id):
            dev_db.add_strategy(dev_id,strategy_id)
        dev_db.strategy_is_read(dev_id, strategy_id)
    for son in del_users:
        uid = son['uid']
        dev_id = dev_db.get_dev_id_by_curuser(uid)
        info='DelStrategy:'+strategy_id
        if not send_encrypt_sms(uid,'del',info,dev_id):   #send encry strategy message
            re=re+1
            continue
        else:
            #+++ 20150922 如果短信发送成功，要删除缓存表中的用户
            re_cmd_db.modify_sms_stra_ok(son,user,info1)
        dev_db.complete_strategy(dev_id,strategy_id)
    if re!=0:
        logging.error("有短信发送失败，需要向前台反馈")
        config.notify_by_push_server(sid,"strategy:ModStrategy:"+strategy_id)
        return False
    else:
        re_cmd_db.complete_re_cmd(user+info1)
        re_cmd_db.complete_re_cmd(user+info2)
        left_users = getLeftUsers(user,strategy_id)
        if len(left_users)>0:
            config.notify_by_push_server(sid,"strategy:ModStrategy:"+strategy_id)
        return True

# +++20150922将修改策略后获取未成功获取到信息的用户过程抽象成函数
def getLeftUsers(admin,strategy_id):
    left_users = []
    info_head1="Mod_DelStrategy:"
    info1=info_head1+strategy_id
    info_head2="Mod_NewStrategy:"
    info2=info_head2+strategy_id
    #针对删除操作
    users=re_cmd_db.get_devs(admin+info1)
    if len(users)==0:
        re_cmd_db.complete_re_cmd(admin+info1)
    left_users = left_users + users
    #针对下发操作
    users=re_cmd_db.get_devs(admin+info2)
    if len(users)==0:
        re_cmd_db.complete_re_cmd(admin+info2)
    left_users = left_users + users

    return left_users

#+++20150403
class SendCmdSms:
    def POST(self):
        """
        input:
            sid:
            devs:
            cmd:
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            # +++20150910 离线判断逻辑提前，在发送的时候可能不知道具体有多少台设备未成功接收，去掉之前的devs
            i = ws_io.ws_input(['cmd','sid'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if not admin_db.is_has_admin(user) and 'admin' != user:
                raise ecode.NOT_PERMISSION

            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP
            if i.get("devs")!=None:
                devs=json.loads(i['devs'])
            else:
                devs = re_cmd_db.get_devs(user+i['cmd'])
            logging.error(str(devs))
            # +++20150906 加入多线程发送短信逻辑
            # sendThread = threading.Thread(target=SendCmdBySms,args=(devs,i['cmd'],i['sid']))
            # sendThread.start()
            SendCmdBySms(devs,i['cmd'],i['sid'])
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('send cmd sms')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)

# +++20150906 将短信发送指令的过程抽象成函数，供多线程调用
def SendCmdBySms(devs,cmd,sid):
    for dev_id in devs:
        uid = dev_db.get_cur_user(dev_id)
        if not user_db.is_my_dev( uid,dev_id):
            logging.error("dev_id is not permittion to uid,dev_id:%s,uid:%s",dev_id,uid)
            continue
        logging.error("开始加载JVM的时间"+str(time.time()))
        logging.error("加载完JVM的时间"+str(time.time()))
        if not send_encrypt_sms(uid,'cmd',cmd,dev_id):
            logging.error("Send cmd by sms failed,uid is :%s",uid)
            continue
        #+++ 20150629
        if cmd=='qccl':
            cur_user=dev_db.get_cur_user(dev_id)
            stra_ids=dev_db.get_strategy_ids(cur_user)
            for stra in stra_ids:
                stra_id=stra["strategy_id"]
                if strategy_db.is_has_strategy(stra_id):
                    if strategy_db.del_user_of_users(stra_id, cur_user):
                        dev_db.remove_strategy(cur_user)  #+++20150629 删除dev_db
        #+++20150615 for feedback of cmd
        re_cmd_db.get_cmd_ok(dev_id)
    # jpype.shutdownJVM()
    # +++20150917 检查re_cmd中短信发送失败的人数
    admin = session_db.user.get_user(sid,"no_use")
    logging.error("SendCmdBySms:"+admin+cmd)
    num = len(re_cmd_db.get_devs(admin+cmd))
    infostr = "cmd:"+cmd+":"+str(num)
    config.notify_by_push_server(sid,infostr)

#+++20150409
class DeleteStrategySms:
    def POST(self):
        """
        input:
            sid:
            ids: "strategy call ids"
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','ids'])
            if not i:
                raise ecode.WS_INPUT
            #user是管理员
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION

            ids=json.loads(i['ids'])
            for iid in ids:
                #+++ 20150615 判断是否过期，过期则不必推送客户端消息
                users = (strategy_db.get_strategy_by_id(iid))['users']
                info='DelStrategy:'+str(iid)
                end_time=(strategy_db.get_strategy_by_id(iid))['end']
                end=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M'))
                now_time=time.time()
                if int(now_time)-int(end)>0:
                    strategy_db.del_strategy(iid)
                    for son in users:
                        sonusers=son["users"]
                        for gson in sonusers:
                            uid=gson["uid"]
                            if dev_db.is_has_user(uid):
                                dev_db.remove_expire_strategy(uid,iid)
                            else: #未激活
                                user_db.remove_expire_strategy(uid,iid)
                else:
                    # +++ 20150906 加入短信删除策略线程
                    # sendThread = threading.Thread(target=DelStraBySms,args=(users,iid,info))
                    # sendThread.start()
                    DelStraBySms(users,iid,info)
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('delete_strategy by sms')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)

#+++20150409 改 20150715
def DelStraBySms(users,strategy_id,info,oldusers=[]):
    re=0
    for son in users:
        sonusers = son['users']
        for gson in sonusers:
            uid = gson['uid']
            dev_id = dev_db.get_dev_id_by_curuser(uid)
            if dev_id is None:
                continue
            else:
                if((info.split(':'))[0]=='DelStrategy'):
                    #在这里，默认都是能成功的，如果调试中发现未成功，则再对逻辑进行改进（成功从re_cmd的users中删除）
                    if not send_encrypt_sms(uid,'del',info,dev_id):   #send encry strategy message
                        re=re+1
                    dev_db.complete_strategy(dev_id,strategy_id)
    if re!=0:
        return False
    else:
        strategy_db.del_strategy(strategy_id)
        for son in users:
            sonusers=son["users"]
            for gson in sonusers:
                uid=gson["uid"]
                if dev_db.is_has_user(uid):
                    dev_db.remove_expire_strategy(uid,strategy_id)
                else: #未激活
                    user_db.remove_expire_strategy(uid,strategy_id)
        return True

#+++ 20150507 des 加解密
#cmds
class GetCmdsDes:
    #{{{
    def GET(self):
        """
        input:
            sid:
        output:
            rt: error code
            cmds: {...}
        """
        rt = ecode.FAILED
        cmds = {}

        try:
            i = ws_io.ws_input_des(['sid'])
            if not i:
                raise ecode.WS_INPUT

            if i.has_key('dev_id'):
                dev_id = i['dev_id']
                user = session_db.user.get_user( i['sid'], web.ctx.ip)
            else:
                user,dev_id = session_db.user.get_user_and_dev( i['sid']
                        , web.ctx.ip)

            if not user:
                raise ecode.NOT_LOGIN

            if config.get('is_org') and 'admin' == user:
                user = dev_db.get_cur_user( i['dev_id'])

            if not user_db.is_my_dev( user, dev_id):
                raise ecode.NOT_PERMISSION

            cmds = dev_db.get_cmds( dev_id )
            #+++ 20150715 for 清除策略
            qccl=0
            for cmd in cmds:
                dev_db.complete_cmd(dev_id,cmd['id'])
                if cmd['cmd']=='qccl':
                    qccl=1
            if qccl==1:
                stra_ids=dev_db.get_strategy_ids(user)
                for stra in stra_ids:
                    stra_id=stra["strategy_id"]
                    if strategy_db.is_has_strategy(stra_id):
                        if not strategy_db.del_user_of_users(stra_id,user):
                            continue
                        dev_db.remove_strategy(user)  #+++20150629 删除dev_db
            #+++ 20150611 for reply send cmd
            re_cmd_db.get_cmd_ok(dev_id)

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get cmds')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        op_user=user
        op_type=operation.STRATEGY_qc.type
        op_desc=operation.STRATEGY_qc.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )
        return ws_io.ws_output_des(dict(rt=rt.eid,cmds=cmds),dev_id,error_info)

#strategy
class GetStrategyById1Des:
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
            i = ws_io.ws_input_des(['sid','strategy_id'])
            if not i:
                raise ecode.WS_INPUT

            strategy_id = i['strategy_id']

            user,dev_id = session_db.user.get_user_and_dev( i['sid']
                    , web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN
            #过去所有的下发了的策略
            strategy = strategy_db.get_strategy_by_id1(strategy_id)
            dev_db.strategy_is_read(dev_id,strategy_id)
#             #+++ 20150703 for modify_stra_ok
#             re_cmd_db.modify_stra_ok(user,strategy_id,'modifyStrategys')
            #+++ 20150616 for re_strategy
            re_cmd_db.get_stra_ok(user,'strategys')
            #+++ 20150714
            re_cmd_db.mod_stra_ok(user,'modifyStrategys','NewStrategy')

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get strategy by id')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output_des(dict(rt=rt.eid,strategy=strategy),dev_id,error_info)

#contacts
class GetContactsDes:
    def GET(self):
        """
        input:
            sid:
        output:
            rt: error code
            contacts: [{name姓名,email电子邮件,job职位,department部门,pnumber电话号码},...]
        """
        rt = ecode.FAILED
        contacts = []
        dev_id = ''

        try:
            i = ws_io.ws_input_des(['sid'])
            if not i:
                raise ecode.WS_INPUT

            user,dev_id = session_db.user.get_user_and_dev( i['sid'],web.ctx.ip)
            logging.error("用户是:%s",user)
            if not user:
                raise ecode.NOT_LOGIN

            contacts = user_db.get_contacts_by_uid(user)
            logging.error("用户的联系人信息:%s",str(contacts))
            #+++20151109 如果取到的联系人信息不为空，则清空联系人缓存区中的联系人信息
            if(len(contacts)>0):
                user_db.del_contact(user)
            # contacts = getLdapContact(uids)
            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get contacts')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output_des(dict(rt=rt.eid,contacts=contacts),dev_id,error_info)

#static info up
class DevStaticInfoDes:
    keys = ('firmware_version',
            'model_number',
            'version_number',
            'imei',
            'imei_version',
            'sim_supplier',
            'sim_sn',
            'sim_state',
            'signal_strength',
            'network_providers',
            'network_type',
            'phone_type',
            'call_status',
            'wifi_bssid',
            'wifi_ip_addr',
            'wifi_mac_addr',
            'wifi_rssi',
            'wifi_ssid',
            'wifi_network_id',
            'wifi_request_status',
            'wifi_conn_speed',
            'bluetooth_is_on',
            'bluetooth_is_search',
            'bluetooth_name',
            'bluetooth_addr',
            'bluetooth_status',
            'bluetooth_pair_dev',
            'battery_status',
            'battery_power',
            'battery_voltage',
            'battery_temperature',
            'battery_technology',
            'battery_life',
            'data_activity_status',
            'data_conn_status',
            'call_volume',
            'system_volume',
            'ring_volume',
            'music_volume',
            'tip_sound_volume',
            'longitude',
            'latitude',
            'pos_corrention_time')

    def POST(self):
        """
        input:
            sid:
            key1:value1
            key2:value2
            ...
        output:
            rt: error code
            count: update success count
        """
        rt = ecode.FAILED
        count = 0

        try:
            i = ws_io.ws_input_des(['sid'])
            if not i:
                raise ecode.WS_INPUT

            user,dev_id = session_db.user.get_user_and_dev( i['sid']
                    , web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN

            for k in i:
                if k not in self.keys:
                    continue
                dev_db.set_static_info( dev_id, k, i[k])
                count = count + 1

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('DevStaticInfo des up')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output_des(dict(rt=rt.eid,count=count),dev_id,error_info)

#loc up
class LocDes:
    def POST(self):
        """
        input:
            sid:
            lon:
            lat:
            baseStationID: 基站地址
            offlinetime:客户端掉线的时间戳    毫秒级
            currenttime: 客户端当前的时间戳   毫秒级
            accuracy: 精度
        output:
            rt: error code 处理的时间都是时间戳     秒级
        """
        rt = ecode.FAILED
        dev_id = ""
        try:
            i = ws_io.ws_input_des(['lon','lat','sid'])
            if not i:
                raise ecode.WS_INPUT

            user,dev_id = session_db.user.get_user_and_dev( i['sid']
                    , web.ctx.ip)

            if not user:
                raise ecode.NOT_LOGIN

            if not user_db.is_my_dev( user, dev_id):
                raise ecode.NOT_PERMISSION

            user_info = user_db.get_user_info_by_uid(user)
            # 修改用户的在线时间等属性
            change_online_state(user_info['key'])
            # 修改用户的活跃度
            if user_db.is_verified(user_info['uid']):
                change_liveness(user_info)
            #基站信息统计（未利用）
            if i.has_key('baseStationId'):
                base_db.add_base(i['lon'],i['lat'],i['baseStationId'])
            #存位置，for 丢失溯源(手机上传就存)
            key = time.time()
            value = i['lon']+':'+i['lat']+':online'
            trace_db.set(user,int(key),value)
            # +++20150901 设置更新时间的过程在这个函数里面，设置位置信息的时候同时就设置了last_update
            dev_db.set_loc( dev_id, i['lon'], i['lat'])
            user_db.set_last_update(user,str(int(time.time())))
            # +++20160119将在线状态上传
            post_online_status(user,time.time())
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('loc des')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output_des(dict(rt=rt.eid),dev_id,error_info)

# upload stored online data
class OnlineData:
    def POST(self):
        """
        input:
            imei:操作的手机IMEI号
            time:[] 开机时间数组
        output:
            rt
        :return:
        """
        rt = ecode.FAILED
        imei = ""
        try:
            i = ws_io.ws_input(["imei","time_index"])
            imei = i["imei"]
            print dev_db.get_dev_by_id(imei)
            if dev_db.get_dev_by_id(imei)==None:
                raise ecode.NOT_ALLOW_OP  #如果设备号不存在，报出异常不允许写入数据
            else:

                user_id = dev_db.get_cur_user(imei)  #找到当前设备的绑定用户
                online_times = json.loads(i["time_index"])
                print "当前设备用户是"+str(user_id)
                for item in online_times:
                    post_online_status(user_id,float(item))
            error_info = ""
            rt = ecode.OK
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.exception('post stored online data')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),imei)


def post_online_status(uid,time_stamp):
    # 生成在线日期
    temp = time.localtime(time_stamp)
    online_day=time.strftime("%Y-%m-%d", temp)
    week_no = time.strftime("%A",temp)
    # 判断和生成该天的数据库条目
    if not online_statistics_db.is_has_time(online_day):
        online_statistics_db.create(online_day,week_no,[])
    online_statistics_db.add_user(online_day,uid)
    print "存入在线状态:"+str(uid)+",日期是"+str(online_day)


def change_online_state(key):
    #活跃度
    starttime = user_db.get_onlinetime(key)
    t=time.localtime()
    tt=datetime.datetime(t[0],t[1],t[2])
    currenttime = time.mktime(tt.timetuple())
    if starttime:
        sttime = datetime.datetime.utcfromtimestamp(starttime)
        cutime = datetime.datetime.utcfromtimestamp(currenttime)
        timediff=(cutime-sttime).days
        if int(timediff)==1:
            onlinestate=user_db.get_onlinestate(key)
            onlinest=str(int(onlinestate['online'])+1)
            user_db.set_onlinestate(key,onlinest)
        elif int(timediff)>1:
            onlinestate=user_db.get_onlinestate(key)
            onlinest=str(int(onlinestate['online'])+1)
            outlinest=str(int(onlinestate['outline'])+int(timediff)-1)
            logging.error('get_onlinestate:onlinest=%s;outlinest=%s',onlinestate['online'],onlinestate['outline'])
            user_db.set_outlinestate(key,onlinest,outlinest)


def change_liveness(user_info):
    # +++ 20150901 user_db中加入活跃度和最后在线时间的时间戳用来排序
    onlinestate1=user_db.get_onlinestate(user_info['key'])
    liveness = long(onlinestate1['online'])*3650-(long(onlinestate1['online'])+long(onlinestate1['outline']))
    user_db.set_liveness(user_info['uid'],liveness)


#+++ 20150508 get offline stra
class GetUserStrategysDes:
    def GET(self):
        """
        input:
            sid:
        output:
            rt: error code
            strategys: {...}
        """
        rt = ecode.FAILED
        strategys = {}

        try:
            i = ws_io.ws_input_des(['sid'])   #数据库读明文数据
            if not i:
                raise ecode.WS_INPUT

            user,dev_id = session_db.user.get_user_and_dev( i['sid'],web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN


            #web端调用（弃）需要管理员来调用
            if user == 'admin' or admin_db.is_has_admin(user):
                user = dev_db.get_cur_user(dev_id)
                ids = dev_db.get_strategy_ids(user)
                strategys = strategy_db.get_strategys_of_user_by_admin(ids)
            #客户端调用
            else:
                newids=[]
                ids = dev_db.get_strategy_ids(user)   #获取user的strategys id（dev_db）
                for stra_id in ids:
                    if(str(stra_id['is_read'])== "false"):   #得到未读取策略id数组
                        newids.append(stra_id)
                strategys = strategy_db.get_strategys_to_user(newids)   #获取未读策略（strategy_db）

                #判定策略是否时间有效，如果无效则删除dev数据库中相应的id号
                dev_id = dev_db.get_dev_id_by_curuser(user)
                key = time.time()
                for stra in strategys:
                    et = time.mktime(time.strptime(str(stra['end']), '%Y-%m-%d %H:%M'))
                    if et < key: #如果策略结束时间比当前服务器时间早，则视为无效数据，需要删除dev_id中的ID号
                        dev_db.complete_strategy(dev_id,stra['strategy_id'])

                #将读取后的id对应标记位 is_read设置为true
                logging.error(user)
                logging.error(dev_id)
                logging.error(len(newids))
                for strid in newids:   #把策略标志位设置为已读
                    dev_db.strategy_is_read(dev_id,strid['strategy_id'])

            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get user strategys des')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output_des(dict(rt=rt.eid,strategys=strategys),dev_id,error_info)

#+++ 20150611 for reply of send cmd
class ReSendCmd:
    def GET(self):
        """
        input:
            sid:
            cmd:
        output:
            rt: error code
            devs: [...]
        """
        rt = ecode.FAILED
        devs = []
        try:
            i = ws_io.ws_input(['sid','cmd'])
            if not i:
                raise ecode.WS_INPUT

            uid = session_db.user.get_user( i['sid'], web.ctx.ip)

            if not uid:
                raise ecode.NOT_LOGIN


            if (uid=='admin') or admin_db.is_has_admin(uid):
                devs=re_cmd_db.get_devs(uid+i['cmd'])
                logging.error("devs from re_cmd_db is : %s",devs)
                #remove cmd
                for dev in devs:
                    if not dev_db.remove_cmd(dev):
                        raise ecode.DB_OP
                if len(devs)==0:
                    re_cmd_db.complete_re_cmd(uid+i['cmd'])
            else:
                raise ecode.NOT_PERMISSION

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('re_send_cmds failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        op_user=session_db.user.get_user( i['sid'], web.ctx.ip)
        op_type=operation.HOME_pushinfo.type
        op_desc=operation.HOME_pushinfo.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )
        return ws_io.ws_output(dict(rt=rt.eid,devs=devs),error_info)

#+++ 20150612 for delete re_cmd dev list
class DelReCmdDev:
    def GET(self):
        """
        input:
            sid:
            cmd:
        output:
            rt: error code
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['sid','cmd'])
            if not i:
                raise ecode.WS_INPUT

            uid = session_db.user.get_user( i['sid'], web.ctx.ip)

            if not uid:
                raise ecode.NOT_LOGIN


            if (uid=='admin') or admin_db.is_has_admin(uid):
#                 devs=re_cmd_db.get_devs(uid+i['cmd'])
#                 #remove cmd +++ 改 20150715 没必要再清指令，已在反馈时清除
#                 for dev in devs:
#                     if not dev_db.remove_cmd(dev):
#                         raise ecode.DB_OP
                re_cmd_db.complete_re_cmd(uid+i['cmd'])
            else:
                raise ecode.NOT_PERMISSION

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('re_send_cmds failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

#+++ 20150616 for reply of send strategy
class ReSendStrategy:
    def GET(self):
        """
        input:
            sid:
            info:
        output:
            rt: error code
            users: [...]
        """
        rt = ecode.FAILED
        users = []
        try:
            i = ws_io.ws_input(['sid','info'])
            if not i:
                raise ecode.WS_INPUT

            uid = session_db.user.get_user( i['sid'], web.ctx.ip)

            if not uid:
                raise ecode.NOT_LOGIN


            if (uid!='admin') and not admin_db.is_has_admin(uid):
                raise ecode.NOT_PERMISSION
            users=re_cmd_db.get_devs(uid+i['info'])
            logging.error("devs from re_cmd_db is : %s",users)
            #remove strategy
            rm_list=[]
            for son in users:
                sonusers=son["users"]
                if len(sonusers)<=0:
                    rm_list.append(son)
                else:
                    strategy_id = i['info'].split(':')[1]
                    for gson in sonusers:
                        cur_user=gson["uid"]
                        dev_db.remove_expire_strategy(cur_user,strategy_id)
            if len(rm_list)>0:
                for rm in rm_list:
                    users.remove(rm)
            logging.error("after re_send_strategy the users is : %s",users)
            if len(users)<=0:
                re_cmd_db.complete_re_cmd(uid+i['info'])
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('re_send_strategy failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,users=users),error_info)

#+++ 20150616 for delete re_strategy users list
class DelReStraUsers:
    def GET(self):
        """
        input:
            sid:
            info:
        output:
            rt: error code
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['sid','info'])
            if not i:
                raise ecode.WS_INPUT

            uid = session_db.user.get_user( i['sid'], web.ctx.ip)

            if not uid:
                raise ecode.NOT_LOGIN


            if (uid=='admin') or admin_db.is_has_admin(uid):
                users=re_cmd_db.get_devs(uid+i['info'])
                #remove strategy
                strategy_id=i['info'].split(":")[1]
                for son in users:
                    sonusers=son["users"]
                    for gson in sonusers:
                        cur_user=gson["uid"]
                        dev_db.remove_expire_strategy(cur_user,strategy_id)
                #发送策略失败、取消则删除该策略中下发失败的用户，若无剩余用户则删除策略
                if strategy_db.mod_users_un_send(strategy_id, users):
                    re_cmd_db.complete_re_cmd(uid+i['info'])
            else:
                raise ecode.NOT_PERMISSION

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('del re strategy failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

#+++20150616
class SendStrategyBySms:
    def POST(self):
        """
        input:
            sid:session id
            users:{作用人}
            info:信息(strategy_type:strategy_id)
        output
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','users','info'])
            if not i:
                raise ecode.WS_INPUT

            user = session_db.user.get_user( i['sid'], str(web.ctx.ip))
            if not user:
                raise ecode.NOT_LOGIN


            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
            #将策略从数据库中读出来,并且以加密短信形式下发
            strategy_id=i['info'].split(":")[1]
            users=json.loads(i["users"])
            if len(users)==0:
                users = re_cmd_db.get_devs(user+i['info'])
            # +++20150911 离线用户短信发送策略多线程操作
            # send_sms_thread = threading.Thread(target=re_send_strategy_by_sms,args=(users,strategy_id,i['info'],user,i['sid']))
            # send_sms_thread.start()
            re_send_strategy_by_sms(users,strategy_id,i['info'],user,i['sid'])
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('send strategy by sms')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        op_user=user
        op_type=operation.STRATEGY_send.type
        op_desc=operation.STRATEGY_send.desc
        op_result=rt.desc
        op_time=time.strftime('%Y-%m-%d %H:%M:%S')
        log_web_db.add_log(op_user,[],op_time ,op_type, op_desc, op_result )
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

# +++20150911 离线用户发送短信逻辑，需要比直接短信发送策略多一个删除缓存表的操作
def re_send_strategy_by_sms(users,strategy_id,info,user,sid):
    # +++20150910 加入多线程发送短信的逻辑
    if SendStrategyBySmsToUsers(users,strategy_id,info):
        re_cmd_db.complete_re_cmd(user+info)
    # +++20150917 查看是否需要向前台反馈信息
    users=re_cmd_db.get_devs(user+info)
    #remove strategy
    rm_list=[]
    for son in users:
        sonusers=son["users"]
        if len(sonusers)<=0:
            rm_list.append(son)
        else:
            strategy_id = info.split(':')[1]
            for gson in sonusers:
                cur_user=gson["uid"]
                dev_db.remove_expire_strategy(cur_user,strategy_id)
    if len(rm_list)>0:
        for rm in rm_list:
            users.remove(rm)
    if len(users)<=0:
        re_cmd_db.complete_re_cmd(user+info)
    else:
        infostr = "strategy:"+info
        config.notify_by_push_server(sid,infostr)


#+++ 20150618 for reply of del strategy
class ReDelStrategy:
    def GET(self):
        """
        input:
            sid:
            info:
        output:
            rt: error code
            re: [...]
        """
        rt=ecode.FAILED
        re=0
        try:
            i = ws_io.ws_input(['sid','info'])
            if not i:
                raise ecode.WS_INPUT

            uid = session_db.user.get_user( i['sid'], web.ctx.ip)

            if not uid:
                raise ecode.NOT_LOGIN


            if (uid=='admin') or admin_db.is_has_admin(uid):
                info_head=i['info'].split(":")[0]+':'
                ids_json=i['info'].split(":")[1]
                ids=json.loads(ids_json)
                for strategy_id in ids:
                    info=info_head+strategy_id
                    users=re_cmd_db.get_devs(uid+info)
                    logging.error("**re_del_strategy*******users is : %s",users)
                    #if no one,remove strategy;if anyone waiting for send del signal,return users
                    if len(users)>0:
                        #下面是ip发送然后手机取走指令的逻辑
                        rm_list=[]
                        for son in users:
                            sonusers=son["users"]
                            if len(sonusers)<=0:
                                rm_list.append(son)
                        if len(rm_list)>0:
                            for rm in rm_list:
                                users.remove(rm)
                        logging.error("**re_del_strategy****after***users is : %s",users)
                    if len(users)==0:
                        strategy_db.del_strategy(strategy_id)
                        re_cmd_db.complete_re_cmd(uid+info)
                    re=re+len(users)
            else:
                raise ecode.NOT_PERMISSION

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('re_send_strategy failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid,re=re),error_info)

#+++ 20150618 for delete re_strategy users list
class ReplaceStraUsers:
    def GET(self):
        """
        input:
            sid:
            info:
        output:
            rt: error code
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['sid','info'])
            if not i:
                raise ecode.WS_INPUT

            uid = session_db.user.get_user( i['sid'], web.ctx.ip)

            if not uid:
                raise ecode.NOT_LOGIN


            if (uid=='admin') or admin_db.is_has_admin(uid):
                #替换strategy_db中的users
                info_head=i['info'].split(":")[0]+':'
                ids_json=i['info'].split(":")[1]
                ids=json.loads(ids_json)
                for strategy_id in ids:
                    info=info_head+strategy_id
                    users=re_cmd_db.get_devs(uid+info)
                    #+++ 20150710 取消即不删策略
                    for son in users:
                        sonusers = son['users']
                        for gson in sonusers:
                            user = gson['uid']
                            dev_id = dev_db.get_dev_id_by_curuser(user)
                            if dev_id is None:
                                continue
                            else:
                                dev_db.strategy_is_read(dev_id, strategy_id)
                    if len(users)==0:
                        strategy_db.del_strategy(strategy_id)
                    else:
                        if strategy_db.is_has_strategy(strategy_id):
                            strategy_db.mod_users_un_del(strategy_id, users)
                    re_cmd_db.complete_re_cmd(uid+info)
            else:
                raise ecode.NOT_PERMISSION

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('replace users of strategy failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

#+++20150618
class DelStrategyBySms:
    def POST(self):
        """
        input:
            sid:
            info:
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['sid','info'])
            if not i:
                raise ecode.WS_INPUT
            #user是管理员
            if not config.get('is_org'):
                raise ecode.NOT_ALLOW_OP

            user = session_db.user.get_user( i['sid'], web.ctx.ip)
            if not user:
                raise ecode.NOT_LOGIN


            if user != 'admin':
                if not admin_db.is_has_admin(user):
                    raise ecode.NOT_PERMISSION
            info = i['info']
            # +++20150916 多线程发送删除策略短信
            # send_del_stra_sms_thread = threading.Thread(target=send_del_stra_sms,args=(info, user, i['sid']))
            # send_del_stra_sms_thread.start()
            send_del_stra_sms(info, user, i['sid'])
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('delete_strategy by sms')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

def send_del_stra_sms(iinfo, user,sid):
    # 给用户发送短信
    info_head = iinfo.split(":")[0] + ':'
    ids_json = iinfo.split(":")[1]
    ids = json.loads(ids_json)
    # +++20150918 是否向前台反馈的
    need_feed_back = 0
    # +++20150922 加入需要反馈的stra_id
    feed_back_strategys = []
    for strategy_id in ids:
        info = info_head + strategy_id
        users = re_cmd_db.get_devs(user + info)
        if DelStraBySms(users, strategy_id, info):
            # +++20150922 短信删除策略失败的情况下已经删除了策略
            # strategy_db.del_strategy(strategy_id)
            #                     #多余的 +++ 20150715
            #                     for son in users:
            #                         sonusers=son["users"]
            #                         for gson in sonusers:
            #                             uid=gson["uid"]
            #                             if dev_db.is_has_user(uid):
            #                                 dev_db.remove_expire_strategy(uid,strategy_id)
            #                             else: #未激活
            #                                 user_db.remove_expire_strategy(uid,strategy_id)
            re_cmd_db.complete_re_cmd(user + info)
        else:
            need_feed_back = 1
            feed_back_strategys.append(strategy_id)
    logging.error("need_feed_back"+str(need_feed_back))
    # +++ 20150918 如果need_feed_back=1的话，就向前端反馈
    infostr = "strategy:"+info_head
    if need_feed_back==1:
        if len(feed_back_strategys)!=0:
            for item in feed_back_strategys:
                infostr+= item+","
            infostr = infostr[0:len(infostr)-1]
    config.notify_by_push_server(sid,infostr)


#+++ 20150619 手机开机获取联系人和策略
class GetContactsAndStrategys:
    def GET(self):
        """
        input:
            sid:
        output:
            rt: error code
            contacts: [{name姓名,email电子邮件,job职位,department部门,pnumber电话号码},...]
            strategys:[]
        """
        rt = ecode.FAILED
        contacts = []
        strategys = []
        dev_id = ''

        try:
            i = ws_io.ws_input_des(['sid'])
            if not i:
                raise ecode.WS_INPUT
            uid,dev_id = session_db.user.get_user_and_dev( i['sid'],web.ctx.ip)
            if not uid:
                raise ecode.NOT_LOGIN
            #contacts
            contacts = user_db.get_contacts_by_uid(uid)
            logging.error("用户的联系人信息:%s",str(contacts))
            #+++20151109 如果取到的联系人信息不为空，则清空联系人缓存区中的联系人信息
            if(len(contacts)>0):
                user_db.del_contact(uid)
            # contacts = getLdapContact(uids)

            #strategys
            newids=[]
            ids=user_db.get_strategy_ids(uid)
            for stra_id in ids:
                if(str(stra_id['is_read'])== "false"):
                    newids.append(stra_id)
            strategys = strategy_db.get_strategys_to_user(newids)
            #将读取后的id对应标记位 is_read设置为true
            for strid in newids:
                user_db.strategy_is_read(uid,strid['strategy_id'])
            #user_db清空策略，dev_db从user_db接收策略
            key = time.time()
            del_list=[]
            for stra in strategys:
                et = time.mktime(time.strptime(str(stra['end']),'%Y-%m-%d %H:%M'))
                if et < key: #如果策略结束时间比当前服务器时间早，则视为无效数据
                    del_list.append(stra['strategy_id'])
            #获取所有的strategy并清空user_db中的,添加到dev_db
            strategy_ids=user_db.get_remain_strategy(uid, del_list)
            if len(strategy_ids)>0:
                dev_db.update_strategy(dev_id, strategy_ids)

            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('get contacts and strategys')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output_des(dict(rt=rt.eid,contacts=contacts,strategys=strategys),dev_id,error_info)

#+++ 20150629 查询当前待同步联系人
class FindContacts:
    def GET(self):
        """
        input:
            sid:
        output:
            rt: error code
        """
        rt = ecode.FAILED
        error_info = ""

        try:
            i = ws_io.ws_input_des(['sid'])
            if not i:
                raise ecode.WS_INPUT
            uid,dev_id = session_db.user.get_user_and_dev( i['sid'],web.ctx.ip)
            if not uid:
                raise ecode.NOT_LOGIN
            user = user_db.get_user_info_by_uid(uid)
            op_user_online.change_online_state(user['key'])
            op_user_online.change_liveness(user)
            op_user_online.change_last_update(uid)
            #contacts
            uids = user_db.get_contacts_by_uid(uid)
            if len(uids)!=0:
                rt = ecode.OK
                error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('find contacts')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)

#+++ 20150709 获取短信网关号码
class GetSmsgateway:
    def GET(self):
        """
        input；
        output:
            rt: error code
            gateway: 短信网关号码
        """

        rt = ecode.FAILED
        gateway=''

        try:
            temps=baseStation.get('gateway')
            if len(temps)==1:
                gateway=temps[0][1]

            rt = ecode.OK
            error_info = ""

        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('GetSmsgateway get failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,gateway=gateway),error_info)

#+++ 20150624 for test send_sms jpype
class TestSendSms:
    def GET(self):
        """
        input:
            uids:[]
            nums:发送次数
            sms:短信内容
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['uids','nums','sms'])
            if not i:
                raise ecode.WS_INPUT

            uids=json.loads(i['uids'])
            nums=int(i['nums'])
            encry_sms=i["sms"]
            logging.warn("three args is %s , %s and %s",uids,nums,encry_sms)
            logging.warn("开始发送短信的时间 %s",str(time.time()))
            for t in range(nums):
                for uid in uids:
                    logging.warn("now send uid is :%s",uid)
                    sms="第"+str(t+1)+"条短信："+encry_sms
                    if not send_sms.send_sms(uid,sms):
                        raise ecode.SMS_TEMP_ERROR
                # send_sms.batch_send_sms(uids,"测试短信")
                logging.warn("it is %s try to send sms finished!",(t+1))
            logging.warn("结束发送短信的时间 %s",str(time.time()))
            # threading.Thread(target=send_sms_func,args=(nums,uids,encry_sms)).start()
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('test send sms')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)

def send_sms_func(nums,uids,smsdata):
    logging.warn("开始发送短信的时间 %s",str(time.time()))
    for t in range(nums):
        for uid in uids:
            logging.warn("now send uid is :%s",uid)
            sms="第"+str(t+1)+"条短信："+smsdata
            result = send_sms.send_sms(uid,sms)
            print(result)
            if not result:
                raise ecode.SMS_TEMP_ERROR
        # send_sms.batch_send_sms(uids,"测试短信")
        logging.warn("it is %s try to send sms finished!",(t+1))
    logging.warn("结束发送短信的时间 %s",str(time.time()))





# 20161227基站上传信息
import time
import httplib
import pseudo_bs_db
import pseudo_bs_phone_db
import safe_gate_db
# 伪基站上传的静态信息
class BSInfo:
    def POST(self):
        """
        input:
            bsid:"session id"
            bsinfo:{
                bsinfo_state:“工作状态”,
                bsinfo_standard:”制式”,
                bsinfo_lon: “经度信息”,
                bainfo_lat: “纬度信息”
                bsinfo_power:“功率”,
                bsinfo_radius: “作用半径”，
                bsinfo_whitelist: “白名单”
            }
        output:
            rt:error code
        """
        infos={}
        rt = ecode.FAILED
        try:
            t=web.input()
            print "1111111111111111111111111111111111111111111"
            print t
            i = ws_io.ws_input(['bsid','bsinfo'])
            #具体逻辑
            uid=i['bsid']
            bsinfo=eval(i['bsinfo'])
            print uid
            print bsinfo
            # bsinfo=json.loads(i['bsinfo'])
            # 最后一次开机时间（存入数据库的时间）
            last_time=time.strftime('%Y-%m-%d %H:%M:%S')
            # uid,type,status,institute,standard,power,radius,position,last_time,remark,whitelist
            standard= bsinfo['bsinfo_standard']
            power=bsinfo['bsinfo_power']
            radius=bsinfo['bsinfo_radius']
            whitelist=bsinfo['bsinfo_whitelist']

            pseudo_bs_db.add_pseudo_bs(  uid,
                                         bsinfo["bsinfo_state"],


                                         bsinfo['bsinfo_lon']+' '+bsinfo['bsinfo_lat'],
                                         last_time,

                                         standard,
                                         power,
                                         radius,
                                         whitelist
                                       )
            rt=ecode.OK
            error_info=""
        except Exception as e:
            logging.error('Send bsinfo failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

# 20161227 基站吸取的手机信息上传
class BSPhoneInfo:
    def POST(self):
        """
        bsid: “session id”,
        bsstatus:0吸附1脱离
  	    bsphoneinfo:（
        output:
            rt:error code
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['bsid','bsstatus','bsphoneinfo'])
            #具体逻辑
            bsid=i['bsid']
            bo=i['bsphoneinfo']
            bsphoneinfo=eval(bo[1:-1])
            # bsstatus 0，正常吸附，1，脱离基站吸附
            status=i['bsstatus']
            pseudo_bs_phone_db.addbsphone(bsid,bsphoneinfo,status)
            # 设置websocket协议，通道号为wjz，向前台传输检测门实时监测数据
            sid="wjz"
            infos=bsphoneinfo
            infos['phone_status']=status
            infos['uid']=bsid

            utime=int(infos['bsphone_time'])*0.001   #长整型转换为python可操作时间戳
            utimeArry=time.localtime(utime)
            logtime=time.strftime("%Y-%m-%d %H:%M:%S",utimeArry)
            infos['bsphone_time']=logtime

            info=json.dumps(infos)
            print info
            conn = httplib.HTTPConnection(
                '%s:%d'%(config.get('pushs_host'),config.get('pushs_port')))
            conn.request("POST", "/pub?id=%s"%(sid), info)
            rt=ecode.OK
            error_info=""
        except Exception as e:
            logging.error('Send bsphoneinfo failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

# 20161205 通信业务管控 基站状态修改
# 修改基站状态 20170104
class ModStatus:
    def POST(self):
        """
        'sid',
        'uid',伪基站设备号
        'state',1开启0关闭
        'cmd',change_state
        'bsinfo_standard',gsm/cdma
        :return:
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['uid','state','cmd','bsinfo_standard'])
            #具体逻辑
            pseudo_bs_db.updatastatus(i['uid'],i['state'])

            infos={}
            # infos['uid']=json.loads(int(i['uid']))
            infos['state']=i['state']
            infos['cmd']=i['cmd']
            infos['bsinfo_standard']=i['bsinfo_standard']
            info=json.dumps(infos)
            # sid="modstatus"
            sid=i['uid']
            conn = httplib.HTTPConnection(
                    '%s:%d'%(config.get('pushs_host'),config.get('pushs_port')))
            conn.request("POST", "/pub?id=%s"%(sid), info)

            rt=ecode.OK
            error_info=""
        except Exception as e:
            logging.error('modstatus failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)
# 20161205 通信业务管控 基站工作半径配置
class ModRadius:
    def POST(self):
        """
        'sid',
        'uid',伪基站设备号
        'radius',工作半径
        'cmd',change_radius
        :return:
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['uid','radius','cmd'])
            #具体逻辑
            infos={}
            # infos['uid']=json.loads(i['uid'])
            infos['radius']=(i['radius'])
            infos['cmd']=i['cmd']
            info=json.dumps(infos)
            # sid="modradius"
            sid=i['uid']
            conn = httplib.HTTPConnection(
                    '%s:%d'%(config.get('pushs_host'),config.get('pushs_port')))
            conn.request("POST", "/pub?id=%s"%(sid), info)
            pseudo_bs_db.updataradius(i['uid'],i['radius'])
            rt=ecode.OK
            error_info=""
        except Exception as e:
            logging.error('modradius failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)
# 20161205 通信业务管控 基站工作功率配置20170104
class ModPower:
    def POST(self):
        """
        'sid',
        'uid',伪基站设备号
        'power',工作功率
        'cmd'，change_power
        :return:
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['uid','power','cmd'])
            #具体逻辑
            infos={}
            # infos['uid']=json.loads(i['uid'])
            infos['power']=(i['power'])
            infos['cmd']=i['cmd']
            info=json.dumps(infos)
            # sid="modpower"
            sid=i['uid']
            print sid
            conn = httplib.HTTPConnection(
                    '%s:%d'%(config.get('pushs_host'),config.get('pushs_port')))
            conn.request("POST", "/pub?id=%s"%(sid), info)
            pseudo_bs_db.updatapower(i['uid'],i['power'])
            rt=ecode.OK
            error_info=""
        except Exception as e:
            logging.error('modpower failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)
# 20161205 通信业务管控 白名单管理 20170104
class ModWhiteList:
    def POST(self):
        """
        'sid',session
        'uid',伪基站设备号
        'imsi',手机imsi号
        'cmd',修改白名单命令
        'change'添加1，删除-1
        :return:
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['uid','imsi','cmd','change'])
            #具体逻辑
            infos={}
            # infos['uid']=json.loads(i['uid'])
            infos['imsi']=(i['imsi'])
            infos['cmd']=i['cmd']
            infos['change']=(i['change'])
            info=json.dumps(infos)
            # sid="modwhitelist"
            sid=i['uid']
            conn = httplib.HTTPConnection(
                    '%s:%d'%(config.get('pushs_host'),config.get('pushs_port')))
            conn.request("POST", "/pub?id=%s"%(sid), info)
            pseudo_bs_db.updatawhitelist(i['uid'],i['change'],i['imsi'])
            rt=ecode.OK
            error_info=""
        except Exception as e:
            logging.error('modwhitelist failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)
# 20161205 通信业务管控 伪装号码短消息发送 不用入库 20170104
class ModMsg:
    def POST(self):
        """
        'sid',
        'uid',伪基站设备号
        'imsi',手机imsi号
        'sms',发送短信内容
        'number',模拟的手机号
        'cmd'，send_msg
        :return:
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['uid','imsi','sms','number','cmd'])
            #具体逻辑
            infos={}
            # infos['uid']=json.loads(i['uid'])
            infos['imsi']=(i['imsi'])
            infos['sms']=i['sms']
            infos['number']=(i['number'])
            infos['cmd']=i['cmd']
            info=json.dumps(infos)
            # sid="modmsg"
            sid=i['uid']
            conn = httplib.HTTPConnection(
                    '%s:%d'%(config.get('pushs_host'),config.get('pushs_port')))
            conn.request("POST", "/pub?id=%s"%(sid), info)
            rt=ecode.OK
            error_info=""
        except Exception as e:
            logging.error('modmsg failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

# 20161205 通信业务管控 伪装手机号码通信 不用入库20170104
class CallPhone:
    def POST(self):
        """
        'sid',
        'uid',伪基站设备号
        'imsi',手机imsi号
        'number',模拟的手机号
        'cmd',call_phone
        :return:
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['uid','imsi','number','cmd'])
            #具体逻辑
            infos={}
            # infos['uid']=json.loads(i['uid'])
            infos['imsi']=(i['imsi'])
            infos['number']=(i['number'])
            infos['cmd']=i['cmd']
            info=json.dumps(infos)
            # sid="callphone"
            sid=i['uid']
            conn = httplib.HTTPConnection(
                    '%s:%d'%(config.get('pushs_host'),config.get('pushs_port')))
            conn.request("POST", "/pub?id=%s"%(sid), info)
            rt=ecode.OK
            error_info=""
        except Exception as e:
            logging.error('callphone failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)


# 20170103 检测门业务管控
class SGInfo:
    def POST(self):
        """
        input:
            “sid”:”检测门设备号”,
             sgstatus: 0 离线 1 在线
  	         institute: 检测门的位置描述信息
            }
        output:
            rt:error code
        """
        rt = ecode.FAILED
        try:
            t=web.data()
            i=eval(t)
            print "11111111111111111111111111111111111111111"
            print i
            position=(i['institute']).decode('gbk')
            uid=i['sid']
            status=i['sgstatus']

            op_time=time.strftime('%Y-%m-%d %H:%M:%S')
            # 检测门上传静态信息写入数据库默认工作状态离线
            print op_time
            pseudo_bs_db.add_safe_gate(  uid,
                                         status,
                                         op_time,
                                         position,
                                        )
            rt=ecode.OK
            error_info=""
        except Exception as e:
            logging.error('upload  safe_gate info  failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)
# 20170103 检测门业务管控 动态信息上传

class SGNUMInfo:
    def POST(self):
        """
        sid: 检测门设备号
  	    sg_normal: 正常通过人数
  	    sg_alarm: 报警人数
  	    sg_time: 报警时刻
        output:
            rt:error code
        """
        rt = ecode.FAILED
        try:
            t=web.data()
            i=eval(t)
            # i = ws_io.ws_input(['sid','sg_normal','sg_alarm','sg_time'])
            print "##################"
            print i
            #具体逻辑
            uid=i['sid']
            sg_normal=i['sg_normal']
            sg_alarm=i['sg_alarm']

            logtime=i['sg_time']
            sg_position=i['sg_position']
            # utime=int(sg_time)*0.001   #长整型转换为python可操作时间戳
            # utimeArry=time.localtime(utime)
            # logtime=time.strftime("%Y-%m-%d %H:%M:%S",utimeArry)

            # 检测门动态上传的信息存到数据库的safe_gate_db中
            safe_gate_db.addalarminfo(uid,sg_normal,sg_alarm,logtime,sg_position)
            # 设置websocket协议，通道号为jcm，向前台传输检测门实时监测数据
            sid="jcm"
            infos={}
            infos['uid']=uid
            infos['sg_normal']=sg_normal
            infos['sg_alarm']=sg_alarm
            infos['sg_time']=logtime
            infos['sg_position']=sg_position
            info=json.dumps(infos)
            print info
            conn = httplib.HTTPConnection(
                '%s:%d'%(config.get('pushs_host'),config.get('pushs_port')))
            conn.request("POST", "/pub?id=%s"%(sid), info)

            rt=ecode.OK
            error_info=""
        except Exception as e:
            logging.error('send safe_gate dynamic infos failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)


class ShutDown:
    def POST(self):
        """
        sid: 检测门设备号
  	    sg_normal: 正常通过人数
  	    sg_alarm: 报警人数
  	    sg_time: 报警时刻
        output:
            rt:error code
        """
        rt = ecode.FAILED
        try:
            i = ws_io.ws_input(['uid'])
            #具体逻辑
            uid=i['uid']
            pseudo_bs_db.shutdown(uid)
            print "gogogogogogogogoggo"
            rt=ecode.OK
            error_info=""
        except Exception as e:
            logging.error('send safe_gate dynamic infos failed')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        return ws_io.ws_output(dict(rt=rt.eid),error_info)
