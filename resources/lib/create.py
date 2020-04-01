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

from __future__ import unicode_literals
from kodi_six.utils import py2_encode, py2_decode
import json
import os
import re
import sys
import xbmc
import xbmcgui

from .common import Globals, Settings, exit, jsonrpc
from .fileSys import readMediaList, removeMediaList, writeMediaList, writeSTRM, writeTutList
from .guiTools import addDir, addLink, editDialog, getType, getTypeLangOnly, mediaListDialog, selectDialog
from .jsonUtils import requestList
from .kodiDB import musicDatabase, writeMovie, writeShow
from .l10n import getString
from .stringUtils import cleanByDictReplacements, cleanStrmFilesys, cleanLabels, cleanStrms, getMovieStrmPath, \
    getProviderId, getStrmname, parseMediaListURL
from .tvdb import getEpisodeByName, getShowByName
from .utils import addon_log, addon_log_notice, key_natural_sort

try:
    import urllib.parse as urllib
except:
    import urllib

globals = Globals()
settings = Settings()


def fillPlugins(cType='video'):
    addons = searchAddons(cType)
    for addon in addons:
        art = dict(thumb=addon.get('thumbnail'), fanart=addon.get('fanart'))
        addDir(addon['name'], 'plugin://{0}'.format(addon['addonid']), 101, art, addon['description'], type=cType)


def searchAddons(cType):
    addons = []
    json_details = jsonrpc('Addons.GetAddons', dict(type='xbmc.addon.{0}'.format(cType), properties=['name', 'thumbnail', 'description', 'fanart', 'extrainfo', 'enabled']))
    for addon in sorted([addon for addon in json_details.get('addons') if addon.get('enabled')], key=lambda json: json.get('name').lower()):
        addontypes = []
        for info in addon.get('extrainfo'):
            if info.get('key') == 'provides':
                addontypes = info.get('value').split(' ')
                break

        if cType in addontypes and not addon.get('addonid') == globals.PLUGIN_ID:
            addons.append(addon)

    return addons


def fillPluginItems(url, media_type='video', file_type=False, strm=False, strm_name='', strm_type='Other', showtitle='None', name_parent='', name_orig=None, pDialog=None):
    name_orig_from_url, plugin_url = parseMediaListURL(url)
    if not name_orig:
        name_orig = name_orig_from_url

    if url.find('playMode=play') == -1:
        details = requestList(plugin_url, media_type).get('files', [])
        retry_count = 1
        while not globals.monitor.abortRequested() and len(details) == 0 and retry_count <= 3:
            addon_log('requestList: try={0} data = {1})'.format(retry_count, details))
            details = requestList(plugin_url, media_type).get('files', [])
            retry_count = retry_count + 1

        if globals.monitor.abortRequested():
            exit()
    else:
        details = [dict(playableSingleMedia=True, url=plugin_url)]

    if re.search('Movies|YouTube|TV-Shows|Album', strm_type):
        pDialogToClose = not pDialog
        if not pDialog:
            pDialog = globals.dialogProgressBG
            pDialog.create(heading='\'{0}\' {1}'.format(strm_name, getString(39138, globals.addon)))

        if re.search('Movies|YouTube', strm_type):
            addMovies(details, strm_name, strm_type, name_orig, pDialog)
        elif re.search('TV-Shows', strm_type):
            getTVShowFromList(details, strm_name, strm_type, name_orig, pDialog)
        elif re.search('Album', strm_type):
            addAlbum(details, strm_name, strm_type, pDialog)

        if pDialogToClose:
            pDialog.close()

        return

    for detail in details:
        filetype = detail.get('filetype')
        label = detail.get('label')
        file = detail.get('file')
        strm_name = cleanByDictReplacements(strm_name.strip())
        plot = detail.get('plot', '')
        art = detail.get('art', {})

        if settings.LINK_TYPE == 0:
            link = '{0}?{1}'.format(sys.argv[0], urllib.urlencode({'url': file, 'mode': 10, 'name': py2_encode(label), 'fanart': art.get('fanart', '')}))
        else:
            link = file

        if strm_type == 'Audio-Single':
            path = os.path.join('Singles', strm_name)
            try:
                album = detail['album'].strip()
                artist = cleanByDictReplacements(', '.join(artist.strip() for artist in detailInfo['artist']) if isinstance(detailInfo['artist'], (list, tuple)) else detailInfo['artist'].strip())
                filename = (strm_name + ' - ' + label).strip()
            except:
                filename = (strm_name + ' - ' + label).strip()

        if strm_type in ['Other']:
            path = os.path.join('Other', strm_name)
            filename = '{0} - {1}'.format(strm_name, label)

        if filetype == 'file':
            if strm:
                if strm_type.find('Audio-Albums') != -1:
                    musicDatabase(album, artist, label, path, link, track)
                writeSTRM(cleanStrms(path.rstrip('.')), cleanStrms(filename.rstrip('.')) , link)
            else:
                addLink(label, file, 10, art, plot, '', '', '', None, '', total=len(details), type=detail.get('type', None), year=detail.get('year', None))
        else:
            if strm:
                fillPluginItems(file, media_type, file_type, strm, label, strm_type, name_orig=name_orig)
            else:
                addDir(label, file, 101, art, plot, '', '', '', name_parent=name_parent, type=detail.get('type', None))


