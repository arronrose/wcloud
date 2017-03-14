# -*- coding: utf8 -*-

import user_db
import dev_db
import trace_db
import online_statistics_db
import time
import datetime
import logging
import ecode
import sha


def check_login(uid,pw,dev_id):
    """
    用户登录检测
    :param uid:
    :param pw:
    :param dev_id:
    :return:
    """
    if dev_id!='web':
        if not user_db.check_pw(uid, sha.new(pw).hexdigest()):   #验证密码
            raise ecode.USER_AUTH
        else:   #密码验证通过，登陆成功
            devs = user_db.devs(uid)
            if devs!=None and len(devs)>0:
                user_dev_id = devs[0]
                if user_dev_id!=dev_id:
                    raise ecode.NOT_PERMISSION
            else:
                if dev_db.is_has_dev(dev_id):
                    dev_cur_user = dev_db.get_cur_user(dev_id)
                    if dev_cur_user!=None and dev_cur_user!='':
                        if dev_cur_user!=uid:
                            raise ecode.NOT_PERMISSION
        return True


def verify_user(uid):
    """
    用户首次登录验证，和密码的过期检测
    :param uid:
    :return:
    """
    user_db.verified(uid)
    user_db.pw_exp(uid,True)


def bind_user_dev(uid,dev_id):
    """
    绑定用户和设备
    :param uid:
    :param dev_id:
    :return:
    """
    user_db.add_dev(uid,dev_id)
    dev_db.add_dev(dev_id,uid)


def loc_op(user,dev_id):
    """
    将遗留的地利位置信息整理上传
    :param user:
    :param dev_id:
    :return:
    """
    loc = dev_db.get_loc(dev_id)
    upt = user_db.get_last_update(user['key'])
    value = loc['lon']+":"+loc['lat']+":offline"
    trace_db.set(user['uid'],upt,value)


# def online_op(key):
#     """
#     用户登录时与时间相关的操作
#     :param key: 登录用户的主键
#     :return:
#     """
#     if len(key)<=0:
#         raise ecode.DATA_LEN_ERROR
#     try:
#         #进入到这个函数应该已经找到用户了,构造用户在线时间
#         online_time_stamp = str(int(time.time()))   #获取登录时的秒时间戳
#         localtime = time.localtime()
#         date_of_today = datetime.datetime(localtime[0],localtime[1],localtime[2])
#         date_stamp = time.mktime(date_of_today.timetuple())
#         result = user_db.get_user_info_by_key(key)
#         if result:
#             if not result.has_key("online"):
#                 user_db.set_last_update(result['key'],online_time_stamp)
#                 # user_db.on
#                 # users.update({"key":key},{"$set":{"last_update":online_time_stamp,"online":1,
#                 #                           "outline":0,"onlinetime":date_stamp}})
#             else:
#                 user_db.update({"key":key},{"$set":{"last_update":online_time_stamp}})
#     except Exception as e:
#         logging.error('create user failed. key:%s', key)


def change_online_state(key):
    """
    修改用户的在线状态相关的值
    :param key:
    :return:
    """
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


def change_last_update(uid):
    online_time_stamp = str(int(time.time()))   #获取登录时的秒时间戳
    logging.error("断线重连时间"+str(online_time_stamp))
    localtime = time.localtime()
    date_of_today = datetime.datetime(localtime[0],localtime[1],localtime[2])
    date_stamp = time.mktime(date_of_today.timetuple())
    result = user_db.get_user_info_by_uid(uid)
    if result:
        if not result.has_key("online"):
            user_db.set_last_update(uid,online_time_stamp)
            user_db.set_outlinestate(result['key'],1,0)
        else:
            user_db.set_last_update(uid,online_time_stamp)

def post_online_status(uid):
    # 生成在线日期
    time_stamp=time.localtime()
    online_day=time.strftime("%Y-%m-%d", time_stamp)
    week_no = time.strftime("%A",time_stamp)
    # 判断和生成该天的数据库条目
    if not online_statistics_db.is_has_time(online_day):
        online_statistics_db.create(online_day,week_no,[])
    online_statistics_db.add_user(online_day,uid)
    logging.error("存入在线状态:"+str(uid)+",日期是"+str(online_day))