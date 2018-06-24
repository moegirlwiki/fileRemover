# -*- coding:utf-8 -*-  
from concurrent import futures
import requests
import config
import model
import json
import time
import datetime

apiroot = "https://commons.moegirl.org/api.php"
cookie = None
def allimages():
	aiend = model.getStarttime() #get the latest timestamp from model
	cont = model.getContinue()
	aicontinue = model.getaiContinue() #get the continueous title from model
	aistart = config.aistart
	params = {}
	if aiend is None or aiend.decode() == "None":
		model.setUTCStarttime()
		aiend = model.getStarttime()
	if aicontinue is None or aicontinue.decode() == "None":
		params = {"action": "query", "aiprop": "canonicaltitle", "format": "json", "list": "allimages",
				 "aisort": "timestamp","aistart":aistart,  "aiend": aiend.decode(), "ailimit": 500 }
	else:
		params = {"action": "query", "aiprop": "canonicaltitle", "format": "json", "list": "allimages",
				 "aisort": "timestamp", "aistart": aistart, "aiend": aiend.decode(), "ailimit": 500,"continue": cont.decode(), "aicontinue": aicontinue.decode()}
	try:
		req = requests.get(apiroot, params=params, cookies = cookie)
		print(req.url)
		jsondata = req.json()
	except ValueError:
		print("jsondata purge error")
		print(req.text)
		return False
	except requests.exceptions.SSLError:
		print("connection lost")
		return False
	except:
		return False
	if req.status_code == 200:
		imagenames=[]
		if 	"continue" in jsondata:
			model.setContinue(jsondata['continue']['continue'])
			model.setaiContinue(jsondata['continue']['aicontinue'])
		else:
			model.setContinue(None)
			model.setaiContinue(None)
			model.setStartflag(0)
			return False
		for image in jsondata['query']['allimages']:
			imagenames.append(image['canonicaltitle'])
			#print(imagenames)
		return imagenames
	else:
		return False

def isNotReffed(imagename):
	params = {"action": "query", "format": "json", "prop":"globalusage", "titles":imagename}
	try:
		req = requests.post(apiroot, data=params)
		jsondata = req.json()
	except ValueError:
		print(req.text)
		print("jsondata purge error")
		return False
	except requests.exceptions.SSLError:
		print("coonection lost")
		return False
	except:
		return False
	key = list(jsondata['query']['pages'].keys())
	globalref = jsondata['query']['pages'][key[0]]['globalusage']
	if globalref == []:
		#return True
		return imagename
	else:
		return False

def isNotCategorized(imagename):
	params = {"action": "query", "format": "json", "prop":"categories", "titles":imagename}
	try:
		req = requests.post(apiroot, data=params)
		jsondata = req.json()
	except ValueError:
		print(req.text)
		print("jsondata purge error")
		return False
	except requests.exceptions.SSLError:
		print("coonection lost")
		return False
	except:
		return False
	key = list(jsondata['query']['pages'].keys())
	try:
		jsondata['query']['pages'][key[0]]['categories']
		return False
	except KeyError:
		return imagename

def getNoRefList():
	imagenames = allimages()
	if imagenames is not False:
		with futures.ThreadPoolExecutor(config.workers) as executor:
			noreflist = list(executor.map(isNotReffed, imagenames))
			nocatlist = list(executor.map(isNotCategorized, imagenames))
			#noreflist = list(filter(isNotReffed, imagenames))
		norefset = set([i for i in noreflist if i is not False])
		nocatset = set([i for i in nocatlist if i is not False])
		model.pushNorefList(norefset & nocatset)

def botLogin():
	token_params = {"action": "query", "meta":"tokens", "type": "login", "format": "json"}
	req = requests.post(apiroot, data=token_params)
	token = req.json()['query']['tokens']['logintoken']
	login_params = {'action': 'login', 'lgname': config.botUsername, 'lgtoken': token, 'lgpassword': config.botPassword, 'format': 'json'}
	cookie = requests.post(apiroot, data=login_params, cookies = req.cookies).cookies

def removeFile(filename):
	try:
		csrf_params = {"action": "query", "format": "json", "meta": "tokens"}
		csrf = requests.post(apiroot, data=csrf_params, cookies = cookie).json()['query']['tokens']['csrftoken']
		del_params={"action": "delete", "title":title, "format": "json","tags":"Bot","reason":"autoremove unused file","token":csrf}
		req = requests.post(apiroot, data = del_params, cookies = cookie)
	except ValueError:
		print("jsondata parse error")
		return False
	except requests.exceptions.SSLError:
		print("connection lost")
		return False
	except:
		return False

def main():
	if model.getStartflag() is None:
		model.setStartflag(1)
	while True:
		if cookie is None:
			botLogin()
		if model.getContinue() is None or model.getContinue().decode() == "None":
			model.swapLists()
			model.setNonetime()
			model.setStartflag(1)
		startflag = bool(int(model.getStartflag().decode()))
		while startflag is True:
			getNoRefList()
			startflag = bool(int(model.getStartflag().decode()))
		else:
			removableList = model.markRemovableImages()
			counter = model.getCounter()
			if int(counter) >= 2:
				with futures.ThreadPoolExecutor(config.workers) as executor:
					executor.map(removeFile, removeableList)
				model.cleanup()
				print("complete")
				break

if __name__ == '__main__':
	main()

	