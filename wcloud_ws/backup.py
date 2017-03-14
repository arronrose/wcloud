# -*- coding: utf8 -*-

import web
import logging
import sha
import ws_io
import ecode
import send_sms
##########################################
import shutil   #+++12.18
import os   #+++12.18
import commands   #+++12.18
import hashlib   #+++12.18
#########################################
import backup_user_db   #+++20150713
import config   #+++20150713
#########################################
import sqlite3   #+++20151201
import codecs    #+++20151201
import traceback


#注册
class RegBackup:
    def POST(self):
        """
        input:
            uid: user id / phone number
            dev_id: imei
            pw: passwd
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['uid','pw','dev_id'])
            if not i:
                raise ecode.WS_INPUT

            if not send_sms.check_pnumber( i['uid']) :
                raise ecode.ERROR_PNUMBER

            if not backup_user_db.create(i['uid'],sha.new(i['pw']).hexdigest(),''):
                raise ecode.USER_EXIST

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('backup user reg.')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)

#登陆
class LoginBackup:
    def POST(self):
        """
        input:
            uid: user id
            pw: password
            dev_id:
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['uid','pw','dev_id'])
            if not i:
                raise ecode.WS_INPUT
            if not backup_user_db.check_pw(i['uid'], sha.new(i['pw']).hexdigest()):
                if not backup_user_db.is_has_user(i['uid']):
                    raise ecode.USER_UN_REGISTER
                else:
                    raise ecode.USER_AUTH
            #登陆标识为dev_id,dev_id为空则未登陆
            if not backup_user_db.set_dev(i['uid'], i['dev_id']):
                raise ecode.DB_OP
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('backup user login')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)

#登出
class LogoutBackup:
    def POST(self):
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
            #登陆标识为dev_id,dev_id为空则未登陆
            if not backup_user_db.set_dev(i['uid'],''):
                raise ecode.DB_OP
            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('backup user logout')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid),error_info)

#数据备份
class DataBackup:
    def POST(self):
        """
        input:
            uid: user id
            backuptime: (int)
            backup_type: (int) 备份类型：0 累加，1 覆盖
            data_path: default path
            data_verify:"file:md5"
        output:
            rt: error code
        """
        rt = ecode.FAILED

        try:
            i = ws_io.ws_input(['uid','backuptime','backup_type','data_path','data_verify'])
            data=i['data_path']
            if not i:
                raise ecode.WS_INPUT
            
            if not backup_user_db.get_dev(i['uid']):
                raise ecode.NOT_LOGIN
            
            #生成存储路径
            phonenumber=i['uid']
            backup_type = i['backup_type']
            backuptime=i['backuptime']
            backup_home='/home/wcloud/opt/org/backup/'
            file_path=os.path.join(backup_home,phonenumber,backuptime)   #存放备份的文件夹
            back_host=config.get('redis_host')   #远程主机
            #远程创建路径
            rt_mkdir=os.popen('ssh '+back_host+' "mkdir -p %s"'%(file_path)).close()
            # if rt_mkdir:
            #将文件放到生成的目录下
            data_verify=i['data_verify']
            dataverify=data_verify.split(':')
            filename=dataverify[0]
            #校验文件
            # rt_md5=commands.getstatusoutput('md5sum -b %s'%(data))
            # print rt_md5
            # file_md5=rt_md5[1][0:32]
            # logging.warn("the md5 of backup data is : %s",file_md5)
            # if file_md5!=dataverify[1]:
            #     commands.getstatusoutput('ssh '+back_host+' "rm %s"'%(file_path))   #校验失败，删除文件
            #     raise ecode.FAILED
            # +++20151204 查看备份类型，决定是否进行覆盖操作

            # 将原来已有的短信和通讯录插入新的文件中
            if(filename.split(".")[1].lower()=="vcf"):
                old_array = backup_user_db.get_contacts(phonenumber)
                logging.error("已有通讯录"+str(len(old_array))+"条")
                analysis_contact(phonenumber,old_array,data,int(backup_type))
            else:
                old_array = backup_user_db.get_smss(phonenumber)
                logging.error("已有短信"+str(len(old_array))+"条")
                analysis_sms(phonenumber,old_array,data,int(backup_type))


            #远程传输
            logging.error("存在新文件路径:"+str(os.path.exists(data)))
            file_backup=os.path.join(file_path,filename)
            rt_scp=commands.getstatusoutput('scp %s %s:%s'%(data,back_host,file_backup))
            logging.error('scp %s %s:%s ! %s',data,back_host,file_backup,rt_scp)
            if rt_scp[0]!=0:
                raise ecode.DB_OP

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('data backup')
            error_info = str(traceback.format_exc()).replace("\n"," ")
        commands.getstatusoutput( 'rm -f %s'%(data))   #删除临时文件
            
        return ws_io.ws_output(dict(rt=rt.eid),error_info)

