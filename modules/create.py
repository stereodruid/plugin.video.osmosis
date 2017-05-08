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

import os, sys, re
import errno
reload(sys)
sys.setdefaultencoding("utf-8")
import urllib
import utils
import xbmc
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs
# import pafy
import SimpleDownloader as downloader
from modules import fileSys
from modules import guiTools
from modules import jsonUtils
from modules import stringUtils
from modules import urlUtils
from modules import kodiDB

thisDialog = sys.modules[__name__]    
thisDialog.dialogeBG = None
thisDialog.dialoge = None

def initialize_DialogBG(mess1,mess2, barType="BG"):
    if barType == "BG":
        if not thisDialog.dialogeBG:
            thisDialog.dialogeBG = xbmcgui.DialogProgressBG()
            thisDialog.dialogeBG.create("OSMOSIS: " + mess1 + ": " , " " + mess2)
        
    else: 
        if not thisDialog.dialoge:
            thisDialog.dialoge = xbmcgui.DialogProgress()
            thisDialog.dialoge.create("OSMOSIS: " + mess1 + ": " , " " + mess2)

addon_id = 'plugin.video.osmosis'
addon = xbmcaddon.Addon(addon_id)
addon_version = addon.getAddonInfo('version')
ADDON_NAME = addon.getAddonInfo('name')
REAL_SETTINGS = xbmcaddon.Addon(id=addon_id)
ADDON_SETTINGS = REAL_SETTINGS.getAddonInfo('profile')
MediaList_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS,'MediaList.xml'))
PAGINGTVshows = REAL_SETTINGS.getSetting('paging_tvshows')
PAGINGMovies = REAL_SETTINGS.getSetting('paging_movies')
folder_medialistentry_movie = REAL_SETTINGS.getSetting('folder_medialistentry_movie')
folder_movie = REAL_SETTINGS.getSetting('folder_movie')
STRM_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS,'STRM_LOC'))
profile = xbmc.translatePath(addon.getAddonInfo('profile').decode('utf-8'))
home = xbmc.translatePath(addon.getAddonInfo('path').decode('utf-8'))
favorites = os.path.join(profile, 'favorites')
history = os.path.join(profile, 'history')
dialog = xbmcgui.Dialog()
icon = os.path.join(home, 'icon.png')
iconRemove = os.path.join(home, 'iconRemove.png')
FANART = os.path.join(home, 'fanart.jpg')
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

global listLength
DIRS = []
STRM_LOC = xbmc.translatePath(addon.getSetting('STRM_LOC'))

def fillPlugins(cType='video'):
    utils.addon_log('fillPlugins, type = ' + cType)
    json_query = ('{"jsonrpc":"2.0","method":"Addons.GetAddons","params":{"type":"xbmc.addon.%s","properties":["name","path","thumbnail","description","fanart","summary"]}, "id": 1 }' % cType)
    json_detail = jsonUtils.sendJSON(json_query)
    detail = re.compile("{(.*?)}", re.DOTALL).findall(json_detail)
    for f in sorted(detail, key=lambda str: re.search('"name" *: *"(.*?)",', str).group(1).lower() if re.search('"name" *: *"(.*?)",', str) else str):
        names = re.search('"name" *: *"(.*?)",', f)
        paths = re.search('"addonid" *: *"(.*?)",', f)
        thumbnails = re.search('"thumbnail" *: *"(.*?)",', f)
        fanarts = re.search('"fanart" *: *"(.*?)",', f)
        descriptions = re.search('"description" *: *"(.*?)",', f)
        if not descriptions:
            descriptions = re.search('"summary" *: *"(.*?)",', f)
        if descriptions:
            description = stringUtils.cleanLabels(descriptions.group(1))
        else:
            description = ''
        if names and paths:
            name = stringUtils.cleanLabels(names.group(1))
            path = paths.group(1)
            if cType == 'video' and path.startswith('plugin.video') and not path.startswith('plugin.video.osmosis'):
                thumbnail = thumbnails.group(1) #stringUtils.removeNonAscii(thumbnails.group(1))
                fanart = fanarts.group(1) #stringUtils.removeNonAscii(fanarts.group(1))
                guiTools.addDir(name, 'plugin://' + path, 101, thumbnail, fanart, description, cType, 'date', 'credits')
            elif cType == 'audio' and path.startswith('plugin.audio') and not path.startswith('plugin.video.osmosis'):
                thumbnail = thumbnails.group(1) #stringUtils.removeNonAscii(thumbnails.group(1))
                fanart = fanarts.group(1) #stringUtils.removeNonAscii(fanarts.group(1))
                guiTools.addDir(name, 'plugin://' + path, 101, thumbnail, fanart, description, cType, 'date', 'credits')

