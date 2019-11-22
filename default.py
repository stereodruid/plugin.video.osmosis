# Copyright (C) 2016 stereodruid(J.G.) Mail: stereodruid@gmail.com
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
from kodi_six.utils import py2_decode
import os, sys
import time
import re
import xbmc, xbmcaddon, xbmcgui, xbmcplugin

import utils
from resources.lib import create
from resources.lib import fileSys
from resources.lib import guiTools
from resources.lib import jsonUtils
from resources.lib import kodiDB
from resources.lib import moduleUtil
from resources.lib import stringUtils
from resources.lib import tvdb
from resources.lib import updateAll
from resources.lib import urlUtils

try:
    import urllib.parse as urlparse
except:
    import urlparse

addon = xbmcaddon.Addon()
home = py2_decode(xbmc.translatePath(addon.getAddonInfo('path')))
FANART = os.path.join(home, 'fanart.jpg')

if __name__ == '__main__':
    params = dict(urlparse.parse_qsl(sys.argv[2][1:]))
    utils.addon_log('params = {0}'.format(params))

    mode = int(params.get('mode')) if params.get('mode') else None

    if mode == None:
        utils.addon_log('getSources')
        guiTools.getSources()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

        if not fileSys.writeTutList("select:PluginType"):
            tutWin = ["Adding content to your library",
                      "Welcome, this is your first time using OSMOSIS. Here, you can select the content type you want to add:",
                      "Video Plugins: Select to add Movies, TV-Shows, YouTube Videos",
                      "Music Plugins: Select to add Music"]
            xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])
    elif mode == 1:
        create.fillPlugins(params.get('url'))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

        if not fileSys.writeTutList("select:Addon"):
            tutWin = ["Adding content to your library",
                      "Here, you can select the Add-on:",
                      "The selected Add-on should provide Video/Music content in the right structure.",
                      "Take a look at ++ Naming video files/TV shows ++ http://kodi.wiki/view/naming_video_files/TV_shows."]
            xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])
    elif mode == 2:
        create.fillPluginItems(params.get('url'))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    elif mode == 666:
        updateAll.strm_update()
    elif mode == 4:
        selectedItems = guiTools.mediaListDialog(header_prefix='Update')
        if selectedItems and len(selectedItems) > 0:
            updateAll.strm_update(selectedItems)
    elif mode == 41:
        selectedItems = guiTools.mediaListDialog(header_prefix='Rename', expand=False)
        if selectedItems and len(selectedItems) > 0:
            create.renameMediaListEntry(selectedItems)
    elif mode == 42:
        selectedItems = guiTools.mediaListDialog(header_prefix='Update')
        if selectedItems and len(selectedItems) > 0:
            create.removeAndReadMedialistEntry(selectedItems)
    elif mode == 5:
        create.removeItemsFromMediaList('list')
    elif mode == 51:
        selectedItems = guiTools.mediaListDialog(True, False, header_prefix='Remove Shows from TVDB cache', cTypeFilter='TV-Shows')
        if selectedItems and len(selectedItems) > 0:
            tvdb.removeShowsFromTVDBCache(selectedItems)
    elif mode == 52:
        tvdb.removeShowsFromTVDBCache()
    elif mode == 6:
        xbmc.executebuiltin('InstallAddon(service.watchdog)')
        xbmc.executebuiltin("XBMC.Container.Refresh")
    elif mode == 7:
        jsonUtils.jsonrpc('Addons.SetAddonEnabled', { "addonid": "service.watchdog", "enabled": True})
        xbmc.executebuiltin("XBMC.Container.Refresh")
    elif mode == 10:
        selectedEntry = None
        mediaType = params.get('mediaType')
        if mediaType:
            if params.get('id') or params.get('showid'):
                providers = kodiDB.getVideo(params.get('id')) if params.get('id') else kodiDB.getVideo(params.get('showid'), params.get('episode'))
                if len(providers) == 1:
                    selectedEntry = providers[0]
                else:
                    selectProvider = ['[{0}] {1}'.format(stringUtils.getProvidername(provider[0]), stringUtils.parseMediaListURL(provider[0])[0]) for provider in providers]

                    choice = guiTools.selectDialog('OSMOSIS: Select provider!', selectProvider)
                    if choice > -1: selectedEntry = providers[choice]

            if selectedEntry:
                item = xbmcgui.ListItem(path=stringUtils.parseMediaListURL(selectedEntry[0])[1])

                props = None
                infoLabels = {}

                if mediaType == 'show':
                    sTVShowTitle = sys.argv[0][sys.argv[0].index('|') + 1:]
                    sTVShowTitle = stringUtils.unicodetoascii(sTVShowTitle)
                    iSeason = int(params.get('episode')[1:params.get('episode').index('e')])
                    iEpisode = params.get('episode')[params.get('episode').index('e') + 1:]
                    props = kodiDB.getKodiEpisodeID(sTVShowTitle, iSeason, iEpisode)

                    infoLabels['tvShowTitle'] = sTVShowTitle
                    infoLabels['season'] = iSeason
                    infoLabels['episode'] = iEpisode
                    infoLabels['mediatype'] = 'episode'
                    if props:
                        infoLabels['title'] = props[2]
                        infoLabels['aired'] = props[3]

                    # match = re.search('<thumb>(.*)<\/thumb>', props[4])
                    # if match:
                    #   item.setArt({'thumb': match.group(1)})
                else:
                    sTitle = sys.argv[0][sys.argv[0].index('|') + 1:]
                    props = kodiDB.getKodiMovieID(sTitle)
                    infoLabels['title'] = sTitle
                    infoLabels['mediatype'] = 'movie'
                    if props:
                        infoLabels['premiered'] = props[2]
                        infoLabels['genre'] = props[3]

                if len(infoLabels) > 0:
                    item.setInfo('video', infoLabels)

                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

                # Wait until the media is started in player
                counter = 0
                activePlayers = {}
                title = params.get('episode') if mediaType == 'show' else stringUtils.cleanStrmFilesys(infoLabels.get('title'))
                while len(activePlayers) == 0 or (xbmc.Player().isPlayingVideo() and xbmc.getInfoLabel('Player.Filename') != "{0}.strm".format(title)):
                    activePlayers = jsonUtils.jsonrpc('Player.GetActivePlayers')
                    xbmc.sleep(100)
                    counter += 1
                    if counter >= 600:
                        raise

                resumePoint = kodiDB.getPlayedURLResumePoint({'filename': xbmc.getInfoLabel('Player.Filename'), 'path': xbmc.getInfoLabel('Player.Folderpath')})
                guiTools.resumePointDialog(resumePoint)
            elif mediaType == 'audio' and params.get('url', '').startswith('plugin://'):
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=params.get('url')))
            else:
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem())
        else:
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem(path=params.get('url')))
    elif mode == 100:
        create.fillPlugins(params.get('url'))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    elif mode == 101:
        create.fillPluginItems(params.get('url'), name_parent=params.get('name', ''))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

        if not fileSys.writeTutList("select:AddonNavi"):
            tutWin = ["Adding content to your library",
                      "Search for your Movie, TV-Show or Music.",
                      "Mark/select content, do not play a Movie or enter a TV-Show.",
                      "Open context menu on the selected and select *create strms*."]
            xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])
    elif mode == 200:
        utils.addon_log("write multi strms")
        create.addToMedialist(params)
    elif mode == 201:
        utils.addon_log("write single strm")
        # create.fillPluginItems(url)
        # makeSTRM(name, name, url)
    elif mode == 202:
        utils.addon_log("Add all season individually to MediaList")
        create.addMultipleSeasonToMediaList(params)