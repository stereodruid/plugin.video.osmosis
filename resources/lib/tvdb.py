# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from kodi_six.utils import py2_decode
import requests
import json
import os
import time
import re
import xbmc, xbmcaddon, xbmcvfs, xbmcgui

import utils
from . import cache
from . import fileSys
from . import stringUtils

try:
    from fuzzywuzzy import fuzz
    use_fuzzy_matching = True
    utils.addon_log('tvdb using fuzzywuzzy for compare')
except:
    use_fuzzy_matching = False

addon = xbmcaddon.Addon()
medialist_path = py2_decode(xbmc.translatePath(addon.getSetting('MediaList_LOC')))
MediaList_LOC = os.path.join(medialist_path, 'MediaList.xml')
tvdb_token_loc = os.path.join(medialist_path, 'tvdb_token.txt')
CONFIRM_USER_ENTRIES = addon.getSetting('confirm_user_entries')
dialog_autoclose_time = int(addon.getSetting('tvdb_dialog_autoclose_time'))

api_baseurl = 'https://api.thetvdb.com/{0}'


def getShowByName(showName, lang):
    utils.addon_log('tvdb getShowByName: enter; name = {0}; lang = {1}'.format(showName, lang))
    show_data = getTVShowFromCache(showName)
    if not show_data:
        lang_tvdb_list = [lang]
        if lang != 'en':
            lang_tvdb_list.append('en')
        selected = 0
        for lang_tvdb in lang_tvdb_list:
            show_data_tvdb = getTVShowFromTVDB(re.sub(' \(\d+\)', '', showName), lang_tvdb)
            if show_data_tvdb:
                if len(show_data_tvdb) > 1:
                    showInfoDialogList = []
                    showInfoList = []
                    preselected = None
                    delta_selected = 1
                    ListItem = xbmcgui.ListItem()
                    ListItem.setLabel('Show not in list')
                    ListItem.setLabel2('Enter TVDB id manually')
                    showInfoDialogList.append(ListItem)
                    if lang != 'en' and lang_tvdb != 'en':
                        ListItem = xbmcgui.ListItem()
                        ListItem.setLabel('Try english')
                        ListItem.setLabel2('Search TVDB again with language set to english')
                        showInfoDialogList.append(ListItem)
                        delta_selected = 2
                    for show in show_data_tvdb:
                        utils.addon_log('tvbd show from id: data = {0}'.format(show))
                        ListItem = xbmcgui.ListItem()
                        ListItem.setLabel('TVDB ID={0} {1}'.format(show.get('id'), show.get('seriesName')))
                        ListItem.setLabel2(show.get('overview'))
                        if show.get('seriesName') == showName:
                            preselected = 0
                            showInfoDialogList.insert(delta_selected, ListItem)
                            showInfoList.insert(0, show)
                        else:
                            showInfoDialogList.append(ListItem)
                            showInfoList.append(show)

                    dialog = xbmcgui.Dialog()
                    time1 = time.time()
                    selected = dialog.select('{0}: multiple entries found on TVDB'
                                            .format(showName), showInfoDialogList, useDetails=True, autoclose=dialog_autoclose_time * 1000,
                                            preselect=int(delta_selected - 1 if preselected is None else preselected + delta_selected))
                    time2 = time.time()
                    if  dialog_autoclose_time > 0 and int(time2 - time1) >= dialog_autoclose_time:
                        selected = -1
                    if selected >= delta_selected:
                        show_data = showInfoList[selected - delta_selected]
                        if lang_tvdb == 'en' and lang != 'en':
                            show_data_orig_lang = getTVShowFromTVDBID(show_data.get('id'), lang)
                            show_data = show_data_orig_lang if show_data_orig_lang else show_data
                        break
                    if selected == 0:
                        break
                else:
                     show_data = show_data_tvdb[0]
                     break
        if not show_data and selected == 0:
            dialog = xbmcgui.Dialog()
            tvdb_id = 0
            try:
                tvdb_id = int(dialog.numeric(0, '{0} not found: Enter TVDB ID'.format(showName)))
            except:
                pass
            if tvdb_id > 0:
                show_data = getTVShowFromTVDBID(tvdb_id, lang)

    if show_data:
         setTVShowCache(showName, show_data)

    utils.addon_log('tvdb getShowByName: name = {0}; lang = {1}; data = {2}'.format(showName, lang, show_data))
    return show_data


