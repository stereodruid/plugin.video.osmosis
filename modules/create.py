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
import urllib
import utils
import copy
import xbmc, xbmcgui, xbmcaddon

from modules import fileSys
from modules import guiTools
from modules import jsonUtils
from modules import stringUtils
from modules import urlUtils
from modules import kodiDB
from modules import tvdb

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
ADDON_NAME = addon.getAddonInfo('name')
HIDE_title_in_OV = addon.getSetting('Hide_tilte_in_OV')
PAGINGTVshows = addon.getSetting('paging_tvshows')
PAGINGMovies = addon.getSetting('paging_movies')
STRM_LOC = xbmc.translatePath(addon.getSetting('STRM_LOC'))
NOE0_STRMS_EXPORT = addon.getSetting('noE0_Strms_Export')
SEARCH_THETVDB = int(addon.getSetting('search_thetvdb'))

thisDialog = sys.modules[__name__]
thisDialog.dialogeBG = None
thisDialog.dialoge = None

def initialize_DialogBG(mess1, mess2, barType="BG"):
    if barType == "BG":
        if not thisDialog.dialogeBG:
            thisDialog.dialogeBG = xbmcgui.DialogProgressBG()
            thisDialog.dialogeBG.create("OSMOSIS: " + mess1 + ": " , " " + mess2)

    else:
        if not thisDialog.dialoge:
            thisDialog.dialoge = xbmcgui.DialogProgress()
            thisDialog.dialoge.create("OSMOSIS: " + mess1 + ": " , " " + mess2)

def fillPlugins(cType='video'):
    json_query = ('{"jsonrpc":"2.0","method":"Addons.GetAddons","params":{"type":"xbmc.addon.%s","properties":["name","path","thumbnail","description","fanart","summary", "extrainfo", "enabled"]}, "id": 1 }' % cType)
    json_details = jsonUtils.sendJSON(json_query)
    for addon in sorted([addon for addon in json_details["addons"] if addon['enabled'] == True], key=lambda json: json['name'].lower()):
        utils.addon_log('fillPlugins entry: %s' % (addon))
        addontypes = []
        for info in addon['extrainfo']:
            if info['key'] == 'provides':
                addontypes = info['value'].split(" ")
                break

        if cType in addontypes and not addon['addonid'] == addon_id:
            art = {'thumb': addon['thumbnail'], 'fanart': addon['fanart']}
            guiTools.addDir(addon['name'], 'plugin://' + addon['addonid'], 101, art, addon['description'], cType, 'date', 'credits')

