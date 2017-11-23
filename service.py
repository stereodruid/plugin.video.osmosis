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
import os
import time
from modules import updateAll
from modules import guiTools
import utils
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
import re

# Debug option pydevd:
if False:
    import pydevd
    pydevd.settrace(stdoutToServer=True, stderrToServer=True)

global thelist
thelist = None

# Plugin Info
ADDON_ID = 'plugin.video.osmosis'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_ID = REAL_SETTINGS.getAddonInfo('id')
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name').decode('utf-8')
ADDON_PATH = REAL_SETTINGS.getAddonInfo('path')
ADDON_SETTINGS = REAL_SETTINGS.getAddonInfo('profile')
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
# PC Settings Info
MediaList_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'MediaList.xml'))
STRM_LOC = REAL_SETTINGS.getSetting('STRM_LOC')
Path_Type = REAL_SETTINGS.getSetting('Path_Type')
Clear_Strms = REAL_SETTINGS.getSetting('Clear_Strms') == 'true'
Automatic_Update_Time = REAL_SETTINGS.getSetting('Automatic_Update_Time') 
Update_at_startup = REAL_SETTINGS.getSetting('Update_at_startup')
Automatic_Update_Delay = REAL_SETTINGS.getSetting('Automatic_Update_Delay')
Automatic_Update_Run = REAL_SETTINGS.getSetting('Automatic_Update_Run')
USE_MYSQL = REAL_SETTINGS.getSetting('USE_MYSQL')
Find_SQLite_DB = REAL_SETTINGS.getSetting('Find_SQLite_DB')
represent = os.path.join(ADDON_PATH, 'icon.png')
toseconds = 0.0
itime = 5000000000  # in miliseconds 

def setDBs(files, path):
    dbtypes = ['video', 'music']

    for dbtype in dbtypes:
        dbname = None
        for file in files:
            if file.lower().startswith('my' + dbtype):
                if dbname is None:
                    dbname = file
                elif re.search('(\d+)', dbname) and re.search('(\d+)', file):
                    dbnumber = int(re.search('(\d+)', dbname).group(1))
                    filedbnumber = int(re.search('(\d+)', file).group(1))
                    if filedbnumber > dbnumber:
                        dbname = file

        if dbname is not None:
            dbpath = xbmc.translatePath(os.path.join(path, dbname))
            dbsetting = REAL_SETTINGS.getSetting('KMovie-DB path') if dbtype == 'video' else REAL_SETTINGS.getSetting('KMusic-DB path')
            if dbpath != dbsetting:
                REAL_SETTINGS.setSetting('KMovie-DB path', dbpath) if dbtype == 'video' else REAL_SETTINGS.setSetting('KMusic-DB path', dbpath)

if __name__ == "__main__":
    if USE_MYSQL == 'false' and Find_SQLite_DB == 'true':
        path = xbmc.translatePath(os.path.join("special://home/", 'userdata/Database/'))
        if xbmcvfs.exists(path):
            dirs, files = xbmcvfs.listdir(path)
            setDBs(files, path)
        
    if Update_at_startup == "true":                        
        updateAll.strm_update()
 
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        # Sleep/wait for abort for 10 seconds
        if monitor.waitForAbort(10):
            # Abort was requested while waiting. We should exit
            break  
        Automatic_Update_Run = REAL_SETTINGS.getSetting('Automatic_Update_Run')
        Timed_Update_Run = REAL_SETTINGS.getSetting('update_time')           
        if Automatic_Update_Run == "true":
            Timed_Update_Run = "0:00"
            Automatic_Update_Time = REAL_SETTINGS.getSetting('Automatic_Update_Time')
            Automatic_Update_Run = REAL_SETTINGS.getSetting('Automatic_Update_Run')
            toseconds = toseconds + 10.0
            
            if ((toseconds >= float(Automatic_Update_Time) * 60 * 60)):
                guiFix = updateAll.guIFix(guiFix)
                updateAll.strm_update()
                toseconds = 0.0
                monitor.waitForAbort(60)
        elif (time.strftime("%H:%M") == Timed_Update_Run) and Timed_Update_Run != "0:00":
            guiFix = updateAll.guIFix(guiFix)
            updateAll.strm_update()
            monitor.waitForAbort(60)
