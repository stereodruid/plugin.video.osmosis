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
import pyxbmct
from modules import stringUtils
from modules import guiTools
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
MusicDB_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'Musik'))
TVShowDB_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'TVShow.db'))
MODBPATH = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'Movies'))
SHDBPATH = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'TVShows'))
STRM_LOC = xbmc.translatePath(os.path.join(REAL_SETTINGS.getSetting('STRM_LOC')))

#Databases
MDBUSERNAME = REAL_SETTINGS.getSetting('Music-DB username')
MDBPASSWORD = REAL_SETTINGS.getSetting('Music-DB password')
MDBNAME = REAL_SETTINGS.getSetting('Music-DB name')
MDBPATH = xbmc.translatePath(REAL_SETTINGS.getSetting('Music-DB path'))
MDBIP = REAL_SETTINGS.getSetting('Music-DB IP')
MDBPORT = REAL_SETTINGS.getSetting('Music-DB port')

MOVDBUSERNAME = REAL_SETTINGS.getSetting('Movies-DB username')
MOVDBPASSWORD = REAL_SETTINGS.getSetting('Movies-DB password')
MOVDBNAME = REAL_SETTINGS.getSetting('Movies-DB name')
MOVDBPATH = xbmc.translatePath(REAL_SETTINGS.getSetting('Movies-DB path'))
MOVDBIP = REAL_SETTINGS.getSetting('Movies-DB IP')
MOVDBPORT = REAL_SETTINGS.getSetting('Movies-DB port')

TVSDBUSERNAME = REAL_SETTINGS.getSetting('TV-Show-DB username')
TVSDBPASSWORD = REAL_SETTINGS.getSetting('TV-Show-DB password')
TVSDBNAME = REAL_SETTINGS.getSetting('TV-Show-DB name')
TVSDBPATH = xbmc.translatePath(REAL_SETTINGS.getSetting('TV-Show-DB path'))
TVSDBIP = REAL_SETTINGS.getSetting('TV-Show-DB IP')
TVSDBPORT = REAL_SETTINGS.getSetting('TV-Show-DB port')

KMODBUSERNAME = REAL_SETTINGS.getSetting('KMovie-DB username')
KMODBPASSWORD = REAL_SETTINGS.getSetting('KMovie-DB password')
KMODBNAME = REAL_SETTINGS.getSetting('KMovie-DB name')
KMODBPATH = xbmc.translatePath(REAL_SETTINGS.getSetting('KMovie-DB path'))
KMODBIP = REAL_SETTINGS.getSetting('KMovie-DB IP')
KMODBPORT = REAL_SETTINGS.getSetting('KMovi-DB port')

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

class Config(object):
    """Configure me so examples work
    
    Use me like this:
    
        mysql.connector.Connect(**Config.dbinfo())
    """
    DatabaseTYpe = ""
    CHARSET = 'utf8'
    UNICODE = True
    WARNINGS = True
    BUFFERED = True
    
    #Databases
    @classmethod
    def dataBaseVal(cls):
       
        DBValuses = ["SERNAME", "PASSWORD", "NAME", "IP", "PORT"]
        
        if cls.DatabaseTYpe == "KMovies":   
            DBValuses = [KMODBUSERNAME, KMODBPASSWORD, KMODBNAME, KMODBIP, KMODBPORT]
        elif cls.DatabaseTYpe == "Musik":   
            DBValuses = [MDBUSERNAME, MDBPASSWORD, MDBNAME, MDBIP, MDBPORT]
        elif cls.DatabaseTYpe == "Movies":
            DBValuses = [MOVDBUSERNAME, MOVDBPASSWORD, MOVDBNAME, MOVDBIP, MOVDBPORT]
        elif cls.DatabaseTYpe == "TVShows":
            DBValuses = [TVSDBUSERNAME, TVSDBPASSWORD, TVSDBNAME, TVSDBIP, TVSDBPORT]
        
 
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
    
