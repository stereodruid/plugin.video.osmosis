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
HIDE_tile_in_OV = REAL_SETTINGS.getSetting('Hide_tilte_in_OV')
PAGINGTVshows = REAL_SETTINGS.getSetting('paging_tvshows')
PAGINGMovies = REAL_SETTINGS.getSetting('paging_movies')
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

DIRS = []
STRM_LOC = xbmc.translatePath(addon.getSetting('STRM_LOC'))

def fillPlugins(cType='video'):    
    json_query = ('{"jsonrpc":"2.0","method":"Addons.GetAddons","params":{"type":"xbmc.addon.%s","properties":["name","path","thumbnail","description","fanart","summary", "extrainfo"]}, "id": 1 }' % cType)
    json_details = jsonUtils.sendJSON(json_query)
    for addon in sorted(json_details["addons"], key=lambda json: json['name'].lower()):
        utils.addon_log('fillPlugins entry: ' + str(addon))
        addontypes = []
        for info in addon['extrainfo']:
            if info['key'] == 'provides':
                addontypes = info['value'].split(" ")
                break

        if cType in addontypes and not addon['addonid'] == 'plugin.video.osmosis':
            art = {'thumb': addon['thumbnail'], 'fanart': addon['fanart']}
            guiTools.addDir(addon['name'], 'plugin://' + addon['addonid'], 101, art, addon['description'], cType, 'date', 'credits')

def fillPluginItems(url, media_type='video', file_type=False, strm=False, strm_name='', strm_type='Other', showtitle='None'):
    initialize_DialogBG("Updating", "Getting content..")
    thisDialog.dialogeBG.update(0, ADDON_NAME + ": Getting: ", stringUtils.getStrmname(strm_name))
    utils.addon_log('fillPluginItems')
    details = []

    if url.find("playMode=play") == -1:
        if not file_type:
            details = jsonUtils.requestList(url, media_type).get('files', [])
        else:
            details = jsonUtils.requestItem(url, media_type).get('files', [])
    else: 
        details.append("palyableSingleMedia")
        details.append(url)

    thisDialog.dialogeBG.close()
    thisDialog.dialogeBG = None  
    if strm_type.find('Cinema') != -1 or strm_type.find('YouTube') != -1 or strm_type.find('Movies') != -1:
        try:
            initialize_DialogBG("Movie", "Adding")
            movieList = addMovies(details, strm_name, strm_type)
            dbMovList = kodiDB.writeMovie(movieList)
            j = 100 / len(dbMovList) if len(dbMovList) > 0 else 1
            # Write strms for all values in movieList
            for i in dbMovList:
                thisDialog.dialogeBG.update(j, ADDON_NAME + ": Writing Movies: ",  " Video: " + i[1].rstrip("."))
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
            getTVShowFromList(details, strm_name, strm_type)
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
        
    if strm_type.find('Album') != -1 :
        try:
            initialize_DialogBG("Album", "Adding")
            addAlbum(details, strm_name, strm_type)
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

    for detail in details:
        filetype = detail['filetype']
        label = stringUtils.cleanLabels(detail['label'])
        file = detail['file'].replace("\\\\", "\\")
        strm_name = str(stringUtils.cleanByDictReplacements(strm_name.strip()))
        plot = stringUtils.cleanLabels(detail.get('plot',''))
        art = detail.get('art',{})
        
        if addon.getSetting('Link_Type') == '0':
            link = sys.argv[0] + "?url=" +urllib.quote_plus(stringUtils.uni(file)) + "&mode=" + str(10) + "&name=" +urllib.quote_plus(stringUtils.uni(label)) + "&fanart=" + urllib.quote_plus(art.get('fanart',''))
        else:
            link = file
    
        if strm_type == 'Audio-Single':
            path = os.path.join('Singles', str(strm_name))
            try:
                album = detail['album'].strip()
                artist = stringUtils.cleanByDictReplacements(", ".join(artist.strip() for artist in detailInfo['artist']) if isinstance(detailInfo['artist'], (list, tuple)) else detailInfo['artist'].strip())
                title = detail['title'].strip()
                type = detail['type'].strip()
                filename = str(strm_name + ' - ' + label).strip()
            except:
                filename = str(strm_name + ' - ' + label).strip()
                               
        if strm_type.find('Audio-Album') != -1:
            path = os.path.join(strm_type, strm_name)
            track = detail.get('track', 0)
            try:
                album = detail['album'].strip()
                artist = stringUtils.cleanByDictReplacements(", ".join(artist.strip() for artist in detailInfo['artist']) if isinstance(detailInfo['artist'], (list, tuple)) else detailInfo['artist'].strip())
                title = stringUtils.cleanByDictReplacements(detail['title'].strip())
                type = stringUtils.cleanByDictReplacements(detail['type'].strip())
                filename = stringUtils.cleanByDictReplacements(label.strip())
            except:
                filename = stringUtils.cleanByDictReplacements(label.strip())

        if strm_type in ['Other']:
            path = os.path.join('Other', strm_name)
            filename = str(strm_name + ' - ' + label)             
                              
        if filetype == 'file':
            if strm:
                if strm_type.find('Audio-Albums') != -1:
                    kodiDB.musicDatabase(album, artist, label, path, link, track)
                fileSys.writeSTRM(stringUtils.cleanStrms((path.rstrip("."))), stringUtils.cleanStrms(filename.rstrip(".")) , link)
            else:
                guiTools.addLink(label, file, 10, art, plot, '', '', '', None, '', total=len(details))
        else:
            if strm:
                fillPluginItems(file, media_type, file_type, strm, label, strm_type)
            else:
                guiTools.addDir(label, file, 101, art, plot, '', '', '')

