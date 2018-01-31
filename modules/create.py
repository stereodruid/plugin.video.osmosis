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

reload(sys)
sys.setdefaultencoding("utf-8")

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
ADDON_NAME = addon.getAddonInfo('name')
HIDE_tile_in_OV = addon.getSetting('Hide_tilte_in_OV')
PAGINGTVshows = addon.getSetting('paging_tvshows')
PAGINGMovies = addon.getSetting('paging_movies')
STRM_LOC = xbmc.translatePath(addon.getSetting('STRM_LOC'))
NOE0_STRMS_EXPORT = addon.getSetting('noE0_Strms_Export')

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
    json_query = ('{"jsonrpc":"2.0","method":"Addons.GetAddons","params":{"type":"xbmc.addon.%s","properties":["name","path","thumbnail","description","fanart","summary", "extrainfo"]}, "id": 1 }' % cType)
    json_details = jsonUtils.sendJSON(json_query)
    for addon in sorted(json_details["addons"], key=lambda json: json['name'].lower()):
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
            addMovies(details, strm_name, strm_type)
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None
            return
        except:
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1]) + (". See your Kodi.log!"))
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
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1]) + (". See your Kodi.log!"))
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
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1]) + (". See your Kodi.log!"))
            utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
            print ("Unexpected error:"), sys.exc_info()[0]
            raise

    for detail in details:
        filetype = detail['filetype']
        label = detail['label']
        file = detail['file'].replace("\\\\", "\\")
        strm_name = stringUtils.cleanByDictReplacements(strm_name.strip())
        plot = detail.get('plot', '')
        art = detail.get('art', {})

        if addon.getSetting('Link_Type') == '0':
            link = '%s?url=%s&mode=%d&name=%s&fanart=%s' % (sys.argv[0], urllib.quote_plus(stringUtils.uni(file)), 10, urllib.quote_plus(stringUtils.uni(label)), urllib.quote_plus(art.get('fanart', '')))
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

        if strm_type.find('Audio-Album') != -1:
            path = os.path.join(strm_type, strm_name)
            track = detail.get('track', 0)
            try:
                album = detail['album'].strip()
                artist = stringUtils.cleanByDictReplacements(", ".join(artist.strip() for artist in detailInfo['artist']) if isinstance(detailInfo['artist'], (list, tuple)) else detailInfo['artist'].strip())
                filename = stringUtils.cleanByDictReplacements(label.strip())
            except:
                filename = stringUtils.cleanByDictReplacements(label.strip())

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
    thelist = fileSys.readMediaList(purge=False)
    items = []
    for entry in thelist:
        splits = entry.strip().split('|')
        plugin = re.search('%s([^\/\?]*)' % ("plugin:\/\/"), splits[2])
        items.append(stringUtils.getStrmname(splits[1]) + " (" + fileSys.getAddonname(plugin.group(1)) + ")")

    selectedItemsIndex = xbmcgui.Dialog().multiselect("Select items", items)
    return [thelist[index] for index in selectedItemsIndex] if selectedItemsIndex is not None else []


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
                art = detailInfo.get('art', {})
                file = detailInfo['file'].replace("\\\\", "\\").encode('utf-8')
                filetype = detailInfo['filetype']
                label = detailInfo['label'].strip()
                thumb = art.get('thumb', '')
                fanart = art.get('fanart', '')
                track = detailInfo.get('track', 0) if detailInfo.get('track', 0) > 0 else index + 1
                duration = detailInfo.get('duration', 0)
                if duration == 0:
                    duration = 200

                try:
                    if filetype == 'directory':
                        dirList.append(jsonUtils.requestList(file, 'music').get('files', []))
                        continue

                    if addon.getSetting('Link_Type') == '0':
                        link = +"%s?url=%s&mode=%d&name=%s&fanart=%s" % (sys.argv[0], urllib.quote_plus(file), 10, urllib.quote_plus(label), urllib.quote_plus(fanart))
                    else:
                        link = file

                    try:
                        album = detailInfo['album'].strip()
                        artist = stringUtils.cleanByDictReplacements(", ".join(artist.strip() for artist in detailInfo['artist']) if isinstance(detailInfo['artist'], (list, tuple)) else detailInfo['artist'].strip())
                        artistList = []
                        # Check for Various Artists
                        for i, sArtist in enumerate(contentList):
                            artistList.append(sArtist.get('artist'))
                        if len(artistList) > 1:
                            try:
                                if artistList[0] != artistList[1] and artistList[1] != artistList[2]:
                                    artist = 'Various Artists'
                            except IndexError:
                                if artistList[0] != artistList[1]:
                                    artist = 'Various Artists'

                    except:
                        pass

                    thisDialog.dialogeBG.update(j, ADDON_NAME + ": Writing File: ", " Title: " + label)
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
                    guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1]) + (". See your Kodi.log!"))
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
            albumList.append([os.path.join(strm_type, stringUtils.getStrmname(strm_name) , label), stringUtils.cleanByDictReplacements(label), link])
            pagesDone = int(PAGINGalbums)

    try:
        # Write strms for all values in albumList
        thelist = fileSys.readMediaList(purge=False)
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
            strm_link = i[2] + "|" + i[1] if addon.getSetting('Link_Type') == '0' else i[2]
            fullpath, fileModTime = fileSys.writeSTRM(path, stringUtils.cleanStrms(i[1].rstrip(".")) , strm_link)
            kodiDB.musicDatabase(i[3], i[4], i[1], i[0], i[2], i[5], i[6], aThumb, fileModTime)
        thisDialog.dialogeBG.close()
    except IOError as (errno, strerror):
        print ("I/O error({0}): {1}").format(errno, strerror)
    except ValueError:
        print ("No valid integer in line.")
    except:
        thisDialog.dialogeBG.close()
        guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1]) + (". See your Kodi.log!"))
        utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
        print ("Unexpected error:"), sys.exc_info()[0]
        raise

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
                file = detailInfo.get('file').replace("\\\\", "\\") if detailInfo.get('file', None) is not None else None
                filetype = detailInfo.get('filetype', None)
                label = detailInfo.get('label').strip() if detailInfo.get('label', None) is not None else None
                imdbnumber = detailInfo.get('imdbnumber').strip() if detailInfo.get('imdbnumber', None) is not None else None

                try:
                    if label and strm_name:
                        label = stringUtils.cleanLabels(label)
                        if HIDE_tile_in_OV == "true" and label.find("[OV]") > -1:
                            get_title_with_OV = False
                        else:
                            get_title_with_OV = True

                        provider = getProvider(file)

                        thisDialog.dialogeBG.update(j, ADDON_NAME + ": Getting Movies: ", " Video: " + label)
                        if filetype is not None and filetype == 'file' and get_title_with_OV == True:
                            m_path = stringUtils.getMovieStrmPath(strm_type, strm_name, label)
                            m_title = stringUtils.getStrmname(label)
                            movieList.append({'path': m_path, 'title':  m_title, 'url': file, 'provider': provider, 'imdbnumber': imdbnumber})
                        j = j + len(contentList) * int(PAGINGMovies) / 100
                except IOError as (errno, strerror):
                    print ("I/O error({0}): {1}").format(errno, strerror)
                except ValueError:
                    print ("No valid integer in line.")
                except:
                    guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1]) + (". See your Kodi.log!"))
                    utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
                    print ("Unexpected error:"), sys.exc_info()[0]
                    raise

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
        try:
            for detailInfo in showList:
                filetype = detailInfo.get('filetype', None)
                file = detailInfo.get('file', None)
                episode = detailInfo.get('episode', -1)
                season = detailInfo.get('season', -1)

                if filetype is not None:
                    if filetype == 'directory':
                        dirList.append(jsonUtils.requestList(file, 'video').get('files', []))
                        continue
                    elif season > -1 and episode > -1 and filetype == 'file':
                        if NOE0_STRMS_EXPORT == "false" or episode > 0:
                            episodesList.append(detailInfo)

            step = float(100.0 / len(episodesList) if len(episodesList) > 0 else 1)
            if pagesDone == 0:
                thisDialog.dialogeBG.update(int(step), "Initialisation of TV-Shows: " + stringUtils.getStrmname(strm_name))
            else:
                thisDialog.dialogeBG.update(int(step), "Page: %d %s" % (pagesDone, stringUtils.getStrmname(strm_name)))
            for index, episode in enumerate(episodesList):
                pagesDone = getEpisode(episode, strm_name, strm_type, pagesDone=pagesDone)
                thisDialog.dialogeBG.update(int(step * (index + 1)))

        except IOError as (errno, strerror):
            print ("I/O error({0}): {1}").format(errno, strerror)
        except ValueError:
            print ("No valid integer in line.")
        except:
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1]) + (". See your Kodi.log!"))
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
    episode = None

    utils.addon_log("detailInfo: %s" % (episode_item))
    file = episode_item.get('file', None)
    episode = episode_item.get('episode', -1)
    season = episode_item.get('season', -1)
    strSeasonEpisode = 's%de%d' % (season, episode)
    showtitle = episode_item.get('showtitle', None)
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