def fillPluginItems(url, media_type='video', file_type=False, strm=False, strm_name='', strm_type='Other', showtitle='None', name_parent='', name_orig=''):
    details = []
    name_orig_from_url, plugin_id = stringUtils.parseMediaListURL(url)
    name_orig = name_orig_from_url if name_orig_from_url != '' else name_orig

    if plugin_id.find("playMode=play") == -1:
        if not file_type:
            details = jsonUtils.requestList(plugin_id, media_type).get('files', [])
            retry_count=1
            while len(details) == 0 and retry_count <= 3:
                utils.addon_log('requestList: try=%d data = %s)' % (retry_count, details))
                details = jsonUtils.requestList(plugin_id, media_type).get('files', [])
                retry_count=retry_count+1
        else:
            details = jsonUtils.requestItem(plugin_id, media_type).get('files', [])
            retry_count=1
            while len(details) == 0 and retry_count <= 3:
                utils.addon_log('requestItem: try=%d data = %s)' % (retry_count, details))
                details = jsonUtils.requestItem(plugin_id, media_type).get('files', [])
                retry_count=retry_count+1
    else:
        details.append("palyableSingleMedia")
        details.append(plugin_id)

    if strm_type.find('Cinema') != -1 or strm_type.find('YouTube') != -1 or strm_type.find('Movies') != -1:
        initialize_DialogBG("Movie", "Adding")
        addMovies(details, strm_name, strm_type, name_orig=name_orig)
        thisDialog.dialogeBG.close()
        thisDialog.dialogeBG = None
        return

    if strm_type.find('TV-Show') != -1 or strm_type.find('Shows-Collection') != -1:
        initialize_DialogBG("Adding TV-Shows", "working..")
        getTVShowFromList(details, strm_name, strm_type, name_orig=name_orig)
        thisDialog.dialogeBG.close()
        thisDialog.dialogeBG = None
        return

    if strm_type.find('Album') != -1 :
        initialize_DialogBG("Album", "Adding")
        addAlbum(details, strm_name, strm_type)
        thisDialog.dialogeBG.close()
        thisDialog.dialogeBG = None
        return
    for detail in details:
        filetype = detail['filetype']
        label = detail['label']
        file = detail['file'].replace("\\\\", "\\")
        strm_name = stringUtils.cleanByDictReplacements(strm_name.strip())
        plot = detail.get('plot', '')
        art = detail.get('art', {})

        if addon.getSetting('Link_Type') == '0':
            link = "{0}?{1}".format(sys.argv[0], urllib.urlencode({'url': file.encode('utf-8'), 'mode': 10, 'name': label.encode('utf-8'), 'fanart': art.get('fanart', '').encode('utf-8')}))
        else:
            link = file

        if strm_type == 'Audio-Single':
            path = os.path.join('Singles', strm_name)
            try:
                album = detail['album'].strip()
                artist = stringUtils.cleanByDictReplacements(", ".join(artist.strip() for artist in detailInfo['artist']) if isinstance(detailInfo['artist'], (list, tuple)) else detailInfo['artist'].strip())
                filename = (strm_name + ' - ' + label).strip()
            except:
                filename = (strm_name + ' - ' + label).strip()

        if strm_type in ['Other']:
            path = os.path.join('Other', strm_name)
            filename = (strm_name + ' - ' + label)

        if filetype == 'file':
            if strm:
                if strm_type.find('Audio-Albums') != -1:
                    kodiDB.musicDatabase(album, artist, label, path, link, track)
                fileSys.writeSTRM(stringUtils.cleanStrms((path.rstrip("."))), stringUtils.cleanStrms(filename.rstrip(".")) , link)
            else:
                guiTools.addLink(label, file, 10, art, plot, '', '', '', None, '', total=len(details), type=detail.get('type', None), year=detail.get('year', None))
        else:
            if strm:
                fillPluginItems(file, media_type, file_type, strm, label, strm_type, name_orig=name_orig)
            else:
                if isinstance (name_parent,str):
                    name_parent=name_parent.decode('utf-8')
                guiTools.addDir(label, file, 101, art, plot, '', '', '', name_parent=name_parent, type=detail.get('type', None))

def addToMedialist(params):
    # A dialog to rename the Change Title for Folder and MediaList entry:
    name_orig = params.get('name')
    name = re.sub('( - |, )*[sS](taffel|eason) \d+.*', '', name_orig)

    if name != name_orig:
        tvshow_detected = True
    else:
        tvshow_detected = False
    if name == '':
        name = params.get('name_parent')
        name_orig = '%s - %s' % (name, name_orig)
    if params.get('type', None) == 'movie' and params.get('year',  None):
        name = name + ' (%s)' % params.get('year', None)
    if params.get('noninteractive', False) == False:
        selectAction = ['Continue with original Title: %s' % name, 'Rename Title', 'Get Title from Medialist']
        if not fileSys.writeTutList("select:Rename"):
            tutWin = ["Adding content to your library",
                      "You can rename your Movie, TV-Show or Music title.",
                      "To make your scraper recognize the content, some times it is necessary to rename the title.",
                      "Be careful, wrong title can also cause that your scraper can't recognize your content."]
            xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])
        choice = guiTools.selectDialog('Title for MediaList entry: %s' % name_orig, selectAction)
    else:
        choice = 0

    if choice != -1:
        cType = params.get('cType', None)
        if choice == 1 or name == None or name == '':
            name = guiTools.editDialog(name).strip()
            name = "{0}++RenamedTitle++".format(name) if name else name

        if choice == 2:
            cTypeFilter=None
            if tvshow_detected or params.get('type', None) == 'tvshow':
                cTypeFilter='TV-Shows'
            elif params.get('type', None) == 'movie':
                cTypeFilter='Movies'
            item = guiTools.mediaListDialog(False, False, header_prefix='Get Title from Medialist for %s' % name_orig, cTypeFilter=cTypeFilter,preselect_name=name)
            splits = item.get('entry').split('|') if item else None
            name = splits[1] if splits else None
            cType = splits[0] if splits else None

        if name:
            url = params.get('url')
            if not cType:
                if not fileSys.writeTutList("select:ContentTypeLang"):
                    tutWin = ["Adding content to your library",
                              "Now select your content type.",
                              "Select language or YouTube type.",
                              "Wait for done message."]
                    xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])

                if tvshow_detected or params.get('type', None) == 'tvshow':
                    cType = guiTools.getTypeLangOnly('TV-Shows')
                elif params.get('type', None) == 'movie':
                    cType = guiTools.getTypeLangOnly('Movies')
                else:
                    cType = guiTools.getType(url)
            if cType != -1:
                if params.get('filetype', 'directory') == 'file':
                    url += '&playMode=play'
                fileSys.writeMediaList('name_orig=%s;%s' % (name_orig, url), name, cType)
                xbmcgui.Dialog().notification(cType, name.replace('++RenamedTitle++', ''), xbmcgui.NOTIFICATION_INFO, 5000, False)

                try:
                    plugin_id = re.search('%s([^\/\?]*)' % ("plugin:\/\/"), url)
                    if plugin_id:
                        module = moduleUtil.getModule(plugin_id.group(1))
                        if module and hasattr(module, 'create'):
                            url = module.create(name, url, 'video')
                except:
                    pass
                fillPluginItems(url, strm=True, strm_name=name, strm_type=cType, name_orig=name_orig)
                xbmcgui.Dialog().notification('Writing items...', "Done", xbmcgui.NOTIFICATION_INFO, 5000, False)

