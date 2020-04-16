# -*- coding: utf-8 -*-
'''
    Provides: Globals, Settings, sleep, jsonRPC
'''
from __future__ import unicode_literals
from datetime import date
from kodi_six.utils import py2_decode, py2_encode
from os.path import join as OSPJoin
from re import search
from sys import argv
from time import mktime, strptime
from json import dumps, loads
import xbmc
import xbmcaddon
import xbmcgui

from .singleton import Singleton


class Globals(Singleton):

    _globals = dict()


    def __getattr__(self, name): return self._globals[name]


    def __init__(self):
        try:
            from urllib.parse import urlparse
        except ImportError:
            from urlparse import urlparse

        # argv[0] can contain the entire path, so we limit ourselves to the base url
        pid = urlparse(argv[0])
        self.pluginid = '{}://{}/'.format(pid.scheme, pid.netloc)
        self.pluginhandle = int(argv[1]) if (1 < len(argv)) and self.pluginid else -1

        self._globals['monitor'] = xbmc.Monitor()
        self._globals['addon'] = xbmcaddon.Addon()
        self._globals['dialog'] = xbmcgui.Dialog()
        self._globals['dialogProgressBG'] = xbmcgui.DialogProgressBG()

        self._globals['DATA_PATH'] = py2_decode(xbmc.translatePath(self.addon.getAddonInfo('profile')))
        self._globals['CONFIG_PATH'] = OSPJoin(self.DATA_PATH, 'config')
        self._globals['HOME_PATH'] = py2_decode(xbmc.translatePath('special://home'))
        self._globals['PLUGIN_ID'] = py2_decode(self.addon.getAddonInfo('id'))
        self._globals['PLUGIN_PATH'] = py2_decode(self.addon.getAddonInfo('path'))
        self._globals['PLUGIN_NAME'] = self.addon.getAddonInfo('name')
        self._globals['PLUGIN_VERSION'] = self.addon.getAddonInfo('version')

        self._globals['MEDIA_FANART'] = OSPJoin(self.PLUGIN_PATH, 'resources/media/fanart.png')
        self._globals['MEDIA_FOLDER'] = OSPJoin(self.PLUGIN_PATH, 'resources/media/folderIcon.png')
        self._globals['MEDIA_ICON'] = OSPJoin(self.PLUGIN_PATH, 'resources/media/icon.png')
        self._globals['MEDIA_REMOVE'] = OSPJoin(self.PLUGIN_PATH, 'resources/media/iconRemove.png')
        self._globals['MEDIA_UPDATE'] = OSPJoin(self.PLUGIN_PATH, 'resources/media/updateIcon.png')

        self._globals['DATABASES'] = [
            {'dbtype': 'movies', 'db': {'sqliteDB': None, 'mysqlDBType': 'Movies'}},
            {'dbtype': 'tvshows', 'db': {'sqliteDB': None, 'mysqlDBType': 'TVShows'}},
            {'dbtype': 'music', 'db': {'sqliteDB': None, 'mysqlDBType': 'Music'}}
        ]
        self._globals['DATABASE_SQLLITE_OSMOSIS_SCHEMA_VERSION_FILES_PATH'] = OSPJoin(self.PLUGIN_PATH, 'resources/db/migrate')

        bv = xbmc.getInfoLabel('System.BuildVersion')
        self._globals['KODI_VERSION'] = int(bv.split('.')[0])
        cdate = search('Git:(\d+)', bv)
        cdate = date.fromtimestamp(mktime(strptime(cdate.group(1), '%Y%m%d'))) if cdate else None
        self._globals['KODI_COMPILE_DATE'] = cdate
        self._globals['FEATURE_PLUGIN_RESUME_SYNC'] = self.KODI_VERSION >= 18 and self.KODI_COMPILE_DATE and self.KODI_COMPILE_DATE >= date(2020, 1, 28)

        try:
            import StorageServer
        except:
            import storageserverdummy as StorageServer

        self._globals['CACHE_TVSHOWS'] = StorageServer.StorageServer(py2_encode('{0}TVShowsTVDB1').format(self.PLUGIN_NAME), 24 * 30)
        self._globals['CACHE_EPISODES'] = StorageServer.StorageServer(py2_encode('{0}EpisodesTVDB1').format(self.PLUGIN_NAME), 24 * 30)
        self._globals['CACHE_EPISODES_MANUAL'] = StorageServer.StorageServer(py2_encode('{0}EpisodesManual1').format(self.PLUGIN_NAME), 24 * 365)
        self._globals['CACHE_TVDB_DATA'] = tvdbDataCache = StorageServer.StorageServer(py2_encode('{0}TVDBData1').format(self.PLUGIN_NAME), 1)
        self._globals['CACHE_ADDONNAME'] = StorageServer.StorageServer(py2_encode('{0}Addonname1').format(self.PLUGIN_NAME), 24)


    def __del__(self):
        del self.monitor, self.addon, self.dialog, self.dialogProgress, self.dialogProgressBG


