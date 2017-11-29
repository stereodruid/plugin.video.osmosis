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

# -*- coding: utf-8 -*-

import os
import sys
import time, datetime
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP
import SimpleDownloader as downloader
from modules import stringUtils
from modules import guiTools
from modules import fileSys
import xbmc
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs
import sqlite3
import mysql.connector
import utils

#Addon
addnon_id = 'plugin.video.osmosis'
addon = xbmcaddon.Addon(addnon_id)
addon_version = addon.getAddonInfo('version')
ADDON_NAME = addon.getAddonInfo('name')
REAL_SETTINGS = xbmcaddon.Addon(id=addnon_id)
ADDON_SETTINGS = REAL_SETTINGS.getAddonInfo('profile')
ADDON_PATH = REAL_SETTINGS.getAddonInfo('path')
MediaList_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'MediaList.xml'))
MusicDB_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'Musik.db'))
TVShowDB_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'TVShow.db'))
MODBPATH = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'Movies.db'))
SHDBPATH = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'Shows.db'))
MODBPATH_MYSQL = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'Movies'))
SHDBPATH_MYSQL = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'TVShows'))
STRM_LOC = xbmc.translatePath(os.path.join(REAL_SETTINGS.getSetting('STRM_LOC')))
DATABASE_MYSQL = REAL_SETTINGS.getSetting('USE_MYSQL')

#Databases
KMDBUSERNAME = REAL_SETTINGS.getSetting('KMusic-DB username')
KMDBPASSWORD = REAL_SETTINGS.getSetting('KMusic-DB password')
KMDBNAME = REAL_SETTINGS.getSetting('KMusic-DB name')
KMDBPATH = xbmc.translatePath(REAL_SETTINGS.getSetting('KMusic-DB path'))
KMDBIP = REAL_SETTINGS.getSetting('KMusic-DB IP')
KMDBPORT = REAL_SETTINGS.getSetting('KMusic-DB port')

KMODBUSERNAME = REAL_SETTINGS.getSetting('KMovie-DB username')
KMODBPASSWORD = REAL_SETTINGS.getSetting('KMovie-DB password')
KMODBNAME = REAL_SETTINGS.getSetting('KMovie-DB name')
KMODBPATH = xbmc.translatePath(REAL_SETTINGS.getSetting('KMovie-DB path'))
KMODBIP = REAL_SETTINGS.getSetting('KMovie-DB IP')
KMODBPORT = REAL_SETTINGS.getSetting('KMovie-DB port')

MOVDBUSERNAME = REAL_SETTINGS.getSetting('Movies-DB username')
MOVDBPASSWORD = REAL_SETTINGS.getSetting('Movies-DB password')
MOVDBNAME = REAL_SETTINGS.getSetting('Movies-DB name')
MOVDBIP = REAL_SETTINGS.getSetting('Movies-DB IP')
MOVDBPORT = REAL_SETTINGS.getSetting('Movies-DB port')

TVSDBUSERNAME = REAL_SETTINGS.getSetting('TV-Show-DB username')
TVSDBPASSWORD = REAL_SETTINGS.getSetting('TV-Show-DB password')
TVSDBNAME = REAL_SETTINGS.getSetting('TV-Show-DB name')
TVSDBIP = REAL_SETTINGS.getSetting('TV-Show-DB IP')
TVSDBPORT = REAL_SETTINGS.getSetting('TV-Show-DB port')

MDBUSERNAME = REAL_SETTINGS.getSetting('Music-DB username')
MDBPASSWORD = REAL_SETTINGS.getSetting('Music-DB password')
MDBNAME = REAL_SETTINGS.getSetting('Music-DB name')
MDBIP = REAL_SETTINGS.getSetting('Music-DB IP')
MDBPORT = REAL_SETTINGS.getSetting('Music-DB port')

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

try:
    import json
except:
    import simplejson as json

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
    
