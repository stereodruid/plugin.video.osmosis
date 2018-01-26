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

import os
import sys
from modules import create
from modules import guiTools
from modules import moduleUtil

import utils
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
import re

addon = xbmcaddon.Addon()
ADDON_PATH = addon.getAddonInfo('path')
MEDIALIST_PATH = addon.getSetting('MediaList_LOC')
MediaList_LOC = xbmc.translatePath(os.path.join(MEDIALIST_PATH, 'MediaList.xml'))
represent = os.path.join(ADDON_PATH, 'icon.png')

actor_update_manual = 0
actor_update_periodictime = 1
actor_update_fixtime = 2


def readMediaList(purge=False):
    try:
        if xbmcvfs.exists(MediaList_LOC):
            fle = xbmcvfs.File(MediaList_LOC, "r")
            thelist = fle.read().splitlines()
            fle.close()
            return thelist
    except:
        pass


def strm_update(selectedItems=None, actor=0):
    try:
        if xbmcvfs.exists(MediaList_LOC):
            thelist = readMediaList() if selectedItems is None else selectedItems
            if len(thelist) > 0:
                dialogeBG = xbmcgui.DialogProgressBG()
                dialogeBG.create("OSMOSIS: " , 'Total Update-Progress:')

                listLen = len(thelist)
                step = j = 100 / listLen
                for entry in thelist:
                    splits = entry.strip().split('|')
                    cType, name, url = splits[0], splits[1], splits[2]

                    try:
                        plugin_id = re.search('%s([^\/\?]*)' % ("plugin:\/\/"), url)
                        if plugin_id:
                            module = moduleUtil.getModule(plugin_id.group(1))
                            if module and hasattr(module, 'update'):
                                url = module.update(name, url, 'video', thelist)

                        dialogeBG.update(j, "OSMOSIS total update process: " , "Current Item: " + name.replace('++RenamedTitle++', '') + " Items left: " + str(listLen))
                        j += step

                        create.fillPluginItems(url, strm=True, strm_name=name, strm_type=cType)
                        listLen -= 1
                    except:
                        pass

                dialogeBG.close()
                if actor == actor_update_periodictime:
                    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (addon.getAddonInfo('name'), "Next update in: " + addon.getSetting('Automatic_Update_Time') + "h" , 5000, represent))
                elif actor == actor_update_fixtime:
                    next_run = addon.getSetting('update_time')[:5]
                    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (addon.getAddonInfo('name'), "Next update: " + next_run + "h" , 5000, represent))
    except IOError as (errno, strerror):
        print ("I/O error({0}): {1}").format(errno, strerror)
    except ValueError:
        print ("No valid integer in line.")
    except:
        guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1]) + (". See your Kodi.log!"))
        utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
        print ("Unexpected error:"), sys.exc_info()[1]
        pass
