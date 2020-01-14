# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from kodi_six.utils import py2_encode, py2_decode
import os
import xbmc, xbmcaddon, xbmcvfs

from .. import stringUtils, jsonUtils, fileSys

addon = xbmcaddon.Addon()


def update(strm_name, url, media_type, thelist):
    plex_details = jsonUtils.requestList('plugin://plugin.video.composite_for_plex', media_type).get('files', [])
    for plex_detail in plex_details:
        orig_name, plugin_id = stringUtils.parseMediaListURL(url)
        if (orig_name and orig_name == plex_detail['label']) \
            or (stringUtils.getStrmname(strm_name) == stringUtils.cleanLabels(plex_detail['label'])):
            serverurl = plex_detail['file']
            if url != serverurl:
                for entry in thelist:
                    splits = entry.split('|')
                    if splits[1] == strm_name:
                        splits[2] = serverurl
                        newentry = '|'.join(splits)
                        thelist = stringUtils.replaceStringElem(thelist, entry, newentry)
                        thefile = py2_decode(xbmc.translatePath(os.path.join(addon.getSetting('MediaList_LOC'), 'MediaList.xml')))

                        output_file = xbmcvfs.File(thefile, 'w')
                        for index, linje in enumerate(thelist):
                            entry = ('{0}\n' if index < len(thelist) - 1 else '{0}').format(linje.strip())
                            output_file.write(py2_encode(entry))

                        return serverurl
            else:
                break
    return url