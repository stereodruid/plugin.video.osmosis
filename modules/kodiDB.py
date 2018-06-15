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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
from modules import guiTools
from modules import fileSys
from modules import stringUtils
import xbmc
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs
import sqlite3
import mysql.connector
import utils

addon = xbmcaddon.Addon()
profile = addon.getAddonInfo('profile')
MusicDB_LOC = xbmc.translatePath(os.path.join(profile, 'Musik.db'))
MODBPATH = xbmc.translatePath(os.path.join(profile, 'Movies.db'))
SHDBPATH = xbmc.translatePath(os.path.join(profile, 'Shows.db'))
MODBPATH_MYSQL = xbmc.translatePath(os.path.join(profile, 'Movies'))
SHDBPATH_MYSQL = xbmc.translatePath(os.path.join(profile, 'TVShows'))
STRM_LOC = xbmc.translatePath(os.path.join(addon.getSetting('STRM_LOC')))
DATABASE_MYSQL = addon.getSetting('USE_MYSQL')

# Databases
KMDBUSERNAME = addon.getSetting('KMusic-DB username')
KMDBPASSWORD = addon.getSetting('KMusic-DB password')
KMDBNAME = addon.getSetting('KMusic-DB name')
KMDBPATH = xbmc.translatePath(addon.getSetting('KMusic-DB path'))
KMDBIP = addon.getSetting('KMusic-DB IP')
KMDBPORT = addon.getSetting('KMusic-DB port')

KMODBUSERNAME = addon.getSetting('KMovie-DB username')
KMODBPASSWORD = addon.getSetting('KMovie-DB password')
KMODBNAME = addon.getSetting('KMovie-DB name')
KMODBPATH = xbmc.translatePath(addon.getSetting('KMovie-DB path'))
KMODBIP = addon.getSetting('KMovie-DB IP')
KMODBPORT = addon.getSetting('KMovie-DB port')

MOVDBUSERNAME = addon.getSetting('Movies-DB username')
MOVDBPASSWORD = addon.getSetting('Movies-DB password')
MOVDBNAME = addon.getSetting('Movies-DB name')
MOVDBIP = addon.getSetting('Movies-DB IP')
MOVDBPORT = addon.getSetting('Movies-DB port')

TVSDBUSERNAME = addon.getSetting('TV-Show-DB username')
TVSDBPASSWORD = addon.getSetting('TV-Show-DB password')
TVSDBNAME = addon.getSetting('TV-Show-DB name')
TVSDBIP = addon.getSetting('TV-Show-DB IP')
TVSDBPORT = addon.getSetting('TV-Show-DB port')

MDBUSERNAME = addon.getSetting('Music-DB username')
MDBPASSWORD = addon.getSetting('Music-DB password')
MDBNAME = addon.getSetting('Music-DB name')
MDBIP = addon.getSetting('Music-DB IP')
MDBPORT = addon.getSetting('Music-DB port')

kodi_version = int(xbmc.getInfoLabel("System.BuildVersion")[:2])


