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

import os, sys, re
import errno
reload(sys)
sys.setdefaultencoding("utf-8")
import urllib
import utils
import xbmc
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs
# import pafy
import SimpleDownloader as downloader
from modules import fileSys
from modules import guiTools
from modules import dialoge
from modules import jsonUtils
from modules import stringUtils


addnon_id = 'plugin.video.osmosis'
addon = xbmcaddon.Addon(addnon_id)
addon_version = addon.getAddonInfo('version')
ADDON_NAME = addon.getAddonInfo('name')
REAL_SETTINGS = xbmcaddon.Addon(id=addnon_id)
ADDON_SETTINGS = REAL_SETTINGS.getAddonInfo('profile')
MediaList_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS,'MediaList.xml'))
PAGINGTVshows = REAL_SETTINGS.getSetting('paging_tvshows')
PAGINGMovies = REAL_SETTINGS.getSetting('paging_movies')
STRM_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS,'STRM_LOC'))
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
dictReplacements = {"'\(\\d+\)'" : '', '()' : '', 'Kinofilme' : '', 
                    '  ' : ' ','\(de\)':'','\(en\)':'', 
                    "\(TVshow\)":"",'Movies' : '', 'Filme' : '', 
                    'Movie' : '', "'.'" : ' ', '\(\)' : '',
                     ":": ' ','"?"': '','"':''}

if os.path.exists(favorites) == True:
    FAV = open(favorites).read()
else: FAV = []
if os.path.exists(favorites) == True:
    FAV = open(favorites).read()
else: FAV = []

global listLength
DIRS = []
STRM_LOC = xbmc.translatePath(addon.getSetting('STRM_LOC'))

def fillPlugins(cType='video'):
    utils.addon_log('fillPlugins, type = ' + cType)
    json_query = ('{"jsonrpc":"2.0","method":"Addons.GetAddons","params":{"type":"xbmc.addon.%s","properties":["name","path","thumbnail","description","fanart","summary"]}, "id": 1 }' % cType)
    json_detail = jsonUtils.sendJSON(json_query)
    detail = re.compile("{(.*?)}", re.DOTALL).findall(json_detail)
    for f in detail:
        names = re.search('"name" *: *"(.*?)",', f)
        paths = re.search('"addonid" *: *"(.*?)",', f)
        thumbnails = re.search('"thumbnail" *: *"(.*?)",', f)
        fanarts = re.search('"fanart" *: *"(.*?)",', f)
        descriptions = re.search('"description" *: *"(.*?)",', f)
        if not descriptions:
            descriptions = re.search('"summary" *: *"(.*?)",', f)
        if descriptions:
            description = stringUtils.cleanLabels(descriptions.group(1))
        else:
            description = ''
        if names and paths:
            name = stringUtils.cleanLabels(names.group(1))
            path = paths.group(1)
            if cType == 'video' and path.startswith('plugin.video') and not path.startswith('plugin.video.osmosis'):
                thumbnail = thumbnails.group(1) #stringUtils.removeNonAscii(thumbnails.group(1))
                fanart = fanarts.group(1) #stringUtils.removeNonAscii(fanarts.group(1))
                guiTools.addDir(name, 'plugin://' + path, 101, thumbnail, fanart, description, cType, 'date', 'credits')
            elif cType == 'audio' and path.startswith('plugin.audio') and not path.startswith('plugin.video.osmosis'):
                thumbnail = thumbnails.group(1) #stringUtils.removeNonAscii(thumbnails.group(1))
                fanart = fanarts.group(1) #stringUtils.removeNonAscii(fanarts.group(1))
                guiTools.addDir(name, 'plugin://' + path, 101, thumbnail, fanart, description, cType, 'date', 'credits')

def fillPluginItems(url, media_type='video', file_type=False, strm=False, strm_name='', strm_type='Other', showtitle='None'):
    utils.addon_log('fillPluginItems')

    if not file_type:
        detail = stringUtils.uni(jsonUtils.requestList(url, media_type))
        listLength = len(detail)
    else:
        detail = stringUtils.uni(jsonUtils.requestItem(url, media_type))
     
    if strm_type.find('Cinema') != -1:
        addMovies(detail, strm_name, strm_type)
        return
    if strm_type.find('TV-Show') != -1:
        addTVShows(detail, strm_name, strm_type)
        return
    if strm_type.find('Shows-Collection') != -1:
        getTVShowFromList(detail, strm_name, strm_type)
        return