def musicDatabase(pstrAlbumName, pstrArtistName, pstrSongTitle, pstrPath, purlLink, track, duration, artPath):
    path = str(os.path.join(STRM_LOC, pstrPath))
    
    # Write to music db and get id's
    roleID = writeRole("Artist")
    pathID = writePath(path)
    artistID = writeArtist(pstrArtistName)
    genreID = writeGenre('osmosis')
    albumID = writeAlbums(pstrAlbumName,pstrArtistName)
    songID = writeSong(pathID, albumID, pstrArtistName, pstrSongTitle, duration, track)   
    songArtistRel = writeSongArtist(artistID, songID, 1, pstrArtistName, 0)
    writeSongGenre(genreID, songID)
    writeAlbumArtist(artistID, albumID,pstrArtistName)
    writeThump(artistID, "artist", "thumb", artPath)
    writeThump(albumID, "album", "thumb", artPath)
    
    #try:
    if DATABASE_MYSQL == "false":
        createMusicDB()
    elif not valDB('Music'):
        createMusicDB()
    writeIntoSongTable(pstrSongTitle, songID, pstrArtistName, pstrAlbumName, albumID, path, pathID, purlLink, roleID, artistID, songArtistRel, "F")

def createMusicDB():
    try:
        if DATABASE_MYSQL == "false":
            if not xbmcvfs.exists(MusicDB_LOC):
                sql_command = """CREATE TABLE songs (id INTEGER PRIMARY KEY,
                                                     strSongTitle VARCHAR(30),
                                                     strArtistName VARCHAR(30),
                                                     strAlbumName VARCHAR(30),
                                                     strPath VARCHAR(30), 
                                                     strURL VARCHAR(300),
                                                     roleID VARCHAR(30),
                                                     pathID VARCHAR(30),
                                                     artistID VARCHAR(30),
                                                     albumID VARCHAR(30),
                                                     songID VARCHAR(30),
                                                     songArtistRel VARCHAR(30),
                                                     delSong CHAR(1));"""
                connectMDB = sqlite3.connect(str(os.path.join(MusicDB_LOC)))
                cursor = connectMDB.cursor()
                cursor.execute(sql_command)
                cursor.close()
                connectMDB.close()

                while not xbmcvfs.exists(MusicDB_LOC):
                    True
        else:
            Config.DATABASETYPE = 'Music'
            Config.BUFFERED = True
            config = Config.dataBaseVal().copy()
            connectMDB = mysql.connector.Connect(**config)
            cursor = connectMDB.cursor()
            sql_command = """CREATE TABLE songs (id INTEGER PRIMARY KEY AUTO_INCREMENT, 
                                                 strSongTitle VARCHAR(30),
                                                 strArtistName VARCHAR(30),
                                                 strAlbumName VARCHAR(30),
                                                 strPath VARCHAR(300), 
                                                 strURL VARCHAR(1000),
                                                 roleID VARCHAR(30),
                                                 pathID VARCHAR(30),
                                                 artistID VARCHAR(30),
                                                 albumID VARCHAR(30),
                                                 songID VARCHAR(30),
                                                 songArtistRel VARCHAR(30),
                                                 delSong CHAR(1));"""
            cursor.execute(sql_command)
            connectMDB.commit()
            cursor.close()
            connectMDB.close()
    except:        
        pass    

def writeIntoSongTable (pstrSongTitle, songID, pstrArtistName, pstrAlbumName, albumID, path, pathID, purlLink, roleID, artistID, songArtistRel, delSong):
    selectQuery = ("SELECT id FROM songs WHERE songID=? AND artistID=? AND albumID=?;")
    selectArgs = (songID, artistID, albumID,)
    insertQuery = ("INSERT INTO songs (strSongTitle, songID, strArtistName, strAlbumName, albumID, strPath, pathID, strURL, roleID, artistID, songArtistRel, delSong) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);")
    insertArgs = (pstrSongTitle, songID, pstrArtistName, pstrAlbumName, albumID, path, pathID, purlLink, roleID, artistID, songArtistRel, delSong,)
    
    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs, str(os.path.join(MusicDB_LOC)))
    