def addMultipleSeasonToMediaList(params):
    name = params.get('name')
    url = params.get('url')
    selectAction = ['Continue with original Title: %s' % name, 'Rename Title', 'Get Title from Medialist']
    if not fileSys.writeTutList("select:Rename"):
        tutWin = ["Adding content to your library",
                  "You can rename your Movie, TV-Show or Music title.",
                  "To make your scraper recognize the content, some times it is necessary to rename the title.",
                  "Be careful, wrong title can also cause that your scraper can't recognize your content."]
        xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])
    choice = guiTools.selectDialog('Title for MediaList entry: %s' % name, selectAction)
    if choice != -1:
        cType = None
        if choice == 1 or name == None or name == '':
            name = guiTools.editDialog(name).strip()
            name = "{0}++RenamedTitle++".format(name) if name else name

        if choice == 2:
            item = guiTools.mediaListDialog(False, False, header_prefix='Get Title from Medialist for %s' % name, preselect_name=name)
            splits = item.get('entry').split('|') if item else None
            name = splits[1] if splits else None
            cType = splits[0] if splits else None

    if not cType:
        cType = guiTools.getTypeLangOnly('TV-Shows')

    details = jsonUtils.requestList(url, 'video').get('files', [])
    retry_count=1
    while len(details) == 0 and retry_count <= 3:
        utils.addon_log('requestList: try=%d data = %s)' % (retry_count, details))
        details = jsonUtils.requestList(url, 'video').get('files', [])
        retry_count=retry_count+1
    seasonList=[]
    for detail in details:
        file = detail['file'].replace("\\\\", "\\")
        filetype = detail['filetype']
        label = detail['label']
        if label.find('COLOR') != -1:
            label=stringUtils.cleanLabels(label) + ' (*)'
        showtitle = detail['showtitle']
        if filetype == 'directory':
            seasonList.append({'name': label.encode('utf-8'), 'name_parent': showtitle.encode('utf-8'), 'url': file.encode('utf-8'), 'cType': cType, 'noninteractive': True})

    sItems = sorted([item.get('name') for item in seasonList], key=lambda k: utils.key_natural_sort(k.lower()))
    preselect = [i for i, item in enumerate(sItems) if item.find(' (*)') == -1]
    selectedItemsIndex = guiTools.selectDialog("Select Seasons to add for %s" % showtitle, sItems, multiselect=True, preselect=preselect)
    seasonList = [item for item in seasonList for index in selectedItemsIndex if item.get('name') == sItems[index]] if selectedItemsIndex and len(selectedItemsIndex) > 0 else None
    if seasonList and len(seasonList) > 0:
        for season in seasonList:
            addToMedialist(season)


def removeItemsFromMediaList(action='list'):
    utils.addon_log('removingitemsdialog')

    selectedItems = guiTools.mediaListDialog(header_prefix='Remove item(s) from Medialist', multiselect=True)

    if selectedItems:
        fileSys.removeMediaList(selectedItems)
        selectedLabels = sorted(list(dict.fromkeys([item.get('name') for item in selectedItems])), key=lambda k: k.lower())
        xbmcgui.Dialog().notification("Finished deleting:", "{0}".format(", ".join(label for label in selectedLabels)))