#     if strm_type.find('YouTube') != -1:
#         
#         video = pafy.new(url)
#         bestaudio = video.getbestaudio()
#         bestaudio.bitrate #get bit rate
#         bestaudio.extension #extension of audio fileurl
# 
#         bestaudio.url #get url
# 
#         #download if you want
#         bestaudio.download()
#         return
            
    for f in detail:
        files = re.search('"file" *: *"(.*?)",', f)
        filetypes = re.search('"filetype" *: *"(.*?)",', f)
        labels = re.search('"label" *: *"(.*?)",', f)
        thumbnails = re.search('"thumbnail" *: *"(.*?)",', f)
        fanarts = re.search('"fanart" *: *"(.*?)",', f)
        descriptions = re.search('"description" *: *"(.*?)",', f)
        
        if filetypes and labels and files:
            filetype = filetypes.group(1)
            label = (stringUtils.cleanLabels(labels.group(1)))
            file = (files.group(1).replace("\\\\", "\\"))
            strm_name = str(utils.multiple_reSub(strm_name.rstrip(), dictReplacements))
                         
            if not descriptions:
                description = ''
            else:
                description = stringUtils.cleanLabels(descriptions.group(1))
                
            thumbnail = thumbnails.group(1) #stringUtils.removeNonAscii(thumbnails.group(1))
            fanart = fanarts.group(1) #stringUtils.removeNonAscii(fanarts.group(1))
            
            if addon.getSetting('Link_Type') == '0': 
                link = sys.argv[0] + "?url=" + urllib.quote_plus(file) + "&mode=" + str(10) + "&name=" + urllib.quote_plus(label) + "&fanart=" + urllib.quote_plus(fanart)
            else:
                link = file
            
            if strm_type.find('TV(') != -1:
                path = os.path.join(strm_type, strm_name)
                filename = str(label)
                
            if strm_type.find('Movie') != -1:
                path = os.path.join(strm_type, strm_name)
                filename = str(label)
            
            if strm_type in ['Audio-Album']:
                path = os.path.join(strm_type, strm_name)
                try:
                    album = re.search('"album" *: *"(.*?)",', f).group(1)
                    try:
                        artist = re.search('"artist" *: *"(.*?)",', f).group(1)
                    except:
                        artist = re.search('"artist"*:*."(.*?)".,', f).group(1)
                    pass
                    titl = re.search('"title" *: *(.*?),', f).group(1)
                    types = re.search('"type" *: *(.*?),', f).group(1)
                    filename = str(strm_name + ' - ' + label)
                except:
                    filename = str(strm_name + ' - ' + label)
        
            if strm_type in ['Audio-Single']:
                path = os.path.join('Singles', str(strm_name))
                try:
                    album = re.search('"album" *: *"(.*?)",', f).group(1)
                    try:
                        artist = re.search('"artist" *: *"(.*?)",', f).group(1)
                    except:
                        artist= re.search('"artist"*:*."(.*?)".,', f).group(1)
                    pass
                    titl = re.search('"title" *: *(.*?),', f).group(1)
                    types = re.search('"type" *: *(.*?),', f).group(1)
                    filename = str(strm_name + ' - ' + label)
                except:
                    filename =str(strm_name + ' - ' + label)
            
            if strm_type in ['Other']:
                path = os.path.join('Other', strm_name)
                filename =str(strm_name + ' - ' + label)
                
                                  
            if filetype == 'file':
                if strm:
                    if strm_type == 'Audio-Album':
                        utils.addon_log(str(path + ' ' + filename))
                        utils.createSongNFO(stringUtils.cleanStrms((path.rstrip("."))), stringUtils.cleanStrms(filename.rstrip(".")), strm_ty=strm_type, artists=artist,albums=album , titls=titl, typese=types) 
                    # xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(path + " - " + filename, " writing...",5000,""))
                    fileSys.writeSTRM(stringUtils.cleanStrms((path.rstrip("."))), stringUtils.cleanStrms(filename.rstrip(".")) , link)
                else:
                    guiTools.addLink(label, file, 10, thumbnail, fanart, description, '', '', '', None, '', total=len(detail))
                    # xbmc.executebuiltin("Container.SetViewMode(500)")
            else:
                if strm:
                    fillPluginItems(file, media_type, file_type, strm, label, strm_type)
                else:
                    guiTools.addDir(label, file, 101, thumbnail, fanart, description, '', '', '')
                    # xbmc.executebuiltin("Container.SetViewMode(500)")