class Config(object):
    """Configure me so examples work
    
    Use me like this:
    
        mysql.connector.Connect(**Config.dbinfo())
    """

    if DATABASE_MYSQL == "false":
        DATABASE = 'Shows.db'
        USER = 'kodi'
        PASSWORD = 'admin'
        PORT = 3306

        CHARSET = 'utf8'
        UNICODE = True
        WARNINGS = True

        @classmethod
        def dbinfo(cls):
            return {
                'host': cls.HOST,
                'port': cls.PORT,
                'database': cls.DATABASE,
                'user': cls.USER,
                'password': cls.PASSWORD,
                'charset': cls.CHARSET,
                'use_unicode': cls.UNICODE,
                'get_warnings': cls.WARNINGS,
                }

    else:
        DATABASETYPE = ""
        CHARSET = 'utf8'
        UNICODE = True
        WARNINGS = True
        BUFFERED = True

        # Databases
        @classmethod
        def dataBaseVal(cls):

            DBValuses = ["SERNAME", "PASSWORD", "NAME", "IP", "PORT"]

            if cls.DATABASETYPE == "KMovies":
                DBValuses = [KMODBUSERNAME, KMODBPASSWORD, KMODBNAME, KMODBIP, KMODBPORT]
            elif cls.DATABASETYPE == "KMusic":
                DBValuses = [KMDBUSERNAME, KMDBPASSWORD, KMDBNAME, KMDBIP, KMDBPORT]
            elif cls.DATABASETYPE == "Movies":
                DBValuses = [MOVDBUSERNAME, MOVDBPASSWORD, MOVDBNAME, MOVDBIP, MOVDBPORT]
            elif cls.DATABASETYPE == "TVShows":
                DBValuses = [TVSDBUSERNAME, TVSDBPASSWORD, TVSDBNAME, TVSDBIP, TVSDBPORT]
            elif cls.DATABASETYPE == "Music":
                DBValuses = [MDBUSERNAME, MDBPASSWORD, MDBNAME, MDBIP, MDBPORT]

            return {
                'user': DBValuses[0],
                'password': DBValuses[1],
                'database': DBValuses[2],
                'host': DBValuses[3],
                'port': DBValuses[4],
                'charset': cls.CHARSET,
                'use_unicode': cls.UNICODE,
                'get_warnings': cls.WARNINGS,
                'buffered': cls.BUFFERED,
                }


def musicDatabase(strAlbumName, strArtistName, strSongTitle, strPath, strURL, iTrack, iDuration, strArtPath, tFileModTime=None):
    strPath = fileSys.completePath(os.path.join(STRM_LOC, strPath))

    # Write to music db and get id's
    iRoleID = writeRole("Artist")
    iPathID = writePath(strPath)
    iArtistID = writeArtist(strArtistName)
    iGenreID = writeGenre('osmosis')
    iAlbumID = writeAlbums(strAlbumName, strArtistName)
    iSongID = writeSong(iPathID, iAlbumID, strArtistName, strSongTitle, iDuration, iTrack, tFileModTime)
    iSongArtistID = writeSongArtist(iArtistID, iSongID, 1, strArtistName, 0)
    writeSongGenre(iGenreID, iSongID)
    writeAlbumArtist(iArtistID, iAlbumID, strArtistName)
    writeThump(iArtistID, "artist", "thumb", strArtPath)
    writeThump(iAlbumID, "album", "thumb", strArtPath)

    if DATABASE_MYSQL == "false":
        if not xbmcvfs.exists(MusicDB_LOC):
            createMusicDB()
    elif not valDB('Music'):
        createMusicDB()

    writeIntoSongTable(strSongTitle, iSongID, strArtistName, strAlbumName, iAlbumID, strPath, iPathID, strURL, iRoleID, iArtistID, iSongArtistID, "F")


def createMusicDB():
    try:
        con, cursor = openDB(MusicDB_LOC, 'Music')

        query = "CREATE TABLE songs (id INTEGER PRIMARY KEY{}, \
                strSongTitle VARCHAR(255), \
                strArtistName VARCHAR(255), \
                strAlbumName VARCHAR(255), \
                strPath TEXT, \
                strURL TEXT, \
                roleID INTEGER, \
                pathID INTEGER, \
                artistID INTEGER, \
                albumID INTEGER, \
                songID INTEGER, \
                songArtistRel INTEGER, \
                delSong CHAR(1));"

        query = query.format('' if DATABASE_MYSQL == "false" else ' AUTO_INCREMENT')

        cursor.execute(query)
        con.commit()
    finally:
        cursor.close()
        con.close()


