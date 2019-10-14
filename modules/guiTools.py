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

from . import stringUtils
from . import fileSys
import os, sys
import time
import urllib
import re
import utils
import jsonUtils
import xmldialogs
import xbmc
import xbmcplugin, xbmcgui, xbmcaddon

try:
    import json
except:
    import simplejson as json

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
ADDON_NAME = addon.getAddonInfo('name')
home = xbmc.translatePath(addon.getAddonInfo('path').decode('utf-8'))
icon = os.path.join(home, 'resources/media/icon.png')
iconRemove = os.path.join(home, 'resources/media/iconRemove.png')
FANART = os.path.join(home, 'resources/media/fanart.jpg')
folderIcon = os.path.join(home, 'resources/media/folderIcon.png')
updateIcon = os.path.join(home, 'resources/media/updateIcon.png')

def addItem(label, mode, icon):
    utils.addon_log('addItem')
    u = "plugin://{0}/?{1}".format(addon_id, urllib.urlencode({'mode': mode, 'fanart': icon}))
    liz = xbmcgui.ListItem(label)
    liz.setInfo(type="Video", infoLabels={"Title": label})
    liz.setArt({'icon': icon, 'thumb': icon, 'fanart': FANART})

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)

def addFunction(labels):
    utils.addon_log('addItem')
    u = "plugin://{0}/?{1}".format(addon_id, urllib.urlencode({'mode': 666, 'fanart': updateIcon}))
    liz = xbmcgui.ListItem(labels)
    liz.setInfo(type="Video", infoLabels={"Title": labels})
    liz.setArt({'icon': updateIcon, 'thumb': updateIcon, 'fanart':  FANART})

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)

def addDir(name, url, mode, art, plot=None, genre=None, date=None, credits=None, showcontext=False, name_parent='', type=None):
    utils.addon_log('addDir: %s (%s)' % (name.encode('utf-8'), name_parent.encode('utf-8')))
    u = "{0}?{1}".format(sys.argv[0], urllib.urlencode({'url': url.encode('utf-8'), 'name': stringUtils.cleanLabels(name.encode('utf-8')), 'type': type, 'name_parent': stringUtils.cleanLabels(name_parent.encode('utf-8')), 'fanart': art.get('fanart', '').encode('utf-8')}))
    contextMenu = []
    liz = xbmcgui.ListItem(name)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot, "Genre": genre, "dateadded": date, "credits": credits})
    liz.setArt(art)
    if type == 'tvshow':
        contextMenu.append(('Add TV-Show to MediaList', 'XBMC.RunPlugin(%s&mode=%d)' % (u, 200)))
        contextMenu.append(('Add seasons individually to MediaList', 'XBMC.RunPlugin(%s&mode=%d)' % (u, 202)))
    elif re.findall('( - |, )*([sS](taffel|eason|erie[s]{0,1})|[pP]art|[tT]eil) \d+.*', name):
        contextMenu.append(('Add Season to MediaList', 'XBMC.RunPlugin(%s&mode=%d)' % (u, 200)))
    elif type == 'movie': # ???
        contextMenu.append(('Add Movie to MediaList', 'XBMC.RunPlugin(%s&mode=%d)' % (u, 200)))
    else:
        contextMenu.append(('Create Strms', 'XBMC.RunPlugin(%s&mode=%d)' % (u, 200)))
    liz.addContextMenuItems(contextMenu)

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='%s&mode=%d' % (u, mode), listitem=liz, isFolder=True)

def addLink(name, url, mode, art, plot, genre, date, showcontext, playlist, regexs, total, setCookie="", type=None, year=None):
    utils.addon_log('addLink: %s' % name.encode('utf-8'))
    u = "{0}?{1}".format(sys.argv[0], urllib.urlencode({'url': url.encode('utf-8'), 'name': stringUtils.cleanLabels(name.encode('utf-8')), 'fanart': art.get('fanart', '').encode('utf-8'), 'type': type, 'year': year}))
    contextMenu = []
    liz = xbmcgui.ListItem(name)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot, "Genre": genre, "dateadded": date})
    liz.setArt(art)
    liz.setProperty('IsPlayable', 'true')
    if type == 'movie':
        contextMenu.append(('Add Movie to MediaList', 'XBMC.RunPlugin(%s&mode=%d&filetype=file)' % (u, 200)))
    else:
        contextMenu.append(('Create Strm', 'XBMC.RunPlugin(%s&mode=%d&filetype=file)' % (u, 200)))
    liz.addContextMenuItems(contextMenu)
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='%s&mode=%d' % (u, mode), listitem=liz, totalItems=total)

