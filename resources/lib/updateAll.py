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
import os
import re
import sys
import xbmc
import xbmcvfs

from .common import Globals, Settings
from .create import fillPluginItems
from .fileSys import readMediaList
from .guiTools import selectDialog
from .moduleUtil import getModule
from .stringUtils import getProviderId, getStrmname, parseMediaListURL

actor_update_manual = 0
actor_update_periodictime = 1
actor_update_fixtime = 2


def strm_update(selectedItems=None, actor=0):
    globals = Globals()
    settings = Settings()
    if xbmcvfs.exists(settings.MEDIALIST_FILENNAME_AND_PATH):
        thelist = sorted(readMediaList())
        if not selectedItems and actor == actor_update_manual:
            selectAction = ['Movies', 'TV-Shows', 'Audio', 'All']
            choice = selectDialog('Update all: Select which Media Types to update', selectAction)
            if choice == -1:
                return
            elif choice == 3:
                cTypeFilter = None
            else:
                cTypeFilter = selectAction[choice]
        else:
            cTypeFilter = None

        items = selectedItems if selectedItems else [{'entry': item} for item in thelist]
        if len(items) > 0:
            pDialog = globals.dialogProgressBG
            pDialog.create('OSMOSIS total update process')

            iUrls = 0
            splittedEntries = []
            for item in items:
                splits = item.get('entry').split('|')
                if cTypeFilter and not re.findall(cTypeFilter, splits[0]):
                    continue
                iUrls += len(splits[2].split('<next>'))
                splittedEntries.append(splits)

            if iUrls == 0:
                pDialog.close()
                return

            step = j = 100 / iUrls
            for splittedEntry in splittedEntries:
                cType, name, url = splittedEntry[0], splittedEntry[1], splittedEntry[2]

                urls = url.split('<next>')
                for url in urls:
                    name_orig, plugin_url = parseMediaListURL(url)
                    plugin_id = getProviderId(plugin_url).get('plugin_id')
                    if plugin_id:
                        module = getModule(plugin_id)
                        if module and hasattr(module, 'update'):
                            url = module.update(name, url, 'video', thelist)

                    pDialog.update(int(j), message='Current Item: {0}; Items left: {1}'.format(getStrmname(name), iUrls))
                    j += step

                    fillPluginItems(url, strm=True, strm_name=name, strm_type=cType, name_orig=name_orig, pDialog=pDialog)
                    iUrls -= 1
            xbmc.log("updateAll: dialog isFinished = {0}".format(pDialog.isFinished()))
            pDialog.close()
            xbmc.log("updateAll: dialog isFinished = {0}".format(pDialog.isFinished()))
            if actor == actor_update_periodictime:
                xbmc.executebuiltin('Notification({0}, {1}, {2}, {3})'.format(globals.PLUGIN_NAME, 'Next update in: {0}h'.format(settings.AUTOMATIC_UPDATE_TIME), 5000, globals.MEDIA_ICON))
            elif actor == actor_update_fixtime:
                next_run = settings.UPDATE_TIME[:5]
                xbmc.executebuiltin('Notification({0}, {1}, {2}, {3})'.format(globals.PLUGIN_NAME, 'Next update: {0}h'.format(next_run), 5000, globals.MEDIA_ICON))