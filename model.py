# -*- coding:utf-8 -*-  

import datetime
import time
from config import r

def getStarttime():
	return r.get("stime")

def getContinue():
	return r.get('continue')

def getaiContinue():
	return r.get("aicontinue")

def setUTCStarttime():
	shiftts = time.time() - 30*24*60*60
	stime = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(shiftts))
	r.set("stime", stime)
	return stime

def setNonetime():
	r.delete("stime")

def setContinue(cont):
	r.set("continue", cont)

def setaiContinue(acont):
	r.set("aicontinue", acont)

def pushNorefList(imagenames):
	for i in imagenames:
		r.sadd("noreflist", i)

def swapLists():
	r.sinterstore("expirelist", "noreflist")
	r.delete("noreflist")

def getStartflag():
	return r.get("startflag")

def setStartflag(flag):
	r.set("startflag", flag)

def markRemovableImages():
	r.sinterstore("resultset", "noreflist", "expirelist")
	r.incr("counter")
	return list(r.smembers("resultset"))

def getCounter():
	return r.get("counter")

def cleanup():
	r.delete("continue", "aicontinue", "startflag", "stime", "noreflist", "expirelist", "resultset", "counter")