def getSources():
    utils.addon_log('getSources')
    xbmcplugin.setContent(int(sys.argv[1]), 'files')
    art = {'fanart': FANART, 'thumb': folderIcon}
    addDir('Video Plugins', 'video', 1, art)
    addDir('Music Plugins', 'audio', 1, art)
    addItem('Update', 4, updateIcon)
    addItem('Update (with removal of unused .strm files)', 42, updateIcon)
    addFunction('Update all')
    addItem('Rename', 41, updateIcon)
    addItem("Remove Media", 5, iconRemove)
    addItem('Remove Shows from TVDB cache', 51, iconRemove )
    addItem('Remove all Shows from TVDB cache', 52, iconRemove )
    if xbmc.getCondVisibility('System.HasAddon(service.watchdog)') != 1:
        json_query = ('{"jsonrpc":"2.0","method":"Addons.GetAddonDetails", "params":{ "addonid": "service.watchdog", "properties":["enabled", "installed"]}, "id": 1 }')
        addon_details = jsonUtils.sendJSON(json_query).get('addon')
        if addon_details and addon_details.get("installed"):
            addItem("Activate Watchdog", 7, icon)
        else:
            addItem("Install Watchdog", 6, icon)
    # ToDo Add label

def getType(url):
    if url.find('plugin.audio') != -1:
        Types = ['YouTube', 'Audio-Album', 'Audio-Single', 'Other']
    else:
        Types = ['Movies', 'TV-Shows', 'YouTube', 'Other']

    selectType = selectDialog('Select category', Types)

    if selectType == -1:
        return -1

    if selectType == 3:
        subType = ['(Music)', '(Movies)', '(TV-Shows)']
        selectOption = selectDialog('Select Video type:', subType)

    else:
        subType = ['(en)', '(de)', '(sp)', '(tr)', 'Other']
        selectOption = selectDialog('Select language tag', subType)

    if selectOption == -1:
        return -1

    if selectType >= 0 and selectOption >= 0:
        return Types[selectType] + subType[selectOption]

def getTypeLangOnly(Type):
    lang = ['(en)', '(de)', '(sp)', '(tr)', 'Other']
    selectOption = selectDialog('Select language tag', lang)

    if selectOption == -1:
        return -1

    if lang >= 0 and selectOption >= 0:
        return Type + lang[selectOption]

def selectDialog(header, list, autoclose=0, multiselect=False, useDetails=False, preselect=None):
    if multiselect:
        if preselect:
            return xbmcgui.Dialog().multiselect(header, list, autoclose=autoclose, useDetails=useDetails, preselect=preselect)
        else:
            return xbmcgui.Dialog().multiselect(header, list, autoclose=autoclose, useDetails=useDetails)
    else:
        if preselect:
            return xbmcgui.Dialog().select(header, list, autoclose, useDetails=useDetails, preselect=preselect)
        else:
            return xbmcgui.Dialog().select(header, list, autoclose, useDetails=useDetails)

def editDialog(nameToChange):
    dialog = xbmcgui.Dialog()
    select = dialog.input(nameToChange, type=xbmcgui.INPUT_ALPHANUM, defaultt=nameToChange)
    return select

# Before executing the code below we need to know the movie original title (string variable originaltitle) and the year (string variable year). They can be obtained from the infolabels of the listitem. The code filters the database for items with the same original title and the same year, year-1 and year+1 to avoid errors identifying the media.
def markMovie(movID, pos, total, done):
    if done:
        try:
            xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "playcount" : 1 }, "id": 1 }' % movID)
            xbmc.executebuiltin("XBMC.Container.Refresh")
        except:
            print("markMovie: Movie not in DB!?")
            pass
    else:
        if xbmc.getCondVisibility('Library.HasContent(Movies)') and pos > 0 and total > 0:
            try:
                xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "resume" : {"position":%s,"total":%s} }, "id": 1 }' % (movID, pos, total))
                xbmc.executebuiltin("XBMC.Container.Refresh")
            except:
                print("markMovie: Movie not in DB!?")
                pass