def addAlbum(contentList, strm_name='', strm_type='Other', PAGINGalbums="1"):
    strm_name = stringUtils.getStrmname(strm_name)
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
                art = detailInfo.get('art', {})
                file = detailInfo['file'].replace("\\\\", "\\")
                filetype = detailInfo['filetype']
                label = detailInfo['label'].strip().encode("utf8")
                thumb = art.get('thumb', '')
                fanart = art.get('fanart', '')
                track = detailInfo.get('track', 0) if detailInfo.get('track', 0) > 0 else index + 1
                album = detailInfo['album'].strip().encode("utf8")
                duration = detailInfo.get('duration', 0)

                if filetype == 'directory':
                    dirList.append(jsonUtils.requestList(file, 'music').get('files', []))
                    continue

                if duration == 0:
                    duration = 200

                if addon.getSetting('Link_Type') == '0':
                    link = "{0}?{1}".format(sys.argv[0], urllib.urlencode({'url': file, 'mode': 10, 'name': label, 'fanart': fanart}))
                else:
                    link = file

                # Check for Various Artists
                artistList = []
                for i, sArtist in enumerate(contentList):
                    for artist in sArtist.get('artist'):
                        if artist.encode("utf8") not in artistList:
                            artistList.append(artist.encode("utf8"))

                if len(artistList) == 1:
                    artist = artistList[0]
                else:
                    artist = 'Various Artists'.encode("utf8")

                thisDialog.dialogeBG.update(j, ADDON_NAME + ": Writing File: ", " Title: " + label)
                path = os.path.join(strm_type, stringUtils.cleanStrmFilesys(artist), stringUtils.cleanStrmFilesys(strm_name.decode('utf8'))).encode('utf8')
                if album and artist and label and path and link and track:
                    albumList.append({'path': path, 'label': label, 'link': link, 'album': album, 'artist': artist, 'track': track, 'duration': duration, 'thumb': thumb})
                j = j + 100 / (len(contentList) * int(PAGINGalbums))

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
            albumList.append({'path': os.path.join(strm_type, strm_name.decode('utf8'), label).encode('utf8'), 'label': stringUtils.cleanByDictReplacements(label), 'link': link})
            pagesDone = int(PAGINGalbums)

    # Write strms for all values in albumList
    thelist = fileSys.readMediaList()
    for entry in thelist:
        splits = entry.strip().split('|')
        splitsstrm = splits[0]
        splitsname = splits[1]
        if splitsstrm.find('Album') != -1 and splitsname.find(strm_name) != -1:
            url = splits[2]
            cType = splits[0]
            fileSys.writeMediaList(url, strm_name, cType, albumartist=artist)
    for album in albumList:
        strm_link = "%s|%s" % (album.get('link'), album.get('label')) if addon.getSetting('Link_Type') == '0' else album.get('link')
        fullpath, fileModTime = fileSys.writeSTRM(album.get('path'), stringUtils.cleanStrms(album.get('label').rstrip(".")) , strm_link)
        kodiDB.musicDatabase(album.get('album'), album.get('artist'), album.get('label'), album.get('path'), album.get('link'), album.get('track'), album.get('duration'), aThumb, fileModTime)
    thisDialog.dialogeBG.close()

    return albumList

