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
import xbmcaddon

try:
    import urllib.parse as urllib
except:
    import urllib

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')


def stripUnquoteURL(url):
    if url.startswith("image://"):
        url = urllib.unquote_plus(url.replace("image://", "").strip("/"))
    else:
        url = urllib.unquote_plus(url.strip("/"))
    return url


def getURL(par):
    try:
        if par.startswith('?url=plugin://{0}/'.format(addon_id)):
            url = par.split('?url=')[1]
        else:
            url = par.split('?url=')[1]
            url = url.split('&mode=')[0]
    except:
        url = None
    return url
