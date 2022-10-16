import os,tarfile,sys,datetime,pathlib,glob,re,time
import xmltodict,sqlite3,re
from hurry.filesize import size
from columnar import columnar
from shutil import copyfile
import pandas as pd
import hashlib
from datetime import datetime,timedelta
import emojis
import json
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

def xml_open(file):
	try:								#opens xml files
		with open(file,"r") as fp:
			dc = xmltodict.parse(fp.read())
	except:
		with open(file,"rb") as fp:
			dc = xmltodict.parse(fp.read())
	return dc

def extract(file):				#Extracts files from wordlist
	global extraction_time
	start_time = time.time()
	allowedApps = ['com.clouthub.clouthub','com.gettr.gettr','com.mewe','com.minds.chat','com.minds.mobile','com.truthsocial.android','com.wimkin.android','net.safechat.app']
	tar = tarfile.open(file)												#Opens the provided tar image
	mem = tar.getmembers()
	
	wordlist = {'com.clouthub.clouthub':'Clouthub.txt','com.gettr.gettr':'Gettr.txt','com.mewe':'MeWe.txt','com.minds.chat':'Minds_Chat.txt','com.minds.mobile':'Minds_Mobile.txt','com.truthsocial.android':'Truth_Social.txt','com.wimkin.android':'Wimkin.txt','net.safechat.app':'SafeChat.txt'}
	
	files = {}
	for a in allowedApps:
		words = []
		try:																#Tries to open the default wordlist
			with open('Default_lists/Android/{}'.format(wordlist[a])) as my_file:	
				for line in my_file:										#Takes words in the wordlist file and creats a list
					words.append(line[:-1])
		except FileNotFoundError:											#File not found error
			print("{} not found".format(wordlist[a]))
			sys.exit()
		files[a] = words

	def members(sub):
		l = len("data/data/{}/".format(sub))
		for word in files[sub]:
			for member in mem:	
				if member.path.startswith("data/data/{}/".format(sub)) and word in member.path:
					member.path = member.path[l:]
					yield member

	for i in allowedApps:
		tar.extractall(members=members(i),path="./{}/{}".format(foldername,i))
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

def gettr(prt):
	if os.path.isdir('./{}/com.gettr.gettr'.format(foldername)):
		print("\nGettr:\n") if prt == 1 else None

	_IMAGE,_G,_USER,_GIF,_GIPHY={},{},{},{},{}
	_HASHES = {"Filename":[],"SHA256":[]}

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/com.gettr.gettr/files/LibCachedImageData.db".format(foldername)
	
	if os.path.isfile(path):
		_HASHES["Filename"].append("LibCachedImageData.db")
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		image = sql(path,"select url,relativePath from cacheObject")

		_IMAGE = {"URL":[],"Relative_Path":[]}
		for i in image:
			_IMAGE["URL"].append(i[0])
			_IMAGE["Relative_Path"].append(i[1])

		prnt("LibCachedImageData.db:",_IMAGE,2) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/com.gettr.gettr/databases/g.db".format(foldername)
	
	if os.path.isfile(path):
		_HASHES["Filename"].append("g.db")
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		g = sql(path,"SELECT key,value from kv where VALUE like '{\"%' or Key='auth_device_id'")

		_G = {"User":[],"Info":[]}
		for i in g:
			_G["User"].append(i[0])
			_G["Info"].append(i[1])

		prnt("g.db:",_G,2) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	if os.path.isdir("./{}/com.gettr.gettr/databases".format(foldername)):
		path = glob.glob('./{}/com.gettr.gettr/databases/private_*.db'.format(foldername))
		if len(path) > 0:
			path = path[0]
			_HASHES["Filename"].append(os.path.basename(path))
			_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
			
			user = sql(path,"SELECT key,value from kv where key='history/followed/list' or key='search/global/userlist'")

			_USER = {"Type":[],"Info":[]}
			for i in user:
				_USER["Type"].append(i[0])
				_USER["Info"].append(i[1])

			prnt(os.path.basename(path),_USER,2) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	if os.path.isdir("./{}/com.gettr.gettr/cache/libCachedImageData".format(foldername)):
		path = glob.glob('./{}/com.gettr.gettr/cache/libCachedImageData/*.gif'.format(foldername))
		_GIF = {"Filenames":[],"Location":[]}
		
		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_GIF["Filenames"].append(os.path.basename(i))
			_GIF["Location"].append("."+i[len(foldername)+2:])

		prnt("Gifs:",_GIF,1) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	pr = 0
	
	if os.path.isfile('./{}/com.gettr.gettr/shared_prefs/giphy_recents_file.xml'.format(foldername)) or os.path.isfile('./{}/com.gettr.gettr/shared_prefs/giphy_searches_file.xml'.format(foldername)):
		_GIPHY = {"Key":[],"Value":[]}
		pr = 1
		
	if os.path.isfile('./{}/com.gettr.gettr/shared_prefs/giphy_recents_file.xml'.format(foldername)):
		recent = dict(dict(dict(xml_open('./{}/com.gettr.gettr/shared_prefs/giphy_recents_file.xml'.format(foldername)))['map'])['string'])
		_HASHES["Filename"].append("giphy_recents_file.xml")
		_HASHES["SHA256"].append(hashlib.sha256(open('./{}/com.gettr.gettr/shared_prefs/giphy_recents_file.xml'.format(foldername),'rb').read()).hexdigest())
		_GIPHY["Key"].append(recent['@name'])
		_GIPHY["Value"].append(recent['#text'])
	
	if os.path.isfile('./{}/com.gettr.gettr/shared_prefs/giphy_searches_file.xml'.format(foldername)):
		search = dict(dict(dict(xml_open('./{}/com.gettr.gettr/shared_prefs/giphy_searches_file.xml'.format(foldername)))['map'])['string'])
		_HASHES["Filename"].append("giphy_searches_file.xml")
		_HASHES["SHA256"].append(hashlib.sha256(open('./{}/com.gettr.gettr/shared_prefs/giphy_searches_file.xml'.format(foldername),'rb').read()).hexdigest())
		_GIPHY["Key"].append(search['@name'])
		_GIPHY["Value"].append(search['#text'])
	
	if pr == 1:
		prnt("Giphy Files:",_GIPHY,2) if prt == 1 else None
	
	return [_IMAGE,_G,_USER,_GIF,_GIPHY,_HASHES]