# +++20151130 对比生成最新的通讯录文件 op_type 0 为累加，1为覆盖
def analysis_contact(uid,old_array,new_path,op_type):
    if op_type==1:
        backup_user_db.del_contact(uid)
        old_array = []
    logging.error("开始解析%s通讯录内容"%(uid,))
    logging.error("已有通讯录长度:"+str(len(old_array)))
    new_file = open(new_path,"r")
    new_array = getContactArray(new_file)
    logging.error("新文件中通讯录长度:"+str(len(new_array)))
    not_exist_contacts = []
    for new_item in new_array:
        in_array = False
        for old_item in old_array:
            if new_item.equalTo(old_item):
                in_array=True
                break
        logging.error("通讯录条目已存在："+str(in_array))
        if not in_array:
            not_exist_contacts.append(new_item.to_dict())
        else:
            continue
    logging.error("不存在的通讯录条目有"+str(len(not_exist_contacts))+"条")
    for item in not_exist_contacts:
        backup_user_db.save_contact(uid,item)
        old_array.append(item)
    logging.error("合并之后通讯录条目有"+str(len(old_array))+"条")
    write2VcfFile(old_array,new_path)
    new_file.close()

class CardClass:
    VERSION = ""
    N=""
    FN=""
    TEL=""
    def __init__(self):
        pass;
    def __del__(self):
        pass;
    def toCsvLine(self):
        return str(self.VERSION) + ','+ self.N+ "," + self.FN + "," + self.TEL
    def printContact(self):
        logging.error(self.toCsvLine())
    def to_dict(self):
        return dict(FN=self.FN,N=self.N,TEL=self.TEL,VERSION=self.VERSION)
    def toFileString(self):
        str = ""
        start = "BEGIN:VCARD"
        str = start+"\n"
        str = str+"VERSION:"+self.VERSION+"\n"
        str = str+"FN:"+self.FN+"\n"
        str = str+"N:"+self.N+"\n"
        str = str+"TEL;"+self.TEL[0:-1]+"\n"
        str = str+"END:VCARD\r\n"
        return str

    def equalTo(self,card):
        if(self.N==card['N'] and self.FN==card['FN'] and self.TEL==card['TEL'] and self.VERSION==card['VERSION']):
        # if(self.N==card.N and self.FN==card.FN and self.TEL==card.TEL and self.VERSION==card.VERSION):
            return True
        else:
            return False
def cardParse(cardstr):
    c = CardClass()
    lines = cardstr.split("\n")
    for line in lines:
        if line:
            if line.startswith("N:"):
                c.N = line[2:]
                continue
            if line.startswith("FN:"):
                c.FN = line[3:]
                continue
            if line.startswith("TEL;"):
                c.TEL += line[4:] + ","
                continue
            if line.startswith("VERSION:"):
                c.VERSION = str(line[8:])
    return c

def getContactArray(f):
    contactArray = []
    linecount = 0
    cardcount = 0
    cardstr = ""
    while True:
        line = f.readline()
        if line:
            #utf8解码
            if line[:3] == codecs.BOM_UTF8:
                line = line[3:]
            line = line.decode("utf-8")
            if line.startswith("BEGIN:VCARD"):
                cardstr = ""
            else:
                if line.startswith("END:VCARD"):
                    card = cardParse(cardstr)
                    contactArray.append(card)
                    cardcount += 1
                    cardstr = ""
                else:
                    line = line.replace("\r", "")
                    line = line.replace("\n", "")
                    cardstr = cardstr + line + "\n"
            linecount += 1
        else:
            break
    f.close()
    logging.error("analysis ok, " + str(cardcount) + " records")
    return contactArray
