# This file is part of OSMOSIS.
#
# OSMOSIS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OSMOSIS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OSMOSIS.  If not, see <http://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-
import os, sys
import urllib

import SimpleDownloader as downloader 
from modules import create
from modules import fileSys
from modules import guiTools
from modules import urlUtils

import utils
import xbmc, xbmcaddon, xbmcgui, xbmcplugin
 
# import pydevd
# pydevd.settrace(stdoutToServer=True, stderrToServer=True)

reload(sys)
sys.setdefaultencoding("utf-8")

#from modules import createNFO
# Debug option pydevd:



addnon_id = 'plugin.video.osmosis'
addon = xbmcaddon.Addon(addnon_id)#
addon_version = addon.getAddonInfo('version')
ADDON_NAME = addon.getAddonInfo('name')
REAL_SETTINGS = xbmcaddon.Addon(id=addnon_id)# 
ADDON_SETTINGS = REAL_SETTINGS.getAddonInfo('profile')
MediaList_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS,'MediaList.xml'))#
STRM_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS,'STRM_LOC'))#
profile = xbmc.translatePath(addon.getAddonInfo('profile').decode('utf-8'))#
home = xbmc.translatePath(addon.getAddonInfo('path').decode('utf-8'))#
favorites = os.path.join(profile, 'favorites')
history = os.path.join(profile, 'history')
dialog = xbmcgui.Dialog()#
icon = os.path.join(home, 'icon.png')
iconRemove = os.path.join(home, 'iconRemove.png')
FANART = os.path.join(home, 'fanart.jpg')
source_file = os.path.join(home, 'source_file')
functions_dir = profile
downloader = downloader.SimpleDownloader()#
debug = addon.getSetting('debug')

if os.path.exists(favorites) == True:
    FAV = open(favorites).read()
else: FAV = []
if os.path.exists(favorites) == True:
    FAV = open(favorites).read()
else: FAV = []

DIRS = []
STRM_LOC = xbmc.translatePath(addon.getSetting('STRM_LOC'))

if __name__ == "__main__":
    try:
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    except:
        pass
    try:
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
    except:
        pass
    try:
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    except:
        pass
    try:
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
    except:
        pass
    try:
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_GENRE)
    except:
        pass
    
    params = utils.get_params()
    name = None
    guiElem = None
    del_item = None
    url = None
    mode = None
    playlist = None
    iconimage = None
    fanart = FANART
    playlist = None
    fav_mode = None
    regexs = None
    album = None
    artist = None
    titl = None
    cType = None
   
#     try:
#         markName = urllib.unquote_plus(params["url"]).decode('utf-8').split('|')[1]
#     except:
#         pass
    try:
        url = urllib.unquote_plus(params["url"]).decode('utf-8')
    except:
        try:
            url = urlUtils.getURL(sys.argv[2])
        except:
            pass
        pass
    try:
        name = urllib.unquote_plus(params["name"])
    except:
        name = None
    try:
        iconimage = urllib.unquote_plus(params["iconimage"])
    except:
        pass
    try:
        fanart = urllib.unquote_plus(params["fanart"])
    except:
        pass
    try:
        mode = int(params["mode"])
    except:
        pass
    try:
        playlist = eval(urllib.unquote_plus(params["playlist"]).replace('||', ','))
    except:
        pass
    try:
        fav_mode = int(params["fav_mode"])
    except:
        pass
    try:
        regexs = params["regexs"]
    except:
        pass
    
    utils.addon_log("Mode: " + str(mode))
 
    if not url is None:
        utils.addon_log("URL: " + str(url)) #.encode('utf-8')))
        utils.addon_log("Name: " + str(name))
    #createNFO.setNamePath(STRM_LOC + "\\TV-Shows(de)", 'The Walking Dead', STRM_LOC) 
    if mode == None:
        utils.addon_log("getSources")
        guiTools.getSources()
        try:
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        except:
            pass
    elif mode == 1:   
        create.fillPlugins(url)
        try:
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        except:
            pass
    elif mode == 2:
        create.fillPluginItems(url)
        try:
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        except:
            pass 
    elif mode == 4:
        create.removeItemsFromMediaList('list') 
    elif mode == 5:
        create.removeItemsFromMediaList('list') 
    elif mode == 10:
        meta = ""
        # Split url to get tags
        purl = url.split('|')[0]
        utils.addon_log("setResolvedUrl")
        item = xbmcgui.ListItem(path=url)
        # Gest infos from selectet media
        sPatToItem = xbmc.getInfoLabel("ListItem.path")
        sTitle = xbmc.getInfoLabel("ListItem.title")
        sShowTitle = xbmc.getInfoLabel("ListItem.TVShowTitle")
        sEpisode = xbmc.getInfoLabel("ListItem.episode")
        sSeason = xbmc.getInfoLabel("ListItem.season")
        sYear = xbmc.getInfoLabel("ListItem.year")
        sDBID = xbmc.getInfoLabel("ListItem.DBID")
        sDuration = xbmc.getInfoLabel("ListItem.Duration")
        
        
        
        try:
            # Exec play process
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            # Wait until the media is started in player
            while meta.find("video") == -1:
                meta = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}')
                
            tvShowTitle = xbmc.getInfoLabel("VideoPlayer.TVShowTitle")
            movieTitle = xbmc.getInfoLabel("VideoPlayer.Title")
            movieBIBID = xbmc.getInfoLabel("VideoPlayer.DBID")
            duration = xbmc.getInfoLabel("VideoPlayer.Duration")
            season = xbmc.getInfoLabel("VideoPlayer.Season")
            episode = xbmc.getInfoLabel("VideoPlayer.Episode")
            playedTime = xbmc.getInfoLabel("VideoPlayer.Time")
            # Set watched status   
            if tvShowTitle != "":
                guiTools.markSeries(sPatToItem,tvShowTitle,episode,season,sYear,movieBIBID,duration)
            else:
                guiTools.markMovie(sPatToItem,movieTitle,sYear,movieBIBID,duration)
        except:
            pass 
    elif mode == 100:
        create.fillPlugins(url)
        try:
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        except:
            pass 
    elif mode == 101:
        create.fillPluginItems(url)
        try:
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        except:
            pass 
        
    elif mode == 200:
        utils.addon_log("write multi strms")
        cType = guiTools.getType(url)
        fileSys.writeMediaList(url, name, cType)
        dialog.notification(cType, name, xbmcgui.NOTIFICATION_INFO, 5000, False) 
        create.fillPluginItems(url, strm=True, strm_name=name, strm_type=cType)
        dialog.notification('Writing items...', "Done", xbmcgui.NOTIFICATION_INFO, 5000, False)    
    elif mode == 201:
        utils.addon_log("write single strm")
        # create.fillPluginItems(url)
        # makeSTRM(name, name, url)
