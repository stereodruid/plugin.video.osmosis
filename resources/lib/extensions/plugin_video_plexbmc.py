# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from kodi_six.utils import py2_encode, py2_decode
import os
import xbmc
import xbmcvfs

from ..common import Globals, Settings
from ..jsonUtils import requestList
from ..stringUtils import cleanLabels, getStrmname, parseMediaListURL, replaceStringElem


def update(strm_name, url, media_type, thelist):
    globals = Globals()
    settings = Settings()
    plex_details = requestList('plugin://plugin.video.plexbmc', media_type).get('files', [])
    for plex_detail in plex_details:
        orig_name, plugin_url = parseMediaListURL(url)
        if (orig_name and orig_name == plex_detail['label']) \
            or (getStrmname(strm_name) == cleanLabels(plex_detail['label'])):
            serverurl = plex_detail['file']
            if url != serverurl:
                for entry in thelist:
                    splits = entry.split('|')
                    if splits[1] == strm_name:
                        splits[2] = serverurl
                        newentry = '|'.join(splits)
                        thelist = replaceStringElem(thelist, entry, newentry)

                        output_file = xbmcvfs.File(settings.MEDIALIST_FILENNAME_AND_PATH, 'w')
                        for index, linje in enumerate(thelist):
                            entry = ('{0}\n' if index < len(thelist) - 1 else '{0}').format(linje.strip())
                            output_file.write(py2_encode(entry))

                        return serverurl
            else:
                break
    return url