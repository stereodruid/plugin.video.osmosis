# Copyright (C) 2016 stereodruid(J.Gina)
#
#
# This file is part of OSMOSIS
#
# OSMOSIS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OSMOSIS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OSMOSIS.  If not, see <http://www.gnu.org/licenses/>.

import re
import sys
import os
reload(sys)  
sys.setdefaultencoding('utf8')
import random
import string
import xml.etree.ElementTree as ET
from os.path import basename, splitext
from os import getcwd
from glob import glob
import xbmc
REMOTE_DBG = True
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs
addon = xbmcaddon.Addon('plugin.video.osmosis')
addon_version = addon.getAddonInfo('version')
ADDON_NAME = addon.getAddonInfo('name')
profile = xbmc.translatePath(addon.getAddonInfo('profile').decode('utf-8'))
home = xbmc.translatePath(addon.getAddonInfo('path').decode('utf-8'))
dialog = xbmcgui.Dialog()
source_file = os.path.join(home, 'source_file')
functions_dir = profile

DIRS = []
STRM_LOC = xbmc.translatePath(addon.getSetting('STRM_LOC'))

#***************************************************************************************
# Python Header 
# Name:
#		replacer
# Purpose:
#		Replace multiple string elements.
# Call it like this:
# def multiple_replace(string, *key_values):
#    return replacer(*key_values)(string)
# Author:
#		stereodruid(J.G.)
# History:
#		0 - init 
def replacer(*key_values):
    replace_dict = uni(dict(key_values))
    replacement_function = lambda match: replace_dict[match.group(0)]
    pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
    return lambda string: pattern.sub(replacement_function, string)
#***************************************************************************************
# Python Header 
#		multiple_replace
# Purpose:
#		caller for replacer
# Author:
#		stereodruid(J.G.)
# History:
#		0 - init 
def multiple_replace(string, *key_values):
    return replacer(*key_values)(string)

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
    return text

def ascii(string):
    if isinstance(string, basestring):
        if isinstance(string, unicode):
           string = string.encode('ascii', 'ignore')
    return string

def uni(string):
    if isinstance(string, basestring):
        if isinstance(string, unicode):
           string = string.encode('utf-8', 'ignore' )
    return string
def createSongNFO(filepath, filename , strm_ty='type',artists='none', albums='no album', titls='title', typese='types'):    
    #create .nfo xml file
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