def addToMedialist(params):
    settings = Settings()
    name = name_orig = params.get('name')
    # A dialog to rename the Change Title for Folder and MediaList entry:
    if params.get('noninteractive', False) == False:
        name = re.sub('( - |, )*([sS](taffel|eason|erie[s]{0,1})|[pP]art|[tT]eil) \d+', '', name_orig)
        if name != name_orig:
            tvshow_detected = True
        else:
            tvshow_detected = False

        if name == '':
            name = params.get('name_parent')
            name_orig = '{0} - {1}'.format(name, name_orig)
        if params.get('type') == 'movie' and params.get('year'):
            name = '{0} ({1})'.format(name, params.get('year'))
        selectAction = ['{0}: \'{1}\''.format(getString(39106, globals.addon), name), getString(39107, globals.addon), getString(39108, globals.addon)]
        if not writeTutList('select:Rename'):
            tutWin = ['Adding content to your library',
                      'You can rename your Movie, TV-Show or Music title.',
                      'To make your scraper recognize the content, some times it is necessary to rename the title.',
                      'Be careful, wrong title can also cause that your scraper can\'t recognize your content.']
            globals.dialog.ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])
        choice = selectDialog('{0}: \'{1}\''.format(getString(39105, globals.addon), name_orig), selectAction)
    else:
        choice = params.get('choice', 0)
        name = params.get('name')
        name_orig = params.get('name_orig')

    if choice != -1:
        cType = params.get('cType', None)
        if name:
            name = cleanLabels(name,keep_year=(settings.KEEP_MOVIE_YEAR and params.get('type', None) == 'movie'))

        if choice == 1 or name == None or name == '':
            name = editDialog(name).strip()
            name = '{0}++RenamedTitle++'.format(name) if name else name

        if choice == 2:
            cTypeFilter = None
            if tvshow_detected or params.get('type', None) == 'tvshow':
                cTypeFilter = 'TV-Shows'
            elif params.get('type', None) == 'movie':
                cTypeFilter = 'Movies'
            item = mediaListDialog(False, False, header_prefix=getString(39125, globals.addon).format(name_orig), cTypeFilter=cTypeFilter, preselect_name=name)
            splits = item.get('entry').split('|') if item else None
            name = splits[1] if splits else None
            cType = splits[0] if splits else None

        if name:
            url = params.get('url')
            if not cType:
                if not writeTutList('select:ContentTypeLang'):
                    tutWin = ['Adding content to your library',
                              'Now select your content type.',
                              'Select language or YouTube type.',
                              'Wait for done message.']
                    globals.dialog.ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])

                if tvshow_detected or params.get('type', None) == 'tvshow':
                    cType = getTypeLangOnly('TV-Shows')
                elif params.get('type', None) == 'movie':
                    cType = getTypeLangOnly('Movies')
                else:
                    cType = getType(url)
            if cType != -1:
                if params.get('filetype', 'directory') == 'file':
                    url += '&playMode=play'
                if (settings.SEARCH_THETVDB == 2 and cType.find('TV-Shows') != -1 and choice == 0):
                    show_data = getShowByName(name, re.sub('TV-Shows\((.*)\)', r'\g<1>', cType))
                    if show_data:
                        showtitle_tvdb = show_data.get('seriesName', name)
                        if showtitle_tvdb != name:
                            addon_log_notice('addToMedialist: Use TVDB name \'{0}\' for \'{1}\''.format(showtitle_tvdb, name))
                            name = showtitle_tvdb
                writeMediaList('name_orig={0};{1}'.format(name_orig, url), name, cType)
                # globals.dialog.notification(cType, name_orig, globals.MEDIA_ICON, 5000, False)

                try:
                    plugin_id = re.search('{0}([^\/\?]*)'.format('plugin:\/\/'), url)
                    if plugin_id:
                        module = moduleUtil.getModule(plugin_id.group(1))
                        if module and hasattr(module, 'create'):
                            url = module.create(name, url, 'video')
                except:
                    pass

                fillPluginItems(url, strm=True, strm_name=name, strm_type=cType, name_orig=name_orig)
                # globals.dialog.notification(getString(39126, globals.addon), getString(39127, globals.addon), globals.MEDIA_ICON, 5000, True)


