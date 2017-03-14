__author__ = 'arron_rose'
# -*- coding:utf8 -*-
import pymongo
import mongoUtil
if __name__=="__main__":
    client = mongoUtil.getClient()
    db = client["wcloud_o"]
    # ads = db["base_station"]
    # ads.insert({'bstype':"base_station",
    #             'dev_id':"1",
    #             'status':"open",
    #             'institute':"中科院信工所",
    #             'standard':"CDMA",
    #             'power':"12",
    #             'radius':"1000",
    #             'position':"益园西门",
    #             'lasttime':"2016-12-05 19:00:00",
    #             'remark':"这是益园"
    #             })

    db.creatCollection("wjz")
    db.creatCollection("jcm")