def writeRole(strRole):
    selectQuery = "SELECT idRole FROM role WHERE strRole LIKE '{}';"
    selectArgs = (strRole,)
    insertQuery = "INSERT INTO role (strRole) VALUES ('{}');"
    insertArgs = (strRole,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writePath(strPath):
    selectStrPath = strPath if DATABASE_MYSQL == "false" else strPath.replace('\\', '\\\\\\\\')
    insertStrPath = strPath if DATABASE_MYSQL == "false" else strPath.replace('\\', '\\\\')

    selectQuery = "SELECT idPath FROM path WHERE strPath LIKE '{}';"
    selectArgs = (selectStrPath,)
    insertQuery = "INSERT INTO path (strPath) VALUES ('{}');"
    insertArgs = (insertStrPath,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeArtist(strArtist):
    selectQuery = "SELECT idArtist FROM artist WHERE strArtist LIKE '{}';"
    selectArgs = (strArtist,)
    insertQuery = "INSERT INTO artist (strArtist) VALUES ('{}');"
    insertArgs = (strArtist,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeGenre(strGenre):
    selectQuery = "SELECT idGenre FROM genre WHERE strGenre LIKE '{}';"
    selectArgs = (strGenre,)
    insertQuery = "INSERT INTO genre (strGenre) VALUES ('{}');"
    insertArgs = (strGenre,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeAlbums(strAlbum, strArtist, strReleaseType='album'):
    artistCol = "strArtistDisp" if kodi_version >= 18 else "strArtists"

    selectQuery = "SELECT idAlbum FROM album WHERE strAlbum LIKE '{}';"
    selectArgs = (strAlbum,)
    insertQuery = "INSERT INTO album (strAlbum, " + artistCol + ", strReleaseType, strGenres) VALUES ('{}', '{}', '{}', '{}');"
    insertArgs = (strAlbum, strArtist, strReleaseType, 'osmosis')

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeSong(iPathID, iAlbumID, strArtist, strTitle, iDuration, iTrack, tFileModTime):
    tDateAdded = datetime.datetime.fromtimestamp(tFileModTime) if tFileModTime else datetime.datetime.now()
    strDateAdded = tDateAdded.strftime("%Y-%m-%d %H:%M:%S")
    iYear = int(datetime.datetime.now().strftime("%Y"))
    artistCol = "strArtistDisp" if kodi_version >= 18 else "strArtists"
    strTitle = stringUtils.invCommas(strTitle)
    strFileName = stringUtils.cleanStrmFilesys(strTitle)
    strFileName += ".strm"

    selectQuery = "SELECT idSong FROM song WHERE {} LIKE '{}' AND strTitle LIKE '{}';"
    selectArgs = (artistCol, strArtist, strTitle)
    insertQuery = "INSERT INTO song (iYear, dateAdded, idAlbum, idPath, " + artistCol + ", strTitle, strFileName, iTrack, strGenres, iDuration, iTimesPlayed, iStartOffset, iEndOffset, userrating, comment, mood, votes)"
    insertQuery += " VALUES ({}, '{}', {}, {}, '{}', '{}', '{}', {}, '{}', {}, {}, {}, {}, {}, '{}', '{}', {});"
    insertArgs = (iYear, strDateAdded, iAlbumID, iPathID, strArtist, strTitle, strFileName, iTrack, 'osmosis', iDuration, 0, 0, 0, 0, 'osmosis', 'osmosis', 0)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeSongArtist(iArtistID, iSongID, iRoleID, strArtist, iOrderID):
    selectQuery = "SELECT idSong FROM song_artist WHERE idSong = {};"
    selectArgs = (iSongID,)
    insertQuery = "INSERT INTO song_artist (idArtist, idSong, idRole, iOrder, strArtist) VALUES ('{}', '{}', '{}', '{}', '{}');"
    insertArgs = (iArtistID, iSongID, iRoleID, iOrderID, strArtist)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeSongGenre(genreID, songID):
    selectQuery = "SELECT idSong FROM song_genre WHERE idGenre='{}' and idSong='{}';"
    selectArgs = (genreID, songID)
    insertQuery = "INSERT INTO song_genre (idGenre, idSong, iOrder) VALUES ('{}', '{}', '{}');"
    insertArgs = (genreID, songID, 0)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeAlbumArtist(iArtistID, iAlbumID, strArtist):
    selectQuery = "SELECT idAlbum FROM album_artist WHERE idAlbum = {};"
    selectArgs = (iAlbumID,)
    insertQuery = "INSERT INTO album_artist (idArtist, idAlbum, iOrder, strArtist) VALUES ('{}', '{}', '{}', '{}');"
    insertArgs = (iArtistID, iAlbumID, 0, strArtist)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeThump(iMediaID, strMediaType, strImageType, strArtPath):
    selectQuery = "SELECT media_id FROM art WHERE media_id = {} AND media_type LIKE '{}';"
    selectArgs = (iMediaID, strMediaType)
    insertQuery = "INSERT INTO art (media_id, media_type, type, url) VALUES ('{}', '{}', '{}', '{}');"
    insertArgs = (iMediaID, strMediaType, strImageType, strArtPath)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeIntoSongTable (strSongTitle, iSongID, strArtistName, strAlbumName, iAlbumID, strPath, iPathID, strURL, iRoleID, iArtistID, iSongArtistID, strDelSong):
    strPath = strPath if DATABASE_MYSQL == "false" else strPath.replace('\\', '\\\\')
    strSongTitle = strSongTitle.replace("'", "''")

    selectQuery = "SELECT id FROM songs WHERE songID = {} AND artistID = {} AND albumID = {};"
    selectArgs = (iSongID, iArtistID, iAlbumID)
    insertQuery = "INSERT INTO songs (strSongTitle, songID, strArtistName, strAlbumName, albumID, strPath, pathID, strURL, roleID, artistID, songArtistRel, delSong) VALUES ('{}', {}, '{}', '{}', {}, '{}', {}, '{}', {}, {}, '{}', '{}');"
    insertArgs = (strSongTitle, iSongID, strArtistName, strAlbumName, iAlbumID, strPath, iPathID, strURL, iRoleID, iArtistID, iSongArtistID, strDelSong)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs, MusicDB_LOC)


def manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs, database=KMDBPATH):
    dID = None
    try:
        con, cursor = openDB(database, 'KMusic' if database == KMDBPATH else 'Music')

        if selectArgs:
            selectQuery = selectQuery.format(*selectArgs)
            cursor.execute(selectQuery)
        else:
            cursor.execute(selectQuery)

        searchResult = cursor.fetchone()

        if not searchResult:
            insertQuery = insertQuery.format(*insertArgs)
            cursor.execute(insertQuery)
            con.commit()
            dID = cursor.lastrowid
        else:
            dID = searchResult[0]
    finally:
        cursor.close()
        con.close()

    return dID


def valDB(database):
    con, cursor = openDB(database, database)

    if DATABASE_MYSQL == "false":
        cursor.execute("SELECT * FROM sqlite_master WHERE name LIKE 'stream_ref' and type LIKE 'table';")
        result = cursor.fetchall()

        cursor.close()
        con.close()
        return True if len(result) == 1 else False
    else:
        if database == "Music":
            query = "SHOW TABLES LIKE 'songs';"
        else:
            query = "SHOW TABLES LIKE 'stream_ref';"

        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        con.close()
        return True if result else False


def writeMovie(movieList):
    dbMovieList = []

    if DATABASE_MYSQL == "false":
        if not xbmcvfs.exists(MODBPATH):
            createMovDB()
        elif not valDB(MODBPATH):
            xbmcvfs.delete(MODBPATH)
            createMovDB()
    else:
        if not valDB('Movies'):
            createMovDB()

    for entry in movieList:
        try:
            kmovName = kmovieExists(entry.get('title'), entry.get('imdbnumber'))
            movID = movieExists(kmovName, entry.get('path'))
            if movID is not None:
                movieStreamExists(movID, entry.get('provider'), entry.get('url'))
                dbMovieList.append({'path': entry.get('path'), 'title': kmovName, 'movieID': movID, 'provider': entry.get('provider')})
        except IOError as (errno, strerror):
            print ("I/O error({0}): {1}").format(errno, strerror)
        except ValueError:
            print ("No valid integer in line.")
        except:
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1]) + (". See your Kodi.log!"))
            utils.addon_log("Unexpected error: " + str(movID) + " " + str(i[3]) + " " + str(url))
            print ("Unexpected error:"), sys.exc_info()[1]
            pass

    return dbMovieList