def fillPluginItems(url, media_type='video', file_type=False, strm=False, strm_name='', strm_type='Other', showtitle='None'):
    initialize_DialogBG("Updating", "Getting content..")
    thisDialog.dialogeBG.update(0, ADDON_NAME + ": Getting: ", getStrmname(strm_name))
    utils.addon_log('fillPluginItems')
    detail = []
    if url.find("playMode=play")== -1:
        if not file_type:
            detail = stringUtils.uni(jsonUtils.requestList(url, media_type))
            listLength = len(detail)
        else:
            detail = stringUtils.uni(jsonUtils.requestItem(url, media_type))
    else: 
        detail.append("palyableSingleMedia")
        detail.append(url)
        
    thisDialog.dialogeBG.close()
    thisDialog.dialogeBG = None  
    if strm_type.find('Cinema') != -1 or strm_type.find('YouTube') != -1 or strm_type.find('Movies') != -1:
        try:
            initialize_DialogBG("Movie", "Adding")
            movieList = addMovies(detail, strm_name, strm_type)
            dbMovList = kodiDB.writeMovie(movieList)
            j = 100 / len(dbMovList) if len(dbMovList) > 0 else 1
            # Write strms for all values in movieList
            for i in dbMovList:   # path,name,url(+name)
                thisDialog.dialogeBG.update(j, ADDON_NAME + ": Writing Movies: ",  " Video: " + i[1].rstrip("."))
                #fileSys.writeSTRM(stringUtils.cleanStrms((i[0].rstrip("."))), stringUtils.cleanStrms(i[1].rstrip(".")) , i[2] + "|" + i[1])
                # plugin://plugin.video.osmosis/?url=plugin&mode=10&mediaType=show&episode=                
                fileSys.writeSTRM(stringUtils.cleanStrms(i[0].rstrip(".")), stringUtils.cleanStrms((i[1].rstrip("."))) , "plugin://plugin.video.osmosis/?url=plugin&mode=10&mediaType=movie&id=" + str(i[2]) + "|" + i[1])

                j = j + 100 / len(movieList)
                
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None 
            return      
        except:
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
            utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
            print ("Unexpected error:"), sys.exc_info()[0]
            raise
        
    if strm_type.find('TV-Show') != -1 or strm_type.find('Shows-Collection') != -1:
        try:
            initialize_DialogBG("Adding TV-Shows", "working..")
            getTVShowFromList(detail, strm_name, strm_type)
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None
            return
        except:
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
            utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
            print ("Unexpected error:"), sys.exc_info()[0]
            raise
        
    if strm_type.find('Album')!= -1 :
        try:
            initialize_DialogBG("Album", "Adding")
            addAlbum(detail, strm_name, strm_type)
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None       
            return
        except:
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
            utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
            print ("Unexpected error:"), sys.exc_info()[0]
            raise
