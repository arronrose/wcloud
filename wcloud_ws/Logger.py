#!/usr/bin/env python
# -*- coding: utf8 -*-

import time
import json
import logging
import urllib2
import re
import socket
import fcntl
import struct

def get_inet_ip():
    """
    Returns the actual ip of the local machine.
    This code figures out what source address would be used if some traffic
    were to be sent out to some well known address on the Internet. In this
    case, a Google DNS server is used, but the specific address does not
    matter much.  No traffic is actually sent.
    """
    try:
        csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        csock.connect(('8.8.8.8', 80))
        (addr, port) = csock.getsockname()
        csock.close()
        return addr
    except Exception as e:
        return "127.0.0.1"

def get_netcard_addr(ifname):
    """
    获取指定网卡的地址
    :param card: 网卡名称
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15]))[20:24])


def get_internet_ip(self):
    try:
        myip = __visit("http://www.whereismyip.com/")
    except:
        try:
            myip = self.visit("http://www.ip138.com/ip2city.asp")
        except:
            myip = "So sorry!!!"
    return myip


def __visit(url):
        opener = urllib2.urlopen(url)
        if url == opener.geturl():
            str = opener.read()
        return re.search('\d+\.\d+\.\d+\.\d+',str).group(0)


def __storage_to_json(input):
    return input[9:-1]


def get_public_ip():
    return get_netcard_addr("eth0")


def get_formated_time():
    # t = time.localtime(time.time())
    # timeStr = time.strftime('[%Y-%m-%d %H:%M:%S]', t)
    timeStr = "%.0f"%(time.time())
    return timeStr

class Logger:
    __logtype = ""
    __time = ""
    __src_ip = ""
    __server_ip = ""
    __request = ""
    __input = ""
    __output = ""
    __error = ""

    def set_logtype(self,logType):
        self.__logtype = logType

    def set_time(self,time):
        self.__time = time

    def set_src_ip(self,src_ip):
        self.__src_ip = src_ip

    def set_server_ip(self,server_ip):
        self.__server_ip = server_ip

    def set_request(self,request):
        self.__request = request

    def set_input(self,input):
        self.__input = input

    def set_output(self,output):
        self.__output = output

    def set_error(self,error):
        self.__error = error

    def log_json(self):
        return json.dumps(dict(logtype=self.__logtype,time=self.__time,src_ip=self.__src_ip,
                               server_ip=self.__server_ip,request=self.__request,input=self.__input,
                               output=self.__output,error=self.__error))

    def debug_log_json(self):
        return json.dumps(dict(logtype=self.__logtype,time=self.__time,
                               server_ip=self.__server_ip,output=self.__output))   #调试输出

    def log_str(self):
        return self.__logtype+"|"+self.__time+"|"+self.__src_ip+"|"+self.__server_ip+"|"+\
               self.__request+"|"+self.__input+"|"+self.__output+"|"+self.__error

    def debug_log_str(self):
        return self.__logtype+"|"+self.__time+"|"+self.__src_ip+"|"+self.__server_ip+"|"+\
               self.__request+"|"+self.__output+"|"+self.__error


def make_sys_log(web,output,error):
    logger = Logger()
    logger.set_logtype("WARNING")
    logger.set_time(get_formated_time())
    logger.set_src_ip(web.ctx.ip)
    logger.set_server_ip(get_public_ip())
    logger.set_request(web.ctx.method+" "+web.ctx.path)
    logger.set_input(__storage_to_json(str(web.input())))
    logger.set_output(output)
    logger.set_error(error)
    print logger.log_str()


def make_error_log(web,output,error):
    logger = Logger()
    logger.set_logtype("ERROR")
    logger.set_time(get_formated_time())
    logger.set_src_ip(web.ctx.ip)
    logger.set_server_ip(get_public_ip())
    logger.set_request(web.ctx.method+" "+web.ctx.path)
    logger.set_input(__storage_to_json(str(web.input())))
    logger.set_output(output)
    logger.set_error(error)
    print logger.log_str()



logging.basicConfig(level=logging.DEBUG,
                format='DEBUG|%(created).0f|'+
                       get_public_ip()+'|%(filename)s[line:%(lineno)d]|%(message)s')

# logging.disable(logging.ERROR)

def make_debug_log(web,output):
    """
    这个需要升级一下，能够自动检测接口调用方
    :param src_ip:
    :param server_ip:
    :param request:
    :param output:
    :return:
    """
    logger = Logger()
    logger.set_logtype("DEBUG")
    logger.set_time(str(int(time.time())))
    logger.set_src_ip(web.ctx.ip)
    logger.set_server_ip(get_public_ip())
    logger.set_request(web.ctx.method+" "+web.ctx.path)
    logger.set_output(output)
    print logger.debug_log_str()

def make_log(web,output,error):
    if(error==""):
        make_sys_log(web,str(output),error)
    else:
        make_error_log(web,str(output),error)
