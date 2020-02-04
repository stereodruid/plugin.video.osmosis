# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from kodi_six.utils import PY2, py2_encode, py2_decode
import os
import re
import xbmc
import xbmcgui
import xbmcplugin

from .common import Globals, Settings, sleep
from .guiTools import resumePointDialog, selectDialog
from .jsonUtils import jsonrpc
from .kodiDB import getKodiEpisodeID, getKodiMovieID, getVideo
from .stringUtils import cleanStrmFilesys, getProvidername, parseMediaListURL
from .utils import addon_log


def play(argv, params):
    selectedEntry = None
    mediaType = params.get('mediaType')
    if mediaType:
        if params.get('id') or params.get('showid'):
            providers = getVideo(params.get('id')) if params.get('id') else getVideo(params.get('showid'), params.get('episode'))
            if PY2:
                providers = [tuple(map(lambda x: py2_decode(x), provider)) for provider in providers]
            if len(providers) == 1:
                selectedEntry = providers[0]
            else:
                selectProvider = ['[{0}] {1}'.format(getProvidername(provider[0]), parseMediaListURL(provider[0])[0]) for provider in providers]

                choice = selectDialog('OSMOSIS: Select provider!', selectProvider)
                if choice > -1: selectedEntry = providers[choice]

        if selectedEntry:
            url = parseMediaListURL(selectedEntry[0])[1]
            item = xbmcgui.ListItem(path=url)

            props = None
            infoLabels = dict()
            if mediaType == 'show':
                sTVShowTitle = argv[0][argv[0].index('|') + 1:]
                iSeason = int(params.get('episode')[1:params.get('episode').index('e')])
                iEpisode = params.get('episode')[params.get('episode').index('e') + 1:]
                props = getKodiEpisodeID(selectedEntry[2], iSeason, iEpisode)

                infoLabels.update({'tvShowTitle': sTVShowTitle, 'season': iSeason, 'episode': iEpisode, 'mediatype': 'episode'})
                if props:
                    infoLabels.update({'title': props.get('title'), 'aired': props.get('aired')})

                    match = re.search('<thumb>(.*)<\/thumb>', props.get('thumb'))
                    if match:
                        item.setArt({'thumb': match.group(1)})
            else:
                sTitle = argv[0][argv[0].index('|') + 1:]
                props = getKodiMovieID(selectedEntry[2])
                infoLabels['title'] = sTitle
                infoLabels['mediatype'] = 'movie'
                if props:
                    infoLabels.update({'premiered': props.get('premiered'), 'genre': props.get('genre')})

            if len(infoLabels) > 0:
                item.setInfo('video', infoLabels)

            if not props:
                props = dict()

            globals = Globals()
            player = Player()
            player.log = addon_log
            player.pluginhandle = int(argv[1])
            player.monitor = globals.monitor
            player.url = url
            player.filepath = props.get('filepath')

            position = 0
            settings = Settings()
            dialog = settings.PLAYBACK_DIALOG
            playback_rewind = settings.PLAYBACK_REWIND
            if dialog == 0:
                position = player.checkResume(dialog, playback_rewind)

            player.resolve(item)

            title = py2_encode('{0}.strm'.format(params.get('episode') if mediaType == 'show' else cleanStrmFilesys(infoLabels.get('title'))))
            while not player.monitor.abortRequested() and player.running and xbmc.getInfoLabel('Player.Filename') != title:
                player.monitor.waitForAbort(player.sleeptm)

            if dialog == 1:
                position = player.checkResume(dialog, playback_rewind)

            player.resume(position)

            if not player.filepath:
                player.filepath = xbmc.getInfoLabel('Player.Filenameandpath')

            while not player.monitor.abortRequested() and xbmc.getInfoLabel('Player.Filename') == title:
                player.monitor.waitForAbort(player.sleeptm)
            player.finished()
            del player
        elif mediaType == 'audio' and params.get('url', '').startswith('plugin://'):
            xbmcplugin.setResolvedUrl(int(argv[1]), True, xbmcgui.ListItem(path=params.get('url')))
        else:
            xbmcplugin.setResolvedUrl(int(argv[1]), False, xbmcgui.ListItem())
    else:
        xbmcplugin.setResolvedUrl(int(argv[1]), False, xbmcgui.ListItem(path=params.get('url')))


class Player(xbmc.Player):


    def __init__(self):
        super(Player, self).__init__()
        self.globals = Globals()
        self.log = None
        self.pluginhandle = None
        self.monitor = None
        self.url = None
        self.filepath = None
        self.running = False
        self.sleeptm = 0.2
        self.video_totaltime = 0


    def resolve(self, li):
        xbmcplugin.setResolvedUrl(self.globals.pluginhandle, True, li)
        self.running = True
        self.getTimes()


    def onPlayBackEnded(self):
        self.finished()


    def onPlayBackStopped(self):
        self.finished()


    def checkResume(self, dialog, playback_rewind):
        resume = None
        if not re.search('(plugin\.video\.amazon)', self.url) and self.filepath:
            resume = jsonrpc('Files.GetFileDetails', {'file': self.filepath, 'media': 'video', 'properties': ['resume']}).get('filedetails', {}).get('resume', {})
        return resumePointDialog(resume, dialog, playback_rewind)


    def resume(self, position):
        if position > 0:
            while not self.monitor.abortRequested() and self.running and (((self.getTime() + 10) < position) or (position < (self.getTime() - 10))):
                self.seekTime(position)
                self.monitor.waitForAbort(self.sleeptm)


    def finished(self):
        if self.running:
            self.running = False
            if self.globals.FEATURE_PLUGIN_RESUME_SYNC:
                resume = jsonrpc("Files.GetFileDetails", {"file": self.filepath, "media": "video", "properties": ["resume"]}).get('filedetails', {}).get('resume', {})
                if resume:
                    jsonrpc("Files.SetFileDetails", {"file": self.url, "media": "video", "resume": {"position": resume.get('position'), "total": resume.get('total')}})


    def getTimes(self):
        while self.video_totaltime <= 0:
            sleep(self.sleeptm)
            if self.isPlaying() and self.getTotalTime() >= self.getTime() >= 0:
                self.video_totaltime = self.getTotalTime()