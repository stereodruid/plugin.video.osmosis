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
from resources.lib import player
from resources.lib import tvdb
from resources.lib import updateAll

try:
    from urllib.parse import parse_qsl
except:
    from urlparse import parse_qsl

addon = xbmcaddon.Addon()
home = py2_decode(xbmc.translatePath(addon.getAddonInfo('path')))
FANART = os.path.join(home, 'fanart.jpg')

if __name__ == '__main__':
    params = dict(parse_qsl(sys.argv[2][1:]))
    for paramKey in params.keys():
        params[paramKey] = py2_decode(params.get(paramKey))
    utils.addon_log('params = {0}'.format(params))

    mode = int(params.get('mode')) if params.get('mode') else None

    if mode == None:
        guiTools.getSources()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

        if not fileSys.writeTutList('select:PluginType'):
            tutWin = ['Adding content to your library',
                      'Welcome, this is your first time using OSMOSIS. Here, you can select the content type you want to add:',
                      'Video Plugins: Select to add Movies, TV-Shows, YouTube Videos',
                      'Music Plugins: Select to add Music']
            xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])
    elif mode == 1:
        create.fillPlugins(params.get('url'))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

        if not fileSys.writeTutList('select:Addon'):
            tutWin = ['Adding content to your library',
                      'Here, you can select the Add-on:',
                      'The selected Add-on should provide Video/Music content in the right structure.',
                      'Take a look at ++ Naming video files/TV shows ++ http://kodi.wiki/view/naming_video_files/TV_shows.']
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
        xbmc.executebuiltin('XBMC.Container.Refresh')
    elif mode == 7:
        jsonUtils.jsonrpc('Addons.SetAddonEnabled', dict(addonid='service.watchdog', enabled=True))
        xbmc.executebuiltin('XBMC.Container.Refresh')
    elif mode == 10:
        player.play(sys.argv, params)
    elif mode == 100:
        create.fillPlugins(params.get('url'))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    elif mode == 101:
        create.fillPluginItems(params.get('url'), name_parent=params.get('name', ''))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

        if not fileSys.writeTutList('select:AddonNavi'):
            tutWin = ['Adding content to your library',
                      'Search for your Movie, TV-Show or Music.',
                      'Mark/select content, do not play a Movie or enter a TV-Show.',
                      'Open context menu on the selected and select *create strms*.']
            xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])
    elif mode == 102:
        favs = jsonUtils.jsonrpc('Favourites.GetFavourites', dict(properties=['path', 'window', 'windowparameter', 'thumbnail'])).get('favourites', {})
        for fav in favs:
            if params.get('type') == 'video' and fav.get('window') == 'videos':
                guiTools.addDir(fav.get('title'), fav.get('windowparameter'), 101, {'thumb': fav.get('thumbnail')}, type=type)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    elif mode == 200:
        utils.addon_log('write multi strms')
        create.addToMedialist(params)
    elif mode == 201:
        utils.addon_log('write single strm')
        # create.fillPluginItems(url)
        # makeSTRM(name, name, url)
    elif mode == 202:
        utils.addon_log('Add all season individually to MediaList')
        create.addMultipleSeasonToMediaList(params)