def getEpisodeByName(showName, episodeSeason, episodeNr, episodeName, lang):
    utils.addon_log('tvdb getEpisodeByName: enter; name = {0}; season = {1}'.format(episodeName, episodeSeason))
    episode = None
    show_data = getShowByName(showName, lang)
    if show_data:
        utils.addon_log('tvbd show from id: data = {0}'.format(show_data))
        episode = findEpisodeByName(show_data, episodeSeason, episodeNr, episodeName, lang)

    utils.addon_log('tvdb getEpisodeByName: name = {0}; data = {1}'.format(episodeName, episode))
    return episode


def getTVShowFromTVDB(showName, lang):
    show_data = None
    params = {'name': showName}
    res = getJsonFromTVDB(api_baseurl.format('search/series'), lang, params)
    if res.status_code == 200 and len(res.json().get('data')) > 0:
        show_data = res.json().get('data')
    utils.addon_log('tvdb getTVShowFromTVDB: show_data = {0}'.format(show_data))
    return show_data


def getTVShowFromTVDBID(tvdb_id, lang):
    show_data = None
    res = getJsonFromTVDB(api_baseurl.format('series/{0}'.format(tvdb_id)), lang)
    if res.status_code == 200 and len(res.json().get('data')) > 0:
        show_data = res.json().get('data')
    utils.addon_log('tvdb getTVShowFromTVDBID: show_data = {0}'.format(show_data))
    return show_data


def getTVShowFromCache(showName):
    data = cache.getShowCache().get(showName)
    utils.addon_log('tvdb getTVShowCache: showName = {0}; data = {1}'.format(showName, data))
    return eval(data) if data and len(data.strip()) > 0 else None


def setTVShowCache(showName, data):
    utils.addon_log('tvdb setTVShowCache: showName = {0}; data = {1}'.format(showName, data))
    cache.getShowCache().set(showName, repr(data))


def deleteTVShowFromCache(showName):
    cache.getShowCache().delete(showName)
    utils.addon_log('tvdb deleteTVShowCache: showName = {0}'.format(showName))


def removeShowsFromTVDBCache(selectedItems=None):
    if not selectedItems and not xbmcgui.Dialog().yesno('Remove all Shows from TVDB cache', 'Are you sure to delete all shows from cache?'):
        return

    delete_type = xbmcgui.Dialog().select('Which data should be deleted from cache?',
                                                ['all cached data for show (includes automatched and user entries for episodes)',
                                                'automatched entries for episodes',
                                                'user entries for episode',
                                                'automatched and user entries for episodes',
                                                ],
                                                preselect=1)

    if xbmcvfs.exists(MediaList_LOC):
        thelist = fileSys.readMediaList()
        items = selectedItems if selectedItems else [{'entry': item} for item in thelist]
        if len(items) > 0:
            splittedEntries = []
            if not selectedItems:
                for item in items:
                    splits = item.get('entry').split('|')
                    splittedEntries.append(splits)
            else:
                splittedEntries = [item.get('entry').split('|') for item in selectedItems]

            for splittedEntry in splittedEntries:
                cType, name = splittedEntry[0], stringUtils.getStrmname(splittedEntry[1])
                if re.findall('TV-Shows', cType):
                    show_data = getTVShowFromCache(name)
                    if show_data:
                        tvdb_id = show_data.get('id')
                        if delete_type in [0, 1, 3]:
                            utils.addon_log_notice('tvdb: Delete automatched episode entries from cache for \'{0}\''.format(name))
                            deleteEpisodeFromCache('%', '%', tvdb_id, user_entry=False)
                        if delete_type in [0, 2, 3]:
                            utils.addon_log_notice('tvdb: Delete user episode entries from cache for \'{0}\''.format(name))
                            deleteEpisodeFromCache('%', '%', tvdb_id, user_entry=True)
                        if delete_type == 0:
                            utils.addon_log_notice('tvdb: Delete TVDB data from cache for \'{0}\''.format(name))
                            deleteTVShowFromCache(name)


