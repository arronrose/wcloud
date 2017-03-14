# -*- coding: utf8 -*-
#!/usr/bin/env python


import sys
import commands
import re
import zipfile
import base64
import os
import logging
from xml.dom.minidom import parse
import xml.dom.minidom

aapt_cmd = '/home/wcloud/android/aapt'

def get_apk_info( apk ):
    apkinfo = {
            'app_id':'',
            'app_name':'',
            'version':'',
            'icon':'',
            'versionCode':''
            }

    rt = commands.getstatusoutput( '%s d badging "%s"'%(aapt_cmd, apk))
    logging.error('get apk info by aapt, rt=%d, output=%s', rt[0], rt[1])
    if not rt[0]:
        logging.error('get apk info by aapt, rt=%d, output=%s', rt[0], rt[1])
    rt = rt[1]

    m = re.findall( r"^package: name='(?P<app_id>\S*)'", rt, re.M|re.S)
    if m:
        apkinfo['app_id'] = m[0]

    m = re.findall( r"^package:[^\n]*versionName='(?P<version>\S*)'", rt, re.M|re.S)
    if m:
        apkinfo['version'] = m[0]

    m = re.findall( r"^package:[^\n]*versionCode='(?P<versionCode>\S*)'", rt, re.M|re.S)
    if m:
        apkinfo['versionCode'] = m[0]

#     m = re.findall( r"^locales:\s'[^\n]*'\s'(?P<locales>\S*)'", rt, re.M|re.S)
#     if m:
    m = re.findall( r"^application: label='(?P<app_name>\S*)'"
                , rt, re.M|re.S)
    if m:
        apkinfo['app_name'] = m[0]

    if not apkinfo['app_name']:
        m = re.findall( r"^application-label:'(?P<app_name>[^\n]*)'", rt, re.M|re.S)
        if m:
            apkinfo['app_name'] = m[0]

    m = re.findall( r"^application: \S*\s*icon='(?P<icon_path>[^\n]*)'", rt, re.M|re.S)
    if m:
        with zipfile.ZipFile(apk,'r') as apk_file:
            apkinfo['icon'] = base64.standard_b64encode(apk_file.read(m[0]))

    logging.error(' apkinfo%s', apkinfo)

    return apkinfo


def get_sop_info(sop):
    # 20160822加入获取元心科技应用信息的方法
    sopinfo = {
            'app_id':'',
            'app_name':'',
            'version':'',
            'icon':'',
            'versionCode':''
            }
    # 首先创建一个应用唯一的文件夹装临时文件
    sop_temp_file = sop[0:-4]
    commands.getstatusoutput('mkdir %s'%(sop_temp_file,))
    commands.getstatusoutput('tar zxvf %s -C %s'%(sop,sop_temp_file))
    # 使用minidom解析器打开 XML 文档
    DOMTree = xml.dom.minidom.parse(sop_temp_file+"/sopconfig.xml")
    collection = DOMTree.documentElement
    if collection.hasAttribute("syberos:sopid"):
        sopinfo["app_id"] = collection.getAttribute("syberos:sopid")
    if collection.hasAttribute("syberos:versionCode"):
        sopinfo["versionCode"] = collection.getAttribute("syberos:versionCode")
    if collection.hasAttribute("syberos:versionName"):
        sopinfo["version"] = collection.getAttribute("syberos:versionName")

    app = collection.getElementsByTagName("application")[0]
    if app.hasAttribute("syberos:name"):
        sopinfo["app_name"] = app.getAttribute("syberos:name")
    if app.hasAttribute("syberos:icon"):
        sopinfo["icon"] = app.getAttribute("syberos:icon")

    logging.error(' apkinfo%s', sopinfo)
    commands.getstatusoutput('rm -rf %s'%(sop_temp_file,))
    return sopinfo
