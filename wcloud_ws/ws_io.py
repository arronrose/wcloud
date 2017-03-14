# -*- coding: utf8 -*-

# process web input and output 

import web
import json
import urlparse
import logging
import config
import string
import cert_db
import ecode
import session_db
import base64
from ctypes import *
import ctypes
#+++ 20150504
from pyDes import *

import Logger

def ws_input(want_list):
    i = web.input()
    for w in want_list:
        if not i.has_key(w):
            logging.error('web input error,need key:%s,raw input:%s',w,web.input())
            return None

    return i




def ws_output(outmap,error_info):
    # if config.get('is_debug'):
    #     logging.warn( 'DEBUG.req:%s %s %s',web.ctx.ip, web.ctx.method, web.ctx.path)
        # logging.warn( 'DEBUG.input:%s', web.input())
        # logging.warn( 'DEBUG.output:%s', outmap)
    Logger.make_log(web,json.dumps(outmap),error_info)

    web.header('Content-Type', 'application/json')
    try:
        return json.dumps(outmap)
    except Exception,ex:
        logging.error('json dumps failed. ex:%s', ex)
        return ''
# def ws_output( outmap ):
#     if config.get('is_debug'):
#         logging.warn( 'DEBUG.req:%s %s %s',web.ctx.ip, web.ctx.method, web.ctx.path)
#         logging.warn( 'DEBUG.input:%s', web.input())
#         logging.warn( 'DEBUG.output:%s', outmap)
#
#     web.header('Content-Type', 'application/json')
#     try:
#         return json.dumps(outmap)
#     except Exception,ex:
#         logging.error('json dumps failed. ex:%s', ex)
#         return ''

def cws_input(want_list):
    """
        现在客户端的加密方式是除了sid不加密，其余字段全部加密
    """
    i = web.input()
    
    #按照want_list对key对应的密文进行解密
    
    if i.has_key('cryptograph'):
        value,length = decrypt_c(i['sid'],i['cryptograph'])
        logging.error("decode result:%s",value)
        
        #实现将sid键值对加入value
        st=json.loads(value)
        st["sid"]=i["sid"]
        logging.warn("cryptograph&sid input:%s",st)
        i=st
        
        if len(value)!=length:
            raise ecode.DECRYPT_DATA_LOSS
     
    for w in want_list:
        if not i.has_key(w):
            logging.error('web input error,need key:%s,raw input:%s',w,web.input())
            return None
        
#         return value
    
    return i

def decrypt_c( sid, cryptograph):
    """
        传入参数是一个密文字符串，是解密过程的一个抽象
    """
    
    #进行解密操作时要调用数据库中的方法来获取所需的参数
    """
    bEncryptedData, 密文串的数据
    uiEncryptedDataLen,密文串数据的长度
    derCert, 证书数据,这一项要求客户端在密文的外层还要加入客户端的dev_id，就是申请证书时的身份
    derCertLen, 证书数据的长度
    keyIndex,服务器证书的密钥号
    bOutData, 解密后的明文数据
    uiOutDataLen解密后的明文数据长度
    """
    #初始化解密模块
    so = cdll.LoadLibrary("./release/libDevoceControl.so")
    so._Z26InitDeviceControlInterfacev.argtypes = []
    so._Z26InitDeviceControlInterfacev.restype = c_int
    rt = so._Z26InitDeviceControlInterfacev()
    logging.error("init return:%d",rt)
    
    if rt:
        raise ecode.INIT_ENCRYPT_ERROR
    #声明参数类型
    so._Z20instructDecrpRequestPhjS_jiS_Pj.argtypes = [c_char_p,c_uint,c_char_p,c_uint,c_int,c_char_p,c_void_p]
    so._Z20instructDecrpRequestPhjS_jiS_Pj.restype = c_int
    
    bEncryptedData = cryptograph
    logging.error("cryptograph:%s",cryptograph)
    uiEncryptedDataLen = len(bEncryptedData)
    user,dev_id = session_db.user.get_user_and_dev( sid, web.ctx.ip)
#     dev_id = '862769025344539'
    logging.error("device:%s",dev_id)
    derCert = cert_db.get_signcert(dev_id)
    logging.error("signcert:%s",derCert)
    derCertLen = len(derCert)
    keyIndex = 1
    bOutData = create_string_buffer(500)
    #要求这一个要是字典型
    uiOutDataLen = c_uint(0) 
    
    rt = so._Z20instructDecrpRequestPhjS_jiS_Pj(bEncryptedData, uiEncryptedDataLen,
              derCert, derCertLen, keyIndex,bOutData, byref(uiOutDataLen))
    if rt:
        raise ecode.CRYPT_ERROR
    
    #反初始化
    if so._Z30FinalizeDeviceControlInterfacev():
        raise ecode.FINALIZE_ENCRYPT_ERROR
    return bOutData.value,uiOutDataLen.value

