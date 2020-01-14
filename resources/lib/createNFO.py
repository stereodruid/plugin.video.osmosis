#!/usr/bin/python
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

from __future__ import unicode_literals
import os
import re
import sys
import xbmcvfs

# from lib import tvdb_api

global torrent_path
global torrent_name

'''Everything matching these patterns, and everything to the right
of the pattern, will be removed from the torrent name before searching
the TVDB api.

Add or remove as needed to suit your needs.

'''
global regexes

'''Set to logging.DEBUG for verbose log output,
logging.WARNING for log output when an nfo cannot be generated,
or logging.ERROR to show only unexpected errors,
or logging.CRITICAL to disable logging completely.

'''
# global log_level

'''The location of the log file, change as desired.'''
# global log_location

##############################################################################
#  Nothing below should need to be edited unless you know what you're doing  #
##############################################################################

# global log


def setNamePath(tPath, tName, logll):
    global torrent_path
    global torrent_name
    global regexes
    # global log_leve
    # global log_location
    # global log
    regexes = [
    '[S|s]0?\d+',
    'PROPER',
    'D[I|i]RF[I|i]x',
    'HDTV',
    '1080',
    '720',
    'DVD',
    'WEB-DL',
    '[E|e]0?\d+',
    'COMPLETE']
    # log_level = logging.WARNING
    # log_location = os.path.expanduser(logll)
    torrent_name = tName
    torrent_path = tPath
    # log_location = logll
    # log = logging.getLogger('tvshow_nfo')
    main()

'''Set to logging.DEBUG for verbose log output,
logging.WARNING for log output when an nfo cannot be generated,
or logging.ERROR to show only unexpected errors,
or logging.CRITICAL to disable logging completely.

'''

'''The location of the log file, change as desired.'''


def _is_tv_show(torrent_path):
    '''Check if torrent is a TV show.

    The default here is to check if the last part
    of the path, the direct parent directory where we
    are saving the torrent data, is called 'tv'.

    This could be changed to whatever you need in order
    to differentiate.  If you have no way to tell, just
    return True here, and let the TVDB lookup fail later.

    '''
    return True
    # return os.path.split(torrent_path)[1] == 'tv'


def _get_show_name(torrent_name):
    '''Parse show name from torrent name.

    This could be the crucial step that fails.
    First, compile our regex, which looks for a string like S02
    Then, split on that regex
    Next, grab the first part of that split
    Finally, replace all dots with spaces and return the result.

    '''
    for regex in regexes:
        compiled_regex = re.compile(regex)
        split_string = re.split(compiled_regex, torrent_name)
        dotted_name = split_string[0]
        name = dotted_name.replace('.', ' ')

        yield name.strip()


def get_show_url(torrent_name):
    '''Get thetvdb.com url for this series.'''
    t = tvdb_api.Tvdb()
    show_id = None
    failed_names = []

    for show_name in _get_show_name(torrent_name):
        if show_name in failed_names:
            # log.debug('Skipping duplicate name: %s' % show_name)
            continue  # Don't look up the same names more than once.
        try:
            # log.debug('Searching TVDB api for show name: %s' % show_name)
            show_id = t[show_name].data['id']
        except Exception:
            # log.debug('Failed to find show with name: %s' % show_name)
            failed_names.append(show_name)

    if show_id is None:
        return None

    return 'http://thetvdb.com/?tab=series&id={0}'.format(show_id)


def main():
    '''First arg should be directory for our new data,
    second arg should be the name of the torrent.

    '''

    # _configure_logging()

    if len(sys.argv) < 3:
        # log.error('Not enough arguments, aborting.')
        return

    # Get torrent path and name from command-line args

    if not _is_tv_show(torrent_path):
        # log.debug('Not a tv show, aborting.')
        return

    # Figure out where to write our new nfo file
    nfo_path = '{0}/{1}/tvshow.nfo'.format(torrent_path, torrent_name)

    # Return if the file already exists
    if os.path.exists(nfo_path):
        # log.debug('A tvshow.nfo already exists for this directory, aborting.')
        return

    # Get show name and thetvdb.com URL
    show_url = get_show_url(torrent_name)
    if show_url is None:
        # log.warn(
            # 'Could not find show on TVDB for %s, aborting.' % torrent_name)
        return

    # Create nfo and write our URL to it
    try:
        if not xbmcvfs.exists(torrent_path + '\\' + torrent_name):
            xbmcvfs.mkdirs(torrent_path + '\\' + torrent_name)

    except:
        pass
    nfo_file = open(nfo_path, 'w')
    nfo_file.write('{0}\n'.format(show_url))
    # log.debug('Wrote nfo')

    # Close all of our files
    nfo_file.close()


if __name__ == '__main__':
    main()
