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

#Addon
addon_id = 'plugin.video.osmosis'
addon = xbmcaddon.Addon(addon_id)
ADDON_SETTINGS = addon.getAddonInfo('profile')
MusicDB_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'Musik.db'))
MODBPATH = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'Movies.db'))
SHDBPATH = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'Shows.db'))
MODBPATH_MYSQL = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'Movies'))
SHDBPATH_MYSQL = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'TVShows'))
STRM_LOC = xbmc.translatePath(os.path.join(addon.getSetting('STRM_LOC')))
DATABASE_MYSQL = addon.getSetting('USE_MYSQL')

#Databases
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

try:    
    kodi_version = int(xbmc.getInfoLabel("System.BuildVersion")[:2])
except:
    kodi_version = 17

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

        #Databases
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
    
def musicDatabase(pstrAlbumName, pstrArtistName, pstrSongTitle, pstrPath, purlLink, track, duration, artPath, fileModTime=None):
    path = fileSys.completePath(os.path.join(STRM_LOC, pstrPath))

    # Write to music db and get id's
    roleID = writeRole("Artist")
    pathID = writePath(path)
    artistID = writeArtist(pstrArtistName)
    genreID = writeGenre('osmosis')
    albumID = writeAlbums(pstrAlbumName,pstrArtistName)
    songID = writeSong(pathID, albumID, pstrArtistName, pstrSongTitle, duration, track, None)   
    songArtistRel = writeSongArtist(artistID, songID, 1, pstrArtistName, 0)
    writeSongGenre(genreID, songID)
    writeAlbumArtist(artistID, albumID,pstrArtistName)
    writeThump(artistID, "artist", "thumb", artPath)
    writeThump(albumID, "album", "thumb", artPath)
    
    if DATABASE_MYSQL == "false":
        if not xbmcvfs.exists(MusicDB_LOC):
            createMusicDB()
    elif not valDB('Music'):
        createMusicDB()

    writeIntoSongTable(pstrSongTitle, songID, pstrArtistName, pstrAlbumName, albumID, path, pathID, purlLink, roleID, artistID, songArtistRel, "F")

def createMusicDB():
    try:
        con, cursor = openDB(MusicDB_LOC, 'Music')

        query = "CREATE TABLE songs (id INTEGER PRIMARY KEY{}, \
                strSongTitle VARCHAR(30), \
                strArtistName VARCHAR(30), \
                strAlbumName VARCHAR(30), \
                strPath VARCHAR(30), \
                strURL VARCHAR(300), \
                roleID VARCHAR(30), \
                pathID VARCHAR(30), \
                artistID VARCHAR(30), \
                albumID VARCHAR(30), \
                songID VARCHAR(30), \
                songArtistRel VARCHAR(30), \
                delSong CHAR(1));"

        query = query.format('' if DATABASE_MYSQL == "false" else ' AUTO_INCREMENT')

        cursor.execute(query)
        con.commit()         
    except:
        pass
    finally:
        cursor.close()
        con.close()  

def writeIntoSongTable (pstrSongTitle, songID, pstrArtistName, pstrAlbumName, albumID, path, pathID, purlLink, roleID, artistID, songArtistRel, delSong):
    selectQuery = "SELECT id FROM songs WHERE songID='{}' AND artistID='{}' AND albumID='{}';"
    selectArgs =  (songID, artistID, albumID)
    insertQuery = "INSERT INTO songs (strSongTitle, songID, strArtistName, strAlbumName, albumID, strPath, pathID, strURL, roleID, artistID, songArtistRel, delSong) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');"
    path = path if DATABASE_MYSQL == "false" else path.replace('\\', '\\\\')
    insertArgs =  (pstrSongTitle.replace("'","''"), songID, pstrArtistName, pstrAlbumName, albumID, path, pathID, purlLink, roleID, artistID, songArtistRel, delSong)
    
    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs, MusicDB_LOC)
    
