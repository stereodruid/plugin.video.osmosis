# Copyright (C) 2016 stereodruid(J.G.)
#
#
# This file is part of OSMOSIS
#
# OSMOSIS is free software: you can redistribute it. 
# You can modify it for private use only.
# OSMOSIS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

import fileinput
import os
import sys
import re
import shutil
import time, datetime
import errno
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP
import SimpleDownloader as downloader
import pyxbmct
import utils
import codecs
from modules import stringUtils
from modules import guiTools
import errno
import xbmc
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs
import sqlite3
addnon_id = 'plugin.video.osmosis'
addon = xbmcaddon.Addon(addnon_id)
addon_version = addon.getAddonInfo('version')
ADDON_NAME = addon.getAddonInfo('name')
REAL_SETTINGS = xbmcaddon.Addon(id=addnon_id)
ADDON_SETTINGS = REAL_SETTINGS.getAddonInfo('profile')
ADDON_PATH = REAL_SETTINGS.getAddonInfo('path')
MediaList_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'MediaList.xml'))
MusicDB_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'Musik.db'))
MovieDB_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'Movie.db'))
TVShowDB_LOC = xbmc.translatePath(os.path.join(ADDON_SETTINGS, 'TVShow.db'))
STRM_LOC = xbmc.translatePath(os.path.join(REAL_SETTINGS.getSetting('STRM_LOC')))
MDBUSERNAME = REAL_SETTINGS.getSetting('Music-DB username')
MDBPASSWORD = REAL_SETTINGS.getSetting('Music-DB password')
MDBNAME = REAL_SETTINGS.getSetting('Music-DB name')
MDBPATH = REAL_SETTINGS.getSetting('Music-DB path')
MDBIP = REAL_SETTINGS.getSetting('Music-DB IP')
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
    albumArtistRel = writeAlbumArtist(artistID, albumID,pstrArtistName)
    writeThump(artistID, "artist", "thumb", artPath)
    writeThump(albumID, "album", "thumb", artPath)
    try:
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
        else:
            connectMDB = sqlite3.connect(str(os.path.join(MusicDB_LOC)))
            cursor = connectMDB.cursor()          
        
        sql_songinfo = """INSERT INTO songs (strSongTitle, 
                                            songID, 
                                            strArtistName, 
                                            strAlbumName, 
                                            albumID, 
                                            strPath, 
                                            pathID, 
                                            strURL,
                                            roleID,
                                            artistID,
                                            albumID,
                                            songArtistRel,
                                            delSong ) 
        VALUES ("%s", "%s", "%s", "%s", "%s", 
                "%s","%s", "%s", "%s", "%s", 
                "%s", "%s","%s");""" % (pstrSongTitle, songID, pstrArtistName,pstrAlbumName, albumID,path, pathID, purlLink,roleID, artistID,albumID, songArtistRel, "F")
        cursor.execute(sql_songinfo)
        connectMDB.commit()
        cursor.close()
        connectMDB.close()
    except:        
        cursor.close()
        connectMDB.close()
        pass    
   
def writePath(path):
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
 
def writeAlbums(album, artist, firstReleaseType='album'):
    lastScraped = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = "INSERT INTO album (strAlbum, strArtists, strReleaseType, lastScraped) " """VALUES (?, ?, ?, ?)"""
    args = (album,artist,firstReleaseType, lastScraped)
 
    try:
        connectMDB = sqlite3.connect(str(os.path.join(MDBPATH)))
        cursor = connectMDB.cursor()
        lastScraped = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #if not cursor.execute("""select "%s" from "%s" where strAlbum="%s";""" % ("strAlbum","album", album)).fetchone() :
        #sql_album = """INSERT INTO album (strAlbum, strArtists, strReleaseType, lastScraped) VALUES ("%s", "%s", "%s","%s");""" % (album,artist,firstReleaseType, lastScraped)
        if not cursor.execute("""select "%s" from "%s" where strAlbum="%s";""" % ("strAlbum","album", album)).fetchone() :
            cursor.execute(query, args)
            dID = cursor.lastrowid       
        else:
            dID = cursor.execute("""select "%s" from "%s" where strAlbum="%s";""" % ("idAlbum","album", album)).fetchone()[0]  
      
        connectMDB.commit()
    except:
        pass
 
    finally:
        cursor.close()
        connectMDB.close()
        return dID
    
def writeSong(pathID, albumID, artist, songName, track="NULL"):
    try: 
        connectMDB = sqlite3.connect(str(os.path.join(MDBPATH)))
        cursor = connectMDB.cursor()      
        dateAdded = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not cursor.execute("""select "%s" from "%s" where strTitle="%s";""" % ("strTitle","song", songName)).fetchone() :
            sql_song = """INSERT INTO song (iYear,dateAdded,idAlbum,idPath,strArtists,strTitle,strFileName,iTrack,strGenres,iDuration,iTimesPlayed,iStartOffset,iEndOffset,userrating,comment,mood,votes) 
                                    VALUES ("2016","%s","%s", "%s", "%s", "%s", "%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s");
                                    """ % (dateAdded, albumID,pathID,artist,songName, songName + ".strm", track, "osmosis", "200", "0","0","0","5","osmosis","osmosis", "100" )

