# -*- coding:utf-8 -*-  
import datetime
import redis

cookie = None
r = redis.Redis(host="localhost", port=6379, db=0)
botUsername = "CommonsFileDeletionBot"
botPassword = "d19Cwj&ayHUv$u!E"
workers = 20
aistart = datetime.datetime(2018,5,20,0,0,0).strftime("%Y-%m-%dT%H:%M:%SZ")
