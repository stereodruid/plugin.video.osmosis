# This file is part of OSMOSIS.
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

import fileinput
import os
import shutil

from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP
import SimpleDownloader as downloader
import pyxbmct
import utils
import codecs
from modules import stringUtils
import errno
import xbmc
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs


try:
    import json
except:
    import simplejson as json


addnon_id = 'plugin.video.osmosis'
addon = xbmcaddon.Addon(addnon_id)
addon_version = addon.getAddonInfo('version')
ADDON_NAME = addon.getAddonInfo('name')
REAL_SETTINGS = xbmcaddon.Addon(id=addnon_id)
ADDON_SETTINGS = REAL_SETTINGS.getAddonInfo('profile')
MediaList_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'MediaList.xml'))
STRM_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'STRM_LOC'))
profile = xbmc.translatePath(addon.getAddonInfo('profile').decode('utf-8'))
home = xbmc.translatePath(addon.getAddonInfo('path').decode('utf-8'))
favorites = os.path.join(profile, 'favorites')
history = os.path.join(profile, 'history')
dialog = xbmcgui.Dialog()
icon = os.path.join(home, 'icon.png')
iconRemove = os.path.join(home, 'iconRemove.png')
FANART = os.path.join(home, 'fanart.jpg')
source_file = os.path.join(home, 'source_file')
functions_dir = profile
downloader = downloader.SimpleDownloader()
debug = addon.getSetting('debug')

if os.path.exists(favorites) == True:
    FAV = open(favorites).read()
else: FAV = []
if os.path.exists(favorites) == True:
    FAV = open(favorites).read()
else: FAV = []

DIRS = []
STRM_LOC = xbmc.translatePath(addon.getSetting('STRM_LOC'))

def writeSTRM(path, file, url):
    
    utils.addon_log('writeSTRM')
    #ToDo: OriginalPlugin option
    if addon.getSetting('Link_Type') == '0':
        if url.find("plugin://plugin.video.osmosis/?url=plugin") == -1:
            url = url.strip().replace("?url=plugin", "plugin://plugin.video.osmosis/?url=plugin", 1)
   
    makeSTRM(path, file, url)
    
def makeSTRM(filepath, filename, url):
    filepath = stringUtils.multiRstrip(filepath.decode("utf-8"))
    filename = filename.decode("utf-8")
    
    utils.addon_log('makeSTRM')
    filepath = os.path.join(STRM_LOC, filepath)
    
    if not xbmcvfs.exists(filepath): 
        xbmcvfs.mkdirs(filepath)
    fullpath = xbmc.translatePath(os.path.join(filepath, filename + '.strm'))

    if xbmcvfs.exists(fullpath):
        if addon.getSetting('Clear_Strms') == 'true':
            x = 0 #xbmcvfs.delete(fullpath)
        else:
            return fullpath
    else:
        try:
            fle = open(fullpath.encode("utf-8"), "w")
        except:
            fle = open(fullpath.decode("utf-8"), "w")
            pass
        fle.write("%s" % url)
        fle.close()
        del fle
        return fullpath
    

def updateStream(strm_Fullpath, replace_text):
    utils.addon_log('updateStream')
    for line in fileinput.input(strm_Fullpath, inplace=1):
        if not line == replace_text:
            line = line.replace(line, replace_text)
            utils.addon_log('Updated: ' + strm_Fullpath)
            
    while os.stat(strm_Fullpath).st_size == 0:
        with open(strm_Fullpath, 'w') as newF:
            newF.write(replace_text)
               
def writeMediaList(url, name, cType='Other'):
    utils.addon_log('writeMediaList')
    thelist = []
    thefile = xbmc.translatePath(os.path.join(profile, 'MediaList.xml'))
    theentry = '|'.join([cType, name.decode("utf-8"), url]) + '\n'  
    
    if not xbmcvfs.exists(profile): 
        xbmcvfs.mkdirs(profile)
    if not xbmcvfs.exists(thefile):
        open(thefile, 'a').close()
    
    fle = codecs.open(thefile, "r", 'UTF-8')
    thelist = fle.readlines()
    fle.close()
    del fle
    for i in thelist:
        if i.split('|',2)[1] == name:
            thelist = stringUtils.replaceStringElem(thelist, theentry, theentry)
            existInList = True     
    if existInList != True:
        thelist.append(theentry)
        
    with open(thefile.decode("utf-8"), 'w') as output_file: 
        for linje in thelist:
            if not linje.startswith('\n'):
                output_file.write(linje.strip().encode('utf-8') + '\n')
            else:
                output_file.write(linje.strip())

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    else:
        fle = codecs.open(thefile, "r", 'UTF-8')
        thelist = fle.readlines()
        fle.close()
        del fle     
    if theentry not in thelist:
        thelist.append(theentry)
    else:
        thelist = stringUtils.replaceStringElem(thelist, theentry, theentry)
        
    with open(thefile.decode("utf-8"), 'w') as output_file: 
        for linje in thelist:
            if not linje.startswith('\n'):
                output_file.write(linje.strip().encode('utf-8') + '\n')
            else:
                output_file.write(linje.strip())

def removeMediaList(Item_remove, replacements):
    utils.addon_log('Removing items')
    thelist = []
    thefile = xbmc.translatePath(os.path.join(profile, 'MediaList.xml'))
      
    if xbmcvfs.exists(thefile):
        fle = open(thefile, "r")
        thelist = fle.readlines()
        fle.close()
        del fle
        delNotInMediaList(Item_remove, thelist, replacements)
        thelist = [i for j, i in enumerate(thelist) if j not in Item_remove]
        
        fle = open(thefile, "w")
        fle.write(''.join(thelist).strip())
        fle.close()
        del fle

def readMediaList(purge=False):
        # try:
        if xbmcvfs.exists(MediaList_LOC):
            fle = open(MediaList_LOC, "r")
            thelist = fle.readlines()
            fle.close()
            return thelist
                          
def isMediaList(url, cType='Other'):
    utils.addon_log('isMediaList')
    # parse MediaList for url return bool if found

def delNotInMediaList(delList, thelist, replacements):
    for i in delList:
        try:
            path = STRM_LOC + "\\" + (thelist[i]).strip().split('|')[0].format(i)
            itemPath = (thelist[i].decode('utf-8')).strip().split('|')[1].format(i)
            print ("remove folder: %s" % itemPath)
            shutil.rmtree(path + "\\" + utils.multiple_reSub(itemPath, replacements) , ignore_errors=True)
        except OSError:
                print ("Unable to remove folder: %s" % itemPath)