class Settings(Singleton):


    def __init__(self):
        self._g = Globals()
        self._gs = self._g.addon.getSetting


    def __getattr__(self, name):
        if 'CLEAR_STRMS' == name: return self._gs('Clear_Strms') == 'true'
        elif 'CONFIRM_USER_ENTRIES' == name: return self._gs('confirm_user_entries') == 'true'

        elif 'DATABASE_MYSQL_KODI_MUSIC_DATABASENAME' == name: return self._gs('KMusic-DB name')
        elif 'DATABASE_MYSQL_KODI_MUSIC_IP' == name: return self._gs('KMusic-DB IP')
        elif 'DATABASE_MYSQL_KODI_MUSIC_PASSWORD' == name: return self._gs('KMusic-DB password')
        elif 'DATABASE_MYSQL_KODI_MUSIC_PORT' == name: return self._gs('KMusic-DB port')
        elif 'DATABASE_MYSQL_KODI_MUSIC_USERNAME' == name: return self._gs('KMusic-DB username')

        elif 'DATABASE_MYSQL_KODI_VIDEO_DATABASENAME' == name: return self._gs('KMovie-DB name')
        elif 'DATABASE_MYSQL_KODI_VIDEO_IP' == name: return self._gs('KMovie-DB IP')
        elif 'DATABASE_MYSQL_KODI_VIDEO_PASSWORD' == name: return self._gs('KMovie-DB password')
        elif 'DATABASE_MYSQL_KODI_VIDEO_PORT' == name: return self._gs('KMovie-DB port')
        elif 'DATABASE_MYSQL_KODI_VIDEO_USERNAME' == name: return self._gs('KMovie-DB username')

        elif 'DATABASE_MYSQL_OSMOSIS_MOVIE_DATABASENAME' == name: return self._gs('Movies-DB name')
        elif 'DATABASE_MYSQL_OSMOSIS_MOVIE_IP' == name: return self._gs('Movies-DB IP')
        elif 'DATABASE_MYSQL_OSMOSIS_MOVIE_PASSWORD' == name: return self._gs('Movies-DB password')
        elif 'DATABASE_MYSQL_OSMOSIS_MOVIE_PORT' == name: return self._gs('Movies-DB port')
        elif 'DATABASE_MYSQL_OSMOSIS_MOVIE_USERNAME' == name: return self._gs('Movies-DB username')

        elif 'DATABASE_MYSQL_OSMOSIS_MUSIC_DATABASENAME' == name: return self._gs('Music-DB name')
        elif 'DATABASE_MYSQL_OSMOSIS_MUSIC_IP' == name: return self._gs('Music-DB IP')
        elif 'DATABASE_MYSQL_OSMOSIS_MUSIC_PASSWORD' == name: return self._gs('Music-DB password')
        elif 'DATABASE_MYSQL_OSMOSIS_MUSIC_PORT' == name: return self._gs('Music-DB port')
        elif 'DATABASE_MYSQL_OSMOSIS_MUSIC_USERNAME' == name: return self._gs('Music-DB username')

        elif 'DATABASE_MYSQL_OSMOSIS_TVSHOW_DATABASENAME' == name: return self._gs('TV-Show-DB name')
        elif 'DATABASE_MYSQL_OSMOSIS_TVSHOW_IP' == name: return self._gs('TV-Show-DB IP')
        elif 'DATABASE_MYSQL_OSMOSIS_TVSHOW_PASSWORD' == name: return self._gs('TV-Show-DB password')
        elif 'DATABASE_MYSQL_OSMOSIS_TVSHOW_PORT' == name: return self._gs('TV-Show-DB port')
        elif 'DATABASE_MYSQL_OSMOSIS_TVSHOW_USERNAME' == name: return self._gs('TV-Show-DB username')

        elif 'DATABASE_SQLLITE_KODI_MUSIC_FILENAME_AND_PATH' == name: return py2_decode(xbmc.translatePath(self._gs('KMusic-DB path')))
        elif 'DATABASE_SQLLITE_KODI_VIDEO_FILENAME_AND_PATH' == name: return py2_decode(xbmc.translatePath(self._gs('KMovie-DB path')))
        elif 'DATABASE_SQLLITE_OSMOSIS_MOVIE_FILENAME_AND_PATH' == name: return py2_decode(OSPJoin(self._g.DATA_PATH, 'Movies.db'))
        elif 'DATABASE_SQLLITE_OSMOSIS_MUSIC_FILENAME_AND_PATH' == name: return py2_decode(OSPJoin(self._g.DATA_PATH, 'Musik.db'))
        elif 'DATABASE_SQLLITE_OSMOSIS_TVSHOW_FILENAME_AND_PATH' == name: return py2_decode(OSPJoin(self._g.DATA_PATH, 'Shows.db'))
        elif 'DATABASE_SQLLITE_OSMOSIS_SCHEMA_VERSION_FILENAME_AND_PATH' == name: return py2_decode(OSPJoin(self._g.DATA_PATH, 'SchemaVersion.db'))

        elif 'FIND_SQLLITE_DB' == name: return self._gs('Find_SQLite_DB') == 'true'
        elif 'KEEP_MOVIE_YEAR' == name: return self._gs('keep_movie_year') == 'true'
        elif 'FOLDER_MEDIALISTENTRY_MOVIE' == name: return self._gs('folder_medialistentry_movie') == 'true'
        elif 'FOLDER_MOVIE' == name: return self._gs('folder_movie') == 'true'
        elif 'HIDE_TITLE_IN_OV' == name: return self._gs('Hide_title_in_OV') == 'true'
        elif 'INFOLABELS_ADD_ADDON_STRING' == name: return self._gs('infolabels_add_addon_string')
        elif 'LINK_TYPE' == name: return int(self._gs('Link_Type'))
        elif 'MEDIALIST_PATH' == name: return py2_decode(xbmc.translatePath(self._gs('MediaList_LOC')))
        elif 'MEDIALIST_FILENNAME_AND_PATH' == name: return py2_decode(OSPJoin(self.MEDIALIST_PATH, 'MediaList.xml'))
        elif 'MYVIDEOS_SELECTACTION' == name: return jsonrpc('Settings.GetSettingValue', dict(setting='myvideos.selectaction')).get('value')
        elif 'NO_E0_STRMS_EXPORT' == name: return self._gs('noE0_Strms_Export') == 'true'
        elif 'PAGING_MOVIES' == name: return int(self._gs('paging_movies'))
        elif 'PAGING_TVSHOWS' == name: return int(self._gs('paging_tvshows'))
        elif 'PLAYBACK_DIALOG' == name: return int(self._gs('playback_dialog'))
        elif 'PLAYBACK_IGNORE_ADDON_STRING' == name: return self._gs('playback_ignore_addon_string')
        elif 'PLAYBACK_REWIND' == name: return int(self._gs('playback_rewind'))
        elif 'SCHEDULED_UPDATE' == name: return int(self._gs('scheduled_update'))
        elif 'SCHEDULED_UPDATE_INTERVAL' == name: return int(self._gs('scheduled_update_interval'))
        elif 'SCHEDULED_UPDATE_INTERVAL_FILENNAME_AND_PATH' == name: return py2_decode(OSPJoin(self.MEDIALIST_PATH, 'scheduled_update_interval.txt'))
        elif 'SCHEDULED_UPDATE_TIME' == name: return strptime(self._gs('scheduled_update_time'), '%H:%M')
        elif 'SEARCH_THETVDB' == name: return int(self._gs('search_thetvdb'))
        elif 'STRM_LOC' == name: return py2_decode(xbmc.translatePath(self._gs('STRM_LOC')))
        elif 'TVDB_DIALOG_AUTOCLOSE_TIME' == name: return int(self._gs('tvdb_dialog_autoclose_time'))
        elif 'TVDB_TOKEN_FILENNAME_AND_PATH' == name: return py2_decode(OSPJoin(self.MEDIALIST_PATH, 'tvdb_token.txt'))
        elif 'UPDATE_AT_STARTUP' == name: return self._gs('Update_at_startup') == 'true'
        elif 'USE_MYSQL' == name: return self._gs('USE_MYSQL') == 'true'


def jsonrpc(action, arguments=None):
    from .utils import addon_log
    ''' put some JSON together for the JSON-RPC APIv6 '''
    if arguments is None:
        arguments = {}

    if arguments:
        request = dumps(dict(id=1, jsonrpc='2.0', method=action, params=arguments))
    else:
        request = dumps(dict(id=1, jsonrpc='2.0', method=action))

    addon_log('Sending request to Kodi: {0}'.format(request))
    return parse_jsonrpc(xbmc.executeJSONRPC(request), addon_log)


def parse_jsonrpc(json_raw, addon_log):
    if not json_raw:
        addon_log('Empty response from Kodi')
        return {}

    addon_log('Response from Kodi: {0}'.format(py2_decode(json_raw)))
    parsed = loads(json_raw)
    if parsed.get('error', False):
        addon_log('Kodi returned an error: {0}'.format(parsed.get('error')))
    return parsed.get('result', {})


def sleep(sec):
    if Globals().monitor.waitForAbort(sec):
        exit()


def exit():
    try:
        from .utils import addon_log
        addon_log('Abort requested - exiting addon')
    except:
        xbmc.log('[plugin.video.osmosis] Abort requested - exiting addon')
    import sys

    sys.exit()
