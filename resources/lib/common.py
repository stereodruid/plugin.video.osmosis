# -*- coding: utf-8 -*-
'''
    Provides: Globals, Settings, sleep, jsonRPC
'''
from __future__ import unicode_literals
from kodi_six.utils import py2_decode
from os.path import join as OSPJoin
from sys import argv
import json
import xbmc
import xbmcaddon
import xbmcgui

from .singleton import Singleton


class Globals(Singleton):
    """ A singleton instance of globals accessible through dot notation """

    _globals = dict()

    KodiK = int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0]) < 18

    """ Allow the usage of dot notation for data inside the _globals dictionary, without explicit function call """


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

        self._globals['DATA_PATH'] = py2_decode(xbmc.translatePath(self.addon.getAddonInfo('profile')))
        self._globals['CONFIG_PATH'] = OSPJoin(self._globals['DATA_PATH'], 'config')
        self._globals['HOME_PATH'] = py2_decode(xbmc.translatePath('special://home'))
        self._globals['PLUGIN_ID'] = py2_decode(self.addon.getAddonInfo('id'))
        self._globals['PLUGIN_PATH'] = py2_decode(self.addon.getAddonInfo('path'))
        self._globals['PLUGIN_NAME'] = self.addon.getAddonInfo('name')
        self._globals['PLUGIN_VERSION'] = self.addon.getAddonInfo('version')


class Settings(Singleton):
    """ A singleton instance of various settings that could be needed to reload during runtime """


    def __init__(self):
        self._g = Globals()
        self._gs = self._g.addon.getSetting


    def __getattr__(self, name):
        return True


def jsonrpc(action, arguments=None):
    from .utils import addon_log
    ''' put some JSON together for the JSON-RPC APIv6 '''
    if arguments is None:
        arguments = {}

    if arguments:
        request = json.dumps(dict(id=1, jsonrpc='2.0', method=action, params=arguments))
    else:
        request = json.dumps(dict(id=1, jsonrpc='2.0', method=action))

    addon_log('Sending request to Kodi: {0}'.format(request))
    return parse_jsonrpc(xbmc.executeJSONRPC(request), addon_log)


def parse_jsonrpc(json_raw, addon_log):
    if not json_raw:
        addon_log('Empty response from Kodi')
        return {}

    addon_log('Response from Kodi: {0}'.format(py2_decode(json_raw)))
    parsed = json.loads(json_raw)
    if parsed.get('error', False):
        addon_log('Kodi returned an error: {0}'.format(parsed.get('error')))
    return parsed.get('result', {})


def sleep(sec):
    from .utils import addon_log
    if Globals().monitor.waitForAbort(sec):
        import sys
        addon_log('Abort requested - exiting addon')
        sys.exit()