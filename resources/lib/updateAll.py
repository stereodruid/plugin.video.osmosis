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
import re
import xbmcvfs

from .common import Globals, Settings
from .create import fillPluginItems
from .fileSys import readMediaList
from .guiTools import selectDialog
from .l10n import getString
from .moduleUtil import getModule
from .stringUtils import getProviderId, getStrmname, parseMediaListURL

actor_update_manual = 0
actor_update_periodictime = 1
actor_update_fixtime = 2


def strm_update(selectedItems=None, actor=0):
    settings = Settings()
    if xbmcvfs.exists(settings.MEDIALIST_FILENNAME_AND_PATH):
        globals = Globals()
        thelist = sorted(readMediaList())
        if not selectedItems and actor == actor_update_manual:
            selectActions = [dict(id='Movies', string_id=39111), dict(id='TV-Shows', string_id=39112), dict(id='Audio', string_id=39113), dict(id='All', string_id=39122)]
            choice = selectDialog('{0}: {1}'.format(getString(39123, globals.addon), getString(39109, globals.addon)), [getString(selectAction.get('string_id')) for selectAction in selectActions])
            if choice == -1:
                return
            elif choice == 3:
                cTypeFilter = None
            else:
                cTypeFilter = selectActions[choice].get('id')
        else:
            cTypeFilter = None

        items = selectedItems if selectedItems else [{'entry': item} for item in thelist]
        if len(items) > 0:
            pDialog = globals.dialogProgressBG
            pDialog.create(getString(39140, globals.addon))

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

            tUrls = iUrls
            step = j = 100 / tUrls
            for index, splittedEntry in enumerate(splittedEntries):
                cType, name, url = splittedEntry[0], splittedEntry[1], splittedEntry[2]

                urls = url.split('<next>')
                for url in urls:
                    name_orig, plugin_url = parseMediaListURL(url)
                    plugin_id = getProviderId(plugin_url).get('plugin_id')
                    if plugin_id:
                        module = getModule(plugin_id)
                        if module and hasattr(module, 'update'):
                            url = module.update(name, url, 'video', thelist)

                    pDialog.update(int(j), heading='{0}: {1}/{2}'.format(getString(39140, globals.addon), (index + 1), iUrls), message='\'{0}\' {1}'.format(getStrmname(name), getString(39134, globals.addon)))
                    j += step

                    fillPluginItems(url, strm=True, strm_name=name, strm_type=cType, name_orig=name_orig, pDialog=pDialog)
                    tUrls -= 1

            pDialog.close()
            if actor == actor_update_periodictime:
                globals.dialog.notification(getString(39123, globals.addon), '{0} {1}h'.format(getString(39136, globals.addon), settings.AUTOMATIC_UPDATE_TIME), globals.MEDIA_ICON, 2000, True)
            elif actor == actor_update_fixtime:
                next_run = settings.UPDATE_TIME[:5]
                globals.dialog.notification(getString(39123, globals.addon), '{0} {1}h'.format(getString(39137, globals.addon), next_run), globals.MEDIA_ICON, 2000, True)