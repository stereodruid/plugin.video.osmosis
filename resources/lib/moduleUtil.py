# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import utils


def getModule(orig_pluginname):
    extension = None
    if orig_pluginname and orig_pluginname != '':
        pluginname = orig_pluginname.replace('.', '_')
        try:
            extension = __import__('resources.lib.extensions.{0}'.format(pluginname), fromlist=[pluginname])
        except ImportError:
            utils.addon_log('Extension {0} could not be found'.format(pluginname))

    return extension