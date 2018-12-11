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

from modules import stringUtils
import utils
import xbmc

try:
    import json
except:
    import simplejson as json


def requestItem(file, fletype='video'):
    utils.addon_log("requestItem, file = " + file)
    if file.find("playMode=play") == -1:
        return requestList(file, fletype)

    json_query = ('{"jsonrpc":"2.0","method":"Player.GetItem","params":{"playerid":1,"properties":["art","title","year","mpaa","imdbnumber","description","season","episode","playcount","genre","duration","runtime","showtitle","album","artist","plot","plotoutline","tagline","tvshowid"]}, "id": 1}')
    return sendJSON(json_query)


def requestList(path, fletype='video'):
    utils.addon_log("requestList, path = " + path)
    if path.find("playMode=play") != -1:
        return requestItem(path, fletype)

    json_query = ('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "%s", "media": "%s", "properties":["art","title","year","track","mpaa","imdbnumber","description","season","episode","playcount","genre","duration","runtime","showtitle","album","artist","plot","plotoutline","tagline","tvshowid"]}, "id": 1}' % (path, fletype))
    return sendJSON(json_query)


def sendJSON(command):
    data = xbmc.executeJSONRPC(command)
    return json.loads(data).get('result', {})