def removeItemsFromMediaList(action='list'):
    utils.addon_log('removingitemsdialog')

    selectedItems = getMediaListDialog()

    if selectedItems is not None:
        fileSys.removeMediaList(selectedItems)
        selectedLabels = [item for index, item in enumerate(items) if index in selectedItems] if selectedItems is not None else []
        xbmcgui.Dialog().notification("Finished deleting:", "{0}".format(", ".join(str(label) for label in selectedLabels)))

def getMediaListDialog():
    thelist = fileSys.readMediaList(purge=False)
    items = []
    for entry in thelist:
        splits = entry.strip().split('|')
        plugin = re.search('%s([^\/\?]*)' % ("plugin:\/\/"), splits[2])
        items.append(stringUtils.getStrmname(splits[1]) + " (" + fileSys.getAddonname(plugin.group(1)) + ")")

    dialog = xbmcgui.Dialog()
    return dialog.multiselect("Select items", items)
    
def addAlbum(contentList, strm_name='', strm_type='Other', PAGINGalbums="1"):
    albumList = []
    dirList = []
    pagesDone = 0
    file = ''
    filetype = ''
    j = 100 / (len(contentList) * int(PAGINGalbums)) if len(contentList) > 0 else 1

    if len(contentList) == 0:
        return contentList

    while pagesDone < int(PAGINGalbums):
        if not contentList[0] == "palyableSingleMedia":
            artThumb = contentList[0].get('art', {})
            aThumb = urlUtils.stripUnquoteURL(artThumb.get('thumb', ''))
                 
            for index, detailInfo in enumerate(contentList):
                art = detailInfo.get('art',{})
                file = detailInfo['file'].replace("\\\\", "\\").encode('utf-8')
                filetype = detailInfo['filetype']
                label = stringUtils.cleanLabels(detailInfo['label'].strip())
                thumb = art.get('thumb','')
                fanart = art.get('fanart','')
                description = detailInfo.get('description', '')
                track = detailInfo.get('track', 0) if detailInfo.get('track', 0) > 0 else index + 1
                duration = detailInfo.get('duration', 0)
                if duration == 0:
                    duration = 200
                
                try:
                    if filetype == 'directory':
                        dirList.append(jsonUtils.requestList(file, 'music').get('files', []))
                        continue

                    if addon.getSetting('Link_Type') == '0': 
                        link = sys.argv[0] + "?url=" + urllib.quote_plus(file) + "&mode=" + str(10) + "&name=" + urllib.quote_plus(label) + "&fanart=" + urllib.quote_plus(fanart)
                    else:
                        link = file

                    try:
                        album = detailInfo['album'].strip()
                        artist = stringUtils.cleanByDictReplacements(", ".join(artist.strip() for artist in detailInfo['artist']) if isinstance(detailInfo['artist'], (list, tuple)) else detailInfo['artist'].strip())
                        artistList = []
                        #Check for Various Artists
                        for i, sArtist in enumerate(contentList):
                            artistList.append(sArtist.get('artist'))
                        if len(artistList) > 1:
                            try:
                                if artistList[0] != artistList[1] and artistList[1] != artistList[2]:
                                    artist = 'Various Artists'
                            except IndexError:
                                if artistList[0] != artistList[1]:
                                    artist = 'Various Artists'
                        title = stringUtils.cleanByDictReplacements(detailInfo['title'].strip())
                        type = stringUtils.cleanByDictReplacements(detailInfo['type'].strip())
                        filename = stringUtils.cleanByDictReplacements(label.strip())
                    except:
                        filename = stringUtils.cleanByDictReplacements(label.strip())
                        pass

                    thisDialog.dialogeBG.update(j, ADDON_NAME + ": Writing File: ",  " Title: " + label)
                    path = os.path.join(strm_type, artist, strm_name.replace('++RenamedTitle++', ''))
                    if album and artist and label and path and link and track:  
                        albumList.append([path, label, link, album, artist, track, duration, thumb])
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
            contentList = []
            if pagesDone < int(PAGINGalbums) and len(dirList) > 0:
                contentList = [item for sublist in dirList for item in sublist]
                dirList = []            

            if False:     
                try:
                    urlUtils.downloadThumb(aThumb, album, os.path.join(STRM_LOC, strm_type, artist)) 
                except:
                    pass             
        else:
            albumList.append([os.path.join(strm_type, stringUtils.getStrmname(strm_name) , label.strip()), str(stringUtils.cleanByDictReplacements(label.strip())), link])
            pagesDone = int(PAGINGalbums)

    try:
        # Write strms for all values in albumList
        thelist = fileSys.readMediaList(purge=False)
        items = []
        for entry in thelist:
            splits = entry.strip().split('|')
            splitsstrm = splits[0]
            splitsname = splits[1]
            if splitsstrm.find('Album') != -1 and splitsname.find(strm_name) != -1:
                url = splits[2]
                cType = splits[0]
                albumartist = artist
                fileSys.rewriteMediaList(url, strm_name, albumartist, cType)
        for i in albumList:
            fullpath, fileModTime = fileSys.writeSTRM(path, stringUtils.cleanStrms(i[1].rstrip(".")) , i[2] + "|" + i[1])
            kodiDB.musicDatabase(i[3], i[4], i[1], i[0], i[2], i[5], i[6], aThumb, fileModTime)
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
    file = ''
    filetype = ''
    j = len(contentList) * int(PAGINGMovies) / 100

    if len(contentList) == 0:
        return contentList
    
    while pagesDone < int(PAGINGMovies):
        if not contentList[0] == "palyableSingleMedia":
            for detailInfo in contentList:
                file = detailInfo['file'].replace("\\\\", "\\")
                filetype = detailInfo['filetype']
                label = detailInfo['label'].strip()
                thumbnail = detailInfo.get('thumbnail', '')
                fanart = detailInfo.get('fanart', '')
                description = detailInfo.get('description', '')
                provGeneral = re.search('%s([^\/\?]*)' % ("plugin:\/\/"), file)
                provXST = re.search('%s(.*)'"\&function"'' % (r"site="), file)
            
                try:                        
                    if provGeneral:
                        listName = fileSys.getAddonname(provGeneral.group(1))
                        if provXST:
                            listName = listName + ": " + provXST.group(1)               
                    
                    if label and strm_name:                                              
                        label = stringUtils.cleanByDictReplacements(label)           
                        if HIDE_tile_in_OV == "true" and not label.find("[OV]") == -1:  
                            get_title_with_OV = 0
                        else:
                            get_title_with_OV = 1

                        thisDialog.dialogeBG.update(j, ADDON_NAME + ": Getting Movies: ",  " Video: " + label)
                        if filetype == 'file' and get_title_with_OV == 1:
                            movieList.append([stringUtils.getMovieStrmPath(strm_type, strm_name, label), stringUtils.cleanByDictReplacements(stringUtils.getStrmname(label)), file, listName])
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
                contentList = jsonUtils.requestList(file, 'video').get('files', [])
            else:
                pagesDone = int(PAGINGMovies)            
        else:
            provGeneral = re.search('%s([^\/\?]*)' % ("plugin:\/\/"), contentList[1])
            provXST = re.search('%s(.*)'"\&function"'' % (r"site="), contentList[1])

            if provGeneral:
                listName = provGeneral.group(1)
                if provXST:
                    listName = listName + ": " + provXST.group(1)
            movieList.append([stringUtils.getMovieStrmPath(strm_type, strm_name), stringUtils.cleanByDictReplacements(stringUtils.getStrmname(strm_name)), contentList[1], listName])
            pagesDone = int(PAGINGMovies)

    return movieList
 