def safechat(prt):
	if os.path.isdir('./{}/net.safechat.app'.format(foldername)):
		print("\nSafe Chat:\n") if prt == 1 else None

	_MP4,_AAC,_CHANNEL,_CONVO,_MSG,_USR,_TASK={},{},{},{},{},{},{}
	_HASHES = {"Filename":[],"SHA256":[]}
	
	#===================================================
	#===================================================
	#===================================================

	if os.path.isdir('./{}/net.safechat.app/cache/SafeChat'.format(foldername)):
		path = glob.glob('./{}/net.safechat.app/cache/SafeChat/*.mp4'.format(foldername))
		_MP4 = {"Filenames":[],"Location":[]}
		
		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_MP4["Filenames"].append(os.path.basename(i))
			_MP4["Location"].append("."+i[len(foldername)+2:])

		prnt("MP4's:",_MP4,1) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	if os.path.isdir('./{}/net.safechat.app/cache'.format(foldername)):
		path = glob.glob('./{}/net.safechat.app/cache/*.aac'.format(foldername))
		_AAC = {"Filenames":[],"Location":[]}
		
		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_AAC["Filenames"].append(os.path.basename(i))
			_AAC["Location"].append("."+i[len(foldername)+2:])

		prnt("ACC's:",_AAC,1) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/net.safechat.app/databases/SafeChat.db".format(foldername)
	
	if os.path.isfile(path):
		_HASHES["Filename"].append("SafeChat.db")
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		channel = sql(path,"SELECT channelId, ownerID, name, description, phone, email, address, totalSubscriber, createdAt from Channel")
		convo = sql(path,"SELECT ownerId, encryptMode, lastMessageId, lastMessagePreview, lastMessageCreatedAt  from Conversation")
		message = sql(path,"SELECT senderId, conversationId, text, textNoAccents, encryptMode, isDecrypted, createdAt, labelStrings  from Message") 
		user = sql(path,"SELECT fullName, email, username, gender, avatarUrl, friendState, joinded  from User")

		_CHANNEL = {"Channel_ID":[], "Owner_ID":[], "Name":[], "Description":[], "Phone":[], "Email":[], "Address":[], "Subscribers":[], "CreatedAt":[]}
		_CONVO = {"Owner_ID":[], "EncryptMode":[], "lastMessageId":[], "lastMessagePreview":[], "lastMessageCreatedAt":[]}
		_MSG = {"Sender_ID":[], "Conversation_ID":[], "Text":[], "TextNoAccents":[], "EncryptMode":[], "isDecrypted":[], "CreatedAt":[], "labelStrings":[]}
		_USR = {"FullName":[], "Email":[], "Username":[], "Gender":[], "AvatarUrl":[], "FriendState":[], "Joinded":[]}

		for i in channel:
			_CHANNEL["Channel_ID"].append(i[0])
			_CHANNEL["Owner_ID"].append(i[1])
			_CHANNEL["Name"].append(i[2])
			_CHANNEL["Description"].append(i[3])
			_CHANNEL["Phone"].append(i[4])
			_CHANNEL["Email"].append(i[5])
			_CHANNEL["Address"].append(i[6])
			_CHANNEL["Subscribers"].append(i[7])
			_CHANNEL["CreatedAt"].append(i[8])

		for i in convo:
			_CONVO["Owner_ID"].append(i[0])
			_CONVO["EncryptMode"].append(i[1])
			_CONVO["lastMessageId"].append(i[2])
			_CONVO["lastMessagePreview"].append(i[3])
			_CONVO["lastMessageCreatedAt"].append(i[4])

		for i in message:
			_MSG["Sender_ID"].append(i[0])
			_MSG["Conversation_ID"].append(i[1])
			_MSG["Text"].append(i[2])
			_MSG["TextNoAccents"].append(i[3])
			_MSG["EncryptMode"].append(i[4])
			_MSG["isDecrypted"].append(i[5])
			_MSG["CreatedAt"].append(i[6])
			_MSG["labelStrings"].append(i[7])
			
		for i in user:
			_USR["FullName"].append(i[0])
			_USR["Email"].append(i[1])
			_USR["Username"].append(i[2])
			_USR["Gender"].append(i[3])
			_USR["AvatarUrl"].append(i[4])
			_USR["FriendState"].append(i[5])
			_USR["Joinded"].append(i[6])

		prnt("Channel:",_CHANNEL,9) if prt == 1 else None
		prnt("Conversation:",_CONVO,5) if prt == 1 else None
		prnt("Messages:",_MSG,8) if prt == 1 else None
		prnt("Users:",_USR,7) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/net.safechat.app/databases/download_tasks.db".format(foldername)
	
	if os.path.isfile(path):
		_HASHES["Filename"].append("download_tasks.db")
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		task = sql(path,"SELECT task_id, url, file_name, saved_dir, time_created from task")
		
		_TASK = {"Task_ID":[], "URL":[], "Filename":[], "Saved_Dir":[], "Time_Created":[]}

		for i in user:
			_TASK["Task_ID"].append(i[0])
			_TASK["URL"].append(i[1])
			_TASK["Filename"].append(i[2])
			_TASK["Saved_Dir"].append(i[3])
			_TASK["Time_Created"].append(i[4])
			
		prnt("Tasks:",_TASK,5) if prt == 1 else None

	return [_MP4,_AAC,_CHANNEL,_CONVO,_MSG,_USR,_TASK,_HASHES]

def minds_chat(prt):
	if os.path.isdir('./{}/com.minds.chat'.format(foldername)):
		print("\nMinds Chat:\n") if prt == 1 else None

	_FILES,_KEYS,_EMOJ={},{},{}
	_HASHES = {"Filename":[],"SHA256":[]}

	path = "./{}/com.minds.chat/cache/downloads".format(foldername)
	
	if os.path.isdir(path):
		listOfFiles = list()
		for (dirpath, dirnames, filenames) in os.walk(path):
			if "\\D\\" in dirpath:
				for file in filenames:
					if "-slack" not in file:
						listOfFiles.append(os.path.join(dirpath, file))

		_FILES = {"Filenames":[],"Location":[]}
		
		for i in listOfFiles:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES["Filenames"].append(os.path.basename(i))
			_FILES["Location"].append("."+i[len(foldername)+2:])

		prnt("DM Files:",_FILES,1) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	if os.path.isfile('./{}/com.minds.chat/shared_prefs/im.vector.matrix.android.keys.xml'.format(foldername)):
		recent = dict(dict(xml_open('./{}/com.minds.chat/shared_prefs/im.vector.matrix.android.keys.xml'.format(foldername)))['map'])['string']
		#_HASHES["Filename"].append("im.vector.matrix.android.keys.xml")
		#_HASHES["SHA256"].append(hashlib.sha256(open('./{}/com.minds.chat/shared_prefs/im.vector.matrix.android.keys.xml'.format(foldername),'rb').read()).hexdigest())
		
		_KEYS = {"Name":[],"Value":[]}
		
		for i in recent:
			_KEYS["Name"].append(dict(i)["@name"])
			_KEYS["Value"].append(dict(i)["#text"])

		#prnt("Keys:",_KEYS,2) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	if os.path.isfile('./{}/com.minds.chat/shared_prefs/emoji-recent-manager.xml'.format(foldername)):
		emoji = open('./{}/com.minds.chat/shared_prefs/emoji-recent-manager.xml'.format(foldername),'rb').readlines()[2]
		_HASHES["Filename"].append("emoji-recent-manager.xml")
		_HASHES["SHA256"].append(hashlib.sha256(open('./{}/com.minds.chat/shared_prefs/emoji-recent-manager.xml'.format(foldername),'rb').read()).hexdigest())
		
		res = emoji.decode('utf-8').encode('unicode-escape').decode('ascii')
		
		_EMOJ = {"Type":[],"Value":[]}
		
		_EMOJ["Type"].append(re.findall(r'\".*?\"', res)[0][1:-1])
		_EMOJ["Value"].append(re.findall(r'\>.*?\<', res)[0][1:-1])

		prnt("Emoji:",_EMOJ,2) if prt == 1 else None

	return [_FILES,_KEYS,_EMOJ,_HASHES]

def minds_mobile(prt):
	if os.path.isdir('./{}/com.minds.mobile'.format(foldername)):
		print("\nMinds Mobile:\n") if prt == 1 else None

	_FILES,_USR,_COMMENT,_FEED,_ENTITIES={},{},{},{},{}
	_HASHES = {"Filename":[],"SHA256":[]}

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/com.minds.mobile/cache/react-native-image-crop-picker".format(foldername)
	
	if os.path.isdir(path):
		listOfFiles = list()
		for (dirpath, dirnames, filenames) in os.walk(path):
			for file in filenames:
				if "-slack" not in file:
					listOfFiles.append(os.path.join(dirpath, file))

		_FILES = {"Filenames":[],"Location":[]}
		
		for i in listOfFiles:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES["Filenames"].append(os.path.basename(i))
			_FILES["Location"].append("."+i[len(foldername)+2:])

		prnt("DM Files:",_FILES,1) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/com.minds.mobile/databases/RKStorage".format(foldername)
	
	if os.path.isfile(path):
		_HASHES["Filename"].append(os.path.basename(path))
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		user = sql(path,"SELECT key,value from catalystLocalStorage where key='@MindsStorage:logged_in_user'")
		
		_USR = {"Key":[], "Value":[]}

		for i in user:
			_USR["Key"].append(i[0])
			_USR["Value"].append(i[1])
			
		prnt("RKStorage:",_USR,2) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/com.minds.mobile/databases/minds1.db".format(foldername)

	if os.path.isfile(path):
		_HASHES["Filename"].append(os.path.basename(path))
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		comments = sql(path,"SELECT parent, data, updated  from comments_feeds")
		feeds = sql(path,"SELECT data, updated  from feeds") 
		entities = sql(path,"SELECT urn, data, updated  from entities")
			
		_COMMENT = {"Parent_ID":[], "Data":[], "Updated":[]}
		_FEED = {"Data":[], "Updated":[]}
		_ENTITIES = {"URN":[], "Data":[], "Updated":[]}
		
		for i in comments:
			_COMMENT["Parent_ID"].append(i[0])
			_COMMENT["Data"].append(i[1])
			_COMMENT["Updated"].append(i[2])
			
		for i in feeds:
			_FEED["Data"].append(i[0])
			_FEED["Updated"].append(i[1])
			
		
		for i in entities:
			_ENTITIES["URN"].append(i[0])
			_ENTITIES["Data"].append(i[1])
			_ENTITIES["Updated"].append(i[2])
		
		prnt("Comment:",_COMMENT,2) if prt == 1 else None
		prnt("Feed:",_FEED,2) if prt == 1 else None
		prnt("Entities:",_ENTITIES,2) if prt == 1 else None

	return [_FILES,_USR,_COMMENT,_FEED,_ENTITIES,_HASHES]