def getEpisodeDataFromTVDB(showid, lang):
    utils.addon_log_notice('getEpisodeDataFromTVDB: showid = {0}, lang = {1}'.format(showid, lang))
    page = 1
    maxpages = 1
    json_data = []
    while page and maxpages and page <= maxpages:
        params = {'page': page}
        path = 'series/{0}/episodes/query'.format(showid)
        res_ep = getJsonFromTVDB(api_baseurl.format(path), lang, params)

        json_ep = res_ep.json()
        if res_ep.status_code == 200 and len(json_ep.get('data', {})) > 0:
            page = json_ep.get('links').get('next')
            maxpages = json_ep.get('links').get('last')
            json_data = json_data + json_ep.get('data')
        else:
            break

    return json_data


def findEpisodeByName(show_data, episodeSeason, episodeNr, episodeName, lang, silent=False, fallback_en=False):
    utils.addon_log('tvdb findEpisodeByName: show_data = {0}'.format(show_data))

    showid = show_data.get('id')
    showname = show_data.get('seriesName')
    utils.addon_log_notice('tvdb findEpisodeByName: \'{0}\'; showname = \'{1}\', showid = {2}, lang = {3}'.format(episodeName, showname, showid, lang))
    episode_data = getEpisodeFromCache(episodeSeason, episodeName, showid)

    if episode_data and episode_data.get('user_entry') == True and CONFIRM_USER_ENTRIES == 'true':
        if silent == False and fallback_en == False:
            confirmed = xbmcgui.Dialog().yesno('Confirm user entry for {0} is correct?'.format(showname),
                                               'S{0:02d}E{1:02d} - {2}'.format(episodeSeason, episodeNr, episodeName),
                                               'User Entry: S{0:02d}E{1:02d} - {2}'.format(episode_data.get('season'),
                                               episode_data.get('episode'), episode_data.get('episodeName', None)),
                                               autoclose=dialog_autoclose_time * 1000)
            if confirmed == False:
                episode_data = None;
        else:
            episode_data = None;

    if episode_data is None:
        ratio_max = 0
        ratio_max2 = 100
        ratio_max_season = -1
        ratio_max_episode = -1
        episodeListData = []
        episodeListDialog = []
        episodecount = 0
        episodecountcurrentseason = 0
        preselected = None

        json_data = cache.getTvdbDataCache().cacheFunction(getEpisodeDataFromTVDB, showid, lang)
        json_data = sorted(json_data, key=lambda x: (x['airedSeason'] == 0,
                                                    x['airedSeason'] != episodeSeason or x['airedEpisodeNumber'] != episodeNr,
                                                    x['airedSeason'] != episodeSeason,
                                                    x['airedSeason'],
                                                    x['airedEpisodeNumber']))

        dictresubList = []
        regex_match_start = '([ \.,:;\(]+|^)'
        regex_match_end = '(?=[ \.,:;\)]+|$)'
        dictresubList.append({
            ' *(?:-|\(|:)* *(?:[tT]eil|[pP]art|[pP]t\.) (\d+|\w+)\)*': r' (\g<1>)',
            ' *(?:-|\(|:)* *(?:[tT]eil 1 und 2|[pP]art[s]* 1 (&|and) 2)': ' (1)',
        })
        dictresubList.append({
            ' *(?:-|\(|:)* *(?:[tT]eil|[pP]art|[pP]t\.) (\d+|\w+)\)*': r' (\g<1>)',
            ' *(?:-|\(|:)* *(?:[tT]eil 1 und 2|[pP]art[s]* 1 (&|and) 2)': ' (1)',
            '[\s:;\.]\([\w\d\. ]*\)[\s:;\.]': ' ',
        })
        dictresubList.append({
            ' *(?:-|\(|:)* *(?:[tT]eil|[pP]art|[pP]t\.) (\d+|\w+)\)*': r' (\g<1>)',
            ' *(?:-|\(|:)* *(?:[tT]eil 1 und 2|[pP]art[s]* 1 (&|and) 2)': ' (1)',
            '[\s:;\.]\([\w\d\. ]*\)$': ' ',
        })
        dictresubList.append({
            ' *(?:-|\(|:)* *(?:[tT]eil|[pP]art|[pP]t\.) (\d+|\w+)\)*': r' (\g<1>)',
            ' *(?:-|\(|:)* *(?:[tT]eil 1 und 2|[pP]art[s]* 1 (&|and) 2)': ' (1)',
            '[\w\s\']{8,}\Z[:;] ([\w\s\']{8,}\Z)': '\g<1>',
        })
        dictresubList.append({
            '[pP]art [oO]ne': 'Part (1)',
            '[pP]art [tT]wo': 'Part (2)',
        })
        dictresubList.append({
            '[pP]art [oO]ne': '(1)',
            '[pP]art [tT]wo': '(2)',
        })
        dictresubList.append({
            '[pP]art 1': 'part one',
            '[pP]art 2': 'part two',
        })
        dictresubList.append({
            '{0}[eE]ins{1}'.format(regex_match_start, regex_match_end): r'\g<1>1',
            '{0}[zW]wei{1}'.format(regex_match_start, regex_match_end): r'\g<1>2',
            '{0}[dD]drei{1}'.format(regex_match_start, regex_match_end): r'\g<1>3',
        })
        dictresubList.append({
            '{0}[oO]ne{1}'.format(regex_match_start, regex_match_end): '\g<1>1',
            '{0}[tT]wo{1}'.format(regex_match_start, regex_match_end): '\g<1>2',
            '{0}[tT]hree{1}'.format(regex_match_start, regex_match_end): '\g<1>3',
        })
        dictresubList.append({
            '{0}1{1}'.format(regex_match_start, regex_match_end): r'\g<1>eins',
            '{0}2{1}'.format(regex_match_start, regex_match_end): r'\g<1>zwei',
            '{0}3{1}'.format(regex_match_start, regex_match_end): r'\g<1>drei',
        })
        dictresubList.append({
            '{0}1{1}'.format(regex_match_start, regex_match_end): r'\g<1>one',
            '{0}2{1}'.format(regex_match_start, regex_match_end): r'\g<1>two',
            '{0}3{1}'.format(regex_match_start, regex_match_end): r'\g<1>thre',
        })
        epNames = {episodeName}
        for dictresub in dictresubList:
            utils.addon_log('dictresub = {0}'.format(dictresub))
            epNames.add(utils.multiple_reSub(episodeName, dictresub))

        epNames_split = list(filter(None, re.split(' / | , ', episodeName)))
        if epNames_split[0] != episodeName:
            epNames.add(epNames_split[0])

        utils.addon_log('tvdb findEpisodeByName: epNames = {0}'.format(epNames))

        delta_selected = 2
        ListItem = xbmcgui.ListItem()
        ListItem.setLabel('Ignore')
        ListItem.setLabel2('This episode will not be exported')
        episodeListDialog.append(ListItem)
        ListItem = xbmcgui.ListItem()
        ListItem.setLabel('Enter manually')
        ListItem.setLabel2('Enter season and episode number')
        episodeListDialog.append(ListItem)
        if lang != 'en':
            ListItem = xbmcgui.ListItem()
            ListItem.setLabel('Try english')
            ListItem.setLabel2('Search TVDB again with language set to english')
            episodeListDialog.append(ListItem)
            delta_selected = 3

        for episode in json_data:
            utils.addon_log('tvdb findEpisodeByName: episode = {0}'.format(episode))
            ListItem = xbmcgui.ListItem()
            ListItem.setLabel('S{0:02d}E{1:02d} - {2}'.format(episode.get('airedSeason'), episode.get('airedEpisodeNumber'), episode.get('episodeName', episodeName)))
            ListItem.setLabel2(episode.get('overview'))
            episodeListDialog.append(ListItem)
            episodeListData.append({'season': episode.get('airedSeason'), 'episode': episode.get('airedEpisodeNumber'),
                                    'episodeName': episode.get('episodeName'), 'match_ratio':-1})
            if episode.get('airedEpisodeNumber') == episodeNr and episode.get('airedSeason') == episodeSeason:
                preselected = episodecount

            episodecount = episodecount + 1

            for epName in epNames:
                if use_fuzzy_matching == True:
                    if episode.get('episodeName', None):
                        episodeNameTVDB = episode.get('episodeName').lower()
                        epNameL = epName.lower()
                        if re.sub('( |:|,|\.)', '', episodeNameTVDB) == re.sub('( |:|,|\.)', '', epNameL):
                            ratio1 = 100
                            ratio2 = 100
                            ratio3 = 100
                            ratio4 = 100
                        else:
                            ratio1 = fuzz.token_sort_ratio(re.sub('(:|,|\.)', '', episodeNameTVDB), re.sub('(:|,|\.)', '', epNameL))
                            ratio2 = fuzz.token_sort_ratio(re.sub('( |:|,|\.)', '', episodeNameTVDB), re.sub('( |:|,|\.)', '', epNameL))
                            ratio3 = fuzz.token_set_ratio(episodeNameTVDB, epNameL)
                            ratio4 = fuzz.partial_ratio(re.sub('(:|,|\.)', '', episodeNameTVDB), re.sub('(:|,|\.)', '', epNameL))

                        if min(len(episodeNameTVDB), len(epNameL)) < 6:
                            ratio = (ratio1 + ratio2) / 2.0
                        else:
                            ratio = (ratio1 + ratio2 + ratio3 + ratio4) / 4.0
                        if episodeSeason != episode.get('airedSeason'):
                            if episode.get('airedSeason') == 0:
                                ratio = 0.72 * ratio
                            else:
                                ratio = 0.80 * ratio

                        utils.addon_log('tvdb ratio: \'{0}\'; \'{1}\' (TVDB); ratio={2:0.1f} ({3:0.1f} {4:0.1f} {5:0.1f} {6:%0.1f})'.format(epName, episode.get('episodeName'), ratio, ratio1, ratio2, ratio3, ratio4))

                        if ratio > ratio_max:
                            if ratio_max > 0 and not (ratio_max_season == episode.get('airedSeason') and ratio_max_episode == episode.get('airedEpisodeNumber')):
                                ratio_max2 = ratio_max
                            ratio_max = ratio
                            ratio_max_season = episode.get('airedSeason')
                            ratio_max_episode = episode.get('airedEpisodeNumber')
                            episode_data = {'season': episode.get('airedSeason'), 'episode': episode.get('airedEpisodeNumber'),
                                            'episodeName': episode.get('episodeName'), 'match_ratio': ratio }
                        else:
                            if (ratio_max2 == 100 or ratio_max2 < ratio) and not (ratio_max_season == episode.get('airedSeason') and ratio_max_episode == episode.get('airedEpisodeNumber')):
                                ratio_max2 = max(ratio, 0.1)

                        if ratio_max > 99.0:
                            break

                else:
                    if episode.get('episodeName', None) and (episode.get('episodeName').lower().replace(' ', '').find(epName.lower().replace(' ', '')) >= 0 or epName.lower().replace(' ', '').find(episode.get('episodeName').lower().replace(' ', '')) >= 0):
                        if episodeSeason == episode.get('airedSeason'):
                            ratio_max = 99.5
                        else:
                            ratio_max = 80
                        episode_data = {'season': episode.get('airedSeason'), 'episode': episode.get('airedEpisodeNumber'), 'episodeName': episode.get('episodeName'), 'match_ratio': ratio_max}
                        setEpisodeCache(episodeSeason, episodeName, showid, episode_data, user_entry=False)
            if ratio_max > 99.0:
                break

        match_found = False
        match_userentry = False
        if ratio_max >= 95 or (use_fuzzy_matching == False and ratio_max >= 80):
            match_found = True
        elif ((ratio_max >= 85 and ratio_max / ratio_max2 >= 1.05)
            or (ratio_max >= 75 and ratio_max / ratio_max2 >= 1.15)
            or (ratio_max >= 68 and ratio_max / ratio_max2 >= 1.48)):
            match_found = True
        else:
            utils.addon_log('tvdb \'{0}\' \'{1}\'; ratio={2:0.1f} (ratio2={3:0.1f}) [{4:0.1f}]'.format(showname, episodeName, ratio_max, ratio_max2, ratio_max / ratio_max2))

        match_found_fallback_en = False
        if match_found == False and lang != 'en':
            episode_data_en = findEpisodeByName(show_data, episodeSeason, episodeNr, episodeName, 'en', silent=True, fallback_en=True)
            if episode_data_en:
                episode_data = episode_data_en
                match_found = True
                match_found_fallback_en = True

        # if match_found == False and silent == False and ratio_max >= 60 and ratio_max/ratio_max2 > 1.05:
            # match_found = xbmcgui.Dialog().yesno('Match for {0}?'.format(showname),
                               # 'from Addon: \'S{0:02d}E{1:02d} - {2}\''.format( episodeSeason, episodeNr, episodeName),
                               # 'TVDB:       \'S{0:02d}E{1:02d} - {2}\''.format(episode_data.get('season'), episode_data.get('episode'), episode_data.get('episodeName')),
                               # 'ratio = {0:0.1f} ({1:0.1f}) [{2:0.1f}]'.format(ratio_max, ratio_max2, ratio_max/ratio_max2),
                               # autoclose = dialog_autoclose_time*1000 )
            if match_found == True:
                match_userentry = True

        if match_found == False and silent == False:
            dialog = xbmcgui.Dialog()
            time1 = time.time()
            selected = dialog.select('No match found for {0}: \'S{1:02d}E{2:02d} - {3}\''.format(showname, episodeSeason, episodeNr, episodeName) ,
                                     episodeListDialog, useDetails=True, autoclose=dialog_autoclose_time * 1000,
                                     preselect=int(0 if preselected is None else preselected + delta_selected))
            time2 = time.time()
            if dialog_autoclose_time > 0 and int(time2 - time1) >= dialog_autoclose_time:
                selected = -1

            if selected >= delta_selected and selected < episodecount + delta_selected:
                episode_data = episodeListData[selected - delta_selected]
                match_found = True
                match_userentry = True
            elif selected == 1:
                try:
                    season_input = int(dialog.numeric(0, 'Season for \'{0}\': \'S{1:02d}E{2:02d} - {3}\''.format(showname, episodeSeason, episodeNr, episodeName), str(episodeSeason)))
                    episode_input = int(dialog.numeric(0, 'Episode for \'{0}\': \'S{1:02d}E{2:02d} - {3}\''.format(showname, episodeSeason, episodeNr, episodeName), str(episodeNr)))
                    episode_data = {'season': season_input, 'episode': episode_input, 'episodeName': episodeName, 'match_ratio':-1}
                    setEpisodeCache(episodeSeason, episodeName, showid, episode_data, user_entry=True)
                    match_found = True
                    match_userentry = True
                except:
                    pass
            elif lang != 'en' and selected == 2:
                episode_data_en = findEpisodeByName(show_data, episodeSeason, episodeNr, episodeName, 'en', fallback_en=True)
                if episode_data_en:
                    episode_data = episode_data_en
                    match_found = True
                    match_found_fallback_en = True
            elif selected == 0:
                episode_data = {'season': episodeSeason, 'episode': episodeNr, 'episodeName': episodeName, 'ignore': True}
                setEpisodeCache(episodeSeason, episodeName, showid, episode_data, user_entry=True)
                utils.addon_log_notice('tvdb findEpisodeByName: ignore episodeName = \'{0}\'; lang = {1}'.format(episodeName, lang))

        if match_found == True:
            if match_found_fallback_en != True:
                setEpisodeCache(episodeSeason, episodeName, showid, episode_data, user_entry=match_userentry)
                utils.addon_log_notice('tvdb findEpisodeByName: \'{0}\' <-> \'{1}\' (TVDB); lang={2}; ratio={3:0.2f}'
                                       .format(episodeName, episode_data.get('episodeName'), lang, episode_data.get('match_ratio')))
        else:
            episode_data = None
            utils.addon_log_notice('tvdb findEpisodeByName: could not match episodeName = \'{0}\'; lang = {1}'.format(episodeName, lang))

    if episode_data and episode_data.get('ignore', False):
        return None
    return episode_data


