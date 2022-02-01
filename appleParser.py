import os,pathlib,sys,glob,time
from datetime import datetime,timedelta
from hurry.filesize import size
import json
import plistlib,sqlite3,tarfile
from columnar import columnar
import pandas as pd 
from IPython.display import HTML,display
import itertools
import hashlib
from shutil import copyfile
import re
from PIL import Image
import subprocess
#Data used for end report
timestamp = ""
case = ""
foldername = ""
examiner = ""
image_size = ""
extraction_time = ""
md5 = ""
sha256 = ""
check_md5 = ""
check_sha256 = ""

def convert_data(data, file_name):
	with open(file_name, 'wb') as file:
		file.write(data)

def pl_open(file):																	#Opens plist files
	with open(file, 'rb') as fp:
			cp = plistlib.load(fp)
	return cp

def extract(file):
	global extraction_time											#Extracts files from wordlist
	start_time = time.time()
	allowedApps = []
	try:																#Tries to open the default wordlist
		with open('Default_lists/allowedApps.txt') as my_file:	
			for line in my_file:										#Takes words in the wordlist file and creats a list
				allowedApps.append(line[:-1])
	except FileNotFoundError:											#File not found error
		print("allowedApps.txt not found")
		sys.exit()

	tar = tarfile.open(file)												#Opens the provided tar image
	members = tar.getmembers()
	names = tar.getnames()
	
	for name in names:
		if 'applicationState.db' in name:
			index = names.index(name)
			path = pathlib.PurePath(members[index].name)
			members[index].name = os.path.basename(members[index].name)
			tar.extract(members[index], path='./{}'.format(foldername))

	
	
	appPaths = {}

	path = "./{}/applicationState.db".format(foldername)
	
	if not os.path.exists(path):
		print("{} not found.".format(path))
		return

	try:
		connection = sqlite3.connect(path)
		connection.text_factory = str
		cursor = connection.cursor()
		rows = cursor.execute("SELECT application_identifier_tab.application_identifier, kvs.value FROM application_identifier_tab INNER JOIN kvs ON application_identifier_tab.id=kvs.application_identifier WHERE kvs.key=1").fetchall()
		for app in allowedApps:
			for row in rows:
				if app == row[0]:
					p = row[1].find(b'/Data/Application/')
					appPaths[app] = [row[1][p+18:p+19+35].decode("utf-8")]
					appPaths[app].append([])

	except:
		print("Error with {}".format(path))
	
	AppGroup = {'parler':'com.parler.parler','minds.chat':'com.minds.chat','minds.mobile':'com.minds.mobile','safechat':'net.safechat.app','howly':'app.howly.ios','clouthub':'com.clouthub.clouthubapp','gettr':'com.gettr.gettr','mewe':'com.mewe'}
	

	for name in names:
		if 'Shared/AppGroup/' in name and '.com.apple.mobile_container_manager.metadata.plist' in name:
			index = names.index(name)
			if members[index].isreg():
				path = pathlib.PurePath(members[index].name)
				members[index].name = os.path.basename(members[index].name)
				tar.extract(members[index],'./{}/Test/'.format(foldername))
				f = pl_open('./{}/Test/.com.apple.mobile_container_manager.metadata.plist'.format(foldername))
				for i in list(AppGroup.keys()):
					if i in f['MCMMetadataIdentifier']:
						appPaths[AppGroup[i]][1].append(path.parent.name)
	os.remove('./{}/Test/.com.apple.mobile_container_manager.metadata.plist'.format(foldername))
	os.rmdir('./{}/Test/'.format(foldername))
	
	conv = {'com.parler.parler':'Parler','com.minds.chat':'Minds(Chat)','com.minds.mobile':'Minds(Mobile)','net.safechat.app':'SafeChat','app.howly.ios':'2nd1st','com.clouthub.clouthubapp':'CloutHub','com.gettr.gettr':'Gettr','com.mewe':'MeWe'}
	wordlist = {'com.parler.parler':'Parler.txt','com.minds.chat':'Minds_Chat.txt','com.minds.mobile':'Minds_Mobile.txt','net.safechat.app':'SafeChat.txt','app.howly.ios':'1st2nd.txt','com.clouthub.clouthubapp':'Clouthub.txt','com.gettr.gettr':'Gettr.txt','com.mewe':'MeWe.txt'}

	installedApps = list(appPaths.keys())
	selectedApps = installedApps

	
	files = {}
	for a in selectedApps:
		words = []
		try:																#Tries to open the default wordlist
			with open('Default_lists/Apple/{}'.format(wordlist[a])) as my_file:	
				for line in my_file:										#Takes words in the wordlist file and creats a list
					words.append(line[:-1])
		except FileNotFoundError:											#File not found error
			print("{} not found".format(wordlist[a]))
			sys.exit()
		files[a] = words

	for name in names:

		for a in selectedApps:
			for i in appPaths[a][1]:
				for j in range(len(i) and len(i) > 0):
					pp = 'Shared/AppGroup/' + appPaths[a][1][j]
					for word in files[a]:
						if word in name and pp in name:
							index = names.index(name)
							if members[index].isreg():
								path = pathlib.PurePath(members[index].name)
								members[index].name = os.path.basename(members[index].name)
								if path.parent.name in appPaths[a][1][j]:
									tar.extract(members[index],'./{}/{}'.format(foldername,conv[a]))
						

			pp = 'Application/' + appPaths[a][0]
			for word in files[a]:
				if word in name and pp in name:
					index = names.index(name)
					if members[index].isreg():
						path = pathlib.PurePath(members[index].name)
						members[index].name = os.path.basename(members[index].name)
						if path.parent.name in ('/tmp') and any(i in members[index].name for i in ['.jpg','.jpeg','png','mp4','.aac']):
							tar.extract(members[index],'./{}/{}/Tmp'.format(foldername,conv[a]))
						elif path.parent.name in ('/react-native-image-crop-picker') and any(i in members[index].name for i in ['.jpg','.jpeg','.png','mp4']):
							tar.extract(members[index],'./{}/{}/Tmp'.format(foldername,conv[a]))
						elif path.parent.name in ('/default') and any(i in members[index].name for i in ['.jpg','.jpeg','.png','.gif']):
							tar.extract(members[index],'./{}/{}/SDImageCache'.format(foldername,conv[a]))
						elif path.parent.name in ('/fsCachedData'):
							tar.extract(members[index],'./{}/{}/fsCachedData'.format(foldername,conv[a]))
						elif path.parent.name in ('/mediacache'):
							tar.extract(members[index],'./{}/{}/mediacache'.format(foldername,conv[a]))
						elif path.parent.name in ('/.video'):
							tar.extract(members[index],'./{}/{}/.video'.format(foldername,conv[a]))
						elif path.parent.name in ('/.image'):
							tar.extract(members[index],'./{}/{}/.image'.format(foldername,conv[a]))
						elif path.parent.name in ('/flutter-images'):
							tar.extract(members[index],'./{}/{}/flutter-images'.format(foldername,conv[a]))
						elif path.parent.name in ('/libCachedImageData'):
							tar.extract(members[index],'./{}/{}/libCachedImageData'.format(foldername,conv[a]))
						elif path.parent.name in ('/Caches') and any(i in members[index].name for i in ['.jpg','.jpeg','.png','.gif','mp4']):
							tar.extract(members[index],'./{}/{}/Caches'.format(foldername,conv[a]))
						elif members[index].name not in word:
							pass
						else:
							tar.extract(members[index],'./{}/{}'.format(foldername,conv[a]))
	tar.close()
	extraction_time = str(timedelta(seconds=round(time.time() - start_time)))