def truthsocial(prt):
    if os.path.isdir('./{}/com.truthsocial.android'.format(foldername)):
        print("\nTruth Social:\n") if prt == 1 else None

    _SERV,_AUTH,_FEED,_PREF,_MSG,_ROOM,_SUBS,_FILES={},{},{},{},{},{},{},{}
    _HASHES = {"Filename":[],"SHA256":[]}

    #===================================================
    #===================================================
    #===================================================

    path = "./{}/com.truthsocial.android/databases/RKStorage".format(foldername)

    if os.path.isfile(path):
        _HASHES["Filename"].append(os.path.basename(path))
        _HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
        
        server = sql(path,"SELECT key,value from catalystLocalStorage where key='server_url' or key='SITE_URL_API_VERSION' or key='AUTH_DATA_KEY'")

        _SERV = {"Key":[], "Value":[]}

        for i in server:
            _SERV["Key"].append(i[0])
            _SERV["Value"].append(i[1])
            
        prnt("RKStorage:",_SERV,2) if prt == 1 else None
    
    #===================================================
    #===================================================
    #===================================================

    if os.path.isfile('./{}/com.truthsocial.android/shared_prefs/rocketUser.xml'.format(foldername)):
        recent = dict(dict(xml_open('./{}/com.truthsocial.android/shared_prefs/rocketUser.xml'.format(foldername)))['map'])['string']
        _HASHES["Filename"].append("rocketUser.xml")
        _HASHES["SHA256"].append(hashlib.sha256(open('./{}/com.truthsocial.android/shared_prefs/rocketUser.xml'.format(foldername),'rb').read()).hexdigest())
        
        _AUTH = {"Name":[],"Value":[]}
        for i in recent:
            _AUTH["Name"].append(dict(i)["@name"])
            _AUTH["Value"].append(dict(i)["#text"])

        prnt("Auth:",_AUTH,2) if prt == 1 else None
    
    #===================================================
    #===================================================
    #===================================================

    if os.path.isfile('./{}/com.truthsocial.android/shared_prefs/io.invertase.firebase.xml'.format(foldername)):
        recent = dict(dict(xml_open('./{}/com.truthsocial.android/shared_prefs/io.invertase.firebase.xml'.format(foldername)))['map'])['string']
        _HASHES["Filename"].append("io.invertase.firebase.xml")
        _HASHES["SHA256"].append(hashlib.sha256(open('./{}/com.truthsocial.android/shared_prefs/io.invertase.firebase.xml'.format(foldername),'rb').read()).hexdigest())
        
        _FEED = {"Name":[],"Value":[]}
        for i in recent:
            _FEED["Name"].append(dict(i)["@name"])
            _FEED["Value"].append(dict(i)["#text"])

        prnt("Feed:",_FEED,2) if prt == 1 else None
    
    #===================================================
    #===================================================
    #===================================================

    if os.path.isfile('./{}/com.truthsocial.android/shared_prefs/com.google.android.gms.measurement.prefs.xml'.format(foldername)):
        recent = dict(dict(xml_open('./{}/com.truthsocial.android/shared_prefs/com.google.android.gms.measurement.prefs.xml'.format(foldername)))['map'])
        #_HASHES["Filename"].append("com.google.android.gms.measurement.prefs.xml")
        #_HASHES["SHA256"].append(hashlib.sha256(open('./{}/com.wimkin.android/shared_prefs/com.google.android.gms.measurement.prefs.xml'.format(foldername),'rb').read()).hexdigest())
        
        _PREF = {"Name":[],"Value":[]}
        l = list(recent.values())
        for i in l:
            for j in i:
                d = dict(j)
                if any(i in d['@name'] for i in ['has_been_opened','first_open_time','last_pause_time','previous_os_version']):
                    _PREF["Name"].append(d['@name'])
                    try:
                        _PREF["Value"].append(d['@value'])
                    except:
                        _PREF["Value"].append(d['#text'])

        #prnt("Prefs:",_PREF,2) if prt == 1 else None
    
    #===================================================
    #===================================================
    #===================================================

    path = "./{}/com.truthsocial.android/chatplus-chat.wimkin.com.db.db".format(foldername)
    
    if os.path.isfile(path):
        _HASHES["Filename"].append(os.path.basename(path))
        _HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
        
        messages = sql(path,"SELECT id, msg, ts, u, attachments, urls from messages")
        rooms = sql(path,"SELECT id, name, usersCount from rooms")
        subs = sql(path,"SELECT id, ts, name, fname, last_message from subscriptions")
            
        _MSG = {"ID":[], "Msg":[], "Timestamp":[], "User":[], "Attachments":[], "URL":[]}
        _ROOM = {"ID":[], "Name":[], "User_Count":[]}
        _SUBS = {"ID":[], "Timestamp":[], "Profile":[], "Name":[], "Last_Message":[]}
        
        for i in messages:
            _MSG["ID"].append(i[0])
            _MSG["Msg"].append(i[1])
            _MSG["Timestamp"].append(i[2])
            _MSG["User"].append(i[3])
            _MSG["Attachments"].append(i[4])
            _MSG["URL"].append(i[5])
            
        for i in rooms:
            _ROOM["ID"].append(i[0])
            _ROOM["Name"].append(i[1])
            _ROOM["User_Count"].append(i[2])

        for i in subs:
            _SUBS["ID"].append(i[0])
            _SUBS["Timestamp"].append(i[1])
            _SUBS["Profile"].append(i[2])
            _SUBS["Name"].append(i[3])
            _SUBS["Last_Message"].append(i[4])
            
        prnt("Messages:",_MSG,6) if prt == 1 else None
        prnt("Rooms:",_ROOM,3) if prt == 1 else None
        prnt("Subscribers:",_SUBS,5) if prt == 1 else None
    
    #===================================================
    #===================================================
    #===================================================
    
    path = glob.glob('./{}/com.truthsocial.android/cache/react-native-image-crop-picker/*.mp4'.format(foldername)) + glob.glob('./{}/com.truthsocial.android/cache/*.m4a'.format(foldername))

    if os.path.isdir('./{}/com.truthsocial.android/cache/react-native-image-crop-picker/*.mp4'.format(foldername)) or os.path.isdir('./{}/com.truthsocial.android/cache/*.m4a'.format(foldername)):
        _FILES = {"Filenames":[],"Location":[]}
        
        for i in path:
            _HASHES["Filename"].append(os.path.basename(i))
            _HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
            _FILES["Filenames"].append(os.path.basename(i))
            _FILES["Location"].append("."+i[len(foldername)+2:])

        prnt("DM Files:",_FILES,1) if prt == 1 else None

    return [_SERV,_AUTH,_FEED,_PREF,_MSG,_ROOM,_SUBS,_FILES,_HASHES]