#     if strm_type.find('YouTube') != -1:
#         
#         video = pafy.new(url)
#         bestaudio = video.getbestaudio()
#         bestaudio.bitrate #get bit rate
#         bestaudio.extension #extension of audio fileurl
# 
#         bestaudio.url #get url
# 
#         #download if you want
#         bestaudio.download()
#         return
            
    for f in detail:
        files = re.search('"file" *: *"(.*?)",', f)
        filetypes = re.search('"filetype" *: *"(.*?)",', f)
        labels = re.search('"label" *: *"(.*?)",', f)
        thumbnails = re.search('"thumbnail" *: *"(.*?)",', f)
        fanarts = re.search('"fanart" *: *"(.*?)",', f)
        descriptions = re.search('"description" *: *"(.*?)",', f)
        tracks = re.search('"track" *: *(.*?),', f)
        durations = re.search('"duration" *: *"(.*?)",', f)
        
        if filetypes and labels and files:
            filetype = filetypes.group(1)
            label = stringUtils.cleanLabels(labels.group(1))
            file = files.group(1).replace("\\\\", "\\")
            strm_name = str(stringUtils.cleanByDictReplacements(strm_name.strip()))
                         
            if not descriptions:
                description = ''
            else:
                description = stringUtils.cleanLabels(descriptions.group(1))
                
            thumbnail = thumbnails.group(1) #stringUtils.removeNonAscii(thumbnails.group(1))
            fanart = fanarts.group(1) #stringUtils.removeNonAscii(fanarts.group(1))
            
            if addon.getSetting('Link_Type') == '0':
                link = sys.argv[0] + "?url=" +urllib.quote_plus(stringUtils.uni(file)) + "&mode=" + str(10) + "&name=" +urllib.quote_plus(stringUtils.uni(label)) + "&fanart=" + urllib.quote_plus(fanart)
            else:
                link = file
        
            if strm_type in ['Audio-Single']:
                path = os.path.join('Singles', str(strm_name))
                try:
                    album = re.search('"album" *: *"(.*?)",', f).group(1).strip()
                    try:
                        artist = re.search('"artist" *: *"(.*?)",', f).group(1).strip()
                    except:
                        artist= re.search('"artist"*:*."(.*?)".,', f).group(1).strip()
                    pass
                    titl = re.search('"title" *: *(.*?),', f).group(1).strip()
                    types = re.search('"type" *: *(.*?),', f).group(1).strip()
                    filename = str(strm_name + ' - ' + label).strip()
                except:
                    filename =str(strm_name + ' - ' + label).strip()
                                   
            if strm_type.find('Audio-Album') != -1:
                path = os.path.join(strm_type, strm_name)
                if tracks:
                    track = tracks.group(1)
                try:
                    album = re.search('"album" *: *"(.*?)",', f).group(1).strip()
                    try:
                        artist = stringUtils.cleanByDictReplacements(re.search('"artist" *: *"(.*?)",', f).group(1).strip())
                    except:
                        artist = stringUtils.cleanByDictReplacements(re.search('"artist"*:*."(.*?)".,', f).group(1).strip())
                    pass
                    titl = stringUtils.cleanByDictReplacements(re.search('"title" *: *(.*?),', f).group(1).strip())
                    types = stringUtils.cleanByDictReplacements(re.search('"type" *: *(.*?),', f).group(1).strip())
                    filename = stringUtils.cleanByDictReplacements(str(label).strip())
                except:
                    filename = stringUtils.cleanByDictReplacements(str(label).strip())

            if strm_type in ['Other']:
                path = os.path.join('Other', strm_name)
                filename =str(strm_name + ' - ' + label)             
                                  
            if filetype == 'file':
                if strm:
                    if strm_type.find('Audio-Albums') != -1:
                        utils.addon_log(str(path + ' ' + filename))
                        #utils.createSongNFO(stringUtils.cleanStrms((path.rstrip("."))), stringUtils.cleanStrms(filename.rstrip(".")), strm_ty=strm_type, artists=artist,albums=album , titls=titl, typese=types) 
                        kodiDB.musicDatabase(album, artist, label, path, link, track)
                    # xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(path + " - " + filename, " writing...",5000,""))
                    fileSys.writeSTRM(stringUtils.cleanStrms((path.rstrip("."))), stringUtils.cleanStrms(filename.rstrip(".")) , link)
                else:
                    guiTools.addLink(label, file, 10, thumbnail, fanart, description, '', '', '', None, '', total=len(detail))
                    # xbmc.executebuiltin("Container.SetViewMode(500)")
            else:
                if strm:
                    fillPluginItems(file, media_type, file_type, strm, label, strm_type)
                else:
                    guiTools.addDir(label, file, 101, thumbnail, fanart, description, '', '', '')
                    # xbmc.executebuiltin("Container.SetViewMode(500)")