def write2VcfFile(array,target_path):
    f = open(target_path,'wt')
    for item in array:
        str = ""
        start = "BEGIN:VCARD"
        str = start+"\n"
        str = str+"VERSION:"+item['VERSION']+"\n"
        str = str+"FN:"+item['FN']+"\n"
        str = str+"N:"+item['N']+"\n"
        str = str+"TEL;"+item['TEL'][0:-1]+"\n"
        str = str+"END:VCARD\r\n"
        f.write(str)
    f.close()
# +++20151201 解析短信获取最新内容 op_type 0 为累加，1为覆盖
def analysis_sms(uid,old_array,new_path,op_type):
    if op_type==1:
        logging.error("用户选项为覆盖，清空数据库中存储的短信")
        backup_user_db.del_sms(uid)
        old_array = []
    logging.error("开始解析%s短信内容"%(uid,))
    new_conn = sqlite3.connect(new_path)
    new_cursor = new_conn.cursor()
    new_cursor.execute("select * from SMS;")
    count = 0
    # 遍历新短信，将旧短信中未存在的插入到总表中
    for item in new_cursor:
        count+=1
        logging.error("第"+str(count)+"条短信，"+"date:"+item[-1])
        exist = backup_user_db.get_sms_by_date(uid,item[-1])
        logging.error("查找结果"+str(exist))
        if(exist==None):
            logging.error("未查找到该短信，存入数据库")
            backup_user_db.save_sms(uid,item)

    logging.error("新短信的数量为:"+str(count))
    logging.error("旧短信的数量为:"+str(len(old_array))+"条")
    not_exist_sms_array = []

    # 查找旧短信在新短信中不存在的
    for old_item in old_array:
        find_result = find_date(old_item["date"],new_cursor)
        if len(find_result)==0:
            logging.error("sqlite中不存在短信，开始向其中插入短信")
            not_exist_sms_array.append(old_item)
        else:
            continue

    #将找到的不重复的短信插入到新表中
    # 这里的_id和mongo的物理地址有冲突，需要调解一下
    for not_exist_sms in not_exist_sms_array:
        new_cursor.execute("insert into SMS (_id, type, read, address, body, date) "
                               "values (?, ?, ?, ?, ?, ?)",
                            ((not_exist_sms['obj_id'],not_exist_sms['type'],not_exist_sms['read'],
                                not_exist_sms['address'],not_exist_sms['body'],not_exist_sms['date'])))

    new_conn.commit()
    logging.error("向sqlite中插入短信成功，共插入"+str(len(not_exist_sms_array))+"条短信")
    new_cursor.close()

def find_date(date,cursor):
    cursor.execute("select * from SMS where date=?",(date,))
    array = []
    for item in cursor:
        array.append(item)
    return array

#数据恢复
class GetDevData:
    def GET(self):
        """
        input:
            uid: phonenumber
            filename: backupdata name 压缩包
            backuptime: 备份时间 (int)
        output:
            rt: error code
            PATH: [filepath,filemd5]
        """
        rt = ecode.FAILED
        PATH=[]

        try:
            i = ws_io.ws_input(['uid','filename','backuptime'])
            if not i:
                raise ecode.WS_INPUT

            if not backup_user_db.get_dev(i['uid']):
                raise ecode.NOT_LOGIN
            
            #生成校验值 md5
            phonenumber=i['uid']
            backup_home='/home/wcloud/opt/org/backup'
            back_host=config.get('redis_host')   #远程主机
            file_backup=os.path.join(backup_home,phonenumber,i['backuptime'],i['filename'])
            rt_md5=commands.getstatusoutput('ssh '+back_host+' "md5sum -b %s"'%(file_backup))
            if rt_md5[0]!=0:
                raise ecode.FAILED
            file_md5=rt_md5[1][0:32]
            
            #生成下载路径
            download_path=os.path.join(phonenumber,i['backuptime'],i['filename'])
            PATH=[download_path,file_md5]

            rt = ecode.OK
            error_info = ""
        except Exception as e:
            rt = (type(e)==type(ecode.OK)) and e or ecode.FAILED
            logging.error('Get backup data')
            error_info = str(traceback.format_exc()).replace("\n"," ")

        return ws_io.ws_output(dict(rt=rt.eid,PATH=PATH),error_info)