#            sql_song = """INSERT INTO song (iYear,dateAdded,idAlbum, idPath, strArtists, strTitle, strFileName, iTrack ) VALUES ("2016","%s","%s", "%s", "%s", "%s", "%s","%s");""" % (dateAdded, albumID,pathID,artist,songName, songName + ".strm", track)
            cursor.execute(sql_song)
            connectMDB.commit()
            dID = cursor.lastrowid
            cursor.close()
            connectMDB.close()
            return dID         
        else:
            dID = cursor.execute("""select "%s" from "%s" where strTitle="%s";""" % ("idSong","song", songName)).fetchone()[0]  
            cursor.close()
            connectMDB.close()
            return dID      
    except:
        connectMDB.close() 
        pass

def writeRole(strRole):
    query = "INSERT INTO role (strRole) " """VALUES ("%s")""" % strRole
    
    try:
        connectMDB = sqlite3.connect(str(os.path.join(MDBPATH)))
        cursor = connectMDB.cursor()

        if not cursor.execute("""select "%s" from "%s" where strRole="%s";""" % ("idRole","role", strRole)).fetchone() :
            cursor.execute(query)
            dID = cursor.lastrowid       
        else:
            dID = cursor.execute("""select "%s" from "%s" where strRole="%s";""" % ("idRole","role", strRole)).fetchone()[0]  
      
        connectMDB.commit()
    except:
        pass
 
    finally:
        cursor.close()
        connectMDB.close()
        return dID
   
def writeArtist(strArtist):
    query = "INSERT INTO artist (strArtist) " """VALUES ("%s")""" % strArtist
    
    try:
        connectMDB = sqlite3.connect(str(os.path.join(MDBPATH)))
        cursor = connectMDB.cursor()

        if not cursor.execute("""select "%s" from "%s" where strArtist="%s";""" % ("idArtist","artist", strArtist)).fetchone() :
            cursor.execute(query)
            dID = cursor.lastrowid       
        else:
            dID = cursor.execute("""select "%s" from "%s" where strArtist="%s";""" % ("idArtist","artist", strArtist)).fetchone()[0]  
      
        connectMDB.commit()
    except:
        pass
 
    finally:
        cursor.close()
        connectMDB.close()
        return dID
           
def writeSongArtist(artistID, songID,roleID, pstrAartistName, orderID):
    query = "INSERT INTO song_artist (idArtist, idSong, idRole, iOrder,strArtist) " """VALUES (?, ?, ?, ?,?)"""
    args = (artistID,songID,roleID,orderID,pstrAartistName )
  
    try:
        connectMDB = sqlite3.connect(str(os.path.join(MDBPATH)))
        cursor = connectMDB.cursor()

        if not cursor.execute("""select "%s" from "%s" where idSong="%s";""" % ("idSong","song_artist", songID)).fetchone() :
            cursor.execute(query, args)
            dID = cursor.lastrowid       
        else:
            dID = cursor.execute("""select "%s" from "%s" where idSong="%s";""" % ("idSong","song_artist", songID)).fetchone()[0]  
       
        connectMDB.commit()
    except:
        pass
    finally:
        cursor.close()
        connectMDB.close()
        return dID
    
def writeAlbumArtist(artistID, albumID,pstrAartistName):
    query = "INSERT INTO album_artist (idArtist, idAlbum,strArtist) " """VALUES (?, ?,?)"""
    args = (artistID,albumID,pstrAartistName )
  
    try:
        connectMDB = sqlite3.connect(str(os.path.join(MDBPATH)))
        cursor = connectMDB.cursor()

        if not cursor.execute("""select "%s" from "%s" where idAlbum="%s";""" % ("idAlbum","album_artist", albumID)).fetchone() :
            cursor.execute(query, args)
            dID = cursor.lastrowid       
        else:
            dID = cursor.execute("""select "%s" from "%s" where idAlbum="%s";""" % ("idAlbum","album_artist", albumID)).fetchone()[0]  
       
        connectMDB.commit()
    except:
        pass
    finally:
        cursor.close()
        connectMDB.close()
        return dID 

def writeThump(mediaId, mediaType, imageType, artPath):
    query = "INSERT INTO art ( media_id, media_type, type, url) " """VALUES (?,?,?,?)"""
    args =  (mediaId, mediaType,imageType, artPath )
    try:
        connectMDB = sqlite3.connect(str(os.path.join(MDBPATH)))
        cursor = connectMDB.cursor()

        if not cursor.execute("""select "%s" from "%s" where media_type="%s" AND media_id="%s";""" % ("media_id","art", mediaType, mediaId)).fetchone() :
            cursor.execute(query, args)
            dID = cursor.lastrowid       
        else:
            dID = cursor.execute("""select "%s" from "%s" where media_type="%s" AND media_id="%s";""" % ("media_id","art", mediaType, mediaId)).fetchone()[0]  
       
        connectMDB.commit()
    except:
        pass
    finally:
        cursor.close()
        connectMDB.close()
        return dID      
