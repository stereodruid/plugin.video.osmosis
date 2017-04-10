import utils

def getModule(orig_pluginname):
    extension = None
    if orig_pluginname and orig_pluginname != "":
        pluginname = orig_pluginname.replace('.','_')
        try:
            extension = __import__('modules.extensions.%s' % pluginname, fromlist=[pluginname])
        except ImportError:
            utils.addon_log("Extension " + pluginname + " could not be found")

	return extension