# Copyright (C) 2016 stereodruid(J.G.)
#
#
# This file is part of OSMOSIS
#
# OSMOSIS is free software: you can redistribute it. 
# You can modify it for private use only.
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OSMOSIS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from modules import stringUtils
#from modules import fileSys
import time
import os, sys, re, traceback
import random
import shutil
import string
import time, datetime
import unicodedata
import urllib, urllib2, cookielib, requests

from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP
import SimpleDownloader as downloader
import pyxbmct
import utils
import xbmc
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs

try:
    import json
except:
    import simplejson as json


addnon_id = 'plugin.video.osmosis'
addon = xbmcaddon.Addon(addnon_id)
addon_version = addon.getAddonInfo('version')
ADDON_NAME = addon.getAddonInfo('name')
REAL_SETTINGS = xbmcaddon.Addon(id=addnon_id)
ADDON_SETTINGS = REAL_SETTINGS.getAddonInfo('profile')
MediaList_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS,'MediaList.xml'))
STRM_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS,'STRM_LOC'))
profile = xbmc.translatePath(addon.getAddonInfo('profile').decode('utf-8'))
home = xbmc.translatePath(addon.getAddonInfo('path').decode('utf-8'))
favorites = os.path.join(profile, 'favorites')
history = os.path.join(profile, 'history')
dialog = xbmcgui.Dialog()
icon = os.path.join(home, 'icon.png')
iconRemove = os.path.join(home, 'iconRemove.png')
FANART = os.path.join(home, 'fanart.jpg')
folderIcon= represent = os.path.join(home, 'folderIcon.png')
updateIcon= represent = os.path.join(home, 'updateIcon.png')
source_file = os.path.join(home, 'source_file')
functions_dir = profile
downloader = downloader.SimpleDownloader()
debug = addon.getSetting('debug')

if os.path.exists(favorites) == True:
    FAV = open(favorites).read()
else: FAV = []
if os.path.exists(favorites) == True:
    FAV = open(favorites).read()
else: FAV = []

DIRS = []
STRM_LOC = xbmc.translatePath(addon.getSetting('STRM_LOC'))

def addItem(labels="n.a"):
    if labels != 'n.a':    
        try:
            utils.addon_log('addItem')
            u = "plugin://plugin.video.osmosis/?url=" + "&mode=" + str(5) + "&fanart=" + urllib.quote_plus(iconRemove)
            ok = True
            liz = xbmcgui.ListItem(labels, iconImage=iconRemove, thumbnailImage=iconRemove)
            liz.setInfo(type="Video", infoLabels={ "Title": labels,"Genre": "actionRemove"})
            liz.setProperty("Fanart_Image", FANART)
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
            xbmcplugin.endOfDirectory(int(sys.argv[1]), updateListing=True)        
        except:#            
            pass
        
def addFunction(labels= 'n.a' ):
    if labels != 'n.a':    
        try:
            utils.addon_log('addItem')
            u = "plugin://plugin.video.osmosis/?url=" + "&mode=" + str(666) + "&fanart=" + urllib.quote_plus(iconRemove)
            ok = True
            liz = xbmcgui.ListItem(labels, iconImage=updateIcon, thumbnailImage=updateIcon)
            liz.setInfo(type="Video", infoLabels={ "Title": labels,"Genre": "actionRemove"})
            liz.setProperty("Fanart_Image", FANART)
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
            #xbmcplugin.endOfDirectory(int(sys.argv[1]), updateListing=True)        
        except:#          
            pass
            
def addDir(name,url,mode,iconimage,fanart,description,genre,date,credits,showcontext=False):
    utils.addon_log('addDir')
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&fanart="+urllib.quote_plus(fanart)
    ok=True
    contextMenu = []
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description, "Genre": genre, "dateadded": date, "credits": credits })
    liz.setProperty("Fanart_Image", fanart)
    contextMenu.append(('Create Strms','XBMC.RunPlugin(%s&mode=200&name=%s)'%(u, name)))
    liz.addContextMenuItems(contextMenu)
    try:
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    except:
        pass
    
    return ok
      
def addLink(name,url,mode,iconimage,fanart,description,genre,date,showcontext,playlist,regexs,total,setCookie=""): 
    utils.addon_log('addLink') 
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&fanart="+urllib.quote_plus(fanart)
    ok = True
    contextMenu =[]
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description, "Genre": genre, "dateadded": date })
    liz.setProperty("Fanart_Image", fanart)
    liz.setProperty('IsPlayable', 'true')
    contextMenu.append(('Create Strm','XBMC.RunPlugin(%s&mode=200&name=%s)'%(u, name)))
    liz.addContextMenuItems(contextMenu)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,totalItems=total)
    return ok

def getSources():
    utils.addon_log('getSources')
    addDir('Video Plugins', 'video', 1, folderIcon, FANART, 'description', 'genre', 'date', 'credits')
    addDir('Music Plugins', 'audio', 1, folderIcon, FANART, 'description', 'genre', 'date', 'credits')
    addDir('UPNP Servers', 'upnp://', 2, folderIcon, FANART, 'description', 'genre', 'date', 'credits')
    addFunction('Update')
    addItem(labels="Remove Media")
    #ToDo Add label