def writePath(path):
    selectQuery = "SELECT idPath FROM path WHERE strPath LIKE '{}';"
    selectArgs =  (path,) if DATABASE_MYSQL == "false" else (path).replace('\\', '\\\\')
    insertQuery = "INSERT INTO path (strPath) VALUES ('{}');"
    insertArgs =  (path,) if DATABASE_MYSQL == "false" else (path).replace('\\', '\\\\')

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeAlbums(album, artist, firstReleaseType='album'):
    lastScraped = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    artistCol = "strArtistDisp" if kodi_version >= 18 else "strArtists"
    selectQuery = "SELECT idAlbum FROM album WHERE strAlbum LIKE '{}';"
    selectArgs =  (album)
    insertQuery = "INSERT INTO album (strAlbum, {}, strReleaseType, strGenres)".format(artistCol)
    insertQuery = (insertQuery + " VALUES ('{}', '{}', '{}', '{}');")
    insertArgs =  (album, artist, firstReleaseType, 'osmosis')
    
    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeSong(pathID, albumID, artist, songName, duration, track, fileModTime):
    dateAdded = datetime.datetime.fromtimestamp(fileModTime) if fileModTime else datetime.datetime.now()
    dateAdded = dateAdded.strftime("%Y-%m-%d %H:%M:%S")
    dateYear = int(datetime.datetime.now().strftime("%Y"))
    artistCol = "strArtistDisp" if kodi_version >= 18 else "strArtists"

    selectQuery = "SELECT idSong FROM song WHERE {}".format(artistCol) + " LIKE '{}' AND strTitle LIKE '{}';"
    selectArgs =  (artist, songName.replace("'","''"))
    songNameFile = stringUtils.cleanStrmFilesys(songName)
    insertQuery = "INSERT INTO song (iYear, dateAdded, idAlbum, idPath, {}, strTitle, strFileName, iTrack, strGenres, iDuration, iTimesPlayed, iStartOffset, iEndOffset, userrating, comment, mood, votes)".format(artistCol)
    insertQuery =  (insertQuery +" VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');")
    insertArgs =  (dateYear, dateAdded, albumID, pathID, artist, songName.replace("'","''"), songNameFile.replace("'","''") + ".strm", track, 'osmosis', duration, 0, 0, 0, 0, 'osmosis', 'osmosis', 0,)
    
    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeRole(strRole):
    selectQuery = "SELECT idRole FROM role WHERE strRole LIKE '{}';"
    selectArgs =  (strRole,)
    insertQuery = "INSERT INTO role (strRole) VALUES ('{}');"
    insertArgs =  (strRole,)
    
    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeArtist(strArtist):
    selectQuery = "SELECT idArtist FROM artist WHERE strArtist LIKE '{}';"
    selectArgs =  (strArtist,)
    insertQuery = "INSERT INTO artist (strArtist) VALUES ('{}');"
    insertArgs =  (strArtist,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeGenre(strGenre):
    selectQuery = "SELECT idGenre FROM genre WHERE strGenre LIKE '{}';"
    selectArgs =  (strGenre,)
    insertQuery = "INSERT INTO genre (strGenre) VALUES ('{}');"
    insertArgs =  (strGenre,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)
           
def writeSongArtist(artistID, songID, roleID, pstrAartistName, orderID):
    selectQuery = "SELECT idSong FROM song_artist WHERE idSong='{}';"
    selectArgs =  (songID)
    insertQuery = "INSERT INTO song_artist (idArtist, idSong, idRole, iOrder, strArtist) VALUES ('{}', '{}', '{}', '{}', '{}');"
    insertArgs =  (artistID, songID, roleID, orderID, pstrAartistName)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeSongGenre(genreID, songID):
    selectQuery = "SELECT idSong FROM song_genre WHERE idGenre='{}' and idSong='{}';"
    selectArgs =  (genreID, songID)
    insertQuery = "INSERT INTO song_genre (idGenre, idSong, iOrder) VALUES ('{}', '{}', '{}');"
    insertArgs =  (genreID, songID, 0)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeAlbumArtist(artistID, albumID,pstrAartistName):
    selectQuery = "SELECT idAlbum FROM album_artist WHERE idAlbum='{}';"
    selectArgs =  (albumID)
    insertQuery = "INSERT INTO album_artist (idArtist, idAlbum, iOrder, strArtist) VALUES ('{}', '{}', '{}', '{}');"
    insertArgs =  (artistID, albumID, 0, pstrAartistName)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeThump(mediaId, mediaType, imageType, artPath):
    selectQuery = "SELECT media_id FROM art WHERE media_type LIKE '{}' AND media_id='{}';"
    selectArgs =  (mediaType, mediaId)
    insertQuery = "INSERT INTO art (media_id, media_type, type, url) VALUES ('{}', '{}', '{}', '{}');"
    insertArgs =  (mediaId, mediaType,imageType, artPath)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs, database=KMDBPATH):
    dID = None

    try:
        con, cursor = openDB(database, 'KMusic' if database == KMDBPATH else 'Music')    

        try:		
            if selectArgs:
                cursor.execute(selectQuery.format(selectArgs,))
                searchResult = cursor.fetchone()
            else:
                cursor.execute(selectQuery)
                searchResult = cursor.fetchone()

        except:
            if selectArgs:
                cursor.execute(selectQuery.format(*(selectArgs)))
                searchResult = cursor.fetchone()
            else:
                cursor.execute(selectQuery)
                searchResult = cursor.fetchone()
        try:
            if not searchResult :
                cursor.execute(insertQuery.format(insertArgs,))
                con.commit()
                dID = cursor.lastrowid
            else:
                dID = searchResult[0]

        except:
            if not searchResult :
                cursor.execute(insertQuery.format(*(insertArgs)))
                con.commit()
                dID = cursor.lastrowid
            else:
                dID = searchResult[0]
                
    except IOError as (errno, strerror):
        print ("I/O error({0}): {1}").format(errno, strerror)
    except ValueError:
        print ("No valid integer in line.")
    except:
        guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". See your Kodi.log!"))
        utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
        print ("Unexpected error:"), sys.exc_info()[1]
    
    finally:
        cursor.close()
        con.close()
    
    return dID

