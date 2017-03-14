# -*- coding: utf8 -*-
#!/usr/bin/env python

import jpype
import os
import logging
import re
import time

# def test():
#     jvmPath = jpype.getDefaultJVMPath()
#     #jvmPath="/usr/lib/jvm/jre/lib/amd64/server/libjvm.so"
#     logging.error('jvm path is: %s',jvmPath)
#     jpype.startJVM(jvmPath)
#     jpype.java.lang.System.out.println("hello world!")
#     jpype.shutdownJVM()
#     return True

def send_sms(phoneNumber,smsData):
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
            #get args
            systemtype=KSystemType.EUserManageSystem
            smsgateway="122.13.138.180"   #gate ip
            smsgate=IPV4Util.ipToInt(smsgateway)
            smsport=int(10320)
            # logging.error("three init arg is : %s , %s and %s , and ip is : %s",systemtype,smsgate,smsport,smsgateway)
            #create the Java class
            SMSManager = jpype.JClass("com.cisi.client.midware.SMSManager")
            smsmanager=SMSManager()
            if not smsmanager.Init(systemtype,smsgate,smsport):
                logging.error('init result is: %s,time is %s',smsmanager.Init(systemtype,smsgate,smsport),time.time())
                raise
            logging.error('init succeed!')
            #发送短信
            if not check_pnumber(phoneNumber):
                print "wrong number"

            #String to Bytes
#             pnumber=phoneNumber
#             smsdata1=smsData.encode("UnicodeBigUnmarked")
#             smsdata=bytes(smsdata1)
            #+++ 20150721 增加特殊短信头
#             smsdata=str(bytearray([0xa,0xa])+bytearray(smsdata))
#             sendresult=smsmanager.SendSMS(0,0,pnumber,smsdata)
            print "开始发送短信的时间"+str(time.time())
            sendresult=smsmanager.SendOtherSMS(phoneNumber,smsData)
            logging.error('sms is sended!phoneNumber is %s,the result is %s,time is %s',phoneNumber,sendresult,time.time())
            #+++   20150612
            if sendresult==-6030:
                return False
            return True
    except Exception,ex:
        logging.error('send_sms. ex:%s', ex)
        return False

def send_sms2(phoneNumber,smsData):
    #获取jar包存放路径
    jarpath="./release/"
    #jvm路径
    #jvmpath=jpype.getDefaultJVMPath()
    jvmpath="/usr/lib/jvm//jre/lib/amd64/server/libjvm.so"
    #待使用jar包文件
    jarFile='SMSGatewayMidwarezxc.jar'

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
            logging.error('jvm is start!')
            Sender=jpype.JClass("com.cisi.SendSms.Sender")
            #发送短信
            if not check_pnumber(phoneNumber):
                raise ecode.ERROR_PNUMBER

            #args
            smsgateway=config.get('smsgate_host')
            logging.error("gate ip is : %s",smsgateway)
            pnumber=phoneNumber
            smsdata=smsData.decode().encode("UnicodeBigUnmarked")
            smsgate=smsgateway
            sender=Sender()
            #test
            logging.error('type of smsdata is %s',type(smsdata))
            #send sms
            sendresult=sender.send(pnumber,smsdata,smsgate)
            logging.error('sms is sended! the result is %s',sendresult)
            #+++   20150612
#             if sendresult!=0:
#                 return False
            return True
    except jpype.JavaException,ex:
        logging.error('send_sms. ex:%s', ex)
    return False

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

send_sms("13261539852","pythontest")