def addMultipleSeasonToMediaList(params):
    name = name_orig = params.get('name')
    url = params.get('url')
    selectAction = ['{0}: \'{1}\''.format(getString(39106, globals.addon), name), getString(39107, globals.addon), getString(39108, globals.addon)]
    if not writeTutList('select:Rename'):
        tutWin = ['Adding content to your library',
                  'You can rename your Movie, TV-Show or Music title.',
                  'To make your scraper recognize the content, some times it is necessary to rename the title.',
                  'Be careful, wrong title can also cause that your scraper can\'t recognize your content.']
        globals.dialog.ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])
    choice = selectDialog('{0}: \'{1}\''.format(getString(39105, globals.addon), name_orig), selectAction)
    if choice != -1:
        cType = None
        if name:
            name = cleanLabels(name)

        if choice == 1 or name == None or name == '':
            name = editDialog(name).strip()
            name = '{0}++RenamedTitle++'.format(name) if name else name

        if choice == 2:
            item = mediaListDialog(False, False, header_prefix=getString(39125, globals.addon).format(name_orig), preselect_name=name, cTypeFilter='TV-Shows')
            splits = item.get('entry').split('|') if item else None
            name = splits[1] if splits else None
            cType = splits[0] if splits else None
        addon_log_notice('addMultipleSeasonToMediaList: name = {0}, cType = {1}'.format(name, cType))
        if name:

            if not cType:
                cType = getTypeLangOnly('TV-Shows')

            if cType != -1:
                details = requestList(url, 'video').get('files', [])
                retry_count = 1
                while not globals.monitor.abortRequested() and len(details) == 0 and retry_count <= 3:
                    addon_log('requestList: try={0} data = {1})'.format(retry_count, details))
                    details = requestList(url, 'video').get('files', [])
                    retry_count = retry_count + 1

                if globals.monitor.abortRequested():
                    exit()

                seasonList = []
                for detail in details:
                    file = detail['file'].replace('\\\\', '\\')
                    filetype = detail['filetype']
                    label = detail['label']
                    if label.find('COLOR') != -1:
                        label = cleanLabels(label) + ' (*)'
                    showtitle = detail['showtitle']
                    name_orig = '{0} - {1}'.format(showtitle, label)
                    if filetype == 'directory':
                        seasonList.append({'label': label, 'name': name, 'name_orig': name_orig, 'url': file, 'cType': cType, 'noninteractive': True})

                sItems = sorted([item.get('label') for item in seasonList], key=lambda k: key_natural_sort(k.lower()))
                preselect = [i for i, item in enumerate(sItems) if item.find(' (*)') == -1]
                selectedItemsIndex = selectDialog(getString(39128, globals.addon).format(showtitle), sItems, multiselect=True, preselect=preselect)
                seasonList = [item for item in seasonList for index in selectedItemsIndex if item.get('label') == sItems[index]] if selectedItemsIndex and len(selectedItemsIndex) > 0 else None
                addon_log_notice('addMultipleSeasonToMediaList: seasonList = {0}'.format(seasonList))
                if seasonList and len(seasonList) > 0:
                    for season in seasonList:
                        addToMedialist(season)


