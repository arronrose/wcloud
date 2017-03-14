__author__ = 'arron_rose'
# -*- coding: utf8 -*-

import xlwt
from pymongo import MongoClient

if __name__ == '__main__':
    mongo_host = "192.168.1.15"
    mongo_port = 27017
    client = MongoClient(mongo_host,mongo_port)
    db = client["wcloud_o"]
    users = db["log"]

    #创建workbook和sheet对象
    workbook = xlwt.Workbook() #注意Workbook的开头W要大写
    sheet1 = workbook.add_sheet('sheet1',cell_overwrite_ok=True)

    xingming = unicode('姓名', "utf-8")
    # shoujihao = unicode('手机号', "utf-8")
    # shebeihao = unicode('IMEI号', "utf-8")
    # group1 = unicode('第一群组', "utf-8")
    # group2 = unicode('第二群组', "utf-8")
    # group3 = unicode('第三群组', "utf-8")

    #向sheet页中写入数据
    sheet1.write(0,0,xingming)
    # sheet1.write(0,1,shoujihao)
    # sheet1.write(0,2,shebeihao)
    # sheet1.write(0,3,group1)
    # sheet1.write(0,4,group2)
    # sheet1.write(0,5,group3)

    user_list = users.find()
    row = 1
    for item in user_list:
        # username = item['username']
        uid = item['uid']
        # devs = item['devs']
        # oudn = item['oudn']
        # length = len(oudn.split(","))
        # # sheet1.write(row,0,username)
        sheet1.write(row,1,uid)
        # sheet1.write(row,2,devs)

        # if length == 3 :
        #     ou1 = oudn.split(",")[-3].split("=")[1]
        #     sheet1.write(row,3,ou1)
        # elif length == 4 :
        #     ou1 = oudn.split(",")[-3].split("=")[1]
        #     ou2 = oudn.split(",")[-4].split("=")[1]
        #     sheet1.write(row,3,ou1)
        #     sheet1.write(row,4,ou2)
        # elif length == 5 :
        #     ou1 = oudn.split(",")[-3].split("=")[1]
        #     ou2 = oudn.split(",")[-4].split("=")[1]
        #     ou3 = oudn.split(",")[-5].split("=")[1]
        #     sheet1.write(row,3,ou1)
        #     sheet1.write(row,4,ou2)
        #     sheet1.write(row,5,ou3)

        row = row + 1

    #保存该excel文件,有同名文件时直接覆盖
    workbook.save('gaojiawei_actual.xls')
    print '创建excel文件完成！'