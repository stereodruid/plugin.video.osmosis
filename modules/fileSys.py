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

addon = xbmcaddon.Addon()
ADDON_PATH = addon.getAddonInfo('path')
profile = xbmc.translatePath(addon.getAddonInfo('profile').decode('utf-8'))
STRM_LOC = xbmc.translatePath(addon.getSetting('STRM_LOC'))
MEDIALIST_PATH = addon.getSetting('MediaList_LOC')
MediaList_LOC = xbmc.translatePath(os.path.join(MEDIALIST_PATH, 'MediaList.xml'))
addonList = {}


def writeSTRM(path, file, url):
    utils.addon_log('writeSTRM')
    return makeSTRM(path, file, url)


def makeSTRM(filepath, filename, url):
    utils.addon_log('makeSTRM')

    mtime = None
    try:
        filename = stringUtils.cleanStrmFilesys(filename.decode("utf-8"))
        filepath = stringUtils.multiRstrip(filepath.decode("utf-8"))
        filepath = completePath(os.path.join(STRM_LOC, filepath))

        if not xbmcvfs.exists(filepath):
            dirs = filepath.replace(STRM_LOC, '').split("\\") if filepath.find("\\") != -1 else filepath.replace(STRM_LOC, '').split("/")
            dirs = filter(None, dirs)

            filepath = STRM_LOC
            for dir in dirs:
                filepath = completePath(os.path.join(filepath, dir))
                if not xbmcvfs.exists(filepath):
                    xbmcvfs.mkdir(filepath)

        if not STRM_LOC.startswith("smb:") and not STRM_LOC.startswith('nfs:'):
            fullpath = '%s.strm' % (os.path.normpath(xbmc.translatePath(os.path.join(filepath, filename))))
        else:
            fullpath = '%s/%s.strm' % (filepath, filename)
#         if xbmcvfs.exists(fullpath):
#             if addon.getSetting('Clear_Strms') == 'true':
#                 x = 0 #xbmcvfs.delete(fullpath)
#             else:
#                 return fullpath

        if True:
            if fullpath.find('Audio') > 0:
                try:
                    if xbmcvfs.exists(fullpath.decode("utf-8")):
                        return fullpath, None
                except:
                    if xbmcvfs.exists(fullpath.encode("utf-8")):
                        return fullpath, None

            try:
                fullpath = fullpath.decode("utf-8")
                fle = xbmcvfs.File(fullpath, 'w')
            except:
                fullpath = fullpath.encode("utf-8")
                fle = xbmcvfs.File(fullpath, 'w')
                pass

            fle.write(bytearray(url, encoding="utf-8"))
            fle.close()
            del fle

            if fullpath.find('Audio') > 0:
                mtime = os.path.getmtime(fullpath)

    except IOError as (errno, strerror):
        print ("I/O error({0}): {1}").format(errno, strerror)
    except ValueError:
        print ("No valid integer in line.")
    except:
        guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1]) + (". See your Kodi.log!"))
        utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
        print ("Unexpected error:"), sys.exc_info()[1]
        pass

    return fullpath, mtime


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
    thefile = xbmc.translatePath(os.path.join(MEDIALIST_PATH, 'MediaList.xml'))

    if not xbmcvfs.exists(profile):
        xbmcvfs.mkdirs(profile)
    if not xbmcvfs.exists(thefile):
        xbmcvfs.File(thefile, 'a').close()

    fle = xbmcvfs.File(thefile, 'r')
    thelist = fle.read().split('\n')
    fle.close()
    del fle

    if len(thelist) > 0:
        for i in thelist:
            splits = i.strip().split('|')
            if stringUtils.getStrmname(splits[1]) == stringUtils.getStrmname(mediaTitle):
                splitPlugin = re.search('plugin:\/\/([^\/\?]*)', splits[2])
                mediaPlugin = re.search('plugin:\/\/([^\/\?]*)', url)
                if mediaPlugin and splitPlugin and mediaPlugin.group(1) == splitPlugin.group(1):
                    existInList = True

    if existInList:
        return True
    else:
        return False


def writeMediaList(url, name, cType='Other', cleanName=True, albumartist=None):
    utils.addon_log('writeMediaList')
    existInList = False
    thefile = xbmc.translatePath(os.path.join(MEDIALIST_PATH, 'MediaList.xml'))

    if not xbmcvfs.exists(profile):
        xbmcvfs.mkdirs(profile)
    if not xbmcvfs.exists(thefile):
        xbmcvfs.File(thefile, 'w').close()

    fle = xbmcvfs.File(thefile, 'r')
    thelist = fle.read().split('\n')
    fle.close()
    del fle

    thelist = [x for x in thelist if x != '']
    if len(thelist) > 0 :
        for i in thelist:
            splits = i.strip().split('|')
            if stringUtils.getStrmname(splits[1]).lower() == stringUtils.getStrmname(name).lower():
                existInList = True
                if splits[2].find(url) == -1:
                    splits[2] = '%s<next>%s' % (splits[2], url)
                    if albumartist:
                        splits[4] = albumartist.decode('utf-8')

                    newentry = '%s\n' % ('|'.join(splits))
                    xbmcgui.Dialog().notification(str(i), "Adding to MediaList", os.path.join(ADDON_PATH, 'resources/representerIcon.png'), 5000)
                    thelist = stringUtils.replaceStringElem(thelist, i, newentry)

    if existInList != True:
        newentry = [cType, name.decode("utf-8"), url]
        if albumartist:
            newentry.append(albumartist.decode('utf-8'))

        newentry = '%s\n' % ('|'.join(newentry))
        thelist.append(newentry)

    output_file = xbmcvfs.File(thefile.decode("utf-8"), 'w')
    for linje in thelist:
        if not linje.startswith('\n'):
            output_file.write(linje.strip().encode('utf-8') + '\n')
        else:
            output_file.write(linje.strip())


def writeTutList(step):
    utils.addon_log('writeTutList')
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


def removeMediaList(delList):
    utils.addon_log('Removing items')
    thefile = completePath(os.path.join(MEDIALIST_PATH))
    thefile = xbmc.translatePath(os.path.join(thefile, 'MediaList.xml'))

    if xbmcvfs.exists(thefile):
        delNotInMediaList(delList)

        fle = xbmcvfs.File(thefile, 'r')
        thelist = fle.read().splitlines()
        fle.close()
        del fle

        thelist = [entry for entry in thelist if entry not in delList]

        fle = xbmcvfs.File(thefile, "w")
        fle.write('\n'.join(thelist).strip())
        fle.close()
        del fle


def readMediaList(purge=False):
    if xbmcvfs.exists(MediaList_LOC):
        fle = xbmcvfs.File(MediaList_LOC, 'r')
        thelist = fle.read().splitlines()
        fle.close()
        return thelist


def delNotInMediaList(delList):
    for entry in delList:
        try:
            splits = entry.split('|')
            type = splits[0]
            isAudio = True if type.lower().find('audio') > -1 else False
            path = completePath(STRM_LOC) + type

            if isAudio and len(splits) > 3:
                path = completePath(path) + stringUtils.cleanByDictReplacements(splits[3])

            itemPath = stringUtils.getStrmname(splits[1])
            path = completePath(completePath(path) + stringUtils.cleanStrmFilesys(itemPath))
            utils.addon_log("remove: %s" % path)
            xbmcvfs.rmdir(path, force=True)
            if isAudio:
                xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioLibrary.Clean", "id": 1}')
        except OSError:
                print ("Unable to remove: %s" % path)


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