def renameMediaListEntry(selectedItems):
    for item in selectedItems:
        splits = item.get('entry').split('|')
        cType = splits[0]
        name_old = getStrmname(splits[1])
        choice = 1
        if cType.find('TV-Shows') != -1:
            selectAction = [getString(39129, globals.addon), getString(39130, globals.addon)]
            choice = selectDialog('{0}: {1}'.format(getString(39006, globals.addon), name_old), selectAction)
        if choice != -1:
            if choice == 1:
                name = editDialog(name_old).strip()
                name = '{0}++RenamedTitle++'.format(name) if name else name
            elif choice == 0:
                show_data = getShowByName(name_old, re.sub('TV-Shows\((.*)\)', r'\g<1>', cType))
                if show_data:
                    name = show_data.get('seriesName', name_old)
            if name and name_old != name:
                addon_log_notice('renameMediaListEntry: Use new name \'{0}\' for \'{1}\''.format(name, name_old))
                item['name_new'] = name
                removeAndReadMedialistEntry([item])


def removeAndReadMedialistEntry(selectedItems):
    for item in selectedItems:
        splits = item.get('entry').split('|')
        cType = splits[0]
        removeMediaList([item])
        name = item.get('name_new', splits[1])
        urls = splits[2].split('<next>')
        for url in urls:
            name_orig, plugin_url = parseMediaListURL(url)
            params = {'cType': cType, 'name': name, 'name_orig': name_orig, 'url': plugin_url, 'choice': 99, 'noninteractive': True}
            addToMedialist(params)


def removeItemsFromMediaList(action='list'):
    addon_log('removingitemsdialog')

    selectedItems = mediaListDialog(header_prefix=getString(39007, globals.addon), multiselect=True)

    if selectedItems:
        removeMediaList(selectedItems)
        selectedLabels = sorted(list(dict.fromkeys([item.get('name') for item in selectedItems])), key=lambda k: k.lower())
        globals.dialog.notification(getString(39131, globals.addon), '{0}'.format(', '.join(label for label in selectedLabels), globals.MEDIA_ICON, 5000, True))


