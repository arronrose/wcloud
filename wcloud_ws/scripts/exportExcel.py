#-*- coding: utf8 -*-
__author__ = 'gcynewstart'


import xlwt

import getDataFromServer


# 将用户数据写入到内存中，生成表格
def generateExcel(users):
    memFile=xlwt.Workbook(encoding='utf-8',style_compression=0)
    #添加一个sheet，命名为log
    sheet=memFile.add_sheet('log',cell_overwrite_ok=True)
    #写入excel（中文需要编码）
    sheet.write(0,0,'手机号码')
    sheet.write(0,1,'IMEI值')
    sheet.write(0,2,'所在部门')
    sheet.write(0,3,'责任人')
    sheet.write(0,4,'职称')
    sheet.write(0,5,'EMAIL')
    count = 1
    for user in users:
        sheet.write(count,0,user['phone'])
        sheet.write(count,1,user['IMEI'])
        sheet.write(count,2,user['department'])
        sheet.write(count,3,user['name'])
        sheet.write(count,4,user['title'])
        sheet.write(count,5,user['mail'])
        count = count+1
    print("构造表完成！")
    return memFile

# 将内存中的表格数据写入到文件中,path包含文件名
def write2File(memFile,path):
    memFile.save(path)
    print("写入表结束！")

# path = raw_input("请输入访问的web接口路径(http://ip:port/)：")
path = "http://122.13.138.131:8082"
users = getDataFromServer.getUserData(path)
memFile = generateExcel(users)
write2File(memFile,"users.xls")





