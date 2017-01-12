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
from modules import urlUtils

thisDialog = sys.modules[__name__]    
thisDialog.dialogeBG = None

def initialize_DialogBG(mess1,mess2):
    if not thisDialog.dialogeBG:
        thisDialog.dialogeBG = xbmcgui.DialogProgressBG()
        thisDialog.dialogeBG.create("OSMOSIS: " + mess1 + ": " , " " + mess2)

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
    initialize_DialogBG("Updating", "Getting content..")
    thisDialog.dialogeBG.update(0, ADDON_NAME + ": Getting: ", strm_name.replace('++RenamedTitle++', ''))
    utils.addon_log('fillPluginItems')
    detail = []
    if url.find("playMode=play")== -1:
        if not file_type:
            detail = stringUtils.uni(jsonUtils.requestList(url, media_type))
            listLength = len(detail)
        else:
            detail = stringUtils.uni(jsonUtils.requestItem(url, media_type))
    else: 
        detail.append("palyableSingleMedia")
        detail.append(url)
        
    thisDialog.dialogeBG.close()
    thisDialog.dialogeBG = None  
    if strm_type.find('Cinema') != -1 or strm_type.find('YouTube') != -1 :
        try:
            initialize_DialogBG("Movie", "Adding")
            addMovies(detail, strm_name, strm_type)
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None       
            return
        except:
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
            utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
            print ("Unexpected error:"), sys.exc_info()[0]
            raise
    
    if strm_type.find('TVShows sub structures') != -1:
        try:
            initialize_DialogBG("TV-Show SST", "Adding")
            addTVShowsSST(detail, strm_name, strm_type)
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None
            return 
        except:
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
            utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
            print ("Unexpected error:"), sys.exc_info()[0]
            raise  
                 
    if strm_type.find('TV-Show') != -1:
        try:
            initialize_DialogBG("TV-Show", "Adding")
            addTVShows(detail, strm_name, strm_type)
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None
            return
        except:
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
            utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
            print ("Unexpected error:"), sys.exc_info()[0]
            raise
        
    if strm_type.find('Shows-Collection') != -1:
        try:
            initialize_DialogBG("Shows-Collection", "Adding")
            getTVShowFromList(detail, strm_name, strm_type)
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None
            return
        except:
            thisDialog.dialogeBG.close()
            thisDialog.dialogeBG = None
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
            utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
            print ("Unexpected error:"), sys.exc_info()[0]
            raise
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
            strm_name = str(utils.multiple_reSub(strm_name.rstrip().lstrip(), dictReplacements))
                         
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
    j = 100 / (len(contentList) * int(PAGINGMovies))
    
    while pagesDone < int(PAGINGMovies):
        if not contentList[0] == "palyableSingleMedia":
            for detailInfo in contentList:
                detailInfo = stringUtils.removeHTMLTAGS(detailInfo)
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
                        
                        if label and strm_name:
                                                   
                            label = str(utils.multiple_reSub(label.rstrip().lstrip(), dictReplacements))
                            thisDialog.dialogeBG.update(99, ADDON_NAME + ": Writing File: ",  " Video: " + label)
                            movieList.append([os.path.join(strm_type, strm_name.rstrip().lstrip().replace('++RenamedTitle++', '') , label.rstrip().lstrip()), str(utils.multiple_reSub(label.rstrip().lstrip(), dictReplacements)), link])
                            j = j + 100 / (len(contentList) * int(PAGINGMovies))
                except IOError as (errno, strerror):
                    print ("I/O error({0}): {1}").format(errno, strerror)
                except ValueError:
                    print ("No valid integer in line.")
                except:
                    guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
                    utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
                    print ("Unexpected error:"), sys.exc_info()[0]
                    raise
            pagesDone += 1
            if filetype != 'file' and pagesDone < int(PAGINGMovies):
                contentList = stringUtils.uni(jsonUtils.requestList(file, 'video'))
            else:
                pagesDone = int(PAGINGMovies)            
        else:
            movieList.append([os.path.join(strm_type, strm_name.rstrip().lstrip().replace('++RenamedTitle++', '')), str(utils.multiple_reSub(strm_name.rstrip().lstrip(), dictReplacements)), contentList[1]])
            pagesDone = int(PAGINGMovies)

    try:
        # Write strms for all values in movieList
        for i in movieList:   # path,name,url(+name)
            fileSys.writeSTRM(stringUtils.cleanStrms((i[0].rstrip("."))), stringUtils.cleanStrms(i[1].rstrip(".")) , i[2] + "|" + i[1])
    except IOError as (errno, strerror):
        print ("I/O error({0}): {1}").format(errno, strerror)
    except ValueError:
        print ("No valid integer in line.")
    except:
        guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
        utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
        print ("Unexpected error:"), sys.exc_info()[0]
        raise
    
    return movieList
 