def writeShow(episode):
    dbEpisode = None

    if DATABASE_MYSQL == "false":
        if not xbmcvfs.exists(SHDBPATH):
            createShowDB()
        elif not valDB(SHDBPATH):
            xbmcvfs.delete(SHDBPATH)
            createShowDB()
    else:
        if not valDB('TVShows'):
            createShowDB()

    if episode is not None:
        try:
            showID = showExists(episode.get('tvShowTitle'), episode.get('path'))
            if showID is not None:
                episodeStreamExists(showID, episode.get('strSeasonEpisode'), episode.get('provider'), episode.get('url'))
                dbEpisode = {'path': episode.get('path'), 'tvShowTitle': episode.get('tvShowTitle'), 'showID': showID, 'strSeasonEpisode': episode.get('strSeasonEpisode')}
        except IOError as (errno, strerror):
            print ("I/O error({0}): {1}").format(errno, strerror)
        except ValueError:
            print ("No valid integer in line.")
        except:
            guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1]) + (". See your Kodi.log!"))
            utils.addon_log("Unexpected error: " + str(showID) + " " + str(i[4]) + " " + str(url))
            print ("Unexpected error:"), sys.exc_info()[1]
            pass

    return dbEpisode


def createMovDB():
    try:
        con, cursor = openDB(MODBPATH, 'Movies')

        sql_strm_ref = "CREATE TABLE stream_ref (id INTEGER PRIMARY KEY{}, mov_id INTEGER NOT NULL, provider TEXT NOT NULL, url TEXT NOT NULL);"
        sql_movtable = "CREATE TABLE movies (id INTEGER PRIMARY KEY{}, title TEXT NOT NULL, filePath TEXT NOT NULL);"

        sql_strm_ref = sql_strm_ref.format('' if DATABASE_MYSQL == "false" else ' AUTO_INCREMENT')
        sql_movtable = sql_movtable.format('' if DATABASE_MYSQL == "false" else ' AUTO_INCREMENT')

        cursor.execute(sql_strm_ref)
        cursor.execute(sql_movtable)
        con.commit()
    finally:
        cursor.close()
        con.close()


