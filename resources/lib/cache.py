# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from kodi_six.utils import py2_encode

from .common import Globals

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

globals = Globals()

showCache = StorageServer.StorageServer(py2_encode('{0}TVShowsTVDB1').format(globals.PLUGIN_NAME), 24 * 30)
episodeCache = StorageServer.StorageServer(py2_encode('{0}EpisodesTVDB1').format(globals.PLUGIN_NAME), 24 * 30)
episodeCache_manual = StorageServer.StorageServer(py2_encode('{0}EpisodesManual1').format(globals.PLUGIN_NAME), 24 * 365)
tvdbDataCache = StorageServer.StorageServer(py2_encode('{0}TVDBData1').format(globals.PLUGIN_NAME), 1)
addonnameCache = StorageServer.StorageServer(py2_encode('{0}Addonname1').format(globals.PLUGIN_NAME), 24)


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