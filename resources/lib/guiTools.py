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

from __future__ import unicode_literals
from kodi_six.utils import py2_encode, py2_decode
import os, sys
import time
import re
import xbmc
import xbmcgui
import xbmcplugin

from .common import Globals, jsonrpc
from .fileSys import readMediaList
from .l10n import getString
from .stringUtils import getProvidername, getStrmname
from .utils import addon_log, key_natural_sort, zeitspanne
from .xmldialogs import show_modal_dialog, Skip

try:
    import urllib.parse as urllib
except:
    import urllib

globals = Globals()


def addItem(label, mode, icon):
    addon_log('addItem')
    u = 'plugin://{0}/?{1}'.format(globals.PLUGIN_ID, urllib.urlencode({'mode': mode, 'fanart': icon}))
    liz = xbmcgui.ListItem(label)
    liz.setInfo(type='Video', infoLabels={'Title': label})
    liz.setArt({'icon': icon, 'thumb': icon, 'fanart': globals.MEDIA_FANART})

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)


def addFunction(labels):
    addon_log('addItem')
    u = 'plugin://{0}/?{1}'.format(globals.PLUGIN_ID, urllib.urlencode({'mode': 666, 'fanart': globals.MEDIA_UPDATE}))
    liz = xbmcgui.ListItem(labels)
    liz.setInfo(type='Video', infoLabels={'Title': labels})
    liz.setArt({'icon': globals.MEDIA_UPDATE, 'thumb': globals.MEDIA_UPDATE, 'fanart':  globals.MEDIA_FANART})

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)


def addDir(name, url, mode, art, plot=None, genre=None, date=None, credits=None, showcontext=False, name_parent='', type=None):
    addon_log('addDir: {0} ({1})'.format(py2_decode(name), py2_decode(name_parent)))
    u = '{0}?{1}'.format(sys.argv[0], urllib.urlencode({'url': url, 'name': py2_encode(name), 'type': type, 'name_parent': py2_encode(name_parent), 'fanart': art.get('fanart', '')}))
    contextMenu = []
    liz = xbmcgui.ListItem(name)
    liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Genre': genre, 'dateadded': date, 'credits': credits})
    liz.setArt(art)
    if type == 'tvshow':
        contextMenu.append((getString(39102, globals.addon), 'RunPlugin({0}&mode={1})'.format(u, 200)))
        contextMenu.append((getString(39104, globals.addon), 'RunPlugin({0}&mode={1})'.format(u, 202)))
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    elif re.findall('( - |, )*([sS](taffel|eason|erie[s]{0,1})|[pP]art|[tT]eil) \d+.*', name):
        contextMenu.append((getString(39103, globals.addon), 'RunPlugin({0}&mode={1})'.format(u, 200)))
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    elif type == 'movie':
        contextMenu.append((getString(39101, globals.addon), 'RunPlugin({0}&mode={1})'.format(u, 200)))
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    else:
        contextMenu.append((getString(39100, globals.addon), 'RunPlugin({0}&mode={1})'.format(u, 200)))
    liz.addContextMenuItems(contextMenu)

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='{0}&mode={1}'.format(u, mode), listitem=liz, isFolder=True)


def addLink(name, url, mode, art, plot, genre, date, showcontext, playlist, regexs, total, setCookie='', type=None, year=None):
    addon_log('addLink: {0}'.format(py2_decode(name)))
    u = '{0}?{1}'.format(sys.argv[0], urllib.urlencode({'url': url, 'name': py2_encode(name), 'fanart': art.get('fanart', ''), 'type': type, 'year': year}))
    contextMenu = []
    liz = xbmcgui.ListItem(name)
    liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Genre': genre, 'dateadded': date})
    liz.setArt(art)
    liz.setProperty('IsPlayable', 'true')
    if type == 'movie':
        contextMenu.append((getString(39101, globals.addon), 'RunPlugin({0}&mode={1}&filetype=file)'.format(u, 200)))
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    else:
        contextMenu.append((getString(39100, globals.addon), 'RunPlugin({0}&mode={1}&filetype=file)'.format(u, 200)))

    liz.addContextMenuItems(contextMenu)

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='{0}&mode={1}'.format(u, mode), listitem=liz, totalItems=total)


