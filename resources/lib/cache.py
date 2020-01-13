# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from kodi_six.utils import py2_encode
import xbmcaddon

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')

showCache = StorageServer.StorageServer(py2_encode('{0}TVShowsTVDB1').format(addon_name), 24 * 30)
episodeCache = StorageServer.StorageServer(py2_encode('{0}EpisodesTVDB1').format(addon_name), 24 * 30)
episodeCache_manual = StorageServer.StorageServer(py2_encode('{0}EpisodesManual1').format(addon_name), 24 * 365)
tvdbDataCache = StorageServer.StorageServer(py2_encode('{0}TVDBData1').format(addon_name), 1)
addonnameCache = StorageServer.StorageServer(py2_encode('{0}Addonname1').format(addon_name), 24)


def getShowCache():
    return showCache;


def getEpisodeCache():
    return episodeCache;


def getEpisodeCacheManual():
    return episodeCache_manual;


def getTvdbDataCache():
    return tvdbDataCache;


def getAddonnameCache():
    return addonnameCache;