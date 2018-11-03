# -*- coding:utf-8 -*-  
import datetime
import redis

# set db=1 , if db=0 have data.
r = redis.Redis(host="localhost", port=6379, db=0)
botUsername = ""
botPassword = ""
workers = 20
aistart = datetime.datetime(2018,5,20,0,0,0).strftime("%Y-%m-%dT%H:%M:%SZ")