def addMovies(contentList, strm_name='', strm_type='Other', provider="n.a", name_orig=''):
    movieList = []
    pagesDone = 0
    file = ''
    filetype = ''
    j = len(contentList) * int(PAGINGMovies) / 100

    if len(contentList) == 0:
        return

    while pagesDone < int(PAGINGMovies):
        if not contentList[0] == "palyableSingleMedia":
            for detailInfo in contentList:
                file = detailInfo.get('file').replace("\\\\", "\\") if detailInfo.get('file', None) else None
                if name_orig != '' and file.find('name_orig=') == -1:
                    file = 'name_orig=%s;%s' % (name_orig , file if isinstance(file, str) else file.encode('utf-8'))
                filetype = detailInfo.get('filetype', None)
                label = detailInfo.get('label').encode("utf-8") if detailInfo.get('label', None) else None
                imdbnumber = detailInfo.get('imdbnumber').strip() if detailInfo.get('imdbnumber', None) else None

                if label and strm_name:
                    label = stringUtils.cleanLabels(label)
                    get_title_with_OV = True
                    if HIDE_title_in_OV == "true":
                        if re.search('(\WOV\W)', label):
                            get_title_with_OV = False

                    provider = stringUtils.getProviderId(file)

                    thisDialog.dialogeBG.update(j, ADDON_NAME + ": Getting Movies: ", " Video: " + label)
                    if filetype is not None and filetype == 'file' and get_title_with_OV == True:
                        m_path = stringUtils.getMovieStrmPath(strm_type, strm_name, label)
                        m_title = stringUtils.getStrmname(label)
                        movieList.append({'path': m_path, 'title':  m_title, 'url': file, 'provider': provider.get('providerId'), 'imdbnumber': imdbnumber})
                    j = j + len(contentList) * int(PAGINGMovies) / 100

            pagesDone += 1
            if filetype != '' and filetype != 'file' and pagesDone < int(PAGINGMovies):
                contentList = jsonUtils.requestList(file, 'video').get('files', [])
                retry_count=1
                while len(contentList) == 0 and retry_count <= 3:
                    utils.addon_log('requestList: try=%d data = %s)' % (retry_count, details))
                    contentList = jsonUtils.requestList(file, 'video').get('files', [])
                    retry_count=retry_count+1
            else:
                pagesDone = int(PAGINGMovies)
        else:
            provider = stringUtils.getProviderId(contentList[1])
            url = contentList[1]
            if name_orig != '' and file.find('name_orig=') == -1:
                url = 'name_orig=%s;%s' % (name_orig , url if isinstance(url, str) else url.encode('utf-8'))
            m_path = stringUtils.getMovieStrmPath(strm_type, strm_name)
            m_title = stringUtils.getStrmname(strm_name)
            movieList.append({'path': m_path, 'title':  m_title, 'url': url, 'provider': provider.get('providerId')})
            pagesDone = int(PAGINGMovies)

    if addon.getSetting('Link_Type') == '0':
        movieList = kodiDB.writeMovie(movieList)

    j = 100 / len(movieList) if len(movieList) > 0 else 1
    # Write strms for all values in movieList
    for movie in movieList:
        thisDialog.dialogeBG.update(j, ADDON_NAME + ": Writing Movies: ", movie.get('title'))
        strm_link = "plugin://%s/?url=plugin&mode=10&mediaType=movie&id=%d|%s" % (addon_id, movie.get('movieID'), movie.get('title')) if addon.getSetting('Link_Type') == '0' else movie.get('url')
        utils.addon_log("write movie = %s" % (movie))
        fileSys.writeSTRM(stringUtils.cleanStrms(movie.get('path')), stringUtils.cleanStrms(movie.get('title')), strm_link)

        j = j + 100 / len(movieList)

