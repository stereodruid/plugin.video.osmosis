# Copyright (C) 2016 stereodruid(J.G.)
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

from .common import jsonrpc
from .utils import addon_log


def requestItem(file, type='video'):
    addon_log('requestItem, file = {0}'.format(file))
    if file.find('playMode=play') == -1:
        return requestList(file, type)

    return jsonrpc('Player.GetItem', dict(playerid=1, properties=['art', 'title', 'year', 'mpaa', 'imdbnumber', 'description', 'season', 'episode', 'playcount', 'genre', 'duration', 'runtime', 'showtitle', 'album', 'artist', 'plot', 'plotoutline', 'tagline', 'tvshowid']))


def requestList(path, type='video'):
    addon_log('requestList, path = {0}'.format(path))
    if path.find('playMode=play') != -1:
        return requestItem(path, type)

    return jsonrpc('Files.GetDirectory', dict(directory=path, media=type, properties=['art', 'title', 'year', 'track', 'mpaa', 'imdbnumber', 'description', 'season', 'episode', 'playcount', 'genre', 'duration', 'runtime', 'showtitle', 'album', 'artist', 'plot', 'plotoutline', 'tagline', 'tvshowid']))