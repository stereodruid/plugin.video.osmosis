# Copyright (C) 2016 stereodruid(J.G.)
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

import fileinput
import os
import sys
import re
import shutil

from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP
import SimpleDownloader as downloader
import pyxbmct
import utils
import codecs
from modules import stringUtils
from modules import guiTools
import errno
import xbmc
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs


try:
    import json
except:
    import simplejson as json


addon_id = 'plugin.video.osmosis'
addon = xbmcaddon.Addon(addon_id)
addon_version = addon.getAddonInfo('version')
ADDON_NAME = addon.getAddonInfo('name')
REAL_SETTINGS = xbmcaddon.Addon(id=addon_id)
ADDON_SETTINGS = REAL_SETTINGS.getAddonInfo('profile')
ADDON_PATH = REAL_SETTINGS.getAddonInfo('path')
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

STRM_LOC = xbmc.translatePath(addon.getSetting('STRM_LOC'))
addonList = {}

def writeSTRM(path, file, url):
    #ToDo: OriginalPlugin option
#     if addon.getSetting('Link_Type') == '0':
#         if url.find("plugin://plugin.video.osmosis/?url=plugin") == -1:
#             url = url.strip().replace("?url=plugin", "plugin://plugin.video.osmosis/?url=plugin", 1)
    utils.addon_log('writeSTRM')
    makeSTRM(path, file, url)
    
def makeSTRM(filepath, filename, url):
    utils.addon_log('makeSTRM')
    
    isSMB = False
    try:
        filepath = stringUtils.multiRstrip(filepath.decode("utf-8"))
        filename = filename.decode("utf-8")
        filepath = completePath(os.path.join(STRM_LOC, filepath))

        if not xbmcvfs.exists(filepath):         
            dirs = filepath.replace(STRM_LOC,'').split("\\") if filepath.find("\\") != -1 else filepath.replace(STRM_LOC,'').split("/")
            dirs = filter(None, dirs)

            filepath = STRM_LOC
            for dir in dirs:
                filepath = completePath(os.path.join(filepath, dir))
                if not xbmcvfs.exists(filepath):
                    xbmcvfs.mkdir(filepath)
        
        if not STRM_LOC.startswith("smb:"):  
            fullpath = os.path.normpath(xbmc.translatePath(os.path.join(filepath,  filename))) +'.strm'
        else:
            isSMB = True 
            fullpath = filepath + "/" + filename + ".strm"

#         if xbmcvfs.exists(fullpath):
#             if addon.getSetting('Clear_Strms') == 'true':
#                 x = 0 #xbmcvfs.delete(fullpath)
#             else:
#                 return fullpath
        if True:
            if isSMB:
                try:
                    fle = xbmcvfs.File(fullpath.decode("utf-8"), 'w')
                except:
                    fle = xbmcvfs.File(fullpath.encode("utf-8"), 'w')
                    pass
        
                fle.write("%s" % str(url))
                fle.close()
                del fle
            else:
                try:
                    fle = open(fullpath.decode("utf-8"), "w")
                except:
                    fle = open(fullpath.encode("utf-8"), "w")
                    pass
        
                fle.write("%s" % url)
                fle.close()
                del fle
                  
    except IOError as (errno, strerror):
        print ("I/O error({0}): {1}").format(errno, strerror)
    except ValueError:
        print ("No valid integer in line.")
    except:
        guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
        utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
        print ("Unexpected error:"), sys.exc_info()[1]
        pass
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
def isInMediaList(mediaTitle, url, cType='Other'):
    utils.addon_log('isInMediaList')
    existInList = False
    thelist = []
    thefile = xbmc.translatePath(os.path.join(profile, 'MediaList.xml'))
    
    if not xbmcvfs.exists(profile): 
        xbmcvfs.mkdirs(profile)
    if not xbmcvfs.exists(thefile):
        open(thefile, 'a').close()
    
    fle = codecs.open(thefile, "r", 'UTF-8')
    thelist = fle.readlines()
    fle.close()
    del fle
    
    if len(thelist) > 0:
        for i in thelist:
            splits = i.strip().split('|')
            if splits[1] == mediaTitle:
                splitPlugin = re.search('%s([^\/\?]*)' % ("plugin:\/\/"), splits[2])
                mediaPlugin = re.search('%s([^\/\?]*)' % ("plugin:\/\/"), url)
                if mediaPlugin and splitPlugin and mediaPlugin.group(1) == splitPlugin.group(1):
                    existInList = True

    if existInList:
        return True
    else:
        return False
    
