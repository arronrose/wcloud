# -*- coding: utf8 -*-
#!/usr/bin/env python

import logging
import jpype
# import config

import re
import Queue
import threading
# import random
import time

queue = Queue.Queue()
SUCCESS_CODE = -6010
FAIL_CODE = -6030
mutex=threading.Lock()
write=threading.Lock()

def startThread():
    smsm = SMSModule()
    smsm.start()


def enque(arg):
    global write,queue
    write.acquire()
    queue.put(arg)
    write.release()



def check_pnumber(pnumber):
        pn_compile = re.compile(r'1\d{10}')
        if len(pnumber) != 11:
            return False
        if not pn_compile.match(pnumber):
            return False
        return True

class SMSModule(threading.Thread):
    instance = None
    smsmanager = None
    # __queue = Queue.Queue()
    __lock = threading.Lock()

    def __init__(self):
        threading.Thread.__init__(self)
        self.init()
        print("__init__"+str(self.smsmanager))
        print(self)


    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.__lock.acquire()
            if cls.instance is None:
                cls.instance = object.__new__(cls)
                # cls.instance.smsmanager = init()
            cls.__lock.release()
        return cls.instance

    def init(self):
        jarpath="./release/"
        #jvm路径
        jvmpath=jpype.getDefaultJVMPath()
        # jvmpath="/usr/lib/jvm//jre/lib/amd64/server/libjvm.so"
        #待使用jar包文件
        jarFile='SMSGatewayMidwarezxc.jar'
        # smsmanager = None
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
                # if not jpype.isThreadAttachedToJVM():
                #     jpype.attachThreadToJVM()
                # +++20150915 必须加入这个方法才能在jpype环境下使用多线程
                logging.error('jvm is start!%s',time.time())
                #get ipv4 and type
                IPV4Util = jpype.JClass("com.cisi.TWBase.IPV4Util")
                KSystemType = jpype.JClass("com.cisi.TWBase.KSystemType")
                logging.error('get ipv4 and type%s',time.time())
                #get args
                systemtype=KSystemType.EUserManageSystem
                # smsgateway=config.get('smsgate_host')   #gate ip
                smsgateway="122.13.138.180"
                smsgate=IPV4Util.ipToInt(smsgateway)
                smsport=int(10320)
                logging.error('smsport%s',time.time())

                #create the Java class
                SMSManager = jpype.JClass("com.cisi.client.midware.SMSManager")
                logging.error('SMSManager%s',time.time())
                smsmanager=SMSManager()
                initResult = smsmanager.Init(systemtype,smsgate,smsport)
                if not initResult:
                    logging.error('init result is: %s,time is %s',initResult,time.time())
                    raise
                logging.error('init succeed!')
                logging.error(str(smsmanager))
                self.smsmanager = smsmanager
                logging.error(str(self.smsmanager))
                # smsmanager = jpype.JClass("ucas.gcy.sendMessage")
        except Exception as e:
            print e.message
            self.smsmanager = None


    def send(self,phoneNumber,smsData):
        # print(SMSModule.instance.smsmanager)
        # sendresult = SUCCESS_CODE
        print("sending")
        print(self)
        print(self.name)
        print(phoneNumber)
        print(smsData)
        sendresult=self.smsmanager.SendOtherSMS(phoneNumber,smsData)
        print("send success")
        return sendresult

    def fetch(self):
        """
            从队列中获取发送任务
        """
        global queue,mutex
        mutex.acquire()
        if queue.qsize()>0:
            task = queue.get()
        else:
            task = None
        mutex.release()
        return task

    def run(self):
        while True:
            item = self.fetch()
            if item:
                print item
                print "phone"+item[0]
                print "sms"+item[1]
                if check_pnumber(item[0]):
                    sendresult = self.smsmanager.SendOtherSMS(item[0],item[1])
                    if sendresult == SUCCESS_CODE:
                        logging.error("phone %s,sms sent succeed",item[0])
                        # print("phone %s,sms sent succeed",item[0])
                    else:
                        # print("phone %s,sms sent failed",item[0])
                        logging.error("phone %s,sms sent failed",item[0])
                else:
                    # print("phone %s,sms sent failed",item[0])
                    logging.error("%s phone error,send failed",item[0])






