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

import os, sys
import urllib, urlparse
import time
import re
import json
from modules import create
from modules import kodiDB
from modules import fileSys
from modules import guiTools
from modules import urlUtils
from modules import updateAll
from modules import moduleUtil
from modules import stringUtils
from modules import jsonUtils

import utils
import xbmc, xbmcaddon, xbmcgui, xbmcplugin

addon = xbmcaddon.Addon()
home = xbmc.translatePath(addon.getAddonInfo('path').decode('utf-8'))
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
        selectedItems = guiTools.mediaListDialog()
        if selectedItems and len(selectedItems) > 0:
            updateAll.strm_update(selectedItems)
    elif mode == 5:
        create.removeItemsFromMediaList('list')
    elif mode == 6:
        xbmc.executebuiltin('InstallAddon(service.watchdog)')
        xbmc.executebuiltin("XBMC.Container.Refresh")
    elif mode == 7:
        json_query = ('{"jsonrpc": "2.0", "method":"Addons.SetAddonEnabled", "params":{ "addonid": "service.watchdog", "enabled": true}, "id": 1 }')
        jsonUtils.sendJSON(json_query)
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
                    selectProvider = [stringUtils.getProvidername(provider[0]) for provider in providers]

                    choice = guiTools.selectDialog('OSMOSIS: Select provider!', selectProvider)
                    if choice > -1: selectedEntry = providers[choice]

            if selectedEntry:
                item = xbmcgui.ListItem(path=selectedEntry[0])

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

                    #match = re.search('<thumb>(.*)<\/thumb>', props[4])
                    #if match:
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
                activePlayers = []
                title = params.get('episode') if mediaType == 'show' else stringUtils.cleanStrmFilesys(infoLabels.get('title'))
                while len(activePlayers) == 0 or (xbmc.Player().isPlayingVideo() and xbmc.getInfoLabel('Player.Filename') != "{0}.strm".format(title)):
                    activePlayers = json.loads(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}')).get('result', [])
                    xbmc.sleep(100)
                    counter += 1
                    if counter >= 600:
                        raise

                resumePoint = kodiDB.getPlayedURLResumePoint({'filename': xbmc.getInfoLabel('Player.Filename'), 'path': xbmc.getInfoLabel('Player.Folderpath')})
                guiTools.resumePointDialog(resumePoint)
            else:
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem())
        else:
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem(path=params.get('url')))
    elif mode == 100:
        create.fillPlugins(params.get('url'))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    elif mode == 101:
        create.fillPluginItems(params.get('url'))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

        if not fileSys.writeTutList("select:AddonNavi"):
            tutWin = ["Adding content to your library",
                      "Search for your Movie, TV-Show or Music.",
                      "Mark/select content, do not play a Movie or enter a TV-Show.",
                      "Open context menu on the selected and select *create strms*."]
            xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])
    elif mode == 200:
        utils.addon_log("write multi strms")

        # A dialog to rename the Change Title for Folder and MediaList entry:
        selectAction = ['No, continue with original Title', 'Rename Title', 'Get Title from Medialist']
        if not fileSys.writeTutList("select:Rename"):
            tutWin = ["Adding content to your library",
                      "You can rename your Movie, TV-Show or Music title.",
                      "To make your scraper recognize the content, some times it is necessary to rename the title.",
                      "Be careful, wrong title can also cause that your scraper can't recognize your content."]
            xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])
        choice = guiTools.selectDialog('Title for Folder and MediaList entry', selectAction)
        if choice != -1:
            cType = None
            name = params.get('name')
            if choice == 1 or name == None or name == '':
                name = guiTools.editDialog(name).strip()
                name = "{0}++RenamedTitle++".format(name) if name else name

            if choice == 2:
                item = guiTools.mediaListDialog(False, False)
                splits = item.get('entry').split('|') if item else None
                name = splits[1] if splits else None
                cType = splits[0] if splits else None

            if name:
                url = params.get('url')
                if not fileSys.writeTutList("select:ContentTypeLang"):
                    tutWin = ["Adding content to your library",
                              "Now select your content type.",
                              "Select language or YouTube type.",
                              "Wait for done message."]
                    xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])

                if not cType:
                    cType = guiTools.getType(url)
                if cType != -1:
                    if params.get('filetype', 'directory') == 'file':
                        url += '&playMode=play'
                    fileSys.writeMediaList(url, name, cType)
                    xbmcgui.Dialog().notification(cType, name.replace('++RenamedTitle++', ''), xbmcgui.NOTIFICATION_INFO, 5000, False)

                    try:
                        plugin_id = re.search('%s([^\/\?]*)' % ("plugin:\/\/"), url)
                        if plugin_id:
                            module = moduleUtil.getModule(plugin_id.group(1))
                            if module and hasattr(module, 'create'):
                                url = module.create(name, url, 'video')
                    except:
                        pass

                    create.fillPluginItems(url, strm=True, strm_name=name, strm_type=cType)
                    xbmcgui.Dialog().notification('Writing items...', "Done", xbmcgui.NOTIFICATION_INFO, 5000, False)
    elif mode == 201:
        utils.addon_log("write single strm")
        # create.fillPluginItems(url)
        # makeSTRM(name, name, url)
