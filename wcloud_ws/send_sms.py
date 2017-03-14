# -*- coding: utf8 -*-
#!/usr/bin/env python

import jpype
import os
import logging
import ecode
import re
import config
import time

# def test():
#     jvmPath = jpype.getDefaultJVMPath()
#     #jvmPath="/usr/lib/jvm/jre/lib/amd64/server/libjvm.so"
#     logging.error('jvm path is: %s',jvmPath)     
#     jpype.startJVM(jvmPath)      
#     jpype.java.lang.System.out.println("hello world!")      
#     jpype.shutdownJVM()
#     return True
SUCCESS_CODE = 0
FAIL_CODE = -1

def send_sms(phoneNumber,smsData):
    #获取jar包存放路径
    jarpath="./release/"
    #jvm路径
    #jvmpath=jpype.getDefaultJVMPath()
    jvmpath="/usr/lib/jvm//jre/lib/amd64/server/libjvm.so"
    #待使用jar包文件
    jarFile='SendMsgCMPP2.0.jar'
    #jarBase='SMSGatewayMidwareBase.jar'
    try:
        #检测并启动jvm,get init args first
        if not jpype.isJVMStarted():                    #test whether the JVM is started
            logging.error('jvm is not start!')
            jpype.startJVM(jvmpath,"-ea","-Djava.class.path=%s" % (jarpath+jarFile))
            while True:
                if jpype.isJVMStarted():
                    break
            logging.error("jvm has started!")
        if jpype.isJVMStarted():
            # +++20150915 必须加入这个方法才能在jpype环境下使用多线程
            if not jpype.isThreadAttachedToJVM():
                jpype.attachThreadToJVM()
            logging.error('jvm is start!%s',time.time())
            #发送短信
            if not check_pnumber(phoneNumber):
                raise ecode.ERROR_PNUMBER

            Sender = jpype.JClass("ucas.gcy.sendMessage.SendMessage")
            sendresult=Sender.send(phoneNumber,smsData)
            logging.error('sms is sended!phoneNumber is %s,the result is %s,time is %s',phoneNumber,sendresult,time.time())
            # +++20160720 关闭smsmanager连接
            #+++   20150612
            return sendresult == 0
    except Exception,ex:
        logging.error('send_sms. ex:%s', ex)
        return False

def send_sms_last(phoneNumber,smsData):
    #获取jar包存放路径
    jarpath="./release/"
    #jvm路径
    #jvmpath=jpype.getDefaultJVMPath()
    jvmpath="/usr/lib/jvm//jre/lib/amd64/server/libjvm.so"
    #待使用jar包文件
    jarFile='SMSGatewayMidwarezxc.jar'
    #jarBase='SMSGatewayMidwareBase.jar'
      
    try:
        #检测并启动jvm,get init args first
        if not jpype.isJVMStarted():                    #test whether the JVM is started 
            logging.error('jvm is not start!')
            jpype.startJVM(jvmpath,"-ea","-Djava.class.path=%s" % (jarpath+jarFile))
            while True:
                if jpype.isJVMStarted():
                    break
            logging.error("jvm has started!")
        if jpype.isJVMStarted():
            # +++20150915 必须加入这个方法才能在jpype环境下使用多线程
            if not jpype.isThreadAttachedToJVM():
                jpype.attachThreadToJVM()
            logging.error('jvm is start!%s',time.time())
            #get ipv4 and type
            IPV4Util = jpype.JClass("com.cisi.TWBase.IPV4Util")
            KSystemType = jpype.JClass("com.cisi.TWBase.KSystemType")
            logging.error('get ipv4 and type%s',time.time())
            #get args
            systemtype=KSystemType.EUserManageSystem
            smsgateway=config.get('smsgate_host')   #gate ip
            smsgate=IPV4Util.ipToInt(smsgateway)
            smsport=int(10320)
            logging.error('smsport%s',time.time())
            # logging.error("three init arg is : %s , %s and %s , and ip is : %s",systemtype,smsgate,smsport,smsgateway)
            #create the Java class 
            SMSManager = jpype.JClass("com.cisi.client.midware.SMSManager")
            logging.error('SMSManager%s',time.time())
            smsmanager=SMSManager()
            initResult = smsmanager.Init(systemtype,smsgate,smsport)
            if not initResult:
                logging.error('init result is: %s,time is %s',initResult,time.time())
                raise
            logging.error('init succeed!')
            #发送短信
            if not check_pnumber(phoneNumber):
                raise ecode.ERROR_PNUMBER
            
            #String to Bytes
#             pnumber=phoneNumber
#             smsdata1=smsData.encode("UnicodeBigUnmarked")
#             smsdata=bytes(smsdata1)
            #+++ 20150721 增加特殊短信头
