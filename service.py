# Copyright (C) 2016 stereodruid(J.G.) Mail: stereodruid@gmail.com
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
import os
import re
import time
import xbmc
import xbmcvfs

from resources.lib.common import Globals, Settings

globals = Globals()
settings = Settings()
startup_time = None


def setDBs(files, path):
    dbtypes = ['video', 'music']

    for dbtype in dbtypes:
        dbname = None
        for file in files:
            if file.lower().startswith('my{0}'.format(dbtype)):
                if dbname is None:
                    dbname = file
                elif re.search('(\d+)', dbname) and re.search('(\d+)', file):
                    dbnumber = int(re.search('(\d+)', dbname).group(1))
                    filedbnumber = int(re.search('(\d+)', file).group(1))
                    if filedbnumber > dbnumber:
                        dbname = file

        if dbname is not None:
            dbpath = py2_decode(os.path.join(path, dbname))
            dbsetting = settings.DATABASE_SQLLITE_KODI_VIDEO_FILENAME_AND_PATH if dbtype == 'video' else settings.DATABASE_SQLLITE_KODI_MUSIC_FILENAME_AND_PATH
            if dbpath != dbsetting:
                globals.addon.setSetting('KMovie-DB path', dbpath) if dbtype == 'video' else globals.addon.setSetting('KMusic-DB path', dbpath)


if __name__ == '__main__':
    if not settings.USE_MYSQL and settings.FIND_SQLLITE_DB:
        path = py2_decode(os.path.join(globals.HOME_PATH, 'userdata/Database/'))
        if xbmcvfs.exists(path):
            dirs, files = xbmcvfs.listdir(path)
            setDBs(files, path)

    if settings.UPDATE_AT_STARTUP:
        xbmc.executebuiltin('XBMC.RunPlugin(plugin://{0}/?url=&mode=666)'.format(globals.PLUGIN_ID))

    monitor = globals.monitor
    while not monitor.abortRequested():
        # Sleep/wait for abort for 10 seconds
        if monitor.waitForAbort(10):
            # Abort was requested while waiting. We should exit
            break

        if settings.AUTOMATIC_UPDATE_RUN:
            if startup_time is None:
                startup_time = time.time()

            next_peridoc_update = startup_time + (settings.AUTOMATIC_UPDATE_TIME * 60 * 60)
            if (next_peridoc_update <= time.time()):
                startup_time = time.time()
                xbmc.executebuiltin('XBMC.RunPlugin(plugin://{0}/?url=&mode=666&updateActor=1)'.format(globals.PLUGIN_ID))
                monitor.waitForAbort(60)
        else:
            if startup_time is not None:
                startup_time = None

            Timed_Update_Run = settings.UPDATE_TIME[:5] if settings.UPDATE_TIME != '' else settings.UPDATE_TIME('update_time')
            if Timed_Update_Run != '' and Timed_Update_Run != '00:00':
                if time.strftime('%H:%M') == Timed_Update_Run:
                    xbmc.executebuiltin('XBMC.RunPlugin(plugin://{0}/?url=&mode=666&updateActor=2)'.format(globals.PLUGIN_ID))
                    monitor.waitForAbort(60)