def writeMoviePath(path):
    pathID = None
    try:
        con, cursor = openDB(MODBPATH, 'Movies')

        cursor.execute("SELECT idPath FROM path WHERE strPath LIKE '{}';".format(fileSys.completePath(path)),)
        result = cursor.fetchone()
        if not result:
            query = "INSERT INTO path (strPath) VALUES ('{}');"
            cursor.execute(query, (fileSys.completePath(path),))
            con.commit()
            pathID = cursor.lastrowid
        else:
            cursor.execute("SELECT idPath FROM path WHERE strPath LIKE '{}';".format(fileSys.completePath(path),))                
            pathID = cursor.fetchone()[0]
    except:
        pass
    finally:
        cursor.close()
        con.close()

    return pathID

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

    db = MODBPATH if DATABASE_MYSQL == "false" else MODBPATH_MYSQL
    table = MODBPATH if DATABASE_MYSQL == "false" else 'Movies'

    if not xbmcvfs.exists(db):
        createMovDB()
    elif not valDB(table):
        xbmcvfs.delete(db)
        createMovDB() 
        
    for i in movieList:
        if i:
            try:
                movID = movieExists(i[1], i[0])
                movieStreamExists(movID, i[3], i[2])
                if not movID in dbMovieList:
                    dbMovieList.append([ i[0], i[1], movID, i[3]])
            except IOError as (errno, strerror):
                print ("I/O error({0}): {1}").format(errno, strerror)
            except ValueError:
                print ("No valid integer in line.") 
            except:
                guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". See your Kodi.log!"))
                utils.addon_log("Unexpected error: " + str(movID) +" "+ str(i[3]) + " "+ str( url))
                print ("Unexpected error:"), sys.exc_info()[1]
                pass

    return dbMovieList

