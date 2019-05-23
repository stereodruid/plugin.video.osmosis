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
kodi_version = int(xbmc.getInfoLabel("System.BuildVersion")[:2])

if __name__ == "__main__":
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

    params = dict(urlparse.parse_qsl(sys.argv[2][1:]))
    utils.addon_log("params = %s" % (params))

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
#         markName = params["url"].decode('utf-8').split('|')[1]
#     except:
#         pass
    try:
        url = params["url"]
    except:
        try:
            url = urlUtils.getURL(sys.argv[2])
        except:
            pass
        pass
    try:
        name = params["name"]
    except:
        name = None
    try:
        iconimage = params["iconimage"]
    except:
        pass
    try:
        movID = params["id"]
    except:
        movID = None
        pass
    try:
        shoID = params["showid"]
    except:
        shoID = None
        pass
    try:
        showID = params["showid"]
    except:
        showID = None
        pass
    try:
        mediaType = params["mediaType"]
    except:
        mediaType = None
        pass
    try:
        episode = params["episode"]
    except:
        episode = None
        pass
    try:
        fanart = params["fanart"]
    except:
        pass
    try:
        mode = int(params["mode"])
    except:
        pass
    try:
        playlist = eval(params["playlist"].replace('||', ','))
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
    try:
        filetype = params.get("filetype", "directory")
    except:
        pass

    if mode == None:
        utils.addon_log("getSources")
        guiTools.getSources()

        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

        if not fileSys.writeTutList("select:PluginType"):
            tutWin = ["Adding content to your library",
                      "Welcome, this is your first time using OSMOSIS. Here, you can select the content type you want to add:",
                      "Video Plugins: Select to add Movies, TV-Shows, YouTube Videos",
                      "Music Plugins: Select to add Music"]
            xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])
    elif mode == 1:
        create.fillPlugins(url)
        if not fileSys.writeTutList("select:Addon"):
            tutWin = ["Adding content to your library",
                      "Here, you can select the Add-on:",
                      "The selected Add-on should provide Video/Music content in the right structure.",
                      "Take a look at ++ Naming video files/TV shows ++ http://kodi.wiki/view/naming_video_files/TV_shows."]
            xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])
        try:
            xbmcplugin.setContent(int(sys.argv[1]), 'movies')
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        except:
            pass
    elif mode == 2:
        create.fillPluginItems(url)
        try:
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        except:
            pass
    elif mode == 666:
        updateAll.strm_update()
    elif mode == 4:
        selectedItems = create.getMediaListDialog()
        if selectedItems:
            updateAll.strm_update(selectedItems)
    elif mode == 5:
        create.removeItemsFromMediaList('list')
    elif mode == 6:
        xbmc.executebuiltin('InstallAddon(service.watchdog)')
    elif mode == 7:
        json_query = ('{"jsonrpc": "2.0", "method":"Addons.SetAddonEnabled", "params":{ "addonid": "service.watchdog", "enabled": true}, "id": 1 }')
        jsonUtils.sendJSON(json_query)
        xbmc.executebuiltin("XBMC.Container.Refresh")
    elif mode == 10:

        selectedEntry = None
        if mediaType:
            if movID or showID:
                providers = kodiDB.getVideo(movID) if movID else kodiDB.getVideo(showID, episode)
                if len(providers) == 1:
                    selectedEntry = providers[0]
                else:
                    selectProvider = []
                    for i in providers:
                        selectProvider.append(i[1])

                    selectedEntry = providers[guiTools.selectDialog(selectProvider, header='OSMOSIS: Select provider!')]

        if selectedEntry:
            url = selectedEntry[0]
            item = xbmcgui.ListItem(path=url)

            if mediaType:
                props = None
                infoLabels = {}

                if mediaType == 'show':
                    sTVShowTitle = sys.argv[0][sys.argv[0].index('|') + 1:]
                    sTVShowTitle = stringUtils.unicodetoascii(sTVShowTitle)
                    iSeason = int(episode[1:episode.index('e')])
                    iEpisode = int(episode[episode.index('e') + 1:])
                    props = kodiDB.getKodiEpisodeID(sTVShowTitle, iSeason, iEpisode)

                    infoLabels['tvShowTitle'] = sTVShowTitle
                    infoLabels['season'] = iSeason
                    infoLabels['episode'] = iEpisode
                    infoLabels['mediatype'] = 'episode'
                    if props:
                        infoLabels['title'] = props[2]
                        infoLabels['aired'] = props[3]
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
                title = episode if mediaType == 'show' else stringUtils.cleanStrmFilesys(infoLabels.get('title'))
                while len(activePlayers) == 0 or (xbmc.Player().isPlayingVideo() and xbmc.getInfoLabel('Player.Filename') != "{0}.strm".format(title)):
                    activePlayers = json.loads(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}')).get('result', [])
                    xbmc.sleep(100)
                    counter += 1
                    if counter >= 600:
                        raise

                resumePoint = kodiDB.getPlayedURLResumePoint({'filename': xbmc.getInfoLabel('Player.Filename'), 'path': xbmc.getInfoLabel('Player.Folderpath')})
                guiTools.resumePointDialog(resumePoint)
            else:
                # Exec play process
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
        else:
            try:
                # Get infos from selectet media
                item = xbmcgui.ListItem(path=url)
            # Exec play process
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            except Exception:
                pass
    elif mode == 100:
        create.fillPlugins(url)
        try:
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        except:
            pass
    elif mode == 101:
        create.fillPluginItems(url)
        if not fileSys.writeTutList("select:AddonNavi"):
            tutWin = ["Adding content to your library",
                      "Search for your Movie, TV-Show or Music.",
                      "Mark/select content, do not play a Movie or enter a TV-Show.",
                      "Open context menu on the selected and select *create strms*."]
            xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])

        try:
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        except:
            pass

    elif mode == 200:
        utils.addon_log("write multi strms")

        # A dialog to rename the Change Title for Folder and MediaList entry:
        selectAction = ['No, continue with original Title!', 'Rename Title!']
        if not fileSys.writeTutList("select:Rename"):
            tutWin = ["Adding content to your library",
                      "You can rename your Movie, TV-Show or Music title.",
                      "To make your scraper recognize the content, some times it is necessary to rename the title.",
                      "Be careful, wrong title can also cause that your scraper can't recognize your content."]
            xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])
        choice = guiTools.selectDialog(selectAction, header='Title for Folder and MediaList entry')
        if choice != -1:
            if choice == 1 or name == None or name == "":
                name = guiTools.editDialog(name).strip() + "++RenamedTitle++"

            if not fileSys.writeTutList("select:ContentTypeLang"):
                tutWin = ["Adding content to your library",
                          "Now select your content type.",
                          "Select language or YouTube type.",
                          "Wait for done message."]
                xbmcgui.Dialog().ok(tutWin[0], tutWin[1], tutWin[2], tutWin[3])

            cType = guiTools.getType(url)
            if filetype == 'file':
                url += '&playMode=play'
            if cType != -1:
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