def addAlbum(contentList, strm_name, strm_type, pDialog, PAGINGalbums='1'):
    strm_name = getStrmname(strm_name)
    albumList = []
    dirList = []
    pagesDone = 0
    file = ''
    filetype = ''
    j = 100 / (len(contentList) * int(PAGINGalbums)) if len(contentList) > 0 else 1

    if len(contentList) == 0:
        return contentList

    while not globals.monitor.abortRequested() and pagesDone < int(PAGINGalbums):
        if not contentList[0].get('playableSingleMedia'):
            for index, detailInfo in enumerate(contentList):
                art = detailInfo.get('art', {})
                file = detailInfo['file'].replace('\\\\', '\\')
                filetype = detailInfo['filetype']
                label = detailInfo['label'].strip()
                thumb = art.get('thumb', '')
                fanart = art.get('fanart', '')
                track = detailInfo.get('track', 0) if detailInfo.get('track', 0) > 0 else index + 1
                album = detailInfo['album'].strip()
                duration = detailInfo.get('duration', 0)

                if filetype == 'directory':
                    dirList.append(requestList(file, 'music').get('files', []))
                    continue

                if duration == 0:
                    duration = 200

                if settings.LINK_TYPE == 0:
                    link = '{0}?{1}'.format(sys.argv[0], urllib.urlencode({'url': file, 'mode': 10, 'mediaType': 'audio', 'name': label, 'fanart': fanart}))
                else:
                    link = file

                # Check for Various Artists
                artistList = []
                for i, sArtist in enumerate(contentList):
                    for artist in sArtist.get('artist'):
                        if artist not in artistList:
                            artistList.append(artist)

                if len(artistList) == 1:
                    artist = artistList[0]
                else:
                    artist = 'Various Artists'

                pDialog.update(int(j), message='\'{0}\' {1}'.format(label, getString(39138, globals.addon)))
                path = os.path.join(strm_type, cleanStrmFilesys(artist), cleanStrmFilesys(strm_name))
                if album and artist and label and path and link and track:
                    albumList.append({'path': path, 'label': label, 'link': link, 'album': album, 'artist': artist, 'track': track, 'duration': duration, 'thumb': thumb})
                j = j + 100 / (len(contentList) * int(PAGINGalbums))

            pagesDone += 1
            contentList = []
            if pagesDone < int(PAGINGalbums) and len(dirList) > 0:
                contentList = [item for sublist in dirList for item in sublist]
                dirList = []
        else:
            albumList.append({'path': os.path.join(strm_type, strm_name, label), 'label': cleanByDictReplacements(label), 'link': link})
            pagesDone = int(PAGINGalbums)

    if globals.monitor.abortRequested():
        exit()

    # Write strms for all values in albumList
    thelist = readMediaList()
    for entry in thelist:
        splits = entry.strip().split('|')
        splitsstrm = splits[0]
        splitsname = splits[1]
        if splitsstrm.find('Album') != -1 and splitsname.find(strm_name) != -1:
            url = splits[2]
            cType = splits[0]
            writeMediaList(url, strm_name, cType, albumartist=artist)
    for album in albumList:
        strm_link = '{0}|{1}'.format(album.get('link'), album.get('label')) if settings.LINK_TYPE == 0 else album.get('link')
        fullpath, fileModTime = writeSTRM(album.get('path'), cleanStrms(album.get('label').rstrip('.')) , strm_link)
        musicDatabase(album.get('album'), album.get('artist'), album.get('label'), album.get('path'), album.get('link'), album.get('track'), album.get('duration'), album.get('thumb'), fileModTime)

    return albumList


