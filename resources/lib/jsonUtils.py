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
import utils
import xbmc

try:
    import json
except:
    import simplejson as json


def requestItem(file, fletype='video'):
    utils.addon_log('requestItem, file = {0}'.format(file))
    if file.find("playMode=play") == -1:
        return requestList(file, fletype)

    return jsonrpc('Player.GetItem',
                {
                    "playerid": 1,
                    "properties": ["art", "title", "year", "mpaa", "imdbnumber", "description", "season", "episode", "playcount", "genre", "duration", "runtime", "showtitle", "album", "artist", "plot", "plotoutline", "tagline", "tvshowid"]
                })


def requestList(path, fletype='video'):
    utils.addon_log('requestList, path = {0}'.format(path))
    if path.find('playMode=play') != -1:
        return requestItem(path, fletype)

    return jsonrpc('Files.GetDirectory',
                {
                    "directory": path,
                    "media": fletype,
                    "properties": ["art", "title", "year", "track", "mpaa", "imdbnumber", "description", "season", "episode", "playcount", "genre", "duration", "runtime", "showtitle", "album", "artist", "plot", "plotoutline", "tagline", "tvshowid"]
                }
            )


def jsonrpc(action, arguments=None):
    """ put some JSON together for the JSON-RPC APIv6 """
    if arguments is None:
        arguments = {}

    if arguments:
        request = json.dumps({
            'id': 1,
            'jsonrpc': '2.0',
            'method': action,
            'params': arguments
        })
    else:
        request = json.dumps({
            'id': 1,
            'jsonrpc': '2.0',
            'method': action
        })

    utils.addon_log('Sending request to Kodi: {0}'.format(request))
    return parse_jsonrpc(xbmc.executeJSONRPC(request))


def parse_jsonrpc(json_raw):
    if not json_raw:
        utils.addon_log('Empty response from Kodi')
        return {}

    utils.addon_log('Response from Kodi: {0}'.format(py2_decode(json_raw)))
    parsed = json.loads(json_raw)
    if parsed.get('error', False):
        utils.addon_log('Kodi returned an error: {0}'.format(parsed.get('error')))
    return parsed.get('result', {})