def markSeries(epID, pos, total, done):
    if done:
        try:
            xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "playcount" : 1 }, "id": 1 }' % epID)
            xbmc.executebuiltin("XBMC.Container.Refresh")
        except:
            print("markMovie: Episode not in DB!?")
            pass
    else:
        if xbmc.getCondVisibility('Library.HasContent(TVShows)') and pos > 0 and total > 0:
            try:
                xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "resume" : {"position":%s,"total":%s} }, "id": 1 }' % (epID, pos, total))
                xbmc.executebuiltin("XBMC.Container.Refresh")
            except:
                print("markSeries: Show not in DB!?")
                pass

# Functions not in usee yet:
def handle_wait(time_to_wait, header, title):
    dlg = xbmcgui.DialogProgress()
    dlg.create("OSMOSIS", header)
    secs = 0
    percent = 0
    increment = int(100 / time_to_wait)
    cancelled = False
    while secs < time_to_wait:
        secs += 1
        percent = increment * secs
        secs_left = str((time_to_wait - secs))
        remaining_display = "Starts In " + str(secs_left) + " seconds, Cancel Channel Change?"
        dlg.update(percent, title, remaining_display)
        xbmc.sleep(1000)
        if (dlg.iscanceled()):
            cancelled = True
            break
    if cancelled == True:
        return False
    else:
        dlg.close()
        return True

def show_busy_dialog():
    xbmc.executebuiltin('ActivateWindow(busydialog)')

def hide_busy_dialog():
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    while xbmc.getCondVisibility('Window.IsActive(busydialog)'):
        time.sleep(.1)

def Error(header, line1='', line2='', line3=''):
    dlg = xbmcgui.Dialog()
    dlg.ok(header, line1, line2, line3)
    del dlg

def infoDialog(str, header=ADDON_NAME, time=10000):
    try: xbmcgui.Dialog().notification(header, str, icon, time, sound=False)
    except: xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % (header, str, time, THUMB))

def okDialog(str1, str2='', header=ADDON_NAME):
    xbmcgui.Dialog().ok(header, str1, str2)

def yesnoDialog(str1, str2='', header=ADDON_NAME, yes='', no=''):
    answer = xbmcgui.Dialog().yesno(header, str1, str2, '', yes, no)
    return answer

def browse(type, heading, shares, mask='', useThumbs=False, treatAsFolder=False, path='', enableMultiple=False):
    retval = xbmcgui.Dialog().browse(type, heading, shares, mask, useThumbs, treatAsFolder, path, enableMultiple)
    return retval

def resumePointDialog(resumePoint):
    if resumePoint:
        xmldialogs.show_modal_dialog(xmldialogs.Skip,
             "plugin-video-osmosis-continue.xml",
             addon.getAddonInfo('path'),
             minutes=0,
             seconds=15,
             skip_to=int(resumePoint[0]) - 5,
             label=addon.getLocalizedString(39000).format(utils.zeitspanne(int(resumePoint[0]))[5]))