def getEpisodeFromCache(episodeSeason, episodeName, showid):
    entry = '{0}_{1}_{2}'.format(episodeSeason, episodeName, showid)
    data_tmp = cache.getEpisodeCache().get(entry)
    if not data_tmp:
        data_tmp = cache.getEpisodeCacheManual().get(entry)
        if data_tmp:
            utils.addon_log('tvdb getEpisodeCache (user entry): season = {0}; episodeName = \'{1}\'; showid = {2}; data = {3}'.format(episodeSeason, episodeName, showid, data_tmp))
            user_entry = True
        else:
            utils.addon_log('tvdb getEpisodeCache: season = {0}; episodeName = \'{1}\'; showid = {2}; no data'.format(episodeSeason, episodeName, showid))
    else:
        utils.addon_log('tvdb getEpisodeCache: season = {0}; episodeName = \'{1}\'; showid = {2}; data = {3}'.format(episodeSeason, episodeName, showid, data_tmp))
        user_entry = False
    data = None
    if data_tmp and len(data_tmp.strip()) > 0 :
        data = eval(data_tmp)
        data['user_entry'] = user_entry
    return data


def setEpisodeCache(episodeSeason, episodeName, showid, data, user_entry=False):
    entry = '{0}_{1}_{2}'.format(episodeSeason, episodeName, showid)
    if user_entry == True:
        utils.addon_log('tvdb setEpisodeCache (user entry): season = {0}; episodeName = \'{1}\'; showid = {2}; data = {3}'.format(episodeSeason, episodeName, showid, data))
        cache.getEpisodeCacheManual().set(entry, repr(data))
        cache.getEpisodeCache().delete(entry)
    else:
        cache.getEpisodeCache().set(entry, repr(data))
        utils.addon_log('tvdb setEpisodeCache: season = {0}; episodeName = \'{1}\'; showid = {2}; data = {3}'.format(episodeSeason, episodeName, showid, data))


