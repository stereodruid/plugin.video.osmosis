# This file is part of OSMOSIS.
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

# -*- coding: utf-8 -*-

import os
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP
import SimpleDownloader as downloader
import pyxbmct
import xbmc
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs

try:
    import json
except:
    import simplejson as json


addnon_id = 'plugin.video.osmosis'
addon = xbmcaddon.Addon(addnon_id)
addon_version = addon.getAddonInfo('version')
ADDON_NAME = addon.getAddonInfo('name')
REAL_SETTINGS = xbmcaddon.Addon(id=addnon_id)
ADDON_SETTINGS = REAL_SETTINGS.getAddonInfo('profile')
MediaList_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS,'MediaList.xml'))
STRM_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS,'STRM_LOC'))
profile = xbmc.translatePath(addon.getAddonInfo('profile').decode('utf-8'))
home = xbmc.translatePath(addon.getAddonInfo('path').decode('utf-8'))
favorites = os.path.join(profile, 'favorites')
history = os.path.join(profile, 'history')
dialog = xbmcgui.Dialog()
icon = os.path.join(home, 'icon.png')
iconRemove = os.path.join(home, 'iconRemove.png')
FANART = os.path.join(home, 'fanart.jpg')
source_file = os.path.join(home, 'source_file')
functions_dir = profile
downloader = downloader.SimpleDownloader()
debug = addon.getSetting('debug')

if os.path.exists(favorites) == True:
    FAV = open(favorites).read()
else: FAV = []
if os.path.exists(favorites) == True:
    FAV = open(favorites).read()
else: FAV = []

DIRS = []
STRM_LOC = xbmc.translatePath(addon.getSetting('STRM_LOC'))

def getURL(par):
    try:
        if par.startswith('?url=plugin://plugin.video.osmosis/'):
            url = par.split('?url=')[1]
        else:
            url = par.split('?url=')[1]
            url = url.split('&mode=')[0]
    except:
        url = None
    return url