def getSources():
    addon_log('getSources')
    xbmcplugin.setContent(int(sys.argv[1]), 'files')
    art = {'fanart': globals.MEDIA_FANART, 'thumb': globals.MEDIA_FOLDER}
    addDir(getString(39000, globals.addon), 'video', 1, art)
    addDir(getString(39001, globals.addon), 'audio', 1, art)
    addDir(getString(39002, globals.addon), '', 102, {'thumb': 'DefaultFavourites.png'}, type='video')
    addItem(getString(39003, globals.addon), 4, globals.MEDIA_UPDATE)
    addItem(getString(39004, globals.addon), 42, globals.MEDIA_UPDATE)
    addFunction(getString(39005, globals.addon))
    addItem(getString(39006, globals.addon), 41, globals.MEDIA_UPDATE)
    addItem(getString(39007, globals.addon), 5, globals.MEDIA_REMOVE)
    addItem(getString(39008, globals.addon), 51, globals.MEDIA_REMOVE)
    addItem(getString(39009, globals.addon), 52, globals.MEDIA_REMOVE)
    if xbmc.getCondVisibility('System.HasAddon(service.watchdog)') != 1:
        addon_details = jsonrpc('Addons.GetAddonDetails', dict(addonid='service.watchdog', properties=['enabled', 'installed'])).get('addon')
        if addon_details and addon_details.get('installed'):
            addItem(getString(39010, globals.addon), 7, globals.MEDIA_ICON)
        else:
            addItem(getString(39011, globals.addon), 6, globals.MEDIA_ICON)


def getType(url):
    if url.find('plugin.audio') != -1:
        types = [dict(id='YouTube', string_id=39116), dict(id='Audio-Album', string_id=39114), dict(id='Audio-Single', string_id=39115), dict(id='Other', string_id=39117)]
    else:
        types = [dict(id='Movies', string_id=39111), dict(id='TV-Shows', string_id=39112), dict(id='YouTube', string_id=39116), dict(id='Other', string_id=39117)]

    selectType = selectDialog(getString(39109, globals.addon), [getString(type.get('string_id')) for type in types])

    if selectType == -1:
        return -1

    if selectType == 3:
        subtypes = [dict(id='(Music)', string_id=39113), dict(id='(Movies)', string_id=39111), dict(id='(TV-Shows)', string_id=39112)]
        selectOption = selectDialog(getString(39109, globals.addon), [getString(subtype.get('string_id')) for subtype in subtypes])
    else:
        subtypes = [dict(id='(de)', string_id=39118), dict(id='(en)', string_id=39119), dict(id='(sp)', string_id=39120), dict(id='(tr)', string_id=39121), dict(id='Other', string_id=39117)]
        selectOption = selectDialog(getString(39110, globals.addon), [getString(subtype.get('string_id')) for subtype in subtypes])

    if selectOption == -1:
        return -1

    if selectType >= 0 and selectOption >= 0:
        return '{0}{1}'.format(types[selectType].get('id'), subtypes[selectOption].get('id'))


def getTypeLangOnly(Type):
    langs = [dict(id='(de)', string_id=39118), dict(id='(en)', string_id=39119), dict(id='(sp)', string_id=39120), dict(id='(tr)', string_id=39121), dict(id='Other', string_id=39117)]
    selectOption = selectDialog(getString(39110, globals.addon), [getString(lang.get('string_id')) for lang in langs])

    if selectOption == -1:
        return -1

    return '{0}{1}'.format(Type, langs[selectOption].get('id'))


def selectDialog(header, list, autoclose=0, multiselect=False, useDetails=False, preselect=None):
    if multiselect:
        if preselect:
            return globals.dialog.multiselect(header, list, autoclose=autoclose, useDetails=useDetails, preselect=preselect)
        else:
            return globals.dialog.multiselect(header, list, autoclose=autoclose, useDetails=useDetails)
    else:
        if preselect:
            return globals.dialog.select(header, list, autoclose, useDetails=useDetails, preselect=preselect)
        else:
            return globals.dialog.select(header, list, autoclose, useDetails=useDetails)


def editDialog(nameToChange):
    return py2_decode(globals.dialog.input(nameToChange, type=xbmcgui.INPUT_ALPHANUM, defaultt=nameToChange))


def resumePointDialog(resume, dialog, playback_rewind):
    if resume and resume.get('position') > 0.0:
        position = int(resume.get('position')) - playback_rewind
        resumeLabel = getString(12022).format(time.strftime("%H:%M:%S", time.gmtime(position)))
        if dialog == 0:
            sel = globals.dialog.contextmenu([resumeLabel, xbmc.getLocalizedString(12021)])
            if sel == 0:
                return position
        elif dialog == 1:
            skip = show_modal_dialog(Skip,
                'plugin-video-osmosis-resume.xml',
                globals.PLUGIN_PATH,
                minutes=0,
                seconds=15,
                skip_to=position,
                label=resumeLabel
            )
            if skip:
                return position

    return 0