def createShowDB():
    try:
        con, cursor = openDB(SHDBPATH, 'TVShows')

        sql_strm_ref = "CREATE TABLE stream_ref (id INTEGER PRIMARY KEY{}, show_id INTEGER NOT NULL, seasonEpisode TEXT NOT NULL, provider TEXT NOT NULL, url TEXT NOT NULL);"
        sql_showtable = "CREATE TABLE shows (id INTEGER PRIMARY KEY{}, showTitle TEXT NOT NULL, filePath TEXT NOT NULL);"

        sql_strm_ref = sql_strm_ref.format('' if DATABASE_MYSQL == "false" else ' AUTO_INCREMENT')
        sql_showtable = sql_showtable.format('' if DATABASE_MYSQL == "false" else ' AUTO_INCREMENT')

        cursor.execute(sql_strm_ref)
        cursor.execute(sql_showtable)
        con.commit()
    finally:
        cursor.close()
        con.close()


def kmovieExists(title, imdbnumber):
    dbMovieName = None
    try:
        con, cursor = openDB(KMODBPATH, 'KMovies')

        # title = stringUtils.invCommas(title)
        cursor.execute("SELECT strFileName FROM movie_view WHERE uniqueid_value LIKE '{}';".format(imdbnumber))

        dbMovieName = cursor.fetchone()

        if dbMovieName is None:
            dbMovieName = title
        else:
            dbMovieName = dbMovieName[0]
        dbMovieName = stringUtils.cleanTitle(dbMovieName)
    finally:
        cursor.close()
        con.close()

    return dbMovieName