def writePath(path):
    completePath = fileSys.completePath(path)
    selectQuery = ("SELECT idPath FROM path WHERE strPath= ?;")
    selectArgs = (completePath,)
    insertQuery = ("INSERT INTO path (strPath) VALUES (?);")
    insertArgs = (completePath,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeAlbums(album, artist, firstReleaseType='album'):
    lastScraped = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    artistCol = "strArtistDisp" if kodi_version >= 18 else "strArtists"
    selectQuery = ("SELECT idAlbum FROM album WHERE strAlbum=?;")
    selectArgs =  (album,)
    insertQuery = ("INSERT INTO album (strAlbum, {}, strReleaseType, strGenres) VALUES (?, ?, ?, ?);".format(artistCol))
    insertArgs =  (album, artist, firstReleaseType, 'osmosis',)
    
    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeSong(pathID, albumID, artist, songName, duration, track):
    dateAdded = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dateYear = int(datetime.datetime.now().strftime("%Y"))
    artistCol = "strArtistDisp" if kodi_version >= 18 else "strArtists"
    selectQuery = ("SELECT idSong FROM song WHERE strTitle=?;")
    selectArgs =  (songName,)
    insertQuery = ("INSERT INTO song (iYear, dateAdded, idAlbum, idPath, {}, strTitle, strFileName, iTrack, strGenres, iDuration, iTimesPlayed, iStartOffset, iEndOffset, userrating, comment, mood, votes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);".format(artistCol))
    insertArgs =  (dateYear, dateAdded, albumID, pathID, artist, songName, songName + ".strm", track, 'osmosis', duration, 0, 0, 0, 0, 'osmosis', 'osmosis', 0,)
    
    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeRole(strRole):
    selectQuery = ("SELECT idRole FROM role WHERE strRole=?;")
    selectArgs =  (strRole,)
    insertQuery = ("INSERT INTO role (strRole) VALUES (?);")
    insertArgs =  (strRole,)
    
    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeArtist(strArtist):
    selectQuery = ("SELECT idArtist FROM artist WHERE strArtist=?;")
    selectArgs =  (strArtist,)
    insertQuery = ("INSERT INTO artist (strArtist) VALUES (?);")
    insertArgs =  (strArtist,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeGenre(strGenre):
    selectQuery = ("SELECT idGenre FROM genre WHERE strGenre=?;")
    selectArgs =  (strGenre,)
    insertQuery = ("INSERT INTO genre (strGenre) VALUES (?);")
    insertArgs =  (strGenre,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)
           
def writeSongArtist(artistID, songID, roleID, pstrAartistName, orderID):
    selectQuery = ("SELECT idSong FROM song_artist WHERE idSong=?;")
    selectArgs =  (songID,)
    insertQuery = ("INSERT INTO song_artist (idArtist, idSong, idRole, iOrder, strArtist) VALUES (?, ?, ?, ?, ?);")
    insertArgs = (artistID, songID, roleID, orderID, pstrAartistName,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeSongGenre(genreID, songID):
    selectQuery = ("SELECT idSong FROM song_genre WHERE idGenre=? and idSong=?;")
    selectArgs =  (genreID, songID,)
    insertQuery = ("INSERT INTO song_genre (idGenre, idSong, iOrder) VALUES (?, ?, ?);")
    insertArgs = (genreID, songID, 0,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeAlbumArtist(artistID, albumID,pstrAartistName):
    selectQuery = ("SELECT idAlbum FROM album_artist WHERE idAlbum=?;")
    selectArgs =  (albumID,)
    insertQuery = ("INSERT INTO album_artist (idArtist, idAlbum, iOrder, strArtist) VALUES (?, ?, ?, ?);")
    insertArgs = (artistID, albumID, 0, pstrAartistName,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def writeThump(mediaId, mediaType, imageType, artPath):
    selectQuery = ("SELECT media_id FROM art WHERE media_type=? AND media_id=?;")
    selectArgs =  (mediaType, mediaId,)
    insertQuery = ("INSERT INTO art (media_id, media_type, type, url) VALUES (?, ?, ?, ?);")
    insertArgs =  (mediaId, mediaType,imageType, artPath,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)

def manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs, database=str(os.path.join(KMDBPATH))):
    try:
        utils.addon_log("insertQuery = " + insertQuery)
        utils.addon_log("insertArgs = " + str(insertArgs))
        dID = None
        if DATABASE_MYSQL == "false":
            connectMDB = sqlite3.connect(database)
            connectMDB.text_factory = str
            cursor = connectMDB.cursor()
            if selectArgs:
                searchResult = cursor.execute(selectQuery, selectArgs).fetchone();
            else:
                searchResult = cursor.execute(selectQuery).fetchone();
            if not searchResult and insertArgs:
                cursor.execute(insertQuery, insertArgs)
                connectMDB.commit()
                dID = cursor.lastrowid
            else:
                dID = searchResult[0]
        else:
            if database == str(os.path.join(KMDBPATH)):
                Config.DATABASETYPE = 'KMusic'
            else:
                Config.DATABASETYPE = 'Music'
            Config.BUFFERED = True
            config = Config.dataBaseVal().copy()
            connectMDB = mysql.connector.Connect(**config)
            cursor = connectMDB.cursor()
            if selectArgs:
                cursor.execute(selectQuery, selectArgs)
                searchResult = cursor.fetchone()
            else:
                cursor.execute(selectQuery)
                searchResult = cursor.fetchone()
            if not searchResult :
                cursor.execute(insertQuery, insertArgs)
                connectMDB.commit()
                dID = cursor.lastrowid
            else:
                dID = searchResult[0]
                
    except IOError as (errno, strerror):
        print ("I/O error({0}): {1}").format(errno, strerror)
    except ValueError:
        print ("No valid integer in line.")
    except:
        guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
        utils.addon_log(("Unexpected error: ") + str(sys.exc_info()[1]))
        print ("Unexpected error:"), sys.exc_info()[1]
    
    finally:
        cursor.close()
        connectMDB.close()
        return dID

def writeMoviePath(path):
    try:
        dID = None
        if DATABASE_MYSQL == "false":
            connectMDB = sqlite3.connect(str(os.path.join(MODBPATH)))
        else:
            Config.DATABASETYPE = 'Movies'
            Config.BUFFERED = True
            config = Config.dataBaseVal().copy()
            connectMDB = mysql.connector.Connect(**config)
        
        cursor = connectMDB.cursor()

        if not cursor.execute("select '%s' from '%s' where strPath='%s';" % ('idPath', 'path', str(os.path.join(path + '\\')))).fetchone() :
            sql_path = "INSERT INTO path (strPath) VALUES ('%s');" % (str(os.path.join(path + '\\')))
            cursor.execute(sql_path)
            connectMDB.commit()
            dID = cursor.lastrowid
        else:
            dID = cursor.execute("select '%s' from '%s' where strPath='%s';" % ("idPath", "path", str(os.path.join(path + '\\')))).fetchone()[0]  

        cursor.close()
        connectMDB.close()
        return dID      
    except:
        cursor.close()
        connectMDB.close() 
        pass

def valDB(database):
    if DATABASE_MYSQL == "false":
        dbcon = sqlite3.connect(database)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM sqlite_master WHERE name ='stream_ref' and type='table';").fetchall()
        if  len(dbcur.execute("SELECT * FROM sqlite_master WHERE name ='stream_ref' and type='table';").fetchall()) == 1:
            dbcur.close()
            return True
        
        dbcur.close()
        return False    
    else:
        Config.DATABASETYPE = database
        Config.BUFFERED = True
        config = Config.dataBaseVal().copy()
        connectMDB = mysql.connector.Connect(**config)
        cursor = connectMDB.cursor()
        if database == "Music":
            #stmt = "SHOW TABLES LIKE 'songs'"
            stmt = "SHOW TABLES LIKE 'songs';"
        else:
            #stmt = "SHOW TABLES LIKE 'stream_ref'"
            stmt = "SHOW TABLES LIKE 'stream_ref';"
        #stmt = "SHOW TABLES LIKE 'stream_ref'"
        cursor.execute(stmt)
        result = cursor.fetchone()
        if result:
            result = True
        else:
        # there are no tables named "tableName"
            result =  False
        
        return result    

def writeMovie(movieList):
    dbMovieList = []
    if DATABASE_MYSQL == "false":
        if not xbmcvfs.exists(MODBPATH):
            createMovDB()
        elif xbmcvfs.exists(MODBPATH) and not valDB(MODBPATH):
            xbmcvfs.delete(MODBPATH)
            createMovDB()       
    else:
        if not xbmcvfs.exists(MODBPATH_MYSQL):
            createMovDB()
        elif xbmcvfs.exists(MODBPATH_MYSQL) and not valDB('Movies'):
            xbmcvfs.delete(MODBPATH_MYSQL)
            createMovDB()     
        
    for i in movieList:
        if i:
            try:
                url = i[2]
                if url.find("?url=plugin") != -1:
                    url = url.strip().replace("?url=plugin", "plugin", 1)
                movID = movieExists(i[1], i[0])
                movieStreamExists(movID, i[3], url)
                if not movID in dbMovieList:
                    #ToDo: OriginalPlugin option
                    dbMovieList.append([ i[0], i[1], movID, i[3]])
            except IOError as (errno, strerror):
                print ("I/O error({0}): {1}").format(errno, strerror)
            except ValueError:
                print ("No valid integer in line.") 
            except:
                guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
                utils.addon_log("Unexpected error: " + str(movID) +" "+ str(i[3]) + " "+ str( url))
                print ("Unexpected error:"), sys.exc_info()[1]
                pass

    return dbMovieList

def writeShow(showList):
    dbShowList = []
    if DATABASE_MYSQL == "false":
        #createShowDB()
        if not xbmcvfs.exists(SHDBPATH):
            createShowDB()
        elif xbmcvfs.exists(SHDBPATH) and not valDB(SHDBPATH):
            xbmcvfs.delete(SHDBPATH)
            createShowDB()       
    else:
        if not valDB('TVShows'):
            createShowDB()       
        
    for i in showList:
        if i:
            try:
                url = i[3]
                if url.find("?url=plugin") != -1:
                    url = url.strip().replace("?url=plugin", "plugin", 1)
                #  ShowTitle, Paht{ i[4], i[0]}
                showID = showExists(i[4], i[0])
                episodeStreamExists(showID, i[1] + i[2], i[5], url)
                if not showID in dbShowList:
                    #ToDo: OriginalPlugin option
                    #Path, ShowTitle, ShowID, season, episode{ i[0], i[4], showID, i[3], i[1], i[2]}
                    dbShowList.append([ i[0], i[4], showID, i[1], i[2]])
            except IOError as (errno, strerror):
                print ("I/O error({0}): {1}").format(errno, strerror)
            except ValueError:
                print ("No valid integer in line.") 
            except:
                guiTools.infoDialog("Unexpected error: " + str(sys.exc_info()[1])+ (". Se your Kodi.log!"))
                utils.addon_log("Unexpected error: " + str(showID) +" "+ str(i[4]) + " "+ str( url))
                print ("Unexpected error:"), sys.exc_info()[1]
                pass

    return dbShowList

def createMovDB():
    try:        
        if DATABASE_MYSQL == "false":
            connectMDB = sqlite3.connect(str(os.path.join(MODBPATH)))
            sql_strm_ref = "CREATE TABLE stream_ref (id INTEGER PRIMARY KEY, mov_id INTEGER NOT NULL, provider TEXT NOT NULL, url TEXT NOT NULL);"
            sql_movtable = "CREATE TABLE movies (id INTEGER PRIMARY KEY, title TEXT NOT NULL, filePath TEXT NOT NULL);"
            cursor = connectMDB.cursor()  
            cursor.execute(sql_movtable)
            cursor.execute(sql_strm_ref)
                
            while not xbmcvfs.exists(MODBPATH):
                True
        else:
            Config.DATABASETYPE = 'Movies'
            Config.BUFFERED = True
            config = Config.dataBaseVal().copy()        
            connectMDB = mysql.connector.Connect(**config)
            sql_strm_ref = "CREATE TABLE stream_ref (id INTEGER PRIMARY KEY AUTO_INCREMENT, mov_id INTEGER NOT NULL, provider TEXT NOT NULL, url TEXT NOT NULL);"
            sql_movtable = "CREATE TABLE movies (id INTEGER PRIMARY KEY AUTO_INCREMENT, title TEXT NOT NULL, filePath TEXT NOT NULL);"
            cursor = connectMDB.cursor()  
            cursor.execute(sql_movtable)
            cursor.execute(sql_strm_ref)
            
        connectMDB.commit() 
        cursor.close()
        connectMDB.close()           
    except:
        pass
    
def createShowDB():
    try:        
        if DATABASE_MYSQL == "false":
            connectMDB = sqlite3.connect(str(os.path.join(SHDBPATH)))
            sql_strm_ref = "CREATE TABLE stream_ref (id INTEGER PRIMARY KEY, show_id INTEGER NOT NULL, seasonEpisode TEXT NOT NULL, provider TEXT NOT NULL, url TEXT NOT NULL);"
            sql_showtable = "CREATE TABLE shows (id INTEGER PRIMARY KEY, showTitle TEXT NOT NULL, filePath TEXT NOT NULL);"
            cursor = connectMDB.cursor()  
            cursor.execute(sql_showtable)
            cursor.execute(sql_strm_ref)
                
            while not xbmcvfs.exists(SHDBPATH):
                True
        else:
            Config.DATABASETYPE = 'TVShows'
            Config.BUFFERED = True
            config = Config.dataBaseVal().copy()        
            connectMDB = mysql.connector.Connect(**config)
            sql_strm_ref = "CREATE TABLE stream_ref (id INTEGER PRIMARY KEY AUTO_INCREMENT, show_id INTEGER NOT NULL, seasonEpisode TEXT NOT NULL, provider TEXT NOT NULL, url TEXT NOT NULL);"
            sql_showtable = "CREATE TABLE shows (id INTEGER PRIMARY KEY AUTO_INCREMENT, showTitle TEXT NOT NULL, filePath TEXT NOT NULL);"
            cursor = connectMDB.cursor()  
            cursor.execute(sql_showtable)
            cursor.execute(sql_strm_ref)
            
        connectMDB.commit() 
        cursor.close()
        connectMDB.close()           
    except:
        pass
    
def movieExists(title, path):
    try:
        path = fileSys.completePath(path)
        dID = None
        if DATABASE_MYSQL == "false":
            connectMDB = sqlite3.connect(str(os.path.join(MODBPATH)))
            cursor = connectMDB.cursor()
            
            if not cursor.execute("select '%s' from '%s' where title='%s';" % ('title', 'movies', title)).fetchone() :
                sql_path = "INSERT INTO movies (title, filePath) VALUES ('%s', '%s');" % (title, path)
                cursor.execute(sql_path)
                connectMDB.commit()
                dID = cursor.lastrowid
            else:
                dID = cursor.execute("select '%s' from '%s' where title='%s';" % ('id', 'movies', title)).fetchone()[0]
        else:
            Config.DATABASETYPE = 'Movies'
            Config.BUFFERED = True
            config = Config.dataBaseVal().copy()
            connectMDB = mysql.connector.Connect(**config)
            cursor = connectMDB.cursor()
            
            query = ("SELECT title FROM movies WHERE title = '%s';")
            cursor.execute(query % title)
            
            if not cursor.fetchone() :
                cursor.execute("INSERT INTO movies (title, filePath) VALUES ('%s', '%s');", (title, path))
                connectMDB.commit()
                dID = cursor.lastrowid
            else:
                query = ("SELECT id FROM movies WHERE title ='%s';")                
                cursor.execute(query % title)
                dID = cursor.fetchone()[0]

        cursor.close()
        connectMDB.close()
        return dID
    except:
        cursor.close()
        connectMDB.close()
        pass

def showExists(title, path):
    try:
        path = fileSys.completePath(path)
        dID = None
        if DATABASE_MYSQL == "false":
            connectMDB = sqlite3.connect(str(os.path.join(SHDBPATH)))
            cursor = connectMDB.cursor()
            
            if not cursor.execute("select '%s' from '%s' where showTitle='%s';" % ("showTitle","shows", title)).fetchone() :
                sql_path = "INSERT INTO shows (showTitle, filePath) VALUES ('%s', '%s');" % (title, path)
                cursor.execute(sql_path)
                connectMDB.commit()
                dID = cursor.lastrowid
            else:
                dID = cursor.execute("select '%s' from '%s' where showTitle='%s';" % ("id","shows", title)).fetchone()[0]
        else:
            Config.DATABASETYPE = 'TVShows'
            Config.BUFFERED = True
            config = Config.dataBaseVal().copy()
            connectMDB = mysql.connector.Connect(**config)
            cursor = connectMDB.cursor()
            
            query = ("SELECT showTitle FROM shows WHERE showTitle='%s';")
            cursor.execute(query % title)
            
            if not cursor.fetchone() :
                cursor.execute("INSERT INTO shows (showTitle, filePath) VALUES (%s, %s);", (title, path))
                connectMDB.commit()
                dID = cursor.lastrowid
            else:
                query = ("SELECT id FROM shows WHERE showTitle='%s';")                
                cursor.execute(query % title)
                dID = cursor.fetchone()[0]

        cursor.close()
        connectMDB.close()
        return dID
    except:
        cursor.close()
        connectMDB.close()
        pass
 
def movieStreamExists(movieID, provider, url):
    try:
        dID = None
        if DATABASE_MYSQL == "false":
            connectMDB = sqlite3.connect(str(os.path.join(MODBPATH)))
            cursor = connectMDB.cursor()
            if url.find("?url=plugin") != -1:
                url = url.strip().replace("?url=plugin", "plugin", 1)
            entry = cursor.execute("SELECT '%s', '%s' FROM '%s' WHERE mov_id='%s' AND provider='%s';" % ("mov_id","url", "stream_ref", movieID, provider)).fetchone()
        else:
            Config.DATABASETYPE = 'Movies'
            Config.BUFFERED = True
            config = Config.dataBaseVal().copy()
            connectMDB = mysql.connector.Connect(**config)
            cursor = connectMDB.cursor()
            if url.find("?url=plugin") != -1:
                url = url.strip().replace("?url=plugin", "plugin", 1)
            query = ("SELECT mov_id FROM stream_ref WHERE mov_id='%s' AND provider='%s' ")
            selectStm = (movieID, provider)
            cursor.execute(query % selectStm)
            entry = cursor.fetchone()
        
        if not entry:
            sql_path = "INSERT INTO stream_ref (mov_id, provider, url) VALUES ('%s', '%s', '%s');" % (movieID, provider, url)
            cursor.execute(sql_path)
            connectMDB.commit()
            dID = cursor.lastrowid
        else:
            if str(entry[1]) != url:
                sql_path = "UPDATE stream_ref SET url = '%s' WHERE mov_id = '%s';" % (url, movieID)
                cursor.execute(sql_path)
                connectMDB.commit()

            dID = cursor.execute("SELECT '%s' FROM '%s' WHERE mov_id='%s' AND url='%s';" % ("mov_id","stream_ref", movieID, url)).fetchone()[0] 

        cursor.close()
        connectMDB.close()
        return dID     
    except:
        cursor.close()
        connectMDB.close()
        pass

def episodeStreamExists(showID, seEp, provider, url):
    try:
        dID = None
        if DATABASE_MYSQL == "false":
            connectMDB = sqlite3.connect(str(os.path.join(SHDBPATH)))
            cursor = connectMDB.cursor()
            if url.find("?url=plugin") != -1:
                url = url.strip().replace("?url=plugin", "plugin", 1)
            entry = cursor.execute("SELECT '%s', '%s' FROM '%s' WHERE show_id='%s' AND seasonEpisode='%s' AND provider='%s';" % ("show_id", "url", "stream_ref", showID, seEp, provider)).fetchone()
        else:
            Config.DATABASETYPE = 'TVShows'
            Config.BUFFERED = True
            config = Config.dataBaseVal().copy()
            connectMDB = mysql.connector.Connect(**config)
            cursor = connectMDB.cursor()
            if url.find("?url=plugin") != -1:
                url = url.strip().replace("?url=plugin", "plugin", 1)
            query = ("SELECT show_id FROM stream_ref WHERE show_id='%s' AND seasonEpisode='%s' AND provider='%s';")
            selectStm = (showID, seEp, provider)
            cursor.execute(query % selectStm)
            entry = cursor.fetchone()
        
        if not entry:
            sql_path = "INSERT INTO stream_ref (show_id, seasonEpisode, provider, url) VALUES ('%s', '%s', '%s', '%s');" % (showID, seEp, provider, url)
            cursor.execute(sql_path)
            connectMDB.commit()
            dID = cursor.lastrowid
        else:
            if str(entry[1]) != url:
                sql_path = "UPDATE stream_ref SET url = '%s' WHERE show_id='%s' AND seasonEpisode='%s' AND provider='%s';" % (url, showID, seEp, provider)
                cursor.execute(sql_path)
                connectMDB.commit()
            dID = cursor.execute("SELECT '%s' FROM '%s' WHERE show_id='%s' AND seasonEpisode='%s' AND provider='%s';" % ("show_id","stream_ref", showID, seEp, provider)).fetchone()[0] 

        cursor.close()
        connectMDB.close()
        return dID     
    except:
        cursor.close()
        connectMDB.close()
        pass
    
def getVideo(ID, seasonEpisodes="n.a"):
    provList = None

    try:    
        args = {'sqliteDB': MODBPATH, 'mysqlDB': 'Movies'} if seasonEpisodes == "n.a" else {'sqliteDB': SHDBPATH, 'mysqlDB': 'TVShows'}
        con, cursor = openDB(**args)
                
        if seasonEpisodes == "n.a":
            query = "SELECT url, provider FROM stream_ref WHERE mov_id=?;"
            args = (ID,)
        else:
            query = "SELECT url, provider FROM stream_ref WHERE show_id=? AND seasonEpisode=?;"
            args = (ID, seasonEpisodes,)
    
        provList = cursor.execute(query, args).fetchall()       
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

        query = ("SELECT idFile FROM files WHERE strFilename=?;")
        args = (url,)

        dbfile = cursor.execute(query, args).fetchone()
        if dbfile:
            dbfileID = dbfile[0]
            query = ("SELECT timeInSeconds, totalTimeInSeconds, idBookmark FROM bookmark WHERE idFile=?;")
            args = (dbfileID,)
            urlResumePoint = cursor.execute(query, args).fetchone()
    except:
        pass
    finally:
        cursor.close()
        con.close()

    return urlResumePoint

def delBookMark(bookmarkID, fileID):
    try:
        con, cursor = openDB(KMODBPATH, 'KMovies')

        selectquery = ('SELECT idBookmark FROM bookmark WHERE {}=?;')
        deletequery = ('DELETE FROM bookmark WHERE {}=?;')
        args = (fileID,)

        dbbookmark = cursor.execute(selectquery.format('idFile'), args).fetchone()
        if dbbookmark:
            cursor.execute(deletequery.format('idFile'), args)

        args = (bookmarkID,)
        dbbookmark = cursor.execute(selectquery.format('idBookmark'), args).fetchone()
        if dbbookmark:
            cursor.execute(deletequery.format('idBookmark'), args)

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
        query = "SELECT idMovie, idFile, premiered, c14 FROM %s WHERE c00 LIKE ?;"
        args = (sTitle,)
        
        dbMovie = cursor.execute(query, args).fetchone()
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
        query = "SELECT episode.idEpisode, episode.idFile, episode.c00, episode.c05 FROM episode inner join tvshow on tvshow.idShow = episode.idShow WHERE episode.c12 = ? and episode.c13 = ? and tvshow.c00 like ?;" 
        args = (iSeason, iEpisode, sTVShowTitle,)
        
        dbEpisode = cursor.execute(query, args).fetchone()
    except:
        pass
    finally:
        cursor.close()
        con.close()

    return dbEpisode

def openDB(sqliteDB, mysqlDB):
    if DATABASE_MYSQL == "false":            
        con = sqlite3.connect(str(os.path.join(sqliteDB)))
        cursor = con.cursor()
    else:
        Config.DATABASETYPE = mysqlDB
        Config.BUFFERED = True
        config = Config.dataBaseVal().copy()
        con = mysql.connector.Connect(**config)
        cursor = con.cursor()

    return con, cursor