def getTVShowFromList(showList, strm_name='', strm_type='Other'):
    pagesDone = 0
    file=''
    
    while pagesDone < int(PAGINGTVshows):
        strm_type = strm_type.replace('Shows-Collection', 'TV-Shows')
        try:
            for detailInfo in showList:
                detailInfo = stringUtils.removeHTMLTAGS(detailInfo)
                filetypes = re.search('"filetype" *: *"(.*?)",', detailInfo)
                if filetypes:
                    filetype = filetypes.group(1)
                    files = re.search('"file" *: *"(.*?)",', detailInfo)
                    episodes = re.search('"episode" *: *(.*?),', detailInfo)
                    seasons = re.search('"season" *: *(.*?),', detailInfo)
                    showtitles = re.search('"showtitle" *: *"(.*?)",', detailInfo)
                    labels = re.search('"label" *: *"(.*?)",', detailInfo)
                    
                    if labels:
                        label = str(labels.group(1).lstrip().rstrip())
                    else:
                        label = "None"
    
                    if showtitles: 
                        showtitle = str(showtitles.group(1).lstrip().rstrip())
                    else:
                        label = "None"
                     
                    if not fileSys.isInMediaList(label, strm_type) and label != "" and label != ">>>" and label != "None" and files.group(1).find("playMode=play") == -1:            
                        fileSys.writeMediaList(files.group(1).lstrip().rstrip(), label, strm_type)
    
                                
                    if filetype != 'file':
                        if showtitles and seasons == "-1" and episodes == "-1":
                            xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (ADDON_NAME, "ShowsList" , 1000, ""))
                            getEpisodes(stringUtils.uni(jsonUtils.requestList(files.group(1), 'video')), strm_name.rstrip().lstrip(), strm_type)
                        else:
                            addTVShows(stringUtils.uni(jsonUtils.requestList(files.group(1), 'video')), strm_name="", strm_type=strm_type)
        except IOError as (errno, strerror):
            print ("I/O error({0}): {1}").format(errno, strerror)
        except ValueError:
            print ("No valid integer in line.")
        except:
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
            utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
            print ("Unexpected error:"), sys.exc_info()[0]
            raise
        
        pagesDone += 1
        if pagesDone < int(PAGINGMovies):
            showList = []
            showList = stringUtils.uni(jsonUtils.requestList(files.group(1), 'video'))
#             dirList = stringUtils.uni(jsonUtils.requestList(files.group(1), 'video'))
#             for i in dirList:
#                 showList.append(i)
        