def addMovies(contentList, strm_name, strm_type, name_orig, pDialog, provider='n.a.'):
    movieList = []
    pagesDone = 0
    file = ''
    filetype = ''
    j = len(contentList) * settings.PAGING_MOVIES / 100

    if len(contentList) == 0:
        return

    while not globals.monitor.abortRequested() and pagesDone < settings.PAGING_MOVIES:
        if not contentList[0].get('playableSingleMedia'):
            for detailInfo in contentList:
                file = detailInfo.get('file').replace('\\\\', '\\') if detailInfo.get('file', None) else None
                if settings.LINK_TYPE == 0 and name_orig and file.find('name_orig=') == -1:
                    file = 'name_orig={0};{1}'.format(name_orig, file)
                filetype = detailInfo.get('filetype', None)
                label = detailInfo.get('label') if detailInfo.get('label', None) else None
                imdbnumber = detailInfo.get('imdbnumber').strip() if detailInfo.get('imdbnumber', None) else None

                if label and strm_name:
                    label = cleanLabels(label)
                    get_title_with_OV = True
                    if settings.HIDE_TITLE_IN_OV:
                        if re.search('(\WOV\W)', label):
                            get_title_with_OV = False

                    provider = getProviderId(file)

                    pDialog.update(int(j), message='\'{0}\' {1}'.format(label, getString(39138, globals.addon)))
                    if filetype and filetype == 'file' and get_title_with_OV:
                        m_path = getMovieStrmPath(strm_type, strm_name, label)
                        m_title = getStrmname(label)
                        movieList.append({'path': m_path, 'title':  m_title, 'url': file, 'provider': provider.get('providerId'), 'imdbnumber': imdbnumber})
                    j = j + len(contentList) * settings.PAGING_MOVIES / 100

            pagesDone += 1
            if filetype != 'file' and pagesDone < settings.PAGING_MOVIES:
                contentList = requestList(file, 'video').get('files', [])
                retry_count = 1
                while not globals.monitor.abortRequested() and len(contentList) == 0 and retry_count <= 3:
                    addon_log('requestList: try={0} data = {1})'.format(retry_count, contentList))
                    contentList = requestList(file, 'video').get('files', [])
                    retry_count = retry_count + 1

                if globals.monitor.abortRequested():
                    exit()
            else:
                pagesDone = settings.PAGING_MOVIES
        else:
            provider = getProviderId(contentList[0].get('url')).get('providerId')
            url = contentList[0].get('url')
            if settings.LINK_TYPE == 0 and name_orig and file.find('name_orig=') == -1:
                url = 'name_orig={0};{1}'.format(name_orig , url)
            m_path = getMovieStrmPath(strm_type, strm_name)
            m_title = getStrmname(strm_name)
            movieList.append({'path': m_path, 'title':  cleanStrmFilesys(m_title), 'url': url, 'provider': provider})
            pagesDone = settings.PAGING_MOVIES

    if globals.monitor.abortRequested():
        exit()

    if settings.LINK_TYPE == 0:
        movieList = writeMovie(movieList)

    j = 100 / len(movieList) if len(movieList) > 0 else 1
    # Write strms for all values in movieList
    for movie in movieList:
        pDialog.update(int(j), message='\'{0}\' {1}'.format(movie.get('title'), getString(39138, globals.addon)))
        strm_link = 'plugin://{0}/?url=plugin&mode=10&mediaType=movie&id={1}|{2}'.format(globals.PLUGIN_ID, movie.get('movieID'), movie.get('title')) if settings.LINK_TYPE == 0 else movie.get('url')
        addon_log('write movie = {0}'.format(movie))
        writeSTRM(cleanStrms(movie.get('path')), cleanStrms(movie.get('title')), strm_link)

        j = j + 100 / len(movieList)


