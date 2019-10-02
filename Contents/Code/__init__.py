# -*- coding: utf-8 -*-
import re,urllib2,base64
import calendar
from datetime import *
import time
#, translit, urllib
# Nice TV Plugin
VERSION						= 3.6
VIDEO_PREFIX				= "/video/nicetv"
NAME						= 'nicetv'
ART							= 'art-default.jpg'
ICON						= 'icon-default.png'
PREFS						= 'icon-prefs.png'
API_URL						= ''
BASE_URL					= ''
USER_AGENT					= 'User-Agent','PLEX NiceTV plugin (Macintosh; U; Intel Mac OS X 10.6; en; rv:1.9.2.13) Nice'
LOGGEDIN					= False
SID							= ''
title1						= NAME
title2						= ''

def Start():

	Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	MediaContainer.title1 = title1
	MediaContainer.title2 = title2
	MediaContainer.viewGroup = "List"
	MediaContainer.art = R(ART)
	DirectoryItem.thumb = R(ICON)
	VideoItem.thumb = R(ICON)
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent']=USER_AGENT #'Mozilla/5.0 [Macintosh; U; Intel Mac OS X 10.6; ru; rv:1.9.2.13] Gecko/20101203 Firefox/3.6.13 GTB7.1'
	HTTP.Headers['Accept']='text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
	HTTP.Headers['Accept-Encoding']='gzip,deflate,sdch'
	HTTP.Headers['Accept-Language']='en-us;q=0.5,en;q=0.3'
	HTTP.Headers['Accept-Charset']='windows-1251,utf-8;q=0.7,*;q=0.7'
	HTTP.Headers['Keep-Alive']='115'
	HTTP.Headers['Referer']='http://'+Prefs['portal']+'/'

def MainMenu():
	global LOGGEDIN, SID ,API_URL ,BASE_URL
	API_URL						= 'http://'+Prefs['portal']+'/api/json/'
	BASE_URL					= 'http://'+Prefs['portal']+'/api/json/'		
	httpCookies=HTTP.GetCookiesForURL(BASE_URL)
	SID=Dict['sessionid']
	dir = MediaContainer(viewGroup="List", noCache=True, httpCookies=httpCookies)	
	DoLogin()
	if SID != "":
		dir.Append(Function(DirectoryItem(Channels, title='TV', thumb=R('tv-icon.png')), link='channel_list', id=0))

	dir.Append(PrefsItem('Settings ', thumb=R('settings.png')))
	dir.Append(Function(DirectoryItem(About, title='Info', thumb=R('info.png'))))
	
	return dir
	
def Channels(sender,link,id=0):
	url=API_URL + 'channel_list?MW_SSID='+Dict['sessionid']
	dir = MediaContainer(viewGroup='InfoList', httpCookies=HTTP.GetCookiesForURL(BASE_URL),title2='<')
	obj = JSON.ObjectFromURL(url)
	if obj.has_key('error'):
		msg=obj["error"]["message"]
		Dict['sessionid']=""
		return MessageContainer("Error", msg)
	else:
		msg=""
	if id==0:						
		for group in obj["groups"]:
			name=group["name"]
			gid=group["id"]				
			dir.Append(Function(DirectoryItem(Channels, title=name,thumb=R('group_'+str(gid)+'.png')), link='channel_list', id=gid))
	else:

		for group in obj["groups"]:
			if group["id"]==id:
				for chan in group["channels"]:
					cid=chan["id"]	
					name=chan["name"]
					#Log("------> Channel ID=%s, POSTER=%s" % (cid,poster))
					#thumb='http://img/'+str(cid)+'.gif'			
					#dir.Append(Function(DirectoryItem(EPG, title=name, summary=name, thumb=R('art-default.jpg')), id=cid, page=1))
					dir.Append(Function(DirectoryItem(PlayCh, title=name, subtitle=name, summary=''), name = name, id=cid))
					
					
        return dir
	