def addTVShowsSST(contentList, strm_name='', strm_type='Other'):
    showsList = []
    showtitle = strm_name
    pagesDone = 0
    sectiveContent = contentList
    #     while pagesDone < int(PAGINGTVshows):
    for detailInfo in contentList:
        detailInfo = stringUtils.removeHTMLTAGS(detailInfo)
        filetypes = re.search('"filetype" *: *"(.*?)",', detailInfo)
        try:        
            if filetypes:
                filetype = filetypes.group(1)
                files = re.search('"file" *: *"(.*?)",', detailInfo)
                if filetype != 'file':
                    contentListSub = stringUtils.uni(jsonUtils.requestList(files.group(1), 'video'))
                    for detailInfo in contentListSub:
                        while filetype != "file":
                            detailInfo = stringUtils.removeHTMLTAGS(detailInfo)
                            filetypes = re.search('"filetype" *: *"(.*?)",', detailInfo)
                                  
                            if filetype != 'file':
                                detailInfo = stringUtils.uni(jsonUtils.requestList(files.group(1), 'video')) 
                            else:
                                getEpisodes(stringUtils.uni(detailInfo), strm_name.rstrip().lstrip(), strm_type)              
                        
                            getEpisodes(stringUtils.uni(detailInfo), strm_name.rstrip().lstrip(), strm_type)       
                         
        except IOError as (errno, strerror):
            print ("I/O error({0}): {1}").format(errno, strerror)
        except ValueError:
            print ("No valid integer in line.")
        except:
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
            utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
            print ("Unexpected error:"), sys.exc_info()[0]
            raise
  
    return showsList 
       
def addTVShows(contentList, strm_name='', strm_type='Other'):
    showsList = []
    showtitle = strm_name
    pagesDone = 0
    sectiveContent = contentList
    #     while pagesDone < int(PAGINGTVshows):
    for detailInfo in contentList:
        detailInfo = stringUtils.removeHTMLTAGS(detailInfo)
        filetypes = re.search('"filetype" *: *"(.*?)",', detailInfo)
        try:        
            if filetypes:
                filetype = filetypes.group(1)
                files = re.search('"file" *: *"(.*?)",', detailInfo)            
                    
                if filetype != 'file':
                    getEpisodes(stringUtils.uni(jsonUtils.requestList(files.group(1), 'video')), strm_name.rstrip().lstrip(), strm_type)
                else:              
                    getEpisodes(detailInfo, strm_name, strm_type) 
        except IOError as (errno, strerror):
            print ("I/O error({0}): {1}").format(errno, strerror)
        except ValueError:
            print ("No valid integer in line.")
        except:
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
            utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
            print ("Unexpected error:"), sys.exc_info()[0]
            raise
  
    return showsList 
   
def getEpisodes(episodesListRaw, strm_name, strm_type):
    episodesList = []
    typeChange = []
    thisDialog.dialogeBG.update(0, ADDON_NAME + " Working!", " Analysing episodes...")

    try:
        if type(episodesListRaw) is unicode:
            typeChange.append(episodesListRaw)
            episodesListRaw = typeChange
    
        for detailInfo in episodesListRaw:
            
            detailInfo = stringUtils.removeHTMLTAGS(detailInfo)
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
                    strm_name = str(utils.multiple_reSub(strm_name.rstrip().lstrip(), dictReplacements))
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
#                   
                    if strm_name.find("++RenamedTitle++") != -1:
                        showtitle = strm_name.rstrip().lstrip().replace('++RenamedTitle++', '')
                    if showtitle != "" and strm_type != "":
                        episodesList.append([os.path.join(xbmc.translatePath(strm_type + "//" + (utils.multiple_reSub(showtitle.rstrip().lstrip(), dictReplacements)))), str('s' + season), str('e'+episode), link])
                        
    except IOError as (errno, strerror):
        print ("I/O error({0}): {1}").format(errno, strerror)
    except ValueError:
        print ("No valid integer in line.")
    except:
        guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
        utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
        print ("Unexpected error:"), sys.exc_info()[0]
        raise

    for i in episodesList:
        j = 100 / len(episodesList)
        thisDialog.dialogeBG.update(99, ADDON_NAME + ": Writing File: ",  stringUtils.cleanStrms(i[0].rstrip(".")) + ": " + stringUtils.cleanStrms(i[1].rstrip(".")) + stringUtils.cleanStrms(i[2].rstrip(".")))
        fileSys.writeSTRM(stringUtils.cleanStrms((i[0].rstrip("."))), stringUtils.cleanStrms(i[1].rstrip(".")) + stringUtils.cleanStrms(i[2].rstrip(".")) , i[3])
        j = j + 100 / len(episodesList)
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