def getTVShowFromList(showList, strm_name, strm_type, name_orig, pDialog, pagesDone=0):
    dirList = []
    episodesList = []

    lang = None
    if strm_type.lower().find('other') == -1:
        lang = strm_type[strm_type.find('(') + 1:strm_type.find(')')]
    showtitle = getStrmname(strm_name)

    while not globals.monitor.abortRequested() and pagesDone < settings.PAGING_TVSHOWS:
        strm_type = strm_type.replace('Shows-Collection', 'TV-Shows')

        for detailInfo in showList:
            filetype = detailInfo.get('filetype', None)
            file = detailInfo.get('file', None)

            if filetype:
                if filetype == 'directory':
                    retry_count = 1
                    json_reply = requestList(file, 'video').get('files', [])
                    while not globals.monitor.abortRequested() and len(json_reply) == 0 and retry_count <= 3:
                        addon_log('requestList: try={0} data = {1})'.format(retry_count, json_reply))
                        json_reply = requestList(file, 'video').get('files', [])
                        retry_count = retry_count + 1

                    if globals.monitor.abortRequested():
                        exit()

                    dirList.append(json_reply)
                    continue
                elif filetype == 'file':
                    get_title_with_OV = True
                    if settings.HIDE_TITLE_IN_OV:
                        label = detailInfo.get('label').strip() if detailInfo.get('label', None) else None
                        label = cleanLabels(label)
                        if re.search('(\WOV\W)', label):
                            get_title_with_OV = False

                    if get_title_with_OV:
                        episodetitle = detailInfo.get('title')
                        episodeseason = detailInfo.get('season', -1)
                        episode = detailInfo.get('episode', -1)
                        export_episode = (not settings.NO_E0_STRMS_EXPORT or episode != 0)

                        if (settings.SEARCH_THETVDB == 2 or (settings.SEARCH_THETVDB == 1 and (episodeseason == -1 or episode == -1))) and export_episode:
                            if showtitle and showtitle != '' and episodetitle and episodetitle != '':
                                eptitle = episodetitle
                                eptitle = eptitle.replace('\u201e', '\'')
                                eptitle = eptitle.replace('\u201c', '\'')
                                eptitle = eptitle.replace('\u2013', '-')
                                addon_log_notice('search tvdb for \'{0}\': \'S{1:02d}E{2:02d} - {3}\' (lang={4})'.format(showtitle, episodeseason, episode, eptitle, lang))
                                data = getEpisodeByName(showtitle, episodeseason, episode, eptitle, lang)

                                if data:
                                    detailInfo['season'] = data.get('season')
                                    detailInfo['episode'] = data.get('episode')
                                    detailInfo['episodeName'] = data.get('episodeName', None)
                                    addon_log_notice('found tvdb entry for \'{0}\': \'S{1:02d}E{2:02d} - {3}\' matched to \'S{4:02d}E{5:02d} - {6}\''
                                                           .format(showtitle, episodeseason, episode, episodetitle,
                                                           detailInfo['season'], detailInfo['episode'], detailInfo['episodeName']))
                                else:
                                    detailInfo['season'] = -1
                                    detailInfo['episode'] = -1
                                    addon_log_notice('no tvdb entry found for \'{0}\': \'S{1:02d}E{2:02d} - {3}\''
                                                           .format(showtitle, episodeseason, episode, episodetitle))

                        if detailInfo.get('season', -1) > -1 and detailInfo.get('episode', -1) > -1  and export_episode:
                            if  episodetitle.find('Teil 1 und 2') >= 0 or episodetitle.find('Parts 1 & 2') >= 0 :
                                addon_log_notice('found tvdb entry for \'{0}\': \'S{1:02d}E{2:02d} - {3}\' (multi) matched to \'S{4:02d}E{5:02d} - {6}\''
                                    .format(showtitle, episodeseason, episode, episodetitle, detailInfo['season'], detailInfo['episode'], detailInfo['episodeName']))
                                data = getEpisodeByName(showtitle, episodeseason, episode + 1, re.sub('(Teil 1 und 2|Parts 1 & 2)', '(2)', eptitle), lang)
                                if data:
                                    addon_log_notice('found tvdb entry for \'{0}\': \'S{1:02d}E{2:02d} - {3}\' (multi) matched to \'S{4:02d}E{5:02d} - {6}\''
                                        .format(showtitle, episodeseason, episode, episodetitle, detailInfo['season'], detailInfo['episode'] + 1, data.get('episodeName', None)))
                                detailInfo['multi_episode'] = True
                                detailInfo['episode'] = [detailInfo['episode'], detailInfo['episode'] + 1]

                            episodetitles = list(filter(None, re.split(' / | , ', episodetitle)))
                            if episodetitles[0] != episodetitle and not re.search(' *(-|\(|:)* *([tT]eil|[pP]art|[pP]t\.) (\d+|\w+)\)*', episodetitle):
                                addon_log_notice('check multi episode \'{0}\': \'S{1:02d}E{2:02d} - {3}\''.format(showtitle, episodeseason, episode, episodetitle))
                                seasonm = []
                                episodem = []
                                episodeNamem = []
                                for e, eptitle in enumerate(episodetitles):
                                    data = getEpisodeByName(showtitle, episodeseason, episode, eptitle, lang)
                                    if data:
                                        seasonm.append(data.get('season'))
                                        episodem.append(data.get('episode'))
                                        episodeNamem.append(data.get('episodeName'))

                                if all(x == seasonm[0] for x in seasonm) and len(set(episodem)) == len(episodetitles):
                                    detailInfo['multi_episode'] = True
                                    detailInfo['episode'] = episodem
                                    for e, ep in enumerate(episodem):
                                        addon_log_notice('found tvdb entry for \'{0}\': \'S{1:02d}E{2:02d} - {3}\' (multi) matched to \'S{4:02d}E{5:02d} - {6}\''
                                            .format(showtitle, episodeseason, episode, episodetitle,
                                            detailInfo['season'], episodem[e], episodeNamem[e]))

                            episodesList.append(detailInfo)

        step = float(100.0 / len(episodesList) if len(episodesList) > 0 else 1)
        if pagesDone > 0:
            pDialog.update(int(step), '\'{0}\' {1}: {2} {3}'.format(getStrmname(strm_name), getString(39138, globals.addon), pagesDone, getString(39139, globals.addon), pagesDone))

        split_episode = 0
        for index, episode in enumerate(episodesList):
            if index > 0:
                if season_prev == episode.get('season') and episode_prev == episode.get('episode'):
                    episodesList[index - 1]['split_episode'] = split_episode + 1
                    episodesList[index]['split_episode'] = split_episode + 2
                    split_episode = split_episode + 1
                else:
                    if split_episode > 0:
                        split_episode_names = []
                        for s in range(0, split_episode + 1):
                            split_episode_names.insert(0, episodesList[index - s - 1]['title'])
                        addon_log_notice('Split Episode for {0}: \'{1}\' matched to \'S{2:02d}E{3:02d} - {4}\''
                                            .format(showtitle, ', '.join(split_episode_names),
                                            episodesList[index - split_episode].get('season', None),
                                            episodesList[index - split_episode].get('episode', None),
                                            episodesList[index - split_episode].get('episodeName', None)))
                    split_episode = 0
            episodesList[index]['showtitle'] = showtitle
            season_prev = episode.get('season')
            episode_prev = episode.get('episode')

        for index, episode in enumerate(episodesList):
            pagesDone = getEpisode(episode, strm_name, strm_type, pagesDone=pagesDone, name_orig=name_orig)
            pDialog.update(int(step * (index + 1)))

        pagesDone += 1
        episodesList = []
        showList = []
        if pagesDone < settings.PAGING_TVSHOWS and len(dirList) > 0:
            showList = [item for sublist in dirList for item in sublist]
            dirList = []