def musicDatabase(pstrAlbumName, pstrArtistName, pstrSongTitle, pstrPath, purlLink, track, artPath):
    path = str(os.path.join(STRM_LOC, pstrPath))
    
    # Write to music db and get id's
    roleID = writeRole("Artist")
    pathID = writePath(path)
    artistID = writeArtist(pstrArtistName)
    albumID = writeAlbums(pstrAlbumName,pstrArtistName)
    songID = writeSong(pathID, albumID,  pstrArtistName, pstrSongTitle, track)   
    songArtistRel = writeSongArtist(artistID, songID,"1", pstrArtistName,"0")
    writeAlbumArtist(artistID, albumID,pstrArtistName)
    writeThump(artistID, "artist", "thumb", artPath)
    writeThump(albumID, "album", "thumb", artPath)
    
    try:
        validateMusicDB(str(os.path.join(MusicDB_LOC)))
        writeIntoSongTable(pstrSongTitle, songID, pstrArtistName, pstrAlbumName, albumID, path, pathID, purlLink, roleID, artistID, songArtistRel, "F")
    except:        
        pass    
   

def validateMusicDB (dbFileName):

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
            
            while not xbmcvfs.exists(MusicDB_LOC):
                True            

def writeIntoSongTable (pstrSongTitle, songID, pstrArtistName, pstrAlbumName, albumID, path, pathID, purlLink, roleID, artistID, songArtistRel, delSong):

    selectQuery = "SELECT id FROM songs WHERE songID=? AND artistID=? AND albumID=?"
    selectArgs =  (songID, artistID, albumID)
    
    insertQuery = "INSERT INTO songs (strSongTitle, songID, strArtistName, strAlbumName, albumID, strPath, pathID, strURL, roleID, artistID, songArtistRel, delSong)  " """VALUES 
                   (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    insertArgs =  (pstrSongTitle, songID, pstrArtistName, pstrAlbumName, albumID, path, pathID, purlLink, roleID, artistID, songArtistRel, delSong)
    
    dID = manageDbRecord (selectQuery, selectArgs, insertQuery, insertArgs, str(os.path.join(MusicDB_LOC)))

    return dID  
    
def writePath(path):

    completePath = str(os.path.join(path + "\\"))
    selectQuery = "SELECT idPath FROM path WHERE strPath=?"
    selectArgs =  (completePath,)
    
    insertQuery = "INSERT INTO path (strPath) " """VALUES (?)"""
    insertArgs =  (completePath,)
    
    dID = manageDbRecord (selectQuery, selectArgs, insertQuery, insertArgs)

    return dID  


def writeAlbums(album, artist, firstReleaseType='album'):

    selectQuery = "SELECT idAlbum FROM album WHERE strAlbum=?"
    selectArgs =  (album,)
    
    lastScraped = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    insertQuery = "INSERT INTO album (strAlbum, strArtists, strReleaseType, lastScraped) " """VALUES (?, ?, ?, ?)"""
    insertArgs =  (album, artist, firstReleaseType, lastScraped)
    
    dID = manageDbRecord (selectQuery, selectArgs, insertQuery, insertArgs)

    return dID  

    
def writeSong(pathID, albumID, artist, songName, track="NULL"):

    selectQuery = "SELECT idSong FROM song WHERE strTitle=?"
    selectArgs =  (songName,)
    
#    selectQuery = """select idSong from song where strTitle="%s";""" % (songName)
    
    dateAdded = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dateYear = datetime.datetime.now().strftime("%Y")
    insertQuery = "INSERT INTO song (iYear,dateAdded,idAlbum,idPath,strArtists,strTitle,strFileName,iTrack,strGenres,iDuration,iTimesPlayed,iStartOffset,iEndOffset,userrating,comment,mood,votes) " """VALUES 
                   (?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    insertArgs =  (dateYear, dateAdded, albumID, pathID, artist, songName, songName + ".strm", track, "osmosis", "200", "0", "0", "0", "5", "osmosis", "osmosis", "100" )
    
    dID = manageDbRecord (selectQuery, selectArgs, insertQuery, insertArgs)

    return dID  


def writeRole(strRole):
    selectQuery = "SELECT idRole FROM role WHERE strRole=?"
    selectArgs =  (strRole,)
    
    insertQuery = "INSERT INTO role (strRole) " """VALUES (?)"""
    insertArgs =  (strRole,)
    
    dID = manageDbRecord (selectQuery, selectArgs, insertQuery, insertArgs)

    return dID  


def writeArtist(strArtist):
    
    selectQuery = "SELECT idArtist FROM artist WHERE strArtist=?"
    selectArgs =  (strArtist,)
    
    insertQuery = "INSERT INTO artist ( strArtist ) " """VALUES (?)"""
    insertArgs =  (strArtist,)
    
    dID = manageDbRecord (selectQuery, selectArgs, insertQuery, insertArgs)

    return dID  
    
    
           
def writeSongArtist(artistID, songID,roleID, pstrAartistName, orderID):   
    selectQuery = "SELECT idSong FROM song_artist WHERE idSong=?"
    selectArgs =  (songID,)
    
    insertQuery = "INSERT INTO song_artist (idArtist, idSong, idRole, iOrder,strArtist) " """VALUES (?, ?, ?, ?,?)"""
    insertArgs = (artistID, songID, roleID, orderID, pstrAartistName)
    
    dID = manageDbRecord (selectQuery, selectArgs, insertQuery, insertArgs)

    return dID  

    
def writeAlbumArtist(artistID, albumID,pstrAartistName):
    selectQuery = "SELECT idAlbum FROM album_artist WHERE idAlbum=?"
    selectArgs =  (albumID,)
    
    insertQuery = "INSERT INTO album_artist (idArtist, idAlbum, strArtist) " """VALUES (?, ?,?)"""
    insertArgs = (artistID, albumID, pstrAartistName)
    
    dID = manageDbRecord (selectQuery, selectArgs, insertQuery, insertArgs)

    return dID  


def writeThump(mediaId, mediaType, imageType, artPath):
    
    selectQuery = "SELECT media_id FROM art WHERE media_type=? AND media_id=?"
    selectArgs =  (mediaType, mediaId)
    
    insertQuery = "INSERT INTO art ( media_id, media_type, type, url) " """VALUES (?,?,?,?)"""
    insertArgs =  (mediaId, mediaType,imageType, artPath )
    
    dID = manageDbRecord (selectQuery, selectArgs, insertQuery, insertArgs)

    return dID  


def manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs, dbPath=str(os.path.join(MDBPATH))):
    try:
        connectMDB = sqlite3.connect(dbPath)
        connectMDB.text_factory = str
        cursor = connectMDB.cursor()

        if selectArgs:
            searchResult = cursor.execute(selectQuery, selectArgs).fetchone();
        else:
            searchResult = cursor.execute(selectQuery).fetchone();
        
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
        Config.DatabaseTYpe = 'Movies'
        Config.BUFFERED = True
        config = Config.dataBaseVal().copy()        
        connectMDB = mysql.connector.Connect(**config)
        cursor = connectMDB.cursor()

        if not cursor.execute("""select "%s" from "%s" where strPath="%s";""" % ("idPath","path", str(os.path.join(path + "\\")))).fetchone() :
            sql_path = """INSERT INTO path (strPath) VALUES ("%s");""" % (str(os.path.join(path + "\\")))
            cursor.execute(sql_path)
            connectMDB.commit()
            dID = cursor.lastrowid
            cursor.close()
            connectMDB.close()
            return dID 
        else:
            dID = cursor.execute("""select "%s" from "%s" where strPath="%s";""" % ("idPath","path", str(os.path.join(path + "\\")))).fetchone()[0]  
            cursor.close()
            connectMDB.close()
            return dID      
    except:
        cursor.close()
        connectMDB.close() 
        pass    