def removeItemsFromMediaList(action='list'):
    from modules import dialoge
    utils.addon_log('removingitemsdialog')
    thelist = fileSys.readMediaList(purge=False)
    items = [getStrmname(thelist[i].strip().split('|')[1]).format(i) for i in range(len(thelist))]
    dialog = dialoge.MultiChoiceDialog("Select items", items)
    dialog.doModal()

    fileSys.removeMediaList(dialog.selected)
        
    xbmcgui.Dialog().notification("Finished deleting:", "{0}".format(", ".join(str(label) for label in dialog.selectedLabels)))
    del dialog
    
def addAlbum(contentList, strm_name='', strm_type='Other', PAGINGalbums="1"):
    albumList = []
    pagesDone = 0
    file=''
    j = 100 / (len(contentList) * int(PAGINGalbums))
    
    while pagesDone < int(PAGINGalbums):
        if not contentList[0] == "palyableSingleMedia":
            albumThumbnails = re.search('"thumbnail" *: *"(.*?)",', str(contentList))
            if albumThumbnails:
                aThumb = urlUtils.stripUnquoteURL(albumThumbnails.group(1))
                 
            for detailInfo in contentList:
                detailInfo = stringUtils.removeHTMLTAGS(detailInfo)
                files = re.search('"file" *: *"(.*?)",', detailInfo)
                filetypes = re.search('"filetype" *: *"(.*?)",', detailInfo)
                labels = re.search('"label" *: *"(.*?)",', detailInfo)
                thumbnails = re.search('"thumbnail" *: *"(.*?)",', detailInfo)
                fanarts = re.search('"fanart" *: *"(.*?)",', detailInfo)
                descriptions = re.search('"description" *: *"(.*?)",', detailInfo)
                tracks = re.search('"track" *: *(.*?),', detailInfo)
                durations = re.search('"duration" *: *"(.*?)",', detailInfo)
                                              
                try:
                    if filetypes and labels and files:
                        filetype = filetypes.group(1)
                        label = (stringUtils.cleanLabels(labels.group(1)))
                        file = (files.group(1).replace("\\\\", "\\"))

                        if fanarts:
                            fanart = fanarts.group(1)
                        else:
                            fanart = ''                        
                        if addon.getSetting('Link_Type') == '0': 
                            link = sys.argv[0] + "?url=" + urllib.quote_plus(file) + "&mode=" + str(10) + "&name=" + urllib.quote_plus(label) + "&fanart=" + urllib.quote_plus(fanart)
                        else:
                            link = file
                        if thumbnails:
                            thumb = urlUtils.stripUnquoteURL(thumbnails.group(1))
                        else:
                            thumb =""   
                        if label and strm_name:                                                 
                            label = str(stringUtils.cleanByDictReplacements(label.strip()))
                        if tracks:
                            track = tracks.group(1)
                        try:
                            album = re.search('"album" *: *"(.*?)",', detailInfo).group(1).strip()
                            try:
                                artist = stringUtils.cleanByDictReplacements(re.search('"artist" *: *"(.*?)",', detailInfo).group(1).strip())
                            except:
                                artist = stringUtils.cleanByDictReplacements(re.search('"artist"*:*."(.*?)".,', detailInfo).group(1).strip())
                            pass                      
                            titl = stringUtils.cleanByDictReplacements(re.search('"title" *: *(.*?),', detailInfo).group(1).strip())
                            types = stringUtils.cleanByDictReplacements(re.search('"type" *: *(.*?),', detailInfo).group(1).strip())
                            filename = stringUtils.cleanByDictReplacements(str(label).strip())
                        except:
                            filename = stringUtils.cleanByDictReplacements(str(label).strip())
                            pass

                        thisDialog.dialogeBG.update(j, ADDON_NAME + ": Writing File: ",  " Title: " + label)
                        path = os.path.join(strm_type, artist.strip(),album.strip())
                        if album and artist and label and path and link and track:  
                            albumList.append([path, label.strip(), link, album, artist, track, thumb])
                        j = j + 100 / (len(contentList) * int(PAGINGalbums))
                except IOError as (errno, strerror):
                    print ("I/O error({0}): {1}").format(errno, strerror)
                except ValueError:
                    print ("No valid integer in line.")
                except:
                    thisDialog.dialogeBG.close()
                    guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
                    utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
                    print ("Unexpected error:"), sys.exc_info()[0]
                    raise
            pagesDone += 1
            if filetypes:
                if filetype != 'file' and pagesDone < int(PAGINGalbums):
                    contentList = stringUtils.uni(jsonUtils.requestList(file, 'video'))
                else:
                    pagesDone = int(PAGINGalbums)
            if False:     
                try:
                    urlUtils.downloadThumb(aThumb,album, os.path.join(STRM_LOC, strm_type, artist)) 
                except:
                    pass             
        else:
            albumList.append([os.path.join(strm_type, getStrmname(strm_name) , label.strip()), str(stringUtils.cleanByDictReplacements(label.strip())), link])
            pagesDone = int(PAGINGalbums)

    try:
        # Write strms for all values in albumList
        for i in albumList:
            fileSys.writeSTRM(path, stringUtils.cleanStrms(i[1].rstrip(".")) , i[2] + "|" + i[1])
            kodiDB.musicDatabase(i[3], i[4], i[1], i[0], i[2], i[5], aThumb)
        thisDialog.dialogeBG.close()
    except IOError as (errno, strerror):
        print ("I/O error({0}): {1}").format(errno, strerror)
    except ValueError:
        print ("No valid integer in line.")
    except:
        thisDialog.dialogeBG.close()
        guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
        utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
        print ("Unexpected error:"), sys.exc_info()[0]
        raise
    
    return albumList


