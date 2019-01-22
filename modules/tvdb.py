import requests
import utils
import json
import os
import time
import xbmc, xbmcaddon, xbmcvfs

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

addon = xbmcaddon.Addon()
medialist_path = addon.getSetting('MediaList_LOC')
tvdb_token_loc = xbmc.translatePath(os.path.join(medialist_path, 'tvdb_token.txt'))

showCache = StorageServer.StorageServer(addon.getAddonInfo('name') + 'TVShowsTVDB', 24 * 30)
episodeCache = StorageServer.StorageServer(addon.getAddonInfo('name') + 'EpisodesTVDB', 24 * 30)

api_baseurl = 'https://api.thetvdb.com/%s'


def getEpisodeByName(showName, episodeName, lang):
    utils.addon_log('tvdb getEpisodeByName: enter')
    episode = None

    token = getToken()
    if token:
        show_data = getTVShowFromCache(showName)

        if show_data:
            episode = findEpisodeByName(token, show_data, episodeName, lang)
        else:
            res = getTVShowFromTVDB(token, showName, lang)
            if res.status_code == 401:
                token = refreshToken(token)
                res = getTVShowFromTVDB(token, showName, lang)

            if res.status_code == 200 and len(res.json().get('data')) > 0:
                setTVShowCache(showName, res.json())
                episode = findEpisodeByName(token, res.json(), episodeName, lang)

    utils.addon_log('tvdb getEpisodeByName: data = %s' % episode)
    return episode


def getTVShowFromTVDB(token, showName, lang):
    headers = getHeaders({'Authorization': 'Bearer %s' % token, 'Accept-Language': lang})
    params = {'name': showName}
    res = requests.get(api_baseurl % 'search/series', headers=headers, params=params)
    utils.addon_log('tvdb searchTVShow: response = %s' % res.json())
    return res


def getTVShowFromCache(showName):
    data = showCache.get(showName)
    utils.addon_log('tvdb getTVShowFromCache: data = %s' % data)
    return eval(data) if data and len(data.strip()) > 0 else None


def setTVShowCache(showName, data):
    utils.addon_log('tvdb setTVShowCache: showName = %s; data = %s' % (showName.encode('utf-8'), data))
    showCache.set(showName, repr(data))


def findEpisodeByName(token, show_data, episodeName, lang):
    utils.addon_log('tvdb findEpisodeByName: show_data = %s' % show_data)

    showid = show_data.get('data')[0].get('id')
    episode_data = getEpisodeFromCache(episodeName, showid)
    if episode_data is None:
        page = 1
        maxpages = 1

        while page <= maxpages:
            headers = getHeaders({'Authorization': 'Bearer %s' % token, 'Accept-Language': lang})
            params = {'page': page}
            path = 'series/%s/episodes/query' % showid
            res_ep = requests.get(api_baseurl % path, headers=headers, params=params)
            utils.addon_log('tvdb findEpisodeByName: response = %s' % res_ep.json())

            json_ep = res_ep.json()
            if res_ep.status_code == 200 and len(json_ep.get('data', {})) > 0:
                page = json_ep.get('links').get('next')
                maxpages = json_ep.get('links').get('last')
                for episode in json_ep.get('data'):
                    utils.addon_log('tvdb findEpisodeByName: episode = %s' % episode)

                    if episode.get('episodeName', None) and (episode.get('episodeName').lower().find(episodeName.lower()) >= 0 or episodeName.lower().find(episode.get('episodeName').lower()) >= 0):
                        episode_data = {'season': episode.get('airedSeason'), 'episode': episode.get('airedEpisodeNumber')}
                        setEpisodeCache(episodeName, showid, episode_data)
                        return episode_data
                utils.addon_log('tvdb findEpisodeByName: could not match episodeName = %s' % episodeName.encode('utf-8'))
            else:
                break
    return episode_data


def getEpisodeFromCache(episodeName, showid):
    entry = "%s_%s" % (episodeName, showid)
    data = episodeCache.get(entry)
    utils.addon_log('tvdb getEpisodeFromCache: data = %s' % data)
    return eval(data) if data and len(data.strip()) > 0 else None


def setEpisodeCache(episodeName, showid, data):
    utils.addon_log('tvdb setEpisodeCache: episodeName = %s; showid = %s; data = %s' % (episodeName.encode('utf-8'), showid, data))
    entry = "%s_%s" % (episodeName, showid)
    episodeCache.set(entry, repr(data))


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
        res = requests.post(api_baseurl % 'login', headers=headers, data=json.dumps(body))
        token = writeToken(res)

    return token


def refreshToken(token):
    headers = getHeaders({'Authorization': 'Bearer %s' % token})
    res = requests.get(api_baseurl % 'refresh_token', headers=headers)
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