def wimkin(prt):
	if os.path.isdir('./{}/com.wimkin.android'.format(foldername)):
		print("\nWimkin:\n") if prt == 1 else None

	_SERV,_AUTH,_FEED,_PREF,_MSG,_ROOM,_SUBS,_FILES={},{},{},{},{},{},{},{}
	_HASHES = {"Filename":[],"SHA256":[]}

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/com.wimkin.android/databases/RKStorage".format(foldername)

	if os.path.isfile(path):
		_HASHES["Filename"].append(os.path.basename(path))
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		server = sql(path,"SELECT key,value from catalystLocalStorage where key='server_url' or key='SITE_URL_API_VERSION' or key='AUTH_DATA_KEY'") 

		_SERV = {"Key":[], "Value":[]}

		for i in server:
			_SERV["Key"].append(i[0])
			_SERV["Value"].append(i[1])
			
		prnt("RKStorage:",_SERV,2) if prt == 1 else None
	
	#===================================================
	#===================================================
	#===================================================

	if os.path.isfile('./{}/com.wimkin.android/shared_prefs/rocketUser.xml'.format(foldername)):
		recent = dict(dict(xml_open('./{}/com.wimkin.android/shared_prefs/rocketUser.xml'.format(foldername)))['map'])['string']
		_HASHES["Filename"].append("rocketUser.xml")
		_HASHES["SHA256"].append(hashlib.sha256(open('./{}/com.wimkin.android/shared_prefs/rocketUser.xml'.format(foldername),'rb').read()).hexdigest())
		
		_AUTH = {"Name":[],"Value":[]}
		for i in recent:
			_AUTH["Name"].append(dict(i)["@name"])
			_AUTH["Value"].append(dict(i)["#text"])

		prnt("Auth:",_AUTH,2) if prt == 1 else None
	
	#===================================================
	#===================================================
	#===================================================

	if os.path.isfile('./{}/com.wimkin.android/shared_prefs/io.invertase.firebase.xml'.format(foldername)):
		recent = dict(dict(xml_open('./{}/com.wimkin.android/shared_prefs/io.invertase.firebase.xml'.format(foldername)))['map'])['string']
		_HASHES["Filename"].append("io.invertase.firebase.xml")
		_HASHES["SHA256"].append(hashlib.sha256(open('./{}/com.wimkin.android/shared_prefs/io.invertase.firebase.xml'.format(foldername),'rb').read()).hexdigest())
		
		_FEED = {"Name":[],"Value":[]}
		for i in recent:
			_FEED["Name"].append(dict(i)["@name"])
			_FEED["Value"].append(dict(i)["#text"])

		prnt("Feed:",_FEED,2) if prt == 1 else None
	
	#===================================================
	#===================================================
	#===================================================

	if os.path.isfile('./{}/com.wimkin.android/shared_prefs/com.google.android.gms.measurement.prefs.xml'.format(foldername)):
		recent = dict(dict(xml_open('./{}/com.wimkin.android/shared_prefs/com.google.android.gms.measurement.prefs.xml'.format(foldername)))['map'])
		#_HASHES["Filename"].append("com.google.android.gms.measurement.prefs.xml")
		#_HASHES["SHA256"].append(hashlib.sha256(open('./{}/com.wimkin.android/shared_prefs/com.google.android.gms.measurement.prefs.xml'.format(foldername),'rb').read()).hexdigest())
		
		_PREF = {"Name":[],"Value":[]}
		l = list(recent.values())
		for i in l:
			for j in i:
				d = dict(j)
				if any(i in d['@name'] for i in ['has_been_opened','first_open_time','last_pause_time','previous_os_version']):
					_PREF["Name"].append(d['@name'])
					try:
						_PREF["Value"].append(d['@value'])
					except:
						_PREF["Value"].append(d['#text'])

		#prnt("Prefs:",_PREF,2) if prt == 1 else None
	
	#===================================================
	#===================================================
	#===================================================

	path = "./{}/com.wimkin.android/chatplus-chat.truthsocial.com.db.db".format(foldername)
	
	if os.path.isfile(path):
		_HASHES["Filename"].append(os.path.basename(path))
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		messages = sql(path,"SELECT id, msg, ts, u, attachments, urls from messages")
		rooms = sql(path,"SELECT id, name, usersCount from rooms")
		subs = sql(path,"SELECT id, ts, name, fname, last_message from subscriptions")
			
		_MSG = {"ID":[], "Msg":[], "Timestamp":[], "User":[], "Attachments":[], "URL":[]}
		_ROOM = {"ID":[], "Name":[], "User_Count":[]}
		_SUBS = {"ID":[], "Timestamp":[], "Profile":[], "Name":[], "Last_Message":[]}
		
		for i in messages:
			_MSG["ID"].append(i[0])
			_MSG["Msg"].append(i[1])
			_MSG["Timestamp"].append(i[2])
			_MSG["User"].append(i[3])
			_MSG["Attachments"].append(i[4])
			_MSG["URL"].append(i[5])
			
		for i in rooms:
			_ROOM["ID"].append(i[0])
			_ROOM["Name"].append(i[1])
			_ROOM["User_Count"].append(i[2])

		for i in subs:
			_SUBS["ID"].append(i[0])
			_SUBS["Timestamp"].append(i[1])
			_SUBS["Profile"].append(i[2])
			_SUBS["Name"].append(i[3])
			_SUBS["Last_Message"].append(i[4])
			
		prnt("Messages:",_MSG,6) if prt == 1 else None
		prnt("Rooms:",_ROOM,3) if prt == 1 else None
		prnt("Subscribers:",_SUBS,5) if prt == 1 else None
	
	#===================================================
	#===================================================
	#===================================================
	
	path = glob.glob('./{}/com.wimkin.android/cache/react-native-image-crop-picker/*.mp4'.format(foldername)) + glob.glob('./{}/com.truthsocial.android/cache/*.m4a'.format(foldername))

	if os.path.isdir('./{}/com.wimkin.android/cache/react-native-image-crop-picker/*.mp4'.format(foldername)) or os.path.isdir('./{}/com.wimkin.android/cache/*.m4a'.format(foldername)):
		_FILES = {"Filenames":[],"Location":[]}
		
		for i in path:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES["Filenames"].append(os.path.basename(i))
			_FILES["Location"].append("."+i[len(foldername)+2:])

		prnt("DM Files:",_FILES,1) if prt == 1 else None

	return [_SERV,_AUTH,_FEED,_PREF,_MSG,_ROOM,_SUBS,_FILES,_HASHES]

