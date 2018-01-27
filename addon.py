# -*- coding: utf-8 -*-

import xbmc, xbmcaddon

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')

if __name__ == '__main__':
    xbmc.executebuiltin('XBMC.RunPlugin(plugin://%s/?url=&mode=4)' % (addon_id))