def writeShow(showList):
    dbShowList = []
    if DATABASE_MYSQL == "false":
        if not xbmcvfs.exists(SHDBPATH):
            createShowDB()
        elif not valDB(SHDBPATH):
            xbmcvfs.delete(SHDBPATH)
            createShowDB()       
    else:
        if not xbmcvfs.exists(SHDBPATH_MYSQL):
            createShowDB()
        elif not valDB('TVShows'):
            xbmcvfs.delete(SHDBPATH_MYSQL)
            createShowDB()
        
    for i in showList:
        if i:
            try:
                showID = showExists(i[4], i[0])
                episodeStreamExists(showID, i[1] + i[2], i[5], i[3])
                if not showID in dbShowList:
                    dbShowList.append([i[0], i[4], showID, i[1], i[2]])
            except IOError as (errno, strerror):
                print ("I/O error({0}): {1}").format(errno, strerror)
            except ValueError:
                print ("No valid integer in line.") 
            except:
                guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". See your Kodi.log!"))
                utils.addon_log("Unexpected error: " + str(showID) +" "+ str(i[4]) + " "+ str( url))
                print ("Unexpected error:"), sys.exc_info()[1]
                pass

    return dbShowList

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
    except:
        pass
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
    except:
        pass
    finally:
        cursor.close()
        con.close()
    
def movieExists(title, path):
    dbMovieID = None
    try:
        con, cursor = openDB(MODBPATH, 'Movies')
        path = fileSys.completePath(path) if DATABASE_MYSQL == "false" else fileSys.completePath(path).replace('\\', '\\\\') 
        dID = None

        cursor.execute("SELECT id, title FROM movies WHERE title LIKE '{}';".format(title,))
        dbMovie = cursor.fetchone()            
        if dbMovie is None:
            cursor.execute("INSERT INTO movies (title, filePath) VALUES ('{}', '{}');".format(title, path,))
            con.commit()
            dbMovieID = cursor.lastrowid
        else:
            dbMovieID = dbMovie[0]
    except:
        pass
    finally:
        cursor.close()
        con.close()

    return dbMovieID
 
def movieStreamExists(movieID, provider, url):
    try:
        con, cursor = openDB(MODBPATH, 'Movies')

        dbMovie = None

        if url.find("?url=plugin") != -1:
            url = url.strip().replace("?url=plugin", "plugin", 1)

        query = "SELECT mov_id, url FROM stream_ref WHERE mov_id='{}' AND provider LIKE '{}';"
        cursor.execute(query.format(movieID, provider,))
        dbMovie = cursor.fetchone()
        
        if dbMovie is None:
            cursor.execute("INSERT INTO stream_ref (mov_id, provider, url) VALUES ('{}', '{}', '{}');".format(movieID, provider, url,))
            con.commit()
        else:
            if str(entry[1]) != url:
                cursor.execute("UPDATE stream_ref SET url='{}' WHERE mov_id='{}';".format(url, movieID,))
                con.commit() 
    except:
        pass
    finally:
        cursor.close()
        con.close()

def showExists(title, path):
    dbShowID = None
    try:
        con, cursor = openDB(SHDBPATH, 'TVShows')

        cursor.execute("SELECT id, showTitle FROM shows WHERE showTitle LIKE '{}';".format(title,))
        dbShow = cursor.fetchone()
        if dbShow is None:
            path = fileSys.completePath(path)
            cursor.execute("INSERT INTO shows (showTitle, filePath) VALUES ('{}', '{}');".format(title, path,))
            con.commit()
            dbShowID = cursor.lastrowid
        else:
            dbShowID = dbShow[0]
    except:
        pass
    finally:
        cursor.close()
        con.close()

    return dbShowID

def episodeStreamExists(showID, seEp, provider, url):
    try:
        con, cursor = openDB(SHDBPATH, 'TVShows')

        dbShow = None

        if url.find("?url=plugin") > -1:
            url = url.strip().replace("?url=plugin", "plugin", 1)
        query = "SELECT show_id, url FROM stream_ref WHERE show_id='{}' AND seasonEpisode LIKE '{}' AND provider LIKE '{}';" 
        cursor.execute(query.format(showID, seEp, provider,))
        dbShow = cursor.fetchone()
        
        if dbShow is None:
            query = "INSERT INTO stream_ref (show_id, seasonEpisode, provider, url) VALUES ('{}', '{}', '{}', '{}');"
            cursor.execute(query.format(showID, seEp, provider, url,))
            con.commit()
        else:
            if str(dbShow[1]) != url:
                query = "UPDATE stream_ref SET url='{}' WHERE show_id='{}' AND seasonEpisode LIKE '{}' AND provider LIKE '{}';"
                cursor.execute(query.format(url, showID, seEp, provider,))
                con.commit()
    except:
        pass
    finally:
        cursor.close()
        con.close()
    