def mediaListDialog(multiselect=True, expand=True, cTypeFilter=None, header_prefix=ADDON_NAME, preselect_name=None):
    thelist = fileSys.readMediaList()
    items = []
    if not cTypeFilter:
        selectAction = ['Movies', 'TV-Shows', 'Audio', 'All']
        choice = selectDialog('%s: Select which Media Types to show' % header_prefix, selectAction)
        if choice != -1:
            if choice == 3:
                cTypeFilter = None
            else:
                cTypeFilter = selectAction[choice]
        else:
            return

    for index, entry in enumerate(thelist):
        splits = entry.strip().split('|')
        if cTypeFilter and not re.findall(cTypeFilter, splits[0]):
            continue
        name = stringUtils.getStrmname(splits[1])
        cType = splits[0].replace('(', '/').replace(')', '')
        matches=re.findall('(?:name_orig=([^;]*);)*(plugin:\/\/[^<]*)', splits[2])
        iconImage=''
        if splits[0].find('TV-Shows') != -1:
            iconImage='DefaultTVShows.png'
        if splits[0].find('Movies') != -1:
            iconImage='DefaultMovies.png'
        if splits[0].find('Audio-Album') != -1:
            iconImage='DefaultMusicAlbums.png'
        if splits[0].find('Audio-Single') != -1:
            iconImage='DefaultMusicSongs.png'
        if matches:
            if expand:
                indent_text = ''
                if len(matches) > 1:
                    items.append({'index': index, 'entry': entry, 'name': name, 'text': '{0} [{1}]'.format(name, cType), 'text2': '', 'url': splits[2], 'iconImage': 'DefaultVideoPlaylists.png'})
                    indent_text = '    '
                for match in matches:
                    name_orig=match[0]
                    url=match[1]
                    item_entry = '|'.join([splits[0], splits[1], 'name_orig=%s;%s' % (name_orig, url) if name_orig != '' else url])
                    items.append({'index': index, 'entry': item_entry, 'name': name, 'text': '{2}{0} [{1}]'.format(name, cType, indent_text), 'text2': '  {2}{1} \n  {2}[{0}]'.format(stringUtils.getProvidername(url), name_orig, indent_text), 'iconImage': iconImage, 'url': url, 'name_orig': name_orig})
            else:
                pluginnames = sorted(set([stringUtils.getProvidername(match[1]) for match in matches]), key=lambda k: k.lower())
                items.append({'index': index, 'entry': entry, 'name': name, 'text': '{0} ({1}: {2})'.format(name, cType,  ', '.join(pluginnames)), 'url': splits[2]})
        else:
            items.append({'index': index, 'entry': entry, 'name': name, 'text': '{0} ({1})'.format(name, cType), 'url': splits[2]})

    preselect_idx=None
    if expand == False:
        sItems = sorted([item.get('text') for item in items], key=lambda k: utils.key_natural_sort(k.lower()))
        if preselect_name:
            preselect_idx = [i for i, item in enumerate(sItems) if item.find(preselect_name) != -1 ]
            if preselect_idx and len(preselect_idx) > 0:
                preselect_idx=preselect_idx[0]
    else:
        sItems = sorted([xbmcgui.ListItem(label=item.get('text'), label2=item.get('text2',''), iconImage=item.get('iconImage')) for item in items],
            key=lambda k: (re.sub('.* \[([^/]*)/.*\]', '\g<1>', k.getLabel()),
                            utils.key_natural_sort(re.sub('^ *', '', k.getLabel().lower())),
                            utils.key_natural_sort(re.sub('( - |, )*([sS](taffel|eason|erie[s]{0,1})|[pP]art|[tT]eil) (?P<number>\d+).*', '\g<number>', k.getLabel2().lower())),
                            utils.key_natural_sort(re.sub('^ *', '', k.getLabel2().lower()))
                            )
                        )
        if preselect_name != None:
            preselect_idx = [i for i, item in enumerate(sItems) if item.getLabel().find(preselect_name) != -1 ]

    if multiselect:
        selectedItemsIndex = selectDialog("%s: Select items" % header_prefix, sItems, multiselect=True, useDetails=expand, preselect=preselect_idx)
        if expand == False:
            return [item for item in items for index in selectedItemsIndex if item.get('text') == sItems[index]] if selectedItemsIndex and len(selectedItemsIndex) > 0 else None
        else:
            return [item for item in items for index in selectedItemsIndex if item.get('text') == sItems[index].getLabel() and item.get('text2') == sItems[index].getLabel2()] if selectedItemsIndex and len(selectedItemsIndex) > 0 else None
    else:
        selectedItemIndex = selectDialog("%s: Select items" % header_prefix, sItems, useDetails=expand, preselect=preselect_idx)
        selectedList = [item for index, item in enumerate(items) if selectedItemIndex > -1 and item.get('text') == sItems[selectedItemIndex]]
        return selectedList[0] if len(selectedList) == 1 else None