def sql(path,query):
	if not os.path.exists(path):
		print("{} not found.".format(path))
		return

	try:
		connection = sqlite3.connect(path)
		connection.text_factory = str
		cursor = connection.cursor()
		image = cursor.execute(query).fetchall() 
		return image

	except:
		print("Error with {}".format(path))

def tables(dikt,rows):
	headers = list(dikt.keys())
	data = list(dikt.values())
	tab_row = []
	for i in range(len(data[0])):
		tab_row.append([data[ind][i] for ind in range(rows)])
	tabl = columnar(tab_row, headers)
	return tabl

def prnt(title,f_tables_0,f_tables_1):
		full = bool([a for a in f_tables_0.values() if a != []])
		if full == True:
			print(title)
			print(tables(f_tables_0,f_tables_1))

def parler(prt):
	if os.path.isdir('./{}/Parler'.format(foldername)):
		print("\nParler:\n") if prt == 1 else None

	_USER,_FILES={},{}
	_HASHES = {"Filename":[],"SHA256":[]}

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/Parler/https_parler.com_0.localstorage".format(foldername)
	
	if os.path.isfile(path):
		_HASHES["Filename"].append(os.path.basename(path))
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		rows = sql(path,"SELECT value from ItemTable where key='username';")
		_USER = {}
		try:
			_USER['username'] = [rows[0][0].decode('utf-16le')]
		except:
			_USER['username'] = ["None"]
		
		prnt("https_parler.com_0.localstorage:",_USER,1) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = glob.glob('./{}/Parler/Tmp/*'.format(foldername))

	if os.path.isdir('./{}/Parler/Tmp'.format(foldername)):
		_FILES = {"Filenames":[],"Location":[]}

		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES["Filenames"].append(os.path.basename(i))
			_FILES["Location"].append("."+i[len(foldername)+2:])

		prnt("Tmp:",_FILES,1) if prt == 1 else None

	return [_USER,_FILES,_HASHES]

