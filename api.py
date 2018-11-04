# -*- coding:utf-8 -*-  
from concurrent import futures
import requests
import config
import model
import json
import time
import datetime
import sys, getopt
reload(sys)
sys.setdefaultencoding('utf-8')

apiroot = "https://commons.moegirl.org/api.php"
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
		req = requests.get(apiroot, params=params, cookies = config.cookie)
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
	config.cookie = requests.post(apiroot, data=login_params, cookies = req.cookies).cookies

def removeFile(filename):
	try:
		print(filename)
		csrf_params = {"action": "query", "format": "json", "meta": "tokens"}
		csrf = requests.post(apiroot, data=csrf_params, cookies = config.cookie).json()['query']['tokens']['csrftoken']
		del_params={"action": "delete", "title":filename, "format": "json","tags":"Bot","reason":"autoremove unused file","token":csrf}
		req = requests.post(apiroot, data = del_params, cookies = config.cookie)
	except ValueError:
		print("jsondata parse error")
		return False
	except requests.exceptions.SSLError:
		print("connection lost")
		return False
	except Exception as e:
		print(e.value)
		return False

def main():
	searchonly = False
	export = None
	exportonlyflag = False
	deleteflag = None
	opts, args = getopt.getopt(sys.argv[1:], "snde:", ["search", "exportonly", "delete", "export="])
	for op, value in opts:
		if op in ("-s, --search"):
			searchonly = True
		if op in ("-n", "--exportonly"):
			exportonlyflag = True
		if op in ("-d", "delete"):
			deleteflag = True
		if op in ("-e", "--export"):
			export = value
	if model.getStartflag() is None:
		model.setStartflag(1)
	if model.getCounter() is None:
		model.initCounter()
	while True:
		if config.cookie is None:
			botLogin()
		if deleteflag is True:
			if searchonly is True or export is not None or exportonlyflag is True:
				raise AttributeError("You should not use -d flag with other options")
			else:
				removableList = model.getRemovableImages()
				with futures.ThreadPoolExecutor(config.workers) as executor:
					executor.map(removeFile, removableList)
				print("complete")
				break
		if model.getContinue() is None or model.getContinue().decode() == "None":
			model.swapLists()
			model.setNonetime()
			model.setStartflag(1)
		if exportonlyflag is True:
			model.setStartflag(0)
		elif deleteflag is True:
			model.setStartflag(0)
		else:
			model.setStartflag(1)
		startflag = bool(int(model.getStartflag().decode()))
		while startflag is True:
			getNoRefList()
			startflag = bool(int(model.getStartflag().decode()))
		else:
			if exportonlyflag is False:
				removableList = model.markRemovableImages()
			counter = model.getCounter()
			if int(counter) >= 2 and searchonly is False:
				with futures.ThreadPoolExecutor(config.workers) as executor:
					executor.map(removeFile, removableList)
				if export is not None:
					with open(export, "w", encoding="utf-8") as f:
						f.writelines([line.decode()+'\n' for line in removableList])
				model.cleanup()
				print("complete")
				break
			elif int(counter) >= 2 and searchonly is True:
				if export is not None:
					with open(export, "w", encoding="utf-8") as f:
						f.writelines([line.decode()+'\n' for line in removableList])
				model.cleanup()
				print("complete")
				break
			elif exportonlyflag is True and export is not None:
				removableList = model.getRemovableImages()
				with open(export, "w", encoding="utf-8") as f:
					f.writelines([line.decode()+"\n" for line in removableList])
				print("complete")
				break
			elif exportonlyflag is True and export is None:
				raise AttributeError("You must specify a export destiniation")



if __name__ == '__main__':
	main()