def movieExists(title, path):
    dbMovieID = None
    try:
        con, cursor = openDB(MODBPATH, 'Movies')

        title = stringUtils.invCommas(title)

        cursor.execute("SELECT id, title FROM movies WHERE title LIKE '{}';".format(title))
        dbMovie = cursor.fetchone()

        if dbMovie is None:
            path = fileSys.completePath(path) if DATABASE_MYSQL == "false" else fileSys.completePath(path).replace('\\', '\\\\')
            path = stringUtils.invCommas(path)
            cursor.execute("INSERT INTO movies (title, filePath) VALUES ('{}', '{}');".format(title, path))
            con.commit()
            dbMovieID = cursor.lastrowid
        else:
            dbMovieID = dbMovie[0]
    finally:
        cursor.close()
        con.close()

    return dbMovieID


def movieStreamExists(movieID, provider, url):
    try:
        con, cursor = openDB(MODBPATH, 'Movies')

        if url.find("?url=plugin") != -1:
            url = url.strip().replace("?url=plugin", "plugin", 1)

        cursor.execute("SELECT mov_id, url FROM stream_ref WHERE mov_id = {} AND provider LIKE '{}';".format(movieID, provider))
        dbMovie = cursor.fetchone()

        if dbMovie is None:
            cursor.execute("INSERT INTO stream_ref (mov_id, provider, url) VALUES ({}, '{}', '{}');".format(movieID, provider, url))
            con.commit()
        else:
            if str(dbMovie[1]) != url:
                cursor.execute("UPDATE stream_ref SET url='{}' WHERE mov_id = {};".format(url, movieID))
                con.commit()
    finally:
        cursor.close()
        con.close()


def showExists(title, path):
    dbShowID = None
    try:
        con, cursor = openDB(SHDBPATH, 'TVShows')

        title = stringUtils.invCommas(title)

        cursor.execute("SELECT id, showTitle FROM shows WHERE showTitle LIKE '{}';".format(title))
        dbShow = cursor.fetchone()

        if dbShow is None:
            path = fileSys.completePath(path) if DATABASE_MYSQL == "false" else fileSys.completePath(path).replace('\\', '\\\\')
            path = stringUtils.invCommas(path)
            cursor.execute("INSERT INTO shows (showTitle, filePath) VALUES ('{}', '{}');".format(title, path))
            con.commit()
            dbShowID = cursor.lastrowid
        else:
            dbShowID = dbShow[0]
    finally:
        cursor.close()
        con.close()

    return dbShowID


def episodeStreamExists(showID, seEp, provider, url):
    try:
        con, cursor = openDB(SHDBPATH, 'TVShows')

        if url.find("?url=plugin") > -1:
            url = url.strip().replace("?url=plugin", "plugin", 1)

        cursor.execute("SELECT show_id, url FROM stream_ref WHERE show_id = {} AND seasonEpisode LIKE '{}' AND provider LIKE '{}';".format(showID, seEp, provider))
        dbShow = cursor.fetchone()

        if dbShow is None:
            cursor.execute("INSERT INTO stream_ref (show_id, seasonEpisode, provider, url) VALUES ({}, '{}', '{}', '{}');".format(showID, seEp, provider, url))
            con.commit()
        else:
            if str(dbShow[1]) != url:
                cursor.execute("UPDATE stream_ref SET url = '{}' WHERE show_id = {} AND seasonEpisode LIKE '{}' AND provider LIKE '{}';".format(url, showID, seEp, provider))
                con.commit()
    finally:
        cursor.close()
        con.close()


