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
import utils
import xbmcaddon

addon = xbmcaddon.Addon()
folder_medialistentry_movie = addon.getSetting('folder_medialistentry_movie')
folder_movie = addon.getSetting('folder_movie')


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
                   (u"//", u'/'), (u'plugin.video.', u''), (u':', u''),
                   (u'plugin.audio.', u''))

    text = utils.multiple_reSub(text, dictresub)
    text = utils.multiple_replace(text, *replacements)
    text = re.sub('[\/:*?<>|!@#$/:,]', '', text)
    text = re.sub('\(.\d*\)', "", text)
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


def cleanStrmFilesys(string):
    return re.sub('[\/:*?<>|!@#$"]', '', string)


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


def unicodetoascii(text):

    TEXT = (text.
            replace('\xe2\x80\x99', "'").
            replace('\xc3\xa9', 'e').
            replace('\xe2\x80\x90', '-').
            replace('\xe2\x80\x91', '-').
            replace('\xe2\x80\x92', '-').
            replace('\xe2\x80\x93', '-').
            replace('\xe2\x80\x94', '-').
            replace('\xe2\x80\x94', '-').
            replace('\xe2\x80\x98', "'").
            replace('\xe2\x80\x9b', "'").
            replace('\xe2\x80\x9c', '"').
            replace('\xe2\x80\x9c', '"').
            replace('\xe2\x80\x9d', '"').
            replace('\xe2\x80\x9e', '"').
            replace('\xe2\x80\x9f', '"').
            replace('\xe2\x80\xa6', '...').
            replace('\xe2\x80\xb2', "'").
            replace('\xe2\x80\xb3', "'").
            replace('\xe2\x80\xb4', "'").
            replace('\xe2\x80\xb5', "'").
            replace('\xe2\x80\xb6', "'").
            replace('\xe2\x80\xb7', "'").
            replace('\xe2\x81\xba', "+").
            replace('\xe2\x81\xbb', "-").
            replace('\xe2\x81\xbc', "=").
            replace('\xe2\x81\xbd', "(").
            replace('\xe2\x81\xbe', ")")
            )
    return TEXT


def removeStringElem(lst, string=''):
    return ([x for x in lst if x != string])


def replaceStringElem(lst, old='', new=''):
    return ([x.replace(old, new) for x in lst])


def cleanByDictReplacements(string):
    dictReplacements = {"'\(\\d+\)'" : '', '()' : '', 'Kinofilme' : '',
                        '  ' : ' ', '\(de\)':'', '\(en\)':'',
                        "\(TVshow\)":"", 'Movies' : '', 'Filme' : '',
                        'Movie' : '', "'.'" : ' ', '\(\)' : '',
                        ":": ' ', '"?"': '', '"':''}

    return utils.multiple_reSub(string, dictReplacements)


def getMovieStrmPath(strmTypePath, mediaListEntry_name, movie_name=''):
    if folder_medialistentry_movie and folder_medialistentry_movie == 'true':
        mediaListEntry_name = cleanByDictReplacements(getStrmname(mediaListEntry_name)) if mediaListEntry_name.find('++RenamedTitle++') == -1 else getStrmname(mediaListEntry_name)
        strmTypePath = os.path.join(strmTypePath, mediaListEntry_name)
    if movie_name != '' and folder_movie and folder_movie == 'true':
        movie_name = cleanByDictReplacements(getStrmname(movie_name))
        strmTypePath = os.path.join(strmTypePath, movie_name)
    return strmTypePath


def getStrmname(strm_name):
    return strm_name.strip().replace('++RenamedTitle++', '')


def invCommas(string):
   string = string.replace("'", "''")
   return string


def cleanTitle(string):
   string = string.replace(".strm", "")
   return string