def getVideo(ID, seasonEpisode=None):
    provList = None

    try:    
        args = {'sqliteDB': MODBPATH, 'mysqlDB': 'Movies'} if seasonEpisode is None else {'sqliteDB': SHDBPATH, 'mysqlDB': 'TVShows'}
        con, cursor = openDB(**args)
                
        if seasonEpisode is None:
            query = "SELECT url, provider FROM stream_ref WHERE mov_id='{}';"
            args = (ID,)
        else:
            query = "SELECT url, provider FROM stream_ref WHERE show_id='{}' AND seasonEpisode LIKE '{}';"
            args = (ID, seasonEpisode)
    
        cursor.execute(query.format(*args))      
        provList = cursor.fetchall()
    except:
        pass
    finally:
        cursor.close()
        con.close()

    return provList    

def getPlayedURLResumePoint(url): 
    urlResumePoint = None

    try:
        con, cursor = openDB(KMODBPATH, 'KMovies')

        query = "SELECT idFile FROM files WHERE strFilename LIKE '{}';"
        args =  (url)

        cursor.execute(query.format(args))
        dbfile = cursor.fetchone()
        if dbfile:
            dbfileID = dbfile[0]
            query = "SELECT timeInSeconds, totalTimeInSeconds, idBookmark FROM bookmark WHERE idFile='{}';"
            args =  (dbfileID)
            cursor.execute(query.format(args))
            urlResumePoint = cursor.fetchone()
    except:
        pass
    finally:
        cursor.close()
        con.close()

    return urlResumePoint

def delBookMark(bookmarkID, fileID):
    try:
        con, cursor = openDB(KMODBPATH, 'KMovies')

        selectquery = "SELECT idBookmark FROM bookmark WHERE {0[0]} = {0[1]};"
        deletequery = "DELETE FROM bookmark WHERE {0[0]} = {0[1]};"
        args = ('idFile', fileID)

        cursor.execute(selectquery.format(args))
        dbbookmark = cursor.fetchone()

        if dbbookmark:
            cursor.execute(deletequery.format(args))

        args = ('idBookmark', bookmarkID)
        cursor.execute(selectquery.format(args))
        dbbookmark = cursor.fetchone()

        if dbbookmark:
            cursor.execute(deletequery.format(args))

        con.commit()
    except:
        pass
    finally:
        cursor.close()
        con.close()

def getKodiMovieID(sTitle):
    dbMovie = None

    try:
        con, cursor = openDB(KMODBPATH, 'KMovies')

        # c00 = title; c14 = genre
        query = "SELECT idMovie, idFile, premiered, c14 FROM movie WHERE c00 LIKE '{}';"
        args = (sTitle)
        
        cursor.execute(query.format(args))
        dbMovie = cursor.fetchone()
    except:
        pass
    finally:
        cursor.close()
        con.close()

    return dbMovie

def getKodiEpisodeID(sTVShowTitle, iSeason, iEpisode):
    dbEpisode = None

    try:
        con, cursor = openDB(KMODBPATH, 'KMovies')

        # episode.c00 = title; episode.c05 = aired; episode.c12 = season; episode.c13 = episode; tvshow.c00 = title
        query = "SELECT episode.idEpisode, episode.idFile, episode.c00, episode.c05 FROM episode INNER JOIN tvshow ON tvshow.idShow = episode.idShow WHERE episode.c12 = '{}' and episode.c13 = '{}' and tvshow.c00 LIKE '{}';" 
        args = (iSeason, iEpisode, sTVShowTitle)
        
        cursor.execute(query.format(*args))
        dbEpisode = cursor.fetchone()
    except:
        pass
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
