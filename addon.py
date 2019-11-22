# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import xbmc, xbmcaddon

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')

if __name__ == '__main__':
    xbmc.executebuiltin('XBMC.RunPlugin(plugin://{0}/?url=&mode=4)'.format(addon_id))