def addMovies(contentList, strm_name='', strm_type='Other', provider="n.a"):
    movieList = []
    listName = strm_name
    pagesDone = 0
    file=''
    filetype=''
    j = len(contentList) * int(PAGINGMovies) / 100
    
    while pagesDone < int(PAGINGMovies):
        if not contentList[0] == "palyableSingleMedia":
            for detailInfo in contentList:
                detailInfo = stringUtils.removeHTMLTAGS(detailInfo)
                files = re.search('"file" *: *"(.*?)",', detailInfo)
                filetypes = re.search('"filetype" *: *"(.*?)",', detailInfo)
                labels = re.search('"label" *: *"(.*?)",', detailInfo)
                thumbnails = re.search('"thumbnail" *: *"(.*?)",', detailInfo)
                fanarts = re.search('"fanart" *: *"(.*?)",', detailInfo)
                descriptions = re.search('"description" *: *"(.*?)",', detailInfo)
                provGeneral = re.search('%s(.*)'"\\/\\?"'' % (r"plugin://plugin.video."), detailInfo)
                provXST = re.search('%s(.*)'"\&function"'' % (r"site="), detailInfo)
            
                try:
                    if filetypes and labels and files:
                        filetype = filetypes.group(1)
                        label = (stringUtils.cleanLabels(labels.group(1)))
                        file = (files.group(1).replace("\\\\", "\\"))
                        
                        if provGeneral:
                            listName = provGeneral.group(1)
                            if provXST:
                                listName = listName + ": " + provXST.group(1)
                        
                        if fanarts:
                            fanart = fanarts.group(1)
                        else:
                            fanart = ''                 
                            
                        link = file
                        
                        if label and strm_name:                                              
                            label = stringUtils.cleanByDictReplacements(label.strip())
                            thisDialog.dialogeBG.update(j, ADDON_NAME + ": Gettin Movies: ",  " Video: " + label)
                            if filetype == 'file':
                                movieList.append([getMovieStrmPath(strm_type, strm_name, label), stringUtils.cleanByDictReplacements(getStrmname(label)), link, listName])
                            j = j + len(contentList) * int(PAGINGMovies) / 100
                except IOError as (errno, strerror):
                    print ("I/O error({0}): {1}").format(errno, strerror)
                except ValueError:
                    print ("No valid integer in line.")
                except:
                    guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
                    utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
                    print ("Unexpected error:"), sys.exc_info()[0]
                    raise
            pagesDone += 1
            if filetype != '' and filetype != 'file' and pagesDone < int(PAGINGMovies):
                contentList = stringUtils.uni(jsonUtils.requestList(file, 'video'))
            else:
                pagesDone = int(PAGINGMovies)            
        else:                                         #<       REMOVE                                   >
            provGeneral = re.search('%s(.*)'"\\/\\?"'' % (r"plugin://plugin.video."), contentList[1])
            provXST = re.search('%s(.*)'"\&function"'' % (r"site="), contentList[1])

            if provGeneral:
                listName = provGeneral.group(1)
                if provXST:
                    listName = listName + ": " + provXST.group(1)
            movieList.append([getMovieStrmPath(strm_type, strm_name), stringUtils.cleanByDictReplacements(getStrmname(strm_name)), contentList[1], listName])
            pagesDone = int(PAGINGMovies)

    return movieList
 