def clouthub(prt):
	if os.path.isdir('./{}/com.clouthub.clouthub'.format(foldername)):
		print("\nCloutHub:\n") if prt == 1 else None

	_FILES,_SERV,_PARTS={},{},{}
	_HASHES = {"Filename":[],"SHA256":[]}

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/com.clouthub.clouthub/cache/compressor".format(foldername)
	
	if os.path.isdir(path):
		listOfFiles = list()
		for (dirpath, dirnames, filenames) in os.walk(path):
			for file in filenames:
					if "-slack" not in file:
						listOfFiles.append(os.path.join(dirpath, file))

		_FILES = {"Filenames":[],"Location":[]}
		
		for i in listOfFiles:
			_HASHES["Filename"].append(os.path.basename(i))
			_HASHES["SHA256"].append(hashlib.sha256(open(i,'rb').read()).hexdigest())
			_FILES["Filenames"].append(os.path.basename(i))
			_FILES["Location"].append("."+i[len(foldername)+2:])

		prnt("DM Files:",_FILES,1) if prt == 1 else None

	#===================================================
	#===================================================
	#===================================================

	path = "./{}/com.clouthub.clouthub/databases/com.amplitude.api".format(foldername)
	
	if os.path.isfile(path):
		#_HASHES["Filename"].append(os.path.basename(path))
		#_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())
		
		server = sql(path,"SELECT key,value from long_store where key='previous_session_id' or key='last_event_time' UNION SELECT key,value from store")
			
		_SERV = {"Key":[], "Value":[]}

		for i in server:
			_SERV["Key"].append(i[0])
			_SERV["Value"].append(i[1])
			
		#prnt("com.amplitude.api:",_SERV,2) if prt == 1 else None
	
	#===================================================
	#===================================================
	#===================================================

	if os.path.isfile("./{}/com.clouthub.clouthub/shared_prefs/Clouthub.xml".format(foldername)):
		path = dict(dict(xml_open("./{}/com.clouthub.clouthub/shared_prefs/Clouthub.xml".format(foldername)))['map'])
		_HASHES["Filename"].append("Clouthub.xml")
		_HASHES["SHA256"].append(hashlib.sha256(open("./{}/com.clouthub.clouthub/shared_prefs/Clouthub.xml".format(foldername),'rb').read()).hexdigest())
		
		_PARTS = {"Keys":[],"Values":[]}

		for i in path['string']:
			if dict(i)['@name'] == "user_data_key":
				jsn = json.loads(dict(i)['#text'])
				_PARTS["Keys"].append('displayname')
				_PARTS["Values"].append(jsn['displayname']) if jsn['displayname'] else _PARTS["Values"].append("")

				_PARTS["Keys"].append('email')
				_PARTS["Values"].append(jsn['email']) if jsn['email'] else _PARTS["Values"].append("")

				_PARTS["Keys"].append('firstname')
				_PARTS["Values"].append(jsn['firstname']) if jsn['firstname'] else _PARTS["Values"].append("")

				_PARTS["Keys"].append('followerCount')
				_PARTS["Values"].append(jsn['followerCount']) if jsn['followerCount'] else _PARTS["Values"].append("")

				_PARTS["Keys"].append('followingCount')
				_PARTS["Values"].append(jsn['followingCount']) if jsn['followingCount'] else _PARTS["Values"].append("")

				_PARTS["Keys"].append('friendCount')
				_PARTS["Values"].append(jsn['friendCount']) if jsn['friendCount'] else _PARTS["Values"].append("")

				_PARTS["Keys"].append('gender')
				_PARTS["Values"].append(jsn['gender']) if jsn['gender'] else _PARTS["Values"].append("")

				_PARTS["Keys"].append('id')
				_PARTS["Values"].append(jsn['id']) if jsn['id'] else _PARTS["Values"].append("")

				_PARTS["Keys"].append('password')
				_PARTS["Values"].append(jsn['password']) if jsn['password'] else _PARTS["Values"].append("")

				_PARTS["Keys"].append('phoneNo')
				_PARTS["Values"].append(jsn['phoneNo']) if jsn['phoneNo'] else _PARTS["Values"].append("")

				_PARTS["Keys"].append('username')
				_PARTS["Values"].append(jsn['username']) if jsn['username'] else _PARTS["Values"].append("")
			if dict(i)['@name'] == "app_setting__deeplink_weburl_key":
				_PARTS["Keys"].append('app_setting__deeplink_weburl_key')
				_PARTS["Values"].append(dict(i)['#text'])
			
		prnt("User Data:",_PARTS,2) if prt == 1 else None

	return [_FILES,_SERV,_PARTS,_HASHES]

def mewe(prt):
	if os.path.isdir('./{}/com.mewe'.format(foldername)):
		print("\nMeWe:\n") if prt == 1 else None

	_CONTACT,_GROUPS,_POST,_COMMENT,_CHATS,_THREADS,_THREADSPART,_PARTS,_PARTS2={},{},{},{},{},{},{},{},{}
	_HASHES = {"Filename":[],"SHA256":[]}

	#===================================================
	#===================================================
	#===================================================
	
	path = "./{}/com.mewe/databases/app_database".format(foldername)
	
	if os.path.isfile(path):
		_HASHES["Filename"].append(os.path.basename(path))
		_HASHES["SHA256"].append(hashlib.sha256(open(path,'rb').read()).hexdigest())

		contact = sql(path,"SELECT id, userId, name, isCloseFriend FROM CONTACT")
		groups = sql(path,"SELECT GROUP_._id,GROUP_.name,GROUP_.descriptionPlain,COMMUNITY.lastVisit from GROUP_ INNER JOIN COMMUNITY ON GROUP_._id = COMMUNITY.id")
		post = sql(path,"SELECT id, localCreatedAt, groupId, groupName, ownerId, ownerName, textPlain, linkUrl from POST")
		comment = sql(path,"SELECT id, postId, groupId, ownerId, ownerName, createdAt, textPlain from COMMENT")
		chat = sql(path,"SELECT threadId, ownerId, ownerName, currentUserMessage, createdAt, textPlain, attachmentType, attachmentName from CHAT_MESSAGE order by createdAt asc")
		threads = sql(path,"SELECT id, name, startedBy, lastMessageId, participantIds from CHAT_THREAD")
		threads_part = sql(path,"SELECT id, name, chatThreadId from CHAT_THREAD_PARTICIPANT")
		
		_CONTACT = {"ID":[],"User ID":[],"Name":[],"isCloseFriend":[]}
		_GROUPS = {"Group ID":[],"Name":[],"Description":[],"Last Visit":[]}
		_POST = {"ID":[],"localCreatedAt":[],"Group ID":[],"Group Name":[],"Owner ID":[],"Owner Name":[],"Text":[],"Url":[]}
		_COMMENT = {"ID":[],"Post ID":[],"Group ID":[],"Owner ID":[],"Owner Name":[],"createdAt":[],"Text":[]}
		_CHATS = {"Thread ID":[],"User ID":[],"Name":[],"Timestamp (UTC)":[],"Msg":[]}
		_THREADS = {"Thread ID":[],"Creator":[],"Last Sent By":[],"Participants":[]}
		_THREADSPART = {"ID":[],"Name":[],"Chat Thread ID":[]}	

		for i in contact:
			_CONTACT["ID"].append(i[0])
			_CONTACT["User ID"].append(i[1])
			_CONTACT["Name"].append(i[2])
			_CONTACT["isCloseFriend"].append(i[3])

		for i in groups:
			_GROUPS["Group ID"].append(i[0])
			_GROUPS["Name"].append(i[1])
			_GROUPS["Description"].append(i[2])
			_GROUPS["Last Visit"].append(datetime.fromtimestamp(int(i[3])/1000).strftime("%m/%d/%Y-%H:%M:%S"))

		for i in post:
			_POST["ID"].append(i[0])
			_POST["localCreatedAt"].append(i[1])
			_POST["Group ID"].append(i[2])
			_POST["Group Name"].append(i[3])
			_POST["Owner ID"].append(i[4])
			_POST["Owner Name"].append(i[5])
			_POST["Text"].append(i[6])
			_POST["Url"].append(i[7])

		for i in comment:
			_COMMENT["ID"].append(i[0])
			_COMMENT["Post ID"].append(i[1])
			_COMMENT["Group ID"].append(i[2])
			_COMMENT["Owner ID"].append(i[3])
			_COMMENT["Owner Name"].append(i[4])
			_COMMENT["createdAt"].append(i[5])
			_COMMENT["Text"].append(i[6])
		
		for i in chat:
			_CHATS["Thread ID"].append(i[0])
			_CHATS["User ID"].append(i[1])
			_CHATS["Name"].append(i[2])
			_CHATS["Timestamp (UTC)"].append(datetime.fromtimestamp(i[4]).strftime("%m/%d/%Y-%H:%M:%S"))
			if i[6] != "UNSUPPORTED":
				_CHATS["Msg"].append("Attachment: " + i[6] + ":" + i[7])
			else:
				_CHATS["Msg"].append(i[5])

		for i in threads:
			_THREADS["Thread ID"].append(i[0])
			_THREADS["Creator"].append(i[1])
			_THREADS["Last Sent By"].append(i[2])
			_THREADS["Participants"].append(i[3])
			
		for i in threads_part:
			_THREADSPART["ID"].append(i[0])
			_THREADSPART["Name"].append(i[1])
			_THREADSPART["Chat Thread ID"].append(i[2])
		
		prnt("Contact:",_CONTACT,4) if prt == 1 else None
		prnt("Groups:",_GROUPS,4) if prt == 1 else None
		prnt("Post:",_POST,8) if prt == 1 else None
		prnt("Comment:",_COMMENT,7) if prt == 1 else None
		prnt("Chats:",_CHATS,5) if prt == 1 else None
		prnt("Threads:",_THREADS,4) if prt == 1 else None
		prnt("Thread Participant:",_THREADSPART,3) if prt == 1 else None
	
	#===================================================
	#===================================================
	#===================================================
	
	if os.path.isfile("./{}/com.mewe/shared_prefs/SGSession.xml".format(foldername)):
		path = dict(dict(xml_open("./{}/com.mewe/shared_prefs/SGSession.xml".format(foldername)))['map'])
		_HASHES["Filename"].append("SGSession.xml")
		_HASHES["SHA256"].append(hashlib.sha256(open("./{}/com.mewe/shared_prefs/SGSession.xml".format(foldername),'rb').read()).hexdigest())
		
		_PARTS = {"Keys":[],"Values":[]}

		for i in path['string']:
			if dict(i)['@name'] == "user_info":
				jsn = json.loads(dict(i)['#text'])
				_PARTS["Keys"].append('firstName')
				_PARTS["Values"].append(jsn['firstName']) if jsn['firstName'] else _PARTS["Values"].append("")
				_PARTS["Keys"].append('id')
				_PARTS["Values"].append(jsn['id']) if jsn['id'] else _PARTS["Values"].append("")
				_PARTS["Keys"].append('lastName')
				_PARTS["Values"].append(jsn['lastName']) if jsn['lastName'] else _PARTS["Values"].append("")
				_PARTS["Keys"].append('phone')
				_PARTS["Values"].append(jsn['phone']) if jsn['phone'] else _PARTS["Values"].append("")
				_PARTS["Keys"].append('primaryPhoneNumber')
				_PARTS["Values"].append(jsn['primaryPhoneNumber']) if 'primaryPhoneNumber' in jsn else _PARTS["Values"].append("None")
				_PARTS["Keys"].append('primaryEmail')
				_PARTS["Values"].append(jsn['primaryEmail']) if 'primaryEmail' in jsn else _PARTS["Values"].append("None")

		prnt("SGSession.xml:",_PARTS,2) if prt == 1 else None
	
	#===================================================
	#===================================================
	#===================================================
	
	if os.path.isfile("./{}/com.mewe/shared_prefs/AppSession.xml".format(foldername)):
		path = dict(dict(xml_open("./{}/com.mewe/shared_prefs/AppSession.xml".format(foldername)))['map'])
		#_HASHES["Filename"].append("AppSession.xml")
		#_HASHES["SHA256"].append(hashlib.sha256(open("./{}/com.mewe/shared_prefs/SGSession.xml".format(foldername),'rb').read()).hexdigest())
		
		_PARTS2 = {"Keys":[],"Values":[]}

		for i in path['string']:
			_PARTS2["Keys"].append(dict(i)["@name"])
			_PARTS2["Values"].append(dict(i)["#text"]) if dict(i)["#text"] else _PARTS["Values"].append("")
				
		#prnt("AppSession.xml",_PARTS2,2) if prt == 1 else None

	return [_CONTACT,_GROUPS,_POST,_COMMENT,_CHATS,_THREADS,_THREADSPART,_PARTS,_PARTS2,_HASHES]