def getVideo(ID, seasonEpisode=None):
    provList = None

    try:
        args = {'sqliteDB': MODBPATH, 'mysqlDB': 'Movies'} if seasonEpisode is None else {'sqliteDB': SHDBPATH, 'mysqlDB': 'TVShows'}
        con, cursor = openDB(**args)

        if seasonEpisode is None:
            query = "SELECT url, provider FROM stream_ref WHERE mov_id = {};"
            args = (ID,)
        else:
            query = "SELECT url, provider FROM stream_ref WHERE show_id = {} AND seasonEpisode LIKE '{}';"
            args = (ID, seasonEpisode)

        cursor.execute(query.format(*args))
        provList = cursor.fetchall()
    finally:
        cursor.close()
        con.close()

    return provList


def getPlayedURLResumePoint(args):
    urlResumePoint = None

    try:
        con, cursor = openDB(KMODBPATH, 'KMovies')

        query = "SELECT timeInSeconds, totalTimeInSeconds, idBookmark FROM bookmark INNER JOIN files on files.idFile = bookmark.idFile"
        if(args.get('url', None)):
            url = stringUtils.invCommas(args.get('url'))
            query += "  WHERE files.strFilename LIKE '{}';".format(url)
        else:
            filename = stringUtils.invCommas(args.get('filename'))
            path = stringUtils.invCommas(args.get('path'))
            query += " INNER JOIN path on path.idPath = files.idPath WHERE files.strFilename LIKE '{}' AND path.strPath LIKE '{}';".format(filename, path)

        cursor.execute(query)
        urlResumePoint = cursor.fetchone()
    finally:
        cursor.close()
        con.close()

    return urlResumePoint


def delBookMark(bookmarkID, fileID):
    try:
        con, cursor = openDB(KMODBPATH, 'KMovies')

        selectquery = "SELECT idBookmark FROM bookmark WHERE {} = {};"
        deletequery = "DELETE FROM bookmark WHERE {} = {};"
        args = ('idFile', fileID)

        cursor.execute(selectquery.format(*args))
        dbbookmark = cursor.fetchone()

        if dbbookmark:
            cursor.execute(deletequery.format(*args))

        args = ('idBookmark', bookmarkID)
        cursor.execute(selectquery.format(*args))
        dbbookmark = cursor.fetchone()

        if dbbookmark:
            cursor.execute(deletequery.format(*args))

        con.commit()
    finally:
        cursor.close()
        con.close()


def getKodiMovieID(sTitle):
    dbMovie = None

    try:
        con, cursor = openDB(KMODBPATH, 'KMovies')

        sTitle = stringUtils.invCommas(sTitle)

        # c00 = title; c14 = genre
        cursor.execute("SELECT idMovie, idFile, premiered, c14 FROM movie WHERE c00 LIKE '{}';".format(sTitle))
        dbMovie = cursor.fetchone()
    finally:
        cursor.close()
        con.close()

    return dbMovie


def getKodiEpisodeID(sTVShowTitle, iSeason, iEpisode):
    dbEpisode = None

    try:
        con, cursor = openDB(KMODBPATH, 'KMovies')

        sTVShowTitle = stringUtils.invCommas(sTVShowTitle)

        # episode.c00 = title; episode.c05 = aired; episode.c12 = season; episode.c13 = episode; tvshow.c00 = title
        query = "SELECT episode.idEpisode, episode.idFile, episode.c00, episode.c05 FROM episode INNER JOIN tvshow ON tvshow.idShow = episode.idShow WHERE episode.c12 = {} and episode.c13 = {} and tvshow.c00 LIKE '{}';"

        cursor.execute(query.format(iSeason, iEpisode, sTVShowTitle))
        dbEpisode = cursor.fetchone()
    finally:
        cursor.close()
        con.close()

    return dbEpisode


def openDB(sqliteDB, mysqlDB):
    if DATABASE_MYSQL == "false":
        con = sqlite3.connect(str(os.path.join(sqliteDB)))
        con.text_factory = str
        cursor = con.cursor()
    else:
        Config.DATABASETYPE = mysqlDB
        Config.BUFFERED = True
        config = Config.dataBaseVal().copy()
        con = mysql.connector.Connect(**config)
        cursor = con.cursor()

    return con, cursor
