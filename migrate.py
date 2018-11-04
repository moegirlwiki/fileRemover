# -*- coding:utf-8 -*-  
from config import r
with open('./noreflist.txt', 'r') as f:
	for line in f.readlines():
		r.sadd('resultset', line.strip())