def mewe(prt):
	if os.path.isdir('./{}/Mewe'.format(foldername)):
		print("\nMeWe:\n") if prt == 1 else None

	_REC,_RES,_FEED,_DM,_FILES1,_FILES2={},{},{},{},{},{}
	_HASHES = {"Filename":[],"SHA256":[]}

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/MeWe/Cache.db".format(foldername)

	if os.path.isfile(path):
		_HASHES["Filename"].append(os.path.basename(path))
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		receiver = sql(path,"SELECT receiver_data from cfurl_cache_receiver_data where receiver_data LIKE '{\"id\"%' ")
		response = sql(path,"select hash_value, request_key, time_stamp from cfurl_cache_response")
		_REC = {'Username':[],'Name':[],'Phone':[]}
		_RES = {'Timestamp':[],'Request Key':[],'Hash Value':[]}

		for i in receiver:
			d = json.loads(i[0].decode())
			if "firstName" in d.keys():
				if d["firstName"] + " " + d["lastName"] not in _REC["Name"]:
					_REC["Name"].append(d["firstName"] + " " + d["lastName"])
					_REC["Username"].append(d["contactInviteId"]) 
					if "primaryPhoneNumber" in d.keys():
						_REC["Phone"].append(d["primaryPhoneNumber"])
					else:
						_REC["Phone"].append("")

		prnt("Receiver:",_REC,3) if prt == 1 else None
		
		for i in response:
			_RES["Timestamp"].append(i[2])
			_RES["Request Key"].append(i[1])
			_RES["Hash Value"].append(i[0])

		prnt("Response:",_RES,3) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/MeWe/sgrouplesdb.sqlite".format(foldername)
	
	if os.path.isfile(path):
		_HASHES["Filename"].append(os.path.basename(path))
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		users = dict(sql(path,"SELECT ZUSERID,ZNAME FROM ZPROFILEDETAILS;"))
		chat = sql(path,"SELECT ZDATE,ZSENDER,ZTEXT from ZCHATMESSAGE;")
		post = sql(path,"SELECT ZPOSTID as 'Post_ID' ,ZCREATIONDATE as 'Timestamp',ZUSERID as 'User',ZTEXT as 'Text' from ZPOST where ZSOURCE='profileFeed';")
		comment = sql(path,"SELECT ZPOSTID as 'Post_ID' ,ZCREATIONDATE as 'Timestamp',ZUSERID as 'User',ZTEXT as 'Text' from ZCOMMENT;")
		_FEED = {'Timestamp':[],'User':[],'Type':[],'Text':[]}
		_DM = {'Timestamp':[],'User':[],'Text':[]}


		unix = datetime(1970, 1, 1)
		cocoa = datetime(2001, 1, 1)
		delta = cocoa - unix
		
		for i in post:
			timestamp = datetime.fromtimestamp(int(i[1])) + delta
			_FEED['Timestamp'].append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))
			_FEED['User'].append(users[i[2]])
			_FEED['Type'].append('Post')
			_FEED['Text'].append(i[3])
			for j in comment:
				if j[0] == i[0]:
					timestamp = datetime.fromtimestamp(int(j[1])) + delta
					_FEED['Timestamp'].append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))
					_FEED['User'].append(users[j[2]])
					_FEED['Type'].append('Comment')
					_FEED['Text'].append(j[3])

		prnt("Feed:",_FEED,4) if prt == 1 else None

		for i in chat:
			if i[2] != "":
				timestamp = datetime.fromtimestamp(int(i[0])) + delta
				_DM['Timestamp'].append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))
				_DM['User'].append(users[i[1]])
				_DM['Text'].append(i[2].strip())

		prnt("DM:",_DM,3) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = glob.glob('./{}/MeWe/Tmp/*'.format(foldername))

	if os.path.isdir('./{}/MeWe/Tmp'.format(foldername)):
		_FILES1 = {"Filenames":[],"Location":[]}

		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES1["Filenames"].append(os.path.basename(i))
			_FILES1["Location"].append("."+i[len(foldername)+2:])

		prnt("Tmp:",_FILES1,1) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = glob.glob('./{}/MeWe/SDImageCache/*'.format(foldername))

	if os.path.isdir('./{}/MeWe/SDImageCache'.format(foldername)):
		_FILES2 = {"Filenames":[],"Location":[]}

		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES2["Filenames"].append(os.path.basename(i))
			_FILES2["Location"].append("."+i[len(foldername)+2:])

		prnt("SDImageCache:",_FILES2,1) if prt == 1 else None

	return [_REC,_RES,_FEED,_DM,_FILES1,_FILES2,_HASHES]

def _1st2nd(prt):
	if os.path.isdir('./{}/2nd1st'.format(foldername)):
		print("2nd1st:") if prt == 1 else None

	_FILES={}
	_HASHES = {"Filename":[],"SHA256":[]}

	#===================================================
	#===================================================
	#===================================================

	path = glob.glob('./{}/2nd1st/Tmp/*'.format(foldername))
	
	if os.path.isdir('./{}/2nd1st/Tmp'.format(foldername)):
		_FILES = {"Filenames":[],"Location":[]}

		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES["Filenames"].append(os.path.basename(i))
			_FILES["Location"].append("."+i[len(foldername)+2:])

		prnt("Tmp:",_FILES,1) if prt == 1 else None

	return [_FILES,_HASHES]

def clouthub(prt):
	if os.path.isdir('./{}/CloutHub'.format(foldername)):
		print("CloutHub:") if prt == 1 else None

	_FILES1,_FILES2,_REC,_SERV={},{},{},{}
	_HASHES = {"Filename":[],"SHA256":[]}

	#===================================================
	#===================================================
	#===================================================

	path = glob.glob('./{}/CloutHub/Tmp/*'.format(foldername))
	
	if os.path.isdir('./{}/CloutHub/Tmp'.format(foldername)):
		_FILES1 = {"Filenames":[],"Location":[]}

		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES1["Filenames"].append(os.path.basename(i))
			_FILES1["Location"].append("."+i[len(foldername)+2:])

		prnt("Tmp:",_FILES1,1) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = glob.glob('./{}/CloutHub/SDImageCache/*'.format(foldername))

	if os.path.isdir('./{}/CloutHub/SDImageCache'.format(foldername)):
		_FILES2 = {"Filenames":[],"Location":[]}

		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES2["Filenames"].append(os.path.basename(i))
			_FILES2["Location"].append("."+i[len(foldername)+2:])

		prnt("SDImageCache:",_FILES2,1) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/CloutHub/Cache.db".format(foldername)
	
	if os.path.isfile(path):
		_HASHES["Filename"].append(os.path.basename(path))
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		receiver = sql(path,"SELECT receiver_data from cfurl_cache_receiver_data where receiver_data like '%messageId%' or receiver_data like '%originalLink%'")
		_REC = {'Key':[],'Value':[]}

		for i in receiver:
			val = json.loads(i[0])
			if "messageId" in val:
				_REC['Key'].append("messageId")
				_REC['Value'].append(val["messageId"])
				_REC['Key'].append("msgBody")
				_REC['Value'].append(val["msgBody"])
				_REC['Key'].append("msgCreateTime")
				_REC['Value'].append(val["msgCreateTime"])
				_REC['Key'].append("Sender")
				_REC['Value'].append(val["sender"]["firstname"] +" "+ val["sender"]["lastname"])
				_REC['Key'].append("Receiver")
				_REC['Value'].append(val["receiver"]["firstname"] +" "+ val["receiver"]["lastname"])
			else:
				_REC['Key'].append("url")
				_REC['Value'].append(val["url"])
				_REC['Key'].append("details")
				_REC['Value'].append(val["details"])
				_REC['Key'].append("image")
				_REC['Value'].append(val["image"])
				
		prnt("Cache.db:",_REC,2) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/CloutHub/com.amplitude.database".format(foldername)
	
	if os.path.isfile(path):
		_HASHES["Filename"].append(os.path.basename(path))
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		server = sql(path,"SELECT key,value from long_store where key='previous_session_id' or key='last_event_time' UNION SELECT key,value from store")
			
		_SERV = {"Key":[], "Value":[]}

		for i in server:
			_SERV["Key"].append(i[0])
			_SERV["Value"].append(i[1])
			
		#prnt("com.amplitude.api:",_SERV,2) if prt == 1 else None

	return [_FILES1,_FILES2,_REC,_SERV,_HASHES]
	