def getTVShowFromList(showList, strm_name='', strm_type='Other', pagesDone=0, name_orig=''):
    dirList = []
    episodesList = []

    lang = None
    if strm_type.lower().find('other') == -1:
        lang = strm_type[strm_type.find('(') + 1:strm_type.find(')')]
    showtitle_tvdb = None
    showtitle = stringUtils.getStrmname(strm_name)
    if isinstance (showtitle,str):
        showtitle = showtitle.decode("utf-8")
    if (SEARCH_THETVDB == 2):
        show_data = tvdb.getShowByName(showtitle, lang)
        if show_data:
            showtitle = show_data.get('seriesName', showtitle)
            showtitle_tvdb = showtitle

    while pagesDone < int(PAGINGTVshows):
        strm_type = strm_type.replace('Shows-Collection', 'TV-Shows')

        for detailInfo in showList:
            filetype = detailInfo.get('filetype', None)
            file = detailInfo.get('file', None)

            if filetype:
                if filetype == 'directory':
                    retry_count=1
                    json_reply=jsonUtils.requestList(file, 'video').get('files', [])
                    while len(json_reply) == 0 and retry_count <= 3:
                        utils.addon_log('requestList: try=%d data = %s)' % (retry_count, json_reply))
                        json_reply=jsonUtils.requestList(file, 'video').get('files', [])
                        retry_count=retry_count+1
                    dirList.append(json_reply)
                    continue
                elif filetype == 'file':
                    if (SEARCH_THETVDB == 2 or (SEARCH_THETVDB == 1 and detailInfo.get('season', -1) == -1 or detailInfo.get('episode', -1) == -1)) and  NOE0_STRMS_EXPORT == "false" or detailInfo.get('episode') > 0:
                        episodetitle = detailInfo.get('title')
                        episodeseason = detailInfo.get('season', -1)
                        episode = detailInfo.get('episode', -1)

                        if showtitle and showtitle != '' and episodetitle and episodetitle != '':

                            eptitle = episodetitle
                            eptitle = eptitle.replace(u"\u201e", "'")
                            eptitle = eptitle.replace(u"\u201c", "'")
                            eptitle = eptitle.replace(u"\u2013", "-")
                            utils.addon_log_notice('search tvdb for "%s": "S%02dE%02d - %s" (lang=%s)' % (showtitle, episodeseason, episode, eptitle, lang))
                            data = tvdb.getEpisodeByName(showtitle, episodeseason, episode, eptitle, lang)

                            if data:
                                detailInfo['season'] = data.get('season')
                                detailInfo['episode'] = data.get('episode')
                                detailInfo['episodeName'] = data.get('episodeName',None)
                                utils.addon_log_notice('found tvdb entry for "%s": "S%02dE%02d - %s" matched to "S%02dE%02d - %s"' %
                                                       (showtitle, episodeseason, episode, episodetitle,
                                                       detailInfo['season'], detailInfo['episode'], detailInfo['episodeName'] ))
                            else:
                                detailInfo['season'] = -1
                                detailInfo['episode'] = -1
                                utils.addon_log_notice('no tvdb entry found for "%s": "S%02dE%02d - %s"' %
                                                       (showtitle, episodeseason, episode, episodetitle ))

                    get_title_with_OV = True
                    if HIDE_title_in_OV == "true":
                        label = detailInfo.get('label').strip().encode("utf-8") if detailInfo.get('label', None) else None
                        label = stringUtils.cleanLabels(label)
                        if re.search('(\WOV\W)', label):
                            get_title_with_OV = False

                    if detailInfo.get('season', -1) > -1 and detailInfo.get('episode', -1) > -1:
                        if NOE0_STRMS_EXPORT == "false" or detailInfo.get('episode') > 0 and get_title_with_OV == True:
                            if  episodetitle.find('Teil 1 und 2') >= 0 or episodetitle.find('Parts 1 & 2') >= 0 :
                                utils.addon_log_notice('found tvdb entry for "%s": "S%02dE%02d - %s" (multi) matched to "S%02dE%02d - %s"' %
                                    (showtitle, episodeseason, episode, episodetitle,
                                    detailInfo['season'], detailInfo['episode'], detailInfo['episodeName'] ))
                                data = tvdb.getEpisodeByName(showtitle, episodeseason, episode+1, re.sub('(Teil 1 und 2|Parts 1 & 2)', '(2)', eptitle), lang)
                                if data:
                                    utils.addon_log_notice('found tvdb entry for "%s": "S%02dE%02d - %s" (multi) matched to "S%02dE%02d - %s"' %
                                        (showtitle, episodeseason, episode, episodetitle,
                                        detailInfo['season'], detailInfo['episode']+1, data.get('episodeName',None) ))
                                detailInfo['multi_episode'] = True
                                detailInfo['episode']=[detailInfo['episode'], detailInfo['episode']+1]

                            episodetitles = filter(None, re.split(' / | , ', episodetitle))
                            if episodetitles[0] != episodetitle and not re.search(' *(-|\(|:)* *([tT]eil|[pP]art|[pP]t\.) (\d+|\w+)\)*', episodetitle):
                                utils.addon_log_notice('check multi episode "%s": "S%02dE%02d - %s"' % (showtitle, episodeseason, episode, episodetitle))
                                seasonm=[]
                                episodem=[]
                                episodeNamem=[]
                                for e, eptitle in enumerate(episodetitles):
                                    data = tvdb.getEpisodeByName(showtitle, episodeseason, episode, eptitle, lang)
                                    if data:
                                        seasonm.append(data.get('season'))
                                        episodem.append(data.get('episode'))
                                        episodeNamem.append(data.get('episodeName'))

                                if all(x == seasonm[0] for x in seasonm) and len(set(episodem)) == len(episodetitles):
                                    detailInfo['multi_episode'] = True
                                    detailInfo['episode']=episodem
                                    for e, ep in enumerate(episodem):
                                        utils.addon_log_notice('found tvdb entry for "%s": "S%02dE%02d - %s" (multi) matched to "S%02dE%02d - %s"' %
                                            (showtitle, episodeseason, episode, episodetitle,
                                            detailInfo['season'], episodem[e], episodeNamem[e]))

                            episodesList.append(detailInfo)

        step = float(100.0 / len(episodesList) if len(episodesList) > 0 else 1)
        if pagesDone == 0:
            thisDialog.dialogeBG.update(int(step), "Initialisation of TV-Shows: " + stringUtils.getStrmname(strm_name))
        else:
            thisDialog.dialogeBG.update(int(step), "Page: %d %s" % (pagesDone, stringUtils.getStrmname(strm_name)))

        split_episode=0
        for index, episode in enumerate(episodesList):
            if index > 0:
                if season_prev == episode.get('season') and episode_prev == episode.get('episode'):
                    episodesList[index-1]['split_episode']=split_episode+1
                    episodesList[index]['split_episode']=split_episode+2
                    split_episode=split_episode+1
                else:
                    if split_episode > 0:
                        split_episode_names = []
                        for s in range(0, split_episode+1):
                            split_episode_names.insert(0, episodesList[index-s-1]['title'])
                        utils.addon_log_notice('Split Episode for %s: "%s" matched to "S%02dE%02d - %s"' % (showtitle, ', '.join(split_episode_names),
                                            episodesList[index-split_episode].get('season',None),
                                            episodesList[index-split_episode].get('episode',None),
                                            episodesList[index-split_episode].get('episodeName',None)))
                    split_episode=0
            if showtitle_tvdb:
                episodesList[index]['showtitle'] = showtitle_tvdb
            season_prev=episode.get('season')
            episode_prev=episode.get('episode')

        for index, episode in enumerate(episodesList):
            pagesDone = getEpisode(episode, strm_name, strm_type, pagesDone=pagesDone, name_orig=name_orig)
            thisDialog.dialogeBG.update(int(step * (index + 1)))

        pagesDone += 1
        episodesList = []
        showList = []
        if pagesDone < int(PAGINGTVshows) and len(dirList) > 0:
            showList = [item for sublist in dirList for item in sublist]
            dirList = []