#             smsdata=str(bytearray([0xa,0xa])+bytearray(smsdata))
#             sendresult=smsmanager.SendSMS(0,0,pnumber,smsdata)
            logging.error("开始发送短信的时间"+str(time.time()))
            sendresult=smsmanager.SendOtherSMS(phoneNumber,smsData)
            logging.error('sms is sended!phoneNumber is %s,the result is %s,time is %s',phoneNumber,sendresult,time.time())
            # +++20160720 关闭smsmanager连接
            smsmanager.Close()
            #+++   20150612
            if sendresult==-6030:
                return False
            return True
    except Exception,ex:
        logging.error('send_sms. ex:%s', ex)
        return False

def send_notice_sms(phoneNumber,smsData):
    return send_sms(phoneNumber,smsData)

def send_sms_captcha(phoneNumber,smsData):
    return send_sms(phoneNumber,smsData)
        
pn_compile = re.compile(r'1\d{10}')
def check_pnumber(pnumber):
    if len(pnumber) != 11:
        return False
    if not pn_compile.match(pnumber):
        return False
    return True

# +++ 20150902 加入批量发送短信的逻辑，每次重新加载那些东西耗资源也耗时
def batch_send_sms(user_list,smsData):
     #获取jar包存放路径
    jarpath="./release/"
    #jvm路径
    #jvmpath=jpype.getDefaultJVMPath()
    jvmpath="/usr/lib/jvm//jre/lib/amd64/server/libjvm.so"
    #待使用jar包文件
    jarFile='SMSGatewayMidwarezxc.jar'
    #jarBase='SMSGatewayMidwareBase.jar'

    try:
        #检测并启动jvm,get init args first
        if not jpype.isJVMStarted():                    #test whether the JVM is started
            logging.error('jvm is not start!')
            jpype.startJVM(jvmpath,"-ea","-Djava.class.path=%s" % (jarpath+jarFile))
            while True:
                if jpype.isJVMStarted():
                    break
            logging.error("jvm has started!")
        if jpype.isJVMStarted():
            logging.error('jvm is start!time is %s',str(time.time()))
            #get ipv4 and type
            IPV4Util = jpype.JClass("com.cisi.TWBase.IPV4Util")
            KSystemType = jpype.JClass("com.cisi.TWBase.KSystemType")
            #get args
            systemtype=KSystemType.EUserManageSystem
            smsgateway=config.get('smsgate_host')   #gate ip
            smsgate=IPV4Util.ipToInt(smsgateway)
            smsport=int(10320)
            # logging.error("three init arg is : %s , %s and %s , and ip is : %s",systemtype,smsgate,smsport,smsgateway)
            #create the Java class
            SMSManager = jpype.JClass("com.cisi.client.midware.SMSManager")
            smsmanager=SMSManager()
            if not smsmanager.Init(systemtype,smsgate,smsport):
                # logging.error('init result is: %s',smsmanager.Init(systemtype,smsgate,smsport))
                raise
            logging.error('init succeed!time is %s',str(time.time()))

            for phoneNumber in user_list:
                #发送短信
                if not check_pnumber(phoneNumber):
                    logging.error("phone number is not valid,pnumber:%s",phoneNumber)
                logging.error('check number succeed!time is %s',str(time.time()))

                sendresult=smsmanager.SendOtherSMS(phoneNumber,smsData)
                logging.error('sms is sended! the result is %s,time is %s',sendresult,str(time.time()))
                #+++   20150612
                if sendresult==-6030:
                    logging.error("send sms failed,%s",phoneNumber)
    except Exception,ex:
        logging.error('send_sms. ex:%s', ex)
        return False

def send_sms_3(phoneNumber,smsData):
    if not check_pnumber(phoneNumber):
        raise ecode.ERROR_PNUMBER
    else:
        #获取jar包存放路径
        jarpath="./release/"
        #jvm路径
        #jvmpath=jpype.getDefaultJVMPath()
        jvmpath="/usr/lib/jvm//jre/lib/amd64/server/libjvm.so"
        #待使用jar包文件
        jarFile='SendSmsByGcy-http.jar'
        #jarBase='SMSGatewayMidwareBase.jar'

        try:
            #检测并启动jvm,get init args first
            if not jpype.isJVMStarted():                    #test whether the JVM is started
                logging.error('jvm is not start!')
                jpype.startJVM(jvmpath,"-ea","-Djava.class.path=%s" % (jarpath+jarFile))
                while True:
                    if jpype.isJVMStarted():
                        break
                logging.error("jvm has started!")
            if jpype.isJVMStarted():
                # +++20150915 必须加入这个方法才能在jpype环境下使用多线程
                if not jpype.isThreadAttachedToJVM():
                    jpype.attachThreadToJVM()
                logging.error('jvm is start!%s',time.time())
                #get the sender
                Sender = jpype.JClass("www.secphone.org.online.SenderHTTP")
                logging.error('Sender%s',str(time.time()))
                # send sms
                sendresult = Sender.SendSMS(phoneNumber,"ffff"+smsData)
                logging.error('sms is sended!phoneNumber is %s,the result is %s,time is %s',phoneNumber,sendresult,time.time())
                # handle connection
                # Sender.logout()
                #+++   20150612
                if sendresult!="SC:0000":
                    return False
                return True
        except Exception,ex:
            logging.error('send_sms. ex:%s', ex)
            return False

