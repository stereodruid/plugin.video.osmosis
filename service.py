# Copyright (C) 2016 stereodruid(J.Gina)
#
#
# This file is part of OSMOSIS
#
# OSMOSIS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OSMOSIS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OSMOSIS.  If not, see <http://www.gnu.org/licenses/>.


# -*- coding: utf-8 -*-
import os, re, sys, time
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
from traceback import print_exc
import unicodedata
#import pydevd
#pydevd.settrace(stdoutToServer=True, stderrToServer=True)
import default
import urllib
import collections
from _ast import While

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
SETTINGS2_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS,'settings2.xml'))
STRM_LOC = REAL_SETTINGS.getSetting('STRM_LOC')
Path_Type = REAL_SETTINGS.getSetting('Path_Type')
Clear_Strms = REAL_SETTINGS.getSetting('Clear_Strms') == 'true'
Automatic_Update_Time = REAL_SETTINGS.getSetting('Automatic_Update_Time') 
Automatic_Update = REAL_SETTINGS.getSetting('Automatic_Update')
Automatic_Update_Delay = REAL_SETTINGS.getSetting('Automatic_Update_Delay')
Automatic_Update_Run = REAL_SETTINGS.getSetting('Automatic_Update_Run')
represent = os.path.join(ADDON_PATH, 'representerIcon.png')
toseconds = 0.0
time = 10000 #in miliseconds  
   
if __name__ == "__main__":
    def readSettings2(purge=False):
        # try:
        if xbmcvfs.exists(SETTINGS2_LOC):
            fle = open(SETTINGS2_LOC, "r")
            thelist = fle.readlines()
            fle.close()
            return thelist
    
    thelist = readSettings2()
    
    def strm_update():
        pDialog = xbmcgui.DialogProgressBG()
        pDialog.create(ADDON_NAME, "Updating")
        #xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(ADDON_NAME, "Starting Update", time, represent))
        try:
            
            j = 100 / len(thelist)
            
            for i in range(len(thelist)):
                    type ,name, url = ((thelist[i]).strip().split('|', 2))
                    #time.sleep(2) # delays for 2 seconds just to make sure Hodor can read the message 
                    pDialog.update(j, ADDON_NAME + " Update: " + name) 
                    try:
                         default.fillPluginItems(url, strm=True, strm_name=name, strm_type=type, showtitle=name)
                    except:#
                        pass
                    
                    j = j + 100 / len(thelist)
            pDialog.update(100, ADDON_NAME + " Update: Done") 
            pDialog.close()
            xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(ADDON_NAME, "Next update in: " + Automatic_Update_Time , time, represent))
        except:
            pass

    if Automatic_Update == "true":      
        strm_update()
        
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        # Sleep/wait for abort for 10 seconds
        if monitor.waitForAbort(10):
            # Abort was requested while waiting. We should exit
            break  
        Automatic_Update_Run = REAL_SETTINGS.getSetting('Automatic_Update_Run')
        if Automatic_Update == "true":
            Automatic_Update_Time = REAL_SETTINGS.getSetting('Automatic_Update_Time') 
            Automatic_Update_Run = REAL_SETTINGS.getSetting('Automatic_Update_Run')
            toseconds = toseconds + 0.020
            if (toseconds >= Automatic_Update_Time):
                strm_update()
                toseconds = 0.0
           
        # Sleep/wait for abort for 10 secondsds