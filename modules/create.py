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


def fillPluginItems(url, media_type='video', file_type=False, strm=False, strm_name='', strm_type='Other', showtitle='None'):
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

    if strm_type.find('Cinema') != -1 or strm_type.find('YouTube') != -1 or strm_type.find('Movies') != -1:
        initialize_DialogBG("Movie", "Adding")
        addMovies(details, strm_name, strm_type)
        thisDialog.dialogeBG.close()
        thisDialog.dialogeBG = None
        return

    if strm_type.find('TV-Show') != -1 or strm_type.find('Shows-Collection') != -1:
        initialize_DialogBG("Adding TV-Shows", "working..")
        getTVShowFromList(details, strm_name, strm_type)
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
        selectedLabels = [stringUtils.getStrmname(item.split('|')[1]) for item in selectedItems]
        xbmcgui.Dialog().notification("Finished deleting:", "{0}".format(", ".join(label for label in selectedLabels)))


def getMediaListDialog():
    thelist = sorted(fileSys.readMediaList(purge=False), key=lambda k: k.split('|')[1].lower())
    items = []
    for entry in thelist:
        splits = entry.strip().split('|')
        matches = re.findall("plugin:\/\/([^\/\?]*)", splits[2])
        if matches:
            pluginnames = [fileSys.getAddonname(plugin) for plugin in matches]
            items.append("{0} ({1})".format(stringUtils.getStrmname(splits[1]), ', '.join(pluginnames)))

    selectedItemsIndex = xbmcgui.Dialog().multiselect("Select items", items)
    return [thelist[index] for index in selectedItemsIndex] if selectedItemsIndex else None


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
    thelist = fileSys.readMediaList(purge=False)
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


def addMovies(contentList, strm_name='', strm_type='Other', provider="n.a"):
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
                filetype = detailInfo.get('filetype', None)
                label = detailInfo.get('label').strip().encode("utf-8") if detailInfo.get('label', None) else None
                imdbnumber = detailInfo.get('imdbnumber').strip() if detailInfo.get('imdbnumber', None) else None

                if label and strm_name:
                    label = stringUtils.cleanLabels(label)
                    get_title_with_OV = True
                    if HIDE_title_in_OV == "true":
                        if re.search('(\WOV\W)', label):
                            get_title_with_OV = False

                    provider = getProvider(file)

                    thisDialog.dialogeBG.update(j, ADDON_NAME + ": Getting Movies: ", " Video: " + label)
                    if filetype is not None and filetype == 'file' and get_title_with_OV == True:
                        m_path = stringUtils.getMovieStrmPath(strm_type, strm_name, label)
                        m_title = stringUtils.getStrmname(label)
                        movieList.append({'path': m_path, 'title':  m_title, 'url': file, 'provider': provider, 'imdbnumber': imdbnumber})
                    j = j + len(contentList) * int(PAGINGMovies) / 100

            pagesDone += 1
            if filetype != '' and filetype != 'file' and pagesDone < int(PAGINGMovies):
                contentList = jsonUtils.requestList(file, 'video').get('files', [])
            else:
                pagesDone = int(PAGINGMovies)
        else:
            provider = getProvider(contentList[1])
            m_path = stringUtils.getMovieStrmPath(strm_type, strm_name)
            m_title = stringUtils.getStrmname(strm_name)
            movieList.append({'path': m_path, 'title':  m_title, 'url': contentList[1], 'provider': provider})
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


def getProvider(entry):
    provider = None
    provGeneral = re.search('%s([^\/\?]*)' % ("plugin:\/\/"), entry)
    provXST = re.search('%s(.*)'"\&function"'' % (r"site="), entry)

    if provGeneral:
        provider = provGeneral.group(1)
        if provXST:
            provider += ": " + provXST.group(1)

    return provider