def decrypt_sec(sid,cryptograph):
    """
        传入参数是一个密文字符串，是解密过程的一个抽象
    """
    #进行解密操作时要调用数据库中的方法来获取所需的参数
    """
    bEncryptedData, 密文串的数据
    uiEncryptedDataLen,密文串数据的长度
    derCert, 证书数据,这一项要求客户端在密文的外层还要加入客户端的dev_id，就是申请证书时的身份
    derCertLen, 证书数据的长度
    keyIndex,服务器证书的密钥号
    bOutData, 解密后的明文数据
    uiOutDataLen解密后的明文数据长度
    """
    #初始化解密模块
    so = cdll.LoadLibrary("./release/libDevoceControl.so")
    so._Z26InitDeviceControlInterfacev.argtypes = []
    so._Z26InitDeviceControlInterfacev.restype = c_int
    rt = so._Z26InitDeviceControlInterfacev()
    logging.error("init return:%d",rt)
    
    if rt:
        raise ecode.INIT_ENCRYPT_ERROR
    #声明参数类型
    so._Z20instructDecrpRequestPhjS_jiS_Pj.argtypes = [c_char_p,c_uint,c_char_p,c_uint,c_int,c_char_p,c_void_p]
    so._Z20instructDecrpRequestPhjS_jiS_Pj.restype = c_int
    
    user,dev_id = session_db.user.get_user_and_dev( sid, web.ctx.ip)
    logging.error("device:%s",dev_id)
    derCert = cert_db.get_signcert(dev_id)
    logging.error("signcert:%s",derCert)
    derCertLen = len(derCert)
    keyIndex = 1
    logging.error("cryptograph:%s",cryptograph)
    #判断分段解密 +++20150416 397src--(maybe 134)encry
    para=(len(cryptograph)-1)/397   #para=0/1/2...
    OutData=''
    for p in range(para+1):
        #截取134字节字符串加密
        ls=p*397
        rs=(p+1)*397
        bEncryptedData=cryptograph[ls:rs]
        uiEncryptedDataLen = len(bEncryptedData)
        bOutData = create_string_buffer(500)
        #要求这一个要是字典型
        uiOutDataLen = c_uint(0) 
        rt = so._Z20instructDecrpRequestPhjS_jiS_Pj(bEncryptedData, uiEncryptedDataLen,derCert, derCertLen, keyIndex,bOutData, byref(uiOutDataLen))
        if rt:
            raise ecode.CRYPT_ERROR
        OutData=OutData+bOutData.value
    
    #反初始化
    if so._Z30FinalizeDeviceControlInterfacev():
        raise ecode.FINALIZE_ENCRYPT_ERROR
    return OutData,len(OutData)

#+++ 20150504

def decrypt_des(sid,crypt_data):
    user,dev_id = session_db.user.get_user_and_dev( sid, web.ctx.ip)
    logging.error("------------------decrypt_des dev_id:"+dev_id)
    #初始化解密模块
    key=dev_id[-8:].encode("utf-8");
    des_mid=des(key,CBC,"\0\0\0\0\0\0\0\0",pad=None,padmode=PAD_PKCS5)
    if des_mid:
        logging.error("init is ok!")
    #解码
    crypt_b64=base64.b64decode(crypt_data)
    #解密
    outData=des_mid.decrypt(crypt_b64)
    logging.error("------------------decrypt_des outData:"+outData)
    return outData

def ws_input_des(want_list):
    """
            现在客户端的加密方式是除了sid不加密，其余字段全部加密
    """
    i = web.input()
    #按照want_list对key对应的密文进行解密
    if i.has_key('cryptograph'):
        value = decrypt_des(i['sid'],i['cryptograph'])
        logging.error("decode result:%s",value)
        
        #实现将sid键值对加入value
        st=json.loads(value)
        st["sid"]=i["sid"]
        logging.warn("cryptograph&sid input:%s",st)
        i=st
        
    for w in want_list:
        if not i.has_key(w):
            logging.error('web input error,need key:%s,raw input:%s',w,web.input())
            return None
    return i

#+++ 20150504
def encrypt_des(data,dev_id):
    #+++ 20150508 与之前不同的是，dict先转为str才能加密，解密反过程
#     data_to_encrypt=json.dumps(data)
#     data_to_encrypt=str(data)
#     #将数据转换为符合json标准的str对象
#     logging.warn("data dict is:%s",data)
#     logging.warn("data json dump is:%s",json.dumps(data))
    Src1 = str(data)
    Src2 = Src1.replace('u\'','\"')
    data_to_encrypt = Src2.replace('\'','\"')