def getTVShowFromList(showList, strm_name='', strm_type='Other', pagesDone=0):
    dirList = []
    episodesList = []
    
    while pagesDone < int(PAGINGTVshows):
        strm_type = strm_type.replace('Shows-Collection', 'TV-Shows')
        try:
            for detailInfo in showList:
                filetype = detailInfo.get('filetype', '')
                if filetype != '':
                    file = detailInfo.get('file', '').strip()
                    episode = detailInfo.get('episode', -1)
                    season = detailInfo.get('season', -1)
                    label = detailInfo.get('label', None).strip()       
    
                    if not fileSys.isInMediaList(stringUtils.getStrmname(strm_name), file, strm_type) and label != None and label != ">>>" and label != "" and file.find("playMode=play") == "-1":            
                        fileSys.writeMediaList(files, label, strm_type)
                    
                    if filetype == 'directory':
                        dirList.append(jsonUtils.requestList(file, 'video').get('files', []))
                        continue
    
                    if season > -1 and episode > -1 and filetype == 'file': 
                        episodesList.append(detailInfo)
                
            step = float(100.0 / len(episodesList) if len(episodesList) > 0 else 1)
            if pagesDone == 0:
                thisDialog.dialogeBG.update(int(step), "Initialisation of TV-Shows: " + stringUtils.getStrmname(strm_name))
            else:
                thisDialog.dialogeBG.update(int(step), "Page: " + str(pagesDone) + " " + stringUtils.getStrmname(strm_name))
            for index, episode in enumerate(episodesList):
                pagesDone = getEpisode(episode, strm_name, strm_type, pagesDone=pagesDone)
                thisDialog.dialogeBG.update(int(step * (index + 1)))
                                   
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
        episodesList = []
        showList = []
        if pagesDone < int(PAGINGTVshows) and len(dirList) > 0:
            showList = [item for sublist in dirList for item in sublist]
            dirList = []                

