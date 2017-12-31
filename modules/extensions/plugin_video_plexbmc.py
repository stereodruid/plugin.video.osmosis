#!/usr/bin/env python
# -*- coding: utf-8 -*-

from modules import stringUtils, jsonUtils, fileSys
import os
import xbmc, xbmcaddon

ADDON_ID = 'plugin.video.osmosis'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
MEDIALIST_PATH = REAL_SETTINGS.getSetting('MediaList_LOC').decode('utf-8')


def update(strm_name, url, media_type, thelist):
    plex_details = jsonUtils.requestList("plugin://plugin.video.plexbmc", media_type).get('files', [])
    for plex_detail in plex_details:
        if strm_name.replace('++RenamedTitle++', '') == stringUtils.cleanLabels(plex_detail['label']):
            serverurl = plex_detail['file']
            if url != serverurl:
                for entry in thelist:
                    if entry.split("|")[1] == strm_name:
                        newentry = '|'.join([entry.split("|")[0], entry.split("|")[1].decode("utf-8"), serverurl]) + '\n'
                        thelist = stringUtils.replaceStringElem(thelist, entry, newentry)
                        thefile = fileSys.completePath(os.path.join(MEDIALIST_PATH))
                        thefile = xbmc.translatePath(os.path.join(thefile, 'MediaList.xml'))
                        with open(thefile.decode("utf-8"), 'w') as output_file:
                            for linje in thelist:
                                if not linje.startswith('\n'):
                                    output_file.write(linje.strip().encode('utf-8') + '\n')
                                else:
                                    output_file.write(linje.strip())
                        return serverurl
            else:
                break
    return url
