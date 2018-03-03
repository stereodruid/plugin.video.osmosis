#!/usr/bin/env python
# -*- coding: utf-8 -*-

from modules import stringUtils, jsonUtils, fileSys
import os
import xbmc, xbmcaddon, xbmcvfs

addon = xbmcaddon.Addon()


def update(strm_name, url, media_type, thelist):
    plex_details = jsonUtils.requestList("plugin://plugin.video.plexbmc", media_type).get('files', [])
    for plex_detail in plex_details:
        if stringUtils.getStrmname(strm_name) == stringUtils.cleanLabels(plex_detail['label']):
            serverurl = plex_detail['file']
            if url != serverurl:
                for entry in thelist:
                    splits = entry.split("|")
                    if splits[1] == strm_name:
                        splits[2] = serverurl
                        newentry = '|'.join(splits)
                        thelist = stringUtils.replaceStringElem(thelist, entry, newentry)
                        thefile = xbmc.translatePath(os.path.join(addon.getSetting('MediaList_LOC'), 'MediaList.xml'))

                        output_file = xbmcvfs.File(thefile.decode("utf-8"), 'w')
                        for index, linje in enumerate(thelist):
                            output_file.write(('%s\n' if index < len(thelist) - 1 else '%s') % linje.strip().encode('utf-8'))

                        return serverurl
            else:
                break
    return url