def valDB(databaseName):
    Config.DatabaseTYpe = databaseName
    Config.BUFFERED = True
    config = Config.dataBaseVal().copy()        
    connectMDB = mysql.connector.Connect(**config)
    
    cursor = connectMDB.cursor()
    stmt = "SHOW TABLES LIKE 'stream_ref'"
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
    if not xbmcvfs.exists(MODBPATH):
        createMovDB()
    elif xbmcvfs.exists(MODBPATH) and not valDB('Movies'):
        xbmcvfs.delete(MODBPATH)
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
#     if not xbmcvfs.exists(SHDBPATH):
#         createShowDB()
#     elif xbmcvfs.exists(SHDBPATH) and not valDB('TVShows'):
#         xbmcvfs.delete(SHDBPATH)
#         createShowDB()       
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
#########################################                ############################################
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
        Config.DatabaseTYpe = 'Movies'
        Config.BUFFERED = True
        config = Config.dataBaseVal().copy()        
        connectMDB = mysql.connector.Connect(**config)
        sql_strm_ref = """CREATE TABLE stream_ref (id INTEGER PRIMARY KEY AUTO_INCREMENT, mov_id INTEGER NOT NULL, provider TEXT NOT NULL, url TEXT NOT NULL);"""
        sql_movtable = """CREATE TABLE movies (id INTEGER PRIMARY KEY AUTO_INCREMENT, title TEXT NOT NULL, filePath TEXT NOT NULL);"""
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
        Config.DatabaseTYpe = 'TVShows'
        config = Config.dataBaseVal().copy()        
        connectMDB = mysql.connector.Connect(**config)
        cursor = connectMDB.cursor()   
        #connectMDB = sqlite3.connect(str(os.path.join(SHDBPATH)))
        sql_strm_ref = """CREATE TABLE stream_ref (id INTEGER PRIMARY KEY AUTO_INCREMENT, show_id INTEGER NOT NULL, seasonEpisode TEXT NOT NULL, provider TEXT NOT NULL, url TEXT NOT NULL);"""
        sql_showtable = """CREATE TABLE shows (id INTEGER PRIMARY KEY AUTO_INCREMENT, showTitle TEXT NOT NULL, filePath TEXT NOT NULL);"""
        cursor = connectMDB.cursor()  
        cursor.execute(sql_showtable)
        cursor.execute(sql_strm_ref)
            
        connectMDB.commit() 
        cursor.close()
        connectMDB.close()           
    except:
        cursor.close()
        connectMDB.close()
        pass 
     