def minds_mobile(prt):
	if os.path.isdir('./{}/Minds(Mobile)'.format(foldername)):
		print("Mind Mobile:") if prt == 1 else None

	_FILES1,_FILES2,_MIND,_REC,_IMG={},{},{},{},{}
	_HASHES = {"Filename":[],"SHA256":[]}

	#===================================================
	#===================================================
	#===================================================

	path = glob.glob('./{}/Minds(Mobile)/Tmp/*'.format(foldername))
	
	if os.path.isdir('./{}/Minds(Mobile)/Tmp'.format(foldername)):
		_FILES1 = {"Filenames":[],"Location":[]}

		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES1["Filenames"].append(os.path.basename(i))
			_FILES1["Location"].append("."+i[len(foldername)+2:])

		prnt("Tmp:",_FILES1,1) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = glob.glob('./{}/Minds(Mobile)/SDImageCache/*'.format(foldername))

	if os.path.isdir('./{}/Minds(Mobile)/SDImageCache'.format(foldername)):
		_FILES2 = {"Filenames":[],"Location":[]}

		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES2["Filenames"].append(os.path.basename(i))
			_FILES2["Location"].append("."+i[len(foldername)+2:])

		prnt("SDImageCache:",_FILES2,1) if prt == 1 else None
	
	#===================================================
	#===================================================
	#===================================================

	path = "./{}/Minds(Mobile)/minds1.db".format(foldername)

	if os.path.isfile(path):
		_HASHES["Filename"].append(os.path.basename(path))
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		minds = sql(path,"SELECT data FROM comments_feeds where data like '%\"type\":\"comment\"%'")
			
		_MIND = {"Timestamp":[],"Username":[],"Comment":[]}

		for i in minds:
			val = json.loads(i[0])
			_MIND["Timestamp"].append(val["comments"][0]["time_created"])
			_MIND["Username"].append(val["comments"][0]["ownerObj"]["username"])
			_MIND["Comment"].append(val["comments"][0]["description"])
			
		prnt("minds1.db:",_MIND,3) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/Minds(Mobile)/Cache.db".format(foldername)

	if os.path.isfile(path):
		_HASHES["Filename"].append(os.path.basename(path))
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		receiver = sql(path,"SELECT entry_ID,receiver_data from cfurl_cache_receiver_data where typeof(receiver_data) == 'blob' and receiver_data NOT like '%{\"status%'")
		_REC = {'Filenames':[],"Location":[]}

		p = os.path.join("./{}/Minds(Mobile)".format(foldername),"Cache")

		if os.path.isdir(p) == 'True' or os.path.isdir(p) == True:
			for f in os.listdir(p):
				os.remove(os.path.join(p, f))
			os.rmdir(p)
		
		os.mkdir(p)
		for i in receiver:
			img_path = "./{}/Minds(Mobile)/Cache/{}.png".format(foldername,i[0])
			convert_data(i[1], img_path)
			_HASHES["Filename"].append(os.path.basename(img_path))
			_HASHES["SHA256"].append(hashlib.sha256(open(img_path,'rb').read()).hexdigest())
			_REC['Filenames'].append(os.path.basename(img_path))
			_REC['Location'].append("."+img_path[len(foldername)+2:])

		prnt("Cache.db:",_REC,1) if prt == 1 else None
	
	#===================================================
	#===================================================
	#===================================================

	path = "./{}/Minds(Mobile)/fsCachedData".format(foldername)
	

	if os.path.isdir(path):
		_IMG = {'Filenames':[],"Location":[]}
		full = ""
		for count, filename in enumerate(os.listdir(path)):
			if ".jpg" not in filename:
				dst1 = f"{filename}.jpg"
				src =f"{path}/{filename}"
				dst =f"{path}/{dst1}"	
				os.rename(src, dst)
				full = os.path.join(path,dst1)
			else:
				full = os.path.join(path,filename)
			_HASHES["Filename"].append(os.path.basename(full))
			_HASHES["SHA256"].append(hashlib.sha256(open(full,'rb').read()).hexdigest())
			_IMG['Filenames'].append(os.path.basename(full))
			_IMG['Location'].append("."+full[len(foldername)+2:])

		prnt("fsCachedData:",_IMG,1) if prt == 1 else None
	
	return [_FILES1,_FILES2,_MIND,_REC,_IMG,_HASHES]