def getTVShowFromList(showList, strm_name='', strm_type='Other', pagesDone=0):
    file=''
    filetype=''
    dirList = []
    
    while pagesDone < int(PAGINGTVshows):
        strm_type = strm_type.replace('Shows-Collection', 'TV-Shows')
        try:
            showList = filter(lambda elem: re.search('"filetype" *: *"(.*?)",', elem), showList)
            step = float(100.0 / len(showList) if len(showList) > 0 else 1)

            for index, detailInfo in enumerate(showList):
                detailInfo = stringUtils.removeHTMLTAGS(detailInfo)
                filetypes = re.search('"filetype" *: *"(.*?)",', detailInfo)
                if filetypes:
                    filetype = filetypes.group(1)
                    files = re.search('"file" *: *"(.*?)",', detailInfo)
                    episodes = re.search('"episode" *: *(.*?),', detailInfo)
                    seasons = re.search('"season" *: *(.*?),', detailInfo)
                    labels = re.search('"label" *: *"(.*?)",', detailInfo)
                    
                    if labels:
                        label = str(labels.group(1).strip())
                    else:
                        label = "None"          

                    if not fileSys.isInMediaList(label, strm_type) and label != "" and label != ">>>" and label != "None" and files.group(1).find("playMode=play") == "-1":            
                        fileSys.writeMediaList(files.group(1).strip(), label, strm_type)
                    
                    if filetype == 'directory':
                        dirList.append(stringUtils.uni(jsonUtils.requestList(files.group(1), 'video')))
                        continue

                    if seasons and episodes and seasons.group(1) != "-1" and episodes.group(1) != "-1" and filetype == 'file': 
                        j = int(step * (index + 1))
                        thisDialog.dialogeBG.update(j, "Page: " + str(pagesDone + 1) + " " + getStrmname(strm_name))                    
                        pagesDone = getEpisodes(detailInfo, strm_name, strm_type,pagesDone=pagesDone)
                        utils.addon_log("percentdone: " + str(j) + "; step: " + str(step))
                                    
        except IOError as (errno, strerror):
            print ("I/O error({0}): {1}").format(errno, strerror)
        except ValueError:
            print ("No valid integer in line.")
        except:
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
            utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
            print ("Unexpected error:"), sys.exc_info()[0]
            raise
        
        pagesDone += 1
        if pagesDone < int(PAGINGTVshows) and len(dirList) > 0:
            showList = [item for sublist in dirList for item in sublist]
            dirList = []