def mediaListDialog(multiselect=True, expand=True, cTypeFilter=None, header_prefix=globals.PLUGIN_NAME, preselect_name=None):
    thelist = readMediaList()
    items = []
    if not cTypeFilter:
        selectActions = [dict(id='Movies', string_id=39111), dict(id='TV-Shows', string_id=39112), dict(id='Audio', string_id=39113), dict(id='All', string_id=39122)]
        choice = selectDialog('{0}: {1}'.format(header_prefix, getString(39109, globals.addon)), [getString(selectAction.get('string_id')) for selectAction in selectActions])
        if choice != -1:
            if choice == 3:
                cTypeFilter = None
            else:
                cTypeFilter = selectActions[choice].get('id')
        else:
            return

    for index, entry in enumerate(thelist):
        splits = entry.strip().split('|')
        if cTypeFilter and not re.findall(cTypeFilter, splits[0]):
            continue
        name = getStrmname(splits[1])
        cType = splits[0].replace('(', '/').replace(')', '')
        matches = re.findall('(?:name_orig=([^;]*);)*(plugin:\/\/[^<]*)', splits[2])
        iconImage = ''
        if splits[0].find('TV-Shows') != -1:
            iconImage = 'DefaultTVShows.png'
        if splits[0].find('Movies') != -1:
            iconImage = 'DefaultMovies.png'
        if splits[0].find('Audio-Album') != -1:
            iconImage = 'DefaultMusicAlbums.png'
        if splits[0].find('Audio-Single') != -1:
            iconImage = 'DefaultMusicSongs.png'
        if matches:
            if expand:
                indent_text = ''
                indent_text2 = ''
                if len(matches) > 1:
                    items.append({'index': index, 'entry': entry, 'name': name, 'text': '{0} [{1}]'.format(name, cType), 'text2': '', \
                                  'url': splits[2], 'iconImage': 'DefaultVideoPlaylists.png'})
                    indent_text = '    '
                    indent_text2 = '{0} '.format(indent_text)
                for match in matches:
                    name_orig = match[0]
                    url = match[1]
                    item_entry = '|'.join([splits[0], name, 'name_orig={0};{1}'.format(name_orig, url) if name_orig else url])
                    items.append({'index': index, 'entry': item_entry, 'name': name, 'text': '{2}{0} [{1}]'.format(name, cType, indent_text), \
                                  'text2': ('{2}{1}\n{2}[{0}]' if name_orig else '{2}[{0}]').format(getProvidername(url), name_orig, indent_text2), \
                                  'iconImage': iconImage, 'url': url, 'name_orig': name_orig})

            else:
                pluginnames = sorted(set([getProvidername(match[1]) for match in matches]), key=lambda k: k.lower())
                items.append({'index': index, 'entry': entry, 'name': name, 'text': '{0} ({1}: {2})'.format(name, cType, ', '.join(pluginnames)), 'url': splits[2]})
        else:
            items.append({'index': index, 'entry': entry, 'name': name, 'text': '{0} ({1})'.format(name, cType), 'url': splits[2]})

    preselect_idx = None
    if expand == False:
        sItems = sorted([item.get('text') for item in items], key=lambda k: key_natural_sort(k.lower()))
        if preselect_name:
            preselect_idx = [i for i, item in enumerate(sItems) if item.find(preselect_name) != -1 ]
    else:
        liz = []
        for item in items:
            li = xbmcgui.ListItem(label=item.get('text'), label2=item.get('text2'))
            li.setArt({'icon': item.get('iconImage')})
            liz.append(li)
        sItems = sorted(liz,
            key=lambda k: (re.sub('.* \[([^/]*)/.*\]', '\g<1>', py2_decode(k.getLabel())),
                            key_natural_sort(re.sub('^ *', '', py2_decode(k.getLabel().lower()))),
                            key_natural_sort(re.sub('( - |, )*([sS](taffel|eason|erie[s]{0,1})|[pP]art|[tT]eil) (?P<number>\d+).*', '\g<number>', py2_decode(k.getLabel2().lower()))),
                            key_natural_sort(re.sub('^ *', '', py2_decode(k.getLabel2().lower())))
                            )
                        )
        if preselect_name:
            preselect_idx = [i for i, item in enumerate(sItems) if item.getLabel().find(preselect_name) != -1 ]

    if multiselect == False and preselect_idx and isinstance(preselect_idx, list) and len(preselect_idx) > 0:
        preselect_idx = preselect_idx[0]

    selectedItemsIndex = selectDialog('{0}: {1}'.format(header_prefix, getString(39124, globals.addon)), sItems, multiselect=multiselect, useDetails=expand, preselect=preselect_idx)
    if multiselect:
        if expand == False:
            return [item for item in items for index in selectedItemsIndex if item.get('text') == py2_decode(sItems[index])] if selectedItemsIndex and len(selectedItemsIndex) > 0 else None
        else:
            return [item for item in items for index in selectedItemsIndex if item.get('text') == py2_decode(sItems[index].getLabel()) and item.get('text2') == py2_decode(sItems[index].getLabel2())] if selectedItemsIndex and len(selectedItemsIndex) > 0 else None
    else:
        selectedList = [item for index, item in enumerate(items) if selectedItemsIndex > -1 and item.get('text') == py2_decode(sItems[selectedItemsIndex])]
        return selectedList[0] if len(selectedList) == 1 else None