def getEpisode(episode_item, strm_name, strm_type, j=0, pagesDone=0):
    try:
        episodeList = []

        utils.addon_log("detailInfo: " + str(episode_item))
        file = episode_item['file']
        filetype = episode_item['filetype'].replace("\\\\", "\\")
        label = episode_item['label']
        thumbnail = episode_item.get('thumbnail','')
        fanart = episode_item.get('fanart','')
        description = stringUtils.cleanLabels(episode_item.get('description',''))
        episode = str(episode_item['episode'])
        season = str(episode_item['season'])
        showtitle = stringUtils.removeHTMLTAGS(episode_item.get('showtitle', ''))
        provGeneral = re.search('%s([^\/\?]*)' % ("plugin:\/\/"), file)
        provXST = re.search('%s(.*)'"\&function"'' % (r"site="), file)
        listName = strm_name
        strm_name = str(stringUtils.cleanByDictReplacements(strm_name.strip()))
        episodesHDF = re.search('Folge.(\\d+)&', file)
        
        if provGeneral:
            listName = fileSys.getAddonname(provGeneral.group(1))
            if provXST:
                listName = listName + ": " + provXST.group(1)
        
        if file.find("hdfilme") != -1 and episodesHDF:
            episode = re.search('Folge.(\\d+)&', file).group(1)
    
        if strm_name.find("++RenamedTitle++") != -1 or showtitle == '':
            showtitle = stringUtils.getStrmname(strm_name)
        if showtitle != "" and strm_type != "":
            episodeList.append([strm_type, str('s' + season), str('e' + episode), file, stringUtils.cleanByDictReplacements(showtitle.strip()), listName])                   
    except IOError as (errno, strerror):
        print ("I/O error({0}): {1}").format(errno, strerror)
    except ValueError:
        print ("No valid integer in line.")
    except:
        guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". See your Kodi.log!"))
        utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
        print ("Unexpected error:"), sys.exc_info()[0]
        raise

    dbEpisode = kodiDB.writeShow(episodeList)
    
    for i in dbEpisode:        
        fileSys.writeSTRM(os.path.join(stringUtils.cleanStrms((i[0].rstrip("."))),stringUtils.cleanStrms(i[1].rstrip("."))), stringUtils.cleanStrms(i[3] + i[4]) , "plugin://plugin.video.osmosis/?url=plugin&mode=10&mediaType=show&episode=" + i[3] + i[4] + "&showid=" + str(i[2]) + "|" + i[1])
    return pagesDone
    
def getData(url, fanart):
    utils.addon_log('getData, url = ' + cType)

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