def isInMovieList(mdediaTitle, cType='Other'):
    utils.addon_log('isInMediaList')
    existInList = False
    thelist = []
    thefile = xbmc.translatePath(os.path.join(profile, 'MediaList.xml'))
    
    if not xbmcvfs.exists(profile): 
        xbmcvfs.mkdirs(profile)
    if not xbmcvfs.exists(thefile):
        open(thefile, 'a').close()
    
    fle = codecs.open(thefile, "r", 'UTF-8')
    thelist = fle.readlines()
    fle.close()
    del fle
    
    if len(thelist) > 0:
        for i in thelist:
            if i.split('|',2)[1] == mdediaTitle:
                existInList = True     
    if existInList:
        return True
    else:
        return False
               
def writeMediaList(url, name, cType='Other', cleanName=True):
    utils.addon_log('writeMediaList')
    existInList = False
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
    
    if len(thelist) > 0:
        for i in thelist:
            splits = i.strip().split('|')
            if stringUtils.getStrmname(splits[1]) == stringUtils.getStrmname(name):
                splitPlugin = re.search('%s([^\/\?]*)' % ("plugin:\/\/"), splits[2])
                mediaPlugin = re.search('%s([^\/\?]*)' % ("plugin:\/\/"), url)
                if mediaPlugin and splitPlugin and mediaPlugin.group(1) == splitPlugin.group(1):
                    xbmcgui.Dialog().notification(str(i), "Adding to MediaList",  os.path.join(ADDON_PATH, 'representerIcon.png'), 5000)
                    thelist = stringUtils.replaceStringElem(thelist, i, theentry)
                    existInList = True     
    if existInList != True:
        thelist.append(theentry)
        
    with open(thefile.decode("utf-8"), 'w') as output_file: 
        for linje in thelist:
            if not linje.startswith('\n'):
                output_file.write(linje.strip().encode('utf-8') + '\n')
            else:
                output_file.write(linje.strip())
def writeTutList(step):
    utils.addon_log('writeMediaList')
    existInList = False
    thelist = []
    thefile = xbmc.translatePath(os.path.join(profile, 'firstTimeTut.xml'))
    theentry = '|'.join([step]) + '\n'  
    
    if not xbmcvfs.exists(profile): 
        xbmcvfs.mkdirs(profile)
    if not xbmcvfs.exists(thefile):
        open(thefile, 'a').close()
    
    fle = codecs.open(thefile, "r", 'UTF-8')
    thelist = fle.readlines()
    fle.close()
    del fle
    
    if len(thelist) > 0:
        for i in thelist:          
            if i.find(step) != -1:
                existInList = True     
    if existInList != True:
        thelist.append(step)

        with open(thefile.decode("utf-8"), 'w') as output_file: 
            for linje in thelist:
                if not linje.startswith('\n'):
                    output_file.write(linje.strip().encode('utf-8') + '\n')
                else:
                    output_file.write(linje.strip())
            return False
    else:
        return True
                
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

def removeMediaList(Item_remove):
    utils.addon_log('Removing items')
    thelist = []
    thefile = xbmc.translatePath(os.path.join(profile, 'MediaList.xml'))
      
    if xbmcvfs.exists(thefile):
        fle = open(thefile, "r")
        thelist = fle.readlines()
        fle.close()
        del fle
        delNotInMediaList(Item_remove, thelist)
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

def delNotInMediaList(delList, thelist):
    for i in delList:
        try:
            path = completePath(STRM_LOC) + (thelist[i]).strip().split('|')[0].format(i)
            itemPath = (thelist[i].decode('utf-8')).strip().split('|')[1].replace('++RenamedTitle++', '').format(i).format(i)
            print ("remove folder: %s" % itemPath)
            shutil.rmtree(completePath(path) + stringUtils.cleanByDictReplacements(itemPath) , ignore_errors=True)
        except OSError:
                print ("Unable to remove folder: %s" % itemPath)

def completePath(filepath):
    if filepath.find("\\") != -1 and not filepath.endswith("\\"):
        filepath += "\\"
    elif filepath.find("/") != -1 and not filepath.endswith("/"):
        filepath += "/"

    return xbmc.translatePath(filepath) 

def getAddonname(addonid):
    if addonid not in addonList:
        r = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "' + addonid + '", "properties": ["name"]}}')
        data = json.loads(r)
        if not "error" in data.keys():
            addonList[addonid] = data["result"]["addon"]["name"]
            return addonList[addonid]
        else:
            return addonid
    else:
        return addonList[addonid]