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
from . import create
from . import guiTools
from . import moduleUtil
from . import stringUtils
from . import fileSys

import utils
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
import re

addon = xbmcaddon.Addon()
ADDON_PATH = addon.getAddonInfo('path')
MEDIALIST_PATH = addon.getSetting('MediaList_LOC')
MediaList_LOC = xbmc.translatePath(os.path.join(MEDIALIST_PATH, 'MediaList.xml'))
represent = os.path.join(ADDON_PATH, 'resources/media/icon.png')

actor_update_manual = 0
actor_update_periodictime = 1
actor_update_fixtime = 2

def strm_update(selectedItems=None, actor=0):
    if xbmcvfs.exists(MediaList_LOC):
        thelist = sorted(fileSys.readMediaList())
        items = selectedItems if selectedItems else [{'entry': item} for item in thelist]
        if len(items) > 0:
            dialogeBG = xbmcgui.DialogProgressBG()
            dialogeBG.create("OSMOSIS: " , 'Total Update-Progress:')

            iUrls = 0
            splittedEntries = []
            if not selectedItems:
                for item in items:
                    splits = item.get('entry').split('|')
                    iUrls += len(splits[2].split('<next>'))
                    splittedEntries.append(splits)
            else:
                iUrls = len(selectedItems)
                splittedEntries = [[item.get('entry').split('|')[0], item.get('entry').split('|')[1], item.get('url')] for item in selectedItems]

            step = j = 100 / iUrls
            for splittedEntry in splittedEntries:
                cType, name, url = splittedEntry[0], splittedEntry[1], re.sub('name_orig=[^;]*;', '', splittedEntry[2])

                urls = url.split('<next>')
                for url in urls:
                    plugin_id = re.search('plugin:\/\/([^\/\?]*)', url)
                    if plugin_id:
                        module = moduleUtil.getModule(plugin_id.group(1))
                        if module and hasattr(module, 'update'):
                            url = module.update(name, url, 'video', thelist)

                    dialogeBG.update(j, "OSMOSIS total update process: " , "Current Item: %s Items left: %d" % (stringUtils.getStrmname(name), iUrls))
                    j += step

                    create.fillPluginItems(url, strm=True, strm_name=name, strm_type=cType)
                    iUrls -= 1

            dialogeBG.close()
            if actor == actor_update_periodictime:
                xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (addon.getAddonInfo('name'), "Next update in: " + addon.getSetting('Automatic_Update_Time') + "h" , 5000, represent))
            elif actor == actor_update_fixtime:
                next_run = addon.getSetting('update_time')[:5]
                xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (addon.getAddonInfo('name'), "Next update: " + next_run + "h" , 5000, represent))