def removeItemsFromMediaList(action='list'):
    utils.addon_log('removingitemsdialog')
    thelist = fileSys.readMediaList(purge=False)
    items = [((thelist[i]).strip().split('|')[1]).format(i) for i in range(len(thelist))]
    dialog = dialoge.MultiChoiceDialog("Select items", items)
    dialog.doModal()

    fileSys.removeMediaList(dialog.selected, dictReplacements)
        
    xbmcgui.Dialog().notification("Finished deleting:", "{0}".format(str(dialog.selectedLabels)))
    del dialog

def addMovies(contentList, strm_name='', strm_type='Other'):
    movieList = []
    pagesDone = 0
    file=''

    while pagesDone < int(PAGINGMovies):

        for detailInfo in contentList:
            files = re.search('"file" *: *"(.*?)",', detailInfo)
            filetypes = re.search('"filetype" *: *"(.*?)",', detailInfo)
            labels = re.search('"label" *: *"(.*?)",', detailInfo)
            thumbnails = re.search('"thumbnail" *: *"(.*?)",', detailInfo)
            fanarts = re.search('"fanart" *: *"(.*?)",', detailInfo)
            descriptions = re.search('"description" *: *"(.*?)",', detailInfo)
            try:
                if filetypes and labels and files:
                    filetype = filetypes.group(1)
                    label = (stringUtils.cleanLabels(labels.group(1)))
                    file = (files.group(1).replace("\\\\", "\\"))
                    
                    if fanarts:
                        fanart = fanarts.group(1)
                    else:
                        fanart = ''
                     
                    if addon.getSetting('Link_Type') == '0': 
                        link = sys.argv[0] + "?url=" + urllib.quote_plus(file) + "&mode=" + str(10) + "&name=" + urllib.quote_plus(label) + "&fanart=" + urllib.quote_plus(fanart)
                    else:
                        link = file
                    
                    if label and strm_name and label:                        
                        label = str(utils.multiple_reSub(label.rstrip(), dictReplacements))
                        movieList.append([os.path.join(strm_type, strm_name, label), str(utils.multiple_reSub(label.rstrip(), dictReplacements)), link])
            except:
                pass
        
        pagesDone += 1
        if filetype != 'file' and pagesDone < int(PAGINGMovies):
            contentList = stringUtils.uni(jsonUtils.requestList(file, 'video'))
        else:
            pagesDone = int(PAGINGMovies)
    # Write strms for all values in movieList
    for i in movieList:   # path,name,url(+name)
        fileSys.writeSTRM(stringUtils.cleanStrms((i[0].rstrip("."))), stringUtils.cleanStrms(i[1].rstrip(".")) , i[2] + "|" + i[1])
    
    return movieList    
def getTVShowFromList(showList, strm_name='', strm_type='Other'):
    strm_type = strm_type.replace('Shows-Collection', 'TV-Shows')
    for detailInfo in showList:
        filetypes = re.search('"filetype" *: *"(.*?)",', detailInfo)
        if filetypes:
            filetype = filetypes.group(1)
            files = re.search('"file" *: *"(.*?)",', detailInfo)
            episodes = re.search('"episode" *: *(.*?),', detailInfo)
            seasons = re.search('"season" *: *(.*?),', detailInfo)
            showtitles = re.search('"showtitle" *: *"(.*?)",', detailInfo)
            
            if filetype != 'file':
                if showtitles and seasons == "-1" and episodes == "-1":
                    getEpisodes(stringUtils.uni(jsonUtils.requestList(files.group(1), 'video')), strm_name, strm_type)
                else:
                    addTVShows(stringUtils.uni(jsonUtils.requestList(files.group(1), 'video')), strm_name="", strm_type=strm_type)
        
def addTVShows(contentList, strm_name='', strm_type='Other'):
    showsList = []
    showtitle = strm_name
    pagesDone = 0
    sectiveContent = contentList
    