def movieExists(title, path):
    try:
        
        Config.DatabaseTYpe = 'Movies'
        config = Config.dataBaseVal().copy() 
        connectMDB = mysql.connector.Connect(**config)
        cursor = connectMDB.cursor()
 
        query = ("""SELECT title FROM movies WHERE title = "%s" """)
        cursor.execute(query % title)
                       
        if not cursor.fetchone() :
            #sql_path = """INSERT INTO movies (title, filePath) VALUES ("%s", "%s");""" % (title, str(os.path.join(path + "\\")))
            cursor.execute("INSERT INTO movies (title, filePath) VALUES (%s, %s)", (title, os.path.join(path + "\\"),))
            connectMDB.commit()
            dID = cursor.lastrowid
            cursor.close()
            connectMDB.close()
            return dID
        else:
            query = ("""SELECT id FROM movies WHERE title ="%s" """)
    
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
        Config.DatabaseTYpe = 'TVShows'
        Config.BUFFERED = True
        config = Config.dataBaseVal().copy()        
        connectMDB = mysql.connector.connect(**config)
        cursor = connectMDB.cursor()
        
        query = ("""SELECT showTitle FROM shows WHERE showTitle = "%s" """)
        #selectStm = ("showTitle", "shows", title)
        cursor.execute(query % title)

        if not cursor.fetchone() :
            sql_path = """INSERT INTO shows (showTitle, filePath) VALUES ("%s", "%s");""" % (title, os.path.join(path + "\\"),)
            cursor.execute("INSERT INTO shows (showTitle, filePath) VALUES (%s, %s)", (title, os.path.join(path + "\\"),))
            connectMDB.commit()
            dID = cursor.lastrowid
            cursor.close()
            connectMDB.close()
            return dID
        else:
            query = ("""SELECT id FROM shows WHERE showTitle = "%s" """)
            #selectStm = ("showTitle", "shows", title)
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
        Config.DatabaseTYpe = 'Movies'
        Config.BUFFERED = True
        config = Config.dataBaseVal().copy()        
        connectMDB = mysql.connector.Connect(**config)
        cursor = connectMDB.cursor()
        if url.find("?url=plugin") != -1:
            url = url.strip().replace("?url=plugin", "plugin", 1)

        query = ("""SELECT mov_id FROM stream_ref WHERE mov_id='%s' AND provider="%s" """)
        selectStm = (movieID, provider)
        
        cursor.execute(query % selectStm)
        #if not cursor.execute("""SELECT "%s" FROM "%s" WHERE mov_id="%s" AND provider="%s";""" % ("mov_id","stream_ref", movieID, provider)).fetchone() :
        dID = cursor.fetchone() 
        if not dID :
            sql_path = """INSERT INTO stream_ref (mov_id, provider, url) VALUES ("%s", "%s", "%s");""" % (movieID, provider, url)
            cursor.execute(sql_path)
            connectMDB.commit()
            dID = cursor.lastrowid
            cursor.close()
            connectMDB.close()
            return dID
        else:
            if str(entry[1]) != url:
                sql_path = """UPDATE stream_ref SET url = "%s" WHERE mov_id = "%s";""" % (url, movieID)
                cursor.execute(sql_path)
                connectMDB.commit()
            dID = cursor.execute("""SELECT "%s" FROM "%s" WHERE mov_id="%s" AND url="%s";""" % ("mov_id","stream_ref", movieID, url)).fetchone()[0] 
            cursor.close()
            connectMDB.close()
            return dID     
    except:
        cursor.close()
        connectMDB.close()
        pass