def getEpisode(episode_item, strm_name, strm_type, j=0, pagesDone=0, name_orig=''):
    episode = None

    utils.addon_log("detailInfo: %s" % (episode_item))
    file = episode_item.get('file', None)

    if name_orig != '' and file.find('name_orig=') == -1:
        file = 'name_orig=%s;%s' % (name_orig , file if isinstance(file, str) else file.encode('utf-8'))
    episode = episode_item.get('episode', -1)
    split_episode = episode_item.get('split_episode', -1)
    multi_episode = episode_item.get('multi_episode', False)
    season = episode_item.get('season', -1)
    if split_episode > 0:
        strSeasonEpisode = 's%de%d.%d' % (season, episode, split_episode)
    else:
        if multi_episode:
            strSeasonEpisode = ('s%de' % season) + '-'.join(map(str,episode))
        else:
            strSeasonEpisode = 's%de%d' % (season, episode)
    showtitle = episode_item.get('showtitle', None).encode("utf-8")
    provider = stringUtils.getProviderId(file)

    if showtitle is not None and showtitle != "" and strm_type != "":
        path = os.path.join(strm_type, stringUtils.cleanStrmFilesys(showtitle)) if strm_name.find('++RenamedTitle++') == -1 else os.path.join(strm_type, stringUtils.cleanStrmFilesys(stringUtils.getStrmname(strm_name)))
        episode = {'path': path, 'strSeasonEpisode': strSeasonEpisode, 'url': file, 'tvShowTitle': showtitle, 'provider': provider.get('providerId')} if strm_name.find('++RenamedTitle++') == -1 else {'path': path, 'strSeasonEpisode': strSeasonEpisode, 'url': file, 'tvShowTitle': stringUtils.getStrmname(strm_name), 'provider': provider.get('providerId')}

        if addon.getSetting('Link_Type') == '0':
            episode = kodiDB.writeShow(episode)

        if episode is not None:
            strm_link = 'plugin://%s/?url=plugin&mode=10&mediaType=show&episode=%s&showid=%d|%s' % (addon_id, episode.get('strSeasonEpisode'), episode.get('showID'), episode.get('tvShowTitle')) if addon.getSetting('Link_Type') == '0' else episode.get('url')
            fileSys.writeSTRM(episode.get('path'), episode.get('strSeasonEpisode'), strm_link)

    return pagesDone
