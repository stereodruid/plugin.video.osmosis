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
import os, re
import random
import string
import urllib, urllib2, cookielib, requests

from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP
import SimpleDownloader as downloader
import pyxbmct
import utils
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

def cleanString(string):
    newstr = uni(string)
    newstr = newstr.replace('&', '&amp;')
    newstr = newstr.replace('>', '&gt;')
    newstr = newstr.replace('<', '&lt;')
    return uni(newstr)

def uncleanString(string):
    newstr = uni(string)
    newstr = newstr.replace('&amp;', '&')
    newstr = newstr.replace('&gt;', '>')
    newstr = newstr.replace('&lt;', '<')
    return uni(newstr)
                       
def cleanLabels(text, formater=''):
    text = uni(text)
    dictresub = {'\[COLOR (.+?)\]' : '', '\[/COLOR\]' : '', '\[COLOR=(.+?)\]' : '', '\[color (.+?)\]': '',
                 '\[/color\]': '', '\[Color=(.+?)\]': '', '\[/Color\]': ''} 
 
    replacements = ((u"[]", u''), (u"[UPPERCASE]", u''),
                   (u"[/UPPERCASE]", u''), (u"[LOWERCASE]", u''),
                   (u"[/LOWERCASE]", u''), (u"[B]", u''), (u"[/B]", u''),
                   (u"[I]", u''), (u"[/I]", u''),
                   (u'[D]', u''), (u'[F]', u''),
                   (u"[CR]", u''), (u"[HD]", u''),
                   (u"()", u''), (u"[CC]", u''),
                   (u"[Cc]", u''), (u"[Favorite]", u""),
                   (u"[DRM]", u""), (u'(cc).', u''),
                   (u'(n)', u''), (u"(SUB)", u''),
                   (u"(DUB)", u''), (u'(repeat)', u''),
                   (u"(English Subtitled)", u""), (u"*", u""),
                   (u"\n", u""), (u"\r", u""),
                   (u"\t", u""), (u"\ ", u''),
                   (u"/ ", u''), (u"\\", u'/'),
                   (u"//", u'/'), (u'plugin.video.', u''),(u':', u''),
                   (u'plugin.audio.', u''))

    text = utils.multiple_reSub(text, dictresub)
    text = utils.multiple_replace(text, *replacements)
    text = re.sub('[\/:*?<>|!@#$/:]', '', text)
    text = re.sub('\(.\d*\)',"", text)
    if formater == 'title':
        text = text.title().replace("'S", "'s")
    elif formater == 'upper':
        text = text.upper()
    elif formater == 'lower':
        text = text.lower()
    else:
        text = text
        
    text = uni(text.strip())
    return text

def cleanStrms(text, formater=''):
    text = uni(text)
    text = text.replace('Full Episodes', '')
    if formater == 'title':
        text = text.title().replace("'S", "'s")
    elif formater == 'upper':
        text = text.upper()
    elif formater == 'lower':
        text = text.lower()
    else:
        text = text
    return text

def multiRstrip(text):
    replaceRstrip = ['.', ',', '-', '_', ' ', '#', '+', '`', '&', '%', '!', '?']
    for i in replaceRstrip:
        text.rstrip(i)
    return text
            
def asciis(string):
    if isinstance(string, basestring):
        if isinstance(string, unicode):
            string = string.encode('ascii', 'ignore')
    return string

def uni(string):
    if isinstance(string, basestring):
        if isinstance(string, unicode):
            string = string.encode('utf-8', 'ignore')
            
    return string
def removeHTMLTAGS(text):
    return re.sub('<[^<]+?>', '', text)

def removeNonAscii(s): return "".join(filter(lambda x: ord(x) < 128, s))

def removeStringElem(lst, string=''):
    return ([x for x in lst if x != string])
    
def replaceStringElem(lst, old='', new=''):
    return ([x.replace(old, new) for x in lst])
