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
STRM_LOC = xbmc.translatePath(os.path.join(REAL_SETTINGS.getSetting('STRM_LOC')))

#Databases
MDBUSERNAME = REAL_SETTINGS.getSetting('Music-DB username')
MDBPASSWORD = REAL_SETTINGS.getSetting('Music-DB password')
MDBNAME = REAL_SETTINGS.getSetting('Music-DB name')
MDBPATH = xbmc.translatePath(REAL_SETTINGS.getSetting('Music-DB path'))
MDBIP = REAL_SETTINGS.getSetting('Music-DB IP')

KMODBUSERNAME = REAL_SETTINGS.getSetting('KMovie-DB username')
KMODBPASSWORD = REAL_SETTINGS.getSetting('KMovie-DB password')
KMODBNAME = REAL_SETTINGS.getSetting('KMovie-DB name')
KMODBPATH = xbmc.translatePath(REAL_SETTINGS.getSetting('KMovie-DB path'))
KMODBIP = REAL_SETTINGS.getSetting('KMovie-DB IP')

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
        writeIntoSongTable(pstrSongTitle, songID, pstrArtistName, pstrAlbumName, albumID,path, pathID, purlLink, roleID, artistID, songArtistRel, "F")
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
    insertArgs =  (pstrSongTitle, songID, pstrArtistName,pstrAlbumName, albumID,path, pathID, purlLink,roleID, artistID,albumID, songArtistRel, delSong)
    
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
        connectMDB = sqlite3.connect(str(os.path.join(MDBPATH)))
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
def valDB(path, tablename):
    dbcon = sqlite3.connect(path)
    dbcur = dbcon.cursor()
    dbcur.execute("SELECT * FROM sqlite_master WHERE name ='stream_ref' and type='table'").fetchall()
    if  len(dbcur.execute("SELECT * FROM sqlite_master WHERE name ='stream_ref' and type='table'").fetchall()) == 1:
        dbcur.close()
        return True
    
    dbcur.close()
    return False    

def writeMovie(movieList):
    dbMovieList = []
    if not xbmcvfs.exists(MODBPATH):
        createMovDB()
    elif xbmcvfs.exists(MODBPATH) and not valDB(MODBPATH, "stream_ref"):
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
    if not xbmcvfs.exists(SHDBPATH):
        createShowDB()
    elif xbmcvfs.exists(SHDBPATH) and not valDB(SHDBPATH, "stream_ref"):
        xbmcvfs.delete(SHDBPATH)
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
        connectMDB = sqlite3.connect(str(os.path.join(MODBPATH)))
        sql_strm_ref = """CREATE TABLE stream_ref (id INTEGER PRIMARY KEY, mov_id INTEGER NOT NULL, provider TEXT NOT NULL, url TEXT NOT NULL);"""
        sql_movtable = """CREATE TABLE movies (id INTEGER PRIMARY KEY, title TEXT NOT NULL, filePath TEXT NOT NULL);"""
        cursor = connectMDB.cursor()  
        cursor.execute(sql_movtable)
        cursor.execute(sql_strm_ref)
            
        while not xbmcvfs.exists(MODBPATH):
            True
            
        connectMDB.commit() 
        cursor.close()
        connectMDB.close()           
    except:
        pass
    
def createShowDB():
    try:        
        connectMDB = sqlite3.connect(str(os.path.join(SHDBPATH)))
        sql_strm_ref = """CREATE TABLE stream_ref (id INTEGER PRIMARY KEY, show_id INTEGER NOT NULL, seasonEpisode TEXT NOT NULL, provider TEXT NOT NULL, url TEXT NOT NULL);"""
        sql_showtable = """CREATE TABLE shows (id INTEGER PRIMARY KEY, showTitle TEXT NOT NULL, filePath TEXT NOT NULL);"""
        cursor = connectMDB.cursor()  
        cursor.execute(sql_showtable)
        cursor.execute(sql_strm_ref)
            
        while not xbmcvfs.exists(SHDBPATH):
            True
            
        connectMDB.commit() 
        cursor.close()
        connectMDB.close()           
    except:
        pass 
     
def movieExists(title, path):
    try:
        connectMDB = sqlite3.connect(str(os.path.join(MODBPATH)))
        cursor = connectMDB.cursor()
 
        if not cursor.execute("""select "%s" from "%s" where title="%s";""" % ("title","movies", title)).fetchone() :
            sql_path = """INSERT INTO movies (title, filePath) VALUES ("%s", "%s");""" % (title, str(os.path.join(path + "\\")))
            cursor.execute(sql_path)
            connectMDB.commit()
            dID = cursor.lastrowid
            cursor.close()
            connectMDB.close()
            return dID
        else:
            dID = cursor.execute("""select "%s" from "%s" where title="%s";""" % ("id","movies", title)).fetchone()[0] 
            cursor.close()
            connectMDB.close()
            return dID     
    except:
        cursor.close()
        connectMDB.close()
        pass
def showExists(title, path):
    try:
        connectMDB = sqlite3.connect(str(os.path.join(SHDBPATH)))
        cursor = connectMDB.cursor()
 
        if not cursor.execute("""select "%s" from "%s" where showTitle="%s";""" % ("showTitle","shows", title)).fetchone() :
            sql_path = """INSERT INTO shows (showTitle, filePath) VALUES ("%s", "%s");""" % (title, os.path.join(path + "\\"))
            cursor.execute(sql_path)
            connectMDB.commit()
            dID = cursor.lastrowid
            cursor.close()
            connectMDB.close()
            return dID
        else:
            dID = cursor.execute("""select "%s" from "%s" where showTitle="%s";""" % ("id","shows", title)).fetchone()[0] 
            cursor.close()
            connectMDB.close()
            return dID     
    except:
        cursor.close()
        connectMDB.close()
        pass
 