@route(VIDEO_PREFIX + '/createvideoclipobject', include_container = bool)
def CreateVideoClipObject(url, title, thumb, art, summary,
                          c_audio_codec = None, c_video_codec = None,
                          c_container = None, c_protocol = None,
                          c_user_agent = None, optimized_for_streaming = True,
                          include_container = False, *args, **kwargs):

    vco = VideoClipObject(
        key = Callback(CreateVideoClipObject,
                       url = url, title = title, thumb = thumb, art = art, summary = summary,
                       c_audio_codec = c_audio_codec, c_video_codec = c_video_codec,
                       c_container = c_container, c_protocol = c_protocol,
                       c_user_agent = c_user_agent, optimized_for_streaming = optimized_for_streaming,
                       include_container = True),
        rating_key = url,
        title = title,
        thumb = thumb,
        art = art,
        summary = summary,
        items = [
            MediaObject(
                parts = [
                    PartObject(
                        key = HTTPLiveStreamURL(Callback(PlayVideo, url = url, c_user_agent = c_user_agent))
                    )
                ],
                audio_codec = c_audio_codec,
                video_codec = c_video_codec,
                container = c_container,
                protocol = c_protocol,
                optimized_for_streaming = optimized_for_streaming
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects = [vco], user_agent = c_user_agent)
    else:
        return vco
	
@indirect
@route(VIDEO_PREFIX + '/playvideo.m3u8')
def PlayVideo(url, c_user_agent = None):

    # Custom User-Agent string
    if c_user_agent:
        HTTP.Headers['User-Agent'] = c_user_agent

    return IndirectResponse(VideoClipObject, key = url)

def PlayCh(sender, name, id):
	progname=""
	#epgd=API_URL+'epg_next?cid='+str(id)+'&MW_SSID='+Dict['sessionid']	
	#objd = JSON.ObjectFromURL(epgd)
	#if objd.has_key("epg"):
		#progname=objd["epg"][0]["t_start"]+"  "+objd["epg"][0]["progname"]+"\n"+objd["epg"][1]["t_start"]+"  "+objd["epg"][1]["progname"]

	url=API_URL+'get_url?cid='+str(id)+'&MW_SSID='+Dict['sessionid']	
	obj = JSON.ObjectFromURL(url)
	if obj.has_key('error'):
		msg=obj["error"]["message"]
		Dict['sessionid']=""
		return MessageContainer("error", msg)
	else:
		msg=""
		murl=obj["url"]
		ing = ''
		x = 0
		y = 2
		v = 0
		l = len(murl)
		while y <= l:
			if v > 4:
			    v = 0
			v += 1
			ing += chr(int(murl[x:y], 16) - v)
			x += 2
			y += 2
		murl = ing
		oc = ObjectContainer(title1 = unicode(L('Channel')) , no_cache = True)
					
		oc.add(	
			CreateVideoClipObject(
				url = murl,
				title = name,
				thumb = R('art-default.jpg'),
				art = R('art-default.jpg'),
				summary = progname,
				c_audio_codec = None,
				c_video_codec = None,
				c_container = None,
				c_protocol = None,
				c_user_agent = USER_AGENT,
				optimized_for_streaming = True,
				include_container = False
			)
		 )

		#strn=JSON.StringFromObject(obj)
		#murl=murl[0:murl.find(" :")]
		#murl=murl.replace('http/ts://','http://')
		#HTTP.SetHeader('User-Agent', 'vlc/1.1.0 LibVLC/1.1.0')
		#HTTP.SetHeader('Icy-MetaData', '1')
		return oc
			
def ShowMessage(sender, title, message):
	return MessageContainer(title, message)
		
def Logout(sender):
	url=API_URL + 'logout' +'&MW_SSID='+Dict['sessionid']
	obj = JSON.ObjectFromURL(url, encoding='utf-8', cacheTime=1)
	Dict['sessionid']=""
	return True

def DoLogin():
	u = Prefs['username']
	p = Prefs['password']
	if( u and p ):
		LOGGEDIN = Login()
		if LOGGEDIN == False:
			return MessageContainer("Error","No access")
		else:
			return MessageContainer("Login","Login - OK")
	else:
		return MessageContainer("Error","Please enter your username and password")
	
def Login():
	global LOGGEDIN, SID
	if LOGGEDIN == True:
		return True
	elif not Prefs['username'] and not Prefs['password']:
		return False
	else:
		url = API_URL+'login?login='+str(Prefs['username'])+'&pass='+str(Prefs['password'])		
		try:
			obj = JSON.ObjectFromURL(url, encoding='utf-8', cacheTime=1)
			strn=JSON.StringFromObject(obj)
		except:
			obj=[]
			LOGGEDIN = False
			return False	
		SID = obj['sid']
		if len(SID) > 0:
			LOGGEDIN = True
			Dict['sessionid']=SID
			return True
		else:
			LOGGEDIN = False
			Dict['sessionid']=""
			return False

def Thumb(url):
	if url=='':
		return Redirect(R(ICON))
	else:
		try:
			data = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
			return DataObject(data, 'image/jpeg')
		except:
			return Redirect(R(ICON))

def Summary(id):
	url=API_URL +"media/details/"+str(id)+".json"
	obj=JSON.ObjectFromURL(url)
	summary=obj['media']['description']
	return summary

def About(sender):
	return MessageContainer(NAME+' (ver. ' + str(VERSION) + ')', 'Nice re/streamer')