def minds_chat(prt):
	if os.path.isdir('./{}/Minds(Chat)'.format(foldername)):
		print("Minds Chat:") if prt == 1 else None

	_FILES1,_FILES2={},{}
	_HASHES = {"Filename":[],"SHA256":[]}

	#===================================================
	#===================================================
	#===================================================

	path = glob.glob('./{}/Minds(Chat)/Caches/*'.format(foldername))
	
	if os.path.isdir('./{}/Minds(Chat)/Caches'.format(foldername)):
		_FILES1 = {"Filenames":[],"Location":[]}

		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES1["Filenames"].append(os.path.basename(i))
			_FILES1["Location"].append("."+i[len(foldername)+2:])

		prnt("Tmp:",_FILES1,1) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/Minds(Chat)/mediacache".format(foldername)
	
	if os.path.isdir(path):
		_FILES2 = {"Filenames":[],"Location":[]}

		listOfFiles = list()
		for (dirpath, dirnames, filenames) in os.walk(path):
			for file in filenames:
				if "_w" not in file and os.path.basename(dirpath) != "mediacache":
					_HASHES["Filename"].append(os.path.basename(file))
					_HASHES["SHA256"].append(hashlib.sha256(open(os.path.join(dirpath, file),'rb').read()).hexdigest())
					_FILES2["Filenames"].append(os.path.basename(file))
					_FILES2["Location"].append("."+dirpath[len(foldername)+2:]+"\\"+file)

		prnt("Tmp:",_FILES2,1) if prt == 1 else None

	return [_FILES1,_FILES2,_HASHES]

def safechat(prt):
	if os.path.isdir('./{}/SafeChat'.format(foldername)):
		print("SafeChat:") if prt == 1 else None
	
	_CONV,_MSG,_USER,_FILES1,_FILES2={},{},{},{},{}
	_HASHES = {"Filename":[],"SHA256":[]}

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/SafeChat/SafeChat.db".format(foldername)
	
	if os.path.isfile(path):
		_HASHES["Filename"].append(os.path.basename(path))
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		convo = sql(path,"SELECT serverId,ownerId,createdAt,localName,sharedKey,lastMessageDecryptedPreview FROM Conversation")
		msg = sql(path,"SELECT senderId,conversationId,text,createdAt,encryptMode FROM Message WHERE text NOT like '{\"%'")
		user = sql(path,"SELECT email, username, friendState FROM User")

		_CONV = {'serverId':[],'ownerId':[],'createdAt':[],'localName':[],'sharedKey':[],'message':[]}
		_MSG = {'senderId':[],'conversationId':[],'text':[],'createdAt':[],'encryptMode':[]}
		_USER = {'email':[],'username':[],'friendState':[]}


		for i in convo:
			_CONV['serverId'].append(i[0])
			_CONV['ownerId'].append(i[1])
			_CONV['createdAt'].append(i[2])
			_CONV['localName'].append(i[3])
			_CONV['sharedKey'].append(i[4])
			_CONV['message'].append(i[5])

		for i in msg:
			_MSG['senderId'].append(i[0])
			_MSG['conversationId'].append(i[1])
			_MSG['text'].append(i[2])
			_MSG['createdAt'].append(i[3])
			_MSG['encryptMode'].append(i[4])

		for i in user:
			_USER['email'].append(i[0])
			_USER['username'].append(i[1])
			_USER['friendState'].append(i[2])	

		prnt("Conversation:",_CONV,6) if prt == 1 else None
		prnt("Messages:",_MSG,5) if prt == 1 else None
		prnt("Users:",_USER,3) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = glob.glob('./{}/SafeChat/Tmp/*'.format(foldername))
	
	if os.path.isdir('./{}/SafeChat/Tmp'.format(foldername)):
		_FILES1 = {"Filenames":[],"Location":[]}

		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES1["Filenames"].append(os.path.basename(i))
			_FILES1["Location"].append("."+i[len(foldername)+2:])

		prnt("Tmp:",_FILES1,1) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = glob.glob('./{}/SafeChat/.video/*'.format(foldername))
	
	if os.path.isdir('./{}/SafeChat/.video'.format(foldername)):
		_FILES2 = {"Filenames":[],"Location":[]}

		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES2["Filenames"].append(os.path.basename(i))
			_FILES2["Location"].append("."+i[len(foldername)+2:])

		prnt("Videos:",_FILES2,1) if prt == 1 else None

	return [_CONV,_MSG,_USER,_FILES1,_FILES2,_HASHES]