def deleteEpisodeFromCache(episodeSeason, episodeName, showid, user_entry=False):
    entry = '{0}_{1}_{2}'.format(episodeSeason, episodeName, showid)
    if user_entry == True:
        utils.addon_log('tvdb deleteEpisodeFromCache (user entry): season = {0}; episodeName = \'{1}\'; showid = {2}'.format(episodeSeason, episodeName, showid))
        cache.getEpisodeCacheManual().delete(entry)
    else:
        cache.getEpisodeCache().delete(entry)
        utils.addon_log('tvdb deleteEpisodeFromCache: season = {0}; episodeName = \'{1}\'; showid = {2}'.format(episodeSeason, episodeName, showid))


def getJsonFromTVDB(url, lang, params=''):
    token = getToken()
    if token:
        headers = getHeaders({'Authorization': 'Bearer {0}'.format(token), 'Accept-Language': lang})

        res = None
        retry_count = 0
        while res is None and retry_count <= 3:
            try:
                res = requests.get(url, headers=headers, params=params)
                if res.status_code == 401:
                    token = refreshToken(token)
                    headers = getHeaders({'Authorization': 'Bearer {0}'.format(token), 'Accept-Language': lang})
                    res = requests.get(url, headers=headers, params=params)
            except:
                pass
            retry_count = retry_count + 1

    return res


def getToken():
    token = None

    if xbmcvfs.exists(tvdb_token_loc):
        file_time = xbmcvfs.Stat(tvdb_token_loc).st_mtime()
        if (time.time() - file_time) / 3600 < 24:
            file = xbmcvfs.File(tvdb_token_loc, 'r')
            token = file.read()
            file.close()

    if token is None or token == '':
        headers = getHeaders({'Content-Type': 'application/json'})
        body = {'apikey': 'A1455004C2008F9B'}
        res = requests.post(api_baseurl.format('login'), headers=headers, data=json.dumps(body))
        token = writeToken(res)

    return token


def refreshToken(token):
    headers = getHeaders({'Authorization': 'Bearer {0}'.format(token)})
    res = requests.get(api_baseurl.format('refresh_token'), headers=headers)
    return writeToken(res)


def writeToken(res):
    if res.status_code == 200 and res.json().get('token', None):
        token = res.json().get('token')
        file = xbmcvfs.File(tvdb_token_loc, 'w')
        file.write(bytearray(token, 'utf-8'))
        file.close()
        return token

    return None


def getHeaders(newHeaders):
    headers = {'Accept': 'application/json'}
    headers.update(newHeaders)

    return headers