#     logging.warn("data str before replace is:%s",Src1)
#     logging.warn("data str is:%s",data_to_encrypt)
#     data_to_encrypt=data_to_encrypt.decode("utf-8")
    
    #初始化解密模块
    key=dev_id[-8:].encode("utf-8");
    des_mid=des(key,CBC,"\0\0\0\0\0\0\0\0",pad=None,padmode=PAD_PKCS5)
    if des_mid:
        logging.error("init is ok!")
    #加密
    enData=des_mid.encrypt(data_to_encrypt)
    #编码
    encrypt_b64=base64.b64encode(enData)
    logging.warn("***encry data is : %s",encrypt_b64)
    return encrypt_b64

#+++ 20150625 for ip
def encrypt_des_ip(data,dev_id):
    #+++ 20150508 与之前不同的是，dict先转为str才能加密，解密反过程
    data_to_encrypt=json.dumps(data)
#     data_to_encrypt=str(data)
#     #将数据转换为符合json标准的str对象
#     logging.warn("data dict is:%s",data)
#     logging.warn("data json dump is:%s",json.dumps(data))
#     Src1 = str(data)
#     Src2 = Src1.replace('u\'','\"')
#     data_to_encrypt = Src2.replace('\'','\"')
#     logging.warn("data str before replace is:%s",Src1)
#     logging.warn("data str is:%s",data_to_encrypt)
#     data_to_encrypt=data_to_encrypt.decode("utf-8")
    
    #初始化解密模块
    key=dev_id[-8:].encode("utf-8");
    des_mid=des(key,CBC,"\0\0\0\0\0\0\0\0",pad=None,padmode=PAD_PKCS5)
    if des_mid:
        logging.error("init is ok!")
    #加密
    enData=des_mid.encrypt(data_to_encrypt)
    #编码
    encrypt_b64=base64.b64encode(enData)
    
    return encrypt_b64

def ws_output_des( outmap,dev_id,error_info):
    # if config.get('is_debug'):
    #     logging.warn( 'DEBUG.req:%s %s', web.ctx.method, web.ctx.path)
    #     logging.warn( 'DEBUG.input:%s', web.input())
    #     logging.warn( 'DEBUG.output:%s', outmap)
    Logger.make_log(web,json.dumps(outmap),error_info)
    web.header('Content-Type', 'application/json')
    try:
        bEncryptedData = encrypt_des_ip(outmap,dev_id)
        logging.error('encode output:%s', bEncryptedData)
        return json.dumps({'encryption':bEncryptedData,'len':len(bEncryptedData)})
    except Exception,ex:
        logging.error('ws_output_des. ex:%s', ex)
        return ''

def cws_output( outmap,dev_id):
    
    
    if config.get('is_debug'):
        logging.warn( 'DEBUG.req:%s %s', web.ctx.method, web.ctx.path)
        logging.warn( 'DEBUG.input:%s', web.input())
        logging.warn( 'DEBUG.output:%s', outmap)
    web.header('Content-Type', 'application/json')
    try:
#         dev_id = "862769025344539"
        bEncryptedData,uiEncryptedDataLen = encrypt_c(outmap,dev_id)
        logging.error('encode output:%s', bEncryptedData)
        return json.dumps({'encryption':bEncryptedData,'len':uiEncryptedDataLen})
#         return json.dumps(dict(bEncryptedData=bEncryptedData))
#         return bEncryptedData
    except Exception,ex:
        logging.error('cws_output. ex:%s', ex)
        return ''
    