def movieStreamExists(movieID, provider, url):
    try:
        connectMDB = sqlite3.connect(str(os.path.join(MODBPATH)))
        cursor = connectMDB.cursor()
        if url.find("?url=plugin") != -1:
            url = url.strip().replace("?url=plugin", "plugin", 1)
            
        if not cursor.execute("""SELECT "%s" FROM "%s" WHERE mov_id="%s" AND provider="%s";""" % ("mov_id","stream_ref", movieID, provider)).fetchone() :
            sql_path = """INSERT INTO stream_ref (mov_id, provider, url) VALUES ("%s", "%s", "%s");""" % (movieID, provider, url)
            cursor.execute(sql_path)
            connectMDB.commit()
            dID = cursor.lastrowid
            cursor.close()
            connectMDB.close()
            return dID
        else:
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
        connectMDB = sqlite3.connect(str(os.path.join(SHDBPATH)))
        cursor = connectMDB.cursor()
        if url.find("?url=plugin") != -1:
            url = url.strip().replace("?url=plugin", "plugin", 1)
            
        if not cursor.execute("""SELECT "%s" FROM "%s" WHERE show_id="%s" AND seasonEpisode="%s" AND provider="%s";""" % ("show_id","stream_ref", showID, seEp, provider)).fetchone() :
            sql_path = """INSERT INTO stream_ref (show_id, seasonEpisode, provider, url) VALUES ("%s", "%s", "%s", "%s");""" % (showID, seEp, provider, url)
            cursor.execute(sql_path)
            connectMDB.commit()
            dID = cursor.lastrowid
            cursor.close()
            connectMDB.close()
            return dID
        else:
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
            connectMDB = sqlite3.connect(str(os.path.join(MODBPATH)))
            cursor = connectMDB.cursor()
            provList = cursor.execute("""SELECT "%s" , "%s" FROM "%s" WHERE mov_id="%s" ;""" % ("url", "provider","stream_ref", ID)).fetchall()
        else:
            connectMDB = sqlite3.connect(str(os.path.join(SHDBPATH)))
            cursor = connectMDB.cursor()
            provList = cursor.execute("""SELECT "%s" , "%s" FROM "%s" WHERE show_id="%s" AND seasonEpisode="%s" ;""" % ("url", "provider","stream_ref", ID, seasonEpisodes)).fetchall()
      
        cursor.close()
        connectMDB.close()
        return provList     
    except:
        cursor.close()
        connectMDB.close()
        pass
def getPlayedURLResumePoint(url):
    try:
        connectMDB = sqlite3.connect(str(os.path.join(KMODBPATH)))
        cursor = connectMDB.cursor()
                  
        if cursor.execute("""SELECT "%s" FROM "%s" WHERE strFilename="%s";""" % ("idFile","files", url)).fetchone():
            dbURLID = cursor.execute("""SELECT "%s" FROM "%s" WHERE strFilename="%s";""" % ("idFile","files", url)).fetchone()[0]
            if cursor.execute("""SELECT "%s", "%s" FROM "%s" WHERE idFile="%s";""" % ("timeInSeconds", "totalTimeInSeconds","bookmark", dbURLID)).fetchone():
                return cursor.execute("""SELECT "%s", "%s", "%s" FROM "%s" WHERE idFile="%s";""" % ("timeInSeconds","totalTimeInSeconds", "idBookmark","bookmark", dbURLID)).fetchall()
        cursor.close()
        connectMDB.close()
    except:
        cursor.close()
        connectMDB.close()
        pass
def delBookMark(ID, movFileID):
    try:
        connectMDB = sqlite3.connect(str(os.path.join(KMODBPATH)))
        cursor = connectMDB.cursor()
                
        if cursor.execute("""SELECT "%s" FROM "%s" WHERE idFile="%s";""" % ("idBookmark","bookmark", movFileID)).fetchone():
            cursor.execute("""DELETE FROM "%s" WHERE idFile="%s";""" % ("bookmark", movFileID))
            time.sleep(1)
        if cursor.execute("""SELECT "%s" FROM "%s" WHERE idBookmark="%s";""" % ("idBookmark","bookmark", ID)).fetchone():
            cursor.execute("""DELETE FROM "%s" WHERE idBookmark="%s";""" % ("bookmark", ID))
        connectMDB.commit()  
        cursor.close()
        connectMDB.close()   
    except:
        cursor.close()
        connectMDB.close()
        pass
def getKodiMovieID(title, sTitle):
    try:
        connectMDB = sqlite3.connect(str(os.path.join(KMODBPATH)))
        cursor = connectMDB.cursor()
                  
        if cursor.execute("""SELECT "%s", "%s" FROM "%s" WHERE c00 LIKE "%s" OR c00 LIKE "%s";"""  % ("idMovie","idFile","movie", title, sTitle)).fetchone():
            return cursor.execute("""SELECT "%s", "%s" FROM "%s" WHERE c00 LIKE "%s" OR c00 LIKE "%s";"""  % ("idMovie","idFile","movie", title, sTitle)).fetchall()
        cursor.close()
        connectMDB.close()        
    except:
        cursor.close()
        connectMDB.close()
    