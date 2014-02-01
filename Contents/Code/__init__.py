# -*- coding: latin-1 -*-

ICON  = 'icon-default.png'

# Plugin parameters
PLUGIN_TITLE		= "Illico Web"
PLUGIN_PREFIX   	= "/video/illicoweb"
BASE_URL = "http://illicoweb.videotron.com/"
API_URL = "https://illicoweb.videotron.com/illicoservice/"
LOGO_URL = 'http://static-illicoweb.videotron.com/illicoweb/static/webtv/images/logos/'
ART_URL = "http://static-illicoweb.videotron.com/illicoweb/static/webtv/images/content/custom/"
DEFAULT_ART_URL = 'http://static-illicoweb.videotron.com/illicoweb/static/webtv/images/content/custom/presse1.jpg'
LOGGEDIN                                        = False
sessionid                                        = ''



MONTHS = [{"french" : "janvier", "english": "January"},{"french" : u"fÃ©vrier", "english": "February"},{"french" : "mars", "english": "March"},
	{"french" : "avril", "english": "April"},{"french" : "mai", "english": "May"},{"french" : "juin", "english": "June"},
	{"french" : "juillet", "english": "July"},{"french" : u"aoÃ»t", "english": "August"},{"french" : "septembre", "english": "September"},
	{"french" : "octobre", "english": "October"},{"french" : "novembre", "english": "November"},{"french" : u"dÃ©cembre", "english": "December"}]

####################################################################################################

def ValidatePrefs():
        global LOGGEDIN, sessionid
        u = Prefs['username']
        p = Prefs['password']
        if( u and p ):
			LOGGEDIN = Login()
			if LOGGEDIN == False:
				return MessageContainer(
					"Erreur",
					"Accès refusé"
				)
		else:
			return MessageContainer(
				"Erreur",
				"Entrez votre nom d'utilisateur et votre mot de passe"
			)



####################################################################################################

def Start():
	#Set handler
	Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE)
	
	# Set the default ObjectContainer attributes
	ObjectContainer.title1    = PLUGIN_TITLE
	DirectoryObject.thumb = R(ICON)

	# Set the default cache time
	HTTP.CacheTime = 1800
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0'
	HTTP.Headers['Referer'] = 'https://illicoweb.videotron.com/accueil'
	
	


###################################################################################################

def MainMenu():
	global LOGGEDIN, sessionid
	oc = ObjectContainer()        
	
	httpCookies=HTTP.GetCookiesForURL(BASE_URL)
	
	url=API_URL +'channels/user?localeLang=fr'
	obj=JSON.ObjectFromURL(url)
	
	if obj['head']['clubIllicoStatus'] == "NOT_CONNECTED":
		LOGGEDIN = Login()
		Log(" --> FROM MAIN1! %s SSID='%s'" % (LOGGEDIN,httpCookies))
	else 
		LOGGEDIN = True		
			
	Log(" --> FROM MAIN! %s SSID='%s'" % (LOGGEDIN,sessionid))
	
	if LOGGEDIN == True:
		urlChannels = API_URL+'channels/user?localeLang=fr'
		objChannels = JSON.ObjectFromURL(url)
		channels = objChannels['body']['main']
		
		for channel in channels:
			title = channel['name']
			try:
				thumb = LOGO_URL + channel['image']
			except:
				thumb = None
			art = DEFAULT_ART_URL
			oc.add(DirectoryObject(key=Callback(Channel, channel=channel, title=title), title = title, thumb = thumb, art = art ))
		

    oc.add(PrefsObject(title = 'Login'))
	
	return oc


####################################################################################################

def Channel(channel,title):
	oc = ObjectContainer(title2 = title)
	url = "url?logicalUrl="+channel['link']['uri']
	obj = JSON.ObjectFromURL(API_URL+url)
	
	provider = obj['body']['main']['provider']
	try:
		thumb = LOGO_URL + provider['image']
	except:
		thumb = None
	try:
		art = ART_URL + obj['body']['main'][0]['backgroundURL']
	except:
		art = DEFAULT_ART_URL
		
		
	sections = obj['body']['main']['sections']
	try:
		live = provider['orderURI']
		
	if live :
		oc.add(DirectoryObject(key=Callback(liveStream, live), title = "En Direct", thumb = thumb, art = art ))
	

    for menu in sections:
		if 'widgetType' in menu:
			if menu['widgetType'] == 'MENU':
				url = menu['contentDownloadURL']
				oc.add(DirectoryObject(key=Callback(getMenu, url), title = "Toutes les émissions", thumb = thumb, art = art ))
			if menu['widgetType'] == "BASIC"
				url = menu['contentDownloadURL']
				menutitle =  menu['titleLabel']['text']
				oc.add(DirectoryObject(key=Callback(getMenu, url), title = menutitle, thumb = thumb, art = art ))
				
	return oc
		

####################################################################################################

def TranslateDate(date):
	for month in MONTHS:
		date = date.replace(month['french'], month['english'])
	return Datetime.ParseDate(date).date()

####################################################################################################

def Login():
	global LOGGEDIN, sessionid
	if LOGGEDIN == True:
		return True
	elif not Prefs['username'] and not Prefs['password']:
		return False
	else:
		values = {
			'username' : Prefs['username'],
			'password' : Prefs['password']
		}
		url = API_URL+'authenticate?localLang=fr&password='+Prefs['password']+'&userId='+Prefs['username']'     
			 
		try:
			obj = JSON.ObjectFromURL(url, values=values, encoding='utf-8', cacheTime=1)
		except:
			obj=[]
			Log("----> Someting Bad'%s'" % (values))
			LOGGEDIN = False
			return False        
   
		if len(obj['body']['main']['sessionId']) > 0:
			sessionid = obj['body']['main']['sessionId']
			LOGGEDIN = True
			Log(" --> Login successful! %s SSID='%s'" % (LOGGEDIN,sessionid))
			return True
		else:
			LOGGEDIN = False
			Log(' --> Username/password incorrect!')
			return False
