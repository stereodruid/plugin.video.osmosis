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

import os
import re
import sys
import datetime

from modules import stringUtils
import xbmc, xbmcaddon, xbmcvfs
import xml.etree.ElementTree as ET

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_version = addon.getAddonInfo('version')
STRM_LOC = xbmc.translatePath(addon.getSetting('STRM_LOC'))


#***************************************************************************************
# Python Header
# Name:
# 		replacer
# Purpose:
# 		Replace multiple string elements.
# Call it like this:
# def multiple_replace(string, *key_values):
#    return replacer(*key_values)(string)
# Author:
# 		stereodruid(J.G.)
# History:
# 		0 - init
def replacer(*key_values):
    replace_dict = dict(key_values)
    replacement_function = lambda match: replace_dict[match.group(0)]
    pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
    return lambda string: pattern.sub(replacement_function, string)


#***************************************************************************************
# Python Header
# 		multiple_replace
# Purpose:
# 		caller for replacer
# Author:
# 		stereodruid(J.G.)
# History:
# 		0 - init
def multiple_replace(string, *key_values):
    return replacer(*key_values)(string.rstrip())


#***************************************************************************************
# Python Header
#        multiple_reSub
# Purpose:
#        reSub all strings insite a dict. Valuse in dict:
# dictReplacements = {'search1' : 'replace with1', 'search2' : 'replace with2'}
# Author:
#        stereodruid(J.G.)
# History:
#        0 - init
def multiple_reSub(text, dic):
    for i, j in dic.iteritems():
        text = re.sub(i, j, text)
    return text.rstrip()


def createSongNFO(filepath, filename , strm_ty='type', artists='none', albums='no album', titls='title', typese='types'):
    # create .nfo xml file
    filepath = os.path.join(STRM_LOC, filepath)

    if not xbmcvfs.exists(filepath):
        xbmcvfs.mkdirs(filepath)
        fullpath = os.path.join(filepath, filename + '.nfo')
        nfo = open(fullpath, 'w+')
        root = ET.Element('musicvideo')
        xtitle = ET.Element('title')
        xtitle.text = titls
        root.append(xtitle)
        xartist = ET.Element('artist')
        xartist.text = artists
        root.append(xartist)
        xalbum = ET.Element('album')
        xalbum.text = albums
        root.append(xalbum)
        s = ET.tostring(root)
        nfo.write(s)
        nfo.close()


def addon_log(string):
    # if debug == 'true':
    xbmc.log("[%s-%s]: %s" % (addon_id, addon_version, string))


def zeitspanne(sekunden):

    delta = datetime.timedelta(seconds=sekunden)
    delta_str = str(delta)[-8:]  # z.B: " 1:01:01"
    hours, minutes, seconds = [ int(val) for val in delta_str.split(":", 3) ]
    weeks = delta.days // 7
    days = delta.days % 7
    timePlayed = datetime.time(hours, minutes, seconds)
    return weeks, days, hours, minutes, seconds, timePlayed