def match(path):
			f_url = os.path.basename(path)
			return '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>'.format(path, f_url)

def report(gettr_,safechat_,mindschat_,mindsmobile_,truthsocial_,wimkin_,clouthub_,mewe_):									#Generates report with parsed data
	copyfile('./style.css', './{}/style.css'.format(foldername))
	f = open("./{}/report.html".format(foldername),"w",encoding='utf-8')
	f.write("<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport'><title>Android</title>\
		     <link href='style.css' rel='stylesheet' type='text/css' /></head><body><h1>Android Forensics Report</h1>\
		     <div style='margin-left:auto;margin-right:auto;width:800px;height:285px;border:2px solid #000;'><h3>\
		     Filename: {}<br>Case: {}<br>Timestamp: {}<br>Examiner: {}<br>Image Size: {}<br>Extraction Time: {}<br>Before Analysis:<br>MD5: {}<br>SHA256: {}<br>After Analysis:<br>MD5: {}<br>SHA256: {}</h3></div>".format(foldername,case,timestamp,examiner,image_size,extraction_time,md5,sha256,check_md5,check_sha256))
	
	
	f.write('''<div class="tab">''')
	f.write('''<button class="tablinks" onclick="apptabs(event, 'Gettr')" id="defaultOpen">Gettr</button>''')
	f.write('''<button class="tablinks" onclick="apptabs(event, 'SafeChat')">SafeChat</button>''')
	f.write('''<button class="tablinks" onclick="apptabs(event, 'MindsChat')">Minds Chat</button>''')
	f.write('''<button class="tablinks" onclick="apptabs(event, 'MindsMobile')">Minds Mobile</button>''')
     f.write('''<button class="tablinks" onclick="apptabs(event, 'TruthSocial')">Truth Social</button>''')
	f.write('''<button class="tablinks" onclick="apptabs(event, 'Wimkin')">Wimkin</button>''')
	f.write('''<button class="tablinks" onclick="apptabs(event, 'CloutHub')">CloutHub</button>''')
	f.write('''<button class="tablinks" onclick="apptabs(event, 'MeWe')">MeWe</button>''')
	f.write('''</div>''')

	
	f.write('''<div id="Gettr" class="tabcontent">''')
	
	if not gettr_[0]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">LibCachedImageData.db</a></h2>\n'''.format(os.path.abspath("./{}/com.gettr.gettr/files/LibCachedImageData.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(gettr_[0])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not gettr_[1]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">g.db</a></h2>\n'''.format(os.path.abspath("./{}/com.gettr.gettr/databases/g.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(gettr_[1])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not gettr_[2]:
		pass
	else:
		file = os.path.basename(glob.glob("./{}/com.gettr.gettr/databases/private_*.db".format(foldername))[0])
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">{}</a></h2>\n'''.format(os.path.abspath("./{}/com.gettr.gettr/databases/{}".format(foldername,file)),file))
		df1 = pd.DataFrame.from_dict(gettr_[2])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not gettr_[3]:
		pass
	else:
		f.write("<h2>GIF's</h2>\n")
		gettr_[3].pop("Filenames")
		df1 = pd.DataFrame.from_dict(gettr_[3])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not gettr_[4]:
		pass
	else:
		if 'recent_gif_ids' in gettr_[4]['Key'] and 'recent_searches' in gettr_[4]['Key']:
			f.write('''<h2><a href='xml-open:{}' target="_blank" rel="noopener noreferrer">giphy_recents_file.xml</a> & <a href='xml-open:{}' target="_blank" rel="noopener noreferrer">giphy_searches_file.xml</a></h2>\n'''.format(os.path.abspath("./{}/com.gettr.gettr/shared_prefs/giphy_recents_file.xml".format(foldername)),os.path.abspath("./{}/com.gettr.gettr/shared_prefs/giphy_searches_file.xml".format(foldername))))
		elif 'recent_gif_ids' in gettr_[4]['Key'] and 'recent_searches' not in gettr_[4]['Key']:
			f.write('''<h2><a href='xml-open:{}' target="_blank" rel="noopener noreferrer">giphy_recents_file.xml</a></h2>\n'''.format(os.path.abspath("./{}/com.gettr.gettr/shared_prefs/giphy_recents_file.xml".format(foldername))))
		elif 'recent_searches' in gettr_[4]['Key'] and 'recent_gif_ids' not in gettr_[4]['Key']: 
			f.write('''<h2><a href='xml-open:{}' target="_blank" rel="noopener noreferrer">giphy_searches_file.xml</a></h2>\n'''.format(os.path.abspath("./{}/com.gettr.gettr/shared_prefs/giphy_searches_file.xml".format(foldername))))
		
		df1 = pd.DataFrame.from_dict(gettr_[4])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not gettr_[5]["Filename"]:
		pass
	else:
		f.write("<h2>Hash Table</h2>\n")
		df1 = pd.DataFrame.from_dict(gettr_[5])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	f.write('''</div>''')
	f.write('''<div id="SafeChat" class="tabcontent">''')
	
	if not safechat_[0]:
		pass
	else:
		f.write("<h2>MP4's</h2>\n")
		safechat_[0].pop("Filenames")
		df1 = pd.DataFrame.from_dict(safechat_[0])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not safechat_[1]:
		pass
	else:
		f.write("<h2>ACC's</h2>\n")
		safechat_[1].pop("Filenames")
		df1 = pd.DataFrame.from_dict(safechat_[1])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not safechat_[2]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">SafeChat.db</a> - Channels</h2>\n'''.format(os.path.abspath("./{}/net.safechat.app/databases/SafeChat.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(safechat_[2])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not safechat_[3]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">SafeChat.db</a> - Conversations</h2>\n'''.format(os.path.abspath("./{}/net.safechat.app/databases/SafeChat.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(safechat_[3])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not safechat_[4]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">SafeChat.db</a> - Messages</h2>\n'''.format(os.path.abspath("./{}/net.safechat.app/databases/SafeChat.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(safechat_[4])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not safechat_[5]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">SafeChat.db</a> - Users</h2>\n'''.format(os.path.abspath("./{}/net.safechat.app/databases/SafeChat.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(safechat_[5])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not safechat_[6]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">download_tasks.db</a> - Tasks</h2>\n'''.format(os.path.abspath("./{}/net.safechat.app/databases/download_tasks.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(safechat_[6])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not safechat_[7]["Filename"]:
		pass
	else:
		f.write("<h2>Hash Table</h2>\n")
		df1 = pd.DataFrame.from_dict(safechat_[7])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	f.write('''</div>''')

	f.write('''<div id="MindsChat" class="tabcontent">''')
	
	if not mindschat_[0]:
		pass
	else:
		f.write("<h2>Direct Message Files</h2>\n")
		mindschat_[0].pop("Filenames")
		df1 = pd.DataFrame.from_dict(mindschat_[0])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	#if not mindschat_[1]:
	#	pass
	#else:
	#	f.write('''<h2><a href='xml-open:{}' target="_blank" rel="noopener noreferrer">im.vector.matrix.android.keys.xml</a></h2>\n'''.format(os.path.abspath("./{}/com.minds.chat/shared_prefs/im.vector.matrix.android.keys.xml".format(foldername))))
	#	df1 = pd.DataFrame.from_dict(mindschat_[1])
	#	df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
	#	df1 = df1.replace("T_t03","t03")
	#	f.write(df1)

	if not mindschat_[2]:
		pass
	else:
		f.write('''<h2><a href='xml-open:{}' target="_blank" rel="noopener noreferrer">emoji-recent-manager.xml</a></h2>\n'''.format(os.path.abspath("./{}/com.minds.chat/shared_prefs/emoji-recent-manager.xml".format(foldername))))
		df1 = pd.DataFrame.from_dict(mindschat_[2])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mindschat_[3]["Filename"]:
		pass
	else:
		f.write("<h2>Hash Table</h2>\n")
		df1 = pd.DataFrame.from_dict(mindschat_[3])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)
	f.write('''</div>''')
	
	f.write('''<div id="MindsMobile" class="tabcontent">''')
	if not mindsmobile_[0]:
		pass
	else:
		f.write("<h2>Direct Message Files</h2>\n")
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
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">RKStorage</a> - User</h2>\n'''.format(os.path.abspath("./{}/com.minds.mobile/databases/RKStorage".format(foldername))))
		df1 = pd.DataFrame.from_dict(mindsmobile_[1])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mindsmobile_[2]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">minds1.db</a> - Comments</h2>\n'''.format(os.path.abspath("./{}/com.minds.mobile/databases/minds1.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(mindsmobile_[2])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mindsmobile_[3]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">minds1.db</a> - Feeds</h2>\n'''.format(os.path.abspath("./{}/com.minds.mobile/databases/minds1.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(mindsmobile_[3])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mindsmobile_[4]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">minds1.db</a> - Entities</h2>\n'''.format(os.path.abspath("./{}/com.minds.mobile/databases/minds1.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(mindsmobile_[4])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
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

    f.write('''<div id="Truth Social" class="tabcontent">''')
    if not truthsocial_[0]:
        pass
    else:
        f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">RKStorage</a></h2>\n'''.format(os.path.abspath("./{}/com.truthsocial.android/databases/RKStorage".format(foldername))))
        df1 = pd.DataFrame.from_dict(truthsocial_[0])
        df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
        df1 = df1.replace("T_t03","t03")
        f.write(df1)

    if not truthsocial_[1]:
        pass
    else:
        f.write('''<h2><a href='xml-open:{}' target="_blank" rel="noopener noreferrer">rocketUser.xml</a></h2>\n'''.format(os.path.abspath("./{}/com.truthsocial.android/shared_prefs/rocketUser.xml".format(foldername))))
        df1 = pd.DataFrame.from_dict(wimkin_[1])
        df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
        df1 = df1.replace("T_t03","t03")
        f.write(df1)

    if not truthsocial_[2]:
        pass
    else:
        f.write('''<h2><a href='xml-open:{}' target="_blank" rel="noopener noreferrer">io.invertase.firebase.xml</a></h2>\n'''.format(os.path.abspath("./{}/com.truthsocial.android/shared_prefs/io.invertase.firebase.xml".format(foldername))))
        df1 = pd.DataFrame.from_dict(truthsocial_[2])
        df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
        df1 = df1.replace("T_t03","t03")
        f.write(df1)

    #if not truthsocial_[3]:
    #    pass
    #else:
    #    f.write('''<h2><a href='xml-open:{}' target="_blank" rel="noopener noreferrer">com.google.android.gms.measurement.prefs.xml</a></h2>\n'''.format(os.path.abspath("./{}/com.truthsocial.android/shared_prefs/com.google.android.gms.measurement.prefs.xml".format(foldername))))
    #    df1 = pd.DataFrame.from_dict(truthsocial_[3])
    #    df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
    #    df1 = df1.replace("T_t03","t03")
    #    f.write(df1)

    if not truthsocial_[4]:
        pass
    else:
        f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">chatplus-chat.truthsocial.com.db.db</a> - Subscribers</h2>\n'''.format(os.path.abspath("./{}/com.wimkin.android/chatplus-chat.truthsocial.com.db.db".format(foldername))))
        df1 = pd.DataFrame.from_dict(truthsocial_[4])
        df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
        df1 = df1.replace("T_t03","t03")
        f.write(df1)

    if not truthsocial_[5]:
        pass
    else:
        f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">chatplus-chat.truthsocial.com.db.db</a> - Rooms</h2>\n'''.format(os.path.abspath("./{}/com.wimkin.android/chatplus-chat.wimkin.com.db.db".format(foldername))))
        df1 = pd.DataFrame.from_dict(truthsocial_[5])
        df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
        df1 = df1.replace("T_t03","t03")
        f.write(df1)

    if not truthsocial_[6]:
        pass
    else:
        f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">chatplus-chat.truthsocial.com.db.db</a> - Messages</h2>\n'''.format(os.path.abspath("./{}/com.truthsocial.android/chatplus-chat.truthsocial.com.db.db".format(foldername))))
        df1 = pd.DataFrame.from_dict(truthsocial_[6])
        df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
        df1 = df1.replace("T_t03","t03")
        f.write(df1)

    if not truthsocial_[7]:
        pass
    else:
        f.write("<h2>Direct Message Files</h2>\n")
        wimkin_[7].pop("Filenames")
        df1 = pd.DataFrame.from_dict(truthsocial_[7])
        df1 = df1.rename(columns={"Location":"Filenames"})
        df1 = df1.style.format({"Filenames":match})
        df1 = df1.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
        df1 = df1.replace("T_t03","t03")
        f.write(df1)

    if not truthsocial_[8]["Filename"]:
        pass
    else:
        f.write("<h2>Hash Table</h2>\n")
        df1 = pd.DataFrame.from_dict(truthsocial_[8])
        df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
        df1 = df1.replace("T_t03","t03")
        f.write(df1)
    f.write('''</div>''')

	f.write('''<div id="Wimkin" class="tabcontent">''')
	if not wimkin_[0]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">RKStorage</a></h2>\n'''.format(os.path.abspath("./{}/com.wimkin.android/databases/RKStorage".format(foldername))))
		df1 = pd.DataFrame.from_dict(wimkin_[0])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not wimkin_[1]:
		pass
	else:
		f.write('''<h2><a href='xml-open:{}' target="_blank" rel="noopener noreferrer">rocketUser.xml</a></h2>\n'''.format(os.path.abspath("./{}/com.wimkin.android/shared_prefs/rocketUser.xml".format(foldername))))
		df1 = pd.DataFrame.from_dict(wimkin_[1])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not wimkin_[2]:
		pass
	else:
		f.write('''<h2><a href='xml-open:{}' target="_blank" rel="noopener noreferrer">io.invertase.firebase.xml</a></h2>\n'''.format(os.path.abspath("./{}/com.wimkin.android/shared_prefs/io.invertase.firebase.xml".format(foldername))))
		df1 = pd.DataFrame.from_dict(wimkin_[2])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	#if not wimkin_[3]:
	#	pass
	#else:
	#	f.write('''<h2><a href='xml-open:{}' target="_blank" rel="noopener noreferrer">com.google.android.gms.measurement.prefs.xml</a></h2>\n'''.format(os.path.abspath("./{}/com.wimkin.android/shared_prefs/com.google.android.gms.measurement.prefs.xml".format(foldername))))
	#	df1 = pd.DataFrame.from_dict(wimkin_[3])
	#	df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
	#	df1 = df1.replace("T_t03","t03")
	#	f.write(df1)

	if not wimkin_[4]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">chatplus-chat.wimkin.com.db.db</a> - Subscribers</h2>\n'''.format(os.path.abspath("./{}/com.wimkin.android/chatplus-chat.wimkin.com.db.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(wimkin_[4])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not wimkin_[5]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">chatplus-chat.wimkin.com.db.db</a> - Rooms</h2>\n'''.format(os.path.abspath("./{}/com.wimkin.android/chatplus-chat.wimkin.com.db.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(wimkin_[5])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not wimkin_[6]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">chatplus-chat.wimkin.com.db.db</a> - Messages</h2>\n'''.format(os.path.abspath("./{}/com.wimkin.android/chatplus-chat.wimkin.com.db.db".format(foldername))))
		df1 = pd.DataFrame.from_dict(wimkin_[6])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not wimkin_[7]:
		pass
	else:
		f.write("<h2>Direct Message Files</h2>\n")
		wimkin_[7].pop("Filenames")
		df1 = pd.DataFrame.from_dict(wimkin_[7])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not wimkin_[8]["Filename"]:
		pass
	else:
		f.write("<h2>Hash Table</h2>\n")
		df1 = pd.DataFrame.from_dict(wimkin_[8])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)
	f.write('''</div>''')
    
	f.write('''<div id="CloutHub" class="tabcontent">''')
	
	if not clouthub_[0]:
		pass
	else:
		f.write("<h2>Direct Message Files</h2>\n")
		clouthub_[0].pop("Filenames")
		df1 = pd.DataFrame.from_dict(clouthub_[0])
		df1 = df1.rename(columns={"Location":"Filenames"})
		df1 = df1.style.format({"Filenames":match})
		df1 = df1.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	#if not clouthub_[1]:
	#	pass
	#else:
	#	f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">com.amplitude.api</a></h2>\n'''.format(os.path.abspath("./{}/com.clouthub.clouthub/databases/com.amplitude.api".format(foldername))))
	#	df1 = pd.DataFrame.from_dict(clouthub_[1])
	#	df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
	#	df1 = df1.replace("T_t03","t03")
	#	f.write(df1)

	if not clouthub_[2]:
		pass
	else:
		f.write('''<h2><a href='xml-open:{}' target="_blank" rel="noopener noreferrer">Clouthub.xml</a></h2>\n'''.format(os.path.abspath("./{}/com.clouthub.clouthub/shared_prefs/Clouthub.xml".format(foldername))))
		df1 = pd.DataFrame.from_dict(clouthub_[2])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not clouthub_[3]["Filename"]:
		pass
	else:
		f.write("<h2>Hash Table</h2>\n")
		df1 = pd.DataFrame.from_dict(clouthub_[3])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)
	f.write('''</div>''')
	
	f.write('''<div id="MeWe" class="tabcontent">''')
	if not mewe_[0]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">app_database</a> - Contact</h2>\n'''.format(os.path.abspath("./{}/com.mewe/databases/app_database".format(foldername))))
		df1 = pd.DataFrame.from_dict(mewe_[0])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mewe_[1]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">app_database</a> - Groups</h2>\n'''.format(os.path.abspath("./{}/com.mewe/databases/app_database".format(foldername))))
		df1 = pd.DataFrame.from_dict(mewe_[1])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mewe_[2]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">app_database</a> - Post</h2>\n'''.format(os.path.abspath("./{}/com.mewe/databases/app_database".format(foldername))))
		df1 = pd.DataFrame.from_dict(mewe_[2])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mewe_[3]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">app_database</a> - Comment</h2>\n'''.format(os.path.abspath("./{}/com.mewe/databases/app_database".format(foldername))))
		df1 = pd.DataFrame.from_dict(mewe_[3])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mewe_[4]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">app_database</a> - Contact</h2>\n'''.format(os.path.abspath("./{}/com.mewe/databases/app_database".format(foldername))))
		f.write("<h2>app_database - Chat</h2>\n")
		df1 = pd.DataFrame.from_dict(mewe_[4])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mewe_[5]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">app_database</a> - Threads</h2>\n'''.format(os.path.abspath("./{}/com.mewe/databases/app_database".format(foldername))))
		df1 = pd.DataFrame.from_dict(mewe_[5])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mewe_[6]:
		pass
	else:
		f.write('''<h2><a href='db-open:{}' target="_blank" rel="noopener noreferrer">app_database</a> - Thread Participant</h2>\n'''.format(os.path.abspath("./{}/com.mewe/databases/app_database".format(foldername))))
		df1 = pd.DataFrame.from_dict(mewe_[6])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	if not mewe_[7]:
		pass
	else:
		f.write('''<h2><a href='xml-open:{}' target="_blank" rel="noopener noreferrer">SGSession.xml</a></h2>\n'''.format(os.path.abspath("./{}/com.mewe/shared_prefs/SGSession.xml".format(foldername))))
		df1 = pd.DataFrame.from_dict(mewe_[7])
		df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
		df1 = df1.replace("T_t03","t03")
		f.write(df1)

	#if not mewe_[8]:
	#	pass
	#else:
	#	f.write('''<h2><a href='xml-open:{}' target="_blank" rel="noopener noreferrer">AppSession.xml</a></h2>\n'''.format(os.path.abspath("./{}/com.mewe/shared_prefs/AppSession.xml".format(foldername))))
	#	df1 = pd.DataFrame.from_dict(mewe_[8])
	#	df1 = df1.style.set_properties(**{'text-align': 'center'},**{'overflow-x':'auto'},**{'max-width':'800px'}).set_table_attributes('class="center"').hide(axis='index').to_html(uuid='t03')
	#	df1 = df1.replace("T_t03","t03")
	#	f.write(df1)

	if not mewe_[9]["Filename"]:
		pass
	else:
		f.write("<h2>Hash Table</h2>\n")
		df1 = pd.DataFrame.from_dict(mewe_[9])
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
	foldername = case+"-Android"
	examiner = input("Enter examiner name:")
	image_size = size(os.path.getsize(file))
	md5 = hashlib.md5(open(file,'rb').read()).hexdigest()
	print("MD5:",md5)
	sha256 = hashlib.sha256(open(file,'rb').read()).hexdigest()
	print("SHA256:",sha256)

def hash_check(file):											#Re-hashes tar file to check integrity
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

	conv = {'com.gettr.gettr':0,'net.safechat.app':0,'com.minds.chat':0,'com.minds.mobile':0,'com.truthsocial.android':0,'com.wimkin.android':0,'com.clouthub.clouthub':0,'com.mewe':0}
	
	selectedApps = select(installedApps)
	
	for i in selectedApps:
		conv[i] = 1

	return list(conv.values())

def android(file):
	setup(file)
	extract(file)
	prt = selection()
	gettr_ = gettr(prt[0])
	safechat_ = safechat(prt[1])
	mindschat_ = minds_chat(prt[2])
	mindsmobile_ = minds_mobile(prt[3])
    truthsocial_ = truth_social(prt[4])
	wimkin_ = wimkin(prt[5])
	clouthub_ = clouthub(prt[6])
	mewe_ = mewe(prt[7])
	hash_check(file)
	report(gettr_,safechat_,mindschat_,mindsmobile_,truthsocial_,wimkin_,clouthub_,mewe_)
