# -*- coding: utf8 -*-

##########后台审计用，留着################

class Operation:
    type = ''
    desc = ''
    def __init__(self,type,desc):
        self.type = type
        self.desc = desc

    def __str__(self):
        return repr(self.type)


LOGIN_admin           =Operation('操作员登陆','登陆成功')
LOGIN_master          =Operation('管理员登陆','登陆成功')
LOGIN_sa              =Operation('安全员登陆','登陆成功')
LOGIN_auditor         =Operation('审计员登陆','登陆成功')
LOGIN_failed          =Operation('登陆','登陆失败')
LOGOUT                =Operation('退出','退出登录')
SETPW_master          =Operation('修改密码','管理员修改密码')
SETPW_admin           =Operation('修改密码','操作员修改密码')
SETPW_auditor         =Operation('修改密码','审计员修改密码')
SETPW_sa              =Operation('修改密码','安全员修改密码')
DEL_master            =Operation('用户删除','删除管理员')
DEL_admin             =Operation('用户删除','删除操作员')
DEL_auditor           =Operation('用户删除','删除审计员')
DEL_sa                =Operation('用户删除','删除安全员')

# 20161117-18+++修改添加
DEL_user              =Operation('用户删除','删除手机用户')
#uid
ADD_admin              =Operation('添加账户','添加操作员')
ADD_master             =Operation('添加账户','添加管理员')
ADD_sa                 =Operation('添加账户','添加安全员')
ADD_auditor            =Operation('添加账户','添加审计员')

ACC_adduser            =Operation('添加账户','添加手机用户')
CHANGE_admin           =Operation('修改账户信息','修改操作员信息')
CHANGE_user            =Operation('修改账户信息','修改手机用户信息')
CONTACTS_send          =Operation('同步联系人','下发联系人')

STRATEGY_qc            =Operation('设备管理','清除策略')
STRATEGY_send          =Operation('策略配置','策略下发')
STRATEGY_del           =Operation('策略配置','删除策略')
STRATEGY_mod           =Operation('策略配置','修改策略')
# STRATEGY_add           =Operation('策略配置','配置策略') 下发和配置下发，是同一个





# 同一个接口，同一个函数，所以日志统一推送HOME_pushinfo
HOME_pushinfo          =Operation('设备管理','推送通知')
HOME_lockpw            =Operation('设备管理','修改锁屏密码')
#uid
HOME_lockphone         =Operation('设备管理','锁定手机用户')
HOME_unlockphone       =Operation('设备管理','解锁手机用户')








# 20161117 ---待添加的
#HOME_control           =Operation('设备管理','多维管控')
MAPP_sendapp           =Operation('应用管理','向用户推送应用')
#MAPP_upapp             =Operation('应用管理','上传本地应用')
#MAPP_del               =Operation('应用管理','删除应用')