def getTVShowFromList(showList, strm_name='', strm_type='Other', pagesDone=0):
    dirList = []
    episodesList = []

    while pagesDone < int(PAGINGTVshows):
        strm_type = strm_type.replace('Shows-Collection', 'TV-Shows')

        for detailInfo in showList:
            filetype = detailInfo.get('filetype', None)
            file = detailInfo.get('file', None)

            if filetype:
                if filetype == 'directory':
                    dirList.append(jsonUtils.requestList(file, 'video').get('files', []))
                    continue
                elif filetype == 'file':
                    if SEARCH_THETVDB == 2 or (SEARCH_THETVDB == 1 and detailInfo.get('season', -1) == -1 or detailInfo.get('episode', -1) == -1):
                        showtitle = detailInfo.get('showtitle')
                        episodetitle = detailInfo.get('title')

                        if showtitle and showtitle != '' and episodetitle and episodetitle != '':
                            lang = None
                            if strm_type.lower().find('other') == -1:
                                lang = strm_type[strm_type.find('(') + 1:strm_type.find(')')]

                            data = tvdb.getEpisodeByName(showtitle, episodetitle, lang)
                            if data:
                                detailInfo['season'] = data.get('season')
                                detailInfo['episode'] = data.get('episode')

                    get_title_with_OV = True
                    if HIDE_title_in_OV == "true":
                        label = detailInfo.get('label').strip().encode("utf-8") if detailInfo.get('label', None) else None
                        label = stringUtils.cleanLabels(label)
                        if re.search('(\WOV\W)', label):
                            get_title_with_OV = False

                    if detailInfo.get('season', -1) > -1 and detailInfo.get('episode', -1) > -1:
                        if NOE0_STRMS_EXPORT == "false" or detailInfo.get('episode') > 0 and get_title_with_OV == True:
                            episodesList.append(detailInfo)

        step = float(100.0 / len(episodesList) if len(episodesList) > 0 else 1)
        if pagesDone == 0:
            thisDialog.dialogeBG.update(int(step), "Initialisation of TV-Shows: " + stringUtils.getStrmname(strm_name))
        else:
            thisDialog.dialogeBG.update(int(step), "Page: %d %s" % (pagesDone, stringUtils.getStrmname(strm_name)))
        for index, episode in enumerate(episodesList):
            pagesDone = getEpisode(episode, strm_name, strm_type, pagesDone=pagesDone)
            thisDialog.dialogeBG.update(int(step * (index + 1)))

        pagesDone += 1
        episodesList = []
        showList = []
        if pagesDone < int(PAGINGTVshows) and len(dirList) > 0:
            showList = [item for sublist in dirList for item in sublist]
            dirList = []


def getEpisode(episode_item, strm_name, strm_type, j=0, pagesDone=0):
    episode = None

    utils.addon_log("detailInfo: %s" % (episode_item))
    file = episode_item.get('file', None)
    episode = episode_item.get('episode', -1)
    season = episode_item.get('season', -1)
    strSeasonEpisode = 's%de%d' % (season, episode)
    showtitle = episode_item.get('showtitle', None).encode("utf-8")
    provider = getProvider(file)

    if showtitle is not None and showtitle != "" and strm_type != "":
        path = os.path.join(strm_type, stringUtils.cleanStrmFilesys(showtitle)) if strm_name.find('++RenamedTitle++') == -1 else os.path.join(strm_type, stringUtils.cleanStrmFilesys(stringUtils.getStrmname(strm_name)))
        episode = {'path': path, 'strSeasonEpisode': strSeasonEpisode, 'url': file, 'tvShowTitle': showtitle, 'provider': provider} if strm_name.find('++RenamedTitle++') == -1 else {'path': path, 'strSeasonEpisode': strSeasonEpisode, 'url': file, 'tvShowTitle': stringUtils.getStrmname(strm_name), 'provider': provider}

        if addon.getSetting('Link_Type') == '0':
            episode = kodiDB.writeShow(episode)

        if episode is not None:
            strm_link = 'plugin://%s/?url=plugin&mode=10&mediaType=show&episode=%s&showid=%d|%s' % (addon_id, episode.get('strSeasonEpisode'), episode.get('showID'), episode.get('tvShowTitle')) if addon.getSetting('Link_Type') == '0' else episode.get('url')
            fileSys.writeSTRM(episode.get('path'), episode.get('strSeasonEpisode'), strm_link)

    return pagesDone