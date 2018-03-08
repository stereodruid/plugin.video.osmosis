import requests
import utils
import json
import os
import xbmc, xbmcaddon, xbmcvfs

addon = xbmcaddon.Addon()
medialist_path = addon.getSetting('MediaList_LOC')
tvdb_token_loc = xbmc.translatePath(os.path.join(medialist_path, 'tvdb_token.txt'))

api_baseurl = 'https://api.thetvdb.com/%s'
api_key = "A1455004C2008F9B"

def getEpisodeByName(showName, episodeName, lang):
    utils.addon_log('tvdb getEpisodeByName: enter')
    episode = None

    token = getToken()
    if token:
        res = searchTVShow(token, showName, lang)
        if res.status_code == 200 and len(res.json().get('data')) > 0:
            episode = findEpisodeByName(res, token, episodeName, lang)
        else:
            token = refreshToken(token)
            res = searchTVShow(token, showName, lang)
            episode = findEpisodeByName(res, token, episodeName, lang)

    utils.addon_log('tvdb getEpisodeByName: data = %s' % episode)
    return episode

def searchTVShow(token, showName, lang):
    headers = getHeaders({'Authorization': 'Bearer %s' % token, 'Accept-Language': lang})
    params = {'name': showName}
    res = requests.get(api_baseurl % 'search/series', headers = headers, params = params)
    utils.addon_log('tvdb searchTVShow: response = %s' % res.json())
    return res
			
def findEpisodeByName(res, token, episodeName, lang):
    episode = None
    show = res.json().get('data')[0]
    page = 1
    maxpages = 1

    while page <= maxpages:
        headers = getHeaders({'Authorization': 'Bearer %s' % token, 'Accept-Language': lang})
        params = {'page': page}
        path = 'series/%s/episodes/query' % show.get('id')
        res_ep = requests.get(api_baseurl % path, headers = headers, params = params)
        utils.addon_log('tvdb findEpisodeByName: response = %s' % res_ep.json())

        if res_ep.status_code == 200 and len(res_ep.json().get('data')) > 0:
            json_ep = res_ep.json()
            page = json_ep.get('links').get('next')
            maxpages = json_ep.get('links').get('last')
            for episode in json_ep.get('data'):
                utils.addon_log('tvdb findEpisodeByName: episode = %s' % episode)
                if episode.get('episodeName') == episodeName:
                    return {'season': episode.get('airedSeason'), 'episode': episode.get('airedEpisodeNumber')}

    return episode

def getToken():
    token = None

    if xbmcvfs.exists(tvdb_token_loc):
        file = xbmcvfs.File(tvdb_token_loc, 'r')
        token = file.read()
        file.close()     

    if token is None or token == '':
        headers = getHeaders({'Content-Type': 'application/json'})
        body = {"apikey": "%s" % api_key}
        res = requests.post(api_baseurl % 'login', headers = headers, data = json.dumps(body))
        token = writeToken(res)

    return token

def refreshToken(token):
    headers = getHeaders({'Authorization': 'Bearer %s' % token})
    res = requests.get(api_baseurl % 'refresh_token', headers = headers)
    return writeToken(res)

def writeToken(res):
    if res.status_code == 200 and res.json().get('token', None):
        token = res.json().get('token')
        file = open(tvdb_token_loc, 'w')
        file.write(token)
        file.close()
        return token

    return None

def getHeaders(newHeaders):
    headers = {'Accept': 'application/json'}
    for key, value in newHeaders.items():
        if key and value:
            headers[key] = value

    return headers