def episodeStreamExists(showID,seEp, provider, url):
    try:
        Config.DatabaseTYpe = 'TVShows'
        Config.BUFFERED = True
        config = Config.dataBaseVal().copy()        
        connectMDB = mysql.connector.Connect(**config)
        cursor = connectMDB.cursor()
        
        if url.find("?url=plugin") != -1:
            url = url.strip().replace("?url=plugin", "plugin", 1)
        
        query = ("""SELECT show_id FROM stream_ref WHERE show_id="%s" AND seasonEpisode="%s" AND provider="%s" """)
        selectStm = (showID, seEp, provider)
        
        cursor.execute(query % selectStm)
        dID = cursor.fetchone() 
        
        if not dID :
            sql_path = """INSERT INTO stream_ref (show_id, seasonEpisode, provider, url) VALUES ("%s", "%s", "%s", "%s");""" % (showID, seEp, provider, url)
            cursor.execute(sql_path)
            connectMDB.commit()
            dID = cursor.lastrowid
            cursor.close()
            connectMDB.close()
            return dID
        else:
            if str(entry[1]) != url:
                sql_path = """UPDATE stream_ref SET url = "%s" WHERE show_id="%s" AND seasonEpisode="%s" AND provider="%s";""" % (url, showID, seEp, provider)
                cursor.execute(sql_path)
                connectMDB.commit()
            dID = cursor.execute("""SELECT "%s" FROM "%s" WHERE show_id="%s" AND seasonEpisode="%s" AND provider="%s";""" % ("show_id","stream_ref", showID, seEp, provider)).fetchone()[0] 
            cursor.close()
            connectMDB.close()
            return dID     
    except:
        cursor.close()
        connectMDB.close()
        pass
    