def gettr(prt):
	if os.path.isdir('./{}/Gettr'.format(foldername)):
		print("Gettr:") if prt == 1 else None

	_FILES1,_USER,_G,_CACHE={},{},{},{}
	_HASHES = {"Filename":[],"SHA256":[]}

	#===================================================
	#===================================================
	#===================================================

	path = glob.glob('./{}/Gettr/.video/*'.format(foldername)) + glob.glob('./{}/Gettr/.image/*'.format(foldername)) + glob.glob('./{}/Gettr/flutter-images/*'.format(foldername)) + glob.glob('./{}/Gettr/libCachedImageData/*'.format(foldername))
	
	if os.path.isdir('./{}/Gettr/.video'.format(foldername)) or os.path.isdir('./{}/Gettr/.image'.format(foldername)) or os.path.isdir('./{}/Gettr/flutter-images'.format(foldername)) or os.path.isdir('./{}/Gettr/libCachedImageData'.format(foldername)):
		_FILES1 = {"Filenames":[],"Location":[]}

		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES1["Filenames"].append(os.path.basename(i))
			_FILES1["Location"].append("."+i[len(foldername)+2:])

		prnt("Tmp:",_FILES1,1) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	if os.path.isdir("./{}/Gettr".format(foldername)):
		path = glob.glob("./{}/Gettr/private_*.db".format(foldername))
		if len(path) > 0:
			path = path[0]

			_HASHES["Filename"].append(os.path.basename(path))
			_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
			
			user = sql(path,"SELECT key,value from kv where key='history/followed/list' or key='search/global/userlist'")

			_USER = {'Key':[],'Value':[]}

			for i in user:
				_USER['Key'].append(i[0])
				_USER['Value'].append(i[1])
				
			prnt(os.path.basename(path),_USER,2) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/Gettr/g.db".format(foldername)

	if os.path.isfile(path):
		_HASHES["Filename"].append(os.path.basename(path))
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		g = sql(path,"SELECT key,value FROM kv WHERE key='user_me' or key='auth_device_id'")

		_G = {'Key':[],'Value':[]}

		for i in g:
			if i[0] == "user_me":
				data = json.loads(i[1])
				_G['Key'].append("token")
				_G['Value'].append(data["token"])
				_G['Key'].append("userId")
				_G['Value'].append(data["userInfo"]["userId"])
				_G['Key'].append("dateCreated")
				_G['Value'].append(data["userInfo"]["dateCreated"])
				_G['Key'].append("dateUpdated")
				_G['Value'].append(data["userInfo"]["dateUpdated"])
			else:
				_G['Key'].append(i[0])
				_G['Value'].append(i[1])

		prnt("g.db:",_G,2) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/Gettr/Cache.db".format(foldername)

	if os.path.isfile(path):
		_HASHES["Filename"].append(os.path.basename(path))
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		cache = sql(path,"SELECT receiver_data from cfurl_cache_receiver_data where receiver_data like '%\"result\":{\"data\":{\"acl\":{\"pub\"%'")

		_CACHE = {'createdAt':[],'dateUpdated':[],'comment':[]}

		for i in cache:
			d = json.loads(i[0])
			_CACHE['createdAt'].append(d['result']['data']['cdate'])
			_CACHE['dateUpdated'].append(d['result']['data']['udate'])
			_CACHE['comment'].append(d['result']['data']['txt'])
			
		prnt("Cache.db:",_CACHE,3) if prt == 1 else None

	return [_FILES1,_USER,_G,_CACHE,_HASHES]

def match(path):
			f_url = os.path.basename(path)
			return '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>'.format(path, f_url)	