#     while pagesDone < int(PAGINGTVshows):
    for detailInfo in contentList:
        filetypes = re.search('"filetype" *: *"(.*?)",', detailInfo)
            
        if filetypes:
            filetype = filetypes.group(1)
            files = re.search('"file" *: *"(.*?)",', detailInfo)            
                
            if filetype != 'file':
                getEpisodes(stringUtils.uni(jsonUtils.requestList(files.group(1), 'video')), strm_name, strm_type)
            else:              
                getEpisodes(detailInfo, strm_name, strm_type)              
#         pagesDone += 1
#         
#         if filetype != 'file' and pagesDone < int(PAGINGMovies) and is_multi:
#             contentList = stringUtils.uni(jsonUtils.requestList(files.group(1), 'video'))
#         else:
#             pagesDone = int(PAGINGMovies)
    return showsList    
def getEpisodes(episodesListRaw, strm_name, strm_type):
    episodesList = []
    typeChange = []
    try:
        if type(episodesListRaw) is unicode:
            typeChange.append(episodesListRaw)
            episodesListRaw = typeChange
            
        for detailInfo in episodesListRaw:
            files = re.search('"file" *: *"(.*?)",', detailInfo)            
            filetypes = re.search('"filetype" *: *"(.*?)",', detailInfo)
            labels = re.search('"label" *: *"(.*?)",', detailInfo)
            thumbnails = re.search('"thumbnail" *: *"(.*?)",', detailInfo)
            fanarts = re.search('"fanart" *: *"(.*?)",', detailInfo)
            descriptions = re.search('"description" *: *"(.*?)",', detailInfo)
            episodes = re.search('"episode" *: *(.*?),', detailInfo)
            seasons = re.search('"season" *: *(.*?),', detailInfo)
            showtitles = re.search('"showtitle" *: *"(.*?)",', detailInfo)
            
            
            if filetypes:
                if re.search('"filetype" *: *"(.*?)",', detailInfo).group(1) == 'directory':
                    contentList = stringUtils.uni(jsonUtils.requestList(files.group(1), 'video'))
                    continue
         
                if showtitles and seasons and episodes:
                    filetype = filetypes.group(1)
                    label = (stringUtils.cleanLabels(labels.group(1))) 
                    file = (files.group(1).replace("\\\\", "\\"))
                    strm_name = str(utils.multiple_reSub(strm_name.rstrip(), dictReplacements))
                    showtitle = utils.multiple_reSub((showtitles.group(1)), dictReplacements)
                    season = (utils.multiple_reSub((seasons.group(1)).replace("-", ""), dictReplacements))
                    episode = (utils.multiple_reSub((episodes.group(1)).replace("-", ""), dictReplacements))
        
                    if not descriptions:
                        description = ''
                    else:
                        description = stringUtils.cleanLabels(descriptions.group(1))
        
                    if fanarts:
                        fanart = fanarts.group(1)
                    else:
                        fanart = ''
                             
                    if addon.getSetting('Link_Type') == '0': 
                        link = sys.argv[0] + "?url=" + urllib.quote_plus(file) + "&mode=" + str(10) + "&name=" + urllib.quote_plus(label) + "&fanart=" + urllib.quote_plus(fanart)
                    else:
                        link = file
#                     if showtitle.find('10-8:') != -1:
#                         x= showtitle
                    episodesList.append([os.path.join(xbmc.translatePath(strm_type + "//" + (utils.multiple_reSub(showtitle, dictReplacements)))), str('s' + season), str('e'+episode), link])
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    except ValueError:
        print "No valid integer in line."
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
            
    for i in episodesList:
        fileSys.writeSTRM(stringUtils.cleanStrms((i[0].rstrip("."))), stringUtils.cleanStrms(i[1].rstrip(".")) + stringUtils.cleanStrms(i[2].rstrip(".")) , i[3])
    
    return episodesList
    
def getData(url, fanart):
    utils.addon_log('getData, url = ' + cType)
    
# def playsetresolved(url, name, iconimage, setresolved=True):
#     utils.addon_log('playsetresolved')
#     if setresolved:
#         liz = xbmcgui.ListItem(name, iconImage=iconimage)
#         liz.setInfo(cType='Video', infoLabels={'Title':name})
#         liz.setProperty("IsPlayable", "true")
#         contextMenu.append(('Create Strm', 'XBMC.RunPlugin(%s&mode=200&name=%s)' % (u, name)))
#         liz.setPath(url)
#         xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
#     else:
#         xbmc.executebuiltin('XBMC.RunPlugin(' + url + ')')