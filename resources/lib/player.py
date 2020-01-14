# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re
import xbmc
import xbmcgui
import xbmcplugin

from resources.lib import guiTools
from resources.lib import jsonUtils
from resources.lib import kodiDB
from resources.lib import stringUtils


def play(argv, params):
    selectedEntry = None
    mediaType = params.get('mediaType')
    if mediaType:
        if params.get('id') or params.get('showid'):
            providers = kodiDB.getVideo(params.get('id')) if params.get('id') else kodiDB.getVideo(params.get('showid'), params.get('episode'))
            if len(providers) == 1:
                selectedEntry = providers[0]
            else:
                selectProvider = ['[{0}] {1}'.format(stringUtils.getProvidername(provider[0]), stringUtils.parseMediaListURL(provider[0])[0]) for provider in providers]

                choice = guiTools.selectDialog('OSMOSIS: Select provider!', selectProvider)
                if choice > -1: selectedEntry = providers[choice]

        if selectedEntry:
            item = xbmcgui.ListItem(path=stringUtils.parseMediaListURL(selectedEntry[0])[1])

            props = None
            infoLabels = dict()

            if mediaType == 'show':
                sTVShowTitle = argv[0][argv[0].index('|') + 1:]
                sTVShowTitle = stringUtils.unicodetoascii(sTVShowTitle)
                iSeason = int(params.get('episode')[1:params.get('episode').index('e')])
                iEpisode = params.get('episode')[params.get('episode').index('e') + 1:]
                props = kodiDB.getKodiEpisodeID(sTVShowTitle, iSeason, iEpisode)

                infoLabels.update({'tvShowTitle': sTVShowTitle, 'season': iSeason, 'episode': iEpisode, 'mediatype': 'episode'})
                if props:
                    infoLabels.update({'title': props[2], 'aired': props[3]})

                match = re.search('<thumb>(.*)<\/thumb>', props[4])
                if match:
                   item.setArt({'thumb': match.group(1)})
            else:
                sTitle = argv[0][argv[0].index('|') + 1:]
                props = kodiDB.getKodiMovieID(sTitle)
                infoLabels['title'] = sTitle
                infoLabels['mediatype'] = 'movie'
                if props:
                    infoLabels['premiered'] = props[2]
                    infoLabels['genre'] = props[3]

            if len(infoLabels) > 0:
                item.setInfo('video', infoLabels)

            xbmcplugin.setResolvedUrl(int(argv[1]), True, item)

            # Wait until the media is started in player
            counter = 0
            activePlayers = {}
            title = params.get('episode') if mediaType == 'show' else stringUtils.cleanStrmFilesys(infoLabels.get('title'))
            while len(activePlayers) == 0 or (xbmc.Player().isPlayingVideo() and xbmc.getInfoLabel('Player.Filename') != '{0}.strm'.format(title)):
                activePlayers = jsonUtils.jsonrpc('Player.GetActivePlayers')
                xbmc.sleep(100)
                counter += 1
                if counter >= 600:
                    raise

            resumePoint = kodiDB.getPlayedURLResumePoint({'filename': xbmc.getInfoLabel('Player.Filename'), 'path': xbmc.getInfoLabel('Player.Folderpath')})
            guiTools.resumePointDialog(resumePoint)
        elif mediaType == 'audio' and params.get('url', '').startswith('plugin://'):
            xbmcplugin.setResolvedUrl(int(argv[1]), True, xbmcgui.ListItem(path=params.get('url')))
        else:
            xbmcplugin.setResolvedUrl(int(argv[1]), False, xbmcgui.ListItem())
    else:
        xbmcplugin.setResolvedUrl(int(argv[1]), False, xbmcgui.ListItem(path=params.get('url')))