def getVideo(ID, seasonEpisodes="n.a"):
    try:
        if seasonEpisodes == "n.a":
            Config.DatabaseTYpe = 'Movies'
            query = ("""SELECT url, provider FROM stream_ref WHERE mov_id= "%s" """)
            selectStm = (ID)
            #provList = cursor.execute("""SELECT "%s" , "%s" FROM "%s" WHERE mov_id="%s" ;""" % ("url", "provider","stream_ref", ID)).fetchall()
        else:
            Config.DatabaseTYpe = 'TVShows'
            query = ("""SELECT url, provider  FROM stream_ref WHERE show_id='%s' AND seasonEpisode="%s" """)
            selectStm = (ID, seasonEpisodes)
            #provList = cursor.execute("""SELECT "%s" , "%s" FROM "%s" WHERE show_id="%s" AND seasonEpisode="%s" ;""" % ("url", "provider","stream_ref", ID, seasonEpisodes)).fetchall()
        
        Config.BUFFERED = True
        config = Config.dataBaseVal().copy()        
        connectMDB = mysql.connector.Connect(**config)
        cursor = connectMDB.cursor()
        
        cursor.execute(query % selectStm)
        provList = cursor.fetchall()
        
        cursor.close()
        connectMDB.close()
        
        return provList     
    except:
        cursor.close()
        connectMDB.close()
        pass
def getPlayedURLResumePoint(url):
    try:
        Config.DatabaseTYpe = 'KMovies'
        query = ("""SELECT idFile FROM files WHERE strFilename="%s" """)
        selectStm = (url)
        
        Config.BUFFERED = True
        config = Config.dataBaseVal().copy()        
        connectMDB = mysql.connector.Connect(**config)
        cursor = connectMDB.cursor()
        
        cursor.execute(query % selectStm)
        if cursor.fetchone() :
            dbURLID = cursor.fetchone()[0]
            query = ("""SELECT timeInSeconds, totalTimeInSeconds FROM bookmark WHERE idFile="%s" """)
            selectStm = (dbURLID)
            cursor.execute(query % selectStm)
            if cursor.fetchone() :
                query = ("""SELECT timeInSeconds, totalTimeInSeconds, idBookmark FROM "bookmark WHERE idFile="%s" """)
                selectStm = (dbURLID)
                urlResumePoint = cursor.fetchall()
        
        cursor.close()
        connectMDB.close()
        
        return urlResumePoint     
    except:
        cursor.close()
        connectMDB.close()
        pass
def delBookMark(ID, movFileID):
    try:
        Config.DatabaseTYpe = 'KMovies'
        query = ("""SELECT idBookmark FROM bookmark WHERE idFile="%s" """)
        selectStm = (movFileID)
        
        Config.BUFFERED = True
        config = Config.dataBaseVal().copy()        
        connectMDB = mysql.connector.Connect(**config)
        cursor = connectMDB.cursor()
        
        cursor.execute(query % selectStm)
        if cursor.fetchone() :
            query = ("""DELETE FROM bookmark WHERE idFile="%s" """)
            selectStm = (movFileID)
            cursor.execute(query % selectStm)
            time.sleep(1)
        
        query = ("""SELECT idBookmark FROM bookmark WHERE idFile="%s" """)
        selectStm = (movFileID)
        
        cursor.execute(query % selectStm)
        if cursor.fetchone() :
            query = ("""DELETE FROM bookmark WHERE idBookmark="%s" """)
            selectStm = (ID)
            cursor.execute(query % selectStm)
        
        cursor.close()
        connectMDB.close()
    except:
        cursor.close()
        connectMDB.close()
        pass
def getKodiMovieID(title, sTitle):
    try:
        Config.DatabaseTYpe = 'KMovies'
        query = ("""SELECT idMovie, idFile FROM movie WHERE c00 LIKE "%s" OR c00 LIKE "%s" """)
        selectStm = (title, sTitle)
        
        Config.BUFFERED = True
        config = Config.dataBaseVal().copy()        
        connectMDB = mysql.connector.Connect(**config)
        cursor = connectMDB.cursor()
        
        cursor.execute(query % selectStm)
        if cursor.fetchone() :
            kodiMovID = cursor.fetchall()
        
        
        cursor.close()
        connectMDB.close()
        
        return kodiMovID     
    except:
        cursor.close()
        connectMDB.close()
        pass
