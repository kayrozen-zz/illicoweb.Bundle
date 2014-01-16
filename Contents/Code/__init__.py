# -*- coding: latin-1 -*-

#Regex
RE_EP_NUM         = Regex('Épisode ([0-9]+)')

# Plugin parameters
PLUGIN_TITLE		= "Illico Web"
PLUGIN_PREFIX   	= "/video/illicoweb"
BASE_URL = "http://illicoweb.videotron.com/"
API_URL = "https://illicoweb.videotron.com/illicoservice/"
LOGGEDIN                                        = False
sessionid                                        = ''



MONTHS = [{"french" : "janvier", "english": "January"},{"french" : u"février", "english": "February"},{"french" : "mars", "english": "March"},
	{"french" : "avril", "english": "April"},{"french" : "mai", "english": "May"},{"french" : "juin", "english": "June"},
	{"french" : "juillet", "english": "July"},{"french" : u"août", "english": "August"},{"french" : "septembre", "english": "September"},
	{"french" : "octobre", "english": "October"},{"french" : "novembre", "english": "November"},{"french" : u"décembre", "english": "December"}]

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
	
	if obj['head']['clubIllicoStatus'] == "NOT_CONNECTED"
		LOGGEDIN = Login()
		Log(" --> FROM MAIN1! %s SSID='%s'" % (LOGGEDIN,httpCookies))
	else 
		LOGGEDIN = True		
			
	Log(" --> FROM MAIN! %s SSID='%s'" % (LOGGEDIN,sessionid))
	
	if LOGGEDIN == True:
		oc.add(DirectoryObject(key=Callback(BrowseChannels), title="Canaux Télé"))

    oc.add(PrefsObject(title = 'Login'))
	
	return oc

####################################################################################################

def BrowseChannels():
	

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
			#initiate = HTTP.Request(BASE_URL+'/login/', encoding='iso-8859-1', cacheTime=1)
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
