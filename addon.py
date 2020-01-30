# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import xbmc
import xbmcaddon

from resources.lib.common import Globals

if __name__ == '__main__':
    xbmc.executebuiltin('XBMC.RunPlugin(plugin://{0}/?url=&mode=4)'.format(Globals().PLUGIN_ID))