def encrypt_c(outmap,dev_id):
    #初始化接口
    so = cdll.LoadLibrary("./release/libDevoceControl.so")
    if not so:
        raise ecode.LOAD_LIB_ERROR
    rt = so._Z26InitDeviceControlInterfacev()
    logging.error("encode api init:%d",rt)
    if rt:
        raise ecode.INIT_ENCRYPT_ERROR
    
    #进行解密操作时要调用数据库中的方法来获取所需的参数
    """ 
    Src, 待加密的数据
    uisrcLen,待加密的数据长度
    derCert, 用户加密证书数据,这一项要求客户端在密文的外层还要加入客户端的dev_id，就是申请证书时的身份
    derCertLen, 加密证书数据的长度
    keyIndex,服务器证书的密钥号  默认为5
    bEncryptedData, 加密后的数据
    uiEncryptedDataLen,加密后的数据长度
    """
    
    #声明函数参数类型
    so._Z18instructCrpRequestPhjS_jiS_Pj.argtypes = [c_char_p,c_uint,c_char_p,c_uint,c_int,c_char_p,c_void_p]
    so._Z18instructCrpRequestPhjS_jiS_Pj.restype = c_int
    #将数据转换为符合json标准的str对象
    Src1 = str(outmap)
    Src2 = Src1.replace('u\'','\"')
    Src = Src2.replace('\'','\"')
    logging.error("mingwen(Src):%s",Src)
    logging.error('len_src is %s',len(Src))
    
    uisrcLen = len(Src)
    logging.error("dev_id:%s",dev_id)
    derCert = cert_db.get_cert(dev_id)
    derCertLen = len(derCert)
    logging.error('derCertLen is : %s',derCertLen)
    keyIndex = 1
    bEncryptedData = create_string_buffer(1000)
    uiEncryptedDataLen = c_uint(0)
    #开始加密，获取返回值输出并验证
    encryrt = so._Z18instructCrpRequestPhjS_jiS_Pj(Src,uisrcLen,derCert,derCertLen,keyIndex,bEncryptedData,byref(uiEncryptedDataLen))
    
    if encryrt:
        logging.error("encryrt is : %s",encryrt)
        raise ecode.CRYPT_ERROR
    finart = so._Z30FinalizeDeviceControlInterfacev()
    if finart:
        raise ecode.FINALIZE_ENCRYPT_ERROR
    
    logging.error('encry_data_len is %s,and encry_data is %s',len(bEncryptedData.value),bEncryptedData.value)
    
    return bEncryptedData.value,uiEncryptedDataLen.value

def encrypt_sec(outmap,dev_id):
    #初始化接口
    so = cdll.LoadLibrary("./release/libDevoceControl.so")
    if not so:
        raise ecode.LOAD_LIB_ERROR
    rt = so._Z26InitDeviceControlInterfacev()
    logging.error("encode api init:%d",rt)
    if rt:
        raise ecode.INIT_ENCRYPT_ERROR
    
    #进行解密操作时要调用数据库中的方法来获取所需的参数
    """ 
    Src, 待加密的数据
    uisrcLen,待加密的数据长度
    derCert, 用户加密证书数据,这一项要求客户端在密文的外层还要加入客户端的dev_id，就是申请证书时的身份
    derCertLen, 加密证书数据的长度
    keyIndex,服务器证书的密钥号  默认为5
    bEncryptedData, 加密后的数据
    uiEncryptedDataLen,加密后的数据长度
    """
    
    #声明函数参数类型
    so._Z18instructCrpRequestPhjS_jiS_Pj.argtypes = [c_char_p,c_uint,c_char_p,c_uint,c_int,c_char_p,c_void_p]
    so._Z18instructCrpRequestPhjS_jiS_Pj.restype = c_int
    #将数据转换为符合json标准的str对象
    Src1 = str(outmap)
    Src2 = Src1.replace('u\'','\"')
    Src = Src2.replace('\'','\"')
    logging.error("mingwen(Src):%s",Src)
    logging.error('len_src is %s',len(Src))
    
#     #test
#     Src=''
#     for l in range(300):
#         Src=Src+'r'
#     logging.error('make src len is %s, Src is %s',len(Src),Src)
    
    logging.error("dev_id:%s",dev_id)
    derCert = cert_db.get_cert(dev_id)
    derCertLen = len(derCert)
    keyIndex = 1
    #判断分段加密 +++20150416 134src--397encry
    para=(len(Src)-1)/134   #para=0/1/2...
    EnData=''
    EnDataLen=''
    for p in range(para+1):
        #截取134字节字符串加密
        ls=p*134
        rs=(p+1)*134
        Src_sec=Src[ls:rs]
        uisrcLen = len(Src_sec)
        bEncryptedData = create_string_buffer(1000)
        uiEncryptedDataLen = c_uint(0)
        #开始加密，获取返回值输出并验证
        encryrt = so._Z18instructCrpRequestPhjS_jiS_Pj(Src_sec,uisrcLen,derCert,derCertLen,keyIndex,bEncryptedData,byref(uiEncryptedDataLen))
        if encryrt:
            logging.error("encryrt is : %s",encryrt)
            raise ecode.CRYPT_ERROR
        EnData=EnData+bEncryptedData.value
        EnDataLen=EnDataLen+str(uiEncryptedDataLen.value)+':'
        logging.error("Endata is %s, Endatalen is %s",EnData,EnDataLen)
        
    EncrptedData=EnData
    EncrptedDataLen=EnDataLen.rstrip(":")
        
    finart = so._Z30FinalizeDeviceControlInterfacev()   #是否不需要反初始化
    if finart:
        raise ecode.FINALIZE_ENCRYPT_ERROR
    logging.error('encry_data_len(397) is %s,and encry_data is %s',len(EncrptedData),EncrptedData)
    
    return EncrptedData,EncrptedDataLen