def getType(url):
    if url.find('plugin.audio') != -1:
        Types = ['YouTube','Audio-Album', 'Audio-Single', 'Other']
    else:
        Types = ['Cinema', 'TV-Shows', 'Shows-Collection', 'YouTube',"TVShows sub structures",'Other']
    
    selectType = selectDialog(Types, header ='Select category')
       
    if selectType == 3:
        subType = ['(Music)', '(Movies)','(TV-Shows)']
        selectOption = selectDialog(subType, header ='Select Video type:')
        
    else:
        subType = ['(en)', '(de)','(sp)','(tr)', 'Other']
        selectOption = selectDialog(subType, header ='Select language tag')
        
    if selectType >= 0 and selectOption >= 0:
        return Types[selectType]+ subType[selectOption]

def selectDialog(list, header=ADDON_NAME, autoclose=0):
    if len(list) > 0:
        select = xbmcgui.Dialog().select(header, list, autoclose)
        return select
def editDialog(nameToChange): 
    dialog = xbmcgui.Dialog()
    select = dialog.input(nameToChange, type=xbmcgui.INPUT_ALPHANUM)
    return select
#Before executing the code below we need to know the movie original title (string variable originaltitle) and the year (string variable year). They can be obtained from the infolabels of the listitem. The code filters the database for items with the same original title and the same year, year-1 and year+1 to avoid errors identifying the media.
def markMovie(sTitle):
    if xbmc.getCondVisibility('Library.HasContent(Movies)'):
        try:
            print("Check if movie exists in library when marking as watched")
            meta = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "filter": {"field": "playcount", "operator": "is", "value": "0"}, "limits": { "start" : 0, "end": 75 }, "properties" : ["art", "rating", "thumbnail", "playcount", "file"], "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libMovies"}')  
            meta = stringUtils.uni(meta)#(meta, 'utf-8', errors='ignore')
            meta = json.loads(meta)
            meta = meta['result']['movies']
        
            cleaned_title= re.sub('[^-a-zA-Z0-9_.()\\\/ ]+', '',  sTitle) #originaltitle)
            try:
                meta = [i for i in meta if cleaned_title.rstrip() in i['file'].rstrip()][0]
            except:
                print("markMovie: Original title not found")
                pass
            xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "playcount" : 1 }, "id": 1 }' % str(meta['movieid']))
        except:
            print("markMovie: Movie not in DB!?")
            pass
               

def markSeries(sShowTitle,sEpisode,sSeason):
    if xbmc.getCondVisibility('Library.HasContent(TVShows)'):
        try:
            print("Check if tvshow episode exists in library when marking as watched")
            cleaned_title= (re.sub('[^-a-zA-Z0-9_.()\\\/ ]+', '',  sShowTitle)).rstrip().lstrip()
            meta = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": {"filter":{"and": [{"field": "season", "operator": "is", "value": "%s"}, {"field": "episode", "operator": "is", "value": "%s"}]}, "properties": ["title", "plot", "votes", "rating", "writer", "firstaired", "playcount", "runtime", "director", "productioncode", "season", "episode", "originaltitle", "showtitle", "lastplayed", "fanart", "thumbnail", "file", "resume", "tvshowid", "dateadded", "uniqueid"]}, "id": 1}' % (sSeason, sEpisode))
            meta = json.loads(meta)
            meta = meta['result']['episodes']
            try:
                gotIt = [i for i in meta if (cleaned_title in i['showtitle'].rstrip() or i['showtitle'].rstrip() in cleaned_title)][0]
            except:
                print("markSeries: Original title not found")
                pass
            if gotIt:               
                player = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}')
                
                #while meta.find("video") == -1:
                    #time.sleep(2)
            #resume playing
            #xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "resume": {"position": 1600, "total": 3600}}, "id": 1 }' % str(gotIt['episodeid']))
            #set watched
            xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "playcount" : 1 }, "id": 1 }' % str(gotIt['episodeid']))
        except:
            print("markSeries: Show not in DB!?")
            pass
# Functions not in usee yet:
def handle_wait(time_to_wait, header, title):
    dlg = xbmcgui.DialogProgress()
    dlg.create("OSMOSIS", header)
    secs = 0
    percent = 0
    increment = int(100 / time_to_wait)
    cancelled = False
    while secs < time_to_wait:
        secs += 1
        percent = increment * secs
        secs_left = str((time_to_wait - secs))
        remaining_display = "Starts In " + str(secs_left) + " seconds, Cancel Channel Change?" 
        dlg.update(percent, title, remaining_display)
        xbmc.sleep(1000)
        if (dlg.iscanceled()):
            cancelled = True
            break
    if cancelled == True:
        return False
    else:
        dlg.close()
        return True

def show_busy_dialog():
    xbmc.executebuiltin('ActivateWindow(busydialog)')

def hide_busy_dialog():
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    while xbmc.getCondVisibility('Window.IsActive(busydialog)'):
        time.sleep(.1)
        
def Error(header, line1='', line2='', line3=''):
    dlg = xbmcgui.Dialog()
    dlg.ok(header, line1, line2, line3)
    del dlg

def infoDialog(str, header=ADDON_NAME, time=10000):
    try: xbmcgui.Dialog().notification(header, str, icon, time, sound=False)
    except: xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % (header, str, time, THUMB))

def okDialog(str1, str2='', header=ADDON_NAME):
    xbmcgui.Dialog().ok(header, str1, str2)

def yesnoDialog(str1, str2='', header=ADDON_NAME, yes='', no=''):
    answer = xbmcgui.Dialog().yesno(header, str1, str2, '', yes, no)
    return answer
     
def browse(type, heading, shares, mask='', useThumbs=False, treatAsFolder=False, path='', enableMultiple=False):
    retval = xbmcgui.Dialog().browse(type, heading, shares, mask, useThumbs, treatAsFolder, path, enableMultiple)
    return retval