def getEpisode(episode_item, strm_name, strm_type, j=0, pagesDone=0, name_orig=None):
    episode = None

    addon_log('detailInfo: {0}'.format(episode_item))
    file = episode_item.get('file', None)

    if name_orig and file.find('name_orig=') == -1 and settings.LINK_TYPE == 0:
        file = 'name_orig={0};{1}'.format(name_orig, file)
    episode = episode_item.get('episode', -1)
    split_episode = episode_item.get('split_episode', -1)
    multi_episode = episode_item.get('multi_episode', False)
    season = episode_item.get('season', -1)
    if split_episode > 0:
        strSeasonEpisode = 's{0}e{1}.{2}'.format(season, episode, split_episode)
    else:
        if multi_episode:
            strSeasonEpisode = 's{0}e{1}'.format(season, '-'.join(map(str, episode)))
        else:
            strSeasonEpisode = 's{0}e{1}'.format(season, episode)
    showtitle = episode_item.get('showtitle', None)

    if showtitle is not None and showtitle != '' and strm_type != '':
        path = os.path.join(strm_type, cleanStrmFilesys(showtitle))
        provider = getProviderId(file)
        episode = {'path': path, 'strSeasonEpisode': strSeasonEpisode, 'url': file, 'tvShowTitle': cleanStrmFilesys(showtitle), 'provider': provider.get('providerId'), 'metadata': json.dumps(episode_item)}

        if settings.LINK_TYPE == 0:
            episode = writeShow(episode)

        if episode is not None:
            strm_link = 'plugin://{0}/?url=plugin&mode=10&mediaType=show&episode={1}&showid={2}|{3}'.format(globals.PLUGIN_ID, episode.get('strSeasonEpisode'), episode.get('showID'), episode.get('tvShowTitle')) if settings.LINK_TYPE == 0 else episode.get('url')
            writeSTRM(episode.get('path'), episode.get('strSeasonEpisode'), strm_link)

    return pagesDone