def getEpisodes(episodesListRaw, strm_name, strm_type, j=0, pagesDone=0):
    episodesList = []
    typeChange = []

    try:
        if type(episodesListRaw) is unicode:
            typeChange.append(episodesListRaw)
            episodesListRaw = typeChange
    
        for detailInfo in episodesListRaw:
            utils.addon_log("detailInfo: " + detailInfo)
            detailInfo = stringUtils.removeHTMLTAGS(detailInfo)
            files = re.search('"file" *: *"(.*?)",', detailInfo)            
            filetypes = re.search('"filetype" *: *"(.*?)",', detailInfo)
            labels = re.search('"label" *: *"(.*?)",', detailInfo)
            thumbnails = re.search('"thumbnail" *: *"(.*?)",', detailInfo)
            fanarts = re.search('"fanart" *: *"(.*?)",', detailInfo)
            descriptions = re.search('"description" *: *"(.*?)",', detailInfo)
            episodes = re.search('"episode" *: *(.*?),', detailInfo)
            seasons = re.search('"season" *: *(.*?),', detailInfo)
            showtitles = re.search('"showtitle" *: *"(.*?)",', detailInfo)
            provGeneral = re.search('%s(.*)'"\\/\\?"'' % (r"plugin://plugin.video."), detailInfo)
            provXST = re.search('%s(.*)'"\&function"'' % (r"site="), detailInfo)
            listName = strm_name

            if filetypes:
                if provGeneral:
                    listName = provGeneral.group(1)
                    if provXST:
                        listName = listName + ": " + provXST.group(1)
     
                if showtitles and seasons and episodes:
                    filetype = filetypes.group(1)
                    label = (stringUtils.cleanLabels(labels.group(1))) 
                    file = (files.group(1).replace("\\\\", "\\"))
                    strm_name = str(stringUtils.cleanByDictReplacements(strm_name.strip()))
                    showtitle = stringUtils.cleanByDictReplacements((showtitles.group(1)))
                    season = stringUtils.cleanByDictReplacements(seasons.group(1).replace("-", ""))
                    episode = stringUtils.cleanByDictReplacements(episodes.group(1).replace("-", ""))
                    episodesHDF = re.search('Folge.(\\d+)&', file)
                    
                    if file.find("hdfilme") != "-1" and episodesHDF:
                        episode = re.search('Folge.(\\d+)&', file).group(1)
                    
                    if not descriptions:
                        description = ''
                    else:
                        description = stringUtils.cleanLabels(descriptions.group(1))
        
                    if fanarts:
                        fanart = fanarts.group(1)
                    else:
                        fanart = ''

                    if strm_name.find("++RenamedTitle++") != -1 or showtitle == "":
                        showtitle = getStrmname(strm_name)
                    if showtitle != "" and strm_type != "":
                        episodesList.append([strm_type, str('s' + season), str('e'+episode), file, stringUtils.cleanByDictReplacements(showtitle.strip()), listName])
                        
    except IOError as (errno, strerror):
        print ("I/O error({0}): {1}").format(errno, strerror)
    except ValueError:
        print ("No valid integer in line.")
    except:
        guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
        utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
        print ("Unexpected error:"), sys.exc_info()[0]
        raise
    dbEpisodes = kodiDB.writeShow(episodesList)
    for i in dbEpisodes:
        j += 1
        
        fileSys.writeSTRM(os.path.join(stringUtils.cleanStrms((i[0].rstrip("."))),stringUtils.cleanStrms(i[1].rstrip("."))), stringUtils.cleanStrms(i[3] + i[4]) , "plugin://plugin.video.osmosis/?url=plugin&mode=10&mediaType=show&episode=" + i[3] + i[4] + "&showid=" + str(i[2]) + "|" + i[1])
        #fileSys.writeSTRM(stringUtils.cleanStrms((i[0].rstrip("."))), stringUtils.cleanStrms(i[1].rstrip(".")) + stringUtils.cleanStrms(i[2].rstrip(".")) , i[3])
        thisDialog.dialogeBG.update(j)
    return pagesDone
    
def getData(url, fanart):
    utils.addon_log('getData, url = ' + cType)

def getMovieStrmPath(strmTypePath, mediaListEntry_name, movie_name=''):
    if folder_medialistentry_movie and folder_medialistentry_movie == 'true':
        mediaListEntry_name = stringUtils.cleanByDictReplacements(getStrmname(mediaListEntry_name))
        strmTypePath = os.path.join(strmTypePath, mediaListEntry_name)
    if movie_name != '' and folder_movie and folder_movie == 'true':
        movie_name = stringUtils.cleanByDictReplacements(getStrmname(movie_name))
        strmTypePath = os.path.join(strmTypePath, movie_name)
    return strmTypePath

def getStrmname(strm_name):
    return strm_name.strip().replace('++RenamedTitle++', '')

# def playsetresolved(url, name, iconimage, setresolved=True):
#     utils.addon_log('playsetresolved')
#     if setresolved:
#         liz = xbmcgui.ListItem(name, iconImage=iconimage)
#         liz.setInfo(cType='Video', infoLabels={'Title':name})
#         liz.setProperty("IsPlayable", "true")
#         contextMenu.append(('Create Strm', 'XBMC.RunPlugin(%s&mode=200&name=%s)' % (u, name)))
#         liz.setPath(url)
#         xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
#     else:
#         xbmc.executebuiltin('XBMC.RunPlugin(' + url + ')')