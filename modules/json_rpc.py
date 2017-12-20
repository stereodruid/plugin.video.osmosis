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

import sys
import xbmc
import utils

if sys.version_info < (2, 7):
    import simplejson as json
else:
    import json

def getEpisode(sTVShowTitle, iSeason, iEpisode):
    tvShow = getKodiTVShow(sTVShowTitle)

    if tvShow:
        query = ('{"jsonrpc":"2.0","method":"VideoLibrary.GetEpisodes", "params":{"tvshowid": %d, "season": %d, "properties": [ "title", "playcount", "season", "episode", "showtitle", "plot", "file", "rating", "resume", "tvshowid", "art", "firstaired", "runtime", "writer", "dateadded", "lastplayed", "streamdetails"]}, "id": 1}') % (tvShow.get('tvshowid'), iSeason)
        result = xbmc.executeJSONRPC(query)
        episodes = json.loads(result.decode('utf-8')).get('result', {}).get('episodes', {})

        for episode in episodes:
            if episode.get('episode') == iEpisode:
                return episode

    return None

def getTVShow(sTVShowTitle):
    query = ('{"jsonrpc":"2.0","method":"VideoLibrary.GetTVShows", "id": 1}')
    result = xbmc.executeJSONRPC(query)
    tvShows = json.loads(result.decode('utf-8')).get('result', {}).get('tvshows', {})

    for show in tvShows:
        if show.get('label') == sTVShowTitle:
            return show

    return None