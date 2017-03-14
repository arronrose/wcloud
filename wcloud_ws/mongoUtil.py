__author__ = 'gcynewstart'
# -*- coding: utf8 -*-
#!/usr/bin/env python

from pymongo import MongoClient
import config


# type:client type "single" for one mongo server；"multiple" for more
def getClient():
    client = None
    mongo_host = config.get("mongo_host")
    if mongo_host.split("/")[0]=="repset":
        mongo_type = "mutiple"
    else:
        mongo_type = "single"

    if mongo_type=="single":
        client = MongoClient(config.get('mongo_host'), config.get('mongo_port'),w=0)
    elif mongo_type=="mutiple":
        replset=config.get("mongo_host").split("/")
        reptype=replset[0]
        master=replset[1]
        slave=replset[2]
        mport=str(config.get('mongo_port'))
        mongoUrl="mongodb://"+master+":"+mport+","+slave+":"+mport+"/?replicaSet="+reptype
        client = MongoClient(mongoUrl,w=0)
    return client

