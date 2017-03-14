#!/usr/bin/env python
# -*- coding: utf8 -*-

import web
import ws2user
import ws2caps
import ws2org
import ws2appstore
import ws2addr
import ecode
import ws_io
import config
# import send_sms   #+++ 20150402
#+++ 20150713
import backup


version = '2.0.1'

class Version:
    def GET(self):
        rt = ecode.OK
        return ws_io.ws_output(dict(rt=rt.eid
            ,version=version
            ,is_org=config.get('is_org')
            ,is_debug=config.get('is_debug')))

urls = ( 
        "/a/wp/user/test_send_sms", ws2user.TestSendSms,   #+++20150624
        "/a/wp/version", Version,
        "/a/wp/user/reg", ws2user.Reg,      #弃用
        "/a/wp/user/captcha", ws2user.Captcha,   #+++20150402 短信向手机发送验证码，暂时弃用
        "/a/wp/user/login", ws2user.Login,
        "/a/wp/user/login_sms", ws2user.LoginSms,   #+++20150409
        "/a/wp/user/logout", ws2user.Logout,
        "/a/wp/user/send_cmd", ws2user.SendCmd,   #+++20150611 接口修改
        "/a/wp/user/send_all_cmd", ws2user.SendAllCmd,   #+++20150827 接口添加 +++20150910 接口修改
        "/a/wp/user/send_staticinfo", ws2user.SendStaticinfo,   #+++10.27
        "/a/wp/user/send_cmd_and_rs", ws2user.SendCmdAndRs,
		"/a/wp/user/get_cmds", ws2user.GetCmds,
        "/a/wp/user/get_cmds_encry", ws2user.GetCmdsEncry,
        "/a/wp/user/get_cmds_des", ws2user.GetCmdsDes,   #+++ 20150507 20150611改
        "/a/wp/user/re_send_cmd", ws2user.ReSendCmd,   #+++ 20150611
        "/a/wp/user/del_re_cmd_dev", ws2user.DelReCmdDev,   #+++ 20150612
        "/a/wp/user/re_send_strategy", ws2user.ReSendStrategy,   #+++ 20150616
        "/a/wp/user/del_re_stra_users", ws2user.DelReStraUsers,   #+++ 20150616
        "/a/wp/user/send_strategy_by_sms", ws2user.SendStrategyBySms,   #+++ 20150616
        "/a/wp/user/re_del_strategy", ws2user.ReDelStrategy,   #+++ 20150618
        "/a/wp/user/replace_stra_users", ws2user.ReplaceStraUsers,   #+++ 20150618
        "/a/wp/user/del_strategy_by_sms", ws2user.DelStrategyBySms,   #+++ 20150618 2101611122 删除策略
        "/a/wp/user/complete_cmd", ws2user.CompleteCmd,
        "/a/wp/user/set_cmd_respons", ws2user.SetCmdRespons,
        "/a/wp/user/set_all_respons", ws2user.SetallRespons,
        "/a/wp/user/get_cmd_respons", ws2user.GetCmdRespons,
        "/a/wp/user/send_strategy", ws2user.SendStrategy,   #+++ 改 20150506  2101611122 策略下发
        "/a/wp/user/get_strategys", ws2user.GetStrategys,
        "/a/wp/user/get_user_strategys",ws2user.GetUserStrategys,   #+++ 改20150508
        "/a/wp/user/get_user_strategys_encry",ws2user.GetUserStrategysEncry,   #+++
        "/a/wp/user/get_user_strategys_des",ws2user.GetUserStrategysDes,
        "/a/wp/user/get_user_need_del_strategys",ws2user.GetUserNeedDelStrategys,
        "/a/wp/user/get_strategy_by_id", ws2user.GetStrategyById,
        "/a/wp/user/get_strategy_by_id1", ws2user.GetStrategyById1,
        "/a/wp/user/get_strategy_by_id1_des", ws2user.GetStrategyById1Des,   #+++ 20150507
        "/a/wp/user/get_strategy_by_id1_encry", ws2user.GetStrategyById1Encry,   #+++
        "/a/wp/user/modify_strategy", ws2user.ModifyStrategy,   #+++改 20150710 2101611122 修改策略
        "/a/wp/user/modify_strategy_by_sms",ws2user.ModifyStrategyBySms,   #+++ 改 20150714 2101611122 修改策略
        "/a/wp/user/check_modify_stra_result",ws2user.CheckModifyResult,   #+++ 20150702
        "/a/wp/user/del_modify_stra_users",ws2user.DelModifyStraUsers,
        "/a/wp/user/modify_users_of_strategy", ws2user.ModifyUsersofStrategy,
        "/a/wp/user/del_strategy", ws2user.DeleteStrategy,   #+++改20150409 20150615 20150618 2101611122 删除策略
        "/a/wp/user/del_user_strategy", ws2user.DeleteUserStrategy,   #+++改20150618 2101611122 删除策略
        "/a/wp/user/complete_strategy", ws2user.CompleteStrategy,
        "/a/wp/user/send_contacts",ws2user.SendContacts,
        "/a/wp/user/get_contacts",ws2user.GetContacts,
        "/a/wp/user/get_contacts_des",ws2user.GetContactsDes,   #+++ 20150507
        "/a/wp/user/get_contacts_encry",ws2user.GetContactsEncry,   #+++添加dev_id
        "/a/wp/org/get_user_log_count",ws2org.GetUserLogCount,
        "/a/wp/org/get_web_logs",ws2org.GetWebLogs,  #+++获取管理员日志
        "/a/wp/org/get_log_contacts",ws2org.GetLogContacts,   #+++20151116 获取下发联系人日志通讯录内容
        "/a/wp/org/get_log_control_users",ws2org.GetLogControlUsers,  #+++20151118 获取日志作用用户
        "/a/wp/user/loc", ws2user.Loc,
        "/a/wp/user/loc_des", ws2user.LocDes,   #+++ 20150507
        "/a/wp/user/online_data", ws2user.OnlineData,
#         "/a/wp/user/loc_and_cur_user",ws2user.GetLocAndCuruser,
        "/a/wp/user/get_devs", ws2user.GetDevs,
        "/a/wp/user/del_me", ws2user.DelMe,
        "/a/wp/user/forget_pw", ws2user.ForgetPW,
        "/a/wp/user/set_pw", ws2user.SetPW,
        "/a/wp/user/get_acc_info", ws2user.GetAccInfo,
        "/a/wp/user/get_dev_info", ws2user.GetDevInfo,
        "/a/wp/user/get_online_status", ws2user.GetOnlineStatus,
        "/a/wp/user/dev_static_info", ws2user.DevStaticInfo,
        "/a/wp/user/dev_static_info_des", ws2user.DevStaticInfoDes,   #+++ 20150507
        "/a/wp/user/dev_app_info", ws2user.DevAppInfo,
        "/a/wp/user/dev_wapp_info", ws2user.DevWebAppInfo,
        "/a/wp/user/log", ws2user.Log,
        "/a/wp/user/test", ws2user.Test,
        "/a/wp/user/get_devs_info", ws2user.DevsInfo,   #+++20150206
        "/a/wp/user/send_strategy_sms", ws2user.SendStrategySms,   #+++20150403  2101611122 策略下发
        "/a/wp/user/send_cmd_sms", ws2user.SendCmdSms,   #+++20150403 改20150612
        "/a/wp/user/del_strategy_sms", ws2user.DeleteStrategySms,   #+++20150409 20150615
        "/a/wp/user/get_contacts_and_strategys",ws2user.GetContactsAndStrategys,   #+++ 20150619
        "/a/wp/user/find_contacts",ws2user.FindContacts,   #+++ 20150629
        "/a/wp/user/get_smsgateway",ws2user.GetSmsgateway,   #+++ 20150709







        "/a/wp/org/login", ws2org.Login,
        "/a/wp/org/set_captcha", ws2org.SetCaptcha,   #+++ 20150804
        "/a/wp/org/logout", ws2org.Logout,
        "/a/wp/org/set_pw", ws2org.SetPW,
        "/a/wp/org/add_admin", ws2org.AddAdmin,
        "/a/wp/org/mod_admin", ws2org.ModAdmin,
        "/a/wp/org/org_info", ws2org.OrgInfo,
        "/a/wp/org/ldap_config", ws2org.LdapConfig,
        "/a/wp/org/ldap_users", ws2org.LdapUsers,
        "/a/wp/org/ldap_ous",ws2org.LdapOus,
        "/a/wp/org/ldap_onelevel",ws2org.LdapOneLevel,
        "/a/wp/org/ldap_onelevel_uid_hide",ws2org.LdapOneLevelUidHide,
        "/a/wp/org/ldap_get_ou_by_sid",ws2org.LdapGetOuBySid,
        "/a/wp/org/ldap_tree",ws2org.LdapTree,
        "/a/wp/org/ldap_users_allow_use", ws2org.LdapUsersAllowUse,
        "/a/wp/org/user_info", ws2org.UserInfo,
        "/a/wp/org/checkpwd_and_devs", ws2org.CheckPwdAndDevs,
        "/a/wp/org/user_log", ws2org.UserLog,
        "/a/wp/org/ldap_sync", ws2org.LdapSync,
        "/a/wp/org/ldap_sync_config", ws2org.LdapSyncConfig,
        "/a/wp/org/logo", ws2org.OrgLogo,
        "/a/wp/org/ldap_add_user", ws2org.LdapAddUser,
        "/a/wp/org/ldap_mod_user", ws2org.LdapModUser,   #+++20150331   修改用户新接口
        "/a/wp/org/check_username",ws2org.CheckUserName, #+++20160420   查看用户姓名是否合法
        "/a/wp/org/ldap_del_user", ws2org.LdapDelUser,   #+++ 20150715 改
        "/a/wp/org/trace_loc_info", ws2org.TraceLocInfo,
        "/a/wp/org/send_certification", ws2org.SendCertification,
        "/a/wp/org/get_all_baseStation", ws2org.GetAllBaseStation,   #+++10.27
        "/a/wp/org/get_all_preStra", ws2org.GetAllPreStra,   #+++ 20150506
        "/a/wp/org/get_strategy_by_desc", ws2org.GetStrategyByDesc,   #+++ 20150506
        "/a/wp/org/send_pre_strategy", ws2org.SendPreStrategy,   #+++20150506
        "/a/wp/org/del_preStra", ws2org.DelPreStra,   #+++20150507
        "/a/wp/org/upldap_excel",ws2org.UpldapByexcel,     #+++++20150601
        "/a/wp/org/get_all_users",ws2org.GetAllUsers,      #+++++20150722
        "/a/wp/org/change_selected_users",ws2org.ChangeSelectedUsers,   #+++++20150727  for change selected user
        "/a/wp/org/change_selected_users_uid_hide",ws2org.ChangeSelectedUsersUidHide,
        "/a/wp/org/get_page_users",ws2org.GetOnePageUsers,       #+++++ 20150728 for get page users
        "/a/wp/org/get_page_users_uid_hide",ws2org.GetOnePageUsersUidHide,
        "/a/wp/org/is_has_admin",ws2org.IsHasAdmin,      #+++++20150828 for check admin existence
        "/a/wp/org/check_old_psw",ws2org.CheckOldPsw,    #+++++20150828 for check admin old psw and change psw
        "/a/wp/org/check_is_has_user",ws2org.CheckIsHasUser, #+++++20150828 for check is has user
        "/a/wp/org/check_uid_exist",ws2org.CheckUidExist,   #+++++20160726 for check uid exist
        "/a/wp/org/check_is_has_username",ws2org.CheckIsHasUsername, #++++20160724 for check is has user name
        "/a/wp/org/get_user_by_uid",ws2org.GetUserByUid, #+++++ 20160219 get userinfo by uid
        "/a/wp/org/get_dev_by_id",ws2org.GetDevById,     #+++++20160222 get devinfo by uid
#         "/a/wp/org/test_is_online",ws2org.TestIsOnline,     #+++++20150625 for liveness of all users
        "/a/was/applist", ws2appstore.AppList,
        "/a/was/appslist", ws2appstore.GetAppList,
        "/a/was/appinfo", ws2appstore.AppInfo,
        "/a/was/add_native_app", ws2appstore.AddNativeApp,
        "/a/was/update_native_app", ws2appstore.UpdateNativeApp,
        "/a/was/add_web_app", ws2appstore.AddWebApp,
        "/a/was/update_web_app", ws2appstore.UpdateWebApp,
        "/a/was/del_app", ws2appstore.DelApp,
        "/a/was/send_app", ws2appstore.SendApp,
        "/a/was/get_sys_version", ws2appstore.GetSysVersion,   #+++ 20150626
        "/a/was/get_app_addr", ws2appstore.GetAppAddr,
        "/a/wqs/orglist", ws2addr.OrgList,
        "/a/wqs/orgaddr", ws2addr.OrgAddr,
        "/a/wqs/add_org", ws2addr.AddOrg,
        "/a/wqs/del_org", ws2addr.DelOrg,
        "/a/backup/data_backup",backup.DataBackup,   #+++ 20150713
        "/a/backup/reg_backup",backup.RegBackup,   #+++ 20150713
        "/a/backup/login_backup",backup.LoginBackup,   #+++ 20150713
        "/a/backup/logout_backup",backup.LogoutBackup,   #+++ 20150713
        "/a/backup/get_dev_data",backup.GetDevData,   #+++ 20150713
        "/a/wp/org/share_user_info",ws2org.ShareUserInfo,
        "/a/wp/org/upload_ip",ws2org.UploadIP,
        #+++20151230数据统计部分接口
        "/a/wp/org/get_ou_base_info",ws2org.GetOuBaseInfo,
        "/a/wp/org/search_first_page_users",ws2org.SearchFirstPageUsers,
        "/a/wp/org/search_all_users",ws2org.SearchAllUsers,
		"/a/wp/org/get_liveness_data",ws2org.GetLivenessData,
        "/a/wp/org/get_online_data",ws2org.GetUserOnlineData,
        # 三员分立
        "/a/wp/org/del_admin", ws2org.DelAdmin,   #+++ 11.20
        "/a/wp/org/add_master", ws2org.AddMaster,   #+++ 11.18
        "/a/wp/org/del_master", ws2org.DelMaster,   #+++ 11.20
        "/a/wp/org/add_auditor", ws2org.AddAuditor,   #+++ 11.19
        "/a/wp/org/del_auditor", ws2org.DelAuditor,   #+++ 11.20
        "/a/wp/org/add_sa", ws2org.AddSA,   #+++ 11.19
        "/a/wp/org/del_sa", ws2org.DelSA,   #+++ 11.20
        "/a/wp/org/master_tree", ws2org.MasterTree,   #+++ 11.19
        "/a/wp/org/admin_tree", ws2org.adminTree,   #+++ 11.20
        "/a/wp/org/sa_tree", ws2org.SaTree,   #+++ 11.20
        "/a/wp/org/auditor_tree", ws2org.AuditorTree,   #+++ 11.20
        "/a/wp/org/log_web", ws2org.LogWeb,   #+++ 11.21
        "/a/wp/org/get_audit_log", ws2org.GetAuditLogs,   #+++ 11.21
        "/a/wp/org/search_logs", ws2org.SearchLogs,   #+++ 11.22
        "/a/wp/org/auditlog_check", ws2org.AuditlogCheck,   #+++ 11.23
        "/a/wp/org/export_log", ws2org.ExportLog,   #+++ 11.23
        "/a/wp/org/get_space_state", ws2org.GetSpaceState,   #+++ 11.23
        "/a/wp/org/set_log_space", ws2org.SetLogSpace,   #+++ 11.23
        "/a/wp/org/auto_search_by_sid",ws2org.AutoSearchBySid,
        "/a/wp/org/auto_search_adm_by_sid",ws2org.AutoSearchAdmBySid,
        "/a/wp/org/auto_selected_by_sid",ws2org.AutoSelectedBySid,
        "/a/wp/org/auto_selected_adm_by_sid",ws2org.AutoSelectedAdmBySid,



         #  20161206+++通信业务管控
        "/a/wp/org/add_control",ws2org.AddControl,#新增设备
        "/a/wp/org/del_control_user",ws2org.DelControlUser,#删除设备（中间列表时）
        "/a/wp/org/control_tree",ws2org.ControlTree,#获取基站设备的所属部门，左侧聚类树显示
        "/a/wp/org/control_tree_list",ws2org.ControlTreeList,#中间设备详细信息，聚类之后显示
        "/a/wp/org/control_tree_info",ws2org.ControlTreeInfo,#获取设备详细信息（单个设备右下角的详细信息）
        "/a/wp/org/control_whitelist_info",ws2org.ControlWhitelistInfo,#获取设备白名单（单个设备右下角的白名单列表）

        # 20161205+++通信业务管控 下行数据
        "/a/wp/user/modwhitelist",ws2user.ModWhiteList,# 修改白名单(修改(删除)和加入)
        "/a/wp/user/modstatus",ws2user.ModStatus,# 修改基站状态
        "/a/wp/user/modradius",ws2user.ModRadius, # 修改工作半径
        "/a/wp/user/modpower",ws2user.ModPower,# 修改基站功率
        "/a/wp/user/modmsg",ws2user.ModMsg,# 发送短消息
        "/a/wp/user/callphone",ws2user.CallPhone, # 伪装号码通信
        #
        # # 20161205+++通信业务管控 上行数据
        "/a/wp/user/bsinfo",ws2user.BSInfo,
        "/a/wp/user/bsphoneinfo",ws2user.BSPhoneInfo,#伪基站传吸附信息的手机
        # 20170103检测门管控
        "/a/wp/user/sginfo",ws2user.SGInfo,#前端动态显示 检测门静态信息设备号和位置信息描述
        "/a/wp/user/sgnuminfo",ws2user.SGNUMInfo,#前端动态显示 检测门静态信息设备号和位置信息描述
        "/a/wp/user/shutdown",ws2user.ShutDown,#前端动态显示 检测门静态信息设备号和位置信息描述

        # 20170221wifi信息
        "/a/wp/org/citywifiinfos",ws2org.CityWifiInfos,
        "/a/wp/org/citywifiinfos1",ws2org.CityWifiInfos1,
        # "/a/wp/org/citywifiinfos2",ws2org.CityWifiInfos2,
        # "/a/wp/org/citywifiinfos3",ws2org.CityWifiInfos3,
        )


#+++ 20150721 关闭debug模式
web.config.debug = False

app = web.application(urls, globals())
application = app.wsgifunc()