def report(parler_,mewe_,clouthub_,firstsecond_,mindsmobile_,mindschat_,safechat_,gettr_):																#Generates report with parsed data
	copyfile('./style.css', './{}/style.css'.format(foldername))
	f = open("./{}/report.html".format(foldername),"w",encoding='utf-8')
	f.write("<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>Apple</title>\
			<link href='style.css' rel='stylesheet' type='text/css' /></head><body><h1>Apple Forensics Report</h1>\
			<div style='margin-left:auto;margin-right:auto;width:800px;height:285px;border:2px solid #000;'><h3>\
			Filename: {}<br>Case: {}<br>Timestamp: {}<br>Examiner: {}<br>Image Size: {}<br>Extraction Time: {}<br>Before Analysis:<br>MD5: {}<br>SHA256: {}<br>After Analysis:<br>MD5: {}<br>SHA256: {}</h3></div>".format(foldername,case,timestamp,examiner,image_size,extraction_time,md5,sha256,check_md5,check_sha256))
	
	f.write('''<div class="tab">''')
	f.write('''<button class="tablinks" onclick="apptabs(event, 'Gettr')" id="defaultOpen">Gettr</button>''')
	f.write('''<button class="tablinks" onclick="apptabs(event, 'SafeChat')">SafeChat</button>''')
	f.write('''<button class="tablinks" onclick="apptabs(event, 'MindsChat')">Minds Chat</button>''')
	f.write('''<button class="tablinks" onclick="apptabs(event, 'MindsMobile')">Minds Mobile</button>''')
	f.write('''<button class="tablinks" onclick="apptabs(event, '1st2nd')">2nd1st</button>''')
	f.write('''<button class="tablinks" onclick="apptabs(event, 'CloutHub')">CloutHub</button>''')
	f.write('''<button class="tablinks" onclick="apptabs(event, 'MeWe')">MeWe</button>''')
	f.write('''<button class="tablinks" onclick="apptabs(event, 'Parler')">Parler</button>''')
	f.write('''</div>''')

	f.write('''<div id="Gettr" class="tabcontent">''')
	
	if not gettr_[0]:
		pass
	else:
		f.write("<h2>Tmp Cache Files</h2>\n")
		gettr_[0].pop("Filenames")
		df1 = pd.DataFrame.from_dict(gettr_[0])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not gettr_[1]:
		pass
	else:
		file = os.path.basename(glob.glob("./{}/Gettr/private_*.db".format(foldername))[0])
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">{}</a></h2>\n'''.format(os.path.abspath("./{}/Gettr/{}".format(foldername,file)),file))
		df1 = pd.DataFrame.from_dict(gettr_[1])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not gettr_[2]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">g.db</a></h2>\n'''.format(os.path.abspath("./{}/Gettr/g.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(gettr_[2])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not gettr_[3]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">Cache.db</a></h2>\n'''.format(os.path.abspath("./{}/Gettr/Cache.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(gettr_[3])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not gettr_[4]["Filename"]:
		pass
	else:
		f.write("<h2>Hash Table</h2>\n")
		df1 = pd.DataFrame.from_dict(gettr_[4])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	f.write('''</div>''')
	f.write('''<div id="SafeChat" class="tabcontent">''')
	
	if not safechat_[0]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">SafeChat.db</a> - Conversation</h2>\n'''.format(os.path.abspath("./{}/SafeChat/SafeChat.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(safechat_[0])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'},**{"word-wrap": "break-word"}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not safechat_[1]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">SafeChat.db</a> - Message</h2>\n'''.format(os.path.abspath("./{}/SafeChat/SafeChat.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(safechat_[1])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not safechat_[2]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">SafeChat.db</a> - User</h2>\n'''.format(os.path.abspath("./{}/SafeChat/SafeChat.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(safechat_[2])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not safechat_[3]:
		pass
	else:
		f.write("<h2>Tmp Cache Files</h2>\n")
		safechat_[3].pop("Filenames")
		df1 = pd.DataFrame.from_dict(safechat_[3])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not safechat_[4]:
		pass
	else:
		f.write("<h2>.video Files</h2>\n")
		safechat_[4].pop("Filenames")
		df1 = pd.DataFrame.from_dict(safechat_[4])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not safechat_[5]["Filename"]:
		pass
	else:
		f.write("<h2>Hash Table</h2>\n")
		df1 = pd.DataFrame.from_dict(safechat_[5])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	f.write('''</div>''')

	f.write('''<div id="MindsChat" class="tabcontent">''')
	
	if not mindschat_[0]:
		pass
	else:
		f.write("<h2>Tmp Cache Files</h2>\n")
		mindschat_[0].pop("Filenames")
		df1 = pd.DataFrame.from_dict(mindschat_[0])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mindschat_[1]:
		pass
	else:
		f.write("<h2>Mediacache Files</h2>\n")
		mindschat_[1].pop("Filenames")
		df1 = pd.DataFrame.from_dict(mindschat_[1])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mindschat_[2]["Filename"]:
		pass
	else:
		f.write("<h2>Hash Table</h2>\n")
		df1 = pd.DataFrame.from_dict(mindschat_[2])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	f.write('''</div>''')
	
	f.write('''<div id="MindsMobile" class="tabcontent">''')
	if not mindsmobile_[0]:
		pass
	else:
		f.write("<h2>Tmp Cache Files</h2>\n")
		mindsmobile_[0].pop("Filenames")
		df1 = pd.DataFrame.from_dict(mindsmobile_[0])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mindsmobile_[1]:
		pass
	else:
		f.write("<h2>SDImageCache Files</h2>\n")
		mindsmobile_[1].pop("Filenames")
		df1 = pd.DataFrame.from_dict(mindsmobile_[1])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mindsmobile_[2]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">minds1.db</a></h2>\n'''.format(os.path.abspath("./{}/Minds(Mobile)/minds1.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(mindsmobile_[2])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mindsmobile_[3]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">Cache.db</a></h2>\n'''.format(os.path.abspath("./{}/Minds(Mobile)/Cache.db".format(foldername))))
		mindsmobile_[3].pop("Filenames")
		df1 = pd.DataFrame.from_dict(mindsmobile_[3])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mindsmobile_[4]:
		pass
	else:
		f.write("<h2>fsCachedData Files</h2>\n")
		mindsmobile_[4].pop("Filenames")
		df1 = pd.DataFrame.from_dict(mindsmobile_[4])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mindsmobile_[5]["Filename"]:
		pass
	else:
		f.write("<h2>Hash Table</h2>\n")
		df1 = pd.DataFrame.from_dict(mindsmobile_[5])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)
	f.write('''</div>''')
	
	f.write('''<div id="1st2nd" class="tabcontent">''')
	if not firstsecond_[0]:
		pass
	else:
		f.write("<h2>Tmp Cache Files</h2>\n")
		firstsecond_[0].pop("Filenames")
		df1 = pd.DataFrame.from_dict(firstsecond_[0])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not firstsecond_[1]["Filename"]:
		pass
	else:
		f.write("<h2>Hash Table</h2>\n")
		df1 = pd.DataFrame.from_dict(firstsecond_[1])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	f.write('''</div>''')
	f.write('''<div id="CloutHub" class="tabcontent">''')
	
	if not clouthub_[0]:
		pass
	else:
		f.write("<h2>Tmp Cache Files</h2>\n")
		clouthub_[0].pop("Filenames")
		df1 = pd.DataFrame.from_dict(clouthub_[0])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not clouthub_[1]:
		pass
	else:
		f.write("<h2>SDImageCache Files</h2>\n")
		clouthub_[1].pop("Filenames")
		df1 = pd.DataFrame.from_dict(clouthub_[1])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not clouthub_[2]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">Cache.db</a></h2>\n'''.format(os.path.abspath("./{}/CloutHub/Cache.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(clouthub_[2])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	#if not clouthub_[3]:
	#	pass
	#else:
	#	f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">com.amplitude.database</a></h2>\n'''.format(os.path.abspath("./{}/CloutHub/com.amplitude.database".format(foldername))))
	#	df1 = pd.DataFrame.from_dict(clouthub_[3])
	#	df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
	#	df1 = df1.replace("T_t03","t03")
	#	f.write(df1)

	if not clouthub_[4]["Filename"]:
		pass
	else:
		f.write("<h2>Hash Table</h2>\n")
		df1 = pd.DataFrame.from_dict(clouthub_[4])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)
	f.write('''</div>''')
	
	f.write('''<div id="MeWe" class="tabcontent">''')
	if not mewe_[0]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">Cache.db</a> - Receiver</h2>\n'''.format(os.path.abspath("./{}/MeWe/Cache.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(mewe_[0])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mewe_[1]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">Cache.db</a> - Response</h2>\n'''.format(os.path.abspath("./{}/MeWe/Cache.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(mewe_[1])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mewe_[2]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">sgrouplesdb.sqlite</a> - post/comment</h2>\n'''.format(os.path.abspath("./{}/Mewe/sgrouplesdb.sqlite".format(foldername))))
		df1 = pd.DataFrame.from_dict(mewe_[2])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mewe_[3]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">sgrouplesdb.sqlite</a> - chat</h2>\n'''.format(os.path.abspath("./{}/Mewe/sgrouplesdb.sqlite".format(foldername))))
		df1 = pd.DataFrame.from_dict(mewe_[3])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mewe_[4]:
		pass
	else:
		f.write("<h2>Tmp Cache Files</h2>\n")
		mewe_[4].pop("Filenames")
		df1 = pd.DataFrame.from_dict(mewe_[4])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mewe_[5]:
		pass
	else:
		f.write("<h2>SDImageCache Files</h2>\n")
		mewe_[5].pop("Filenames")
		df1 = pd.DataFrame.from_dict(mewe_[5])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mewe_[6]["Filename"]:
		pass
	else:
		f.write("<h2>Hash Table</h2>\n")
		df1 = pd.DataFrame.from_dict(mewe_[6])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)
	f.write('''</div>''')

	f.write('''<div id="Parler" class="tabcontent">''')
	if not parler_[0]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">https_parler.com_0.localstorage</a></h2>\n'''.format(os.path.abspath("./{}/Parler/https_parler.com_0.localstorage".format(foldername))))
		df1 = pd.DataFrame.from_dict(parler_[0])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not parler_[1]:
		pass
	else:
		f.write("<h2>Cache Files</h2>\n")
		parler_[1].pop("Filenames")
		df1 = pd.DataFrame.from_dict(parler_[1])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)
	
	if not parler_[2]["Filename"]:
		pass
	else:
		f.write("<h2>Hash Table</h2>\n")
		df1 = pd.DataFrame.from_dict(parler_[2])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)
	f.write('''</div>''')

	f.write('''<script>function apptabs(evt, appName) {  var i, tabcontent, tablinks;  tabcontent = document.getElementsByClassName("tabcontent");  for (i = 0; i < tabcontent.length; i++) {    tabcontent[i].style.display = "none";  }  tablinks = document.getElementsByClassName("tablinks");  for (i = 0; i < tablinks.length; i++) {    tablinks[i].className = tablinks[i].className.replace(" active", "");  }  document.getElementById(appName).style.display = "block";  evt.currentTarget.className += " active";}</script>''')	
	
	f.write("</body></html>")
	f.close()

def setup(file):
	global case,examiner,md5,sha256,foldername,timestamp,image_size
	timestamp = datetime.utcnow().strftime("%m/%d/%Y-%H:%M:%S UTC")
	case = input("Enter case #:")
	foldername = case+"-Apple"
	examiner = input("Enter examiner name:")
	image_size = size(os.path.getsize(file))
	md5 = hashlib.md5(open(file,'rb').read()).hexdigest()
	print("MD5:",md5)
	sha256 = hashlib.sha256(open(file,'rb').read()).hexdigest()
	print("SHA256:",sha256)

def hash_check(file):												#Re-hashes tar file to check integrity
	global check_md5,check_sha256
	print("After Analysis:")
	check_md5 = hashlib.md5(open(file,'rb').read()).hexdigest()
	if md5 == check_md5:
		print("MD5:",check_md5,": Matched") 
		check_md5 += " : Matched"
	else: 
		print("MD5:",check_md5,": Not Matched") 
		check_md5 += " : Not Matched"
	
	check_sha256 = hashlib.sha256(open(file,'rb').read()).hexdigest()
	if sha256 == check_sha256:
		print("SHA256:",check_sha256,": Matched") 
		check_sha256 += " : Matched"
	else:
		print("SHA256:",check_sha256,": Not Matched")
		check_sha256 += " : Not Matched"


def selection():
	print("\nApplications:")
	installedApps = []
	apps = os.listdir("./{}/".format(foldername))
	ct = 1
	for i in apps:
		if os.path.isdir("./{}/{}".format(foldername,i)):
			print(ct, i)
			ct+=1
			installedApps.append(i)

	selectedApps = []
	
	def select(instApps):
		selected = []
		selection = ""
		print("\nEx: 'ALL' or '1259'")
		selection = input("Select which apps you want: ")
		if selection == 'ALL' or selection == 'all' or selection.isnumeric():
			if selection == 'ALL' or selection == 'all':
				return instApps
			else:
				selection = list(selection)
				for sel in selection:
					selected.append(instApps[int(sel)-1])
				return selected
		else:
			print("\n\nSelection format is wrong. Please try again.")
			return select(installedApps)

	conv = {'Parler':0,'MeWe':0,'CloutHub':0,'2nd1st':0,'Minds(Mobile)':0,'Minds(Chat)':0,'SafeChat':0,'Gettr':0}
	
	selectedApps = select(installedApps)

	for i in selectedApps:
		conv[i] = 1

	return list(conv.values())

def apple(file):
	setup(file)
	extract(file)
	prt = selection()
	parler_ = parler(prt[0])
	mewe_ = mewe(prt[1])
	clouthub_ = clouthub(prt[2])
	firstsecond_ = _1st2nd(prt[3])
	mindsmobile_ = minds_mobile(prt[4])
	mindschat_ = minds_chat(prt[5])
	safechat_ = safechat(prt[6])
	gettr_ = gettr(prt[7])
	hash_check(file)
	report(parler_,mewe_,clouthub_,firstsecond_,mindsmobile_,mindschat_,safechat_,gettr_)
